#!/bin/bash
# 🎯 FASE 0: Validação de Mudanças (Phase-Aware Tolerance + Data Collection)
# Data: 2025-12-09
# Tempo: ~2-3 minutos

set -e

cd /home/fahbrain/projects/omnimind

echo "======================================================================"
echo "🔍 VALIDAÇÃO DE IMPLEMENTAÇÃO - FASE 0"
echo "======================================================================"
echo ""

# 1. Verificar mudanças no código
echo "1️⃣  Validando mudanças no código..."
echo ""

# Check 1: theoretical_consistency_guard.py - current_phase
if grep -q "current_phase: int = 6" src/consciousness/theoretical_consistency_guard.py; then
    echo "   ✅ theoretical_consistency_guard.__init__: current_phase adicionado"
else
    echo "   ❌ ERRO: current_phase não encontrado em __init__"
fi

# Check 2: theoretical_consistency_guard.py - phase parameter
if grep -q "phase: Optional\[int\] = None" src/consciousness/theoretical_consistency_guard.py; then
    echo "   ✅ validate_cycle: phase parameter adicionado"
else
    echo "   ❌ ERRO: phase parameter não encontrado"
fi

# Check 3: theoretical_consistency_guard.py - phase-aware logic
if grep -q "self.current_phase == 7" src/consciousness/theoretical_consistency_guard.py; then
    echo "   ✅ _get_dynamic_tolerance: logic phase-aware implementada"
else
    echo "   ❌ ERRO: phase-aware logic não encontrada"
fi

# Check 4: integration_loop.py - consistency_guard com current_phase=7
if grep -q "current_phase=7" src/consciousness/integration_loop.py; then
    echo "   ✅ integration_loop: consistency_guard inicializado com current_phase=7"
else
    echo "   ❌ ERRO: current_phase=7 não encontrado na inicialização"
fi

# Check 5: integration_loop.py - phase passado ao validate_cycle
if grep -q "phase=7," src/consciousness/integration_loop.py; then
    echo "   ✅ integration_loop: phase=7 passado ao validate_cycle"
else
    echo "   ❌ ERRO: phase=7 não passado ao validate_cycle"
fi

echo ""
echo "2️⃣  Validando coleta de dados..."
echo ""

# Check 6: run_200_cycles_production.py - 8 variáveis
if grep -q "bonding_quality_progression" scripts/run_200_cycles_production.py; then
    echo "   ✅ bonding_quality_progression agregada"
else
    echo "   ❌ ERRO: bonding_quality_progression não encontrada"
fi

if grep -q "delta_progression" scripts/run_200_cycles_production.py; then
    echo "   ✅ delta_progression agregada"
else
    echo "   ❌ ERRO: delta_progression não encontrada"
fi

if grep -q "error_delta_phi_progression" scripts/run_200_cycles_production.py; then
    echo "   ✅ error_delta_phi_progression agregada"
else
    echo "   ❌ ERRO: error_delta_phi_progression não encontrada"
fi

echo ""
echo "3️⃣  Compilação de sintaxe Python..."
echo ""

# Check 7: Sintaxe válida
python -m py_compile src/consciousness/theoretical_consistency_guard.py && echo "   ✅ theoretical_consistency_guard.py: sintaxe OK" || echo "   ❌ ERRO de sintaxe em theoretical_consistency_guard.py"
python -m py_compile src/consciousness/integration_loop.py && echo "   ✅ integration_loop.py: sintaxe OK" || echo "   ❌ ERRO de sintaxe em integration_loop.py"
python -m py_compile scripts/run_200_cycles_production.py && echo "   ✅ run_200_cycles_production.py: sintaxe OK" || echo "   ❌ ERRO de sintaxe em run_200_cycles_production.py"

echo ""
echo "======================================================================"
echo "✅ VALIDAÇÃO CONCLUÍDA"
echo "======================================================================"
echo ""
echo "📋 Próximos passos:"
echo "   1. Executar: python scripts/run_200_cycles_production.py"
echo "   2. Aguardar ~3 minutos"
echo "   3. Verificar: ls -la data/monitor/phi_200_cycles_production_metrics_*.json"
echo "   4. Confirmar que novo JSON contém as 8 variáveis"
echo ""
echo "🎯 Objetivo:"
echo "   • Reduzir warnings Δ-Φ de 80-100 para ~5-10 por 200 ciclos"
echo "   • Coletar dados para Soluções 4, 5, 6 (Phase 8+)"
echo ""
echo "======================================================================"
