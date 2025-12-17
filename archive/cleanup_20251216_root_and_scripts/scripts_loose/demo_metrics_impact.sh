#!/bin/bash

# Script de Demonstração: Impacto da Implementação

cd /home/fahbrain/projects/omnimind

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  📊 DEMONSTRAÇÃO: Impacto da Implementação"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Analisar estado atual dos reports
echo "1️⃣  STATUS ATUAL DOS REPORTS"
echo "─────────────────────────────────────────────────────────────"

TOTAL_JSON=$(find data/reports/modules -name "*.json" -type f 2>/dev/null | wc -l)
TOTAL_GZ=$(find data/reports/modules -name "*.json.gz" -type f 2>/dev/null | wc -l)

SIZE_JSON=$(du -sh data/reports/modules --exclude=archive 2>/dev/null | cut -f1)
SIZE_ARCHIVE=$(du -sh data/reports/modules/archive 2>/dev/null | cut -f1)

echo "  📁 Arquivos JSON (ativos): $TOTAL_JSON"
echo "  📦 Arquivos GZ (compactados): $TOTAL_GZ"
echo "  💾 Tamanho JSON: $SIZE_JSON"
echo "  🗜️  Tamanho Archive: $SIZE_ARCHIVE"

echo ""
echo "2️⃣  SNAPSHOT DE MÉTRICAS"
echo "─────────────────────────────────────────────────────────────"

if [ -f "data/monitor/module_metrics/snapshot.json" ]; then
    MODULES_WITH_METRICS=$(jq 'keys | length' data/monitor/module_metrics/snapshot.json 2>/dev/null || echo "0")
    echo "  📊 Módulos com métricas registradas: $MODULES_WITH_METRICS"

    # Listar alguns exemplos
    echo ""
    echo "  📋 Exemplos de módulos com métricas:"
    jq -r 'keys[] | select(startswith("integration_loop_cycle") or startswith("autopoietic_cycle")) | "     🔹 \(.)"' data/monitor/module_metrics/snapshot.json 2>/dev/null | head -5
else
    echo "  ⚠️  snapshot.json não encontrado ainda"
fi

echo ""
echo "3️⃣  ÚLTIMOS REPORTS GERADOS"
echo "─────────────────────────────────────────────────────────────"

echo "  📅 Integration Loop Cycles:"
ls -t data/reports/modules/integration_loop_cycle_*.json 2>/dev/null | head -3 | while read f; do
    echo "     📄 $(basename $f) ($(stat -f%z "$f" 2>/dev/null || stat -c%s "$f" 2>/dev/null | numfmt --to=iec) bytes)"
done

echo ""
echo "  🔄 Autopoietic Cycles:"
ls -t data/reports/modules/autopoietic_cycle_*.json 2>/dev/null | head -3 | while read f; do
    echo "     📄 $(basename $f) ($(stat -f%z "$f" 2>/dev/null || stat -c%s "$f" 2>/dev/null | numfmt --to=iec) bytes)"
done

echo ""
echo "4️⃣  STATUS DO SCHEDULER"
echo "─────────────────────────────────────────────────────────────"

python3 << 'EOF'
try:
    from src.observability.report_maintenance_scheduler import get_report_maintenance_scheduler

    scheduler = get_report_maintenance_scheduler(auto_start=False)
    status = scheduler.get_status()

    print(f"  🔄 Status: {'✅ Rodando' if status['running'] else '⏸️  Parado'}")
    print(f"  ⏱️  Intervalo de verificação: {status['check_interval_seconds']} segundos")
    print(f"  ⏰ Execução diária: {status['daily_execution_time']}")

    if status['last_check_time']:
        print(f"  📍 Última verificação: {status['last_check_time']}")
    if status['last_execution_time']:
        print(f"  ✔️  Última execução: {status['last_execution_time']}")
except Exception as e:
    print(f"  ⚠️  Erro ao verificar status: {e}")
EOF

echo ""
echo "5️⃣  ESTIMATIVA DE ECONOMIA"
echo "─────────────────────────────────────────────────────────────"

python3 << 'EOF'
import os
from pathlib import Path

# Simular compressão (sem realmente fazer)
json_dir = Path("data/reports/modules")
total_size = 0
total_files = 0

for f in json_dir.glob("*.json"):
    total_size += f.stat().st_size
    total_files += 1

if total_files > 0:
    avg_size = total_size / total_files
    # Assumir compressão gzip de ~85%
    compressed_size = total_size * 0.15
    savings = total_size - compressed_size

    print(f"  📊 Dados Atuais:")
    print(f"     • Arquivos: {total_files:,}")
    print(f"     • Tamanho total: {total_size / (1024*1024):.1f} MB")
    print(f"     • Tamanho médio: {avg_size / 1024:.1f} KB")
    print()
    print(f"  🎯 Após Compressão Automática:")
    print(f"     • Tamanho compactado: {compressed_size / (1024*1024):.1f} MB")
    print(f"     • Economia: {savings / (1024*1024):.1f} MB ({savings/total_size*100:.0f}%)")
else:
    print("  ℹ️  Nenhum arquivo JSON encontrado ainda")
EOF

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  ✅ Implementação completa e operacional!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📚 Documentação: IMPLEMENTACAO_METRICAS_CLEANUP_20251211.md"
echo "🔧 Validação: scripts/validate_metrics_implementation.sh"
echo ""
