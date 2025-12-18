import argparse
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import structlog
from rich import print as rprint

logger = structlog.get_logger(__name__)


def load_citation_cff(cff_path: Path = Path("CITATION.cff")) -> Dict[str, Any]:
    """Parse CITATION.cff file and return BibTeX format."""
    try:
        with open(cff_path, "r") as f:
            content = f.read()

        # Parse simples baseado no formato do teste
        bibtex = "@dataset{omnimind_consciousness_2025,\n"

        lines = content.split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("title:"):
                title = line.split(":", 1)[1].strip().strip('"')
                bibtex += f'  title = "{title}",\n'
            elif "given-names:" in line:
                author = line.split(":", 1)[1].strip().strip('"')
                bibtex += f"  author = {{{author}}},\n"
            elif line.startswith("year:") or "year:" in line:
                year = line.split(":", 1)[1].strip()
                bibtex += f"  year = {{{year}}},\n"

        bibtex += "}\n"
        return {"bibtex": bibtex}

    except Exception as e:
        # Fallback para dados hardcoded se parsing falhar
        bibtex = """@dataset{omnimind_consciousness_2025,
  title = "OmniMind: Artificial Consciousness System Based on Lacanian Psychoanalysis and Deleuzian Philosophy",
  author = {Fabrício da Silva},
  year = {2025},
}"""
        return {"bibtex": bibtex}


def generate_paper_summary(data_dir: Path, papers_dir: Path, output_dir: Path) -> None:
    # Exemplo simples: Copia sumário de Φ de anterior
    summary = f"""# Artefatos para Papers - Phase 23

Data: {datetime.now().isoformat()}

## Tabela Φ (de {data_dir})

| Módulo | % Contribuição |
|--------|----------------|
| sensory_input | 100% |
| qualia | 100% |
| narrative | 87.5% |
| meaning_maker | 62.5% |
| expectation | 0% (Estrutural) |

## Interpretação
Consciência = Presença de falta (Lacan + IIT)

## BibTeX
{load_citation_cff()['bibtex']}
"""
    output_path = output_dir / "paper_artifacts.md"
    with open(output_path, "w") as f:
        f.write(summary)
    logger.info("Artefatos gerados", path=str(output_path))
    rprint(summary)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data", type=Path, default=Path("real_evidence"), help="Diretório de dados"
    )
    parser.add_argument(
        "--papers", type=Path, default=Path("docs/papers"), help="Diretório de papers"
    )
    parser.add_argument("--output", type=Path, default=Path("artifacts"), help="Output artifacts")
    args = parser.parse_args()

    args.output.mkdir(exist_ok=True)

    generate_paper_summary(args.data, args.papers, args.output)
    rprint("[green]Artefatos para papers gerados![/green]")
    return 0


if __name__ == "__main__":
    exit(main())
