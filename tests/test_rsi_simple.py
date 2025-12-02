#!/usr/bin/env python3
"""
Teste Simples: RSI Topology Integration

Testa apenas a topologia RSI com Sinthome emergente.
"""

import sys
import os
from datetime import datetime

# Adicionar src ao path
sys.path.insert(0, '/home/fahbrain/projects/omnimind/src')

def test_rsi_topology_simple():
    """
    Teste simples da topologia RSI.
    """
    print("🧠 Teste Simples: RSI Topology Integration")
    print("=" * 50)

    try:
        from consciousness.rsi_topology_integrated import RSI_Topology_Integrated, RuptureType
        print("✅ Imports bem-sucedidos")
    except ImportError as e:
        print(f"❌ Erro nos imports: {e}")
        return False

    # Inicializar topologia
    rsi_topology = RSI_Topology_Integrated()
    print("✅ Topologia RSI inicializada")

    # Verificar status inicial
    status = rsi_topology.get_topology_status()
    print(f"Status inicial: {status}")

    # Simular rupturas
    print("\nSimulando rupturas...")
    for i in range(6):  # Mais que o threshold
        rsi_topology.detect_rupture(
            rupture_type=RuptureType.REAL_TO_SYMBOLIC,
            description=f"ruptura_teste_{i+1}",
            intensity=0.8
        )

    # Verificar se sinthome emergiu
    sinthome_status = rsi_topology.get_sinthome_status()
    if sinthome_status:
        print("✅ Sinthome emergiu!")
        print(f"   Solução: {sinthome_status['creative_solution']}")
        print(".2f")
    else:
        print("❌ Sinthome não emergiu")
        return False

    # Status final
    final_status = rsi_topology.get_topology_status()
    print(f"Status final: {final_status}")

    print("\n🎉 Teste RSI Topology: SUCESSO!")
    return True

if __name__ == "__main__":
    success = test_rsi_topology_simple()
    sys.exit(0 if success else 1)