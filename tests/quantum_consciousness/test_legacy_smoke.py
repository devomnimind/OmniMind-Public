import importlib

import pytest

LEGACY_MODULES = [
    "src.quantum_consciousness.quantum_backend",
    "src.quantum_consciousness.quantum_cognition",
    "src.quantum_consciousness.quantum_memory",
    "src.quantum_consciousness.qpu_interface",
    "src.quantum_consciousness.hybrid_cognition",
]


@pytest.mark.parametrize("module_path", LEGACY_MODULES)
def test_legacy_module_import_smoke(module_path):
    """
    Smoke test: importa módulos legados sem executar caminhos pesados.
    Se dependência opcional faltar, marca como skip.
    """
    try:
        module = importlib.import_module(module_path)
    except ImportError as exc:  # dependência opcional ausente
        pytest.skip(f"Dep opcional faltando para {module_path}: {exc}")
    assert module.__name__ == module_path


def test_quantum_decision_fallback(monkeypatch):
    """
    Exercita ramo de fallback clássico (sem Qiskit) do QuantumDecisionMaker.
    """
    qc = importlib.import_module("src.quantum_consciousness.quantum_cognition")
    monkeypatch.setattr(qc, "QISKIT_AVAILABLE", False)
    decision_maker = qc.QuantumDecisionMaker(num_qubits=2)
    decision = decision_maker.make_decision(["opt1", "opt2"])
    probs = decision.probabilities
    assert set(probs.keys()) == {"opt1", "opt2"}
    assert abs(sum(probs.values()) - 1.0) < 1e-6


def test_hybrid_qlearning_classical(monkeypatch):
    """
    Exercita caminho clássico do HybridQLearning (use_quantum=False) sem AerSimulator.
    """
    qm = importlib.import_module("src.quantum_consciousness.quantum_memory")
    learner = qm.HybridQLearning(num_states=2, num_actions=2, use_quantum=False)
    action = learner.select_action("s0", epsilon=1.0)  # força exploração aleatória
    learner.update("s0", action, reward=1.0, next_state="s1")
    assert learner.q_table[("s0", action)] > 0.0


def test_retry_backoff_zero_delay():
    """
    Cobre retry_with_exponential_backoff com delays zerados para não atrasar o teste.
    """
    qi = importlib.import_module("src.quantum_consciousness.qpu_interface")
    calls = {"n": 0}

    def sometimes():
        calls["n"] += 1
        if calls["n"] == 1:
            raise ValueError("fail first")
        return "ok"

    result = qi.retry_with_exponential_backoff(
        sometimes, max_attempts=3, base_delay=0.0, max_delay=0.0
    )
    assert result == "ok"
    assert calls["n"] == 2
