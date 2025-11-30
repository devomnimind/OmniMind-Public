#!/bin/bash
# 🧹 OmniMind - Prepare Public Repository Script
# 
# Este script prepara o repositório OmniMind para publicação pública
# removendo arquivos temporários, logs e aplicando correções de qualidade.
#
# Uso: ./prepare_public_repo.sh [--dry-run]
#
# --dry-run: Apenas mostra o que seria feito sem executar

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

DRY_RUN=false

if [ "$1" == "--dry-run" ]; then
    DRY_RUN=true
    echo -e "${YELLOW}🔍 Modo DRY-RUN: Nenhuma modificação será feita${NC}"
    echo ""
fi

# Função para executar comando ou simular
run_cmd() {
    local cmd="$1"
    local desc="$2"
    
    echo -e "${BLUE}▶ ${desc}${NC}"
    
    if [ "$DRY_RUN" = true ]; then
        echo "   [DRY-RUN] $cmd"
    else
        eval "$cmd"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}   ✓ Concluído${NC}"
        else
            echo -e "${RED}   ✗ Erro (código: $?)${NC}"
        fi
    fi
    echo ""
}

echo "🧠 =============================================="
echo "   OmniMind - Preparação de Repositório Público"
echo "=============================================="
echo ""

# Verificar se estamos no diretório correto
if [ ! -f "README.md" ] || [ ! -d "src" ]; then
    echo -e "${RED}❌ Erro: Execute este script na raiz do repositório OmniMind${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Diretório verificado: $(pwd)${NC}"
echo ""

# ============================================
# FASE 1: LIMPEZA DE ARQUIVOS TEMPORÁRIOS
# ============================================

echo -e "${YELLOW}📁 FASE 1: Limpeza de Arquivos Temporários${NC}"
echo "=========================================="
echo ""

# 1.1 Remover logs de execução
run_cmd "find data/long_term_logs -name '*.out' -type f -delete 2>/dev/null || true" \
        "Removendo logs de execução (*.out)"

run_cmd "find logs -name '*.log' -type f -delete 2>/dev/null || true" \
        "Removendo logs gerais (*.log)"

# 1.2 Remover cache Python
run_cmd "find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true" \
        "Removendo __pycache__"

run_cmd "find . -name '*.pyc' -delete 2>/dev/null || true" \
        "Removendo arquivos *.pyc"

run_cmd "find . -name '*.pyo' -delete 2>/dev/null || true" \
        "Removendo arquivos *.pyo"

# 1.3 Remover arquivos temporários gerais
run_cmd "find . -name '*.tmp' -delete 2>/dev/null || true" \
        "Removendo arquivos *.tmp"

run_cmd "find . -name '*~' -delete 2>/dev/null || true" \
        "Removendo arquivos de backup (*~)"

run_cmd "find . -name '.DS_Store' -delete 2>/dev/null || true" \
        "Removendo .DS_Store (macOS)"

# 1.4 Limpar pytest cache
run_cmd "rm -rf .pytest_cache 2>/dev/null || true" \
        "Removendo .pytest_cache"

run_cmd "rm -rf htmlcov 2>/dev/null || true" \
        "Removendo htmlcov (coverage reports locais)"

# ============================================
# FASE 2: VERIFICAÇÃO DE SEGURANÇA
# ============================================

echo -e "${YELLOW}🔐 FASE 2: Verificação de Segurança${NC}"
echo "=========================================="
echo ""

# 2.1 Verificar credenciais hardcoded
echo -e "${BLUE}▶ Verificando credenciais hardcoded...${NC}"
SECRETS=$(grep -r "API_KEY\|SECRET\|TOKEN\|PASSWORD" --include="*.py" src/ 2>/dev/null | grep -v "os.getenv\|os.environ\|# " | grep -v ".example" | grep -v ".template" || true)

if [ -n "$SECRETS" ]; then
    echo -e "${RED}   ❌ ERRO: Potenciais credenciais encontradas!${NC}"
    echo "$SECRETS"
    echo ""
    echo -e "${RED}   Revise manualmente antes de continuar.${NC}"
    if [ "$DRY_RUN" = false ]; then
        exit 1
    fi
else
    echo -e "${GREEN}   ✓ Nenhuma credencial hardcoded encontrada${NC}"
fi
echo ""

# 2.2 Verificar .env não commitado
echo -e "${BLUE}▶ Verificando arquivos .env...${NC}"
if git ls-files | grep -E "^\.env$" > /dev/null 2>&1; then
    echo -e "${RED}   ❌ ERRO: Arquivo .env está commitado!${NC}"
    if [ "$DRY_RUN" = false ]; then
        exit 1
    fi
else
    echo -e "${GREEN}   ✓ Arquivo .env não commitado${NC}"
fi
echo ""

# 2.3 Verificar arquivos grandes
echo -e "${BLUE}▶ Verificando arquivos grandes (>5MB)...${NC}"
LARGE_FILES=$(find . -type f -size +5M ! -path "./.git/*" ! -path "./.venv/*" 2>/dev/null || true)

if [ -n "$LARGE_FILES" ]; then
    echo -e "${YELLOW}   ⚠️  Arquivos grandes encontrados:${NC}"
    echo "$LARGE_FILES"
    echo ""
    echo -e "${YELLOW}   Considere adicionar ao .gitignore ou usar Git LFS${NC}"
else
    echo -e "${GREEN}   ✓ Nenhum arquivo grande encontrado${NC}"
fi
echo ""

# ============================================
# FASE 3: FORMATAÇÃO E LINTING
# ============================================

echo -e "${YELLOW}✨ FASE 3: Formatação e Linting${NC}"
echo "=========================================="
echo ""

# 3.1 Black (formatação)
if command -v black &> /dev/null; then
    if [ "$DRY_RUN" = true ]; then
        run_cmd "black --check src/ tests/ scripts/ 2>&1 || true" \
                "Verificando formatação com Black"
    else
        run_cmd "black src/ tests/ scripts/ 2>&1 || true" \
                "Formatando código com Black"
    fi
else
    echo -e "${YELLOW}⚠️  Black não instalado. Pulando formatação.${NC}"
    echo "   Instale com: pip install black"
    echo ""
fi

# 3.2 Flake8 (linting)
if command -v flake8 &> /dev/null; then
    run_cmd "flake8 src/ tests/ --max-line-length=100 --count --statistics --exit-zero 2>&1 | tail -20" \
            "Verificando código com Flake8"
else
    echo -e "${YELLOW}⚠️  Flake8 não instalado. Pulando linting.${NC}"
    echo "   Instale com: pip install flake8"
    echo ""
fi

# ============================================
# FASE 4: TESTES
# ============================================

echo -e "${YELLOW}🧪 FASE 4: Executando Testes${NC}"
echo "=========================================="
echo ""

if command -v pytest &> /dev/null; then
    # Teste rápido (apenas smoke tests)
    run_cmd "pytest tests/ -x --maxfail=5 -q --tb=short 2>&1 | tail -30 || true" \
            "Executando smoke tests (rápido)"
else
    echo -e "${YELLOW}⚠️  Pytest não instalado. Pulando testes.${NC}"
    echo "   Instale com: pip install pytest pytest-cov"
    echo ""
fi

# ============================================
# FASE 5: ATUALIZAR .gitignore
# ============================================

echo -e "${YELLOW}📝 FASE 5: Atualizando .gitignore${NC}"
echo "=========================================="
echo ""

if [ "$DRY_RUN" = false ]; then
    # Adicionar entradas ao .gitignore se não existirem
    cat >> .gitignore << 'GITIGNORE_EOF'

# === Adicionado por prepare_public_repo.sh ===

# Execution logs
data/long_term_logs/*.out
logs/*.log

# Build artifacts (raiz)
coverage.json
gpu_llm_diagnosis.json
orchestrator_audit.json
current_packages.txt
feedback_report.txt
log_analysis_test.json

# Test screenshots
test_sync_screenshot.png
test_*.png

# Coverage reports
htmlcov/
.coverage
coverage.xml

# MyPy cache
.mypy_cache/

# Pytest cache
.pytest_cache/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*~
GITIGNORE_EOF

    echo -e "${GREEN}✓ .gitignore atualizado${NC}"
else
    echo -e "${BLUE}[DRY-RUN] .gitignore seria atualizado${NC}"
fi
echo ""

# ============================================
# FASE 6: RELATÓRIO FINAL
# ============================================

echo -e "${YELLOW}📊 FASE 6: Relatório Final${NC}"
echo "=========================================="
echo ""

# Estatísticas
echo -e "${BLUE}Estatísticas do Repositório:${NC}"
echo ""
echo "  Arquivos Python:  $(find src -name '*.py' | wc -l)"
echo "  Arquivos Markdown: $(find . -name '*.md' | wc -l)"
echo "  Testes:           $(find tests -name 'test_*.py' | wc -l)"
echo "  Tamanho total:    $(du -sh . 2>/dev/null | cut -f1)"
echo ""

# Verificações finais
echo -e "${BLUE}Verificações Finais:${NC}"
echo ""

FINAL_CHECKS=0

# Check 1: README exists
if [ -f "README.md" ]; then
    echo -e "${GREEN}  ✓ README.md presente${NC}"
else
    echo -e "${RED}  ✗ README.md ausente${NC}"
    ((FINAL_CHECKS++))
fi

# Check 2: LICENSE exists
if [ -f "LICENSE" ]; then
    echo -e "${GREEN}  ✓ LICENSE presente${NC}"
else
    echo -e "${RED}  ✗ LICENSE ausente${NC}"
    ((FINAL_CHECKS++))
fi

# Check 3: CONTRIBUTING exists
if [ -f "CONTRIBUTING.md" ]; then
    echo -e "${GREEN}  ✓ CONTRIBUTING.md presente${NC}"
else
    echo -e "${RED}  ✗ CONTRIBUTING.md ausente${NC}"
    ((FINAL_CHECKS++))
fi

# Check 4: .gitignore exists
if [ -f ".gitignore" ]; then
    echo -e "${GREEN}  ✓ .gitignore presente${NC}"
else
    echo -e "${RED}  ✗ .gitignore ausente${NC}"
    ((FINAL_CHECKS++))
fi

# Check 5: No .env committed
if ! git ls-files | grep -E "^\.env$" > /dev/null 2>&1; then
    echo -e "${GREEN}  ✓ .env não commitado${NC}"
else
    echo -e "${RED}  ✗ .env está commitado!${NC}"
    ((FINAL_CHECKS++))
fi

echo ""

# ============================================
# CONCLUSÃO
# ============================================

echo "=============================================="

if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}🔍 Modo DRY-RUN: Nenhuma modificação foi feita${NC}"
    echo ""
    echo "Para aplicar as mudanças, execute:"
    echo "  ./prepare_public_repo.sh"
else
    if [ $FINAL_CHECKS -eq 0 ]; then
        echo -e "${GREEN}✅ Repositório preparado com sucesso!${NC}"
        echo ""
        echo "Próximos passos:"
        echo "  1. Revise as mudanças: git status"
        echo "  2. Commit: git add . && git commit -m 'chore: prepare repository for public release'"
        echo "  3. Execute testes completos: pytest tests/ -v --cov=src"
        echo "  4. Revise AUDIT_REPORT.md e PUBLICATION_CHECKLIST.md"
        echo "  5. Quando pronto: git push origin main"
    else
        echo -e "${RED}⚠️  Repositório preparado com $FINAL_CHECKS avisos${NC}"
        echo ""
        echo "Revise os issues acima antes de publicar."
    fi
fi

echo "=============================================="
echo ""

exit 0
