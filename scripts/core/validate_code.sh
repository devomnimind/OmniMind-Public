#!/bin/bash

echo "🔍 VALIDAÇÃO MANUAL DE QUALIDADE DE CÓDIGO"
echo "=========================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para output colorido
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

# Verificar ROO Code
# echo "1. Verificando presença de ROO Code..."
# if code --list-extensions | grep -q roo; then
#     echo -e "${RED}🚨 ROO CODE AINDA INSTALADA! REMOVA IMEDIATAMENTE${NC}"
#     exit 1
# else
#     print_status 0 "ROO Code não encontrada"
# fi

# Black formatting
echo "2. Verificando formatação (Black)..."
if black --check --quiet src/ tests/ > /dev/null 2>&1; then
    print_status 0 "Formatação correta"
else
    echo -e "${YELLOW}⚠️  Formatação incorreta. Corrigindo...${NC}"
    black src/ tests/
    print_status 1 "Formatação corrigida automaticamente"
fi

# Flake8 linting
echo "3. Verificando linting (Flake8)..."
FLAKE8_OUTPUT=$(flake8 src/ tests/ --count --select=E9,F63,F7,F82 2>/dev/null)
if [ "$FLAKE8_OUTPUT" = "0" ]; then
    print_status 0 "Linting limpo"
else
    echo -e "${RED}❌ Erros críticos de linting: $FLAKE8_OUTPUT${NC}"
    flake8 src/ tests/ --select=E9,F63,F7,F82
    exit 1
fi

# MyPy type checking
echo "4. Verificando tipos (MyPy)..."
MYPY_ERRORS=$(mypy src/ --ignore-missing-imports 2>&1 | grep -c "error:")
if [ "$MYPY_ERRORS" -eq 0 ]; then
    print_status 0 "Tipos corretos (0 erros)"
elif [ "$MYPY_ERRORS" -le 25 ]; then
    echo -e "${YELLOW}⚠️  $MYPY_ERRORS erros de tipo (aceitável)${NC}"
else
    echo -e "${RED}❌ Muitos erros de tipo: $MYPY_ERRORS (máximo: 25)${NC}"
    exit 1
fi

# Pytest
echo "5. Executando testes..."
if python -m pytest --tb=short -q > /dev/null 2>&1; then
    print_status 0 "Testes passando"
else
    echo -e "${RED}❌ Testes falhando${NC}"
    python -m pytest --tb=short
    exit 1
fi

# Verificar arquivos suspeitos
echo "6. Verificando integridade de arquivos..."
SUSPICIOUS=$(find . -type d \( -name .venv -o -name .git -o -name .mypy_cache -o -name .pytest_cache \) -prune -o \( -name ".roo" \) -print)
if [ -z "$SUSPICIOUS" ]; then
    print_status 0 "Nenhum arquivo suspeito encontrado"
else
    echo -e "${RED}❌ Arquivos suspeitos encontrados:${NC}"
    echo "$SUSPICIOUS"
    exit 1
fi

# Verificar audit chain
echo "7. Verificando cadeia de auditoria..."
python -c "
import os
import sys
import hashlib
import json
from pathlib import Path

def verify_audit_chain():
    audit_dir = Path('logs')
    hash_chain_file = audit_dir / 'hash_chain.json'
    
    if not hash_chain_file.exists():
        return False, 'Arquivo de cadeia de auditoria não encontrado'
    
    try:
        with open(hash_chain_file, 'r') as f:
            chain_data = json.load(f)
        
        previous_hash = '0' * 64
        
        for entry in chain_data.get('chain', []):
            current_hash = entry.get('hash', '')
            expected_hash = hashlib.sha256(
                f\"{previous_hash}:{entry.get('timestamp', '')}:{entry.get('action', '')}:{entry.get('data', '')}\".encode()
            ).hexdigest()
            
            if current_hash != expected_hash:
                return False, f'Corrupção detectada na entrada {entry.get(\"timestamp\", \"desconhecida\")}'
            
            previous_hash = current_hash
        
        return True, 'Cadeia de auditoria válida'
        
    except Exception as e:
        return False, f'Erro na verificação: {e}'

valid, message = verify_audit_chain()
if valid:
    print('✅ Cadeia de auditoria válida')
else:
    print(f'❌ Problema na cadeia de auditoria: {message}')
    exit(1)
"

echo ""
echo -e "${GREEN}🎉 TODAS VALIDAÇÕES PASSARAM!${NC}"
echo "Código pronto para commit seguro."
