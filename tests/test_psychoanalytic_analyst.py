"""Tests for the PsychoanalyticAnalyst agent."""

import json
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock

import pytest

from src.agents.psychoanalytic_analyst import (
    PsychoanalyticAnalyst,
    PsychoanalyticFramework,
)


@pytest.fixture
def analyst(tmp_path: Path) -> Generator[PsychoanalyticAnalyst, None, None]:
    """Fixture to create a PsychoanalyticAnalyst with a mocked LLM."""
    config_path = tmp_path / "agent_config.yaml"
    config_path.write_text(
        """
model:
  name: 'fake_model'
memory:
  qdrant_url: "http://localhost:6333"
  collection_name: "test_collection"
system:
  mcp_allowed_dirs: ["/tmp"]
  shell_whitelist: ["echo"]
  shell_timeout: 30
"""
    )

    # Mock dependencies of the parent ReactAgent
    with pytest.MonkeyPatch().context() as m:
        m.setattr("src.agents.react_agent.EpisodicMemory", MagicMock())
        m.setattr(
            "src.agents.react_agent.ReactAgent._run_supabase_memory_onboarding",
            MagicMock(),
        )

        agent = PsychoanalyticAnalyst(str(config_path))

        # Mock the LLM after initialization
        agent.llm = MagicMock()
        return agent


def test_analyst_initialization(analyst: PsychoanalyticAnalyst) -> None:
    """Test that the agent initializes correctly."""
    assert analyst.mode == "psychoanalyst"
    assert analyst.llm is not None


def test_analyze_session_freudian(analyst: PsychoanalyticAnalyst) -> None:
    """Test the session analysis with the Freudian framework."""
    session_notes = (
        "O paciente relata um sonho recorrente com seu pai, "
        "onde ele se sente pequeno e impotente."
    )

    mock_response = {
        "hypothesis": (
            "A hipótese é que o sonho reflete um complexo de Édipo não resolvido, "
            "com o pai como figura de autoridade castradora."
        ),
        "resistance": (
            "A tendência do paciente em minimizar a importância do sonho "
            "pode ser uma forma de resistência."
        ),
        "key_elements": "Sonho recorrente, figura paterna, sentimento de impotência.",
        "observations": (
            "Explorar a relação do paciente com figuras de autoridade " "em sua vida desperta."
        ),
    }

    # The LLM response might be a string or an object with a 'content' attribute
    mock_llm_output = MagicMock()
    mock_llm_output.content = json.dumps(mock_response)
    analyst.llm.invoke = MagicMock(return_value=mock_llm_output)

    result = analyst.analyze_session(session_notes, framework=PsychoanalyticFramework.FREUDIAN)

    # Verify that the correct prompt was built and sent to the LLM
    analyst.llm.invoke.assert_called_once()
    prompt_arg = analyst.llm.invoke.call_args[0][0]
    assert prompt_arg.strip().startswith("Você é um assistente de IA especializado em psicanálise.")
    assert f"framework {PsychoanalyticFramework.FREUDIAN.value}" in prompt_arg
    assert session_notes in prompt_arg

    # Verify the parsed result
    assert result["framework_used"] == "Freudiano"
    assert result["hypothesis"] == mock_response["hypothesis"]
    assert result["resistance"] == mock_response["resistance"]


def test_generate_abnt_report(analyst: PsychoanalyticAnalyst) -> None:
    """Test the generation of a structured report."""
    analysis_data = {
        "framework_used": "Lacaniano",
        "hypothesis": (
            "O discurso do paciente opera na cadeia de significantes, "
            "onde o sintoma é uma metáfora de uma verdade não dita."
        ),
        "resistance": (
            "O silêncio em certos tópicos funciona como uma barra "
            "entre o significante e o significado."
        ),
        "key_elements": "Ato falho, o Outro, o objeto a.",
        "observations": "Investigar qual significante mestre organiza o discurso do paciente.",
    }

    report = analyst.generate_abnt_report(analysis_data)

    assert "RELATÓRIO DE ANÁLISE PSICANALÍTICA" in report
    assert "**Framework Teórico:** Lacaniano" in report
    assert analysis_data["hypothesis"] in report
    assert analysis_data["resistance"] in report


def test_parse_analysis_handles_errors(analyst: PsychoanalyticAnalyst) -> None:
    """Test that the parser handles invalid LLM responses gracefully."""
    invalid_response = MagicMock()
    invalid_response.content = "This is not a valid JSON."

    analyst.llm.invoke.return_value = invalid_response

    result = analyst.analyze_session("some notes")

    assert "error" in result
    assert "Não foi possível parsear a análise." in result["error"]
    assert "raw_response" in result
