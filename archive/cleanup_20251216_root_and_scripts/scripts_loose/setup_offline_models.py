#!/usr/bin/env python3
"""
Script para configurar fallback offline para modelos HuggingFace.

Garante que modelos críticos estejam disponíveis localmente
e configura variáveis de ambiente para modo offline quando apropriado.
"""

import os
from pathlib import Path


def setup_offline_mode():
    """Configura modo offline para evitar requests desnecessários."""
    print("🔧 Configurando modo offline para modelos HuggingFace...")

    # Modelos críticos que devem estar disponíveis localmente
    critical_models = [
        "sentence-transformers/all-MiniLM-L6-v2",
    ]

    cache_dir = Path.home() / ".cache" / "huggingface" / "hub"

    for model_name in critical_models:
        model_dir_name = f"models--{model_name.replace('/', '--')}"
        model_dir = cache_dir / model_dir_name

        if model_dir.exists():
            print(f"✅ {model_name}: encontrado em cache")

            # Verificar snapshots
            snapshots_dir = model_dir / "snapshots"
            if snapshots_dir.exists():
                snapshots = list(snapshots_dir.glob("*"))
                if snapshots:
                    latest_snapshot = max(snapshots, key=lambda x: x.stat().st_mtime)
                    print(f"   📁 Snapshot: {latest_snapshot.name}")

                    # Verificar arquivos essenciais
                    essential_files = ["model.safetensors", "config.json", "tokenizer.json"]
                    missing = []
                    for file in essential_files:
                        if not (latest_snapshot / file).exists():
                            missing.append(file)

                    if missing:
                        print(f"   ⚠️ Arquivos faltando: {missing}")
                    else:
                        print("   ✅ Arquivos completos")
                else:
                    print("   ❌ Nenhum snapshot encontrado")
            else:
                print("   ❌ Diretório snapshots não encontrado")
        else:
            print(f"❌ {model_name}: não encontrado em cache")
            print(f"   💡 Para baixar: huggingface-cli download {model_name}")

    # Configurar variáveis de ambiente para modo offline quando cache estiver disponível
    print("\n🔧 Configurando variáveis de ambiente...")

    # Verificar se podemos operar offline
    can_work_offline = True
    for model_name in critical_models:
        model_dir_name = f"models--{model_name.replace('/', '--')}"
        model_dir = cache_dir / model_dir_name
        if not model_dir.exists():
            can_work_offline = False
            break

    if can_work_offline:
        print("✅ Sistema pode operar offline - modelos críticos disponíveis")
        print("💡 Configure HF_HUB_OFFLINE=1 para forçar modo offline")
    else:
        print("⚠️ Sistema requer conexão para baixar modelos faltantes")

    return can_work_offline


def test_offline_loading():
    """Testa carregamento offline dos modelos."""
    print("\n🧪 Testando carregamento offline...")

    try:
        # Forçar modo offline
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

        from sentence_transformers import SentenceTransformer

        model_path = str(
            Path.home()
            / ".cache"
            / "huggingface"
            / "hub"
            / "models--sentence-transformers--all-MiniLM-L6-v2"
            / "snapshots"
            / "c9745ed1d9f207416be6d2e6f8de32d1f16199bf"
        )

        print("Carregando modelo offline...")
        model = SentenceTransformer(model_path, device="cpu", local_files_only=True)

        # Teste rápido
        test_text = "This is a test for offline model loading."
        embedding = model.encode(test_text, normalize_embeddings=True)

        print("✅ Modelo carregado offline com sucesso")
        print(f"   📏 Dimensão do embedding: {len(embedding)}")

        return True

    except Exception as e:
        print(f"❌ Erro no carregamento offline: {e}")
        return False
    finally:
        # Limpar variáveis de ambiente
        os.environ.pop("HF_HUB_OFFLINE", None)
        os.environ.pop("HF_HUB_DISABLE_TELEMETRY", None)


if __name__ == "__main__":
    print("🚀 Configuração de Fallback Offline - OmniMind")
    print("=" * 50)

    # Verificar e configurar
    can_work_offline = setup_offline_mode()

    # Testar se funciona
    if can_work_offline:
        test_offline_loading()

    print("\n📋 Recomendações:")
    if can_work_offline:
        print("✅ Configure 'HF_HUB_OFFLINE=1' no ambiente para evitar requests desnecessários")
        print("✅ O sistema funcionará mesmo sem conexão com HuggingFace")
    else:
        print("⚠️ Baixe os modelos faltantes antes de operar offline")
        print("💡 Comando: huggingface-cli download sentence-transformers/all-MiniLM-L6-v2")

    print("\n✨ Configuração concluída!")
