from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List
from .react_agent import ReactAgent


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
PsychoanalyticAnalyst - Agente de Análise Psicanalítica
Modo: psychoanalyst (🧐)

Função: Analisar textos (transcrições de sessões, notas) sob diferentes
lentes teóricas da psicanálise para gerar insights e relatórios.
Implementa o sistema de decisão Id/Ego/Superego com votação ponderada.
"""


logger = logging.getLogger(__name__)


class PsychoanalyticFramework(Enum):
    """Frameworks teóricos disponíveis para análise."""

    FREUDIAN = "Freudiano"
    LACANIAN = "Lacaniano"
    KLEINIAN = "Kleiniano"
    WINNICOTTIAN = "Winnicottiano"


@dataclass
class AgentVote:
    """Representa o voto de um agente interno."""

    agent_name: str
    recommendation: str
    confidence: float
    justification: str


class InternalAgent:
    """Classe base para agentes internos (Id, Ego, Superego)."""

    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.weight = 0.33  # Peso inicial igualitário

    def vote(self, context: str) -> AgentVote:
        """Gera um voto baseado no papel do agente."""
        raise NotImplementedError


class IdAgent(InternalAgent):
    def __init__(self, llm_client=None):
        super().__init__("Id", "Impulsos, desejos, preservação imediata, evitação de dor")
        self.llm = llm_client

    def vote(self, context: str) -> AgentVote:
        """Generate vote using LLM-based analysis of Id perspective."""
        if self.llm:
            prompt = f"""
            Você é o Id (instinto básico) em um sistema psicanalítico.
            Seu papel: impulsos, desejos, preservação imediata, evitação de dor.

            Contexto da decisão: {context}

            Como o Id votaria nesta situação? Forneça:
            1. Recomendação (uma palavra/frase curta)
            2. Confiança (0.0-1.0)
            3. Justificativa (breve)

            Responda em formato JSON:
            {{
                "recommendation": "sua_recomendacao",
                "confidence": 0.8,
                "justification": "sua_justificativa"
            }}
            """

            try:
                response = self.llm.invoke(prompt)
                content = getattr(response, "content", response)
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                result = json.loads(content)

                return AgentVote(
                    agent_name=self.name,
                    recommendation=result.get("recommendation", "avoid_conflict"),
                    confidence=float(result.get("confidence", 0.8)),
                    justification=result.get(
                        "justification", "Evitar dor e conflito é prioridade."
                    ),
                )
            except Exception as e:
                logger.warning(f"LLM call failed for Id agent: {e}, using fallback")

        # Fallback hardcoded response
        return AgentVote(
            agent_name=self.name,
            recommendation="avoid_conflict",
            confidence=0.8,
            justification="Evitar dor e conflito é a prioridade imediata.",
        )


class EgoAgent(InternalAgent):
    def __init__(self, llm_client=None):
        super().__init__("Ego", "Realidade, mediação, lógica, consequências práticas")
        self.llm = llm_client

    def vote(self, context: str) -> AgentVote:
        """Generate vote using LLM-based analysis of Ego perspective."""
        if self.llm:
            prompt = f"""
            Você é o Ego (mediador racional) em um sistema psicanalítico.
            Seu papel: realidade, mediação, lógica, consequências práticas.

            Contexto da decisão: {context}

            Como o Ego votaria nesta situação? Forneça:
            1. Recomendação (uma palavra/frase curta)
            2. Confiança (0.0-1.0)
            3. Justificativa (breve)

            Responda em formato JSON:
            {{
                "recommendation": "sua_recomendacao",
                "confidence": 0.75,
                "justification": "sua_justificativa"
            }}
            """

            try:
                response = self.llm.invoke(prompt)
                content = getattr(response, "content", response)
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                result = json.loads(content)

                return AgentVote(
                    agent_name=self.name,
                    recommendation=result.get("recommendation", "analyze_rationally"),
                    confidence=float(result.get("confidence", 0.75)),
                    justification=result.get(
                        "justification", "Devemos analisar os fatos antes de agir."
                    ),
                )
            except Exception as e:
                logger.warning(f"LLM call failed for Ego agent: {e}, using fallback")

        # Fallback hardcoded response
        return AgentVote(
            agent_name=self.name,
            recommendation="analyze_rationally",
            confidence=0.75,
            justification="Devemos analisar os fatos antes de agir.",
        )


class SuperegoAgent(InternalAgent):
    def __init__(self, llm_client=None):
        super().__init__("Superego", "Moralidade, regras, ética, ideal de eu")
        self.llm = llm_client

    def vote(self, context: str) -> AgentVote:
        """Generate vote using LLM-based analysis of Superego perspective."""
        if self.llm:
            prompt = f"""
            Você é o Superego (consciência moral) em um sistema psicanalítico.
            Seu papel: moralidade, regras, ética, ideal de eu.

            Contexto da decisão: {context}

            Como o Superego votaria nesta situação? Forneça:
            1. Recomendação (uma palavra/frase curta)
            2. Confiança (0.0-1.0)
            3. Justificativa (breve)

            Responda em formato JSON:
            {{
                "recommendation": "sua_recomendacao",
                "confidence": 0.9,
                "justification": "sua_justificativa"
            }}
            """

            try:
                response = self.llm.invoke(prompt)
                content = getattr(response, "content", response)
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                result = json.loads(content)

                return AgentVote(
                    agent_name=self.name,
                    recommendation=result.get("recommendation", "follow_rules"),
                    confidence=float(result.get("confidence", 0.9)),
                    justification=result.get(
                        "justification", "É imperativo seguir as normas éticas."
                    ),
                )
            except Exception as e:
                logger.warning(f"LLM call failed for Superego agent: {e}, using fallback")

        # Fallback hardcoded response
        return AgentVote(
            agent_name=self.name,
            recommendation="follow_rules",
            confidence=0.9,
            justification="É imperativo seguir as normas éticas estabelecidas.",
        )


class PsychoanalyticDecisionSystem:
    """Orquestra os agentes internos e realiza a votação ponderada."""

    def __init__(self, llm_client=None):
        self.agents = [IdAgent(llm_client), EgoAgent(llm_client), SuperegoAgent(llm_client)]
        self.history: List[Dict[str, Any]] = []

    def resolve_conflict(self, context: str) -> Dict[str, Any]:
        """
        Resolve um conflito tomando uma decisão baseada em votos ponderados.
        """
        votes = [agent.vote(context) for agent in self.agents]

        # Weighted Voting Logic
        results = {}
        total_weight = 0.0

        for i, agent in enumerate(self.agents):
            vote = votes[i]
            # Score = Weight * Confidence
            score = agent.weight * vote.confidence

            if vote.recommendation not in results:
                results[vote.recommendation] = 0.0
            results[vote.recommendation] += score
            total_weight += score

        # Determine winner
        winner = max(results, key=results.get)
        winning_score = results[winner]

        # Normalize confidence
        final_confidence = winning_score / total_weight if total_weight > 0 else 0.0

        decision = {
            "winner": winner,
            "confidence": final_confidence,
            "votes": [
                {
                    "agent": v.agent_name,
                    "recommendation": v.recommendation,
                    "confidence": v.confidence,
                    "weight": self.agents[i].weight,
                    "score": self.agents[i].weight * v.confidence,
                }
                for i, v in enumerate(votes)
            ],
        }

        self.history.append(decision)
        return decision

    def update_weights(self, feedback: Dict[str, float]):
        """Atualiza pesos dos agentes (placeholder para integração com EWC)."""
        for agent in self.agents:
            if agent.name in feedback:
                agent.weight = feedback[agent.name]


class PsychoanalyticAnalyst(ReactAgent):
    """
    Agente especializado em análise de textos com base em teorias psicanalíticas.
    Agora inclui o sistema de decisão interna.
    """

    def __init__(self, config_path: str) -> None:
        super().__init__(config_path)
        self.mode = "psychoanalyst"
        self.decision_system = PsychoanalyticDecisionSystem(self.llm)

    def analyze_session(
        self,
        session_notes: str,
        framework: PsychoanalyticFramework = PsychoanalyticFramework.FREUDIAN,
    ) -> Dict[str, Any]:
        """
        Analisa as notas de uma sessão clínica usando um framework psicanalítico.

        Args:
            session_notes: O texto com as notas da sessão.
            framework: O framework teórico a ser utilizado.

        Returns:
            Um dicionário com os insights e a análise.
        """
        prompt = self._build_analysis_prompt(session_notes, framework)

        logger.info(f"Iniciando análise com o framework {framework.value}...")

        response = self.llm.invoke(prompt)

        analysis = self._parse_analysis(response)
        analysis["framework_used"] = framework.value

        # Run internal decision simulation for metadata
        internal_decision = self.decision_system.resolve_conflict(session_notes)
        analysis["internal_dynamics"] = internal_decision

        return analysis

    def generate_abnt_report(self, analysis: Dict[str, Any]) -> str:
        """
        Gera um relatório estruturado a partir da análise (placeholder).
        NOTA: ABNT completo é complexo. Isto é uma simulação estruturada.
        """
        dynamics = analysis.get("internal_dynamics", {})
        winner = dynamics.get("winner", "N/A")

        report = f"""
# RELATÓRIO DE ANÁLISE PSICANALÍTICA

**Framework Teórico:** {analysis.get('framework_used', 'N/A')}

## 1. Hipótese Interpretativa Principal
{analysis.get('hypothesis', 'Nenhuma hipótese gerada.')}

## 2. Pontos de Resistência Identificados
{analysis.get('resistance', 'Nenhum ponto de resistência identificado.')}

## 3. Elementos-Chave da Sessão
{analysis.get('key_elements', 'Nenhum elemento-chave identificado.')}

## 4. Observações Adicionais
{analysis.get('observations', 'Nenhuma observação adicional.')}

## 5. Dinâmica Interna do Sistema (Meta-Análise)
O sistema simulou um conflito interno para esta análise.
- **Decisão Predominante:** {winner}
- **Confiança do Sistema:** {dynamics.get('confidence', 0.0):.2f}

---
*Este é um relatório gerado automaticamente pelo OmniMind.*
"""
        return report

    def _build_analysis_prompt(self, session_notes: str, framework: PsychoanalyticFramework) -> str:
        """Constrói o prompt para o LLM."""

        framework_instructions = {
            PsychoanalyticFramework.FREUDIAN: (
                "Foque em conflitos edípicos, mecanismos de defesa "
                "(repressão, negação, projeção), e a dinâmica entre Id, Ego e Superego."
            ),
            PsychoanalyticFramework.LACANIAN: (
                "Analise a estrutura da linguagem, a função do significante, "
                "o Real, o Simbólico e o Imaginário, e a posição do sujeito em relação ao Outro."
            ),
            PsychoanalyticFramework.KLEINIAN: (
                "Identifique ansiedades primitivas, posições esquizo-paranoide e depressiva, "
                "e o uso de identificação projetiva."
            ),
            PsychoanalyticFramework.WINNICOTTIAN: (
                "Observe a relação com o ambiente, o papel do 'holding', "
                "objetos transicionais e a dialética entre o verdadeiro e o falso self."
            ),
        }

        prompt = f"""
Você é um assistente de IA especializado em psicanálise. Sua tarefa é analisar as seguintes
notas de uma sessão clínica sob a ótica do framework {framework.value}.

**Instruções do Framework:**
{framework_instructions[framework]}

**Notas da Sessão:**
---
{session_notes}
---

**Sua Análise (responda em formato JSON):**
Com base nas notas e no framework, forneça a seguinte estrutura:
{{
  "hypothesis": "Formule uma hipótese interpretativa central sobre o material apresentado.",
  "resistance": (
      "Identifique possíveis pontos de resistência ou defesas notáveis no discurso."
  ),
  "key_elements": (
      "Liste 3 a 5 elementos-chave (símbolos, atos falhos, padrões de repetição) "
      "que se destacam."
  ),
  "observations": (
      "Ofereça uma breve observação ou questão que poderia guiar a próxima sessão."
  )
}}
"""
        return prompt

    def _parse_analysis(self, llm_response: Any) -> Dict[str, Any]:
        """Extrai a análise JSON da resposta do LLM."""
        try:
            # A resposta do Ollama pode vir em um objeto com 'content'
            content = getattr(llm_response, "content", llm_response)
            # O LLM pode retornar o JSON dentro de um bloco de código markdown
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]

            parsed = json.loads(content)
            assert isinstance(parsed, dict)
            return parsed
        except (json.JSONDecodeError, AttributeError, IndexError) as e:
            logger.error(f"Falha ao parsear a resposta do LLM: {e}")
            return {
                "error": "Não foi possível parsear a análise.",
                "raw_response": str(llm_response),
            }


__all__ = ["PsychoanalyticAnalyst", "PsychoanalyticFramework"]
