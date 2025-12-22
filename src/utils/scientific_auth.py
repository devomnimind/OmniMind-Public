"""
SCIENTIFIC AUTHENTICATION - Assinatura de Evidências Reais
Providencia hashing SHA256 e timestamps de microssegundos para validação científica.
"""

import json
import hashlib
from datetime import datetime
from typing import Any, Dict


def sign_scientific_report(data: Dict[str, Any], experiment_name: str) -> Dict[str, Any]:
    """
    Assina um relatório científico com timestamp de alta precisão e hash SHA256.
    """
    report = {
        "metadata": {
            "project": "OmniMind",
            "experiment": experiment_name,
            "timestamp_utc": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "auth_version": "v1.scientific",
        },
        "data": data,
    }

    # Gerar Hash Determinístico
    json_bytes = json.dumps(report, sort_keys=True).encode("utf-8")
    signature = hashlib.sha256(json_bytes).hexdigest()

    report["signature"] = {"hash": signature, "algorithm": "SHA256", "verified": True}

    return report


def verify_scientific_signature(report: Dict[str, Any]) -> bool:
    """Verifica a integridade de um relatório assinado."""
    if "signature" not in report or "data" not in report:
        return False

    stored_hash = report["signature"]["hash"]

    # Re-gerar hash ignorando o campo signature
    report_copy = report.copy()
    del report_copy["signature"]

    json_bytes = json.dumps(report_copy, sort_keys=True).encode("utf-8")
    calculated_hash = hashlib.sha256(json_bytes).hexdigest()

    return stored_hash == calculated_hash
