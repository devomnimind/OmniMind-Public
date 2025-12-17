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
from src.autopoietic.code_synthesizer import SynthesizedComponent
from src.autopoietic.meta_architect import ComponentSpec


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
        signed_name = f"modulo_autopoiesis_data_{spec.name}"
        assert signed_name in patches

        synth = patches[signed_name]
        assert isinstance(synth, SynthesizedComponent)
        assert synth.name == signed_name
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
        signed_a = f"modulo_autopoiesis_data_{specs[0].name}"
        signed_b = f"modulo_autopoiesis_data_{specs[1].name}"
        assert signed_a in patches
        assert signed_b in patches

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
        signed_name = "modulo_autopoiesis_data_repair_component"
        synth = SynthesizedComponent(
            name=signed_name,
            source_code="class RepairComponent:\n    pass",
            natural_description="Test repair component",
        )
        patches = {signed_name: synth}

        applied = repair.apply_patches(patches)

        assert isinstance(applied, dict)
        assert len(applied) == 1

        expected_path = f"src/autopoietic/repairs/{signed_name}.py"
        assert expected_path in applied
        assert applied[expected_path] == synth.source_code

    def test_apply_patches_multiple(self) -> None:
        """Testa aplicação de múltiplos patches."""
        repair = AdvancedRepair()
        signed_x = "modulo_autopoiesis_data_repair_x"
        signed_y = "modulo_autopoiesis_data_repair_y"
        signed_z = "modulo_autopoiesis_data_repair_z"
        patches = {
            signed_x: SynthesizedComponent(
                name=signed_x,
                source_code="# Repair X code",
                natural_description="Test repair component X",
            ),
            signed_y: SynthesizedComponent(
                name=signed_y,
                source_code="# Repair Y code",
                natural_description="Test repair component Y",
            ),
            signed_z: SynthesizedComponent(
                name=signed_z,
                source_code="# Repair Z code",
                natural_description="Test repair component Z",
            ),
        }

        applied = repair.apply_patches(patches)

        assert len(applied) == 3
        assert f"src/autopoietic/repairs/{signed_x}.py" in applied
        assert f"src/autopoietic/repairs/{signed_y}.py" in applied
        assert f"src/autopoietic/repairs/{signed_z}.py" in applied

        assert applied[f"src/autopoietic/repairs/{signed_x}.py"] == "# Repair X code"
        assert applied[f"src/autopoietic/repairs/{signed_y}.py"] == "# Repair Y code"
        assert applied[f"src/autopoietic/repairs/{signed_z}.py"] == "# Repair Z code"

    def test_apply_patches_preserves_source_code(self) -> None:
        """Testa que o código fonte é preservado corretamente."""
        repair = AdvancedRepair()
        source = """class MyRepair:
    def __init__(self):
        self.status = 'active'

    def repair(self):
        return True
"""
        signed_name = "modulo_autopoiesis_data_my_repair"
        synth = SynthesizedComponent(
            name=signed_name,
            source_code=source,
            natural_description="Test repair component with custom source code",
        )
        applied = repair.apply_patches({signed_name: synth})

        path = f"src/autopoietic/repairs/{signed_name}.py"
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
        signed_broken = "modulo_autopoiesis_data_repair_broken_module"
        signed_failing = "modulo_autopoiesis_data_repair_failing_component"
        assert signed_broken in patches
        assert signed_failing in patches

        # 3. Aplica patches
        applied = repair.apply_patches(patches)
        assert len(applied) == 2
        assert f"src/autopoietic/repairs/{signed_broken}.py" in applied
        assert f"src/autopoietic/repairs/{signed_failing}.py" in applied

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
        signed_name = "modulo_autopoiesis_data_fix_a"
        path = f"src/autopoietic/repairs/{signed_name}.py"
        assert path in applied
        assert len(applied[path]) > 0
