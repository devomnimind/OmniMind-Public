"""
Langevin Dynamics - Perturbação Estocástica para Embeddings

Implementa dinâmica de Langevin para quebrar loops determinísticos e introduzir
exploração termodinâmica no sistema.

Equação: E_{t+1} = E_t - η∇F + √(2T)ξ

Onde:
- E: Embedding
- ∇F: Gradiente do erro de predição (Free Energy)
- T: Temperatura (derivada de Ψ)
- ξ: Ruído branco
- η: Taxa de aprendizado

Baseado em:
- Free Energy Principle (Friston, 2010)
- Langevin Dynamics (Física Estatística)
- Protocolo Livewire FASE 2

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-07
"""

import logging
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


class LangevinDynamics:
    """
    Implementa perturbação estocástica de Langevin para embeddings.

    Quebra loops determinísticos introduzindo ruído termodinâmico controlado.
    """

    def __init__(
        self,
        learning_rate: float = 0.01,
        min_temperature: float = 0.001,
        max_temperature: float = 0.1,
    ):
        """
        Inicializa dinâmica de Langevin.

        Args:
            learning_rate: Taxa de aprendizado (η)
            min_temperature: Temperatura mínima (evita colapso total)
            max_temperature: Temperatura máxima (evita caos total)
        """
        self.learning_rate = learning_rate
        self.min_temperature = min_temperature
        self.max_temperature = max_temperature
        self.logger = logger

    def perturb_embedding(
        self,
        embedding: np.ndarray,
        free_energy_gradient: Optional[np.ndarray] = None,
        temperature: float = 0.01,
        psi_value: Optional[float] = None,
    ) -> np.ndarray:
        """
        Aplica perturbação estocástica de Langevin a um embedding.

        Equação: E_{t+1} = E_t - η∇F + √(2T)ξ

        Args:
            embedding: Embedding atual (E_t)
            free_energy_gradient: Gradiente do erro de predição (∇F) - opcional
            temperature: Temperatura (T) - se não fornecido, usa psi_value
            psi_value: Valor de Ψ (Incerteza) - usado para calcular temperatura se T não fornecido

        Returns:
            Embedding perturbado (E_{t+1})
        """
        # Calcular temperatura se não fornecida
        if temperature is None or temperature == 0.01:  # Valor padrão
            if psi_value is not None:
                # Temperatura derivada de Ψ (Incerteza)
                # Ψ alto = alta incerteza = alta temperatura = mais exploração
                temperature = self._calculate_temperature_from_psi(psi_value)
            else:
                # Usar temperatura mínima se nada fornecido
                temperature = self.min_temperature

        # Garantir que temperatura está no range válido
        temperature = np.clip(temperature, self.min_temperature, self.max_temperature)

        # Termo de gradiente (se fornecido)
        gradient_term = np.zeros_like(embedding)
        if free_energy_gradient is not None:
            gradient_term = -self.learning_rate * free_energy_gradient

        # Termo de ruído (ruído branco gaussiano)
        noise_amplitude = np.sqrt(2.0 * temperature)
        noise = np.random.normal(0.0, 1.0, size=embedding.shape)
        noise_term = noise_amplitude * noise

        # Aplicar perturbação
        perturbed_embedding = embedding + gradient_term + noise_term

        # Normalizar para manter magnitude razoável
        original_norm = np.linalg.norm(embedding)
        if original_norm > 0:
            perturbed_norm = np.linalg.norm(perturbed_embedding)
            if perturbed_norm > 0:
                # Manter magnitude similar (evitar explosão)
                scale_factor = original_norm / perturbed_norm
                perturbed_embedding = perturbed_embedding * scale_factor

        self.logger.debug(
            f"Langevin perturbation: T={temperature:.6f}, "
            f"noise_amplitude={noise_amplitude:.6f}, "
            f"gradient_norm={np.linalg.norm(gradient_term):.6f}"
        )

        return perturbed_embedding

    def _calculate_temperature_from_psi(self, psi_value: float) -> float:
        """
        Calcula temperatura a partir de Ψ (Incerteza).

        Ψ alto = alta incerteza = alta temperatura = mais exploração

        Args:
            psi_value: Valor de Ψ [0, 1]

        Returns:
            Temperatura [min_temperature, max_temperature]
        """
        # Mapear Ψ [0, 1] para temperatura [min, max]
        # Usar função sigmóide para suavidade
        psi_clipped = np.clip(psi_value, 0.0, 1.0)
        temperature_range = self.max_temperature - self.min_temperature
        temperature = self.min_temperature + temperature_range * psi_clipped

        return float(temperature)

    def ensure_minimum_variance(
        self,
        embedding: np.ndarray,
        previous_embedding: Optional[np.ndarray] = None,
        min_variance: float = 0.01,
    ) -> np.ndarray:
        """
        Garante variação mínima entre embeddings (evita colapso).

        Se a variação é muito baixa, injeta ruído adicional.

        Args:
            embedding: Embedding atual
            previous_embedding: Embedding anterior (opcional)
            min_variance: Variação mínima requerida (aumentado de 0.001 para 0.01)

        Returns:
            Embedding com variação garantida
        """
        if previous_embedding is None:
            # Sem histórico, não há como verificar variação
            return embedding

        # Calcular variação
        variance = np.var(embedding - previous_embedding)

        if variance < min_variance:
            # Variação muito baixa - injetar ruído
            noise_amplitude = np.sqrt(min_variance - variance)
            noise = np.random.normal(0.0, noise_amplitude, size=embedding.shape)
            embedding = embedding + noise

            self.logger.warning(
                f"Variação mínima violada ({variance:.6f} < {min_variance:.6f}). "
                f"Ruído injetado (amplitude={noise_amplitude:.6f})"
            )

        return embedding


__all__ = ["LangevinDynamics"]
