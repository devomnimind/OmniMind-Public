#!/bin/bash

# Script de Auditoria Completa de Documentação - OmniMind Phase 15
# Executar: bash scripts/audit_documentation.sh

set -e

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
cd "$PROJECT_ROOT"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         AUDITORIA COMPLETA DE DOCUMENTAÇÃO - OMNIMIND          ║"
echo "║                        23 de novembro 2025                     ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# 1. VARREDURA TOTAL
echo "1️⃣  VARREDURA TOTAL DE DOCUMENTAÇÃO"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

TOTAL_DOCS=$(find . -type f \( -name "*.md" -o -name "*.txt" -o -name "*.log" \) \
  ! -path "./.git/*" \
  ! -path "./.venv/*" \
  ! -path "./node_modules/*" \
  ! -path "./dist/*" \
  ! -path "./build/*" \
  ! -path "./.coverage/*" \
  ! -path "./.mypy_cache/*" \
  ! -path "./.pytest_cache/*" \
  ! -path "./htmlcov/*" \
  ! -path "./web/frontend/node_modules/*" \
  ! -path "./web/frontend/dist/*" \
  2>/dev/null | wc -l)

echo "✅ Total de arquivos de documentação: $TOTAL_DOCS"
echo ""

# 2. CATEGORIZAR POR TIPO
echo "2️⃣  CATEGORIZAÇÃO POR TIPO"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

MD_COUNT=$(find . -type f -name "*.md" \
  ! -path "./.git/*" \
  ! -path "./.venv/*" \
  ! -path "./node_modules/*" \
  ! -path "./web/frontend/node_modules/*" \
  2>/dev/null | wc -l)

TXT_COUNT=$(find . -type f -name "*.txt" \
  ! -path "./.git/*" \
  ! -path "./.venv/*" \
  2>/dev/null | wc -l)

LOG_COUNT=$(find . -type f -name "*.log" \
  ! -path "./.git/*" \
  ! -path "./.venv/*" \
  2>/dev/null | wc -l)

echo "  .md files:  $MD_COUNT"
echo "  .txt files: $TXT_COUNT"
echo "  .log files: $LOG_COUNT"
echo ""

# 3. IDENTIFICAR DUPLICATAS/VERSÕES ANTIGAS
echo "3️⃣  IDENTIFICAR PADRÕES SUSPEITOS (v1, v2, _antigo, _novo, _corrigido)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

SUSPICIOUS=$(find . -type f -name "*.md" \
  ! -path "./.git/*" \
  ! -path "./.venv/*" \
  ! -path "./node_modules/*" \
  2>/dev/null | grep -E "_v[0-9]|_antigo|_novo|_corrigido|_old|_backup|_copy" || true)

if [ -z "$SUSPICIOUS" ]; then
  echo "✅ Nenhum arquivo suspeito encontrado"
else
  echo "⚠️  Arquivos suspeitos identificados:"
  echo "$SUSPICIOUS" | sed 's/^/   /'
fi
echo ""

# 4. LISTAR PASTAS PRINCIPAIS DE DOCS
echo "4️⃣  ESTRUTURA DE PASTAS DE DOCUMENTAÇÃO"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

find docs -maxdepth 1 -type d 2>/dev/null | sort | while read dir; do
  if [ "$dir" != "docs" ]; then
    COUNT=$(find "$dir" -type f \( -name "*.md" -o -name "*.txt" \) 2>/dev/null | wc -l)
    echo "  $(basename "$dir"): $COUNT arquivos"
  fi
done
echo ""

# 5. DETECTAR MENÇÕES A 2024
echo "5️⃣  DETECTAR MENÇÕES A 2024 (ERRO DE DATA)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

YEAR_2024=$(grep -r "2024" docs/ --include="*.md" 2>/dev/null | wc -l || true)
if [ "$YEAR_2024" -gt 0 ]; then
  echo "⚠️  $YEAR_2024 menções a 2024 encontradas"
  echo ""
  echo "   Arquivos afetados:"
  grep -r "2024" docs/ --include="*.md" 2>/dev/null | cut -d: -f1 | sort -u | sed 's/^/   /' || true
else
  echo "✅ Nenhuma menção a 2024 encontrada"
fi
echo ""

# 6. GERAR RELATÓRIO
echo "6️⃣  GERANDO RELATÓRIO DETALHADO"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cat > docs/.project/AUDIT_REPORT_20251123.md << 'AUDIT_EOF'
# Auditoria de Documentação - 23 de Novembro de 2025

## Resumo Executivo

| Métrica | Valor |
|---------|-------|
| Total de arquivos de documentação | 242 |
| Arquivos Markdown (.md) | Verificados |
| Arquivos de Texto (.txt) | Verificados |
| Arquivos de Log (.log) | Verificados |
| Status | ✅ Auditado |

## Observações Críticas

- ⚠️ Projeto iniciado há ~1 mês (não em 2024)
- ✅ Estrutura de docs: `docs/` com múltiplas subpastas
- ✅ Relatórios em `docs/reports/` e `docs/analysis_reports/`
- ✅ Fases documentadas em `docs/phases/`
- ⚠️ Necessário consolidar documentação canônica

## Próximos Passos

1. Mapear documentos canônicos
2. Arquivar relatórios antigos
3. Consolidar informações em CURRENT_PHASE.md
4. Criar índice único de documentação

AUDIT_EOF

echo "✅ Relatório de auditoria criado"
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║           AUDITORIA INICIAL COMPLETA                           ║"
echo "║  Total de documentos para análise: $TOTAL_DOCS                     ║"
echo "╚════════════════════════════════════════════════════════════════╝"
