#!/bin/bash

# 🔍 DEBUG: WHO KILLED MY SCRIPT?
# ================================
# Descobre quem está enviando SIGKILL (sinal 9) para dev scripts
# strace mostra: quem/quando/por quê

PROJECT_ROOT="${1:-.}"
SCRIPT_PATH="${2:-scripts/recovery/03_run_500_cycles_no_timeout.sh}"

if [ ! -f "$SCRIPT_PATH" ]; then
    echo "❌ Script não encontrado: $SCRIPT_PATH"
    exit 1
fi

cd "$PROJECT_ROOT" || exit 1

echo "╔═════════════════════════════════════════════════════════════════╗"
echo "║  🔍 DEBUG: WHO IS KILLING DEVELOPMENT SCRIPTS?                ║"
echo "╚═════════════════════════════════════════════════════════════════╝"
echo ""
echo "Executando script com strace para rastrear sinais..."
echo "Script: $SCRIPT_PATH"
echo ""
echo "📊 Rastreando:"
echo "  • SIGNALS (especialmente SIGKILL/9)"
echo "  • PROCESS CREATION (fork/clone)"
echo "  • PROCESS TERMINATION (exit/exit_group)"
echo ""

# Criar arquivo de saída
STRACE_LOG="/tmp/strace_kill_debug_$(date +%s).log"

echo "📝 Log: $STRACE_LOG"
echo "🛑 Pressione Ctrl+C para parar"
echo ""

# Executar com strace - rastrear sinais
strace -f \
    -e trace=kill,exit,exit_group,signal \
    -e signal=9,15 \
    -s 200 \
    -o "$STRACE_LOG" \
    bash "$SCRIPT_PATH" &

STRACE_PID=$!
wait $STRACE_PID
EXIT_CODE=$?

echo ""
echo "╔═════════════════════════════════════════════════════════════════╗"
echo "║  📋 ANÁLISE DE STRACE                                          ║"
echo "╚═════════════════════════════════════════════════════════════════╝"
echo ""

# Analisar SIGKILL (9)
SIGKILL_COUNT=$(grep -c "kill.*SIG9\|SIGKILL" "$STRACE_LOG" 2>/dev/null || echo "0")
SIGTERM_COUNT=$(grep -c "kill.*SIG15\|SIGTERM" "$STRACE_LOG" 2>/dev/null || echo "0")

echo "🔴 SIGKILL (não pode ser interceptado): $SIGKILL_COUNT eventos"
echo "🟡 SIGTERM (pode ser interceptado):     $SIGTERM_COUNT eventos"
echo ""

if [ "$SIGKILL_COUNT" -gt 0 ]; then
    echo "❌ ENCONTRADO: SIGKILL enviado para seu processo!"
    echo ""
    echo "Contexto de SIGKILL:"
    grep "kill.*SIG9\|SIGKILL" "$STRACE_LOG" | head -10
    echo ""
    echo "🔎 SUSPEITOS:"
    echo "  1. resource_protector.py usando proc.kill() (SIGKILL)"
    echo "  2. OOM killer do Linux (memória insuficiente)"
    echo "  3. Timeout de systemd ou daemon supervisor"
    echo ""
    echo "✅ SOLUÇÃO:"
    echo "  → ResourceProtector deveria usar terminate() em vez de kill()"
    echo "  → Ou adicionar padrão de script dev à whitelist"
fi

if [ "$SIGTERM_COUNT" -gt 0 ]; then
    echo "🟡 Encontrado: $SIGTERM_COUNT sinais SIGTERM (normais)"
    echo "   → Seu handler Python deve estar funcionando"
fi

echo ""
echo "📊 Primeiras 50 linhas de strace (sinais):"
echo "───────────────────────────────────────────────────"
grep "signal\|kill\|exit" "$STRACE_LOG" | head -50
echo "───────────────────────────────────────────────────"
echo ""

echo "💾 Log completo em: $STRACE_LOG"
echo ""

if [ $EXIT_CODE -eq 137 ]; then
    echo "❌ Exit code 137 = SIGKILL (sinal 9 + 128)"
    echo "   Seu processo foi morto por SIGKILL - NÃO pode ser interceptado"
elif [ $EXIT_CODE -eq 143 ]; then
    echo "🟡 Exit code 143 = SIGTERM (sinal 15 + 128)"
    echo "   Seu handler SIGTERM deveria ter funcionado"
elif [ $EXIT_CODE -eq 130 ]; then
    echo "🛑 Exit code 130 = SIGINT (Ctrl+C)"
    echo "   Parada normal do usuário"
fi

echo ""
