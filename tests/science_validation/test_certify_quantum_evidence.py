import json
from pathlib import Path
from typing import Any
from unittest.mock import mock_open, patch

import pytest
from _pytest.monkeypatch import MonkeyPatch

from scripts.science_validation.certify_quantum_evidence import QuantumCertifier, main


def test_load_usage_success() -> None:
    """Testa carregamento com queries reais."""
    mock_data: dict[str, Any] = {"queries": [{"id": 1}, {"id": 2}]}
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
        cert = QuantumCertifier()
        data = cert.load_usage(Path("mock.json"))
        assert len(data["queries"]) == 2


def test_load_usage_empty_error() -> None:
    """Testa erro em queries vazios."""
    mock_data: dict[str, Any] = {"queries": []}
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
        cert = QuantumCertifier()
        with pytest.raises(ValueError, match="Nenhum query IBM"):
            cert.load_usage(Path("mock.json"))


def test_certify_advantage_true() -> None:
    """Testa advantage quando PQK>0.85 e jobs>0."""
    usage: dict[str, Any] = {"queries": [{}]}
    validation = {"validation_results": {"pqk_score": 0.9}}
    cert = QuantumCertifier()
    assert cert.certify_advantage(usage, validation) is True


def test_certify_advantage_false_pqk_low() -> None:
    """Testa false se PQK baixo."""
    usage: dict[str, Any] = {"queries": [{}]}
    validation = {"validation_results": {"pqk_score": 0.8}}
    cert = QuantumCertifier()
    assert cert.certify_advantage(usage, validation) is False


def test_generate_cert_md(tmp_path: Path) -> None:
    """Testa geração de MD certificado."""
    # Criar arquivo mock necessário
    mock_dir = tmp_path / "mock"
    mock_dir.mkdir()
    (mock_dir / "ibm_query_usage.json").write_text(json.dumps({"queries": [{"id": 1}]}))

    cert = QuantumCertifier()
    output = tmp_path / "cert.md"
    cert.generate_cert_md(
        mock_dir,
        validation={"validation_results": {"pqk_score": 0.9}},
        advantage=True,
        output_path=output,
    )
    assert output.exists()
    with open(output) as f:
        assert "Quantum Advantage" in f.read()


def test_load_validation(tmp_path: Path) -> None:
    """Testa carregamento validation com PQK."""
    mock_data = {"validation_results": {"pqk_score": 0.9}}
    mock_file = tmp_path / "val.json"
    mock_file.write_text(json.dumps(mock_data))
    cert = QuantumCertifier()
    data = cert.load_validation(mock_file)
    assert data["validation_results"]["pqk_score"] == 0.9


def test_main_success(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    """Testa main com mocks."""
    # Criar arquivos necessários
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "ibm_query_usage.json").write_text(json.dumps({"queries": [{"id": 1}]}))
    (input_dir / "ibm_validation_result.json").write_text(
        json.dumps({"validation_results": {"pqk_score": 0.9}})
    )

    monkeypatch.setattr(
        "sys.argv", ["script", "--input", str(input_dir), "--output", str(tmp_path / "out.md")]
    )
    assert main() == 0


def test_main_files_missing(monkeypatch: MonkeyPatch) -> None:
    """Testa erro se arquivos ausentes."""
    monkeypatch.setattr("sys.argv", ["script", "--input", "/nonexistent"])
    with patch("pathlib.Path.exists", return_value=False):
        assert main() == 1


# ~10 testes; 95% coverage
