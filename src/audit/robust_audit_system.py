"""
Sistema de Auditoria Robusta com Merkle Tree e Cadeamento Criptográfico

Implementação baseada em blockchain best practices e ISO 27037 (chain of custody).
Fornece integridade tamper-evident com verificação eficiente via Merkle proofs.
"""

import hashlib
import hmac
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class RobustChainIntegrityManager:
    """
    Gerenciador robusto de integridade de cadeia com:
    - Merkle Tree para verificação eficiente
    - Cadeamento criptográfico com HMAC-SHA256
    - Recuperação com validação de integridade
    - Detecção de tamper-evident
    """

    def __init__(self, log_dir: str, secret_key: Optional[bytes] = None):
        self.log_dir = Path(log_dir).expanduser()
        self.chain_file = self.log_dir / "cryptographic_chain.json"
        self.merkle_tree_file = self.log_dir / "merkle_tree.json"
        self.integrity_proof = self.log_dir / "integrity_proof.json"

        # Chave secreta para HMAC (usar variável de ambiente em produção)
        default_key = "omnimind-secret-key-change-in-production"
        env_key = os.getenv("AUDIT_SECRET_KEY", default_key)
        self.secret_key = secret_key or env_key.encode() if isinstance(env_key, str) else env_key
        self._load_existing_data()

    def _load_existing_data(self):
        """Carregar dados existentes da cadeia"""
        if self.chain_file.exists():
            try:
                with open(self.chain_file, "r") as f:
                    self.chain_data = json.load(f)
            except Exception as e:
                print(f"Aviso: Não foi possível carregar cadeia existente: {e}")
                self.chain_data = []
        else:
            # Inicializar cadeia vazia
            self.chain_data = []

        if self.merkle_tree_file.exists():
            try:
                with open(self.merkle_tree_file, "r") as f:
                    self.merkle_tree = json.load(f)
            except Exception as e:
                print(f"Aviso: Não foi possível carregar árvore Merkle: {e}")
                self.merkle_tree = {}
        else:
            self.merkle_tree = {}

    def _save_chain_data(self):
        """Salvar dados da cadeia em disco"""
        with open(self.chain_file, "w") as f:
            json.dump(self.chain_data, f, indent=2)

    def _save_merkle_tree(self):
        """Salvar árvore Merkle em disco"""
        with open(self.merkle_tree_file, "w") as f:
            json.dump(self.merkle_tree, f, indent=2)

    def _sha256_hash(self, data: str) -> str:
        """Calcular SHA-256 hash"""
        return hashlib.sha256(data.encode()).hexdigest()

    def _compute_hmac(self, data: str, previous_hash: str) -> str:
        """Computar HMAC-SHA256 para cadeamento criptográfico"""
        message = f"{data}:{previous_hash}".encode()
        return hmac.new(self.secret_key, message, hashlib.sha256).hexdigest()

    def _merkle_hash(self, left: str, right: str) -> str:
        """Computar hash de nó merkle"""
        combined = f"{left}{right}"
        return self._sha256_hash(combined)

    def build_merkle_tree(self, events: List[Dict[str, Any]]) -> str:
        """
        Construir árvore de Merkle para eventos
        Retorna: hash raiz da árvore (merkle root)
        """
        if not events:
            return ""

        # Nível folha: hash de cada evento
        leaves = [self._sha256_hash(json.dumps(event, sort_keys=True)) for event in events]

        # Construir árvore de baixo para cima
        tree_levels = [leaves]

        while len(tree_levels[-1]) > 1:
            current_level = tree_levels[-1]
            next_level = []

            # Processar pares de hashes
            for i in range(0, len(current_level), 2):
                if i + 1 < len(current_level):
                    parent = self._merkle_hash(current_level[i], current_level[i + 1])
                else:
                    # Nó folha sem par: duplicar o hash
                    parent = self._merkle_hash(current_level[i], current_level[i])
                next_level.append(parent)

            tree_levels.append(next_level)

        # Armazenar estrutura da árvore
        self.merkle_tree = {
            "levels": tree_levels,
            "leaf_count": len(leaves),
            "timestamp": datetime.now().isoformat(),
        }

        # Salvar árvore
        self._save_merkle_tree()

        # Retornar merkle root
        merkle_root = tree_levels[-1][0] if tree_levels[-1] else ""
        return merkle_root

    def create_merkle_proof(self, event_index: int) -> List[Tuple[str, str]]:
        """
        Gerar merkle proof para um evento específico
        Prova criptográfica que o evento está na árvore sem precisar de todos os dados
        """
        if "levels" not in self.merkle_tree:
            return []

        levels = self.merkle_tree["levels"]
        proof = []
        current_index = event_index

        for level_idx in range(len(levels) - 1):
            level = levels[level_idx]
            sibling_index = current_index + 1 if current_index % 2 == 0 else current_index - 1

            if sibling_index < len(level):
                proof.append(
                    (
                        "L" if sibling_index < current_index else "R",
                        level[sibling_index],
                    )
                )

            current_index = current_index // 2

        return proof

    def verify_merkle_proof(
        self, event: Dict[str, Any], proof: List[Tuple[str, str]], merkle_root: str
    ) -> bool:
        """
        Verificar merkle proof de um evento contra o merkle root
        Validação eficiente sem precisar de toda a árvore
        """
        event_hash = self._sha256_hash(json.dumps(event, sort_keys=True))

        for direction, sibling_hash in proof:
            if direction == "L":
                event_hash = self._merkle_hash(sibling_hash, event_hash)
            else:
                event_hash = self._merkle_hash(event_hash, sibling_hash)

        return event_hash == merkle_root

    def log_event_with_chain_integrity(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Registrar evento com integridade criptográfica de cadeia
        Retorna: evento com hash de cadeia e prova de integridade
        """
        # Obter último hash da cadeia
        previous_hash = self.chain_data[-1].get("chain_hash", "") if self.chain_data else "0" * 64

        # Serializar evento
        event_data = json.dumps(event, sort_keys=True)

        # Calcular hash do evento
        event_hash = self._sha256_hash(event_data)

        # Computar HMAC-SHA256 para cadeamento criptográfico robusto
        chain_hash = self._compute_hmac(event_data, previous_hash)

        # Estrutura do evento na cadeia
        chained_event = {
            "timestamp": datetime.now().isoformat(),
            "sequence": len(self.chain_data),
            "event": event,
            "event_hash": event_hash,
            "previous_hash": previous_hash,
            "chain_hash": chain_hash,  # HMAC que encadeia este evento ao anterior
            "integrity_valid": True,
        }

        self.chain_data.append(chained_event)
        self._save_chain_data()
        return chained_event

    def verify_chain_integrity(self) -> Dict[str, Any]:
        """
        Verificar integridade completa da cadeia
        Detecta qualquer corrupção ou tamper
        """
        if not self.chain_data:
            return {"valid": True, "events_verified": 0, "corruptions": []}

        corruptions = []
        previous_hash = "0" * 64

        for idx, event in enumerate(self.chain_data):
            # Verificar cadeamento
            expected_chain_hash = self._compute_hmac(
                json.dumps(event["event"], sort_keys=True), previous_hash
            )

            if event["chain_hash"] != expected_chain_hash:
                corruptions.append(
                    {
                        "event_index": idx,
                        "reason": "chain_hash_mismatch",
                        "expected": expected_chain_hash,
                        "actual": event["chain_hash"],
                    }
                )
                event["integrity_valid"] = False

            # Verificar hash do evento
            expected_event_hash = self._sha256_hash(json.dumps(event["event"], sort_keys=True))
            if event["event_hash"] != expected_event_hash:
                corruptions.append(
                    {
                        "event_index": idx,
                        "reason": "event_hash_mismatch",
                        "expected": expected_event_hash,
                        "actual": event["event_hash"],
                    }
                )
                event["integrity_valid"] = False

            previous_hash = event["chain_hash"]

        # Construir merkle tree para integridade global
        events_list = [e["event"] for e in self.chain_data]
        merkle_root = self.build_merkle_tree(events_list)

        result = {
            "valid": len(corruptions) == 0,
            "events_verified": len(self.chain_data),
            "corruptions": corruptions,
            "merkle_root": merkle_root,
            "timestamp": datetime.now().isoformat(),
        }

        # Salvar prova de integridade
        with open(self.integrity_proof, "w") as f:
            json.dump(result, f, indent=2)

        return result

    def recover_corrupted_events(self) -> List[Dict[str, Any]]:
        """
        Recuperar eventos considerando integridade
        Recupera apenas eventos com integridade válida verificada
        """
        recovered = []

        for event in self.chain_data:
            if event.get("integrity_valid", False):
                recovered.append(event)

        return recovered

    def export_chain_with_proofs(self, output_file: str):
        """
        Exportar cadeia com merkle proofs para cada evento
        Permite verificação independente sem acesso ao sistema
        """
        exports = []

        for idx, event in enumerate(self.chain_data):
            merkle_proof = self.create_merkle_proof(idx)
            export_item = {
                "sequence": idx,
                "event": event["event"],
                "event_hash": event["event_hash"],
                "chain_hash": event["chain_hash"],
                "merkle_proof": [{"direction": d, "hash": h} for d, h in merkle_proof],
                "timestamp": event["timestamp"],
            }
            exports.append(export_item)

        with open(output_file, "w") as f:
            json.dump(
                {
                    "chain_exports": exports,
                    "merkle_root": self.build_merkle_tree([e["event"] for e in self.chain_data]),
                    "export_timestamp": datetime.now().isoformat(),
                },
                f,
                indent=2,
            )


class RobustAuditSystem:
    """
    Sistema de Auditoria Robusta - Interface principal
    """

    def __init__(self, log_dir: str):
        self.log_dir = Path(log_dir).expanduser()
        self.chain_manager = RobustChainIntegrityManager(str(self.log_dir))

    def log_action(
        self,
        action: str,
        details: Optional[Dict[str, Any]] = None,
        category: str = "general",
    ) -> str:
        """
        Registrar ação no sistema de auditoria robusto
        Retorna: hash da cadeia do evento
        """
        if details is None:
            details = {}

        event = {
            "action": action,
            "details": details,
            "category": category,
            "hostname": os.getenv("HOSTNAME", "unknown"),
            "user": os.getenv("USER", "unknown"),
        }

        chained_event = self.chain_manager.log_event_with_chain_integrity(event)
        return chained_event["chain_hash"]

    def verify_chain_integrity(self) -> Dict[str, Any]:
        """
        Verificar integridade da cadeia
        """
        return self.chain_manager.verify_chain_integrity()

    def get_chain_summary(self) -> Dict[str, Any]:
        """
        Obter resumo da cadeia atual
        """
        integrity = self.verify_chain_integrity()
        return {
            "total_events": len(self.chain_manager.chain_data),
            "valid_events": len(
                [e for e in self.chain_manager.chain_data if e.get("integrity_valid", False)]
            ),
            "corrupted_events": len(integrity.get("corruptions", [])),
            "merkle_root": integrity.get("merkle_root", ""),
            "last_event_timestamp": (
                self.chain_manager.chain_data[-1]["timestamp"]
                if self.chain_manager.chain_data
                else None
            ),
        }

    def get_integrity_report(self) -> Dict[str, Any]:
        """
        Obter relatório detalhado de integridade
        """
        return self.verify_chain_integrity()

    def repair_chain_integrity(self) -> Dict[str, Any]:
        """
        Tentar reparar corrupções na cadeia
        """
        integrity = self.verify_chain_integrity()
        if integrity["valid"]:
            return {"repaired": True, "message": "Cadeia já está íntegra"}

        # Tentar recuperar eventos válidos
        recovered = self.chain_manager.recover_corrupted_events()

        # Reconstruir cadeia com eventos válidos
        self.chain_manager.chain_data = recovered
        self.chain_manager._save_chain_data()

        # Re-verificar
        new_integrity = self.verify_chain_integrity()

        return {
            "repaired": new_integrity["valid"],
            "recovered_events": len(recovered),
            "remaining_corruptions": len(new_integrity["corruptions"]),
            "message": ("Reparação concluída" if new_integrity["valid"] else "Reparação parcial"),
        }


# Integração no script de migração
class ImprovedAuditMigrationManager:
    """Versão melhorada do gestor de migração"""

    def __init__(self, log_dir: str = "~/projects/omnimind/logs"):
        self.log_dir = Path(log_dir).expanduser()
        self.chain_manager = RobustChainIntegrityManager(str(self.log_dir))

    def migrate_with_robust_integrity(
        self, events: List[Dict[str, Any]]
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Migrar eventos com verificação robusta de integridade
        """
        migrated_count = 0

        for event in events:
            try:
                # Log com integridade de cadeia
                self.chain_manager.log_event_with_chain_integrity(event)
                migrated_count += 1
            except Exception as e:
                print(f"Erro migrando evento: {e}")
                continue

        # Verificar integridade completa
        integrity_result = self.chain_manager.verify_chain_integrity()

        # Exportar com proofs
        self.chain_manager.export_chain_with_proofs(
            str(self.log_dir / "migrated_chain_with_proofs.json")
        )

        return integrity_result["valid"], integrity_result
