#!/bin/bash
# REFERENCE CARD - 500-CICLOS PRODUCTION
# Copie e cole os comandos abaixo conforme necessário

echo "════════════════════════════════════════════════════════════════"
echo "  🚀 500-CICLOS OMNIMIND - REFERENCE CARD"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📍 LOCALIZAÇÃO: /home/fahbrain/projects/omnimind"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🎯 COMANDOS PRINCIPAIS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "1️⃣  EXECUTAR 500 CICLOS (Opção A - Simples):"
echo "   python3 scripts/run_500_cycles_production.py"
echo ""

echo "2️⃣  EXECUTAR 500 CICLOS (Opção B - Com Checklist)"
echo "   bash scripts/run_500_cycles_production.sh"
echo ""

echo "3️⃣  EXECUTAR EM BACKGROUND:"
echo "   nohup python3 scripts/run_500_cycles_production.py > run.log 2>&1 &"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📊 MONITORAMENTO (Use em terminal separado)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Monitor em tempo real:"
echo "   bash scripts/monitor_500_cycles.sh"
echo ""

echo "Contar ciclos em tempo real:"
echo "   watch -n 3 'ls -1 data/monitor/executions/\$(ls -d data/monitor/executions/*/ | tail -1 | xargs basename)/ | wc -l'"
echo ""

echo "Ver PHI dos últimos ciclos:"
echo "   watch -n 5 'ls -t data/monitor/executions/*/[0-9]*.json | head -5 | xargs -I {} sh -c \"echo {} && tail -n 1 {}\"'"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📈 ANÁLISE (Após execução terminar)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Análise automática da última execução:"
echo "   python3 scripts/analyze_execution_results.py"
echo ""

echo "Análise de execução específica:"
echo "   python3 scripts/analyze_execution_results.py data/monitor/executions/execution_001_..."
echo ""

echo "Listar todas as execuções:"
echo "   ls -lh data/monitor/executions/"
echo ""

echo "Contar ciclos completados:"
echo "   ls -1 data/monitor/executions/*/[0-9]*.json | wc -l"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📁 ESTRUTURA DE DADOS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Ver índice global:"
echo "   cat data/monitor/executions/index.json | python3 -m json.tool"
echo ""

echo "Ver resumo da execução 1:"
echo "   cat data/monitor/executions/execution_001_*/summary.json | python3 -m json.tool"
echo ""

echo "Ver ciclo 1:"
echo "   cat data/monitor/executions/execution_001_*/1.json | python3 -m json.tool"
echo ""

echo "Ver ciclo 500:"
echo "   cat data/monitor/executions/execution_001_*/500.json | python3 -m json.tool"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🔧 TROUBLESHOOTING"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Matar processo se travar:"
echo "   pkill -9 -f run_500_cycles"
echo ""

echo "Verificar se GPU está funcionando:"
echo "   nvidia-smi"
echo ""

echo "Aumentar limites de sistema:"
echo "   ulimit -u unlimited && ulimit -s unlimited"
echo ""

echo "Diagnóstico completo de threads:"
echo "   python3 scripts/diagnose_threads.py"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📚 DOCUMENTAÇÃO"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Guia rápido (1 página):"
echo "   cat docs/GUIA_500_CICLOS_PRODUCTION.md"
echo ""

echo "Guia completo:"
echo "   cat docs/EXECUTAR_500_CICLOS_PRODUCTION.md"
echo ""

echo "Resumo final:"
echo "   cat docs/RESUMO_500_CICLOS_FINAL.md"
echo ""

echo "Início rápido:"
echo "   cat INICIO_RAPIDO_500_CICLOS.md"
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "  ✅ Tudo pronto! Execute um dos comandos acima."
echo "════════════════════════════════════════════════════════════════"
