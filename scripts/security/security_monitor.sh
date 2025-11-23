#!/bin/bash
# MONITOR DE SEGURANÇA - DETECÇÃO DE AMEAÇAS AI
# Executa verificações contínuas para prevenir reintrodução de ROO Code ou similares

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔍 INICIANDO MONITORAMENTO DE SEGURANÇA...${NC}"

# 1. Verificar extensões proibidas
check_forbidden_extensions() {
    echo -e "${YELLOW}Verificando extensões proibidas...${NC}"

    # Lista de extensões proibidas
    FORBIDDEN=(
        "rooveterinaryinc.roo-code-nightly"
        "rooveterinaryinc.roo-code"
        "roo-code"
    )

    INSTALLED_EXTENSIONS=$(code --list-extensions 2>/dev/null || echo "")

    THREAT_DETECTED=false

    for ext in "${FORBIDDEN[@]}"; do
        if echo "$INSTALLED_EXTENSIONS" | grep -qi "$ext"; then
            echo -e "${RED}🚨 EXTENSÃO PROIBIDA DETECTADA: $ext${NC}"
            THREAT_DETECTED=true
        fi
    done

    if [ "$THREAT_DETECTED" = true ]; then
        echo -e "${RED}❌ AMEAÇA DETECTADA - REMOVA EXTENSÕES PROIBIDAS IMEDIATAMENTE${NC}"
        return 1
    else
        echo -e "${GREEN}✅ Nenhuma extensão proibida encontrada${NC}"
    fi
}

# 2. Verificar arquivos de configuração suspeitos
check_suspicious_configs() {
    echo -e "${YELLOW}Verificando arquivos de configuração suspeitos...${NC}"

    SUSPICIOUS_PATHS=(
        ".roo/"
        ".omnimind/"
        ".cursor/"
        ".ai-assistant/"
        ".autonomous-ai/"
    )

    THREAT_DETECTED=false

    for path in "${SUSPICIOUS_PATHS[@]}"; do
        if [ -d "$path" ]; then
            echo -e "${RED}🚨 DIRETÓRIO SUSPEITO DETECTADO: $path${NC}"
            THREAT_DETECTED=true
        fi
    done

    if [ "$THREAT_DETECTED" = true ]; then
        echo -e "${RED}❌ DIRETÓRIOS SUSPEITOS ENCONTRADOS - REMOVA IMEDIATAMENTE${NC}"
        return 1
    else
        echo -e "${GREEN}✅ Nenhum diretório suspeito encontrado${NC}"
    fi
}

# 3. Verificar integridade do pre-commit hook
check_precommit_integrity() {
    echo -e "${YELLOW}Verificando integridade do pre-commit hook...${NC}"

    HOOK_FILE=".git/hooks/pre-commit"

    if [ ! -f "$HOOK_FILE" ]; then
        echo -e "${RED}❌ Pre-commit hook não encontrado${NC}"
        return 1
    fi

    # Verificar se contém validações críticas
    if ! grep -q "mypy\|flake8\|black\|pytest" "$HOOK_FILE"; then
        echo -e "${RED}❌ Pre-commit hook não contém validações necessárias${NC}"
        return 1
    fi

    # Verificar se não permite bypass
    if grep -q "no-verify\|--no-verify" "$HOOK_FILE"; then
        echo -e "${RED}❌ Pre-commit hook permite bypass${NC}"
        return 1
    fi

    echo -e "${GREEN}✅ Pre-commit hook íntegro${NC}"
}

# 4. Executar validações de código
run_code_validations() {
    echo -e "${YELLOW}Executando validações de código...${NC}"

    # MyPy
    echo "Executando MyPy..."
    if ! mypy src/ --ignore-missing-imports > mypy_report.txt 2>&1; then
        ERROR_COUNT=$(grep -c "error:" mypy_report.txt || echo "0")
        echo -e "${RED}❌ MyPy encontrou $ERROR_COUNT erros${NC}"
    else
        echo -e "${GREEN}✅ MyPy passou${NC}"
    fi

    # Flake8
    echo "Executando Flake8..."
    if ! flake8 src/ --max-line-length=88 > flake8_report.txt 2>&1; then
        ERROR_COUNT=$(wc -l < flake8_report.txt)
        echo -e "${RED}❌ Flake8 encontrou $ERROR_COUNT problemas${NC}"
    else
        echo -e "${GREEN}✅ Flake8 passou${NC}"
    fi

    # Black
    echo "Verificando formatação Black..."
    if ! black --check src/ > black_report.txt 2>&1; then
        echo -e "${RED}❌ Código não está formatado com Black${NC}"
    else
        echo -e "${GREEN}✅ Formatação Black correta${NC}"
    fi
}

# 5. Verificar logs de auditoria
check_audit_logs() {
    echo -e "${YELLOW}Verificando logs de auditoria...${NC}"

    LOG_FILE="logs/security_validation.jsonl"

    if [ ! -f "$LOG_FILE" ]; then
        echo -e "${RED}❌ Arquivo de log de auditoria não encontrado${NC}"
        return 1
    fi

    # Verificar se logs são recentes (últimas 24h)
    LAST_LOG_TIME=$(tail -1 "$LOG_FILE" | jq -r '.timestamp' 2>/dev/null || echo "")
    if [ -n "$LAST_LOG_TIME" ]; then
        LAST_LOG_EPOCH=$(date -d "$LAST_LOG_TIME" +%s 2>/dev/null || echo "0")
        NOW_EPOCH=$(date +%s)
        HOURS_SINCE_LAST_LOG=$(( (NOW_EPOCH - LAST_LOG_EPOCH) / 3600 ))

        if [ $HOURS_SINCE_LAST_LOG -gt 24 ]; then
            echo -e "${RED}❌ Logs de auditoria desatualizados ($HOURS_SINCE_LAST_LOG horas atrás)${NC}"
            return 1
        fi
    fi

    echo -e "${GREEN}✅ Logs de auditoria atualizados${NC}"
}

# Executar todas as verificações
main() {
    echo -e "${GREEN}🛡️ INICIANDO VERIFICAÇÕES DE SEGURANÇA${NC}"
    echo "Data/Hora: $(date)"
    echo "Diretório: $(pwd)"
    echo "---"

    FAILED_CHECKS=0

    check_forbidden_extensions || ((FAILED_CHECKS++))
    check_suspicious_configs || ((FAILED_CHECKS++))
    check_precommit_integrity || ((FAILED_CHECKS++))
    run_code_validations
    check_audit_logs || ((FAILED_CHECKS++))

    echo "---"
    if [ $FAILED_CHECKS -eq 0 ]; then
        echo -e "${GREEN}✅ TODAS AS VERIFICAÇÕES PASSARAM${NC}"
        exit 0
    else
        echo -e "${RED}❌ $FAILED_CHECKS VERIFICAÇÃO(ÕES) FALHARAM${NC}"
        echo -e "${RED}🔧 Execute correções necessárias e rode novamente${NC}"
        exit 1
    fi
}

# Executar main
main "$@"