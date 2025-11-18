#!/usr/bin/env python3
"""
Sistema de Auditoria Imutável para OmniMind
Implementa chain hashing e validação de integridade para todas as operações críticas.

Baseado em: /home/fahbrain/OmniAgent/registroauditoria.md
"""

import hashlib
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
import threading


class ImmutableAuditSystem:
    """
    Sistema de auditoria com chain hashing para garantir integridade de logs.
    Cada evento é hasheado com SHA-256 incluindo o hash do evento anterior.
    """

    def __init__(self, log_dir: str = "~/projects/omnimind/logs"):
        self.log_dir = Path(log_dir).expanduser()
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.audit_log_file = self.log_dir / "audit_chain.log"
        self.hash_chain_file = self.log_dir / "hash_chain.json"
        self.security_log = self.log_dir / "security_events.log"

        # Thread lock para escrita segura
        self._lock = threading.Lock()

        # Inicializar cadeia de hash
        self.last_hash = self._load_last_hash()

        # Registrar inicialização do sistema
        self._log_system_event(
            "audit_system_initialized",
            {"version": "1.0.0", "log_dir": str(self.log_dir)},
        )

    def _load_last_hash(self) -> str:
        """Carrega o último hash da cadeia ou retorna hash inicial."""
        if self.hash_chain_file.exists():
            try:
                with open(self.hash_chain_file, "r") as f:
                    data = json.load(f)
                    return data.get("last_hash", "0" * 64)
            except Exception as e:
                self._log_security_event(f"Erro ao carregar hash chain: {e}")
                return "0" * 64
        return "0" * 64  # Hash inicial (64 zeros)

    def _save_last_hash(self, hash_value: str):
        """Salva o último hash da cadeia."""
        with open(self.hash_chain_file, "w") as f:
            json.dump(
                {
                    "last_hash": hash_value,
                    "timestamp": time.time(),
                    "datetime": datetime.now(timezone.utc).isoformat(),
                },
                f,
                indent=2,
            )

    def hash_content(self, content: bytes) -> str:
        """
        Gera hash SHA-256 de conteúdo.

        Args:
            content: Bytes do conteúdo a ser hasheado

        Returns:
            String hexadecimal do hash SHA-256
        """
        return hashlib.sha256(content).hexdigest()

    def log_action(
        self, action: str, details: Dict[str, Any], category: str = "general"
    ) -> str:
        """
        Registra ação crítica no sistema de auditoria com chain hashing.

        Args:
            action: Nome da ação executada
            details: Dicionário com detalhes da ação
            category: Categoria da ação (general, code, config, security)

        Returns:
            Hash do evento registrado
        """
        with self._lock:
            # Criar evento com metadata
            event_data = {
                "action": action,
                "category": category,
                "details": details,
                "timestamp": time.time(),
                "datetime_utc": datetime.now(timezone.utc).isoformat(),
                "prev_hash": self.last_hash,
            }

            # Serializar e hashear (sem current_hash ainda)
            json_data = json.dumps(event_data, sort_keys=True).encode("utf-8")
            current_hash = self.hash_content(json_data)

            # Adicionar hash ao evento
            event_data["current_hash"] = current_hash

            # Serializar novamente COM o hash para salvar
            json_data_with_hash = json.dumps(event_data, sort_keys=True).encode("utf-8")

            # Escrever no log
            try:
                with open(self.audit_log_file, "ab") as f:
                    f.write(json_data_with_hash + b"\n")

                # Atualizar último hash
                self.last_hash = current_hash
                self._save_last_hash(current_hash)

                return current_hash

            except Exception as e:
                self._log_security_event(f"CRÍTICO: Falha ao escrever audit log: {e}")
                raise

    def verify_chain_integrity(self) -> Dict[str, Any]:
        """
        Verifica integridade completa da cadeia de hash.

        Returns:
            Dicionário com resultado da verificação
        """
        if not self.audit_log_file.exists():
            return {
                "valid": True,
                "message": "Log de auditoria vazio",
                "events_verified": 0,
            }

        events_verified = 0
        prev_hash = "0" * 64
        corrupted_events = []

        try:
            with open(self.audit_log_file, "rb") as f:
                for line_num, line in enumerate(f, 1):
                    if not line.strip():
                        continue

                    try:
                        event = json.loads(line)

                        # Verificar hash anterior
                        if event.get("prev_hash") != prev_hash:
                            corrupted_events.append(
                                {
                                    "line": line_num,
                                    "expected_prev_hash": prev_hash,
                                    "found_prev_hash": event.get("prev_hash"),
                                }
                            )

                        # Recalcular hash do evento (SEM o current_hash)
                        event_for_hash = {
                            "action": event.get("action"),
                            "category": event.get("category"),
                            "details": event.get("details"),
                            "timestamp": event.get("timestamp"),
                            "datetime_utc": event.get("datetime_utc"),
                            "prev_hash": event.get("prev_hash"),
                        }

                        json_data = json.dumps(event_for_hash, sort_keys=True).encode(
                            "utf-8"
                        )
                        calculated_hash = self.hash_content(json_data)
                        stored_hash = event.get("current_hash")

                        if calculated_hash != stored_hash:
                            corrupted_events.append(
                                {
                                    "line": line_num,
                                    "hash_mismatch": True,
                                    "expected": calculated_hash,
                                    "found": stored_hash,
                                }
                            )

                        prev_hash = stored_hash or calculated_hash
                        events_verified += 1

                    except json.JSONDecodeError:
                        corrupted_events.append(
                            {"line": line_num, "error": "JSON inválido"}
                        )

            if corrupted_events:
                corruption_msg = (
                    "ALERTA: Cadeia de auditoria corrompida! "
                    f"{len(corrupted_events)} eventos inválidos"
                )
                self._log_security_event(corruption_msg)
                return {
                    "valid": False,
                    "message": "Cadeia corrompida detectada",
                    "events_verified": events_verified,
                    "corrupted_events": corrupted_events,
                }

            return {
                "valid": True,
                "message": "Cadeia íntegra",
                "events_verified": events_verified,
            }

        except Exception as e:
            self._log_security_event(f"Erro ao verificar cadeia: {e}")
            return {
                "valid": False,
                "message": f"Erro na verificação: {str(e)}",
                "events_verified": events_verified,
            }

    def set_file_xattr(self, filepath: str, content_hash: str) -> bool:
        """
        Marca arquivo com hash em extended attributes (xattr).

        Args:
            filepath: Caminho do arquivo
            content_hash: Hash SHA-256 do conteúdo

        Returns:
            True se sucesso, False se falhou
        """
        try:
            subprocess.run(
                ["setfattr", "-n", "user.omnimind_hash", "-v", content_hash, filepath],
                check=True,
                capture_output=True,
                timeout=5,
            )
            return True
        except subprocess.CalledProcessError as e:
            self._log_security_event(f"Falha ao setar xattr em {filepath}: {e}")
            return False
        except FileNotFoundError:
            # setfattr não disponível, registrar mas não falhar
            self._log_security_event("setfattr não disponível - xattr desabilitado")
            return False

    def verify_file_integrity(self, filepath: str) -> Dict[str, Any]:
        """
        Verifica integridade de arquivo comparando hash com xattr.

        Args:
            filepath: Caminho do arquivo

        Returns:
            Dicionário com resultado da verificação
        """
        path = Path(filepath)

        if not path.exists():
            return {"valid": False, "message": "Arquivo não existe"}

        try:
            # Calcular hash atual
            with open(path, "rb") as f:
                current_hash = self.hash_content(f.read())

            # Obter hash do xattr
            try:
                result = subprocess.run(
                    [
                        "getfattr",
                        "-n",
                        "user.omnimind_hash",
                        "--only-values",
                        str(path),
                    ],
                    check=True,
                    capture_output=True,
                    timeout=5,
                    text=True,
                )
                stored_hash = result.stdout.strip()

                if current_hash == stored_hash:
                    return {
                        "valid": True,
                        "message": "Arquivo íntegro",
                        "hash": current_hash,
                    }
                else:
                    self._log_security_event(
                        f"ALERTA: Arquivo {filepath} foi modificado! "
                        f"Hash esperado: {stored_hash}, encontrado: {current_hash}"
                    )
                    return {
                        "valid": False,
                        "message": "Arquivo modificado",
                        "expected_hash": stored_hash,
                        "current_hash": current_hash,
                    }

            except subprocess.CalledProcessError:
                # xattr não existe ou não acessível
                return {
                    "valid": None,
                    "message": "Sem xattr registrado",
                    "current_hash": current_hash,
                }

        except Exception as e:
            return {"valid": False, "message": f"Erro na verificação: {str(e)}"}

    def protect_log_file(self, filepath: str) -> bool:
        """
        Torna arquivo imutável usando chattr +i (requer root).

        Args:
            filepath: Caminho do arquivo

        Returns:
            True se sucesso, False se falhou
        """
        try:
            subprocess.run(
                ["sudo", "chattr", "+i", filepath],
                check=True,
                capture_output=True,
                timeout=5,
            )
            return True
        except subprocess.CalledProcessError:
            # Pode falhar se não for root, não é crítico
            return False
        except FileNotFoundError:
            return False

    def _log_security_event(self, message: str):
        """Registra evento de segurança em log separado."""
        timestamp = datetime.now(timezone.utc).isoformat()
        with open(self.security_log, "a") as f:
            f.write(f"[{timestamp}] {message}\n")

    def _log_system_event(self, event: str, details: Dict[str, Any]):
        """Registra evento de sistema no audit log."""
        try:
            self.log_action(event, details, category="system")
        except Exception as e:
            self._log_security_event(f"Falha ao registrar evento de sistema: {e}")

    def get_audit_summary(self) -> Dict[str, Any]:
        """
        Retorna resumo do sistema de auditoria.

        Returns:
            Dicionário com estatísticas do audit log
        """
        summary = {
            "log_dir": str(self.log_dir),
            "audit_log_exists": self.audit_log_file.exists(),
            "last_hash": self.last_hash,
            "total_events": 0,
            "log_size_bytes": 0,
        }

        if self.audit_log_file.exists():
            summary["log_size_bytes"] = self.audit_log_file.stat().st_size

            with open(self.audit_log_file, "rb") as f:
                summary["total_events"] = sum(1 for line in f if line.strip())

        # Verificar integridade
        integrity = self.verify_chain_integrity()
        summary["chain_integrity"] = integrity

        return summary


# Instância global singleton
_audit_system: Optional[ImmutableAuditSystem] = None


def get_audit_system() -> ImmutableAuditSystem:
    """Retorna instância singleton do sistema de auditoria."""
    global _audit_system
    if _audit_system is None:
        _audit_system = ImmutableAuditSystem()
    return _audit_system


def log_action(action: str, details: Dict[str, Any], category: str = "general") -> str:
    """Atalho para registrar ação no sistema de auditoria."""
    return get_audit_system().log_action(action, details, category)


# Teste unitário embutido
if __name__ == "__main__":
    print("=== Teste do Sistema de Auditoria Imutável ===\n")

    # Criar instância de teste
    audit = ImmutableAuditSystem()

    # Teste 1: Registrar ações
    print("1. Registrando ações de teste...")
    hash1 = audit.log_action("test_action_1", {"data": "teste1"}, "test")
    print(f"   Hash 1: {hash1[:16]}...")

    hash2 = audit.log_action("test_action_2", {"data": "teste2"}, "test")
    print(f"   Hash 2: {hash2[:16]}...")

    # Teste 2: Verificar integridade
    print("\n2. Verificando integridade da cadeia...")
    integrity = audit.verify_chain_integrity()
    print(f"   Válido: {integrity['valid']}")
    print(f"   Eventos verificados: {integrity['events_verified']}")

    # Teste 3: Resumo
    print("\n3. Resumo do sistema:")
    summary = audit.get_audit_summary()
    print(f"   Total de eventos: {summary['total_events']}")
    print(f"   Tamanho do log: {summary['log_size_bytes']} bytes")
    print(f"   Integridade: {summary['chain_integrity']['valid']}")

    # Teste 4: File integrity
    print("\n4. Testando marcação de arquivo...")
    test_file = Path("/tmp/omnimind_test.txt")
    test_file.write_text("Conteúdo de teste")

    content_hash = audit.hash_content(test_file.read_bytes())
    if audit.set_file_xattr(str(test_file), content_hash):
        print("   ✓ xattr definido com sucesso")

        verification = audit.verify_file_integrity(str(test_file))
        print(f"   ✓ Verificação: {verification['message']}")
    else:
        print("   ⚠ xattr não disponível (requer attr-utils)")

    test_file.unlink()

    print("\n✓ Todos os testes concluídos!")
    print(f"\nLogs salvos em: {audit.log_dir}")
