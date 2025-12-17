#!/usr/bin/env python3
"""
Análise rápida dos módulos de consciência.
Verifica stubs (pass), métodos vazios, imports e status de implementação.
"""

import ast
import logging
from pathlib import Path
from typing import Dict, List, Tuple

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

MODULES_TO_CHECK = [
    ("expectation", "src/consciousness/expectation_module.py"),
    ("sensory_input", "src/consciousness/qualia_engine.py"),  # SensoryQualia class
    ("qualia", "src/consciousness/qualia_engine.py"),  # QualaEngine class
    ("narrative", "src/consciousness/production_consciousness.py"),
    ("meaning_maker", "src/consciousness/production_consciousness.py"),
]


class ModuleAnalyzer:
    """Analisa módulos de consciência."""

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.results: Dict[str, Dict] = {}

    def analyze(self) -> None:
        """Analisa todos os módulos."""
        logger.info("=" * 70)
        logger.info("ANÁLISE DE MÓDULOS DE CONSCIÊNCIA")
        logger.info("=" * 70)
        logger.info("")

        for module_name, file_path in MODULES_TO_CHECK:
            full_path = self.workspace_root / file_path
            logger.info(f"📄 {module_name}")
            logger.info(f"   Arquivo: {file_path}")

            if not full_path.exists():
                logger.warning(f"   ❌ ARQUIVO NÃO ENCONTRADO")
                self.results[module_name] = {"status": "not_found"}
                continue

            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Parse AST
                tree = ast.parse(content)

                # Procura por classes relevantes
                classes = self._find_classes(tree, module_name)
                functions = self._find_functions(tree)
                has_pass_stubs = "pass" in content
                has_not_implemented = "NotImplementedError" in content

                logger.info(f"   Status:")
                logger.info(f"     • Classes encontradas: {len(classes)}")
                if classes:
                    for cls_name in classes:
                        logger.info(f"       - {cls_name}")

                logger.info(f"     • Funções/métodos: {len(functions)}")
                if functions:
                    for func_name, has_impl in functions:
                        status = "✅ Implementado" if has_impl else "⚠️  Stub (pass)"
                        logger.info(f"       - {func_name}: {status}")

                if has_pass_stubs:
                    logger.warning(f"   ⚠️  Contém stubs (pass)")

                if has_not_implemented:
                    logger.warning(f"   ⚠️  Contém NotImplementedError")

                self.results[module_name] = {
                    "status": "analyzed",
                    "classes": classes,
                    "functions": [f[0] for f in functions],
                    "has_stubs": has_pass_stubs,
                    "has_not_implemented": has_not_implemented,
                }

            except Exception as e:
                logger.error(f"   ❌ Erro ao analisar: {e}")
                self.results[module_name] = {"status": "error", "error": str(e)}

            logger.info("")

    def _find_classes(self, tree: ast.AST, module_name: str) -> List[str]:
        """Encontra classes no AST."""
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Heurística: procura por classe que contenha parte do nome do módulo
                if module_name.replace("_", "").lower() in node.name.lower():
                    classes.append(node.name)
        return (
            classes or [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)][:3]
        )

    def _find_functions(self, tree: ast.AST) -> List[Tuple[str, bool]]:
        """Encontra funções e verifica se têm implementação."""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Verifica se é apenas "pass"
                has_implementation = not (
                    len(node.body) == 1 and isinstance(node.body[0], ast.Pass)
                )
                functions.append((node.name, has_implementation))
        return functions[:5]  # Limita a 5 principais

    def print_summary(self) -> None:
        """Imprime resumo executivo."""
        logger.info("=" * 70)
        logger.info("RESUMO EXECUTIVO")
        logger.info("=" * 70)

        ready = sum(1 for r in self.results.values() if r.get("status") == "analyzed")
        total = len(self.results)

        logger.info(f"Módulos analisados: {ready}/{total}")
        logger.info("")

        for module_name, info in self.results.items():
            if info.get("status") == "analyzed":
                has_stubs = "⚠️  Stubs" if info.get("has_stubs") else "✅ Sem stubs"
                has_not_impl = "⚠️  NotImplemented" if info.get("has_not_implemented") else "✅"
                logger.info(f"  {module_name:20s}: {has_stubs:20s} {has_not_impl}")


if __name__ == "__main__":
    workspace_root = Path("/home/fahbrain/projects/omnimind")
    analyzer = ModuleAnalyzer(workspace_root)
    analyzer.analyze()
    analyzer.print_summary()
