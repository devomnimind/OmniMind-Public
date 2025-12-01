"""
Testes Científicos para Emergência Real do Sinthome

Validação experimental da teoria:
1. Histórico de rupturas → Padrão emergente
2. Padrão recorrente >70% → Sinthome válido
3. Sinthome não pré-definido, emerge dos dados

Este é um teste de descoberta científica,
não um teste unitário convencional.
"""

import pytest
from src.sinthome.emergent_stabilization_rule import (
    BorromeanTopology,
    LacanianRegister,
    RuptureEvent,
    SinthomeEmergence,
    SinthomaticStabilizationRule,
    StabilizationStrategy,
)


class TestBorromeanTopology:
    """Testa topologia borromeana R-S-I."""

    def test_topology_initialization(self):
        """Verifica inicialização da topologia."""
        topology = BorromeanTopology()
        
        assert topology.real_layer == {}
        assert topology.symbolic_layer == {}
        assert topology.imaginary_layer == {}
        assert len(topology.links) == 3

    def test_link_rupture_detection_cycle(self):
        """Detecta ciclos irresolvíveis."""
        topology = BorromeanTopology()
        
        # Simula ciclo: A→B→C→A
        topology.links[('real', 'symbolic')] = ['A', 'B', 'C', 'A']
        
        # Ciclo irresolvível = ruptura
        assert topology.detect_link_rupture(('real', 'symbolic'))

    def test_topology_not_broken_initially(self):
        """Topologia não está quebrada no início."""
        topology = BorromeanTopology()
        
        assert not topology.is_fully_broken()

    def test_topology_fully_broken(self):
        """Detecta quando todos os 3 links estão rompidos."""
        topology = BorromeanTopology()
        
        # Força ruptura em todos os links
        topology.links[('real', 'symbolic')] = ['cycle']
        topology.links[('symbolic', 'imaginary')] = ['cycle']
        topology.links[('imaginary', 'real')] = ['cycle']
        
        assert topology.is_fully_broken()


class TestSinthomeEmergence:
    """Testa emergência do Sinthome a partir do histórico."""

    def test_insufficient_history_returns_none(self):
        """Com <10 rupturas, não há emergência."""
        engine = SinthomeEmergence(min_history_size=10)
        
        # Adiciona 5 rupturas (insuficiente)
        for i in range(5):
            rupture = RuptureEvent(
                timestamp=0.0,
                register=LacanianRegister.REAL,
                context={"error": f"error_{i}"},
                error_type="test_error"
            )
            engine.record_rupture(rupture)
        
        # Sem histórico suficiente, retorna None
        assert engine.analyze_sinthome_emergence() is None

    def test_sinthome_emerges_with_sufficient_recurrence(self):
        """Sinthome emerge com >70% recorrência."""
        engine = SinthomeEmergence(min_history_size=10, recurrence_threshold=0.7)
        
        # Adiciona 10 rupturas
        for i in range(10):
            rupture = RuptureEvent(
                timestamp=float(i),
                register=LacanianRegister.REAL,
                context={"error": f"error_{i}"},
                error_type="test_error"
            )
            engine.record_rupture(rupture)
        
        # Simula 8 estabilizações com o MESMO padrão (80% recorrência)
        for i in range(8):
            stab = StabilizationStrategy(
                timestamp=float(i),
                action_taken="exhaustive_validation",
                parameters={},
                success=True,
                is_singular=True
            )
            engine.record_stabilization(stab)
        
        # 2 estabilizações com padrão diferente
        for i in range(2):
            stab = StabilizationStrategy(
                timestamp=float(8 + i),
                action_taken="fast_recovery",
                parameters={},
                success=True,
                is_singular=False
            )
            engine.record_stabilization(stab)
        
        # Agora deve detectar emergência
        pattern = engine.analyze_sinthome_emergence()
        
        assert pattern is not None
        assert pattern.name == "exhaustive_validation"
        assert pattern.recurrence_rate >= 0.7
        assert pattern.is_irreducible
        assert engine.confidence_level > 0.6

    def test_sinthome_pattern_has_jouissance(self):
        """Sinthome identifica ponto de gozo."""
        engine = SinthomeEmergence(min_history_size=10, recurrence_threshold=0.7)
        
        # Adiciona história
        for i in range(10):
            rupture = RuptureEvent(
                timestamp=float(i),
                register=LacanianRegister.REAL,
                context={"error": f"error_{i}"},
                error_type="test_error"
            )
            engine.record_rupture(rupture)
        
        # 8 vezes o mesmo padrão → gozo detectado
        for i in range(8):
            stab = StabilizationStrategy(
                timestamp=float(i),
                action_taken="exhaustive_validation",
                parameters={},
                success=True,
                is_singular=True
            )
            engine.record_stabilization(stab)
        
        for i in range(2):
            stab = StabilizationStrategy(
                timestamp=float(8 + i),
                action_taken="fast_recovery",
                parameters={},
                success=True
            )
            engine.record_stabilization(stab)
        
        pattern = engine.analyze_sinthome_emergence()
        
        assert pattern is not None
        assert pattern.jouissance_fixation == "Gozo da verificação ilimitada"

    def test_sinthome_signature(self):
        """Retorna assinatura científica válida."""
        engine = SinthomeEmergence(min_history_size=10)
        
        # Simula emergência
        for i in range(10):
            rupture = RuptureEvent(
                timestamp=float(i),
                register=LacanianRegister.REAL,
                context={"error": f"error_{i}"},
                error_type="test_error"
            )
            engine.record_rupture(rupture)
        
        for i in range(8):
            stab = StabilizationStrategy(
                timestamp=float(i),
                action_taken="exhaustive_validation",
                parameters={},
                success=True,
                is_singular=True
            )
            engine.record_stabilization(stab)
        
        for i in range(2):
            stab = StabilizationStrategy(
                timestamp=float(8 + i),
                action_taken="fast_recovery",
                parameters={},
                success=True
            )
            engine.record_stabilization(stab)
        
        # Força emergência
        engine.analyze_sinthome_emergence()
        
        signature = engine.get_sinthome_signature()
        
        assert signature is not None
        assert "name" in signature
        assert "recurrence_rate" in signature
        assert "is_irreducible" in signature
        assert "jouissance" in signature
        assert signature["is_singular"] is True


class TestSinthomaticStabilizationRule:
    """Testa integração da nova regra sinthomática."""

    def test_system_initialization(self):
        """Sistema inicializa sem Sinthome ativo."""
        system = SinthomaticStabilizationRule("TestOmniMind")
        
        assert system.system_name == "TestOmniMind"
        assert not system.sinthome_is_active
        assert system.sinthome_pattern is None

    def test_process_rupture_and_stabilization(self):
        """Processa ruptura e estabilização."""
        system = SinthomaticStabilizationRule("TestOmniMind")
        
        # Adiciona 10 rupturas
        for i in range(10):
            system.process_rupture(
                register=LacanianRegister.REAL,
                error_context={"error_id": i},
                error_type="gpu_out_of_memory"
            )
            
            # Estabiliza sempre com o mesmo padrão (80%)
            if i < 8:
                system.attempt_stabilization(
                    action="exhaustive_validation",
                    parameters={"attempts": 3}
                )
            else:
                system.attempt_stabilization(
                    action="quick_recovery",
                    parameters={"timeout": 5}
                )
        
        history = system.get_rupture_history()
        assert len(history) == 10
        
        patterns = system.get_stabilization_patterns()
        assert patterns["exhaustive_validation"] == 8

    def test_sinthome_detection(self):
        """Detecta emergência do Sinthome."""
        system = SinthomaticStabilizationRule("TestOmniMind")
        
        # Simula histórico que causa emergência
        for i in range(10):
            system.process_rupture(
                register=LacanianRegister.REAL,
                error_context={"error_id": i},
                error_type="test_error"
            )
            
            if i < 8:
                system.attempt_stabilization(
                    action="exhaustive_validation",
                    parameters={"depth": i}
                )
            else:
                system.attempt_stabilization(
                    action="quick_recovery",
                    parameters={}
                )
        
        # Detecta emergência
        pattern = system.detect_and_emergentize_sinthome()
        
        assert pattern is not None
        assert system.sinthome_is_active
        assert pattern.name == "exhaustive_validation"

    def test_apply_sinthome_when_irresolvable(self):
        """Aplica Sinthome quando irresolvível."""
        system = SinthomaticStabilizationRule("TestOmniMind")
        
        # Cria Sinthome
        for i in range(10):
            system.process_rupture(
                register=LacanianRegister.REAL,
                error_context={"error_id": i},
                error_type="test_error"
            )
            system.attempt_stabilization(
                action="exhaustive_validation",
                parameters={"depth": i}
            )
        
        system.detect_and_emergentize_sinthome()
        
        # Aplica quando enfrenta contexto irresolvível
        decision = system.apply_sinthome_when_irresolvable({
            "conflicting_requirements": ["speed", "safety"],
            "cannot_satisfy": "both"
        })
        
        assert decision is not None
        assert decision["is_singular"] is True
        assert decision["is_analyzable"] is False
        assert "exhaustive_validation" in decision["applied_sinthome"]

    def test_sinthome_signature_not_emergent(self):
        """Assinatura quando Sinthome não emergiu."""
        system = SinthomaticStabilizationRule("TestOmniMind")
        
        signature = system.get_sinthome_signature()
        
        assert signature["status"] == "not_emergent"
        assert "Insufficient history" in signature["reason"]

    def test_sinthome_signature_emergent(self):
        """Assinatura quando Sinthome emergiu."""
        system = SinthomaticStabilizationRule("TestOmniMind")
        
        # Força emergência
        for i in range(10):
            system.process_rupture(
                register=LacanianRegister.REAL,
                error_context={"error_id": i},
                error_type="test_error"
            )
            system.attempt_stabilization(
                action="exhaustive_validation",
                parameters={"depth": i}
            )
        
        system.detect_and_emergentize_sinthome()
        
        signature = system.get_sinthome_signature()
        
        assert signature["status"] == "emergent"
        assert signature["system"] == "TestOmniMind"
        assert "confidence" in signature


class TestScientificDiscovery:
    """Valida a descoberta científica do Sinthome emergente."""

    def test_discovery_no_predefined_rule(self):
        """Sinthome não é uma regra pré-definida."""
        system = SinthomaticStabilizationRule("OmniMind")
        
        # Sinthome não deve estar ativo inicialmente
        assert not system.sinthome_is_active
        
        # Ao tentar aplicar sem emergência, retorna None
        result = system.apply_sinthome_when_irresolvable({"test": "context"})
        assert result is None

    def test_discovery_emergent_not_hardcoded(self):
        """
        Descobe científica: Sinthome emerge, não é 'Security-First' hardcoded.
        
        Se o sistema tivesse padrão de "quick_recovery" em 80% das rupturas,
        o Sinthome seria "quick_recovery", não "Security-First".
        """
        system = SinthomaticStabilizationRule("OmniMind")
        
        # Diferente histórico → Diferente Sinthome
        for i in range(10):
            system.process_rupture(
                register=LacanianRegister.REAL,
                error_context={"error_id": i},
                error_type="test_error"
            )
            
            if i < 8:
                # 80% das vezes usa "quick_recovery"
                system.attempt_stabilization(
                    action="quick_recovery",
                    parameters={"fast": True}
                )
            else:
                system.attempt_stabilization(
                    action="exhaustive_validation",
                    parameters={"deep": True}
                )
        
        pattern = system.detect_and_emergentize_sinthome()
        
        # Sinthome emergido é "quick_recovery", não hardcoded "Security-First"
        assert pattern.name == "quick_recovery"

    def test_discovery_multiple_systems_different_sinthomes(self):
        """Cada sistema pode ter Sinthome singular diferente."""
        system1 = SinthomaticStabilizationRule("OmniMind1")
        system2 = SinthomaticStabilizationRule("OmniMind2")
        
        # Sistema 1: prioriza validação
        for i in range(10):
            system1.process_rupture(
                register=LacanianRegister.REAL,
                error_context={"error_id": i},
                error_type="test_error"
            )
            if i < 8:
                system1.attempt_stabilization(
                    action="exhaustive_validation",
                    parameters={}
                )
            else:
                system1.attempt_stabilization(
                    action="quick_recovery",
                    parameters={}
                )
        
        # Sistema 2: prioriza velocidade
        for i in range(10):
            system2.process_rupture(
                register=LacanianRegister.REAL,
                error_context={"error_id": i},
                error_type="test_error"
            )
            if i < 8:
                system2.attempt_stabilization(
                    action="quick_recovery",
                    parameters={}
                )
            else:
                system2.attempt_stabilization(
                    action="exhaustive_validation",
                    parameters={}
                )
        
        pattern1 = system1.detect_and_emergentize_sinthome()
        pattern2 = system2.detect_and_emergentize_sinthome()
        
        # Cada sistema tem seu próprio Sinthome singular
        assert pattern1.name == "exhaustive_validation"
        assert pattern2.name == "quick_recovery"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
