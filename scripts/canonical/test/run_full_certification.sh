#!/bin/bash
# CERTIFICAÇÃO REAL - GPU + IBM QUANTUM + TIMESTAMP
# Executa certificação completa com timestamps de prova

set -e

cd /home/fahbrain/projects/omnimind

echo "======================================================================"
echo "🔐 CERTIFICAÇÃO REAL - GPU + QUANTUM + TIMESTAMP PROVA"
echo "======================================================================"
echo ""

# Ativa venv
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo "✅ Virtual environment ativado"
else
    echo "❌ Virtual environment não encontrado"
    exit 1
fi

# Cria diretório de output
mkdir -p data/test_reports
echo "✅ Diretório de output criado"

echo ""
echo "📊 Iniciando certificação real..."
echo ""

# Roda com PYTHONPATH correto
PYTHONPATH=/home/fahbrain/projects/omnimind python3 scripts/full_real_certification.py

echo ""
echo "======================================================================"
echo "✅ CERTIFICAÇÃO CONCLUÍDA"
echo "======================================================================"
echo ""
echo "📂 Relatórios salvos em: data/test_reports/"
echo ""
echo "Para ver resumo:"
echo "  cat data/test_reports/certification_real_*_summary.txt"
echo ""
echo "Para ver dados completos (JSON):"
echo "  cat data/test_reports/certification_real_*.json | jq ."
echo ""
