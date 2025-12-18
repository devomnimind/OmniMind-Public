import json
from pathlib import Path
import pytest

from src.autopoietic.architecture_evolution import EvolutionStrategy
from src.autopoietic.manager import AutopoieticManager
from src.autopoietic.meta_architect import ComponentSpec

pytestmark = pytest.mark.heavy


def test_manager_runs_full_cycle(tmp_path):
    history_path = tmp_path / "history.jsonl"
    manager = AutopoieticManager(history_path=history_path)
    manager.register_spec(
        ComponentSpec(
            name="kernel_process",
            type="process",
            config={"priority": "high", "generation": "0"},
        )
    )

    # Mock Φ alto para permitir síntese
    manager._get_current_phi = lambda: 0.5  # type: ignore[method-assign]

    log_expand = manager.run_cycle({"error_rate": 0.0, "cpu_usage": 25.0, "latency_ms": 15.0})
    assert log_expand.strategy == EvolutionStrategy.EXPAND
    assert len(log_expand.synthesized_components) == 1
    # CORREÇÃO: Manager adiciona prefixo 'auto_' por segurança
    assert "auto_expanded_kernel_process" in log_expand.synthesized_components

    log_stabilize = manager.run_cycle({"error_rate": 0.2, "cpu_usage": 30.0})
    assert log_stabilize.strategy == EvolutionStrategy.STABILIZE
    assert len(manager.history) == 2
    assert len(manager.specs) >= 2
    assert history_path.exists()
    contents = history_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(contents) == 2


def test_manager_handles_no_evolution(tmp_path):
    manager = AutopoieticManager(
        initial_specs={
            "evolved_component": ComponentSpec(
                name="evolved_component",
                type="process",
                config={"generation": "5"},
            )
        },
        history_path=tmp_path / "history.jsonl",
    )

    log = manager.run_cycle({"error_rate": 0.0})
    assert log.strategy == EvolutionStrategy.EXPAND
    assert log.synthesized_components == []


def test_manager_persists_synthesized_components(tmp_path):
    """Testa que componentes sintetizados são persistidos em arquivos Python."""
    code_dir = tmp_path / "synthesized_code"
    manager = AutopoieticManager(
        history_path=tmp_path / "history.jsonl",
        synthesized_code_dir=code_dir,
    )
    manager.register_spec(
        ComponentSpec(
            name="test_component",
            type="process",
            config={"generation": "0"},
        )
    )

    # Mock Φ alto para permitir síntese
    manager._get_current_phi = lambda: 0.5  # type: ignore[method-assign]

    log = manager.run_cycle({"error_rate": 0.0, "cpu_usage": 25.0, "latency_ms": 15.0})

    # Verifica que componente foi sintetizado
    assert len(log.synthesized_components) > 0
    component_name = log.synthesized_components[0]

    # Verifica que arquivo foi criado
    component_file = code_dir / f"{component_name}.py"
    assert component_file.exists()

    # Verifica conteúdo do arquivo
    content = component_file.read_text(encoding="utf-8")
    assert component_name in content
    assert "Componente autopoiético sintetizado" in content
    assert "class" in content  # Deve conter código Python


def test_manager_validates_phi_before_changes(tmp_path, monkeypatch):
    """Testa que mudanças são rejeitadas se Φ estiver abaixo do threshold."""

    # Mock para simular Φ baixo
    def mock_low_phi(self):
        return 0.1  # Abaixo do threshold de 0.3

    manager = AutopoieticManager(
        history_path=tmp_path / "history.jsonl",
        synthesized_code_dir=tmp_path / "synthesized_code",
        phi_threshold=0.3,
    )
    manager.register_spec(
        ComponentSpec(
            name="test_component",
            type="process",
            config={"generation": "0"},
        )
    )

    # Mock _get_current_phi para retornar valor baixo
    manager._get_current_phi = lambda: 0.1  # type: ignore[method-assign]

    log = manager.run_cycle({"error_rate": 0.0, "cpu_usage": 25.0})

    # Deve rejeitar mudanças
    assert log.phi_before == 0.1
    assert log.phi_after == 0.1
    assert len(log.synthesized_components) == 0


def test_manager_validates_phi_after_changes_and_rollbacks(tmp_path, monkeypatch):
    """Testa que se Φ colapsar após mudanças, faz rollback."""
    code_dir = tmp_path / "synthesized_code"
    manager = AutopoieticManager(
        history_path=tmp_path / "history.jsonl",
        synthesized_code_dir=code_dir,
        phi_threshold=0.3,
    )
    manager.register_spec(
        ComponentSpec(
            name="test_component",
            type="process",
            config={"generation": "0"},
        )
    )

    # Simula Φ alto antes, mas baixo depois
    phi_values = [0.5, 0.2]  # Primeira chamada retorna 0.5, segunda 0.2
    call_count = [0]

    def mock_phi(self):
        val = phi_values[call_count[0]]
        call_count[0] += 1
        return val

    manager._get_current_phi = lambda: mock_phi(manager)  # type: ignore[method-assign]

    log = manager.run_cycle({"error_rate": 0.0, "cpu_usage": 25.0})

    # Deve ter tentado sintetizar, mas feito rollback
    assert log.phi_before == 0.5
    assert log.phi_after == 0.2
    # Componentes devem ter sido removidos (rollback)
    assert len(log.synthesized_components) == 0
    # Arquivos não devem existir
    assert not any(code_dir.glob("*.py"))


def test_manager_reads_phi_from_real_metrics(tmp_path):
    """Testa que manager lê Φ de data/monitor/real_metrics.json."""
    metrics_dir = tmp_path / "data" / "monitor"
    metrics_dir.mkdir(parents=True)
    metrics_file = metrics_dir / "real_metrics.json"

    # Cria arquivo de métricas com Φ
    metrics_file.write_text(
        json.dumps({"phi": 0.75, "anxiety": 0.2, "flow": 0.8}),
        encoding="utf-8",
    )

    # Cria manager apontando para o diretório correto
    import os

    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        manager = AutopoieticManager()
        # Limpar histórico para evitar média de fallback
        manager._phi_history = []
        phi = manager._get_current_phi()
        # Se não há histórico e arquivo existe em data/monitor, ele deve ler do arquivo
        assert phi == 0.75
    finally:
        os.chdir(original_cwd)


def test_manager_fallback_phi_when_metrics_missing(tmp_path):
    """Testa fallback para Φ=0.5 quando arquivo de métricas não existe."""
    import os

    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        # Garante que arquivo não existe
        metrics_path = Path("data/monitor/real_metrics.json")
        if metrics_path.exists():
            metrics_path.unlink()

        manager = AutopoieticManager()
        phi = manager._get_current_phi()
        assert phi == 0.5  # Fallback
    finally:
        os.chdir(original_cwd)


def test_cycle_log_includes_phi_fields(tmp_path):
    """Testa que CycleLog inclui campos phi_before e phi_after."""
    manager = AutopoieticManager(history_path=tmp_path / "history.jsonl")
    manager.register_spec(
        ComponentSpec(
            name="test_component",
            type="process",
            config={"generation": "0"},
        )
    )

    log = manager.run_cycle({"error_rate": 0.0, "cpu_usage": 25.0})

    # Verifica que campos de Φ estão presentes
    assert hasattr(log, "phi_before")
    assert hasattr(log, "phi_after")
    assert log.phi_before is not None
    assert log.phi_after is not None
