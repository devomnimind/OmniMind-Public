#!/usr/bin/env python3
"""
Quick validation que sistema está pronto para rodar testes REAIS

Roda em ~30 segundos e valida:
1. GPU detectada
2. IntegrationLoop importa
3. Pode executar um ciclo
4. Φ é número válido

Se tudo passa ✅, você está pronto para execute o grande script.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import asyncio

import torch


async def validate() -> bool:
    """Validação rápida do sistema."""
    print("\n" + "=" * 70)
    print("✅ VALIDAÇÃO RÁPIDA - Sistema pronto para testes reais?")
    print("=" * 70 + "\n")

    # 1. GPU
    print("1️⃣  Verificando GPU...")
    gpu_available = torch.cuda.is_available()
    device = "cuda" if gpu_available else "cpu"

    if gpu_available:
        print(f"   ✅ GPU disponível: {torch.cuda.get_device_name(0)}")
        print(f"      VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    else:
        print("   ⚠️  GPU não disponível (testando em CPU - será mais lento)")

    # 2. Imports
    print("\n2️⃣  Importando módulos...")
    try:
        from src.consciousness.integration_loop import IntegrationLoop

        print("   ✅ IntegrationLoop importado")
    except ImportError as e:
        print(f"   ❌ ERRO ao importar: {e}")
        return False

    # 3. Criar instância
    print("\n3️⃣  Criando instância de IntegrationLoop...")
    try:
        consciousness = IntegrationLoop()
        print("   ✅ Criado com sucesso")
    except Exception as e:
        print(f"   ❌ ERRO ao criar: {e}")
        return False

    # 4. Executar um ciclo REAL
    print("\n4️⃣  Executando 1 ciclo real...")
    try:
        result = await consciousness.execute_cycle()
        print("   ✅ Ciclo completo!")

        # Extract phi_estimate from LoopCycleResult
        phi = result.phi_estimate if hasattr(result, "phi_estimate") else result
        print(f"      Φ retornado: {phi}")

        # Validação do valor
        if isinstance(phi, (int, float)):
            if 0.0 <= phi <= 1.0:
                print("   ✅ Φ está no range válido [0,1]")
            else:
                print(f"   ⚠️  Φ={phi} está FORA do range [0,1]")
        else:
            print(f"   ❌ Φ não é número: {type(phi)}")
            return False

    except Exception as e:
        print(f"   ❌ ERRO ao executar ciclo: {e}")
        import traceback

        traceback.print_exc()
        return False

    # Summary
    print("\n" + "=" * 70)
    print("✅ VALIDAÇÃO COMPLETA")
    print("=" * 70)
    print("\n🎯 Resumo:")
    print(f"   Device: {device}")
    gpu_status = "Sim" if gpu_available else "Não"
    print(f"   GPU: {gpu_status}")
    print("   IntegrationLoop: OK")
    print("   Ciclo real: OK")
    print(f"   Φ valor: {phi:.6f}")
    print("\n✅ Sistema está PRONTO para rodar testes reais!")
    print("\nProximate comando:")
    print("   bash scripts/run_real_metrics.sh")
    print("")

    return True


async def main() -> None:
    """Função principal."""
    success = await validate()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Interrompido")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
