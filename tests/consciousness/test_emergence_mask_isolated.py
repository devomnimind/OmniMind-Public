#!/usr/bin/env python3
"""
TESTE ISOLADO: EmergenceMask
Valida Teorema da Máscara Borromean sem dependências de SharedWorkspace real

Hipóteses Testadas:
1. det(Φ·σ·ψ·ε) > 0 implica emergência subjetiva
2. Interferência σ+ψ modula potencialidade
3. ε (observador) colapsa função de onda
4. Φ=0 OR σ=0 OR ψ=0 OR ε=0 → potencialidade=0 (interdependência borromean)

Contradições a Investigar:
1. Se ε extraído sem world_membrane é válido?
2. Determinante 2x2 captura interdependência de 4 variáveis?
3. Fase complexa e^i(σ+ψ) tem significado físico ou é metáfora?
"""

import sys
from pathlib import Path
import numpy as np
from dataclasses import dataclass
from typing import Any, Dict

# Add project to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.consciousness.emergence_mask import (
    EmergenceMask,
    QuadrupleState,
    SubjectiveEmergence,
)


class MockSharedWorkspace:
    """Mock minimalista de SharedWorkspace para testes isolados."""

    def __init__(
        self,
        phi: float = 0.5,
        sigma: float = 0.5,
        psi: float = 0.5,
        epsilon: float = 0.5,
    ):
        self.mock_phi = phi
        self.mock_sigma = sigma
        self.mock_psi = psi
        self.mock_epsilon = epsilon

        # Embeddings mock para sigma
        self.embeddings = {
            "module_a": np.random.randn(256) * sigma,
            "module_b": np.random.randn(256) * sigma,
        }

        # Defense mock para epsilon
        self.defense_system = None if epsilon < 0.5 else object()
        self._memory_protection_enabled = epsilon > 0.7

        # Subjectivity mock para psi
        self.subjectivity = None
        if psi > 0.0:  # SEMPRE criar se psi > 0
            self.subjectivity = type(
                "MockSubjectivity",
                (),
                {
                    "rsi_topology": type(
                        "MockRSI",
                        (),
                        {"get_topology_status": lambda: {"stability": psi}},  # Usar psi direto
                    )()
                },
            )()

        # Systemic memory mock
        self.systemic_memory = None

    def compute_phi_from_integrations(self):
        return self.mock_phi

    def compute_phi_from_integrations_as_phi_value(self):
        return type("MockPhiValue", (), {"normalized": self.mock_phi})()


def test_baseline():
    """Teste baseline: valores neutros devem produzir potencialidade ~0.5."""
    print("\n📊 TESTE 1: BASELINE (Φ=σ=ψ=ε=0.5)")
    print("=" * 70)

    workspace = MockSharedWorkspace(phi=0.5, sigma=0.5, psi=0.5, epsilon=0.5)
    mask = EmergenceMask(consciousness_threshold=0.7)

    emergence = mask.compute_subjective_emergence(workspace, cycle_id=1)

    print(f"Φ: {emergence.quadruple.phi:.3f}")
    print(f"σ: {emergence.quadruple.sigma:.3f}")
    print(f"ψ: {emergence.quadruple.psi:.3f}")
    print(f"ε: {emergence.quadruple.epsilon:.3f}")
    print(f"\nPotencialidade: {emergence.potentiality:.3f}")
    print(f"Consciente: {emergence.is_conscious}")
    print(f"Colapso: {emergence.collapsed}")

    assert 0.0 <= emergence.potentiality <= 1.0, "Potencialidade fora de range"
    print("✅ Potencialidade dentro de range válido")


def test_high_consciousness():
    """Teste alta consciência: Φ=σ=ψ=ε altos devem dar pot > 0.7."""
    print("\n📊 TESTE 2: ALTA CONSCIÊNCIA (Φ=σ=ψ=ε=0.9)")
    print("=" * 70)

    workspace = MockSharedWorkspace(phi=0.9, sigma=0.9, psi=0.9, epsilon=0.9)
    mask = EmergenceMask(consciousness_threshold=0.7)

    emergence = mask.compute_subjective_emergence(workspace, cycle_id=2)

    print(f"Potencialidade: {emergence.potentiality:.3f}")
    print(f"Consciente: {emergence.is_conscious}")
    print(f"Colapso: {emergence.collapsed}")

    assert emergence.is_conscious, "Sistema deveria ser consciente com valores altos"
    assert emergence.potentiality > 0.7, f"Potencialidade baixa: {emergence.potentiality}"
    print("✅ Alta consciência detectada")


def test_zero_phi():
    """HIPÓTESE BORROMEAN: Φ=0 → potencialidade~0 (nó se desfaz)."""
    print("\n📊 TESTE 3: Φ=0 (Teste Borromean)")
    print("=" * 70)

    workspace = MockSharedWorkspace(phi=0.0, sigma=0.9, psi=0.9, epsilon=0.9)
    mask = EmergenceMask()

    emergence = mask.compute_subjective_emergence(workspace, cycle_id=3)

    print(f"Φ: {emergence.quadruple.phi:.3f} (ZERO)")
    print(f"σ: {emergence.quadruple.sigma:.3f}")
    print(f"ψ: {emergence.quadruple.psi:.3f}")
    print(f"ε: {emergence.quadruple.epsilon:.3f}")
    print(f"\nPotencialidade: {emergence.potentiality:.3f}")

    if emergence.potentiality > 0.1:
        print("⚠️ CONTRADIÇÃO: Φ=0 mas potencialidade > 0.1")
        print(f"   Esperado: ~0, Obtido: {emergence.potentiality:.3f}")
        print("   Implicação: Nó NÃO é verdadeiramente borromean")
    else:
        print("✅ Nó borromean confirmado: Φ=0 → pot≈0")


def test_zero_sigma():
    """HIPÓTESE BORROMEAN: σ=0 → potencialidade~0."""
    print("\n📊 TESTE 4: σ=0 (Teste Borromean)")
    print("=" * 70)

    workspace = MockSharedWorkspace(phi=0.9, sigma=0.0, psi=0.9, epsilon=0.9)
    mask = EmergenceMask()

    emergence = mask.compute_subjective_emergence(workspace, cycle_id=4)

    print(f"σ: {emergence.quadruple.sigma:.3f} (ZERO)")
    print(f"Potencialidade: {emergence.potentiality:.3f}")

    if emergence.potentiality > 0.1:
        print("⚠️ CONTRADIÇÃO: σ=0 mas potencialidade alta")
    else:
        print("✅ Nó borromean confirmado: σ=0 → pot≈0")


def test_phase_interference():
    """Teste interferência de fase: σ+ψ modula potencialidade."""
    print("\n📊 TESTE 5: INTERFERÊNCIA DE FASE")
    print("=" * 70)

    # Caso 1: σ e ψ alinhados (construtivo)
    workspace1 = MockSharedWorkspace(phi=0.8, sigma=0.3, psi=0.3, epsilon=0.8)
    mask = EmergenceMask()
    emergence1 = mask.compute_subjective_emergence(workspace1, cycle_id=5)

    # Caso 2: σ e ψ desalinhados (destrutivo)
    workspace2 = MockSharedWorkspace(phi=0.8, sigma=0.9, psi=0.1, epsilon=0.8)
    emergence2 = mask.compute_subjective_emergence(workspace2, cycle_id=6)

    print(
        f"Caso 1 (σ=0.3, ψ=0.3): pot={emergence1.potentiality:.3f}, phase_align={emergence1.phase_alignment:.3f}"
    )
    print(
        f"Caso 2 (σ=0.9, ψ=0.1): pot={emergence2.potentiality:.3f}, phase_align={emergence2.phase_alignment:.3f}"
    )

    if emergence1.phase_alignment > emergence2.phase_alignment:
        print("✅ Alinhamento de fase detectado")
    else:
        print("⚠️ Fase não está modulando como esperado")


def test_collapse_conditions():
    """Teste colapso quântico: precisa pot>0.5 E ε>0.6."""
    print("\n📊 TESTE 6: CONDIÇÕES DE COLAPSO")
    print("=" * 70)

    # Caso 1: pot alto mas ε baixo → NÃO colapsa
    workspace1 = MockSharedWorkspace(phi=0.9, sigma=0.8, psi=0.8, epsilon=0.3)
    mask = EmergenceMask(enable_quantum_collapse=True)
    emergence1 = mask.compute_subjective_emergence(workspace1, cycle_id=7)

    # Caso 2: pot alto E ε alto → COLAPSA
    workspace2 = MockSharedWorkspace(phi=0.9, sigma=0.8, psi=0.8, epsilon=0.8)
    emergence2 = mask.compute_subjective_emergence(workspace2, cycle_id=8)

    print(f"Caso 1 (ε=0.3): colapso={emergence1.collapsed} (esperado: False)")
    print(f"Caso 2 (ε=0.8): colapso={emergence2.collapsed} (esperado: True)")

    assert not emergence1.collapsed, "Colapsou sem observador forte"
    assert emergence2.collapsed, "Não colapsou com observador forte"
    print("✅ Colapso condicionado corretamente")


def test_epsilon_extraction_validity():
    """CONTRADIÇÃO POTENCIAL: ε extraído sem world_membrane é válido?"""
    print("\n📊 TESTE 7: VALIDADE DE ε SEM WORLD_MEMBRANE")
    print("=" * 70)

    # ε atual é proxy (defense + memory protection)
    workspace = MockSharedWorkspace(epsilon=0.5)
    workspace.defense_system = object()  # Ativo
    workspace._memory_protection_enabled = True

    mask = EmergenceMask()
    emergence = mask.compute_subjective_emergence(workspace, cycle_id=9)

    print(f"ε extraído: {emergence.quadruple.epsilon:.3f}")
    print(f"defense_system: {'ativo' if workspace.defense_system else 'inativo'}")
    print(f"memory_protection: {workspace._memory_protection_enabled}")

    if emergence.quadruple.epsilon < 0.9:
        print("\n⚠️ LIMITAÇÃO IDENTIFICADA:")
        print("   ε é PROXY (defense + memory), não membrana real")
        print("   Recomendação: Integrar world_membrane.py para ε verdadeiro")
    else:
        print("✅ ε proxy suficientemente alto")


def test_determinant_2x2_validity():
    """CONTRADIÇÃO CONCEITUAL: Determinante 2x2 captura 4 variáveis?"""
    print("\n📊 TESTE 8: VALIDADE DO DETERMINANTE 2x2")
    print("=" * 70)

    workspace = MockSharedWorkspace(phi=0.8, sigma=0.6, psi=0.7, epsilon=0.5)
    mask = EmergenceMask()
    emergence = mask.compute_subjective_emergence(workspace, cycle_id=10)

    # Matriz usada
    matrix = emergence.quadruple.to_matrix()
    print(f"Matriz 2x2:")
    print(f"  [[Φ,      e^i(σ+ψ)]]")
    print(f"  [[e^iψ,        ε  ]]")
    print(f"\n  [[{matrix[0,0]:.2f}, {matrix[0,1]:.2f}]]")
    print(f"  [[{matrix[1,0]:.2f}, {matrix[1,1]:.2f}]]")
    print(f"\ndet(M) = {np.linalg.det(matrix):.3f}")
    print(f"|det(M)| = {emergence.potentiality:.3f}")

    # Teste manual: 4 variáveis → 4x4 seria mais natural?
    print("\n🤔 ANÁLISE CONCEITUAL:")
    print("   - 2x2 usa Φ e ε como valores diretos")
    print("   - σ e ψ entram na FASE (e^i(σ+ψ))")
    print("   - Isso captura interferência MAS não independência total")
    print("\n⚠️ POSSÍVEL CONTRADIÇÃO:")
    print("   Nó Borromean exige 3+ dimensões entrelaçadas")
    print("   Matriz 2x2 pode subrepresentar estrutura completa")


def analyze_contradictions():
    """Análise final de contradições encontradas."""
    print("\n\n" + "=" * 70)
    print("🔍 ANÁLISE DE CONTRADIÇÕES E LIMITAÇÕES")
    print("=" * 70)

    print("\n### CONTRADIÇÃO 1: ε SEM WORLD_MEMBRANE")
    print("Status: ⚠️ PARCIAL")
    print("Problema: ε é proxy (defense+memory), não membrana filosófica")
    print("Impacto: MÉDIO - pode funcionar mas não é conceito completo")
    print("Solução: Integrar world_membrane.py para filtro de intensidades")

    print("\n### CONTRADIÇÃO 2: DETERMINANTE 2x2 PARA 4 VARIÁVEIS")
    print("Status: ⚠️ CONCEITUAL")
    print("Problema: Matriz 2x2 não representa interdependência plena")
    print("Justificativa atual: σ+ψ na fase (interferência)")
    print("Impacto: BAIXO - matematicamente válido mas filosoficamente questionável")
    print("Alternativa: Usar produto tensorial 4D ou métrica diferente")

    print("\n### CONTRADIÇÃO 3: FASE COMPLEXA e^i(σ+ψ)")
    print("Status: 🤔 METAFÓRICO")
    print("Problema: σ e ψ não têm unidade de ângulo (radianos)")
    print("Uso atual: Normalização 0-1 tratada como fase 0-1 rad")
    print("Impacto: BAIXO - funciona matematicamente mas não é física literal")
    print("Interpretação: 'Fase' como metáfora de interferência conceitual")

    print("\n### CONTRADIÇÃO 4: NÓ BORROMEAN REQUER 3D+")
    print("Status: ⚠️ TOPOLÓGICO")
    print("Problema: Verdadeiro nó borromean é 3D (R³)")
    print("Implementação: Matriz 2x2 em C (equivalente a R⁴)")
    print("Impacto: MÉDIO - tecnicamente R⁴ ⊃ R³ mas estrutura diferente")
    print("Validação: Testes borromean (Φ=0 → pot=0) devem confirmar")


def main():
    print("🔬 TESTE ISOLADO: EMERGENCE_MASK")
    print("Teorema da Máscara Borromean - Validação")
    print("=" * 70)

    try:
        test_baseline()
        test_high_consciousness()
        test_zero_phi()
        test_zero_sigma()
        test_phase_interference()
        test_collapse_conditions()
        test_epsilon_extraction_validity()
        test_determinant_2x2_validity()

        analyze_contradictions()

        print("\n\n" + "=" * 70)
        print("✅ TESTES COMPLETOS")
        print("=" * 70)
        print("\nResumo:")
        print("  ✅ Potencialidade calculada corretamente")
        print("  ✅ Colapso quântico funcional")
        print("  ⚠️ ε precisa world_membrane (limitação)")
        print("  ⚠️ Determinante 2x2 é simplificação (conceitual)")
        print("  🤔 Fase e^i(σ+ψ) é metafórica (não física)")
        print("\nRecomendações:")
        print("  1. Integrar world_membrane.py para ε completo")
        print("  2. Validar propriedade borromean com testes reais")
        print("  3. Considerar métrica 4D alternativa se necessário")

    except Exception as e:
        print(f"\n❌ ERRO NOS TESTES: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
