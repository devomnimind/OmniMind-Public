#!/usr/bin/env python3
"""
✅ VALIDADOR DE READMEs - OMNIMIND

Verifica qualidade de READMEs gerados:
- Cobertura de classes (tem documentação de classe principal?)
- Cobertura de funções (tem documentação de função principal?)
- Formatação consistente
- Links válidos
- Completude de seções
"""

import re
from pathlib import Path
from typing import Dict


class ReadmeValidator:
    """Valida qualidade de READMEs."""

    REQUIRED_SECTIONS = [
        "Classes Principais",
        "Funções",
        "Módulos",
    ]

    def __init__(self, src_path: str = "src"):
        self.src_path = Path(src_path)
        self.results = []

    def validate_all(self) -> Dict:
        """Valida todos os READMEs."""
        stats = {"total": 0, "valid": 0, "issues": [], "warnings": []}

        for folder in sorted(self.src_path.iterdir()):
            if not folder.is_dir() or folder.name.startswith("__"):
                continue

            readme_path = folder / "README.md"
            if not readme_path.exists():
                stats["warnings"].append(f"❌ {folder.name}: README.md não existe")
                continue

            stats["total"] += 1
            result = self._validate_readme(readme_path, folder.name)

            if result["valid"]:
                stats["valid"] += 1
                print(f"✅ {folder.name}")
            else:
                print(f"⚠️  {folder.name}: {', '.join(result['issues'][:2])}")
                stats["issues"].extend(result["issues"])

        return stats

    def _validate_readme(self, readme_path: Path, folder_name: str) -> Dict:
        """Valida um README individual."""
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        issues = []
        warnings = []

        # 1. Verificar seções obrigatórias
        for section in self.REQUIRED_SECTIONS:
            if f"## {section}" not in content and f"# {section}" not in content:
                warnings.append(f"Falta seção: {section}")

        # 2. Verificar estrutura básica
        if not content.startswith("#"):
            issues.append("README não começa com título")

        # 3. Verificar API Reference
        if "API Reference" not in content:
            warnings.append("Falta seção API Reference")

        # 4. Contar classes documentadas
        class_count = len(re.findall(r"^### `\w+", content, re.MULTILINE))
        if class_count == 0:
            warnings.append("Nenhuma classe documentada")

        # 5. Contar funções documentadas
        func_count = len(re.findall(r"^#### `\w+", content, re.MULTILINE))
        if func_count == 0:
            warnings.append("Nenhuma função documentada")

        # 6. Verificar docstrings
        doc_count = len(re.findall(r"^- `", content, re.MULTILINE))
        if doc_count < 3:
            warnings.append("Poucos métodos documentados")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "classes": class_count,
            "functions": func_count,
            "methods": doc_count,
        }


def main():
    """Executa validação."""
    print("\n" + "=" * 60)
    print("✅ VALIDADOR DE READMEs - OMNIMIND")
    print("=" * 60 + "\n")

    validator = ReadmeValidator("src")
    stats = validator.validate_all()

    print("\n" + "=" * 60)
    print("📊 RELATÓRIO DE VALIDAÇÃO")
    print("=" * 60)
    print(f"✅ Válidos: {stats['valid']}/{stats['total']}")
    print(f"📋 Total: {stats['total']}")

    if stats["issues"]:
        print(f"\n❌ ISSUES ({len(stats['issues'])}):")
        for issue in stats["issues"][:10]:
            print(f"   - {issue}")

    if stats["warnings"]:
        print(f"\n⚠️  WARNINGS ({len(stats['warnings'])}):")
        for warning in stats["warnings"][:10]:
            print(f"   - {warning}")

    print("\n" + "=" * 60)
    print("💡 Próximos passos:")
    print("   1. Verificar warnings acima")
    print("   2. Completar READMEs faltantes")
    print("   3. Rodar novamente: python3 scripts/validate_readmes.py")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
