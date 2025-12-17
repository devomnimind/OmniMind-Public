#!/bin/bash
# Reorganização de Documentação - OmniMind
# Move documentos da raiz para docs/ e organiza estrutura

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "============================================================"
echo "📦 REORGANIZAÇÃO DE DOCUMENTAÇÃO"
echo "============================================================"
echo

# Criar diretórios necessários
mkdir -p docs/reports
mkdir -p docs/production
mkdir -p docs/archive/root_reports

# Mover documentos da raiz para docs/
echo "📄 Movendo documentos da raiz para docs/..."

# Phase reports → docs/reports/
if [ -f "PHASE_22_ANALYSIS_REPORT.md" ]; then
    mv "PHASE_22_ANALYSIS_REPORT.md" "docs/reports/"
    echo "  ✅ PHASE_22_ANALYSIS_REPORT.md → docs/reports/"
fi

# Production reports → docs/production/
if [ -f "PRODUCTION_STATUS_REPORT.md" ]; then
    mv "PRODUCTION_STATUS_REPORT.md" "docs/production/"
    echo "  ✅ PRODUCTION_STATUS_REPORT.md → docs/production/"
fi

if [ -f "VALIDATION_REPORT.md" ]; then
    mv "VALIDATION_REPORT.md" "docs/production/"
    echo "  ✅ VALIDATION_REPORT.md → docs/production/"
fi

# Changelog → docs/
if [ -f "CHANGELOG.md" ]; then
    mv "CHANGELOG.md" "docs/"
    echo "  ✅ CHANGELOG.md → docs/"
fi

# Config docs → docs/
if [ -f "PYLANCE_CONFIG.md" ]; then
    mv "PYLANCE_CONFIG.md" "docs/"
    echo "  ✅ PYLANCE_CONFIG.md → docs/"
fi

# Research/Philosophy docs → docs/
for file in antianthropocentric_consciousness.md \
            executive_summary_decision.md \
            feature_urgent.md \
            omnimind_deleuze_iit_framework.md \
            omnimind_implementation_code.md \
            scientific_gaps_critical\(1\).md \
            stimulation_interpretation_guide.md \
            theoretical_bridge_guide.md; do
    if [ -f "$file" ]; then
        mv "$file" "docs/"
        echo "  ✅ $file → docs/"
    fi
done

echo
echo "============================================================"
echo "✅ REORGANIZAÇÃO CONCLUÍDA"
echo "============================================================"

