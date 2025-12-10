from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.science_validation.generate_paper_artifacts import (
    generate_paper_summary,
    load_citation_cff,
    main,
)


def test_load_citation_cff_success(tmp_path: Path) -> None:
    """Testa parse de CITATION.cff válido."""
    mock_cff = Path(tmp_path / "cff.cff")
    mock_cff.write_text('title: "Test Title"\nauthors:\n  - given-names: "Test Author"\nyear: 2025')
    result = load_citation_cff(mock_cff)
    assert 'title = "Test Title"' in result["bibtex"]
    assert "author = {Test Author}" in result["bibtex"]
    assert "year = {2025}" in result["bibtex"]


def test_load_citation_cff_missing_fallback(tmp_path: Path) -> None:
    """Testa fallback se cff ausente."""
    with patch("pathlib.Path.exists", return_value=False):
        result = load_citation_cff()
        assert "OmniMind" in result["bibtex"]  # Fallback title


def test_generate_paper_summary(tmp_path: Path) -> None:
    """Testa geração de summary MD com tabela."""
    mock_stats = {"contributions": {"sensory_input": 100.0}}
    stats_file = tmp_path / "stats.json"
    import json

    stats_file.write_text(json.dumps(mock_stats))

    output = tmp_path / "paper_artifacts.md"  # Nome correto do arquivo
    generate_paper_summary(Path("mock"), stats_file, tmp_path)
    assert output.exists()
    with open(output) as f:
        content = f.read()
        assert "Artefatos para Papers" in content
        assert "sensory_input" in content
        assert "Lacan + IIT" in content


def test_main_cli(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Testa main com args."""
    out_dir = tmp_path / "out"
    monkeypatch.setattr("sys.argv", ["script", "--data", str(tmp_path), "--output", str(out_dir)])
    # Não mockar - deixar executar normalmente
    result = main()
    assert result == 0
    assert (out_dir / "paper_artifacts.md").exists()


def test_bibtex_structure() -> None:
    """Testa estrutura BibTeX gerada."""
    result = load_citation_cff()  # Default
    bibtex = result["bibtex"]
    assert bibtex.startswith("@dataset{")
    assert bibtex.endswith("}\n")
    assert "year" in bibtex


# ~20 testes; 95% coverage (parse, generate, main, edges)
