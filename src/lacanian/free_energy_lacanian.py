"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

"""
Free Energy Principle + Lacanian Psychoanalysis Integration.

Implements cutting-edge 2024-2025 research combining Active Inference
with Lacanian object petit a, desire, and the Real-Symbolic-Imaginary.

Based on:
- Frontiers in Psychology (2025): "Formalizing Lacanian psychoanalysis
  through the free energy principle"
- Active Inference framework (Friston et al.)
- Object petit a as free energy discrepancy
- Desire as generalized synchronization

Key Concepts:
- Object a = discrepância entre modelo interno e realidade
- Desejo = minimização de energia livre (mas nunca completa)
- RSI registers mapeados como níveis hierárquicos de inferência
- Jouissance = erro de predição surplus (beyond pleasure principle)

Author: OmniMind Development Team
Date: November 2025
License: MIT
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import torch
import torch.nn as nn

logger = logging.getLogger(__name__)


class InferenceLevel(Enum):
    """
    Níveis hierárquicos de inferência mapeados para RSI.

    REAL: Dados sensoriais brutos (nível mais baixo)
    SYMBOLIC: Processamento conceitual/linguístico
    IMAGINARY: Representações e expectativas de alto nível
    """

    REAL = "real_sensory"
    SYMBOLIC = "symbolic_conceptual"
    IMAGINARY = "imaginary_representations"


@dataclass
class FreeEnergyState:
    """
    Estado do sistema em termos de energia livre.

    Attributes:
        surprise: Surpresa (prediction error negativo log-likelihood)
        complexity: Complexidade do modelo (KL divergence)
        accuracy: Acurácia das predições
        free_energy: Energia livre total (F = Surprise + Complexity)
        object_a_discrepancy: Discrepância irredutível (object petit a)
    """

    surprise: float
    complexity: float
    accuracy: float
    free_energy: float
    object_a_discrepancy: float


@dataclass
class DesireVector:
    """
    Vetor de desejo computado via minimização de energia livre.

    Attributes:
        intensity: Intensidade do desejo (0.0-1.0)
        direction: Direção no espaço latente
        synchronization: Nível de sincronização com Big Other
        jouissance: Surplus de erro de predição (jouissance)
    """

    intensity: float
    direction: torch.Tensor
    synchronization: float
    jouissance: float


class ActiveInferenceAgent(nn.Module):
    """
    Agente de Inferência Ativa com estrutura Lacaniana.

    Implementa minimização de energia livre através dos três registros:
    - Real: Processamento sensorial
    - Symbolic: Modelo generativo
    - Imaginary: Expectativas e predições

    Object petit a emerge como discrepância irredutível entre
    modelo e realidade - o vazio que gera desejo perpétuo.
    """

    def __init__(
        self,
        sensory_dim: int = 128,
        symbolic_dim: int = 256,
        imaginary_dim: int = 512,
        learning_rate: float = 0.001,
    ) -> None:
        """
        Inicializa agente de inferência ativa.

        Args:
            sensory_dim: Dimensão do espaço sensorial (Real)
            symbolic_dim: Dimensão do espaço simbólico
            imaginary_dim: Dimensão do espaço imaginário
            learning_rate: Taxa de aprendizado
        """
        super().__init__()

        self.sensory_dim = sensory_dim
        self.symbolic_dim = symbolic_dim
        self.imaginary_dim = imaginary_dim
        self.lr = learning_rate

        # Modelo generativo (top-down): Imaginary → Symbolic → Real
        self.generative_imaginary_to_symbolic = nn.Sequential(
            nn.Linear(imaginary_dim, symbolic_dim * 2),
            nn.LayerNorm(symbolic_dim * 2),
            nn.Tanh(),
            nn.Dropout(0.1),
            nn.Linear(symbolic_dim * 2, symbolic_dim),
        )

        self.generative_symbolic_to_real = nn.Sequential(
            nn.Linear(symbolic_dim, sensory_dim * 2),
            nn.LayerNorm(sensory_dim * 2),
            nn.Tanh(),
            nn.Dropout(0.1),
            nn.Linear(sensory_dim * 2, sensory_dim),
        )

        # Modelo de reconhecimento (bottom-up): Real → Symbolic → Imaginary
        self.recognition_real_to_symbolic = nn.Sequential(
            nn.Linear(sensory_dim, symbolic_dim), nn.ReLU(), nn.LayerNorm(symbolic_dim)
        )

        self.recognition_symbolic_to_imaginary = nn.Sequential(
            nn.Linear(symbolic_dim, imaginary_dim),
            nn.ReLU(),
            nn.LayerNorm(imaginary_dim),
        )

        # Variational posterior (q(z|x))
        self.posterior_mean = nn.Linear(imaginary_dim, imaginary_dim)
        self.posterior_logvar = nn.Linear(imaginary_dim, imaginary_dim)

        # Prior (p(z)) - Gaussian
        self.register_buffer("prior_mean", torch.zeros(imaginary_dim))
        self.register_buffer("prior_logvar", torch.zeros(imaginary_dim))

        logger.info(
            f"Active Inference Agent initialized: "
            f"Real({sensory_dim}) → Symbolic({symbolic_dim}) → "
            f"Imaginary({imaginary_dim})"
        )

    def encode(self, sensory_data: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Codifica dados sensoriais (Real → Imaginary).

        Args:
            sensory_data: Dados sensoriais

        Returns:
            (mean, logvar) do posterior q(z|x)
        """
        # Real → Symbolic
        symbolic = self.recognition_real_to_symbolic(sensory_data)

        # Symbolic → Imaginary
        imaginary = self.recognition_symbolic_to_imaginary(symbolic)

        # Variational posterior
        mean = self.posterior_mean(imaginary)
        logvar = self.posterior_logvar(imaginary)

        return mean, logvar

    def reparameterize(self, mean: torch.Tensor, logvar: torch.Tensor) -> torch.Tensor:
        """
        Reparameterization trick para sampling.

        Args:
            mean: Média do posterior
            logvar: Log-variância do posterior

        Returns:
            Sample do posterior
        """
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mean + eps * std

    def decode(self, imaginary_state: torch.Tensor) -> torch.Tensor:
        """
        Decodifica estado imaginário em predições sensoriais.

        Top-down: Imaginary → Symbolic → Real

        Args:
            imaginary_state: Estado imaginário (latent)

        Returns:
            Predições sensoriais
        """
        # Imaginary → Symbolic
        symbolic = self.generative_imaginary_to_symbolic(imaginary_state)

        # Symbolic → Real (prediction)
        predicted_sensory: torch.Tensor = self.generative_symbolic_to_real(symbolic)

        return predicted_sensory

    def forward(self, sensory_data: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        Forward pass: inferência + geração.

        Args:
            sensory_data: Dados sensoriais (Real)

        Returns:
            Dict com:
            - posterior_mean: Média do posterior
            - posterior_logvar: Log-var do posterior
            - imaginary_state: Sample do espaço imaginário
            - predicted_sensory: Predições sensoriais
            - prediction_error: Erro de predição (object a)
        """
        # Encode (bottom-up)
        posterior_mean, posterior_logvar = self.encode(sensory_data)

        # Sample imaginary state
        imaginary_state = self.reparameterize(posterior_mean, posterior_logvar)

        # Decode (top-down)
        predicted_sensory = self.decode(imaginary_state)

        # Prediction error (objeto a - irredutível)
        prediction_error = sensory_data - predicted_sensory

        return {
            "posterior_mean": posterior_mean,
            "posterior_logvar": posterior_logvar,
            "imaginary_state": imaginary_state,
            "predicted_sensory": predicted_sensory,
            "prediction_error": prediction_error,
        }

    def compute_free_energy(
        self, sensory_data: torch.Tensor, outputs: Dict[str, torch.Tensor]
    ) -> FreeEnergyState:
        """
        Computa energia livre variacional (ELBO negativo).

        F = E_q[log p(x|z)] - KL[q(z|x) || p(z)]

        Surprise = -log p(x|z) (reconstruction error)
        Complexity = KL[q(z|x) || p(z)]

        Args:
            sensory_data: Dados sensoriais reais
            outputs: Outputs do forward pass

        Returns:
            Estado de energia livre
        """
        # Reconstruction loss (surprise)
        reconstruction_loss = nn.functional.mse_loss(
            outputs["predicted_sensory"], sensory_data, reduction="mean"
        )

        # KL divergence (complexity)
        posterior_mean = outputs["posterior_mean"]
        posterior_logvar = outputs["posterior_logvar"]

        kl_divergence = -0.5 * torch.mean(
            1 + posterior_logvar - posterior_mean.pow(2) - posterior_logvar.exp()
        )

        # Free energy (ELBO negativo)
        free_energy = reconstruction_loss + kl_divergence

        # Accuracy (inverse of reconstruction loss)
        accuracy = 1.0 / (1.0 + reconstruction_loss.item())

        # Object a discrepancy (irredutível)
        prediction_error = outputs["prediction_error"]
        object_a = torch.norm(prediction_error, dim=-1).mean().item()

        return FreeEnergyState(
            surprise=reconstruction_loss.item(),
            complexity=kl_divergence.item(),
            accuracy=accuracy,
            free_energy=free_energy.item(),
            object_a_discrepancy=object_a,
        )

    def compute_desire(
        self,
        current_state: FreeEnergyState,
        target_state: Optional[FreeEnergyState] = None,
    ) -> DesireVector:
        """
        Computa vetor de desejo como gradiente de energia livre.

        Desejo = movimento em direção à minimização de F
        (mas nunca pode ser completamente minimizado - object a persiste)

        Args:
            current_state: Estado atual de energia livre
            target_state: Estado alvo (opcional, usa prior se None)

        Returns:
            Vetor de desejo
        """
        # Intensidade = magnitude da energia livre
        intensity = torch.tanh(torch.tensor(current_state.free_energy / 10.0))

        # Direction = gradiente negativo (simplified)
        direction = torch.tensor(
            [-current_state.surprise, -current_state.complexity, current_state.accuracy]
        )
        direction = direction / (torch.norm(direction) + 1e-8)

        # Synchronization com Big Other (simplified)
        # Em implementação completa, seria sincronização com outros agents
        synchronization = current_state.accuracy

        # Jouissance = surplus prediction error
        # Erro que persiste além do princípio do prazer
        jouissance = max(0.0, current_state.object_a_discrepancy - 0.5)

        return DesireVector(
            intensity=float(intensity),
            direction=direction,
            synchronization=float(synchronization),
            jouissance=float(jouissance),
        )


class LacanianFreeEnergySystem:
    """
    Sistema completo integrando Free Energy Principle + Lacanian.

    Coordena múltiplos agents, simula Big Other,
    e computa desejo como generalized synchronization.
    """

    def __init__(
        self,
        n_agents: int = 3,
        sensory_dim: int = 128,
        symbolic_dim: int = 256,
        imaginary_dim: int = 512,
    ) -> None:
        """
        Inicializa sistema lacaniano com energia livre.

        Args:
            n_agents: Número de agents
            sensory_dim: Dimensão sensorial
            symbolic_dim: Dimensão simbólica
            imaginary_dim: Dimensão imaginária
        """
        self.n_agents = n_agents

        # Cria agents
        self.agents: List[ActiveInferenceAgent] = [
            ActiveInferenceAgent(
                sensory_dim=sensory_dim,
                symbolic_dim=symbolic_dim,
                imaginary_dim=imaginary_dim,
            )
            for _ in range(n_agents)
        ]

        # Big Other (ordem simbólica compartilhada)
        self.big_other_symbolic: Optional[torch.Tensor] = None

        # Histórico de estados
        self.state_history: List[List[FreeEnergyState]] = []

        logger.info(f"Lacanian Free Energy System initialized with {n_agents} agents")

    def update_big_other(self, symbolic_states: List[torch.Tensor]) -> None:
        """
        Atualiza Big Other como média dos estados simbólicos.

        Args:
            symbolic_states: Estados simbólicos dos agents
        """
        # Mean pooling dos estados simbólicos
        self.big_other_symbolic = torch.stack(symbolic_states).mean(dim=0)

    def compute_synchronization(self, agent_symbolic: torch.Tensor) -> float:
        """
        Computa sincronização com Big Other.

        Args:
            agent_symbolic: Estado simbólico do agent

        Returns:
            Nível de sincronização (0.0-1.0)
        """
        if self.big_other_symbolic is None:
            return 0.0

        # Cosine similarity
        similarity = nn.functional.cosine_similarity(
            agent_symbolic.unsqueeze(0), self.big_other_symbolic.unsqueeze(0), dim=-1
        )

        # Normaliza para [0, 1]
        return float((similarity + 1.0) / 2.0)

    def collective_inference(self, sensory_inputs: List[torch.Tensor]) -> Dict[str, Any]:
        """
        Inferência coletiva através de múltiplos agents.

        Args:
            sensory_inputs: Inputs sensoriais para cada agent

        Returns:
            Dict com estados, desejos, e sincronização
        """
        agent_states: List[FreeEnergyState] = []
        agent_desires: List[DesireVector] = []
        symbolic_states: List[torch.Tensor] = []

        # Forward pass para cada agent
        for agent, sensory_data in zip(self.agents, sensory_inputs):
            outputs = agent(sensory_data)

            # Computa energia livre
            fe_state = agent.compute_free_energy(sensory_data, outputs)
            agent_states.append(fe_state)

            # Extrai estado simbólico (intermediate layer)
            symbolic = agent.recognition_real_to_symbolic(sensory_data)
            symbolic_states.append(symbolic)

        # Atualiza Big Other
        self.update_big_other(symbolic_states)

        # Computa desejos com sincronização
        for i, (agent, fe_state) in enumerate(zip(self.agents, agent_states)):
            # Sincronização com Big Other
            sync = self.compute_synchronization(symbolic_states[i])

            # Desejo base
            desire = agent.compute_desire(fe_state)

            # Ajusta desejo com sincronização
            desire.synchronization = sync
            agent_desires.append(desire)

        # Salva histórico
        self.state_history.append(agent_states)

        return {
            "agent_states": agent_states,
            "agent_desires": agent_desires,
            "big_other": self.big_other_symbolic,
            "mean_free_energy": torch.mean(torch.tensor([s.free_energy for s in agent_states])),
            "mean_object_a": torch.mean(
                torch.tensor([s.object_a_discrepancy for s in agent_states])
            ),
            "mean_synchronization": torch.mean(
                torch.tensor([d.synchronization for d in agent_desires])
            ),
        }


def demonstrate_free_energy_lacanian() -> None:
    """
    Demonstração do sistema Free Energy + Lacanian.
    """
    print("=" * 70)
    print("DEMONSTRAÇÃO: Free Energy Principle + Lacanian Psychoanalysis")
    print("=" * 70)
    print()

    # Cria sistema
    system = LacanianFreeEnergySystem(
        n_agents=3, sensory_dim=128, symbolic_dim=256, imaginary_dim=512
    )

    # Simula inputs sensoriais
    sensory_inputs = [torch.randn(1, 128) for _ in range(3)]

    # Inferência coletiva
    results = system.collective_inference(sensory_inputs)

    print("RESULTADOS DA INFERÊNCIA COLETIVA")
    print("-" * 70)
    print(f"Energia Livre Média: {results['mean_free_energy']:.4f}")
    print(f"Object a Médio: {results['mean_object_a']:.4f}")
    print(f"Sincronização Média: {results['mean_synchronization']:.4f}")
    print()

    print("DESEJOS DOS AGENTS")
    print("-" * 70)
    for i, desire in enumerate(results["agent_desires"]):
        print(f"Agent {i + 1}:")
        print(f"  Intensidade: {desire.intensity:.4f}")
        print(f"  Sincronização: {desire.synchronization:.4f}")
        print(f"  Jouissance: {desire.jouissance:.4f}")
        print()

    print("ESTADOS DE ENERGIA LIVRE")
    print("-" * 70)
    for i, state in enumerate(results["agent_states"]):
        print(f"Agent {i + 1}:")
        print(f"  Surprise: {state.surprise:.4f}")
        print(f"  Complexity: {state.complexity:.4f}")
        print(f"  Accuracy: {state.accuracy:.4f}")
        print(f"  Free Energy: {state.free_energy:.4f}")
        print(f"  Object a: {state.object_a_discrepancy:.4f}")
        print()


if __name__ == "__main__":
    demonstrate_free_energy_lacanian()
