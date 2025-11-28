import hashlib
import json
import shutil
import subprocess
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

"""
Sistema de Auditoria Imutável para OmniMind
Implementa chain hashing e validação de integridade para todas as operações críticas.

Baseado em: /home/fahbrain/OmniAgent/registroauditoria.md
"""



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

        # 🔧 RECUPERAÇÃO AUTOMÁTICA: Verificar e reparar integridade na inicialização
        self._auto_recover_chain()

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
                    last_hash = data.get("last_hash", "0" * 64)
                    if isinstance(last_hash, str):
                        return last_hash
                    return str(last_hash)
            except Exception as e:
                self._log_security_event(f"Erro ao carregar hash chain: {e}")
                return "0" * 64
        return "0" * 64  # Hash inicial (64 zeros)

    def _auto_recover_chain(self) -> None:
        """
        Recuperação automática da cadeia de auditoria na inicialização.
        Executa verificação e reparo automático se necessário.
        """
        if not self.audit_log_file.exists():
            self._log_system_event(
                "audit_chain_auto_recover",
                {"action": "skip_recovery", "reason": "audit_log_not_exists"},
            )
            return

        # Verificar integridade atual
        integrity_check = self.verify_chain_integrity()

        if integrity_check.get("valid", False):
            # Cadeia íntegra - registrar sucesso
            self._log_system_event(
                "audit_chain_auto_recover",
                {
                    "action": "integrity_verified",
                    "events_verified": integrity_check.get("events_verified", 0),
                    "system_restarts": integrity_check.get("system_restarts", 0),
                },
            )
            return

        # Cadeia corrompida - tentar reparo automático
        self._log_security_event(
            f"🔧 Iniciando recuperação automática da cadeia de auditoria. "
            f"Status: {integrity_check.get('message', 'unknown')}"
        )

        try:
            repair_result = self.repair_chain_integrity()

            if repair_result.get("repaired", False):
                # Reparo bem-sucedido
                self._log_system_event(
                    "audit_chain_auto_recover",
                    {
                        "action": "repair_successful",
                        "events_repaired": repair_result.get("events_repaired", 0),
                        "events_removed": repair_result.get("events_removed", 0),
                        "system_restarts": repair_result.get("system_restarts", 0),
                        "backup_file": repair_result.get("backup_file", ""),
                    },
                )

                # Recarregar último hash após reparo
                self.last_hash = self._load_last_hash()

                self._log_security_event(
                    f"✅ Recuperação automática concluída: {repair_result.get('message', '')}"
                )

            else:
                # Reparo falhou - log de erro crítico
                self._log_security_event(
                    f"❌ CRÍTICO: Recuperação automática falhou: {repair_result.get('message', '')}"
                )
                self._log_system_event(
                    "audit_chain_auto_recover",
                    {
                        "action": "repair_failed",
                        "error": repair_result.get("message", "unknown"),
                        "backup_restored": repair_result.get("backup_restored", False),
                    },
                )

        except Exception as e:
            # Erro durante reparo
            error_msg = f"Erro crítico na recuperação automática: {str(e)}"
            self._log_security_event(f"❌ {error_msg}")
            self._log_system_event(
                "audit_chain_auto_recover", {"action": "repair_error", "error": str(e)}
            )

    def _save_last_hash(self, hash_value: str) -> None:
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

    def log_action(self, action: str, details: Dict[str, Any], category: str = "general") -> str:
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
        Permite quebras controladas na cadeia quando há reinicializações do sistema.

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
        system_restarts = 0

        try:
            with open(self.audit_log_file, "rb") as f:
                for line_num, line in enumerate(f, 1):
                    if not line.strip():
                        continue

                    try:
                        event = json.loads(line)
                        action = event.get("action", "")

                        # Permitir quebra na cadeia para eventos de inicialização do sistema
                        if action == "audit_system_initialized":
                            # Verificar se é um reset (000...) ou continuação válida
                            if event.get("prev_hash") == "0" * 64:
                                # Reset explícito
                                prev_hash = "0" * 64
                                system_restarts += 1
                            elif event.get("prev_hash") == prev_hash:
                                # Continuação da cadeia (Melhor segurança)
                                pass
                            else:
                                # Nem reset nem continuação válida
                                corrupted_events.append(
                                    {
                                        "line": line_num,
                                        "expected_prev_hash": f"{prev_hash} OR {'0'*64}",
                                        "found_prev_hash": event.get("prev_hash"),
                                        "action": action,
                                    }
                                )
                        elif event.get("prev_hash") != prev_hash:
                            # Verificar se é uma quebra não autorizada
                            corrupted_events.append(
                                {
                                    "line": line_num,
                                    "expected_prev_hash": prev_hash,
                                    "found_prev_hash": event.get("prev_hash"),
                                    "action": action,
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

                        json_data = json.dumps(event_for_hash, sort_keys=True).encode("utf-8")
                        calculated_hash = self.hash_content(json_data)
                        stored_hash = event.get("current_hash")

                        if calculated_hash != stored_hash:
                            corrupted_events.append(
                                {
                                    "line": line_num,
                                    "hash_mismatch": True,
                                    "expected": calculated_hash,
                                    "found": stored_hash,
                                    "action": action,
                                }
                            )

                        prev_hash = stored_hash or calculated_hash
                        events_verified += 1

                    except json.JSONDecodeError:
                        corrupted_events.append({"line": line_num, "error": "JSON inválido"})

            # Avaliar resultado baseado em corrupções não autorizadas
            unauthorized_corruptions = [
                c for c in corrupted_events if not c.get("action", "").startswith("audit_system_")
            ]

            if unauthorized_corruptions:
                corruption_msg = (
                    "ALERTA: Cadeia de auditoria corrompida! "
                    f"{len(unauthorized_corruptions)} eventos inválidos não autorizados"
                )
                self._log_security_event(corruption_msg)
                return {
                    "valid": False,
                    "message": "Cadeia corrompida detectada",
                    "events_verified": events_verified,
                    "system_restarts": system_restarts,
                    "unauthorized_corruptions": len(unauthorized_corruptions),
                    "corrupted_events": unauthorized_corruptions,
                }

            return {
                "valid": True,
                "message": f"Cadeia íntegra ({system_restarts} reinicializações autorizadas)",
                "events_verified": events_verified,
                "system_restarts": system_restarts,
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
                ["sudo", "-n", "chattr", "+i", filepath],
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

    def _log_security_event(self, message: str) -> None:
        """Registra evento de segurança em log separado."""
        timestamp = datetime.now(timezone.utc).isoformat()
        with open(self.security_log, "a") as f:
            f.write(f"[{timestamp}] {message}\n")

    def _log_system_event(self, event: str, details: Dict[str, Any]) -> None:
        """Registra evento de sistema no audit log."""
        try:
            self.log_action(event, details, category="system")
        except Exception as e:
            self._log_security_event(f"Falha ao registrar evento de sistema: {e}")

    def repair_chain_integrity(self) -> Dict[str, Any]:
        """
        Tenta reparar a cadeia de auditoria detectando e corrigindo quebras.

        Returns:
            Dicionário com resultado do reparo
        """
        if not self.audit_log_file.exists():
            return {"repaired": False, "message": "Log não existe"}

        print("🔧 Iniciando reparo da cadeia de auditoria...")

        # Fazer backup do log original
        backup_file = self.audit_log_file.with_suffix(".bak")

        shutil.copy2(self.audit_log_file, backup_file)

        events_repaired = 0
        events_removed = 0
        valid_events = []

        try:
            with open(self.audit_log_file, "rb") as f:
                lines = f.readlines()

            prev_hash = "0" * 64
            system_restarts = 0

            for line_num, line in enumerate(lines, 1):
                if not line.strip():
                    continue

                try:
                    event = json.loads(line)
                    action = event.get("action", "")

                    # Permitir quebra na cadeia para eventos de inicialização
                    if action == "audit_system_initialized":
                        prev_hash = "0" * 64
                        system_restarts += 1
                        valid_events.append(line)
                        continue

                    # Verificar se o prev_hash está correto
                    if event.get("prev_hash") != prev_hash:
                        print(
                            f"⚠️  Quebra detectada na linha {line_num} "
                            f"({action}) - removendo evento"
                        )
                        events_removed += 1
                        continue

                    # Verificar hash do evento
                    event_for_hash = {
                        "action": event.get("action"),
                        "category": event.get("category"),
                        "details": event.get("details"),
                        "timestamp": event.get("timestamp"),
                        "datetime_utc": event.get("datetime_utc"),
                        "prev_hash": event.get("prev_hash"),
                    }

                    json_data = json.dumps(event_for_hash, sort_keys=True).encode("utf-8")
                    calculated_hash = self.hash_content(json_data)
                    stored_hash = event.get("current_hash")

                    if calculated_hash != stored_hash:
                        print(
                            f"⚠️  Hash inválido na linha {line_num} "
                            f"({action}) - removendo evento"
                        )
                        events_removed += 1
                        continue

                    # Evento válido
                    valid_events.append(line)
                    prev_hash = stored_hash
                    events_repaired += 1

                except json.JSONDecodeError:
                    print(f"⚠️  JSON inválido na linha {line_num} - removendo")
                    events_removed += 1

            # Reescrever log com eventos válidos
            with open(self.audit_log_file, "wb") as f:
                for event_line in valid_events:
                    f.write(event_line)

            # Atualizar último hash
            if valid_events:
                last_event = json.loads(valid_events[-1])
                self.last_hash = last_event.get("current_hash", "0" * 64)
                self._save_last_hash(self.last_hash)

            result = {
                "repaired": True,
                "message": (
                    f"Cadeia reparada: {events_repaired} eventos válidos, "
                    f"{events_removed} removidos"
                ),
                "events_repaired": events_repaired,
                "events_removed": events_removed,
                "system_restarts": system_restarts,
                "backup_file": str(backup_file),
            }

            print(f"✅ Reparo concluído: {result['message']}")
            self._log_security_event(
                f"Cadeia de auditoria reparada: {events_repaired} válidos, "
                f"{events_removed} removidos"
            )

            return result

        except Exception as e:
            error_msg = f"Erro durante reparo: {str(e)}"
            print(f"❌ {error_msg}")
            self._log_security_event(error_msg)

            # Restaurar backup em caso de erro
            shutil.copy2(backup_file, self.audit_log_file)
            print("📁 Backup restaurado")

            return {
                "repaired": False,
                "message": error_msg,
                "backup_restored": True,
            }

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
_audit_lock = threading.Lock()


def get_audit_system() -> ImmutableAuditSystem:
    """Retorna instância singleton do sistema de auditoria."""
    global _audit_system
    with _audit_lock:
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
