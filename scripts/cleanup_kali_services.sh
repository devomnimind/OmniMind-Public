#!/bin/bash

# ========================================================================
# LIMPEZA DE SERVIÇOS KALI NÃO UTILIZADOS
# ========================================================================
# Este script mata processos de ferramentas de penetração testing
# que não estão sendo usados no ambiente de desenvolvimento OmniMind
# ========================================================================

set -e

echo "🔍 Scanning para processos Kali/Metasploit não utilizados..."
echo ""

# Array de processos perigosos que queremos matar
DANGEROUS_PROCESSES=(
    "metasploitd"
    "msfvenom"
    "msfconsole"
    "postgres.*metasploit"
    "nmap"
    "sqlmap"
    "snort"
    "suricata"
    "airmon-ng"
    "aircrack-ng"
    "hydra"
    "john"
    "hashcat"
    "sqlninja"
    "beef"
    "empire"
    "covenant"
    "responder"
    "inveigh"
    "mitm6"
    "ntlmrelayx"
    "impacket"
    "crackmapexec"
    "evil-winrm"
    "bloodhound"
)

KILLED_COUNT=0

for process in "${DANGEROUS_PROCESSES[@]}"; do
    # Procurar por processos (excluir grep e chrome_crashpad_handler)
    PIDS=$(pgrep -f "$process" 2>/dev/null | grep -v grep || true)

    if [ -n "$PIDS" ]; then
        echo "⚠️  Encontrado: $process (PIDs: $PIDS)"
        for pid in $PIDS; do
            kill -9 "$pid" 2>/dev/null && {
                echo "   ✅ Matou PID $pid"
                ((KILLED_COUNT++))
            } || {
                echo "   ❌ Falha ao matar PID $pid"
            }
        done
    fi
done

echo ""
echo "========================================================================="
if [ $KILLED_COUNT -eq 0 ]; then
    echo "✅ Nenhum processo perigoso encontrado. Sistema limpo!"
else
    echo "✅ Limpeza concluída! $KILLED_COUNT processo(s) matado(s)"
fi
echo "========================================================================="
echo ""
echo "📊 Recursos atuais:"
free -h | head -2
echo ""
echo "💾 Uso de disco:"
df -h / | tail -1
