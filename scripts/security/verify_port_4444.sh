#!/bin/bash
# Script de verificação de porta 4444
# Criado: 2025-12-05

echo "🔍 Verificando porta 4444..."

# Verificar regras iptables
echo "📊 Regras iptables:"
sudo iptables -L -n | grep 4444 || echo "   Nenhuma regra encontrada"

# Verificar processos
echo "📊 Processos usando porta 4444:"
sudo lsof -i :4444 || echo "   Nenhum processo encontrado"

# Verificar serviços OmniMind
echo "📊 Serviços OmniMind:"
for port in 8000 8080 3000 3001; do
    if sudo lsof -i :$port > /dev/null 2>&1; then
        echo "   ✅ Porta $port: Em uso"
    else
        echo "   ⚠️  Porta $port: Não em uso"
    fi
done
