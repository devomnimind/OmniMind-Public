import sys
import os
import logging

sys.path.append(os.getcwd())

# Configurar logging para stdout
logging.basicConfig(level=logging.INFO)

try:
    from src.integrations.ibm_cloud_connector import IBMCloudConnector

    print("✅ Módulo importado com sucesso.")
except ImportError as e:
    print(f"❌ Falha ao importar módulo: {e}")
    sys.exit(1)


def test_connection():
    try:
        connector = IBMCloudConnector()
        status = connector.get_infrastructure_status()
        print("\n📊 Status da Infraestrutura:")
        for k, v in status.items():
            print(f"  - {k}: {v}")

        if status["cos_status"] == "Active":
            print("\n🧪 Testando upload_memory...")
            test_data = b"Memory Verification Artifact - Timestamp: Post-Crash Audit"
            success = connector.upload_memory("verification_test_artifact.txt", test_data)
            if success:
                print("✅ Upload de memória bem-sucedido!")
            else:
                print("❌ Falha no upload de memória.")
        else:
            print("\n⚠️ Pular teste de upload (COS desconectado).")

    except Exception as e:
        print(f"\n❌ Erro durante teste: {e}")


if __name__ == "__main__":
    test_connection()
