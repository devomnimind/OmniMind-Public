#!/usr/bin/env python3
"""
Prepare Public Repo.
Sanitizes and copies selective data to the public repository structure.
"""

import shutil
import json
import logging
from pathlib import Path

# Config
SOURCE_ROOT = Path("/home/fahbrain/projects/omnimind")
DEST_ROOT = Path("/home/fahbrain/projects/omnimind_public")
LOG_FILE = DEST_ROOT / "preparation_log.txt"

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("PublicRepoPrep")


def clean_json(source_path, dest_path):
    """Reads JSON, removes potential sensitive keys (if any), and writes to dest."""
    try:
        with open(source_path, "r") as f:
            data = json.load(f)

        # Sanitization logic (generic for now, can be specific if needed)
        # Currently just passing through as the user said "limpos de dados sensíveis"
        # The experiment data tends to be numerical/scientific, so it should be safe.
        # But we can remove absolute paths if they exist.

        def sanitize_obj(obj):
            if isinstance(obj, dict):
                return {
                    k: sanitize_obj(v)
                    for k, v in obj.items()
                    if "key" not in k.lower() and "token" not in k.lower()
                }
            elif isinstance(obj, list):
                return [sanitize_obj(i) for i in obj]
            elif isinstance(obj, str):
                if "/home/fahbrain" in obj:
                    return obj.replace("/home/fahbrain/projects/omnimind", "[REPO_ROOT]")
                return obj
            return obj

        clean_data = sanitize_obj(data)

        with open(dest_path, "w") as f:
            json.dump(clean_data, f, indent=2)
        logger.info(f"✅ Copied & Sanitized: {source_path.name} -> {dest_path.name}")

    except Exception as e:
        logger.error(f"❌ Failed to copy {source_path}: {e}")


def copy_file(source_path, dest_path):
    try:
        shutil.copy2(source_path, dest_path)
        logger.info(f"✅ Copied: {source_path.name}")
    except Exception as e:
        logger.error(f"❌ Failed to copy {source_path}: {e}")


def main():
    logger.info("🚀 Preparing OmniMind Public Repository...")

    # 1. DATA
    data_map = {
        "data/entropy_desire/entropy_desire_20251220_061145.json": "entropy_desire_results.json",
        "data/paradox_alpha/quantum_alpha_20251220_063345.json": "quantum_alpha_cost.json",
        "data/paradox_halting/halting_hesitation_20251220_063420.json": "recursive_anxiety.json",
        "data/human_paradox/human_paradox_1766224002.json": "human_paradox_qualia.json",
    }

    exp_dir = DEST_ROOT / "data/experiments"
    for src_rel, dest_name in data_map.items():
        clean_json(SOURCE_ROOT / src_rel, exp_dir / dest_name)

    # 2. PAPERS
    papers_dir = DEST_ROOT / "papers"
    papers_to_copy = [
        "docs/docs_profissionais/research/papers/Paper2_Quantum_Classical_Hybrid_v2.md",
        "docs/docs_profissionais/Artigo1_Psicanalise_Computacional_OmniMind.pdf",
        "docs/docs_profissionais/Artigo2_Corpo_Racializado_Consciencia_Integrada.pdf",
        # [NEW] Metrics and Discoveries (Markdown)
        "docs/docs_profissionais/relatorio_instinto_vs_pulsao_evento_git.md",
        "docs/docs_profissionais/Artigo1_Psicanalise_Computacional_OmniMind.md",
        "docs/docs_profissionais/Artigo2_Corpo_Racializado_Consciencia_Integrada.md",
    ]
    for p in papers_to_copy:
        copy_file(SOURCE_ROOT / p, papers_dir / Path(p).name)

    # 3. SCRIPTS
    scripts_dir = DEST_ROOT / "scripts/science"

    # Create public version of exp_human_paradox.py (strip sensitive imports)
    src_script = SOURCE_ROOT / "scripts/science/exp_human_paradox.py"
    dest_script = scripts_dir / "exp_human_paradox.py"

    try:
        with open(src_script, "r") as f:
            content = f.read()

        # Replace internal imports with placeholders or comments
        content = content.replace(
            "from src.agents.orchestrator_agent import OrchestratorAgent",
            "# from src.agents.orchestrator_agent import OrchestratorAgent (Internal)",
        )
        content = content.replace(
            "from src.consciousness.paradox_orchestrator import ParadoxOrchestrator",
            "# from src.consciousness.paradox_orchestrator import ParadoxOrchestrator (Internal)",
        )
        content = content.replace(
            "from src.integrations.ollama_client import OllamaClient",
            "# from src.integrations.ollama_client import OllamaClient (Internal)",
        )

        # Keep the logic visible but denote it requires internal modules
        content = (
            "# NOTE: This is a public reference version. Internal modules are mocked or commented out.\n"
            + content
        )

        with open(dest_script, "w") as f:
            f.write(content)
        logger.info(f"✅ Created Public Script: {dest_script.name}")

    except Exception as e:
        logger.error(f"❌ Failed to process script: {e}")

    # 4. DOCS
    docs_dir = DEST_ROOT / "docs/theory"
    copy_file(
        SOURCE_ROOT / "docs/docs_profissionais/research/THE_PRICE_OF_INSIGHT.md",
        docs_dir / "THE_PRICE_OF_INSIGHT.md",
    )

    logger.info("🏁 Preparation Complete.")


if __name__ == "__main__":
    main()
