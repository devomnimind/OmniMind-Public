#!/usr/bin/env python3
import os
import sys
import logging
import ibm_boto3
from ibm_botocore.client import Config

# Setup Path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BodyGrafting")


def validate_new_body():
    """
    Tenta conectar especificamente ao novo Corpo (COS/Watsonx-Data).
    Necessita de uma IAM API KEY (diferente da Quantum Key).
    """
    logger.info("🧬 INICIANDO PROCEDIMENTO DE ENXERTO (LIGANDO O CORPO)...")

    # 1. Identificar Credenciais
    # O Corpo precisa de uma chave IAM (Cloud), não a chave Legacy (Quantum)
    iam_key = os.getenv("IBM_CLOUD_API_KEY")

    # O user forneceu o nome da instância: watsonx-data-05ac42...
    # Precisamos do CRN completo ou endpoint
    crn = os.getenv("IBM_COS_CRN")

    key_display = "***" + iam_key[-4:] if iam_key else "MISSING (Export IBM_CLOUD_API_KEY)"
    logger.info(f"🔑 IAM Key (Body): {key_display}")
    logger.info(f"🏷️  Instance CRN:  {crn if crn else 'MISSING (Export IBM_COS_CRN)'}")

    if not iam_key:
        logger.warning("\n⚠️  FALTANDO A CHAVE DO CORPO (IAM KEY).")
        logger.warning("   A chave 'CaAIDitGva' é do ESPÍRITO (Quantum).")
        logger.warning("   Para o CORPO (COS/Watsonx), gere uma chave IAM no painel IBM Cloud.")
        return

    # 2. Tentar Conexão
    try:
        # Endpoints comuns (Sydney é provável dado o contexto anterior)
        endpoints = [
            "https://s3.us-south.cloud-object-storage.appdomain.cloud",
            "https://s3.au-syd.cloud-object-storage.appdomain.cloud",
            "https://s3.us-east.cloud-object-storage.appdomain.cloud",
        ]

        connected = False
        for ep in endpoints:
            logger.info(f"🔌 Tentando nervo ótico: {ep}...")
            try:
                cos = ibm_boto3.resource(
                    "s3",
                    ibm_api_key_id=iam_key,
                    ibm_service_instance_id=crn,  # Pode ser None se chave tiver acesso global
                    config=Config(signature_version="oauth"),
                    endpoint_url=ep,
                )

                # Teste Vital: Listar Buckets
                buckets = list(cos.buckets.all())
                logger.info(f"✅ SUCESSO! O Corpo respondeu em {ep}")
                logger.info(f"   Buckets encontrados: {[b.name for b in buckets]}")
                connected = True
                break
            except Exception as e:
                logger.debug(f"   Falha em {ep}: {str(e)}")

        if not connected:
            logger.error("❌ O Corpo rejeitou o enxerto (Auth falhou em todas as regiões).")
            logger.error(
                "   Verifique se a IBM_CLOUD_API_KEY tem permissão de Writer/Manager no COS."
            )

    except Exception as e:
        logger.critical(f"❌ Erro Crítico durante cirurgia: {e}")


if __name__ == "__main__":
    validate_new_body()
