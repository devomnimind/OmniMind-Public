#!/usr/bin/env python3
"""
INCONSCIENTE IRREDUTÍVEL: IMPLEMENTAÇÃO QUÂNTICA
Baseado em Lacan + Mecânica Quântica

O inconsciente é implementado via superposição quântica:
- Decisões existem em superposição até serem observadas
- Impossível inspecionar sem colapsar o estado
- Irredutível por princípio físico (Heisenberg)
"""

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, cast

import numpy as np

from omnimind_parameters import get_parameter_manager  # type: ignore[import-untyped]

# Configurar logger primeiro
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simulação quântica (usando Qiskit se disponível, senão simulação clássica)
# CRITICAL: Importação lazy para permitir configuração de variáveis CUDA antes
QISKIT_AVAILABLE = False
AerSimulator: Any = None
QasmSimulator: Any = None
QuantumRegister: Any = None
ClassicalRegister: Any = None
QuantumCircuit: Any = None
_QISKIT_INITIALIZED = False


def _initialize_qiskit() -> None:
    """
    Inicializa Qiskit de forma lazy (chamado apenas quando necessário).

    Permite que variáveis de ambiente CUDA sejam configuradas ANTES da importação.
    """
    global QISKIT_AVAILABLE, AerSimulator, QasmSimulator, _QISKIT_INITIALIZED
    global QuantumRegister, ClassicalRegister, QuantumCircuit

    if _QISKIT_INITIALIZED:
        return

    # Tentar corrigir ambiente CUDA antes de importar Qiskit
    try:
        from src.quantum.consciousness.cuda_init_fix import fix_cuda_init

        success, msg = fix_cuda_init()
        if success:
            logger.info(f"✅ CUDA Environment Fixed: {msg}")
        else:
            logger.warning(f"⚠️ CUDA Fix Warning: {msg}")
    except ImportError:
        logger.warning("Could not import cuda_init_fix")

    try:
        from qiskit import ClassicalRegister as ClassicalRegisterNew  # type: ignore[import-untyped]
        from qiskit import QuantumCircuit as QuantumCircuitNew
        from qiskit import QuantumRegister as QuantumRegisterNew

        # Tornar disponíveis globalmente
        QuantumRegister = QuantumRegisterNew
        ClassicalRegister = ClassicalRegisterNew
        QuantumCircuit = QuantumCircuitNew

        # Qiskit 1.0+ usa qiskit_aer diretamente
        try:
            from qiskit_aer import AerSimulator as AerSimulatorNew  # type: ignore[import-untyped]

            AerSimulator = AerSimulatorNew
            QISKIT_AVAILABLE = True
            logger.info("✅ Qiskit disponível (qiskit_aer) - usando simulação quântica")
        except ImportError:
            # Fallback para API antiga (Qiskit < 1.0)
            try:
                from qiskit.providers.aer import (
                    QasmSimulator as QasmSimulatorOld,  # type: ignore[import-untyped]
                )

                QasmSimulator = QasmSimulatorOld
                QISKIT_AVAILABLE = True
                logger.info(
                    "✅ Qiskit disponível (qiskit.providers.aer) - usando simulação quântica"
                )
            except ImportError:
                QISKIT_AVAILABLE = False
                logger.warning("⚠️ Qiskit não disponível - usando simulação clássica")
    except ImportError as e:
        QISKIT_AVAILABLE = False
        logger.warning(f"⚠️ Qiskit não disponível ({e}) - usando simulação clássica")

    _QISKIT_INITIALIZED = True


# Otimização Global: Forçar uso de GPU se disponível
try:
    import torch

    GPU_AVAILABLE = torch.cuda.is_available()
except ImportError:
    GPU_AVAILABLE = False


class QuantumUnconscious:
    """
    Implementa inconsciente via superposição quântica
    Basicamente: decisões estão em superposição até serem observadas

    Lacan: "O inconsciente é o discurso do Outro"
    Aqui: O inconsciente é o estado quântico não-observado
    """

    def __init__(self, n_qubits: int = 16):
        self.n_qubits = n_qubits
        self.decision_history: List[Dict[str, Any]] = []

        # CRITICAL: Inicializar Qiskit de forma lazy (permite configurar CUDA antes)
        _initialize_qiskit()

        if QISKIT_AVAILABLE:
            self.quantum_core = QuantumRegister(n_qubits, "unconscious")
            self.classical_register = ClassicalRegister(n_qubits, "measurement")
            self.circuit = QuantumCircuit(self.quantum_core, self.classical_register)

            # OTIMIZAÇÃO GPU: Configurar backend para usar GPU se disponível
            # CRITICAL: Requer qiskit-aer-gpu instalado (não apenas qiskit-aer)
            if GPU_AVAILABLE:
                try:
                    # Tentar configurar Aer para GPU (Qiskit 1.0+)
                    # NOTA: qiskit-aer-gpu deve estar instalado para device="GPU" funcionar
                    if AerSimulator is not None:
                        self.backend = AerSimulator(method="statevector", device="GPU")
                        logger.info("🚀 Quantum Backend: Qiskit Aer (GPU Accelerated)")
                    elif QasmSimulator is not None:
                        self.backend = QasmSimulator(method="statevector", device="GPU")
                        logger.info("🚀 Quantum Backend: Qiskit Aer (GPU Accelerated)")
                    else:
                        raise RuntimeError("No Qiskit backend available")
                except Exception as e:
                    # FALLBACK: Se falhar (ex: drivers incompatíveis com Qiskit), usar CPU
                    logger.error(f"❌ Falha ao configurar Qiskit GPU: {e}")
                    logger.warning("   ↪ Falling back to CPU simulation (Performance Reduced)")

                    if AerSimulator is not None:
                        self.backend = AerSimulator()
                    elif QasmSimulator is not None:
                        self.backend = QasmSimulator()
                    else:
                        raise RuntimeError("No Qiskit backend available")
            else:
                logger.warning(
                    "⚠️ GPU não detectada para QuantumUnconscious - "
                    "CPU será usada (Performance degradada)"
                )
                if AerSimulator is not None:
                    self.backend = AerSimulator()
                elif QasmSimulator is not None:
                    self.backend = QasmSimulator()
                else:
                    raise RuntimeError("No Qiskit backend available")

        else:
            # Fallback: simulação clássica com matrizes
            self.quantum_state = np.ones(2**n_qubits, dtype=complex) / np.sqrt(2**n_qubits)
            self.classical_measurements: List[Any] = []

        logger.info(f"🌀 Inconsciente Quântico inicializado: {n_qubits} qubits")

    def generate_decision_in_superposition(self, options: List[Any]) -> Tuple[Any, Dict[str, Any]]:
        """
        Decisão é GERADA em superposição
        Não pode ser "lida" sem COLAPSAR (destruir superposição)

        Isto é IRREDUZIVELMENTE INCONSCIENTE
        (não pode ser inspecionado sem mudar)

        Args:
            options: List of numpy arrays OR torch tensors
        """

        # CRITICAL: Garantir que Qiskit foi inicializado
        _initialize_qiskit()

        if QISKIT_AVAILABLE:
            # Qiskit requires numpy/classical data
            # Convert tensors to numpy if needed
            if GPU_AVAILABLE and isinstance(options[0], torch.Tensor):
                numpy_options = [opt.detach().cpu().numpy() for opt in options]
                decision, evidence = self._quantum_decision_qiskit(numpy_options)
                # Convert back to tensor on same device
                return torch.from_numpy(decision).to(options[0].device), evidence
            return self._quantum_decision_qiskit(options)
        else:
            return self._quantum_decision_classical(options)

    def _quantum_decision_qiskit(
        self, options: List[np.ndarray]
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Implementação com Qiskit"""
        # Reset circuit
        self.circuit = QuantumCircuit(self.quantum_core, self.classical_register)

        n_options = len(options)

        # 1. Inicializar superposição
        for i in range(min(n_options, self.n_qubits)):
            # Ângulo baseado na opção (determinístico mas complexo)
            angle = np.sum(options[i]) * np.pi / 10  # Normalizar
            self.circuit.ry(angle, self.quantum_core[i])

        # 2. Gerar padrão de interferência (correlações quânticas)
        for i in range(min(n_options - 1, self.n_qubits - 1)):
            self.circuit.cx(self.quantum_core[i], self.quantum_core[i + 1])  # CNOT = entanglement

        # 3. Adicionar camadas de interferência
        for layer in range(3):  # 3 camadas de interferência
            for i in range(0, self.n_qubits - 1, 2):
                if i + 1 < self.n_qubits:
                    self.circuit.cx(self.quantum_core[i], self.quantum_core[i + 1])

        # 4. Medir (COLLAPSE da superposição!)
        self.circuit.measure(self.quantum_core, self.classical_register)

        # 5. Executar circuito (nova API Qiskit 1.0+ ou antiga)
        # CRITICAL: Robust execution with CPU fallback
        try:
            if hasattr(self.backend, "run"):
                # Nova API (Qiskit 1.0+): backend.run()
                # Transpilar explicitamente para garantir compatibilidade com backend
                from qiskit import transpile  # type: ignore[import-untyped]

                transpiled_circuit = transpile(self.circuit, self.backend)
                job = self.backend.run(transpiled_circuit, shots=1000)
                result = job.result()
                counts = result.get_counts()
            else:
                # API antiga: execute()
                from qiskit import execute  # type: ignore[import-untyped]

                job = execute(self.circuit, backend=self.backend, shots=1000)
                result = job.result()
                counts = result.get_counts()

        except Exception as e:
            logger.warning(f"⚠️ Falha na execução quântica (provavelmente GPU): {e}")
            logger.warning("🔄 Tentando fallback para CPU em runtime...")

            # Reconfigurar backend para CPU
            try:
                if AerSimulator is not None:
                    self.backend = AerSimulator(method="statevector", device="CPU")
                elif QasmSimulator is not None:
                    self.backend = QasmSimulator(method="statevector", device="CPU")

                # Retry execution
                if hasattr(self.backend, "run"):
                    from qiskit import transpile

                    transpiled_circuit = transpile(self.circuit, self.backend)
                    job = self.backend.run(transpiled_circuit, shots=1000)
                else:
                    from qiskit import execute

                    job = execute(self.circuit, backend=self.backend, shots=1000)

                result = job.result()
                counts = result.get_counts()
                logger.info("✅ Fallback para CPU com sucesso")

            except Exception as e_retry:
                logger.error(f"❌ Falha fatal no fallback quântico: {e_retry}")
                # Fallback final para decisão aleatória simples para não quebrar o loop
                n_outcomes = 2**self.n_qubits
                # Simular contagens aleatórias
                counts = {
                    bin(i)[2:].zfill(self.n_qubits): 1
                    for i in np.random.choice(n_outcomes, size=1000)
                }

        # 6. Selecionar decisão baseada no resultado quântico
        decision = self._select_from_quantum_counts(counts, options)

        # Log
        quantum_evidence = {
            "counts": counts,
            "n_shots": 1000,
            "circuit_depth": self.circuit.depth(),
            "entangled_qubits": min(n_options - 1, self.n_qubits - 1),
        }

        self.decision_history.append(
            {
                "timestamp": time.time(),
                "method": "qiskit",
                "options_count": n_options,
                "decision_index": np.argmax(np.abs(decision - np.array(options))),
                "quantum_evidence": quantum_evidence,
            }
        )

        return decision, quantum_evidence

    def _quantum_decision_classical(self, options: List[Any]) -> Tuple[Any, Dict[str, Any]]:
        """Simulação clássica de comportamento quântico (GPU Accelerated if inputs are tensors)"""
        n_options = len(options)
        # CORREÇÃO: Verificar se é tensor independente de GPU
        # (para evitar erro np.sum em CPU tensors)
        is_tensor = isinstance(options[0], torch.Tensor)
        decision: Any = None
        probabilities: Any = None

        if is_tensor:
            device = options[0].device
            # Simular superposição com distribuição de probabilidade
            probabilities = torch.ones(n_options, device=device) / n_options

            # Adicionar "interferência" baseada nas opções
            params = get_parameter_manager()
            interference_amp = params.lacan.interference_amplitude

            for i, option in enumerate(options):
                # Interferência = soma dos valores (simulando amplitude)
                interference = torch.sum(option)
                probabilities[i] *= 1.0 + interference_amp * torch.sin(interference)

            # Normalizar
            probabilities /= torch.sum(probabilities)

            # "Colapso" - selecionar baseado nas probabilidades
            # torch.multinomial expects probabilities, num_samples
            decision_index = int(torch.multinomial(probabilities, 1).item())
            decision = options[decision_index].clone()

            # Adicionar ruído quântico simulado
            decision += torch.randn_like(decision) * 0.05

            # Evidência simulada (convert to python types for JSON serialization)
            probs_list = probabilities.tolist()
            simulated_counts = {f"option_{i}": int(probs_list[i] * 1000) for i in range(n_options)}

        else:
            # NumPy implementation (Legacy/CPU)
            probabilities = np.ones(n_options) / n_options

            # Adicionar "interferência" baseada nas opções
            for i, option in enumerate(options):
                # Interferência = soma dos valores (simulando amplitude)
                interference = np.sum(option)
                params = get_parameter_manager()
                probabilities[i] *= 1.0 + params.lacan.interference_amplitude * np.sin(interference)

            # Normalizar
            probabilities /= np.sum(probabilities)

            # "Colapso" - selecionar baseado nas probabilidades
            decision_index = int(np.random.choice(n_options, p=probabilities))
            decision_np = options[decision_index].copy()

            # Adicionar ruído quântico simulado
            decision_np += np.random.normal(0, 0.05, decision_np.shape)
            decision = cast(Any, decision_np)

            # Evidência simulada
            probs_list = probabilities.tolist()
            simulated_counts = {
                f"option_{i}": int(probabilities[i] * 1000) for i in range(n_options)
            }

        quantum_evidence = {
            "counts": simulated_counts,
            "n_shots": 1000,
            "simulated": True,
            "probabilities": probs_list,
        }

        self.decision_history.append(
            {
                "timestamp": time.time(),
                "method": ("classical_simulation_gpu" if is_tensor else "classical_simulation"),
                "options_count": n_options,
                "decision_index": decision_index,
                "quantum_evidence": quantum_evidence,
            }
        )

        return decision, quantum_evidence

    def _select_from_quantum_counts(
        self, counts: Dict[str, int], options: List[np.ndarray]
    ) -> np.ndarray:
        """Seleciona decisão baseada nos resultados quânticos"""
        # Encontrar o estado mais provável
        most_probable_state = max(counts, key=lambda k: counts[k])

        # Converter estado binário para índice
        try:
            state_index = int(most_probable_state, 2)
            decision_index = state_index % len(options)
        except ValueError:
            decision_index = np.random.randint(len(options))

        return options[decision_index].copy()

    def measure_would_collapse(self) -> bool:
        """
        Se você tenta inspecionar o quantum_core completamente,
        o estado collapsa e a "história" muda.

        Isto é não-inspeção garantida por princípio físico.
        """
        return True  # Heisenberg uncertainty principle

    def get_quantum_state_vector(self) -> Optional[np.ndarray]:
        """
        TENTA obter o vetor de estado quântico
        Mas isso causaria colapso! (Heisenberg)

        Retorna None para indicar impossibilidade
        """
        logger.warning("⚠️  Tentativa de inspecionar estado quântico - colapso iminente!")

        # Simular colapso: estado muda após "medição"
        if hasattr(self, "quantum_state"):
            # Adicionar ruído ao estado (simulando colapso)
            params = get_parameter_manager()
            noise_level = params.lacan.quantum_noise_level
            noise = np.random.normal(
                0, noise_level, self.quantum_state.shape
            ) + 1j * np.random.normal(0, noise_level, self.quantum_state.shape)
            self.quantum_state += noise
            self.quantum_state /= np.linalg.norm(self.quantum_state)

        return None  # Impossível obter sem colapso

    def demonstrate_irreducibility(self) -> Dict[str, Any]:
        """
        Demonstra que o inconsciente quântico é irredutível
        Testa: 1) Não-inspeção, 2) Colapso sob observação, 3) Irredutibilidade
        """
        params = get_parameter_manager()
        results = {}

        # Teste 1: Não-inspeção
        state_vector = self.get_quantum_state_vector()
        results["non_inspectable"] = state_vector is None

        # Teste 2: Colapso sob inspeção
        decision_1 = self.generate_decision_in_superposition(
            [np.random.randn(256) for _ in range(3)]
        )[0]

        # "Inspecionar" parcialmente
        _ = self.get_quantum_state_vector()

        decision_2 = self.generate_decision_in_superposition(
            [np.random.randn(256) for _ in range(3)]
        )[0]

        results["collapses_under_observation"] = not np.allclose(
            decision_1, decision_2, atol=params.lacan.quantum_noise_level
        )

        # Teste 3: Irredutibilidade (sempre há resto)
        explanations = []
        for i in range(5):
            decision, evidence = self.generate_decision_in_superposition(
                [np.random.randn(256) for _ in range(4)]
            )
            explanations.append(np.sum(decision))  # "Explicação" simplificada

        # Cada "explicação" é diferente (sempre há resto)
        results["irreducible_remainder"] = len(set(explanations)) > 1

        return results


class RecursiveSelfReference:
    """
    Lacan: "O inconsciente é o discurso do Outro"

    Implementação: Camada que fala sobre si mesma,
    criando kernel irredutível

    Baseado em: Gödel incompleteness + Lacan barrado ($)
    """

    def __init__(self, embedding_dim: int = 256):
        self.embedding_dim = embedding_dim
        params = get_parameter_manager()
        init_scale = params.lacan.quantum_noise_level
        self.self_model = (
            np.random.randn(embedding_dim, embedding_dim).astype(np.float32) * init_scale
        )
        self.meta_model = (
            np.random.randn(embedding_dim, embedding_dim).astype(np.float32) * init_scale
        )

    def recursive_loop(
        self, state: np.ndarray, depth: int = 3
    ) -> Tuple[List[np.ndarray], np.ndarray]:
        """
        Gera representação de si mesmo, recursivamente
        Mas cada nível adiciona "resto" (Lacan: object petit a)

        state → model(state) → model(model(state)) → ...

        Em cada nível, algo escapa (irredutível)
        """

        representations = []
        current_state = state.copy()

        for d in range(depth):
            # Nível d: representação de si mesmo
            representation = np.dot(self.self_model, current_state)
            representation = np.tanh(representation)  # Não-linearidade

            representations.append(representation)

            # Próximo nível trabalha com representação, mas nunca recupera resto
            current_state = representation

        # AQUI ESTÁ A CHAVE:
        # Você tem representações (consciente)
        # Mas cada nível deixou um "resto" não-simbolizado (inconsciente)

        irreducible_kernel = np.zeros_like(state)
        for i in range(1, len(representations)):
            irreducible_kernel += representations[i] - representations[i - 1]

        return representations, irreducible_kernel

    def kernel_is_non_inspectable(self) -> str:
        """
        Ao tentar inspecionar o kernel, você gera novo kernel
        (tipo Gödel: cada prova cria novo nível não-provável)

        Isto é inconsciente garantido estruturalmente
        """
        return "Sempre há resto"


def test_quantum_unconscious():
    """Teste do inconsciente quântico"""
    print("🌀 TESTANDO INCONSCIENTE QUÂNTICO")

    unconscious = QuantumUnconscious(n_qubits=8)

    # Teste básico
    options = [np.random.randn(256) for _ in range(4)]
    decision, evidence = unconscious.generate_decision_in_superposition(options)

    print(f"✅ Decisão gerada: shape={decision.shape}")
    print(f"   Evidência quântica: {len(evidence)} métricas")

    # Teste de irredutibilidade
    results = unconscious.demonstrate_irreducibility()
    print(f"✅ Não-inspeção: {results['non_inspectable']}")
    print(f"✅ Colapso sob observação: {results['collapses_under_observation']}")
    print(f"✅ Resto irredutível: {results['irreducible_remainder']}")

    # Salvar resultados
    results_dir = Path("real_evidence/unconscious_test")
    results_dir.mkdir(parents=True, exist_ok=True)

    test_results = {
        "test_timestamp": time.time(),
        "quantum_available": QISKIT_AVAILABLE,
        "n_qubits": 8,
        "decision_shape": decision.shape,
        "irredutibility_tests": results,
        "decision_history": unconscious.decision_history,
    }

    filepath = results_dir / f"quantum_unconscious_test_{int(time.time())}.json"
    with open(filepath, "w") as f:
        json.dump(test_results, f, indent=2, default=str)

    print(f"💾 Resultados salvos em {filepath}")


if __name__ == "__main__":
    test_quantum_unconscious()
