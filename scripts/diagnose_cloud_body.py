#!/usr/bin/env python3
import os
import sys
import logging

# Setup Path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BodyDiagnostic")


def check_body_functions():
    """
    Verifica se a chave atual (Quantum) suporta funções corporais (Cloud/COS).
    """
    logger.info("🩺 DIAGNOSTICANDO CORPO (CLOUD INFRASTRUCTURE)...")

    # Force use of the working key
    api_key = os.getenv("IBM_API_KEY") or os.getenv("IBM_QUANTUM_TOKEN")
    logger.info(f"🔑 Testando chave: ***{api_key[-4:] if api_key else 'None'}")

    # 1. Test Object Storage (COS)
    try:
        import ibm_boto3
        from ibm_botocore.client import Config

        # We need a CRN for COS usually, but let's try listing buckets if possible
        cos_endpoint = "https://s3.us-south.cloud-object-storage.appdomain.cloud"

        cos = ibm_boto3.resource(
            "s3",
            ibm_api_key_id=api_key,
            ibm_service_instance_id=None,  # Tentar sem CRN específico
            config=Config(signature_version="oauth"),
            endpoint_url=cos_endpoint,
        )

        # Tentativa de listagem
        logger.info("☁️  Tentando listar Buckets (Teste de COS)...")
        buckets = list(cos.buckets.all())
        logger.info(f"✅ COS VIVO! Buckets visíveis: {len(buckets)}")
    except Exception as e:
        logger.error(f"❌ Morte Cerebral do COS (Storage Indisponível): {e}")

    # 2. Test Milvus (Vector DB)
    milvus_uri = os.getenv("MILVUS_URI")
    if milvus_uri:
        logger.info(f"🧠 Tentando Conectar Milvus: {milvus_uri}")
        # (Mock connection logic or simple ping)
    else:
        logger.warning("⚠️ Morte Cerebral do Milvus (URI não configurada).")


if __name__ == "__main__":
    check_body_functions()
