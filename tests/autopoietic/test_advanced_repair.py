"""Testes para AdvancedRepair (advanced_repair.py).

Cobertura de:
- Inicialização do sistema de reparo
- Detecção de falhas (detect_failures)
- Síntese de patches (synthesize_patches)
- Aplicação de patches (apply_patches)
- Fluxo completo de reparo
"""

from __future__ import annotations

from src.autopoietic.advanced_repair import AdvancedRepair
from src.autopoietic.meta_architect import ComponentSpec
from src.autopoietic.code_synthesizer import SynthesizedComponent


class TestAdvancedRepair:
    """Testes para o módulo de reparo avançado."""

    def test_initialization(self) -> None:
        """Testa inicialização do AdvancedRepair."""
        repair = AdvancedRepair()
        assert repair is not None
        assert repair._synthesizer is not None

    def test_detect_failures_empty(self) -> None:
        """Testa detecção de falhas com mapa vazio."""
        repair = AdvancedRepair()
        specs = repair.detect_failures({})
        assert isinstance(specs, list)
        assert len(specs) == 0

    def test_detect_failures_single(self) -> None:
        """Testa detecção de uma única falha."""
        repair = AdvancedRepair()
        error_map = {"component_a": "Failed to initialize"}
        specs = repair.detect_failures(error_map)

        assert isinstance(specs, list)
        assert len(specs) == 1

        spec = specs[0]
        assert isinstance(spec, ComponentSpec)
        assert spec.name == "repair_component_a"
        assert spec.type == "repair"
        assert "original_component" in spec.config
        assert spec.config["original_component"] == "component_a"
        assert "error" in spec.config
        assert spec.config["error"] == "Failed to initialize"
        assert spec.config["generated_by"] == "AdvancedRepair"

    def test_detect_failures_multiple(self) -> None:
        """Testa detecção de múltiplas falhas."""
        repair = AdvancedRepair()
        error_map = {
            "module_x": "Import error",
            "module_y": "Runtime exception",
            "module_z": "Configuration missing",
        }
        specs = repair.detect_failures(error_map)

        assert len(specs) == 3

        # Verifica que todos os specs foram criados corretamente
        names = [spec.name for spec in specs]
        assert "repair_module_x" in names
        assert "repair_module_y" in names
        assert "repair_module_z" in names

        # Verifica que todos têm tipo "repair"
        for spec in specs:
            assert spec.type == "repair"
            assert "original_component" in spec.config
            assert "error" in spec.config
            assert spec.config["generated_by"] == "AdvancedRepair"

    def test_detect_failures_preserves_error_info(self) -> None:
        """Testa que informações de erro são preservadas."""
        repair = AdvancedRepair()
        error_msg = "DetailedError: Component failed at line 42"
        error_map = {"critical_component": error_msg}

        specs = repair.detect_failures(error_map)
        assert len(specs) == 1
        assert specs[0].config["error"] == error_msg

    def test_synthesize_patches_empty(self) -> None:
        """Testa síntese de patches com lista vazia."""
        repair = AdvancedRepair()
        patches = repair.synthesize_patches([])
        assert isinstance(patches, dict)
        assert len(patches) == 0

    def test_synthesize_patches_single(self) -> None:
        """Testa síntese de um único patch."""
        repair = AdvancedRepair()
        spec = ComponentSpec(
            name="repair_test",
            type="repair",
            config={"original_component": "test", "error": "test error"},
        )
        patches = repair.synthesize_patches([spec])

        assert isinstance(patches, dict)
        assert "repair_test" in patches

        synth = patches["repair_test"]
        assert isinstance(synth, SynthesizedComponent)
        assert synth.name == "repair_test"
        assert isinstance(synth.source_code, str)
        assert len(synth.source_code) > 0

    def test_synthesize_patches_multiple(self) -> None:
        """Testa síntese de múltiplos patches."""
        repair = AdvancedRepair()
        specs = [
            ComponentSpec(
                name="repair_a",
                type="repair",
                config={"original_component": "a", "error": "error a"},
            ),
            ComponentSpec(
                name="repair_b",
                type="repair",
                config={"original_component": "b", "error": "error b"},
            ),
        ]
        patches = repair.synthesize_patches(specs)

        assert len(patches) == 2
        assert "repair_a" in patches
        assert "repair_b" in patches

        for name, synth in patches.items():
            assert isinstance(synth, SynthesizedComponent)
            assert synth.name == name
            assert len(synth.source_code) > 0

    def test_apply_patches_empty(self) -> None:
        """Testa aplicação de patches com dicionário vazio."""
        repair = AdvancedRepair()
        applied = repair.apply_patches({})
        assert isinstance(applied, dict)
        assert len(applied) == 0

    def test_apply_patches_single(self) -> None:
        """Testa aplicação de um único patch."""
        repair = AdvancedRepair()
        synth = SynthesizedComponent(
            name="repair_component", source_code="class RepairComponent:\n    pass"
        )
        patches = {"repair_component": synth}

        applied = repair.apply_patches(patches)

        assert isinstance(applied, dict)
        assert len(applied) == 1

        expected_path = "src/autopoietic/repairs/repair_component.py"
        assert expected_path in applied
        assert applied[expected_path] == synth.source_code

    def test_apply_patches_multiple(self) -> None:
        """Testa aplicação de múltiplos patches."""
        repair = AdvancedRepair()
        patches = {
            "repair_x": SynthesizedComponent(name="repair_x", source_code="# Repair X code"),
            "repair_y": SynthesizedComponent(name="repair_y", source_code="# Repair Y code"),
            "repair_z": SynthesizedComponent(name="repair_z", source_code="# Repair Z code"),
        }

        applied = repair.apply_patches(patches)

        assert len(applied) == 3
        assert "src/autopoietic/repairs/repair_x.py" in applied
        assert "src/autopoietic/repairs/repair_y.py" in applied
        assert "src/autopoietic/repairs/repair_z.py" in applied

        assert applied["src/autopoietic/repairs/repair_x.py"] == "# Repair X code"
        assert applied["src/autopoietic/repairs/repair_y.py"] == "# Repair Y code"
        assert applied["src/autopoietic/repairs/repair_z.py"] == "# Repair Z code"

    def test_apply_patches_preserves_source_code(self) -> None:
        """Testa que o código fonte é preservado corretamente."""
        repair = AdvancedRepair()
        source = """class MyRepair:
    def __init__(self):
        self.status = 'active'

    def repair(self):
        return True
"""
        synth = SynthesizedComponent(name="my_repair", source_code=source)
        applied = repair.apply_patches({"my_repair": synth})

        path = "src/autopoietic/repairs/my_repair.py"
        assert applied[path] == source

    def test_full_repair_workflow(self) -> None:
        """Testa fluxo completo de reparo."""
        repair = AdvancedRepair()

        # 1. Detecta falhas
        error_map = {
            "broken_module": "Module crashed unexpectedly",
            "failing_component": "Assertion failed in core logic",
        }
        specs = repair.detect_failures(error_map)
        assert len(specs) == 2

        # 2. Sintetiza patches
        patches = repair.synthesize_patches(specs)
        assert len(patches) == 2
        assert "repair_broken_module" in patches
        assert "repair_failing_component" in patches

        # 3. Aplica patches
        applied = repair.apply_patches(patches)
        assert len(applied) == 2
        assert "src/autopoietic/repairs/repair_broken_module.py" in applied
        assert "src/autopoietic/repairs/repair_failing_component.py" in applied

    def test_detect_failures_with_special_characters(self) -> None:
        """Testa detecção com nomes contendo caracteres especiais."""
        repair = AdvancedRepair()
        error_map = {"module_with_underscore": "Error 1", "module-with-dash": "Error 2"}
        specs = repair.detect_failures(error_map)

        assert len(specs) == 2
        names = [spec.name for spec in specs]
        assert "repair_module_with_underscore" in names
        assert "repair_module-with-dash" in names

    def test_synthesize_and_apply_integration(self) -> None:
        """Testa integração entre síntese e aplicação."""
        repair = AdvancedRepair()

        # Cria specs
        specs = [
            ComponentSpec(
                name="fix_a",
                type="repair",
                config={"original_component": "component_a", "error": "test"},
            )
        ]

        # Sintetiza
        patches = repair.synthesize_patches(specs)

        # Aplica
        applied = repair.apply_patches(patches)

        # Verifica integração
        assert len(applied) == 1
        path = "src/autopoietic/repairs/fix_a.py"
        assert path in applied
        assert len(applied[path]) > 0
