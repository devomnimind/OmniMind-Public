#!/bin/bash
# Script para executar testes por categoria: MOCK, SEMI-REAL, REAL

set -e

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
cd "$PROJECT_ROOT"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para printar com cor
print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Criar diretório de reports
mkdir -p data/test_reports

# Função para executar categoria de testes
run_test_category() {
    local category=$1
    local description=$2
    local pytest_args=$3
    local timeout_val=$4
    
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local log_file="data/test_reports/test_${category}_${timestamp}.log"
    
    print_header "🧪 EXECUTANDO TESTES: $category"
    echo "Descrição: $description"
    echo "Argumentos: $pytest_args"
    echo "Timeout: $timeout_val"
    echo "Log: $log_file"
    echo ""
    
    # Construir comando pytest
    local cmd="pytest $pytest_args --tb=short -v --durations=20"
    
    if [ "$timeout_val" != "0" ]; then
        cmd="$cmd --timeout=$timeout_val"
    fi
    
    # Executar e capturar output
    if eval "$cmd" 2>&1 | tee "$log_file"; then
        print_success "Testes $category completados com sucesso"
        
        # Extrair estatísticas
        local passed=$(grep -c " PASSED" "$log_file" || echo "0")
        local failed=$(grep -c " FAILED" "$log_file" || echo "0")
        local timeout=$(grep -c "Timeout" "$log_file" || echo "0")
        
        echo ""
        echo "📊 RESULTADOS:"
        echo "   ✅ PASSED:  $passed"
        echo "   ❌ FAILED:  $failed"
        echo "   ⏱️  TIMEOUT: $timeout"
        echo ""
    else
        print_warning "Alguns testes falharam em $category (veja log para detalhes)"
    fi
}

# Menu principal
if [ $# -eq 0 ]; then
    print_header "🚀 OMNIMIND TEST RUNNER - Seletor de Categoria"
    echo ""
    echo "Opções:"
    echo "  1) [MOCK]      - Testes com @patch (rápido, ~2 min)"
    echo "  2) [SEMI-REAL] - Testes sem @patch (médio, ~10 min)"
    echo "  3) [ALL]       - MOCK + SEMI-REAL (rápido, ~12 min)"
    echo "  4) [REAL]      - Testes com GPU+LLM (lento, 30+ min, sem timeout)"
    echo "  5) [FULL]      - Todos (MOCK+SEMI-REAL+REAL, 1-2 horas)"
    echo "  6) [QUANTUM]   - Testes IBM Quantum (opcional)"
    echo ""
    read -p "Escolha uma opção (1-6): " choice
else
    choice=$1
fi

case $choice in
    1|mock|MOCK)
        print_header "📦 TESTES MOCK (COM @patch)"
        run_test_category "mock" \
            "Testes que usam @patch - validam estrutura, não sistema real" \
            "tests/ -k \"patch or Mock\"" \
            "300"
        ;;
    
    2|semi|semi_real|SEMI-REAL)
        print_header "🔧 TESTES SEMI-REAL (SEM @patch)"
        run_test_category "semi_real" \
            "Testes sem @patch - tocam GPU/PyTorch mas sem LLM real" \
            "tests/ -k \"not patch and not Mock\"" \
            "300"
        ;;
    
    3|all|ALL)
        print_header "📦🔧 TESTES MOCK + SEMI-REAL"
        run_test_category "all_quick" \
            "MOCK + SEMI-REAL - validação rápida do sistema" \
            "tests/ --ignore=tests/consciousness/test_multiseed_analysis.py" \
            "300"
        ;;
    
    4|real|REAL)
        print_header "🚀 TESTES REAL (GPU + LLM + NETWORK)"
        echo ""
        print_warning "⚠️  TESTES REAIS LEVAM 30+ MINUTOS"
        print_warning "    Certifique-se que:"
        print_warning "    1. Ollama qwen2:7b está rodando (http://localhost:11434)"
        print_warning "    2. GPU tem 4GB+ VRAM disponível"
        print_warning "    3. Você tem tempo para esperar"
        echo ""
        read -p "Continuar? (s/n): " confirm
        if [ "$confirm" = "s" ] || [ "$confirm" = "S" ]; then
            run_test_category "real_consciousness" \
                "Testes REAIS: GPU + Ollama + consciência - MEDE Φ REAL" \
                "tests/consciousness/test_multiseed_analysis.py tests/consciousness/test_contrafactual.py" \
                "0"  # Sem timeout para testes reais
        else
            print_warning "Cancelado"
        fi
        ;;
    
    5|full|FULL)
        print_header "🌟 SUITE COMPLETA (MOCK + SEMI-REAL + REAL)"
        print_warning "⚠️  FULL SUITE LEVA 1-2 HORAS"
        print_warning "    Você pode parar com Ctrl+C a qualquer momento"
        echo ""
        read -p "Continuar? (s/n): " confirm
        if [ "$confirm" = "s" ] || [ "$confirm" = "S" ]; then
            run_test_category "full_suite" \
                "Todos os testes - validação completa" \
                "tests/" \
                "0"  # Sem timeout
        else
            print_warning "Cancelado"
        fi
        ;;
    
    6|quantum|QUANTUM)
        print_header "🔬 TESTES IBM QUANTUM"
        if [ -d "tests/quantum" ]; then
            print_warning "⚠️  TESTES IBM LEVAM 5+ MINUTOS POR TESTE"
            print_warning "    Requer: IBM Quantum token (QISKIT_IBM_TOKEN)"
            echo ""
            read -p "Continuar? (s/n): " confirm
            if [ "$confirm" = "s" ] || [ "$confirm" = "S" ]; then
                run_test_category "quantum" \
                    "Testes quânticos reais na IBM - sem Qiskit mock" \
                    "tests/quantum/" \
                    "0"  # Sem timeout para quantum
            else
                print_warning "Cancelado"
            fi
        else
            print_error "Diretório tests/quantum/ não encontrado"
            echo "Crie testes quânticos em tests/quantum/test_ibm_real_*.py"
        fi
        ;;
    
    *)
        print_error "Opção inválida: $choice"
        exit 1
        ;;
esac

echo ""
print_header "✅ EXECUÇÃO FINALIZADA"
echo "Logs salvos em: data/test_reports/"
echo ""
echo "Para analisar resultado:"
echo "  tail -100 data/test_reports/test_*.log"
echo ""
