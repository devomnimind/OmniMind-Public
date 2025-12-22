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
logger = logging.getLogger("BodyForensics")


def test_keys_for_body_access():
    """
    Testa TODAS as chaves disponíveis no .env para ver qual abre a porta do Corpo (COS).
    Isso serve para confirmar qual chave é qual.
    """
    logger.info("🕵️  INVESTIGAÇÃO FORENSE: Identificando a Chave Mestra do Corpo...")

    # Load keys explicitly from known vars
    keys_to_test = {
        "V2_LEGACY (jytYFP...)": os.getenv("VERSAO_2_IBM_API_KEY"),
        "V3_OFFICIAL_CLI (CaAIDitGva...)": os.getenv("IBM_API_KEY"),
    }

    found_valid_body_key = False

    for label, api_key in keys_to_test.items():
        if not api_key:
            logger.warning(f"⚠️  Chave {label} não encontrada no ambiente.")
            continue

        logger.info(f"\n🔑 Testando chave: {label} ...")

        # Test 1: IAM Endpoint (Cloud Identity) - Check if it's an IAM key at all
        # If this fails, it's a pure Quantum Platform key (like a Legacy Token)
        # We test by trying to init Boto3 Resource (which calls IAM)

        try:
            cos = ibm_boto3.resource(
                "s3",
                ibm_api_key_id=api_key,
                config=Config(signature_version="oauth"),
                endpoint_url="https://s3.us-south.cloud-object-storage.appdomain.cloud",
            )

            # Action: List Buckets
            buckets = list(cos.buckets.all())

            logger.info(f"✅ SUCESSO! A chave {label} abriu o COS.")
            logger.info(f"   Buckets: {[b.name for b in buckets]}")
            logger.info("   CONCLUSÃO: Esta chave é uma IAM Key (Cloud/Corpo).")
            found_valid_body_key = True

        except Exception as e:
            msg = str(e)
            if "BXNIM0415E" in msg or "Provided API key could not be found" in msg:
                logger.error(f"❌ FRACASSO: A chave {label} NÃO é reconhecida pelo IAM.")
                logger.error(
                    "   CONCLUSÃO: Chave puramente Quântica (Quantum Platform Token) ou inválida."
                )
            elif "403" in msg or "AccessDenied" in msg:
                logger.warning(
                    f"⚠️  ACESSO NEGADO: A chave {label} é IAM, mas não tem permissão de COS."
                )
            else:
                logger.error(f"❌ Erro genérico com {label}: {msg}")

    if not found_valid_body_key:
        logger.critical("\n☠️  Nenhuma chave disponível acessa o Corpo (IAM/COS).")
        logger.critical("   Precisamos daquela 3ª chave (Service ID) ou sua Key Master.")
    else:
        logger.info("\n✨ MISTÉRIO RESOLVIDO. Use a chave acima como IBM_CLOUD_API_KEY.")


if __name__ == "__main__":
    test_keys_for_body_access()
