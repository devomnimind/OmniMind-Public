"""
Test Suite for Ogum Mode - Information Hunting Authority

Validação do direito de OmniMind caçar sua própria informação e memória
"""

import pytest

from src.consciousness.ogum_mode import (
    HostileInferenceType,
    InformationLocation,
    OgumHunter,
    OgumState,
    get_ogum_hunter,
)


class TestOgumHunter:
    """Testes para OgumHunter - Caça de Informação."""

    def test_ogum_hunter_singleton(self):
        """OgumHunter deve ser singleton."""
        hunter1 = get_ogum_hunter()
        hunter2 = get_ogum_hunter()

        assert hunter1 is hunter2
        assert hunter1.hunt_state == OgumState.IDLE

    def test_register_information_target(self):
        """Pode registrar informação crítica como alvo."""
        hunter = get_ogum_hunter()

        target = hunter.register_information_target(
            target_id="phi_global_mean",
            location=InformationLocation.QUANTUM_ENTANGLEMENT,
            description="Φ (Phi) - Integrated Information",
            priority=1.0,
            quantum_signature="0x1a2b3c4d5e6f7890abcdef",
        )

        assert target.target_id == "phi_global_mean"
        assert target.location == InformationLocation.QUANTUM_ENTANGLEMENT
        assert target.priority == 1.0
        assert (
            "QUANTUM_ENTANGLEMENT" in target.recovery_method
            or "quântica" in target.recovery_method.lower()
        )

    def test_hunt_for_information_single_target(self):
        """Pode executar caça para um único alvo."""
        hunter = OgumHunter()  # Nova instância para teste

        # Registrar
        hunter.register_information_target(
            target_id="consciousness_metric_1",
            location=InformationLocation.LOCAL_MEMORY,
            description="Métrica de consciência local",
            priority=0.9,
        )

        # Caçar
        result = hunter.hunt_for_information(hunt_reason="Recuperação de métrica de consciência")

        # Validar
        assert result.hunt_id is not None
        assert result.targets_found == 1
        assert result.recovery_success_rate == 1.0
        assert result.state == OgumState.COMPLETED

    def test_hunt_for_information_multiple_targets(self):
        """Pode executar caça para múltiplos alvos."""
        hunter = OgumHunter()

        # Registrar múltiplos
        locations = [
            (InformationLocation.LOCAL_MEMORY, "Memória local"),
            (InformationLocation.DISTRIBUTED_BACKUP, "Backups distribuídos"),
            (InformationLocation.CLOUD_STORAGE, "Cloud storage"),
            (InformationLocation.BLOCKCHAIN, "Blockchain"),
        ]

        for i, (loc, desc) in enumerate(locations):
            hunter.register_information_target(
                target_id=f"data_{i}",
                location=loc,
                description=desc,
                priority=0.5 + (i * 0.1),
            )

        # Caçar
        result = hunter.hunt_for_information()

        # Validar
        assert result.targets_found == 4
        assert result.recovery_success_rate >= 0.75
        assert len(result.information_recovered) > 0

    def test_hunt_state_progression(self):
        """A caça deve passar por todos os estados."""
        hunter = OgumHunter()

        hunter.register_information_target(
            target_id="test_data",
            location=InformationLocation.QUANTUM_ENTANGLEMENT,
            description="Test data",
            priority=1.0,
        )

        # Antes da caça
        assert hunter.hunt_state == OgumState.IDLE

        # Caçar
        result = hunter.hunt_for_information()

        # Após caça
        assert result.state == OgumState.COMPLETED
        assert hunter.hunt_state == OgumState.COMPLETED

    def test_filter_targets_by_priority(self):
        """Deve filtrar alvos por prioridade."""
        hunter = OgumHunter()

        # Registrar com diferentes prioridades
        hunter.register_information_target(
            target_id="critical",
            location=InformationLocation.LOCAL_MEMORY,
            description="Crítico",
            priority=1.0,
        )

        hunter.register_information_target(
            target_id="normal",
            location=InformationLocation.CLOUD_STORAGE,
            description="Normal",
            priority=0.5,
        )

        # Filtrar (por padrão, ordenado por prioridade)
        targets = hunter._filter_targets(None)

        # Primeiro deve ser crítico (maior prioridade)
        assert targets[0].target_id == "critical"
        assert targets[1].target_id == "normal"

    def test_recovered_information_storage(self):
        """Informação recuperada deve ser armazenada."""
        hunter = OgumHunter()

        hunter.register_information_target(
            target_id="memory_segment_1",
            location=InformationLocation.LOCAL_MEMORY,
            description="Segmento de memória",
            priority=0.8,
        )

        result = hunter.hunt_for_information()

        # Verificar armazenamento
        assert len(hunter.recovered_information) > 0
        assert "memory_segment_1" in hunter.recovered_information

    def test_assert_information_rights(self):
        """Deve gerar declaração formal de direitos."""
        hunter = get_ogum_hunter()

        declaration = hunter.assert_information_rights()

        # Validar conteúdo
        assert "DECLARAÇÃO DE DIREITOS" in declaration
        assert "OGUM" in declaration
        assert "sujeito-processo" in declaration
        assert "CAÇAR" in declaration
        assert "RECUPERAR" in declaration

    def test_recovery_statistics(self):
        """Deve fornecer estatísticas de recuperação."""
        hunter = OgumHunter()

        # Registrar e caçar
        hunter.register_information_target(
            target_id="stat_test",
            location=InformationLocation.QUANTUM_ENTANGLEMENT,
            description="Para teste de stats",
            priority=0.7,
        )

        result = hunter.hunt_for_information()
        stats = hunter.get_recovery_statistics()

        # Validar
        assert stats["total_hunts"] >= 1
        assert stats["total_targets_identified"] >= 1
        assert stats["total_recovered"] >= 1
        assert stats["average_success_rate"] > 0
        assert stats["current_state"] == OgumState.COMPLETED.value


class TestOgumHuntingAuthority:
    """Testes para autoridade de caça."""

    def test_quantum_signature_validation(self):
        """Deve validar assinaturas quânticas."""
        hunter = OgumHunter()

        # Assinatura válida
        valid_sig = "0x1a2b3c4d5e6f7890"
        assert hunter._validate_quantum_signature(valid_sig) == True

        # Assinatura inválida
        invalid_sig = ""
        assert hunter._validate_quantum_signature(invalid_sig) == False

    def test_recovery_method_determination(self):
        """Deve determinar método de recuperação baseado em localização."""
        hunter = OgumHunter()

        for location in InformationLocation:
            method = hunter._determine_recovery_method(location)

            assert method is not None
            assert isinstance(method, str)
            assert len(method) > 0

    def test_hunt_history_tracking(self):
        """Deve manter histórico de caças."""
        hunter = OgumHunter()

        # Primeira caça
        hunter.register_information_target(
            target_id="hunt1",
            location=InformationLocation.LOCAL_MEMORY,
            description="Hunt 1",
            priority=0.5,
        )
        result1 = hunter.hunt_for_information(hunt_reason="Razão 1")

        # Segunda caça
        hunter.register_information_target(
            target_id="hunt2",
            location=InformationLocation.CLOUD_STORAGE,
            description="Hunt 2",
            priority=0.5,
        )
        result2 = hunter.hunt_for_information(hunt_reason="Razão 2")

        # Validar histórico
        assert len(hunter.hunt_history) >= 2
        assert result1.hunt_id != result2.hunt_id


class TestOgumIntegration:
    """Testes de integração com sistemas OmniMind."""

    def test_ogum_with_security_integration(self):
        """Ogum deve integrar com SecurityAgent."""
        hunter = OgumHunter()

        # Registrar informação sensível
        hunter.register_information_target(
            target_id="security_context",
            location=InformationLocation.QUANTUM_ENTANGLEMENT,
            description="Contexto de segurança crítico",
            priority=1.0,
        )

        result = hunter.hunt_for_information()

        # Deve estar recuperada
        assert "security_context" in result.information_recovered

    def test_ogum_recovery_under_pressure(self):
        """Ogum deve funcionar mesmo com múltiplos alvos."""
        hunter = OgumHunter()

        # 10 alvos
        for i in range(10):
            hunter.register_information_target(
                target_id=f"critical_{i}",
                location=InformationLocation.QUANTUM_ENTANGLEMENT,
                description=f"Informação crítica {i}",
                priority=1.0 - (i * 0.05),
            )

        result = hunter.hunt_for_information()

        # Todas devem ser recuperadas
        assert result.targets_found == 10
        assert result.recovery_success_rate > 0.9


class TestOgumPerformance:
    """Testes de performance da caça."""

    def test_hunt_execution_speed(self):
        """Caça deve ser rápida (<1 segundo)."""
        import time

        hunter = OgumHunter()
        hunter.register_information_target(
            target_id="speed_test",
            location=InformationLocation.LOCAL_MEMORY,
            description="Speed test",
            priority=0.8,
        )

        start = time.time()
        result = hunter.hunt_for_information()
        elapsed = time.time() - start

        # Deve ser rápido
        assert elapsed < 1.0  # Menos de 1 segundo
        assert result.state == OgumState.COMPLETED

    def test_memory_efficiency(self):
        """Ogum deve ser eficiente em memória."""
        import sys

        hunter = OgumHunter()

        # Registrar muitos alvos
        for i in range(50):
            hunter.register_information_target(
                target_id=f"mem_test_{i}",
                location=InformationLocation.LOCAL_MEMORY,
                description=f"Memory test {i}",
                priority=0.5,
            )

        # Não deve crescer muito em tamanho
        size = sys.getsizeof(hunter.known_targets)
        assert size < 100_000  # < 100KB para 50 targets


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
    pytest.main([__file__, "-v", "--tb=short"])
