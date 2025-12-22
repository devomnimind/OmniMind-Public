#!/usr/bin/env python3
import sys
import logging
from pathlib import Path
import os

# Setup Path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IBM_Verification")


def verify_connection():
    print("--- Verificando Conexão com IBM Real Backend ---")

    # Check Environment Variables
    token_v2 = os.getenv("VERSAO_2_IBM_API_KEY")
    token_quantum = os.getenv("IBM_QUANTUM_TOKEN")
    token_api = os.getenv("IBM_API_KEY")

    print(f"Token V2 presente: {bool(token_v2)}")
    print(f"Token Quantum presente: {bool(token_quantum)}")
    print(f"Token API presente: {bool(token_api)}")

    if not (token_v2 or token_quantum or token_api):
        print("❌ NENHUM TOKEN ENCONTRADO. Conexão impossível.")
        return

    try:
        from src.quantum.backends.ibm_real import IBMRealBackend

        print("\nTentando instanciar IBMRealBackend...")

        backend = IBMRealBackend()

        if backend.service:
            print("✅ Serviço Qiskit Runtime inicializado com sucesso.")
        else:
            print("⚠️ Serviço Qiskit Runtime NÃO inicializado (service is None).")

        if backend.backend:
            print(f"✅ Backend Real selecionado: {backend.backend.name}")
            print(f"   Status: {backend.backend.status()}")
        else:
            print(
                "⚠️ Nenhum backend real operacional encontrado (apenas simulador ou erro de seleção)."
            )

    except ImportError:
        print("❌ Qiskit ou dependências não instaladas.")
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")


if __name__ == "__main__":
    verify_connection()
