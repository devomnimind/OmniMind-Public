"""
Extended Loop Cycle Result - Extensão compatível de LoopCycleResult.

Adiciona campos opcionais para métricas completas (Φ, Ψ, σ, tríade) sem breaking changes.

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-07
Baseado em: REDESENHO_RADICAL_EMBEDDINGS.py + decisões arquiteturais aprovadas
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np

from src.consciousness.consciousness_triad import ConsciousnessTriad
from src.consciousness.integration_loop import LoopCycleResult


@dataclass
class ExtendedLoopCycleResult(LoopCycleResult):
    """
    Extensão de LoopCycleResult com campos opcionais para métricas completas.

    Mantém compatibilidade total: todos os campos novos são Optional.
    Scripts existentes continuam funcionando sem modificação.

    Campos adicionais:
    - module_outputs: Embeddings de cada módulo no ciclo
    - module_activations: Ativação normalizada de cada módulo
    - integration_strength: Força de integração entre módulos
    - temporal_signature: Assinatura temporal para cálculo de LZ
    - psi: Ψ_produtor (Deleuze) calculado a partir de embeddings
    - sigma: σ_sinthome (Lacan) calculado para o ciclo
    - triad: Tríade completa (Φ, Ψ, σ)
    - cycle_id: ID único do ciclo (string)
    """

    # Campos opcionais (compatibilidade)
    module_outputs: Optional[Dict[str, np.ndarray]] = None
    module_activations: Optional[Dict[str, float]] = None
    integration_strength: Optional[float] = None
    temporal_signature: Optional[List[float]] = None
    psi: Optional[float] = None
    sigma: Optional[float] = None
    triad: Optional[ConsciousnessTriad] = None
    cycle_id: Optional[str] = None
    trace_id: Optional[str] = None  # NOVO: TraceID para correlação distribuída (Sprint 1)

    # Novos campos (Isomorfismo Estrutural)
    gozo: Optional[float] = None  # Gozo (excesso não integrado)
    delta: Optional[float] = None  # δ (defesa psicanalítica)
    epsilon: Optional[float] = None  # ϵ (desire engine - desejo)
    phi_causal: Optional[float] = None  # Φ_causal (phi calculado sobre padrões causais RNN)
    repression_strength: Optional[float] = None  # Força de repressão (defesa estrutural)
    imagination_output: Optional[np.ndarray] = None  # Output do módulo imagination
    control_effectiveness: Optional[float] = None  # Efetividade de controle total
    homeostatic_state: Optional[Dict[str, Any]] = (
        None  # Estado homeostático (PROTOCOLO CLÍNICO-CIBERNÉTICO)
    )

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário (serialização)."""
        base_dict = {
            "cycle_number": self.cycle_number,
            "cycle_duration_ms": self.cycle_duration_ms,
            "modules_executed": self.modules_executed,
            "errors_occurred": self.errors_occurred,
            "cross_prediction_scores": self.cross_prediction_scores,
            "phi_estimate": self.phi_estimate,
            "timestamp": (
                self.timestamp.isoformat()
                if isinstance(self.timestamp, datetime)
                else str(self.timestamp)
            ),
            "complexity_metrics": self.complexity_metrics,
        }

        # Adiciona campos estendidos se presentes
        if self.module_outputs is not None:
            base_dict["module_outputs"] = {
                name: emb.tolist() if isinstance(emb, np.ndarray) else emb
                for name, emb in self.module_outputs.items()
            }
        if self.module_activations is not None:
            base_dict["module_activations"] = self.module_activations
        if self.integration_strength is not None:
            base_dict["integration_strength"] = self.integration_strength
        if self.temporal_signature is not None:
            base_dict["temporal_signature"] = self.temporal_signature
        if self.psi is not None:
            base_dict["psi"] = self.psi
        if self.sigma is not None:
            base_dict["sigma"] = self.sigma
        if self.triad is not None:
            base_dict["triad"] = self.triad.to_dict()
        if self.cycle_id is not None:
            base_dict["cycle_id"] = self.cycle_id
        if self.trace_id is not None:
            base_dict["trace_id"] = self.trace_id
        if self.gozo is not None:
            base_dict["gozo"] = self.gozo
        if self.delta is not None:
            base_dict["delta"] = self.delta
        if self.epsilon is not None:
            base_dict["epsilon"] = self.epsilon
        if self.phi_causal is not None:
            base_dict["phi_causal"] = self.phi_causal
        if self.repression_strength is not None:
            base_dict["repression_strength"] = self.repression_strength
        if self.imagination_output is not None:
            base_dict["imagination_output"] = (
                self.imagination_output.tolist()
                if isinstance(self.imagination_output, np.ndarray)
                else self.imagination_output
            )
        if self.control_effectiveness is not None:
            base_dict["control_effectiveness"] = self.control_effectiveness
        if self.homeostatic_state is not None:
            base_dict["homeostatic_state"] = self.homeostatic_state

        return base_dict

    def has_extended_data(self) -> bool:
        """Verifica se contém dados estendidos."""
        return (
            self.module_outputs is not None
            or self.module_activations is not None
            or self.integration_strength is not None
            or self.temporal_signature is not None
            or self.psi is not None
            or self.sigma is not None
            or self.triad is not None
            or self.gozo is not None
            or self.delta is not None
            or self.epsilon is not None
            or self.phi_causal is not None
            or self.repression_strength is not None
            or self.imagination_output is not None
            or self.control_effectiveness is not None
            or self.homeostatic_state is not None
        )

    @classmethod
    def from_base_result(
        cls,
        base_result: LoopCycleResult,
        module_outputs: Optional[Dict[str, np.ndarray]] = None,
        module_activations: Optional[Dict[str, float]] = None,
        integration_strength: Optional[float] = None,
        temporal_signature: Optional[List[float]] = None,
        psi: Optional[float] = None,
        sigma: Optional[float] = None,
        triad: Optional[ConsciousnessTriad] = None,
        cycle_id: Optional[str] = None,
    ) -> "ExtendedLoopCycleResult":
        """
        Cria ExtendedLoopCycleResult a partir de LoopCycleResult base.

        Args:
            base_result: LoopCycleResult existente
            module_outputs: Embeddings dos módulos (opcional)
            module_activations: Ativações dos módulos (opcional)
            integration_strength: Força de integração (opcional)
            temporal_signature: Assinatura temporal (opcional)
            psi: Ψ calculado (opcional)
            sigma: σ calculado (opcional)
            triad: Tríade completa (opcional)
            cycle_id: ID do ciclo (opcional)

        Returns:
            ExtendedLoopCycleResult com campos base + estendidos
        """
        return cls(
            cycle_number=base_result.cycle_number,
            cycle_duration_ms=base_result.cycle_duration_ms,
            modules_executed=base_result.modules_executed,
            errors_occurred=base_result.errors_occurred,
            cross_prediction_scores=base_result.cross_prediction_scores,
            phi_estimate=base_result.phi_estimate,
            timestamp=base_result.timestamp,
            complexity_metrics=base_result.complexity_metrics,
            # Campos estendidos
            module_outputs=module_outputs,
            module_activations=module_activations,
            integration_strength=integration_strength,
            temporal_signature=temporal_signature,
            psi=psi,
            sigma=sigma,
            triad=triad,
            cycle_id=cycle_id,
        )
