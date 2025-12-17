#!/bin/bash

# Script de Validação da Implementação de Métricas e Cleanup Automático
# Verifica se as correções foram aplicadas corretamente

set -e

cd /home/fahbrain/projects/omnimind

echo "=============================================="
echo "🧪 Validação de Implementação de Métricas"
echo "=============================================="

# 1. Validar se os imports foram adicionados
echo ""
echo "✓ Verificando se record_metric() foi adicionado em integration_loop.py..."
if grep -q "metrics_collector.record_metric" src/consciousness/integration_loop.py; then
    echo "  ✅ record_metric() encontrado em integration_loop.py"
else
    echo "  ❌ record_metric() NÃO encontrado em integration_loop.py"
    exit 1
fi

echo ""
echo "✓ Verificando se record_metric() foi adicionado em manager.py..."
if grep -q "metrics_collector.record_metric" src/autopoietic/manager.py; then
    echo "  ✅ record_metric() encontrado em manager.py"
else
    echo "  ❌ record_metric() NÃO encontrado em manager.py"
    exit 1
fi

# 2. Validar arquivos de maintenance
echo ""
echo "✓ Verificando se report_maintenance.py foi criado..."
if [ -f "src/observability/report_maintenance.py" ]; then
    echo "  ✅ report_maintenance.py existe"
else
    echo "  ❌ report_maintenance.py NÃO encontrado"
    exit 1
fi

echo ""
echo "✓ Verificando se report_maintenance_scheduler.py foi criado..."
if [ -f "src/observability/report_maintenance_scheduler.py" ]; then
    echo "  ✅ report_maintenance_scheduler.py existe"
else
    echo "  ❌ report_maintenance_scheduler.py NÃO encontrado"
    exit 1
fi

# 3. Validar inicialização no main.py
echo ""
echo "✓ Verificando se scheduler foi inicializado em main.py..."
if grep -q "init_report_maintenance_scheduler" src/main.py; then
    echo "  ✅ init_report_maintenance_scheduler encontrado em main.py"
else
    echo "  ❌ init_report_maintenance_scheduler NÃO encontrado em main.py"
    exit 1
fi

# 4. Verificar sintaxe Python
echo ""
echo "✓ Verificando sintaxe Python dos novos arquivos..."
python -m py_compile src/observability/report_maintenance.py && echo "  ✅ report_maintenance.py: sintaxe OK" || exit 1
python -m py_compile src/observability/report_maintenance_scheduler.py && echo "  ✅ report_maintenance_scheduler.py: sintaxe OK" || exit 1
python -m py_compile src/consciousness/integration_loop.py && echo "  ✅ integration_loop.py: sintaxe OK" || exit 1
python -m py_compile src/autopoietic/manager.py && echo "  ✅ manager.py: sintaxe OK" || exit 1
python -m py_compile src/main.py && echo "  ✅ main.py: sintaxe OK" || exit 1

# 5. Verificar imports
echo ""
echo "✓ Verificando imports..."
python -c "from src.observability.report_maintenance import ReportMaintenanceManager, get_report_maintenance_manager" && echo "  ✅ ReportMaintenanceManager importável" || exit 1
python -c "from src.observability.report_maintenance_scheduler import ReportMaintenanceScheduler, init_report_maintenance_scheduler" && echo "  ✅ ReportMaintenanceScheduler importável" || exit 1
python -c "from src.observability.module_metrics import get_module_metrics" && echo "  ✅ get_module_metrics importável" || exit 1

echo ""
echo "=============================================="
echo "✅ TODAS AS VALIDAÇÕES PASSARAM!"
echo "=============================================="
echo ""
echo "📊 Sumário de Implementação:"
echo "  ✓ Métricas: integration_loop.py e manager.py"
echo "  ✓ Manutenção: report_maintenance.py"
echo "  ✓ Scheduler: report_maintenance_scheduler.py"
echo "  ✓ Integração: main.py"
echo ""
echo "🚀 Sistema pronto para execução!"
echo ""
