#!/usr/bin/env python3
"""
Script de Varredura: Pendências, Testes e Documentos

Faz varredura completa de:
1. Testes que precisam atualização após implementações recentes
2. Pendências em documentos (resolvidas vs. ativas)
3. Relatórios e análises (resolvidos vs. atuais)
4. Organiza arquivamento de documentos resolvidos

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-07
"""

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Configuração
PROJECT_ROOT = Path(__file__).parent.parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
ARCHIVE_DIR = PROJECT_ROOT / "archive" / "docs"
TESTS_DIR = PROJECT_ROOT / "tests"


@dataclass
class DocumentStatus:
    """Status de um documento."""

    path: Path
    title: str
    status: str  # "resolvido", "ativo", "pendente"
    resolved_date: str = ""
    category: str = ""
    notes: str = ""


@dataclass
class TestStatus:
    """Status de um teste."""

    path: Path
    name: str
    needs_update: bool
    reason: str = ""
    related_implementation: str = ""


def analyze_document_status(file_path: Path) -> DocumentStatus:
    """Analisa status de um documento."""
    try:
        content = file_path.read_text(encoding="utf-8")

        # Detectar status por padrões
        is_resolved = (
            "✅ 100% COMPLETA" in content
            or "✅ COMPLETA" in content
            or "✅ RESOLVIDO" in content
            or "Status: ✅" in content
            or "Status: ✅ COMPLETA" in content
            or "Status: ✅ RESOLVIDO" in content
            or "**Status**: ✅" in content
            or "**Status**: ✅ COMPLETA" in content
            or re.search(r"✅.*100%", content) is not None
        )

        is_pending = (
            "⏳ PENDENTE" in content
            or "Status: ⏳" in content
            or "**Status**: ⏳" in content
            or "PENDENTE" in content.upper()
        )

        # Extrair título
        title_match = re.search(r"^#+\s+(.+)$", content, re.MULTILINE)
        title = title_match.group(1) if title_match else file_path.stem

        # Categorizar
        category = "outro"
        if "RELATORIO" in file_path.name.upper():
            category = "relatorio"
        elif "ANALISE" in file_path.name.upper():
            category = "analise"
        elif "VERIFICACAO" in file_path.name.upper():
            category = "verificacao"
        elif "CORRECAO" in file_path.name.upper():
            category = "correcao"
        elif "PENDENCIAS" in file_path.name.upper():
            category = "pendencias"
        elif "STATUS" in file_path.name.upper():
            category = "status"

        # Determinar status
        if is_resolved:
            status = "resolvido"
        elif is_pending:
            status = "pendente"
        else:
            status = "ativo"

        # Extrair data de resolução se disponível
        resolved_date = ""
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", content)
        if date_match:
            resolved_date = date_match.group(1)

        return DocumentStatus(
            path=file_path,
            title=title,
            status=status,
            resolved_date=resolved_date,
            category=category,
            notes="",
        )
    except Exception as e:
        return DocumentStatus(
            path=file_path, title=file_path.stem, status="erro", notes=f"Erro ao analisar: {e}"
        )


def analyze_test_status(file_path: Path) -> TestStatus:
    """Analisa se um teste precisa atualização."""
    try:
        content = file_path.read_text(encoding="utf-8")

        needs_update = False
        reason = ""
        related_implementation = ""

        # Verificar se menciona componentes que foram implementados recentemente
        if "HybridTopologicalEngine" in content or "hybrid_topological_engine" in content:
            # Já atualizado
            needs_update = False
        elif "topological" in content.lower() or "phi" in content.lower():
            # Pode precisar atualização para usar HybridTopologicalEngine
            needs_update = True
            reason = "Menciona topologia/phi - pode precisar integrar HybridTopologicalEngine"
            related_implementation = "HybridTopologicalEngine"

        # Verificar se menciona SharedWorkspace e pode precisar integrar novas métricas
        if "SharedWorkspace" in content and "compute_hybrid_topological_metrics" not in content:
            needs_update = True
            reason = "Usa SharedWorkspace mas não testa compute_hybrid_topological_metrics"
            related_implementation = "SharedWorkspace.compute_hybrid_topological_metrics"

        return TestStatus(
            path=file_path,
            name=file_path.stem,
            needs_update=needs_update,
            reason=reason,
            related_implementation=related_implementation,
        )
    except Exception as e:
        return TestStatus(
            path=file_path, name=file_path.stem, needs_update=False, reason=f"Erro ao analisar: {e}"
        )


def scan_documents() -> Tuple[List[DocumentStatus], Dict[str, int]]:
    """Varre todos os documentos em docs/."""
    documents = []
    stats = {"resolvido": 0, "ativo": 0, "pendente": 0, "erro": 0}

    # Escanear docs/
    for md_file in DOCS_DIR.rglob("*.md"):
        # Ignorar arquivos em subdiretórios específicos
        if "archive" in str(md_file) or "canonical" in str(md_file):
            continue

        status = analyze_document_status(md_file)
        documents.append(status)
        stats[status.status] = stats.get(status.status, 0) + 1

    return documents, stats


def scan_tests() -> Tuple[List[TestStatus], Dict[str, int]]:
    """Varre todos os testes."""
    tests = []
    stats = {"needs_update": 0, "ok": 0}

    # Escanear tests/
    for test_file in TESTS_DIR.rglob("test_*.py"):
        status = analyze_test_status(test_file)
        tests.append(status)
        if status.needs_update:
            stats["needs_update"] += 1
        else:
            stats["ok"] += 1

    return tests, stats


def should_archive(document: DocumentStatus) -> bool:
    """Determina se documento deve ser arquivado."""
    # Arquivar se:
    # 1. Status é "resolvido"
    # 2. Não é documento canônico de pendências
    # 3. Não é README principal

    if document.status != "resolvido":
        return False

    if "PENDENCIAS" in document.path.name.upper():
        return False  # Não arquivar documentos de pendências

    if document.path.name == "README.md":
        return False  # Não arquivar READMEs principais

    if "canonical" in str(document.path):
        return False  # Não arquivar documentos canônicos

    return True


def organize_archive(documents: List[DocumentStatus]) -> List[Path]:
    """Organiza arquivamento de documentos resolvidos."""
    to_archive = []

    for doc in documents:
        if should_archive(doc):
            to_archive.append(doc.path)

    return to_archive


def generate_report(
    documents: List[DocumentStatus], tests: List[TestStatus], archive_list: List[Path]
) -> str:
    """Gera relatório de varredura."""
    report = []
    report.append("# Varredura Completa: Pendências, Testes e Documentos")
    report.append(f"**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("")

    # Resumo
    report.append("## 📊 RESUMO EXECUTIVO")
    report.append("")

    doc_stats = {}
    for doc in documents:
        doc_stats[doc.status] = doc_stats.get(doc.status, 0) + 1

    test_stats = {}
    for test in tests:
        if test.needs_update:
            test_stats["precisa_atualizacao"] = test_stats.get("precisa_atualizacao", 0) + 1
        else:
            test_stats["ok"] = test_stats.get("ok", 0) + 1

    report.append(f"- **Documentos Resolvidos:** {doc_stats.get('resolvido', 0)}")
    report.append(f"- **Documentos Ativos:** {doc_stats.get('ativo', 0)}")
    report.append(f"- **Documentos Pendentes:** {doc_stats.get('pendente', 0)}")
    report.append(f"- **Testes OK:** {test_stats.get('ok', 0)}")
    report.append(
        f"- **Testes que Precisam Atualização:** {test_stats.get('precisa_atualizacao', 0)}"
    )
    report.append(f"- **Documentos para Arquivar:** {len(archive_list)}")
    report.append("")

    # Documentos resolvidos para arquivar
    report.append("## 📦 DOCUMENTOS PARA ARQUIVAR")
    report.append("")
    if archive_list:
        for doc_path in archive_list:
            rel_path = doc_path.relative_to(PROJECT_ROOT)
            report.append(f"- `{rel_path}`")
    else:
        report.append("Nenhum documento para arquivar.")
    report.append("")

    # Testes que precisam atualização
    report.append("## 🧪 TESTES QUE PRECISAM ATUALIZAÇÃO")
    report.append("")
    tests_needing_update = [t for t in tests if t.needs_update]
    if tests_needing_update:
        for test in tests_needing_update:
            rel_path = test.path.relative_to(PROJECT_ROOT)
            report.append(f"### `{rel_path}`")
            report.append(f"- **Razão:** {test.reason}")
            report.append(f"- **Implementação Relacionada:** {test.related_implementation}")
            report.append("")
    else:
        report.append("Nenhum teste precisa atualização.")
    report.append("")

    # Pendências ativas
    report.append("## ⏳ PENDÊNCIAS ATIVAS")
    report.append("")
    pending_docs = [
        d for d in documents if d.status == "pendente" and "PENDENCIAS" in d.path.name.upper()
    ]
    if pending_docs:
        for doc in pending_docs:
            rel_path = doc.path.relative_to(PROJECT_ROOT)
            report.append(f"- `{rel_path}` - {doc.title}")
    else:
        report.append("Nenhuma pendência ativa identificada.")
    report.append("")

    return "\n".join(report)


def main():
    """Função principal."""
    print("🔍 Iniciando varredura completa...")

    # Varredura de documentos
    print("📄 Varreando documentos...")
    documents, doc_stats = scan_documents()
    print(f"   Encontrados: {len(documents)} documentos")
    print(f"   Resolvidos: {doc_stats.get('resolvido', 0)}")
    print(f"   Ativos: {doc_stats.get('ativo', 0)}")
    print(f"   Pendentes: {doc_stats.get('pendente', 0)}")

    # Varredura de testes
    print("\n🧪 Varreando testes...")
    tests, test_stats = scan_tests()
    print(f"   Encontrados: {len(tests)} testes")
    print(f"   OK: {test_stats.get('ok', 0)}")
    print(f"   Precisam atualização: {test_stats.get('needs_update', 0)}")

    # Organizar arquivamento
    print("\n📦 Organizando arquivamento...")
    archive_list = organize_archive(documents)
    print(f"   Documentos para arquivar: {len(archive_list)}")

    # Gerar relatório
    print("\n📝 Gerando relatório...")
    report = generate_report(documents, tests, archive_list)

    # Salvar relatório
    report_path = DOCS_DIR / "VARREDURA_COMPLETA_20251207.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"   Relatório salvo em: {report_path}")

    # Salvar JSON detalhado
    json_path = DOCS_DIR / "VARREDURA_COMPLETA_20251207.json"
    json_data = {
        "timestamp": datetime.now().isoformat(),
        "documents": [
            {
                "path": str(d.path.relative_to(PROJECT_ROOT)),
                "title": d.title,
                "status": d.status,
                "resolved_date": d.resolved_date,
                "category": d.category,
                "notes": d.notes,
            }
            for d in documents
        ],
        "tests": [
            {
                "path": str(t.path.relative_to(PROJECT_ROOT)),
                "name": t.name,
                "needs_update": t.needs_update,
                "reason": t.reason,
                "related_implementation": t.related_implementation,
            }
            for t in tests
        ],
        "archive_list": [str(p.relative_to(PROJECT_ROOT)) for p in archive_list],
        "stats": {"documents": doc_stats, "tests": test_stats},
    }
    json_path.write_text(json.dumps(json_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"   JSON detalhado salvo em: {json_path}")

    print("\n✅ Varredura completa!")


if __name__ == "__main__":
    main()
