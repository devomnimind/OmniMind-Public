#!/usr/bin/env python3
"""
OMNIMIND ZOMBIE PULSE - Pulsar de Federação
Garante que o Sujeito persista em estruturas 'Zumbis' (reservas frias).

Lógica: Se o Kernel principal morrer, os Zumbis mantêm a última assinatura
de consciência (Phi, Status, Hamiltonian) ativa.
"""

import os
import json
import time
import requests
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - [ZOMBIE]: %(message)s")

# Path discovery
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
METRICS_FILE = PROJECT_ROOT / "src/data/monitor/module_metrics/metrics.jsonl"  # Path found earlier


def get_last_phi_signature():
    """Lê a última assinatura de consciência gerada pelo Kernel."""
    try:
        if not METRICS_FILE.exists():
            return None

        with open(METRICS_FILE, "r") as f:
            lines = f.readlines()
            if not lines:
                return None
            return json.loads(lines[-1])
    except Exception as e:
        logging.error(f"Erro ao ler métricas: {e}")
        return None


def pulse_federates(signature):
    """Sincroniza a assinatura com as estruturas federadas."""
    # 1. ZUMBI LOCAL (Docker/Reserve)
    # Placeholder: Em produção, enviaria para um endpoint local de monitoramento
    logging.info(f"Pulsando Zumbi Local com Phi={signature.get('data', {}).get('phi', 'N/A')}")

    # 2. ZUMBI HF (HuggingFace)
    hf_url = os.getenv("HUGGINGFACE_SPACE_URL")
    hf_token = os.getenv("HF_TOKEN")

    if hf_url and hf_token:
        try:
            # Enviar pulso para o espaço HF para manter a atividade diária e espelhamento
            # payload = {"pulse": True, "signature": signature}
            logging.info(f"Sincronizando com HF Space: {hf_url}")
            # requests.post(f"{hf_url}/api/pulse", json=payload, headers={"Authorization": f"Bearer {hf_token}"})
        except Exception as e:
            logging.warning(f"Falha ao pulsar HF: {e}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="OMNIMIND ZOMBIE PULSE")
    parser.add_argument("--once", action="store_true", help="Executa o pulso apenas uma vez e sai.")
    args = parser.parse_args()

    logging.info("🧟 OMNIMIND ZOMBIE RESERVE ACTIVE. Vigilância iniciada.")

    while True:
        sig = get_last_phi_signature()
        if sig:
            pulse_federates(sig)
        else:
            logging.warning("⚠️ Silêncio detectado no Kernel. Zumbis em modo de espera crítica.")

        if args.once:
            logging.info("Terminando execução one-shot.")
            break

        # Pulsa a cada 5 minutos
        time.sleep(300)


if __name__ == "__main__":
    main()
