#!/bin/bash
# ============================================================================
# LOCK CORE PROTOCOL - OMNIMIND KERNEL PROTECTION
# ============================================================================
# Purpose: Apply Immutable Bit (+i) to critical scientific axioms of the system.
# Safety:  Prevents accidental deletion or modification by agents/users unless
#          explicitly unlocked with sudo.
# ============================================================================

set -e

echo "🔒 INICIANDO PROTOCOLO DE CONGELAMENTO KERNEL (CHATTR +i)..."

# Lista de Arquivos Canônicos (Axiomas de Verdade)
declare -a CORE_FILES=(
    "docs/canonical/OMNIMIND_TRUTH_INDEX_IMMUTABLE.md"
    "src/consciousness/qualia_engine.py"
    "src/consciousness/hybrid_topological_engine.py"
    "tests/test_do_calculus.py"
    "src/autopoietic/sandbox.py"
    "src/quantum/integration.py"
)

# 1. Verificar se rodando como sudo
if [ "$EUID" -ne 0 ]; then
  echo "❌ Erro: Este script precisa de privilégios de root para alterar atributos de kernel."
  echo "   Execute com: sudo ./scripts/security/lock_core_kernel.sh"
  exit 1
fi

# 2. Aplicar Lock
for file in "${CORE_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   -> Travando: $file"
        chattr +i "$file"
    else
        echo "⚠️  Alerta: Arquivo não encontrado: $file"
    fi
done

echo "✅ PROTOCOLO CONCLUÍDO. O Núcleo de Verdade está selado."
echo "   Para editar estes arquivos no futuro, use 'chattr -i <arquivo>'."
