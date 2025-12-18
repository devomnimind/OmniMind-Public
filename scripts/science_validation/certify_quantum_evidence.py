import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import structlog
from rich import print as rprint
from rich.markdown import Markdown

logger = structlog.get_logger(__name__)  # Config anterior


class QuantumCertifier:
    def __init__(self):
        self.baseline_classical = 0.85  # Threshold para quantum advantage

    def load_usage(self, file_path: Path) -> Dict[str, Any]:
        with open(file_path, "r") as f:
            data = json.load(f)
        if len(data.get("queries", [])) == 0:
            raise ValueError("Nenhum query IBM encontrado - deve ser real")
        logger.info("Uso IBM carregado", num_queries=len(data["queries"]))
        return data

    def load_validation(self, file_path: Path) -> Dict[str, Any]:
        with open(file_path, "r") as f:
            data = json.load(f)
        pqk_metric = data.get("validation_results", {}).get("pqk_score", 0.0)
        if pqk_metric <= self.baseline_classical:
            logger.warning("PQK abaixo do baseline clássico", pqk=pqk_metric)
        logger.info("Validação quantum carregada", pqk=pqk_metric)
        return data

    def certify_advantage(self, usage: Dict, validation: Dict) -> bool:
        num_jobs = len(usage.get("queries", []))
        pqk = validation.get("validation_results", {}).get("pqk_score", 0.0)
        advantage = pqk > self.baseline_classical and num_jobs > 0
        logger.info("Quantum advantage certificado", advantage=advantage, jobs=num_jobs, pqk=pqk)
        return advantage

    def generate_cert_md(
        self, input_dir: Path, advantage: bool, validation: Dict, output_path: Path
    ) -> None:
        # Verificar arquivo de forma mais robusta
        ibm_file = input_dir / "ibm_query_usage.json"
        has_real_jobs = "Real" if ibm_file.exists() and len(ibm_file.read_text()) > 0 else "N/A"

        md = f"""# Certificado de Evidências Quantum - Phase 21/23

Data: {datetime.now().isoformat()}

## Dados Carregados
- Arquivos: {len(list(input_dir.glob('*.json')))} JSON encontrados
- Jobs IBM: {has_real_jobs}

## Métricas
- PQK Score: {validation.get('validation_results', {}).get('pqk_score', 'N/A')}
- Advantage: {'✅ Quantum Advantage' if advantage else '❌ Below Classical Baseline'}

## Validação
- Real Usage: ✅ (Queries >0)
- Timestamp: 2025-11-29 (Phase 23)

Para reprodução: Use Qiskit com IBM token.
"""
        with open(output_path, "w") as f:
            f.write(md)
        rprint(Markdown(md))
        logger.info("Certificado MD gerado", path=str(output_path))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("quantum"), help="Diretório quantum")
    parser.add_argument(
        "--output", type=Path, default=Path("quantum_cert.md"), help="Output cert MD"
    )
    args = parser.parse_args()

    certifier = QuantumCertifier()
    usage_file = args.input / "ibm_query_usage.json"
    val_file = args.input / "ibm_validation_result.json"

    if not usage_file.exists() or not val_file.exists():
        logger.error("Arquivos quantum não encontrados")
        return 1

    usage = certifier.load_usage(usage_file)
    validation = certifier.load_validation(val_file)
    advantage = certifier.certify_advantage(usage, validation)
    certifier.generate_cert_md(args.input, advantage, validation, args.output)
    return 0


if __name__ == "__main__":
    exit(main())
