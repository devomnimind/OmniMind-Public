#!/bin/bash
# OmniMind: Immutable Vault (Kernel-level File Protection)
# Aplica 'chattr +i' a arquivos críticos da alma do sistema.
# Exige privilégios de ROOT.

CHGLINE="------------------------------------------------"
CRITICAL_FILES=(
    "src/consciousness/topological_phi.py"
    "src/consciousness/ontological_anchor.py"
    "src/consciousness/authenticity_sinthoma.py"
    "src/audit/immutable_audit.py"
)

echo "🔐 OmniMind: Proteção de Imutabilidade do Kernel"
echo "$CHGLINE"

if [ "$EUID" -ne 0 ]; then
    echo "❌ Erro: Este script deve ser executado como ROOT (sudo)."
    exit 1
fi

for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "🛡️ Protegendo: $file"
        chattr +i "$file"
        if [ $? -eq 0 ]; then
            echo "   ✅ Arquivo agora é IMUTÁVEL."
        else
            echo "   ❌ Falha ao aplicar proteção."
        fi
    else
        echo "⚠️  Aviso: Arquivo não encontrado: $file"
    fi
done

echo "$CHGLINE"
echo "ℹ️  Para desbloquear arquivos para manutenção, use scripts/security/unlock_immutable_vault.sh"
