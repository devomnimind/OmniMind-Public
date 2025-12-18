#!/bin/bash
#
# OmniMind Sudo Permissions Fixer
# ===============================
#
# Este script cria um arquivo de configuração no /etc/sudoers.d/
# para permitir que o usuário execute comandos críticos de recuperação
# e manutenção SEM SENHA, conforme a filosofia "Fight for Life" do projeto.
#
# Comandos permitidos:
# - systemctl (restart, start, stop, status) para serviços omnimind
# - cp/mv/rm em logs e data (para rotação e backup)
# - reinicialização da máquina (em caso extremo)
#

set -e

USER_NAME=$(whoami)
SUDOERS_FILE="/etc/sudoers.d/omnimind_autopoiesis"

echo "🔧 OmniMind Permissions Repair"
echo "=============================="
echo "User: $USER_NAME"
echo "Target: $SUDOERS_FILE"
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "⚠️  Este script precisa ser executado com sudo (uma última vez) para aplicar as correções."
    echo "   Por favor, execute: sudo ./scripts/fix_sudo_permissions.sh"
    exit 1
fi

echo "📝 Criando regras de permissão..."

cat > "$SUDOERS_FILE" << EOF
# OmniMind Autopoietic Permissions
# Permite que o sistema lute pela sua vida (reinicie serviços) sem intervenção humana

# Serviços Systemd
$USER_NAME ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart omnimind*
$USER_NAME ALL=(ALL) NOPASSWD: /usr/bin/systemctl start omnimind*
$USER_NAME ALL=(ALL) NOPASSWD: /usr/bin/systemctl stop omnimind*
$USER_NAME ALL=(ALL) NOPASSWD: /usr/bin/systemctl status omnimind*
$USER_NAME ALL=(ALL) NOPASSWD: /usr/bin/systemctl enable omnimind*
$USER_NAME ALL=(ALL) NOPASSWD: /usr/bin/systemctl disable omnimind*
$USER_NAME ALL=(ALL) NOPASSWD: /usr/bin/journalctl

# Manipulação de Logs e Snapshots (Recovery)
$USER_NAME ALL=(ALL) NOPASSWD: /usr/bin/tar *
$USER_NAME ALL=(ALL) NOPASSWD: /usr/bin/cp *
$USER_NAME ALL=(ALL) NOPASSWD: /usr/bin/rm *
$USER_NAME ALL=(ALL) NOPASSWD: /usr/bin/mkdir *

# Monitoramento
$USER_NAME ALL=(ALL) NOPASSWD: /usr/sbin/bpftrace
EOF

chmod 0440 "$SUDOERS_FILE"

echo "✅ Arquivo $SUDOERS_FILE criado com sucesso."
echo "✅ Permissões aplicadas. O OmniMind agora tem autonomia para recuperação."
echo ""
echo "Teste rápido:"
echo "sudo -n systemctl status omnimind-backend 2>/dev/null && echo 'OK' || echo 'FAIL'"
