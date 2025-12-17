#!/bin/bash
# Script para verificar estado do sistema antes de executar validação científica

echo "🔍 VERIFICAÇÃO DO SISTEMA ANTES DE EXECUÇÃO"
echo "=========================================="
echo ""

# Verificar memória
echo "📊 MEMÓRIA:"
free -h | grep Mem
MEM_AVAIL=$(free -g | grep Mem | awk '{print $7}')
if [ "$MEM_AVAIL" -lt 4 ]; then
    echo "⚠️  AVISO: Menos de 4GB de memória disponível"
else
    echo "✅ Memória suficiente: ${MEM_AVAIL}GB disponível"
fi
echo ""

# Verificar load average
echo "📊 LOAD AVERAGE:"
LOAD=$(uptime | awk -F'load average:' '{print $2}')
echo "   $LOAD"
LOAD_1MIN=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
# Comparar usando awk (não precisa de bc)
LOAD_CHECK=$(echo "$LOAD_1MIN 8.0" | awk '{if ($1 > $2) print "high"; else print "ok"}')
if [ "$LOAD_CHECK" = "high" ]; then
    echo "⚠️  AVISO: Load average alto (>8.0) - sistema sob carga pesada"
else
    echo "✅ Load average aceitável"
fi
echo ""

# Verificar processos MCP
echo "📊 PROCESSOS MCP:"
MCP_COUNT=$(ps aux | grep -E "mcp_.*_server|mcp_.*_wrapper" | grep -v grep | wc -l)
echo "   $MCP_COUNT processos MCP rodando"
if [ "$MCP_COUNT" -gt 10 ]; then
    echo "⚠️  AVISO: Muitos processos MCP ($MCP_COUNT) - considere fechar alguns"
    echo "   Processos MCP ativos:"
    ps aux | grep -E "mcp_.*_server|mcp_.*_wrapper" | grep -v grep | awk '{print "      PID", $2, "-", $11}'
else
    echo "✅ Número de processos MCP aceitável"
fi
echo ""

# Verificar espaço em disco
echo "📊 ESPAÇO EM DISCO:"
df -h . | tail -1
DISK_AVAIL=$(df . | tail -1 | awk '{print $4}')
if [ "$DISK_AVAIL" -lt 1048576 ]; then  # Menos de 1GB em KB
    echo "⚠️  AVISO: Pouco espaço em disco (<1GB)"
else
    echo "✅ Espaço em disco suficiente"
fi
echo ""

# Verificar GPU
echo "📊 GPU:"
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,memory.free,memory.total --format=csv,noheader | head -1
    GPU_FREE=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)
    if [ "$GPU_FREE" -lt 100 ]; then
        echo "⚠️  AVISO: Pouca memória GPU livre (<100MB)"
    else
        echo "✅ GPU com memória suficiente"
    fi
else
    echo "⚠️  nvidia-smi não encontrado"
fi
echo ""

# Resumo
echo "=========================================="
echo "📋 RESUMO:"
READY=true
if [ "$MEM_AVAIL" -lt 4 ]; then
    READY=false
fi
if [ "$LOAD_CHECK" = "high" ]; then
    READY=false
fi
if [ "$MCP_COUNT" -gt 10 ]; then
    READY=false
fi

if [ "$READY" = "true" ]; then
    echo "✅ Sistema pronto para execução"
    exit 0
else
    echo "⚠️  Sistema pode ter problemas durante execução"
    echo ""
    echo "💡 RECOMENDAÇÕES:"
    if [ "$MEM_AVAIL" -lt 4 ]; then
        echo "   - Liberar memória (fechar programas desnecessários)"
    fi
    if [ "$LOAD_CHECK" = "high" ]; then
        echo "   - Aguardar carga do sistema diminuir"
        echo "   - Ou executar com 'nice -n 19' para reduzir prioridade"
    fi
    if [ "$MCP_COUNT" -gt 10 ]; then
        echo "   - Considerar fechar alguns processos MCP"
    fi
    exit 1
fi

