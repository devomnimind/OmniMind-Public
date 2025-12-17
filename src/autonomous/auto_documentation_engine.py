"""Auto Documentation Engine - Phase 26C

Documents adaptations automatically.

Author: OmniMind Development
License: MIT
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


class AutoDocumentationEngine:
    """Documenta automaticamente o que foi feito"""

    def __init__(self, log_dir: Path | None = None):
        """Initialize documentation engine

        Args:
            log_dir: Directory for adaptation logs (default: logs/autonomous)
        """
        if log_dir is None:
            base_dir = Path(__file__).resolve().parents[2]
            log_dir = base_dir / "logs" / "autonomous"

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"AutoDocumentationEngine initialized: {self.log_dir}")

    def document_adaptation(
        self, issue: Dict[str, Any], solution: Dict[str, Any], result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create adaptation documentation

        Args:
            issue: Issue dictionary
            solution: Solution dictionary
            result: Result dictionary (success, metrics_before, metrics_after, etc)

        Returns:
            Documentation dict
        """
        doc = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "issue": {
                "type": issue.get("type", ""),
                "severity": issue.get("severity", ""),
                "description": issue.get("description", ""),
            },
            "solution": {
                "source": solution.get("source", ""),
                "applied": solution.get("solution", {}),
                "confidence": solution.get("confidence", 0.0),
            },
            "result": {
                "success": result.get("success", False),
                "metrics_before": result.get("metrics_before", {}),
                "metrics_after": result.get("metrics_after", {}),
                "improvement_percent": result.get("improvement_percent", 0.0),
            },
            "machine": {
                "specs": result.get("machine_specs", {}),
                "framework_version": result.get("framework_version", "unknown"),
            },
            "rollback": {
                "available": True,
                "command": result.get("rollback_command", "N/A"),
            },
        }

        # Save to log file
        log_file = self.log_dir / "autonomous_adaptations.jsonl"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")

        # Also update solutions database (for future lookups)
        self._update_solutions_db(issue, solution, result)

        logger.info(f"📝 Documentação salva: {log_file}")

        return doc

    def _update_solutions_db(
        self, issue: Dict[str, Any], solution: Dict[str, Any], result: Dict[str, Any]
    ) -> None:
        """Update solutions database with new solution

        Args:
            issue: Issue dict
            solution: Solution dict
            result: Result dict
        """
        if not result.get("success", False):
            return  # Only document successful solutions

        base_dir = Path(__file__).resolve().parents[2]
        solutions_db = base_dir / "data" / "known_solutions.json"

        if not solutions_db.exists():
            return  # Solutions DB not available

        try:
            with open(solutions_db, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Add new solution
            new_solution = {
                "id": f"auto_{datetime.now(timezone.utc).isoformat()}",
                "source": "autonomous_adaptation",
                "problem": {
                    "description": issue.get("description", ""),
                    "type": issue.get("type", ""),
                },
                "solution": {
                    "description": str(solution.get("solution", {})),
                    "confidence": 0.9,  # High confidence (validated and applied)
                },
                "metadata": {
                    "applied_at": datetime.now(timezone.utc).isoformat(),
                    "improvement": result.get("improvement_percent", 0.0),
                    "machine_specs": result.get("machine_specs", {}),
                },
            }

            data["solutions"].append(new_solution)
            data["total_solutions"] = len(data["solutions"])

            with open(solutions_db, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info("✅ Solutions database atualizado")

        except Exception as e:
            logger.warning(f"Error updating solutions DB: {e}")
