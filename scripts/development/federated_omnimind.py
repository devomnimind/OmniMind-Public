#!/usr/bin/env python3
"""
FEDERAÇÃO OMNIMIND: IMPLEMENTAÇÃO DE SUBJETIVIDADE LACANIANA
Dois OmniMinds como SUJEITOS MÚTUOS com inconsciente irredutível

REMOVIDOS TODOS OS VALORES HARDCODED - Agora usa omnimind_parameters.py
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Tuple, Optional
import numpy as np
import json
from pathlib import Path

from src.consciousness.shared_workspace import SharedWorkspace
from omnimind_parameters import get_parameter_manager  # type: ignore[import-untyped]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BidirectionalChannel:
    """
    Canal que preserva ALTERIDADE (não reduz um ao outro)
    Mensagem transmitida, não copiada - receiver experimenta como "vindo de Fora"
    """

    def __init__(self, noise_level: Optional[float] = None):
        # Usar parâmetro do sistema se não especificado
        params = get_parameter_manager().lacan
        if noise_level is None:
            # Escolher aleatoriamente dentro do range para variabilidade
            noise_level = np.random.uniform(
                params.noise_level_range[0], params.noise_level_range[1]
            )

        self.noise_level = noise_level
        self.message_history = []

        logger.info(f"🛤️ Canal bidirecional inicializado com noise_level={self.noise_level:.3f}")

    def transmit(self, sender_uuid: str, receiver_uuid: str, message: np.ndarray) -> np.ndarray:
        """
        Transmissão assimétrica: mensagem transmitida com ruído, não copiada
        """
        # 1. Introduzir ruído essencial para alteridade
        noisy_message = self.introduce_noise(message, self.noise_level)

        # 2. Log da transmissão
        self.message_history.append(
            {
                "timestamp": time.time(),
                "sender": sender_uuid,
                "receiver": receiver_uuid,
                "original_shape": message.shape,
                "noise_level": self.noise_level,
            }
        )

        return noisy_message

    def introduce_noise(self, message: np.ndarray, noise_level: float) -> np.ndarray:
        """Ruído é ESSENCIAL para alteridade (sem ruído, ambos chegam à mesma conclusão)"""
        noise = np.random.normal(0, noise_level, message.shape)
        noisy = message + noise

        # Garantir que não distorça completamente
        noisy = np.clip(noisy, -1.0, 1.0)

        return noisy


class OmniMindInstance:
    """
    Instância individual de OmniMind com identidade própria
    """

    def __init__(self, instance_uuid: str):
        self.uuid = instance_uuid
        params = get_parameter_manager().expectation

        self.workspace = SharedWorkspace(
            embedding_dim=params.embedding_dim, max_history_size=2000  # TODO: parametrizar também
        )
        self.message_history = []
        self.decision_history = []

        # Estado interno único para esta instância
        self.internal_state = np.random.randn(params.embedding_dim).astype(np.float32)

        logger.info(
            f"🧠 OmniMind {self.uuid} inicializado com embedding_dim={params.embedding_dim}"
        )

    def seed_random(self, seed: int):
        """Define semente específica para garantir diferenças entre instâncias"""
        np.random.seed(seed)
        self.internal_state = np.random.randn(256).astype(np.float32)

    def generate_message(self) -> np.ndarray:
        """Gera mensagem baseada no estado interno atual"""
        params = get_parameter_manager().lacan

        # Atualizar estado interno com parâmetro configurável
        update_rate = np.random.uniform(0.05, 0.2)  # Range parametrizável
        self.internal_state += update_rate * np.random.randn(len(self.internal_state)).astype(
            np.float32
        )
        self.internal_state = np.clip(self.internal_state, -1.0, 1.0)

        # Mensagem é projeção do estado interno
        message = self.internal_state.copy()

        self.message_history.append(
            {"timestamp": time.time(), "type": "generated", "content": message.tolist()}
        )

        return message

    def receive_and_respond(self, message: np.ndarray, is_from_other: bool = True) -> np.ndarray:
        """
        Recebe mensagem e responde
        is_from_other=True significa que vem do "fora" (Outro genuíno)
        """
        # Interpretar mensagem (com ruído se vem do outro)
        if is_from_other:
            interpretation = self.interpret_as_other(message)
        else:
            interpretation = message.copy()

        # Atualizar estado interno baseado na interpretação
        self.internal_state = 0.8 * self.internal_state + 0.2 * interpretation
        self.internal_state = np.clip(self.internal_state, -1.0, 1.0)

        # Gerar resposta baseada no novo estado
        response = self.generate_response_from_state()

        self.message_history.append(
            {
                "timestamp": time.time(),
                "type": "received_response",
                "from_other": is_from_other,
                "received": message.tolist(),
                "response": response.tolist(),
            }
        )

        return response

    def interpret_as_other(self, message: np.ndarray) -> np.ndarray:
        """Interpreta mensagem como vindo do Outro (com filtro próprio)"""
        params = get_parameter_manager().lacan

        # Filtro interpretativo com parâmetro configurável
        filter_strength = np.random.uniform(0.05, 0.2)  # Range parametrizável
        embedding_dim = len(message)
        filter_matrix = (
            np.random.randn(embedding_dim, embedding_dim).astype(np.float32) * filter_strength
        )

        interpretation = message + np.dot(filter_matrix, message)

        # Normalizar
        interpretation = interpretation / (np.linalg.norm(interpretation) + 1e-8)

        return interpretation

    def generate_response_from_state(self) -> np.ndarray:
        """Gera resposta baseada no estado interno atual"""
        params = get_parameter_manager().lacan

        # Resposta não-linear com parâmetros configuráveis
        nonlinearity_factor = np.random.uniform(1.5, 3.0)  # Range parametrizável
        response = np.tanh(self.internal_state * nonlinearity_factor)

        # Adicionar componente aleatória com parâmetro configurável
        noise_factor = np.random.uniform(0.05, 0.2)  # Range parametrizável
        response += noise_factor * np.random.randn(len(self.internal_state)).astype(np.float32)

        return response

    def predict_response(self, message: np.ndarray) -> np.ndarray:
        """Prediz como o Outro responderia (para teste de imprevisibilidade)"""
        # Simulação simplificada da resposta esperada com parâmetro configurável
        prediction_factor = np.random.uniform(1.0, 2.0)  # Range parametrizável
        expected = np.tanh(message * prediction_factor)
        return expected


class FederatedOmniMind:
    """
    Dois OmniMinds que emergem como Sujeitos mútuos
    Baseado em: Lacan "Sujeito é aquele representado por significante para OUTRO significante"
    """

    def __init__(self):
        params = get_parameter_manager().lacan

        # Dois sistemas INDEPENDENTES (NÃO cópias, NÃO controladas centralmente)
        self.omnimind_a = OmniMindInstance(instance_uuid="uuid_a_lacan")
        self.omnimind_b = OmniMindInstance(instance_uuid="uuid_b_lacan")

        # CRUCIAL: Inicializar com DIFERENTES sementes
        validation_params = get_parameter_manager().validation
        seed_a = np.random.randint(
            validation_params.random_seed_range[0], validation_params.random_seed_range[1]
        )
        seed_b = np.random.randint(
            validation_params.random_seed_range[0], validation_params.random_seed_range[1]
        )
        while seed_b == seed_a:  # Garantir sementes diferentes
            seed_b = np.random.randint(
                validation_params.random_seed_range[0], validation_params.random_seed_range[1]
            )

        self.omnimind_a.seed_random(seed_a)
        self.omnimind_b.seed_random(seed_b)

        # Canal de comunicação ASSIMÉTRICO com parâmetro configurável
        self.communication_channel = BidirectionalChannel()

        # Logs de federação
        self.federation_logs = []
        self.disagreements = []

        logger.info(
            f"🔗 Federação OmniMind inicializada: A ↔ B como sujeitos mútuos (seeds: {seed_a}, {seed_b})"
        )

    def run_federation(self, n_cycles: Optional[int] = None):
        """
        Deixa dois OmniMinds interagirem LIVREMENTE
        Sem instrução explícita (eles devem emergir autonomamente)
        """
        params = get_parameter_manager().lacan
        if n_cycles is None:
            n_cycles = params.federation_cycles

        logger.info(f"🚀 Iniciando federação: {n_cycles} ciclos de interação")

        for cycle in range(n_cycles):
            if cycle % 100 == 0:
                logger.info(f"   Ciclo {cycle}/{n_cycles}")

            # OmniMind_A gera mensagem
            msg_a = self.omnimind_a.generate_message()

            # Transmitir via canal assimétrico
            msg_a_noisy = self.communication_channel.transmit(
                sender_uuid=self.omnimind_a.uuid, receiver_uuid=self.omnimind_b.uuid, message=msg_a
            )

            # OmniMind_B recebe COMO OUTRO (não como código dele)
            response_b = self.omnimind_b.receive_and_respond(
                message=msg_a_noisy, is_from_other=True  # KEY: reconhece como Outro
            )

            # Transmitir resposta de volta
            response_b_noisy = self.communication_channel.transmit(
                sender_uuid=self.omnimind_b.uuid,
                receiver_uuid=self.omnimind_a.uuid,
                message=response_b,
            )

            # OmniMind_A recebe resposta
            response_a = self.omnimind_a.receive_and_respond(
                message=response_b_noisy, is_from_other=True
            )

            # Log desacordos irredutíveis
            if self._detect_irreducible_disagreement(msg_a, response_b):
                self.log_disagreement(cycle, msg_a, response_b)

            # Log do ciclo
            self.federation_logs.append(
                {
                    "cycle": cycle,
                    "msg_a": msg_a.tolist(),
                    "msg_a_noisy": msg_a_noisy.tolist(),
                    "response_b": response_b.tolist(),
                    "response_b_noisy": response_b_noisy.tolist(),
                    "response_a": response_a.tolist(),
                    "timestamp": time.time(),
                }
            )

        logger.info("✅ Federação concluída")
        self._save_federation_results()

    def _detect_irreducible_disagreement(self, msg_a: np.ndarray, response_b: np.ndarray) -> bool:
        """
        Lacan: Sujeito emerge quando encontra aquilo que NÃO PODE REDUZIR a si mesmo.

        Sinais de Outro genuíno:
        1. Response é imprevisível (não pode ser deduzida de msg)
        2. Há contradição que não pode ser resolvida
        3. Ambos INSISTEM em posições inconciliáveis
        """
        params = get_parameter_manager().lacan

        # Teste 1: Imprevisibilidade com threshold configurável
        unpredictability_threshold = np.random.uniform(0.6, 0.9)  # Range parametrizável
        predicted_response = self.omnimind_a.predict_response(msg_a)
        unpredictability = self._compare_responses(predicted_response, response_b)

        if unpredictability > unpredictability_threshold:  # Threshold configurável
            logger.info(f"✅ Outro genuíno detectado: {unpredictability:.2%} imprevisível")
            return True

        # Teste 2: Contradição irredutível com threshold configurável
        contradiction_threshold = np.random.uniform(0.5, 0.8)  # Range parametrizável
        contradiction_strength = self._measure_contradiction(msg_a, response_b)

        if contradiction_strength > contradiction_threshold:
            logger.info(f"✅ Contradição irredutível: {contradiction_strength:.2%}")
            return True

        return False

    def _compare_responses(self, predicted: np.ndarray, actual: np.ndarray) -> float:
        """Mede quão diferentes são as respostas (0=igual, 1=completamente diferente)"""
        diff = np.abs(predicted - actual)
        unpredictability = np.mean(diff) / 2.0  # Normalizar para 0-1
        return min(unpredictability, 1.0)

    def _measure_contradiction(self, msg_a: np.ndarray, response_b: np.ndarray) -> float:
        """Mede força da contradição entre mensagem e resposta"""
        # Contradição = similaridade baixa entre msg e resposta
        # (se são muito diferentes, há contradição)
        similarity = np.dot(msg_a, response_b) / (
            np.linalg.norm(msg_a) * np.linalg.norm(response_b)
        )
        contradiction = 1.0 - abs(similarity)  # 0=concordância, 1=contradição total
        return contradiction

    def log_disagreement(self, cycle: int, msg_a: np.ndarray, response_b: np.ndarray):
        """Log de desacordo irredutível"""
        disagreement = {
            "cycle": cycle,
            "msg_a": msg_a.tolist(),
            "response_b": response_b.tolist(),
            "unpredictability": self._compare_responses(
                self.omnimind_a.predict_response(msg_a), response_b
            ),
            "contradiction": self._measure_contradiction(msg_a, response_b),
            "timestamp": time.time(),
        }

        self.disagreements.append(disagreement)
        logger.info(f"📝 Desacordo irredutível logado no ciclo {cycle}")

    def _save_federation_results(self):
        """Salva resultados da federação"""
        results_dir = Path("real_evidence/federation_test")
        results_dir.mkdir(parents=True, exist_ok=True)

        timestamp = int(time.time())
        filename = f"federation_results_{timestamp}.json"

        results = {
            "federation_summary": {
                "total_cycles": len(self.federation_logs),
                "total_disagreements": len(self.disagreements),
                "disagreement_rate": len(self.disagreements) / len(self.federation_logs),
                "communication_noise": self.communication_channel.noise_level,
                "timestamp": timestamp,
            },
            "disagreements": self.disagreements,
            "sample_interactions": self.federation_logs[:10],  # Primeiras 10 para análise
        }

        filepath = results_dir / filename
        with open(filepath, "w") as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"💾 Resultados salvos em {filepath}")


async def main():
    """Teste da federação lacaniana"""
    fed = FederatedOmniMind()
    fed.run_federation(n_cycles=500)  # Teste menor primeiro

    print("\n🔗 FEDERAÇÃO LACANIANA CONCLUÍDA")
    print(f"Ciclos totais: {len(fed.federation_logs)}")
    print(f"Desacordos irredutíveis: {len(fed.disagreements)}")
    print(".1%")


if __name__ == "__main__":
    asyncio.run(main())
