#!/bin/bash

# ============================================================================
# 🔐 CONFIGURE SUDO FOR OMNIMIND AUTOMATION
# ============================================================================
# Adiciona entrada sudoers para rodar scripts sem pedir senha
# USO: bash scripts/configure_sudo_omnimind.sh
# ============================================================================

set -e

echo "🔐 Configurando sudo para OmniMind..."
echo ""

# Detectar usuário atual
CURRENT_USER=$(whoami)
PROJECT_ROOT=$(cd "$(dirname "$0")/.." && pwd)
SCRIPTS_DIR="$PROJECT_ROOT/scripts"

echo "📋 Informações:"
echo "   Usuário: $CURRENT_USER"
echo "   Projeto: $PROJECT_ROOT"
echo "   Scripts: $SCRIPTS_DIR"
echo ""

# Arquivo de configuração sudoers
SUDOERS_FILE="/etc/sudoers.d/omnimind-automation"

# Conteúdo que será adicionado
SUDOERS_CONTENT="# OmniMind Automation - Permite rodar scripts sem pedir senha
$CURRENT_USER ALL=(ALL) NOPASSWD: $SCRIPTS_DIR/start_omnimind_system_sudo.sh
$CURRENT_USER ALL=(ALL) NOPASSWD: $SCRIPTS_DIR/canonical/system/start_omnimind_system.sh
$CURRENT_USER ALL=(ALL) NOPASSWD: $SCRIPTS_DIR/canonical/system/run_cluster.sh
$CURRENT_USER ALL=(ALL) NOPASSWD: /usr/bin/bpftrace
$CURRENT_USER ALL=(ALL) NOPASSWD: /usr/bin/pkill
$CURRENT_USER ALL=(ALL) NOPASSWD: /bin/bash -E"

echo "📝 Será adicionado ao sudoers:"
echo "$SUDOERS_CONTENT"
echo ""

# Pedir confirmação
read -p "Deseja continuar? (S/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "❌ Cancelado"
    exit 1
fi

# Adicionar ao sudoers usando visudo para validação
echo "$SUDOERS_CONTENT" | sudo tee "$SUDOERS_FILE" > /dev/null

# Validar sintaxe sudoers
sudo visudo -c -f "$SUDOERS_FILE"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Configuração sudoers adicionada com sucesso!"
    echo "   Arquivo: $SUDOERS_FILE"
    echo ""
    echo "🧪 Teste agora:"
    echo "   sudo -n bash scripts/start_omnimind_system_sudo.sh"
    echo ""
    echo "   Se não pedir senha, está pronto!"
else
    echo "❌ Erro na sintaxe sudoers"
    exit 1
fi
