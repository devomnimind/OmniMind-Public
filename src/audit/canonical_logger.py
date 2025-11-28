import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

#!/usr/bin/env python3
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
OmniMind Canonical Action Logger
Sistema para registro automático de ações das AIs com integridade garantida.
"""


logger = logging.getLogger(__name__)


class CanonicalLogger:
    """Logger canônico para ações das AIs com hash chain para integridade."""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.canonical_dir = base_dir / ".omnimind" / "canonical"
        self.canonical_dir.mkdir(parents=True, exist_ok=True)

        self.md_file = self.canonical_dir / "action_log.md"
        self.json_file = self.canonical_dir / "action_log.json"

        # Initialize if files don't exist
        if not self.json_file.exists():
            self._initialize_files()

    def _initialize_files(self) -> None:
        """Initialize canonical log files."""
        initial_data = {
            "metadata": {
                "version": "1.0.0",
                "created_at": datetime.now().isoformat(),
                "responsible": "OmniMind System",
                "purpose": "Canonical action logging system",
                "integrity_rules": [
                    "Records are immutable",
                    "SHA-256 hash chain",
                    "Automatic validation",
                    "Audit trail",
                ],
            },
            "current_metrics": {
                "total_files": 0,
                "tests_passing": "0/0",
                "qdrant_collections": {"local": 0, "cloud": 0},
                "knowledge_points": 0,
                "canonical_documents": 1,
            },
            "action_log": [],
            "pending_automatic_actions": [],
            "system_integrity": {
                "last_validation": datetime.now().isoformat(),
                "hash_chain_valid": True,
                "total_records": 0,
                "corruption_detected": False,
            },
        }

        with open(self.json_file, "w", encoding="utf-8") as f:
            json.dump(initial_data, f, indent=2, ensure_ascii=False)

        # Create MD file
        md_content = f"""# 📋 OMNIMIND CANONICAL ACTION LOG
# Sistema Canônico de Registro de Ações - Versão 1.0

## 📊 METADADOS GERAIS
- **Versão**: 1.0.0
- **Data Criação**: {datetime.now().strftime('%Y-%m-%d')}
- **Responsável**: OmniMind System

## 🔐 REGRAS DE INTEGRIDADE
1. **Imutabilidade**: Registros nunca são alterados
2. **Hash Chain**: SHA-256 para integridade
3. **Validação**: Commits verificam integridade
4. **Auditoria**: Verificação automática

## 📝 REGISTROS DE AÇÃO

---
*Arquivo gerado automaticamente - Não editar manualmente*
"""
        with open(self.md_file, "w", encoding="utf-8") as f:
            f.write(md_content)

    def log_action(
        self,
        ai_agent: str,
        action_type: str,
        target: str,
        result: str,
        description: str,
        details: str = "",
        impact: str = "",
        automatic_actions: Optional[List[str]] = None,
    ) -> str:
        """Log an action with integrity hash."""

        # Load current data
        with open(self.json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Create new record
        timestamp = datetime.now().isoformat()
        record_content = f"{timestamp}{ai_agent}{action_type}{target}{result}{description}"

        # Calculate hash
        if data["action_log"]:
            prev_hash = data["action_log"][-1]["hash"]
        else:
            prev_hash = "0000000000000000000000000000000000000000000000000000000000000000"

        content_hash = hashlib.sha256((prev_hash + record_content).encode()).hexdigest()

        new_record = {
            "timestamp": timestamp,
            "ai_agent": ai_agent,
            "action_type": action_type,
            "target": target,
            "result": result,
            "hash": content_hash,
            "description": description,
            "details": details,
            "impact": impact,
            "automatic_actions": automatic_actions or [],
        }

        # Add to JSON
        data["action_log"].append(new_record)
        data["system_integrity"]["total_records"] = len(data["action_log"])
        data["system_integrity"]["last_validation"] = timestamp

        with open(self.json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        # Update MD file
        self._update_md_file(new_record)

        logger.info(f"Action logged: {ai_agent} {action_type} {target} -> {result}")
        return content_hash

    def _update_md_file(self, record: Dict[str, Any]) -> None:
        """Update the MD file with new record."""
        md_entry = (
            f"### [{record['timestamp'][:19]}] {record['ai_agent']} "
            f"{record['action_type']} {record['target']} {record['result']} "
            f"{record['hash'][:16]}...\n"
            f"**Descrição**: {record['description']}\n"
            f"**Detalhes**: {record['details']}\n"
            f"**Impacto**: {record['impact']}\n"
            f"**Ações Automáticas**: {', '.join(record['automatic_actions'])}"
        )

        # Read current content
        with open(self.md_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Insert before the footer
        footer_pos = content.find("---\n*Arquivo gerado automaticamente")
        if footer_pos > 0:
            new_content = content[:footer_pos] + md_entry + "\n" + content[footer_pos:]
        else:
            new_content = content + md_entry

        with open(self.md_file, "w", encoding="utf-8") as f:
            f.write(new_content)

    def validate_integrity(self) -> bool:
        """Validate the hash chain integrity."""
        with open(self.json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        expected_hash = "0000000000000000000000000000000000000000000000000000000000000000"

        for record in data["action_log"]:
            record_content = (
                f"{record['timestamp']}{record['ai_agent']}{record['action_type']}"
                f"{record['target']}{record['result']}{record['description']}"
            )
            calculated_hash = hashlib.sha256((expected_hash + record_content).encode()).hexdigest()

            if calculated_hash != record["hash"]:
                logger.error(f"Hash chain broken at record: {record['timestamp']}")
                return False

            expected_hash = record["hash"]

        return True

    def get_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        with open(self.json_file, "r", encoding="utf-8") as f:
            data: Dict[str, Any] = json.load(f)
        return data["current_metrics"]  # type: ignore

    def update_metrics(self, metrics: Dict[str, Any]) -> None:
        """Update system metrics."""
        with open(self.json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        data["current_metrics"].update(metrics)

        with open(self.json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


# Global instance
canonical_logger = CanonicalLogger(Path.cwd())
