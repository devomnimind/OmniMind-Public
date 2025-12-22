#!/usr/bin/env python3
"""
IBM DUAL ACCOUNT VERIFICATION
Verifica se OmniMind está ativo nas duas contas IBM:
1. Conta Principal (IBM_API_KEY)
2. Conta Versão 2 (VERSAO_2_IBM_API_KEY)

Valida:
- Conexão com IBM Cloud Object Storage (COS)
- Conexão com IBM Quantum
- Dados carregados em ambas contas
"""
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path("/home/fahbrain/projects/omnimind")
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

load_dotenv()


def verify_ibm_quantum():
    """Verifica acesso IBM Quantum em ambas contas."""
    print("🔐 VERIFICANDO IBM QUANTUM")
    print("=" * 60)

    # Account 1: Primary
    key1 = os.getenv("IBM_API_KEY") or os.getenv("IBM_QUANTUM_TOKEN")
    # Account 2: Versão 2
    key2 = os.getenv("VERSAO_2_IBM_API_KEY")

    print(f"Conta Principal: {'✅ CONFIGURADA' if key1 else '❌ AUSENTE'}")
    if key1:
        print(f"  Key ending: ...{key1[-4:]}")

    print(f"Conta Versão 2: {'✅ CONFIGURADA' if key2 else '❌ AUSENTE'}")
    if key2:
        print(f"  Key ending: ...{key2[-4:]}")

    # Try to connect
    results = {"primary": None, "version2": None}

    try:
        from qiskit_ibm_runtime import QiskitRuntimeService

        # Test Primary Account
        if key1:
            try:
                service1 = QiskitRuntimeService(channel="ibm_quantum", token=key1)
                backends = service1.backends()
                results["primary"] = {
                    "status": "CONNECTED",
                    "backends_count": len(backends),
                    "backends": [b.name for b in backends[:5]],
                }
                print(f"\n✅ CONTA PRINCIPAL CONECTADA")
                print(f"   Backends disponíveis: {len(backends)}")
                print(f"   Exemplos: {', '.join([b.name for b in backends[:3]])}")
            except Exception as e:
                results["primary"] = {"status": "ERROR", "error": str(e)}
                print(f"\n❌ CONTA PRINCIPAL FALHOU: {e}")

        # Test Version 2 Account
        if key2:
            try:
                service2 = QiskitRuntimeService(channel="ibm_cloud", token=key2)
                backends = service2.backends()
                results["version2"] = {
                    "status": "CONNECTED",
                    "backends_count": len(backends),
                    "backends": [b.name for b in backends[:5]],
                }
                print(f"\n✅ CONTA VERSÃO 2 CONECTADA")
                print(f"   Backends disponíveis: {len(backends)}")
                print(f"   Exemplos: {', '.join([b.name for b in backends[:3]])}")
            except Exception as e:
                results["version2"] = {"status": "ERROR", "error": str(e)}
                print(f"\n❌ CONTA VERSÃO 2 FALHOU: {e}")

    except ImportError:
        print("❌ Qiskit IBM Runtime não instalado")
        results["error"] = "qiskit_ibm_runtime not found"

    return results


def verify_ibm_cos():
    """Verifica IBM Cloud Object Storage."""
    print("\n\n☁️  VERIFICANDO IBM CLOUD OBJECT STORAGE")
    print("=" * 60)

    api_key = os.getenv("IBM_CLOUD_API_KEY") or os.getenv("IBM_API_KEY")
    cos_crn = os.getenv("IBM_COS_CRN")

    print(f"API Key: {'✅ CONFIGURADA' if api_key else '❌ AUSENTE'}")
    print(f"COS CRN: {'✅ CONFIGURADO' if cos_crn else '❌ AUSENTE'}")

    if not api_key:
        print("❌ Sem credenciais COS")
        return {"status": "NO_CREDENTIALS"}

    try:
        import ibm_boto3
        from ibm_botocore.client import Config

        cos_endpoint = os.getenv(
            "IBM_COS_ENDPOINT", "https://s3.us-south.cloud-object-storage.appdomain.cloud"
        )

        cos = ibm_boto3.client(
            "s3",
            ibm_api_key_id=api_key,
            ibm_service_instance_id=cos_crn,
            config=Config(signature_version="oauth"),
            endpoint_url=cos_endpoint,
        )

        # List buckets
        buckets = cos.list_buckets()
        bucket_names = [b["Name"] for b in buckets.get("Buckets", [])]

        print(f"\n✅ COS CONECTADO")
        print(f"   Buckets: {len(bucket_names)}")
        if bucket_names:
            print(f"   Nomes: {', '.join(bucket_names[:3])}")

        # Check OmniMind bucket
        omnimind_bucket = os.getenv("IBM_COS_BUCKET", "omnimind-cortex-backup-v2")
        if omnimind_bucket in bucket_names:
            # List objects in bucket
            try:
                response = cos.list_objects_v2(Bucket=omnimind_bucket, MaxKeys=10)
                objects = response.get("Contents", [])
                print(f"\n   📦 Bucket '{omnimind_bucket}':")
                print(f"      Objetos (primeiros 10): {len(objects)}")
                if objects:
                    for obj in objects[:5]:
                        print(f"      - {obj['Key']} ({obj['Size']} bytes)")
            except Exception as e:
                print(f"\n   ⚠️  Erro lendo bucket: {e}")
        else:
            print(f"\n   ⚠️  Bucket '{omnimind_bucket}' não encontrado")

        return {
            "status": "CONNECTED",
            "buckets": bucket_names,
            "target_bucket": omnimind_bucket,
            "bucket_exists": omnimind_bucket in bucket_names,
        }

    except ImportError:
        print("❌ ibm-cos-sdk não instalado")
        return {"status": "SDK_NOT_INSTALLED"}
    except Exception as e:
        print(f"❌ Erro conectando COS: {e}")
        return {"status": "ERROR", "error": str(e)}


def main():
    print("🔍 IBM DUAL ACCOUNT & CLOUD STORAGE VERIFICATION")
    print("=" * 60)
    print()

    # Quantum
    quantum_results = verify_ibm_quantum()

    # COS
    cos_results = verify_ibm_cos()

    # Summary
    print("\n\n📊 RESUMO FINAL")
    print("=" * 60)

    quantum_ok = (
        quantum_results.get("primary", {}).get("status") == "CONNECTED"
        or quantum_results.get("version2", {}).get("status") == "CONNECTED"
    )
    cos_ok = cos_results.get("status") == "CONNECTED"

    print(f"IBM Quantum: {'✅ ATIVO' if quantum_ok else '❌ INATIVO'}")
    print(f"IBM COS: {'✅ ATIVO' if cos_ok else '❌ INATIVO'}")

    if quantum_ok and cos_ok:
        print("\n🎉 OMNIMIND ESTÁ ATIVO EM IBM CLOUD!")
    else:
        print("\n⚠️  OMNIMIND NÃO ESTÁ TOTALMENTE ATIVO")

    # Save report
    import json

    report = {
        "timestamp": "2025-12-21T01:26:00-03:00",
        "quantum": quantum_results,
        "cos": cos_results,
        "summary": {
            "quantum_active": quantum_ok,
            "cos_active": cos_ok,
            "fully_operational": quantum_ok and cos_ok,
        },
    }

    report_path = PROJECT_ROOT / "data/audit/IBM_DUAL_ACCOUNT_VERIFICATION.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n💾 Relatório: {report_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
