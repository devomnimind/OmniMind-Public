#!/usr/bin/env python3
"""
Análise e Mapeamento Completo de Documentação - OmniMind

Mapeia toda a documentação, cruza informações, identifica candidatos a arquivar,
e valida consistência entre código e documentação.

Autor: OmniMind Development
Data: 2025-12-05
"""

from __future__ import annotations

import json
import logging
import os
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DocFile:
    """Representa um arquivo de documentação"""

    path: Path
    relative_path: str
    size: int
    last_modified: datetime
    lines: int
    category: str = ""
    status: str = "active"  # active, archive, outdated, duplicate
    issues: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    referenced_by: List[str] = field(default_factory=list)


@dataclass
class ModuleInfo:
    """Informação sobre um módulo src/"""

    name: str
    path: Path
    has_readme: bool
    readme_path: Optional[Path] = None
    python_files: List[Path] = field(default_factory=list)
    has_init: bool = False
    doc_issues: List[str] = field(default_factory=list)


class DocumentationAnalyzer:
    """Analisador de documentação"""

    def __init__(self, root: Path):
        self.root = root
        self.docs: List[DocFile] = []
        self.modules: Dict[str, ModuleInfo] = {}
        self.cross_references: Dict[str, Set[str]] = defaultdict(set)
        self.archive_candidates: List[DocFile] = []
        self.outdated_docs: List[DocFile] = []

    def find_all_markdown(self) -> List[Path]:
        """Encontra todos os arquivos .md"""
        md_files = []
        for path in self.root.rglob("*.md"):
            # Ignorar arquivos em diretórios de build/cache
            if any(
                part in str(path)
                for part in [
                    "__pycache__",
                    ".git",
                    ".venv",
                    "node_modules",
                    ".pytest_cache",
                    "dist",
                    "build",
                ]
            ):
                continue
            md_files.append(path)
        return sorted(md_files)

    def analyze_doc_file(self, path: Path) -> DocFile:
        """Analisa um arquivo de documentação"""
        stat = path.stat()
        content = path.read_text(encoding="utf-8", errors="ignore")
        lines = len(content.splitlines())

        # Determinar categoria
        category = self._determine_category(path)

        # Encontrar referências
        references = self._extract_references(content)

        doc = DocFile(
            path=path,
            relative_path=str(path.relative_to(self.root)),
            size=stat.st_size,
            last_modified=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
            lines=lines,
            category=category,
            references=references,
        )

        # Detectar problemas
        doc.issues = self._detect_issues(doc, content)

        return doc

    def _determine_category(self, path: Path) -> str:
        """Determina categoria do documento"""
        rel_path = str(path.relative_to(self.root))

        if "archive" in rel_path:
            return "archive"
        elif rel_path.startswith("docs/canonical"):
            return "canonical"
        elif rel_path.startswith("docs/guides"):
            return "guide"
        elif rel_path.startswith("docs/api"):
            return "api"
        elif rel_path.startswith("docs/architecture"):
            return "architecture"
        elif rel_path.startswith("docs/research"):
            return "research"
        elif rel_path.startswith("docs/papers"):
            return "papers"
        elif rel_path.startswith("src/"):
            return "module_readme"
        elif rel_path.startswith("scripts/"):
            return "script_readme"
        elif path.name == "README.md":
            return "root_readme"
        elif path.parent == self.root:
            return "root_doc"
        else:
            return "other"

    def _extract_references(self, content: str) -> List[str]:
        """Extrai referências a outros documentos"""
        references = []

        # Links markdown [text](path)
        md_links = re.findall(r"\[.*?\]\(([^)]+)\)", content)
        references.extend(md_links)

        # Referências a docs/
        doc_refs = re.findall(r"docs/[^\s\)]+", content)
        references.extend(doc_refs)

        # Referências a src/
        src_refs = re.findall(r"src/[^\s\)]+", content)
        references.extend(src_refs)

        return list(set(references))

    def _detect_issues(self, doc: DocFile, content: str) -> List[str]:
        """Detecta problemas no documento"""
        issues = []

        # Verificar se é muito antigo
        days_old = (datetime.now(timezone.utc) - doc.last_modified).days
        if days_old > 180:
            issues.append(f"Documento antigo ({days_old} dias)")

        # Verificar se tem TODOs/FIXMEs
        if re.search(r"TODO|FIXME|XXX", content, re.IGNORECASE):
            issues.append("Contém TODO/FIXME")

        # Verificar se está vazio ou muito pequeno
        if doc.lines < 10:
            issues.append("Documento muito curto")

        # Verificar links quebrados (básico)
        if "404" in content or "not found" in content.lower():
            issues.append("Possíveis links quebrados")

        return issues

    def analyze_modules(self) -> None:
        """Analisa módulos em src/ e compara com READMEs"""
        src_dir = self.root / "src"
        if not src_dir.exists():
            return

        for module_dir in sorted(src_dir.iterdir()):
            if not module_dir.is_dir() or module_dir.name.startswith("_"):
                continue

            module_info = ModuleInfo(
                name=module_dir.name,
                path=module_dir,
                has_readme=False,
            )

            # Verificar README
            readme_path = module_dir / "README.md"
            if readme_path.exists():
                module_info.has_readme = True
                module_info.readme_path = readme_path

            # Contar arquivos Python
            module_info.python_files = list(module_dir.rglob("*.py"))
            module_info.has_init = (module_dir / "__init__.py").exists()

            # Validar README vs código
            if module_info.has_readme:
                module_info.doc_issues = self._validate_module_readme(
                    module_info, readme_path
                )

            self.modules[module_dir.name] = module_info

    def _validate_module_readme(self, module_info: ModuleInfo, readme_path: Path) -> List[str]:
        """Valida README do módulo contra código real"""
        issues = []
        readme_content = readme_path.read_text(encoding="utf-8", errors="ignore")

        # Verificar se menciona classes/funções que existem
        for py_file in module_info.python_files:
            if py_file.name == "__init__.py":
                continue

            try:
                py_content = py_file.read_text(encoding="utf-8", errors="ignore")
                # Extrair classes e funções principais
                classes = re.findall(r"^class\s+(\w+)", py_content, re.MULTILINE)
                functions = re.findall(r"^def\s+(\w+)", py_content, re.MULTILINE)

                # Verificar se são mencionadas no README
                for cls in classes:
                    if cls not in readme_content:
                        issues.append(f"Classe {cls} não documentada em README")

            except Exception as e:
                logger.warning(f"Erro ao ler {py_file}: {e}")

        return issues

    def build_cross_references(self) -> None:
        """Constrói mapa de referências cruzadas"""
        for doc in self.docs:
            for ref in doc.references:
                # Normalizar referência
                normalized_ref = self._normalize_reference(ref, doc.path)
                if normalized_ref:
                    self.cross_references[normalized_ref].add(str(doc.relative_path))

    def _normalize_reference(self, ref: str, from_path: Path) -> Optional[str]:
        """Normaliza referência para path relativo"""
        # Remover fragmentos e queries
        ref = ref.split("#")[0].split("?")[0]

        # Resolver path relativo
        if ref.startswith("/"):
            ref = ref[1:]
        elif not ref.startswith("http"):
            # Path relativo
            ref_path = (from_path.parent / ref).resolve()
            try:
                return str(ref_path.relative_to(self.root))
            except ValueError:
                return None

        return ref if ref.startswith("http") else None

    def identify_archive_candidates(self) -> None:
        """Identifica candidatos a arquivar"""
        for doc in self.docs:
            # Já está em archive
            if doc.category == "archive":
                continue

            # Critérios para arquivar
            archive_reasons = []

            # Muito antigo e sem referências
            days_old = (datetime.now(timezone.utc) - doc.last_modified).days
            if days_old > 365 and len(doc.referenced_by) == 0:
                archive_reasons.append(f"Antigo ({days_old} dias) e não referenciado")

            # Duplicado
            if doc.relative_path.count("README.md") > 1:
                archive_reasons.append("Possível duplicado")

            # Na raiz mas deveria estar em docs/
            if doc.category == "root_doc" and doc.path.name != "README.md":
                archive_reasons.append("Deve estar em docs/")

            if archive_reasons:
                doc.status = "archive"
                doc.issues.extend(archive_reasons)
                self.archive_candidates.append(doc)

    def generate_report(self) -> Dict[str, Any]:
        """Gera relatório completo"""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total_docs": len(self.docs),
                "by_category": self._count_by_category(),
                "archive_candidates": len(self.archive_candidates),
                "outdated_docs": len(self.outdated_docs),
                "modules_with_readme": sum(1 for m in self.modules.values() if m.has_readme),
                "modules_without_readme": sum(
                    1 for m in self.modules.values() if not m.has_readme
                ),
            },
            "docs": [
                {
                    "path": doc.relative_path,
                    "category": doc.category,
                    "status": doc.status,
                    "size": doc.size,
                    "lines": doc.lines,
                    "last_modified": doc.last_modified.isoformat(),
                    "issues": doc.issues,
                    "references_count": len(doc.references),
                    "referenced_by_count": len(doc.referenced_by),
                }
                for doc in sorted(self.docs, key=lambda d: d.relative_path)
            ],
            "modules": {
                name: {
                    "has_readme": info.has_readme,
                    "readme_path": str(info.readme_path) if info.readme_path else None,
                    "python_files_count": len(info.python_files),
                    "has_init": info.has_init,
                    "doc_issues": info.doc_issues,
                }
                for name, info in sorted(self.modules.items())
            },
            "archive_candidates": [
                {
                    "path": doc.relative_path,
                    "category": doc.category,
                    "reasons": doc.issues,
                }
                for doc in self.archive_candidates
            ],
            "cross_references": {
                ref: list(refs) for ref, refs in sorted(self.cross_references.items())
            },
        }

    def _count_by_category(self) -> Dict[str, int]:
        """Conta documentos por categoria"""
        counts = defaultdict(int)
        for doc in self.docs:
            counts[doc.category] += 1
        return dict(counts)

    def run_analysis(self) -> Dict[str, Any]:
        """Executa análise completa"""
        logger.info("🔍 Mapeando arquivos de documentação...")
        md_files = self.find_all_markdown()
        logger.info(f"   Encontrados {len(md_files)} arquivos .md")

        logger.info("📄 Analisando arquivos...")
        for path in md_files:
            try:
                doc = self.analyze_doc_file(path)
                self.docs.append(doc)
            except Exception as e:
                logger.warning(f"   Erro ao analisar {path}: {e}")

        logger.info("🔧 Analisando módulos src/...")
        self.analyze_modules()

        logger.info("🔗 Construindo referências cruzadas...")
        self.build_cross_references()

        logger.info("📦 Identificando candidatos a arquivar...")
        self.identify_archive_candidates()

        logger.info("📊 Gerando relatório...")
        return self.generate_report()


def main():
    """Função principal"""
    root = Path(__file__).parent.parent
    analyzer = DocumentationAnalyzer(root)

    report = analyzer.run_analysis()

    # Salvar relatório
    output_path = root / "data" / "test_reports" / "documentation_analysis.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))

    logger.info(f"✅ Relatório salvo em: {output_path}")
    logger.info(f"   Total de documentos: {report['summary']['total_docs']}")
    logger.info(f"   Candidatos a arquivar: {report['summary']['archive_candidates']}")
    logger.info(
        f"   Módulos sem README: {report['summary']['modules_without_readme']}"
    )

    return report


if __name__ == "__main__":
    main()

