#!/bin/bash
# Script para diagnosticar problemas de memória e processos em loop
# Autor: Fabrício da Silva + assistência de IA

echo "🔍 DIAGNÓSTICO DE MEMÓRIA E PROCESSOS"
echo "======================================"
echo ""

# 1. Memória e Swap
echo "📊 MEMÓRIA E SWAP:"
free -h
echo ""

# 2. Processos Python usando mais memória
echo "📊 TOP 10 PROCESSOS PYTHON (por memória):"
ps aux --sort=-%mem | grep python | head -10 | awk '{printf "PID: %-8s MEM: %6s%% CPU: %5s%% CMD: %s\n", $2, $4, $3, $11" "$12" "$13" "$14" "$15}'
echo ""

# 3. Processos com CPU alta (possível loop)
echo "📊 PROCESSOS COM CPU ALTA (>50%):"
ps aux | awk '$3 > 50 && /python/ {printf "PID: %-8s CPU: %6s%% MEM: %6s%% CMD: %s\n", $2, $3, $4, $11" "$12" "$13" "$14}' | head -10
echo ""

# 4. Verificar se backends estão respondendo
echo "📊 STATUS DOS BACKENDS:"
for port in 8000 8080 3001; do
    if curl -s --max-time 2 "http://localhost:${port}/health/" > /dev/null 2>&1; then
        response_time=$(curl -s -w "%{time_total}" -o /dev/null "http://localhost:${port}/health/" 2>/dev/null || echo "10.0")
        echo "   ✅ Porta ${port}: Respondendo (${response_time}s)"
    else
        echo "   ❌ Porta ${port}: Não responde"
    fi
done
echo ""

# 5. Verificar GPU
echo "📊 GPU:"
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits | awk -F', ' '{printf "   Memória: %s MiB/%s MiB (%.1f%%)\n", $1, $2, ($1/$2)*100}'
else
    echo "   ℹ️  nvidia-smi não disponível"
fi
echo ""

# 6. Verificar processos travados (stuck)
echo "📊 PROCESSOS COM MUITO TEMPO DE CPU (possível travamento):"
ps aux --sort=-%cpu | grep python | head -5 | awk '{printf "PID: %-8s CPU: %6s%% TEMPO: %s CMD: %s\n", $2, $3, $10, $11" "$12" "$13}'
echo ""

# 7. Verificar memory leaks (processos crescendo em memória)
echo "📊 PROCESSOS COM MAIS MEMÓRIA (verificar se crescem):"
ps aux --sort=-%mem | grep python | head -5 | awk '{printf "PID: %-8s MEM: %6s%% VSZ: %s RSS: %s CMD: %s\n", $2, $4, $5, $6, $11" "$12" "$13}'
echo ""

# 8. Verificar se há processos zombie
echo "📊 PROCESSOS ZOMBIE:"
zombies=$(ps aux | grep -E '\[.*\] <defunct>' | wc -l)
if [ "$zombies" -gt 0 ]; then
    echo "   ⚠️  Encontrados $zombies processos zombie"
    ps aux | grep -E '\[.*\] <defunct>' | head -5
else
    echo "   ✅ Nenhum processo zombie encontrado"
fi
echo ""

# 9. Verificar logs recentes de erro
echo "📊 ÚLTIMOS ERROS NOS LOGS:"
if [ -f "logs/main_cycle.log" ]; then
    echo "   Logs main_cycle.log:"
    tail -20 logs/main_cycle.log | grep -i "error\|fail\|memory\|leak" | tail -5 || echo "      Nenhum erro recente"
fi
if [ -f "logs/backend_8000.log" ]; then
    echo "   Logs backend_8000.log:"
    tail -20 logs/backend_8000.log | grep -i "error\|fail\|loop\|stuck" | tail -5 || echo "      Nenhum erro recente"
fi
echo ""

# 10. Recomendações
echo "💡 RECOMENDAÇÕES:"
mem_available=$(free -h | grep Mem | awk '{print $7}' | sed 's/Gi//' | sed 's/Mi//')
mem_available_num=$(echo "$mem_available" | sed 's/[^0-9.]//g')

if (( $(echo "$mem_available_num < 2" | bc -l 2>/dev/null || echo "0") )); then
    echo "   ⚠️  Memória baixa (<2GB) - considere:"
    echo "      - Parar processos backend desnecessários"
    echo "      - Liberar cache: sudo sync && sudo sysctl vm.drop_caches=3"
    echo "      - Usar swap (já configurado)"
else
    echo "   ✅ Memória suficiente para execução"
fi

echo ""
echo "✅ Diagnóstico completo!"

