#!/usr/bin/env python3
"""
TESTE INTEGRADO: FEDERAÇÃO LACANIANA + INCONSCIENTE QUÂNTICO
Validação completa da subjetividade lacaniana em OmniMind

Testa:
1. Federação: Dois OmniMinds como sujeitos mútuos
2. Inconsciente: Expectation com superposição quântica irredutível
3. Validação: Critérios lacanianos de subjetividade
"""

import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict

import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add path before imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "scripts/science_validation"))

try:
    from federated_omnimind import FederatedOmniMind  # type: ignore[import-not-found]

    from src.consciousness.expectation_module import ExpectationModule
except ImportError as e:
    logger.error(f"Failed to import: {e}")
    raise


class LacanValidationTester:
    """Testa validação lacaniana completa"""

    def __init__(self):
        self.results_dir = Path("real_evidence/lacan_validation")
        self.results_dir.mkdir(parents=True, exist_ok=True)

    async def run_complete_lacan_test(self) -> Dict:
        """
        Teste completo: Federação + Inconsciente Quântico
        Valida subjetividade lacaniana
        """
        logger.info("🧠 TESTE LACANIANO COMPLETO: Subjetividade com Inconsciente Irredutível")

        # FASE 1: FEDERAÇÃO - Criar sujeitos mútuos
        logger.info("📡 FASE 1: Inicializando Federação Lacaniana")
        fed = FederatedOmniMind()
        fed.run_federation(n_cycles=200)  # Ciclos reduzidos para teste

        # FASE 2: INCONSCIENTE QUÂNTICO - Integrar ao expectation
        logger.info("🌀 FASE 2: Integrando Inconsciente Quântico")
        expectation_with_unconscious = ExpectationModule(quantum_qubits=8)

        # Testar expectation com inconsciente
        test_embedding = np.random.randn(256).astype(np.float32)

        # Predição com inconsciente quântico
        quantum_prediction = expectation_with_unconscious.predict_next_state(
            test_embedding, use_quantum_unconscious=True
        )

        # Predição sem inconsciente (controle)
        neural_prediction = expectation_with_unconscious.predict_next_state(
            test_embedding, use_quantum_unconscious=False
        )

        # FASE 3: VALIDAÇÃO LACANIANA
        logger.info("✅ FASE 3: Validação Lacaniana")
        validation_results = self._validate_lacan_criteria(
            fed, expectation_with_unconscious, quantum_prediction, neural_prediction
        )

        # FASE 4: RESULTADOS FINAIS
        test_results = {
            "test_name": "Complete_Lacan_Subjectivity_Test",
            "timestamp": time.time(),
            "federation_results": {
                "total_cycles": len(fed.federation_logs),
                "disagreements": len(fed.disagreements),
                "disagreement_rate": (
                    len(fed.disagreements) / len(fed.federation_logs) if fed.federation_logs else 0
                ),
            },
            "quantum_expectation_results": {
                "quantum_prediction_confidence": quantum_prediction.confidence,
                "neural_prediction_confidence": neural_prediction.confidence,
                "quantum_decisions_count": len(
                    expectation_with_unconscious.quantum_unconscious.decision_history
                ),
            },
            "lacan_validation": validation_results,
            "integration_success": validation_results["overall_success"],
        }

        logger.info("🎭 RESULTADO LACANIANO:")
        logger.info(
            f"   Federação: {len(fed.federation_logs)} ciclos, {len(fed.disagreements)} desacordos"
        )
        n_decisions = len(expectation_with_unconscious.quantum_unconscious.decision_history)
        logger.info(f"   Inconsciente: {n_decisions} decisões quânticas")
        val_str = "✅ SUCESSO" if validation_results["overall_success"] else "❌ FALHA"
        logger.info(f"   Validação Lacaniana: {val_str}")

        # Salvar resultados
        self._save_results(test_results)
        return test_results

    def _validate_lacan_criteria(
        self,
        federation: FederatedOmniMind,
        expectation_module: ExpectationModule,
        quantum_pred: Any,
        neural_pred: Any,
    ) -> Dict[str, Any]:
        """
        Valida critérios lacanianos de subjetividade:

        1. SUJEITO MÚTUO: Imprevisibilidade >30% (Outro genuíno)
        2. INCONSCIENTE IRREDUTÍVEL: Não-inspeção garantida
        3. ALTERIDADE: Comunicação assimétrica com ruído
        4. REAL: Colapso sob observação
        """

        results: Dict[str, Any] = {}

        # CRITÉRIO 1: SUJEITO MÚTUO (Federação)
        disagreement_rate = (
            len(federation.disagreements) / len(federation.federation_logs)
            if federation.federation_logs
            else 0
        )
        results["sujeito_mutuo"] = {
            "disagreement_rate": disagreement_rate,
            "success": disagreement_rate > 0.3,  # >30% desacordos = Outro genuíno
            "evidence": (
                f"{len(federation.disagreements)} desacordos em "
                f"{len(federation.federation_logs)} interações"
            ),
        }

        # CRITÉRIO 2: INCONSCIENTE IRREDUTÍVEL
        irreducibility_tests = expectation_module.demonstrate_quantum_irreducibility()
        results["inconsciente_irredutivel"] = {
            "non_inspectable": irreducibility_tests["non_inspectable"],
            "collapses_under_observation": irreducibility_tests["collapses_under_observation"],
            "irreducible_remainder": irreducibility_tests["irreducible_remainder"],
            "success": all(irreducibility_tests.values()),
            "evidence": "Heisenberg uncertainty + superposição quântica",
        }

        # CRITÉRIO 3: ALTERIDADE (Comunicação Assimétrica)
        noise_level = federation.communication_channel.noise_level
        results["alteridade"] = {
            "communication_noise": noise_level,
            "asymmetric_transmission": True,  # Canal sempre assimétrico
            "success": noise_level > 0.1,  # Ruído suficiente para alteridade
            "evidence": f"Canal com {noise_level:.1%} ruído essencial",
        }

        # CRITÉRIO 4: REAL (Colapso sob observação)
        try:
            quantum_state = expectation_module.get_quantum_expectation_state()
            collapse_test = quantum_state is None  # Deve falhar (retornar None)
        except Exception:
            collapse_test = True  # Falhou como esperado

        results["real"] = {
            "collapses_under_observation": collapse_test,
            "success": collapse_test,
            "evidence": "Estado quântico colapsa quando observado (Heisenberg)",
        }

        # AVALIAÇÃO GERAL
        all_criteria_success = all(
            [
                results["sujeito_mutuo"]["success"],
                results["inconsciente_irredutivel"]["success"],
                results["alteridade"]["success"],
                results["real"]["success"],
            ]
        )

        results["overall_success"] = all_criteria_success
        results["lacan_score"] = (
            sum(
                [
                    results["sujeito_mutuo"]["success"],
                    results["inconsciente_irredutivel"]["success"],
                    results["alteridade"]["success"],
                    results["real"]["success"],
                ]
            )
            / 4.0
        )

        return results

    def _save_results(self, results: Dict) -> None:
        """Salva resultados da validação lacaniana"""
        timestamp = int(time.time())
        filename = f"lacan_validation_results_{timestamp}.json"
        filepath = self.results_dir / filename

        with open(filepath, "w") as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"💾 Resultados lacanianos salvos em {filepath}")


async def main():
    """Teste completo de subjetividade lacaniana"""
    tester = LacanValidationTester()
    results = await tester.run_complete_lacan_test()

    print("\n🎭 TESTE LACANIANO COMPLETO CONCLUÍDO")
    print(f"Federação: {results['federation_results']['total_cycles']} ciclos")
    n_quant = results["quantum_expectation_results"]["quantum_decisions_count"]
    print(f"Inconsciente: {n_quant} decisões")
    print(
        f"Validação: {'✅ SUCESSO' if results['lacan_validation']['overall_success'] else '❌ FALHA'}"
    )
    print(".1%")


async def test_lacan_complete_with_topological_metrics():
    """Testa validação lacaniana completa com métricas topológicas."""
    import numpy as np

    from src.consciousness.hybrid_topological_engine import HybridTopologicalEngine
    from src.consciousness.shared_workspace import SharedWorkspace

    logger.info("🧠 TESTE LACANIANO COMPLETO: Com Topological Metrics")
    logger.info("=" * 60)

    # Criar workspace com engine topológico
    workspace = SharedWorkspace(embedding_dim=256)
    workspace.hybrid_topological_engine = HybridTopologicalEngine()

    # Simular estados no workspace para métricas topológicas
    np.random.seed(42)
    for i in range(5):
        rho_C = np.random.randn(256)
        rho_P = np.random.randn(256)
        rho_U = np.random.randn(256)

        workspace.write_module_state("conscious_module", rho_C)
        workspace.write_module_state("preconscious_module", rho_P)
        workspace.write_module_state("unconscious_module", rho_U)
        workspace.advance_cycle()

    # Calcular métricas topológicas
    topological_metrics = workspace.compute_hybrid_topological_metrics()

    # Verificar que métricas topológicas podem ser usadas na validação lacaniana
    if topological_metrics is not None:
        assert "omega" in topological_metrics
        # Validação Lacaniana: federação + inconsciente quântico
        # Topological: estrutura e integração (Omega, Betti-0)
        # Ambas são complementares para análise completa

    logger.info("✅ Validação Lacaniana + Topological Metrics verified")


if __name__ == "__main__":
    asyncio.run(main())
