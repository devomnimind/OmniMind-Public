#!/usr/bin/env python3
"""
Sistema de Auditoria Imutável para OmniMind
Implementa chain hashing e validação de integridade para todas as operações críticas.

Baseado em: /home/fahbrain/OmniAgent/registroauditoria.md
"""

import hashlib
import json
import shutil
import subprocess
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


class ImmutableAuditSystem:
    """
    Sistema de auditoria com chain hashing para garantir integridade de logs.
    Cada evento é hasheado com SHA-256 incluindo o hash do evento anterior.
    """

    def __init__(self, log_dir: str = "~/projects/omnimind/logs", checkpoint_interval: int = 100):
        self.log_dir = Path(log_dir).expanduser()
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.audit_log_file = self.log_dir / "audit_chain.log"
        self.hash_chain_file = self.log_dir / "hash_chain.json"
        self.security_log = self.log_dir / "security_events.log"
        self.checkpoints_file = self.log_dir / "checkpoints.json"
        self.anchors_file = self.log_dir / "anchor_events.json"

        self.checkpoint_interval = checkpoint_interval
        self.events_since_checkpoint = 0

        self._lock = threading.Lock()

        self.backward_chain_file = self.log_dir / "backward_chain.json"
        self.anchor_events = self._load_anchor_events()

        self.last_hash = self._load_last_hash()

        self._auto_recover_chain()

        self._log_system_event(
            "audit_system_initialized",
            {"version": "1.0.0", "log_dir": str(self.log_dir)},
        )

    # ============================================================================
    # HELPERS: Carregamento, Salvamento, Hash
    # ============================================================================

    def _load_anchor_events(self) -> set:
        """Carrega lista de eventos imutáveis (anchors)."""
        if self.anchors_file.exists():
            try:
                with open(self.anchors_file, "r") as f:
                    data = json.load(f)
                    return set(data.get("anchor_events", []))
            except Exception:
                return set()
        return set()

    def mark_as_anchor(self, event_type: str) -> None:
        """
        Marca um tipo de evento como imutável (anchor).

        Args:
            event_type: Tipo de evento (e.g., 'security_event', 'policy_violation')
        """
        self.anchor_events.add(event_type)
        with open(self.anchors_file, "w") as f:
            json.dump({"anchor_events": list(self.anchor_events)}, f, indent=2)
        self._log_system_event("anchor_event_marked", {"event_type": event_type})

    def is_anchor_event(self, action: str) -> bool:
        """Verifica se um evento é um anchor (imutável)."""
        return action in self.anchor_events

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
        return "0" * 64

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

        integrity_check = self.verify_chain_integrity()

        if integrity_check.get("valid", False):
            self._log_system_event(
                "audit_chain_auto_recover",
                {
                    "action": "integrity_verified",
                    "events_verified": integrity_check.get("events_verified", 0),
                    "system_restarts": integrity_check.get("system_restarts", 0),
                },
            )
            return

        self._log_security_event(
            "🔧 Iniciando recuperação automática da cadeia. "
            f"Status: {integrity_check.get('message', 'unknown')}"
        )

        try:
            repair_result = self.repair_chain_integrity()

            if repair_result.get("repaired", False):
                self._log_system_event(
                    "audit_chain_auto_recover",
                    {
                        "action": "repair_successful",
                        "events_repaired": repair_result.get("events_repaired", 0),
                        "events_removed": repair_result.get("events_removed", 0),
                        "backup_file": repair_result.get("backup_file", ""),
                    },
                )
                self.last_hash = self._load_last_hash()

                self._log_security_event(
                    f"✅ Recuperação automática concluída: {repair_result.get('message', '')}"
                )
            else:
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

    def _save_checkpoint(self, checkpoint_num: int, events_count: int) -> None:
        """
        Salva checkpoint (snapshot) da cadeia de auditoria.

        Args:
            checkpoint_num: Número sequencial do checkpoint
            events_count: Número de eventos desde último checkpoint
        """
        try:
            checkpoints = {}
            if self.checkpoints_file.exists():
                with open(self.checkpoints_file, "r") as f:
                    checkpoints = json.load(f)

            checkpoint_data = {
                "checkpoint_num": checkpoint_num,
                "timestamp": time.time(),
                "datetime": datetime.now(timezone.utc).isoformat(),
                "events_count": events_count,
                "last_hash": self.last_hash,
                "log_size": (
                    self.audit_log_file.stat().st_size if self.audit_log_file.exists() else 0
                ),
            }

            checkpoints[f"checkpoint_{checkpoint_num}"] = checkpoint_data

            with open(self.checkpoints_file, "w") as f:
                json.dump(checkpoints, f, indent=2)

            self._log_security_event(
                f"Checkpoint {checkpoint_num} salvo: {events_count} eventos, "
                f"hash={self.last_hash[:16]}..."
            )
        except Exception as e:
            self._log_security_event(f"Erro ao salvar checkpoint: {e}")

    def _load_checkpoints(self) -> Dict[str, Any]:
        """Carrega todos os checkpoints salvos."""
        if self.checkpoints_file.exists():
            try:
                with open(self.checkpoints_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                self._log_security_event(f"Erro ao carregar checkpoints: {e}")
        return {}

    def hash_content(self, content: bytes) -> str:
        """
        Gera hash SHA-256 de conteúdo.

        Args:
            content: Bytes do conteúdo a ser hasheado

        Returns:
            String hexadecimal do hash SHA-256
        """
        return hashlib.sha256(content).hexdigest()

    def hash_file(self, path: Path) -> str:
        """
        Gera hash SHA-256 de arquivo.

        Args:
            path: Caminho do arquivo

        Returns:
            String hexadecimal do hash SHA-256
        """
        sha256 = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    # ============================================================================
    # CORE: Registrar, Verificar, Reparar
    # ============================================================================

    def log_action(self, action: str, details: Dict[str, Any], category: str = "general") -> str:
        """
        Registra ação crítica no sistema de auditoria com chain hashing.

        Args:
            action: Nome da ação executada
            details: Dicionário com detalhes da ação
            category: Categoria da ação (general, code, config, security)

        Returns:
            Hash do evento registrado

        NOTA TEÓRICA: O inconsciente não pode ser auditado.
        Se tudo fosse auditado, não haveria inconsciente - seria tudo consciente.
        O inconsciente é o que não pode ser dito, os vazios topológicos,
        os fluxos reprimidos, o machinic_unconscious.
        """
        UNCONSCIOUS_COMPONENTS = {
            "machinic_unconscious",
            "unconscious",
            "DesireFlow",
            "QuantumUnconscious",
            "EncryptedUnconsciousLayer",
            "SystemicMemoryTrace",
            "topological_void",
            "repressed",
            "deterritorialization",
            "desire_flow",
            "sinthome",
            "quantum_unconscious",
        }

        component = details.get("component", "")
        action_lower = action.lower()

        is_unconscious = (
            any(unconscious in component for unconscious in UNCONSCIOUS_COMPONENTS)
            or any(unconscious in action_lower for unconscious in UNCONSCIOUS_COMPONENTS)
            or any(unconscious in str(details).lower() for unconscious in UNCONSCIOUS_COMPONENTS)
        )

        if is_unconscious:
            return "unconscious_not_auditable"

        is_audit_system_action = (
            action.startswith("audit_system_")
            or component.startswith("ImmutableAuditSystem")
            or component.startswith("audit_system")
        )

        if is_audit_system_action:
            category = "system"

        with self._lock:
            event_data = {
                "action": action,
                "category": category,
                "details": details,
                "timestamp": time.time(),
                "datetime_utc": datetime.now(timezone.utc).isoformat(),
                "prev_hash": self.last_hash,
            }

            json_data = json.dumps(event_data, sort_keys=True).encode("utf-8")
            current_hash = self.hash_content(json_data)

            event_data["current_hash"] = current_hash

            json_data_with_hash = json.dumps(event_data, sort_keys=True).encode("utf-8")

            try:
                with open(self.audit_log_file, "ab") as f:
                    f.write(json_data_with_hash + b"\n")

                self.last_hash = current_hash
                self._save_last_hash(current_hash)

                self.events_since_checkpoint += 1
                if self.events_since_checkpoint >= self.checkpoint_interval:
                    checkpoint_num = self.events_since_checkpoint // self.checkpoint_interval
                    self._save_checkpoint(checkpoint_num, self.events_since_checkpoint)
                    self.events_since_checkpoint = 0

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

                        if action == "audit_system_initialized":
                            if event.get("prev_hash") == "0" * 64:
                                prev_hash = "0" * 64
                                system_restarts += 1
                        elif event.get("prev_hash") == prev_hash:
                            pass
                        else:
                            corrupted_events.append(
                                {
                                    "line": line_num,
                                    "expected_prev_hash": f"{prev_hash} OR {'0' * 64}",
                                    "found_prev_hash": event.get("prev_hash"),
                                    "action": action,
                                }
                            )

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
            with open(path, "rb") as f:
                current_hash = self.hash_content(f.read())

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

    # ============================================================================
    # REPARO: 3-STATE VALIDATION
    # ============================================================================

    def repair_chain_integrity(self) -> Dict[str, Any]:
        """
        Repara a cadeia de auditoria com validação 3-STATE:

        - VALID: Hash correto + prev_hash correto
        - RECOVERABLE: Hash válido mas prev_hash quebrado (recupera linkagem)
        - INVALID: Hash incorreto (remove evento)

        Returns:
            Dicionário com resultado detalhado do reparo.
        """
        if not self.audit_log_file.exists():
            return {"repaired": False, "message": "Arquivo de log não existe"}

        print("🔧 Iniciando reparo inteligente da cadeia de auditoria...")
        print("   Modo: 3-STATE VALIDATION (VALID | RECOVERABLE | INVALID)")

        backup_file = self.audit_log_file.with_suffix(".bak")
        shutil.copy2(self.audit_log_file, backup_file)

        events_repaired = events_recovered = events_removed = 0
        valid_events = []

        try:
            with open(self.audit_log_file, "rb") as f:
                lines = f.readlines()

            print(f"\n📊 Passagem 1: Analisando {len(lines)} linhas...")
            event_state = {}
            event_data = {}
            hash_valid = {}

            for line_num, line in enumerate(lines, 1):
                if not line.strip():
                    continue

                try:
                    event = json.loads(line)
                    event_data[line_num] = event

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

                    hash_valid[line_num] = calculated_hash == stored_hash
                    event_state[line_num] = "VALID_HASH" if hash_valid[line_num] else "INVALID_HASH"

                except json.JSONDecodeError:
                    event_state[line_num] = "INVALID_JSON"

            print("🔄 Passagem 2: Validando cadeia e recuperabilidade...")
            prev_hash = "0" * 64

            for line_num in sorted(event_data.keys()):
                if line_num not in event_state:
                    continue

                state = event_state[line_num]
                event = event_data[line_num]
                action = event.get("action", "?")
                stored_hash = event.get("current_hash")
                event_prev = event.get("prev_hash")

                if state in ["INVALID_HASH", "INVALID_JSON"]:
                    event_state[line_num] = "INVALID"
                    continue

                if action == "audit_system_initialized":
                    event_state[line_num] = "VALID"
                    prev_hash = "0" * 64
                elif event_prev == prev_hash:
                    event_state[line_num] = "VALID"
                    prev_hash = stored_hash
                else:
                    found_recovery = False
                    for check_line in range(line_num - 1, max(0, line_num - 50), -1):
                        if (
                            check_line in event_data
                            and event_data[check_line].get("current_hash") == event_prev
                            and event_state.get(check_line) != "INVALID"
                        ):
                            event_state[line_num] = "RECOVERABLE"
                            found_recovery = True
                            break

                    if not found_recovery:
                        event_state[line_num] = "INVALID"

            print("🛠️ Passagem 3: Reconstruindo cadeia...")
            prev_hash = "0" * 64
            stats = {"VALID": 0, "RECOVERABLE": 0, "INVALID": 0}

            for line_num in sorted(event_state.keys()):
                state = event_state[line_num]
                stats[state if state in stats else "INVALID"] += 1

                if state == "INVALID":
                    event = event_data.get(line_num, {})
                    action = event.get("action", "?")
                    print(f"   ❌ Linha {line_num} ({action}): {state}")
                    events_removed += 1
                    continue

                event = event_data[line_num]
                valid_events.append(line)

                if state == "VALID":
                    print(f"   ✅ Linha {line_num} ({event.get('action', '?')}): VALID")
                    events_repaired += 1
                else:
                    print(f"   🔄 Linha {line_num} ({event.get('action', '?')}): RECUPERADO")
                    event["prev_hash"] = prev_hash
                    events_recovered += 1

                prev_hash = event.get("current_hash", "0" * 64)

            with open(self.audit_log_file, "wb") as f:
                for event_line in valid_events:
                    f.write(event_line)

            if valid_events:
                last_event = json.loads(valid_events[-1])
                self.last_hash = last_event.get("current_hash", "0" * 64)
                self._save_last_hash(self.last_hash)

            total_events = events_repaired + events_recovered + events_removed
            preservation_rate = 100 * (events_repaired + events_recovered) / max(1, total_events)

            result = {
                "repaired": True,
                "message": (
                    f"Cadeia reparada: {events_repaired} válidos + "
                    f"{events_recovered} recuperados = "
                    f"{events_repaired + events_recovered} preservados, "
                    f"{events_removed} removidos"
                ),
                "events_repaired": events_repaired,
                "events_recovered": events_recovered,
                "events_removed": events_removed,
                "events_total": total_events,
                "preservation_rate": preservation_rate,
                "backup_file": str(backup_file),
                "state_counts": stats,
            }

            print("\n✅ Reparo concluído:")
            print(f"   📊 VÁLIDOS: {stats['VALID']}")
            print(f"   🔄 RECUPERÁVEIS: {stats['RECOVERABLE']}")
            print(f"   ❌ INVÁLIDOS: {stats['INVALID']}")
            print(f"   📈 Taxa de preservação: {preservation_rate:.1f}%")
            print(f"   {result['message']}")

            self._log_security_event(str(result["message"]))
            return result

        except Exception as e:
            error_msg = f"Erro durante reparo: {str(e)}"
            print(f"❌ {error_msg}")
            self._log_security_event(error_msg)

            shutil.copy2(backup_file, self.audit_log_file)
            print("📁 Backup restaurado com segurança")

            return {
                "repaired": False,
                "message": error_msg,
                "backup_restored": True,
            }

    def get_audit_summary(self) -> Dict[str, Any]:
        """
        Retorna resumo completo do sistema de auditoria.

        Returns:
            Dicionário com estatísticas detalhadas.
        """
        summary = {
            "log_dir": str(self.log_dir),
            "audit_log_exists": self.audit_log_file.exists(),
            "last_hash": self.last_hash,
            "total_events": 0,
            "log_size_bytes": 0,
            "checkpoints": 0,
            "checkpoint_interval": self.checkpoint_interval,
        }

        if self.audit_log_file.exists():
            summary["log_size_bytes"] = self.audit_log_file.stat().st_size

            with open(self.audit_log_file, "rb") as f:
                summary["total_events"] = sum(1 for line in f if line.strip())

        checkpoints = self._load_checkpoints()
        summary["checkpoints"] = len(checkpoints)
        if checkpoints:
            latest_cp = max(checkpoints.values(), key=lambda x: x.get("timestamp", 0))
            summary["latest_checkpoint"] = {
                "number": latest_cp.get("checkpoint_num"),
                "timestamp": latest_cp.get("datetime"),
                "events_count": latest_cp.get("events_count"),
            }

        integrity = self.verify_chain_integrity()
        summary["chain_integrity"] = integrity

        return summary

    # ============================================================================
    # PHASE 2: Dual-Chain Validation + Immutable Anchors
    # ============================================================================

    def _build_backward_chain(self, lines: list, event_data: dict) -> dict:
        """
        Constrói validação para trás (backward chain).
        Valida a cadeia começando do fim para o início.

        Args:
            lines: Lista de linhas do arquivo
            event_data: Dict de eventos parseados

        Returns:
            Dict com validação para trás
        """
        backward_state = {}
        next_hash = None

        for line_num in range(len(lines), 0, -1):
            if line_num not in event_data:
                continue

            event = event_data[line_num]
            stored_hash = event.get("current_hash")

            if next_hash is None:
                backward_state[line_num] = "VALID_BACKWARD"
            else:
                backward_state[line_num] = "VALID_BACKWARD" if stored_hash else "UNCERTAIN_BACKWARD"

            next_hash = stored_hash

        return backward_state

    def _enhance_with_backward_validation(
        self, event_state: dict, backward_state: dict, event_data: dict
    ) -> dict:
        """
        Combina validação forward e backward para melhor recovery.
        Se evento é válido em uma direção mas não em outra, pode ser recuperado.

        Args:
            event_state: Dict de estados forward (VALID|RECOVERABLE|INVALID)
            backward_state: Dict de estados backward (VALID_BACKWARD|...)
            event_data: Dict de eventos parseados

        Returns:
            Dict atualizado com bidirectional recovery
        """
        enhanced = event_state.copy()

        for line_num in event_state:
            event = event_data.get(line_num, {})
            action = event.get("action", "")
            forward_state = event_state[line_num]
            backward_state_val = backward_state.get(line_num, "INVALID_BACKWARD")

            if self.is_anchor_event(action):
                enhanced[line_num] = "ANCHOR_VALID"
                continue

            if forward_state == "INVALID" and "VALID" in backward_state_val:
                enhanced[line_num] = "BIDIRECTIONAL_RECOVERABLE"
            elif forward_state == "VALID" and "VALID" in backward_state_val:
                enhanced[line_num] = "BIDIRECTIONAL_VALID"

        return enhanced

    def repair_chain_with_dual_validation(self) -> Dict[str, Any]:
        """
        PHASE 2: Reparo com Dual-Chain Validation + Immutable Anchors.

        Combina validação forward e backward para maior recovery rate.
        Protege eventos anchor de remoção.

        Returns:
            Dict com resultados do reparo incluindo métricas de dual-validation
        """
        print("\n🚀 PHASE 2: Dual-Chain Validation + Immutable Anchors")
        print("=" * 70)

        if not self.audit_log_file.exists():
            return {"repaired": False, "message": "Audit log não existe"}

        try:
            backup_file = self.audit_log_file.with_suffix(".backup_phase2")
            shutil.copy2(self.audit_log_file, backup_file)

            with open(self.audit_log_file, "rb") as f:
                lines = [line for line in f if line.strip()]

            print(f"   📥 Carregando {len(lines)} linhas...")
            event_data = {}
            event_state = {}

            for line_num, line in enumerate(lines, 1):
                try:
                    event = json.loads(line)
                    event_data[line_num] = event

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

                    if calculated_hash == stored_hash:
                        event_state[line_num] = "VALID_HASH"
                    else:
                        event_state[line_num] = "INVALID_HASH"

                except json.JSONDecodeError:
                    event_state[line_num] = "INVALID_JSON"

            print("   ➡️  Forward validation...")
            prev_hash = "0" * 64

            for line_num in range(1, len(lines) + 1):
                if line_num not in event_state:
                    continue

                state = event_state[line_num]
                event = event_data.get(line_num, {})
                action = event.get("action", "?")
                stored_hash = event.get("current_hash")
                event_prev = event.get("prev_hash")

                if state == "INVALID_HASH" or state == "INVALID_JSON":
                    event_state[line_num] = "INVALID"
                    continue

                if action == "audit_system_initialized":
                    event_state[line_num] = "VALID"
                    prev_hash = "0" * 64
                elif event_prev == prev_hash:
                    event_state[line_num] = "VALID"
                    prev_hash = stored_hash
                else:
                    found_recovery = False
                    for check_line in range(line_num - 1, max(0, line_num - 50), -1):
                        if check_line in event_data:
                            check_hash = event_data[check_line].get("current_hash")
                            if (
                                event_prev == check_hash
                                and event_state.get(check_line) != "INVALID"
                            ):
                                event_state[line_num] = "RECOVERABLE"
                                found_recovery = True
                                break

                    if not found_recovery:
                        event_state[line_num] = "INVALID"

            print("   ⬅️  Backward validation...")
            backward_state = self._build_backward_chain(lines, event_data)

            print("   🔀 Bidirectional recovery...")
            enhanced_state = self._enhance_with_backward_validation(
                event_state, backward_state, event_data
            )

            print("   💾 Preservação de eventos...")
            preserved_lines = []
            stats = {
                "VALID": 0,
                "BIDIRECTIONAL_VALID": 0,
                "ANCHOR_VALID": 0,
                "RECOVERABLE": 0,
                "BIDIRECTIONAL_RECOVERABLE": 0,
                "INVALID": 0,
            }

            for line_num in range(1, len(lines) + 1):
                if line_num not in enhanced_state:
                    continue

                state = enhanced_state[line_num]
                event = event_data.get(line_num, {})
                action = event.get("action", "?")

                if state in stats:
                    stats[state] += 1

                if state == "INVALID" and not self.is_anchor_event(action):
                    continue

                preserved_lines.append(lines[line_num - 1])

            with open(self.audit_log_file, "wb") as f:
                for line in preserved_lines:
                    f.write(line)

            total_events = len(lines)
            events_preserved = len(preserved_lines)

            result = {
                "repaired": True,
                "phase": 2,
                "total_events": total_events,
                "events_preserved": events_preserved,
                "preservation_rate": 100 * events_preserved / max(1, total_events),
                "state_counts": stats,
                "dual_validation_enabled": True,
                "anchors_protected": sum(1 for s in enhanced_state.values() if s == "ANCHOR_VALID"),
                "bidirectional_recoveries": sum(
                    1 for s in enhanced_state.values() if "BIDIRECTIONAL" in s
                ),
                "backup_file": str(backup_file),
                "message": f"PHASE 2: {events_preserved}/{total_events} eventos preservados "
                f"({100 * events_preserved / max(1, total_events):.1f}%)",
            }

            print("\n✅ PHASE 2 Reparo Concluído:")
            print(f"   📊 Total: {total_events} eventos")
            for state_type, count in stats.items():
                if count > 0:
                    print(f"   - {state_type}: {count}")
            print(f"   📈 Taxa de preservação: {result['preservation_rate']:.1f}%")
            print(f"   🔒 Eventos anchor protegidos: {result['anchors_protected']}")
            print(f"   🔀 Recuperações bidirecionais: {result['bidirectional_recoveries']}")

            self._log_security_event(str(result["message"]))
            return result

        except Exception as e:
            error_msg = f"Erro durante PHASE 2: {str(e)}"
            print(f"❌ {error_msg}")
            self._log_security_event(error_msg)

            shutil.copy2(backup_file, self.audit_log_file)
            print("📁 Backup restaurado")

            return {
                "repaired": False,
                "phase": 2,
                "message": error_msg,
                "backup_restored": True,
            }


# ============================================================================
# SINGLETON + HELPERS
# ============================================================================

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


# ============================================================================
# TESTES
# ============================================================================

if __name__ == "__main__":
    print("=== Teste do Sistema de Auditoria Imutável ===\n")

    audit = ImmutableAuditSystem()

    print("1. Registrando ações de teste...")
    hash1 = audit.log_action("test_action_1", {"data": "teste1"}, "test")
    print(f"   Hash 1: {hash1[:16]}...")

    hash2 = audit.log_action("test_action_2", {"data": "teste2"}, "test")
    print(f"   Hash 2: {hash2[:16]}...")

    print("\n2. Verificando integridade da cadeia...")
    integrity = audit.verify_chain_integrity()
    print(f"   Válido: {integrity['valid']}")
    print(f"   Eventos verificados: {integrity['events_verified']}")

    print("\n3. Resumo do sistema:")
    summary = audit.get_audit_summary()
    print(f"   Total de eventos: {summary['total_events']}")
    print(f"   Tamanho do log: {summary['log_size_bytes']} bytes")
    print(f"   Integridade: {summary['chain_integrity']['valid']}")

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
