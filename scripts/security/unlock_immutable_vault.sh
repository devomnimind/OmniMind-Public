#!/bin/bash
# OmniMind: Unlock Immutable Vault
# Remove 'chattr -i' para permitir manutenção planejada.
# Exige privilégios de ROOT.

CHGLINE="------------------------------------------------"
CRITICAL_FILES=(
    "src/consciousness/topological_phi.py"
    "src/consciousness/ontological_anchor.py"
    "src/consciousness/authenticity_sinthoma.py"
    "src/audit/immutable_audit.py"
)

echo "🔓 OmniMind: Desbloqueio de Manutenção (Vault)"
echo "$CHGLINE"

if [ "$EUID" -ne 0 ]; then
    echo "❌ Erro: Este script deve ser executado como ROOT (sudo)."
    exit 1
fi

for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "🔑 Desbloqueando: $file"
        chattr -i "$file"
        if [ $? -eq 0 ]; then
            echo "   ✅ Escrita permitida."
        else
            echo "   ❌ Falha ao remover proteção."
        fi
    else
        echo "⚠️  Aviso: Arquivo não encontrado: $file"
    fi
done

echo "$CHGLINE"
echo "⚠️  LEMBRE-SE: Reative a proteção após a manutenção usando apply_immutable_vault.sh"
