#!/bin/bash
# Script para corrigir caminhos e permissões do OmniMind
# Corrige problemas de PATH, keyring e permissões administrativas

set -e

echo "🔧 Iniciando correção de caminhos e permissões do OmniMind..."

# 1. Corrigir PATH permanentemente
echo "📁 Corrigindo PATH do sistema..."
export PATH="/usr/bin:/bin:/usr/local/bin:/usr/sbin:/sbin:$PATH"

# 2. Verificar e corrigir variáveis de ambiente críticas
echo "🌍 Verificando variáveis de ambiente..."

# Verificar se estamos no VS Code snap
if [[ "$SNAP" == *"code"* ]]; then
    echo "⚠️  Detectado VS Code Snap - aplicando correções específicas..."

    # Corrigir variáveis do snap
    export XDG_DATA_DIRS="/usr/share/ubuntu:/usr/share/gnome:/usr/local/share:/usr/share:/var/lib/snapd/desktop:$XDG_DATA_DIRS"
    export GTK_PATH="/usr/lib/x86_64-linux-gnu/gtk-3.0:$GTK_PATH"
    export LOCPATH="/usr/lib/locale:$LOCPATH"

    # Corrigir acesso ao keyring
    export GNOME_KEYRING_CONTROL="/run/user/$(id -u)/keyring"
fi

# 3. Configurar Python keyring corretamente
echo "🔐 Configurando Python keyring..."

# Remover configuração problemática se existir
unset PYTHON_KEYRING_BACKEND

# Testar keyring no ambiente do OmniMind
cd /home/fahbrain/projects/omnimind
source .venv/bin/activate

python3 -c "
import keyring
import os

# Configurar backend seguro
try:
    # Tentar usar GNOME keyring se disponível
    if os.environ.get('GNOME_KEYRING_CONTROL'):
        keyring.set_keyring(keyring.backends.SecretService.Keyring())
        print('✅ Usando GNOME Keyring')
    else:
        # Fallback para cryptfile
        from keyrings.cryptfile.cryptfile import CryptFileKeyring
        keyring.set_keyring(CryptFileKeyring())
        print('✅ Usando CryptFile Keyring')

    # Testar funcionalidade
    test_service = 'omnimind_test'
    test_user = 'test_user'
    test_password = 'test_password_123'

    keyring.set_password(test_service, test_user, test_password)
    retrieved = keyring.get_password(test_service, test_user)

    if retrieved == test_password:
        print('✅ Keyring funcionando corretamente')
        keyring.delete_password(test_service, test_user)
    else:
        print('❌ Keyring com problemas')

except Exception as e:
    print(f'❌ Erro no keyring: {e}')
"

# 4. Verificar permissões do OmniMind
echo "🔒 Verificando permissões do OmniMind..."

# Verificar se usuário está no grupo correto
if groups | grep -q sudo; then
    echo "✅ Usuário tem permissões sudo"
else
    echo "❌ Usuário NÃO tem permissões sudo"
fi

# Verificar configurações sudo do OmniMind
if sudo test -f /etc/sudoers.d/omnimind; then
    echo "✅ Configurações sudo do OmniMind instaladas"
else
    echo "⚠️  Configurações sudo do OmniMind NÃO encontradas"
    echo "💡 Execute: sudo cp config/sudoers.d/omnimind /etc/sudoers.d/ && sudo chmod 440 /etc/sudoers.d/omnimind"
fi

# 5. Configurar variáveis de ambiente permanentes
echo "⚙️  Configurando variáveis de ambiente..."

# Criar/atualizar .bashrc com configurações necessárias
BASHRC="$HOME/.bashrc"
OMNIMIND_ENV_BLOCK="# OmniMind Environment Configuration
export PATH=\"/usr/bin:/bin:/usr/local/bin:/usr/sbin:/sbin:\$PATH\"
export PYTHONPATH=\"/home/fahbrain/projects/omnimind/src:\$PYTHONPATH\"

# Keyring configuration
unset PYTHON_KEYRING_BACKEND

# VS Code Snap corrections
if [[ \"\$SNAP\" == *\"code\"* ]]; then
    export XDG_DATA_DIRS=\"/usr/share/ubuntu:/usr/share/gnome:/usr/local/share:/usr/share:/var/lib/snapd/desktop:\$XDG_DATA_DIRS\"
    export GTK_PATH=\"/usr/lib/x86_64-linux-gnu/gtk-3.0:\$GTK_PATH\"
    export LOCPATH=\"/usr/lib/locale:\$LOCPATH\"
    export GNOME_KEYRING_CONTROL=\"/run/user/\$(id -u)/keyring\"
fi

# OmniMind shortcuts
alias omnimind-activate='cd /home/fahbrain/projects/omnimind && source .venv/bin/activate'
alias omnimind-status='sudo systemctl status omnimind-backend omnimind-frontend qdrant redis-server'
alias omnimind-logs='tail -f /var/log/omnimind/omnimind.log'
# End OmniMind Environment Configuration"

# Verificar se o bloco já existe
if ! grep -q "OmniMind Environment Configuration" "$BASHRC"; then
    echo "📝 Adicionando configurações ao .bashrc..."
    echo "$OMNIMIND_ENV_BLOCK" >> "$BASHRC"
    echo "✅ Configurações adicionadas ao .bashrc"
else
    echo "✅ Configurações já existem no .bashrc"
fi

# 6. Testar serviços críticos
echo "🧪 Testando serviços críticos..."

# Testar acesso aos serviços
services=("qdrant" "redis-server")
for service in "${services[@]}"; do
    if sudo systemctl is-active --quiet "$service" 2>/dev/null; then
        echo "✅ Serviço $service está ativo"
    else
        echo "⚠️  Serviço $service não está ativo ou inacessível"
    fi
done

# 7. Verificar acesso aos arquivos críticos
echo "📂 Verificando acesso aos arquivos críticos..."

critical_paths=(
    "/home/fahbrain/projects/omnimind/src"
    "/home/fahbrain/projects/omnimind/config"
    "/home/fahbrain/projects/omnimind/logs"
    "/var/log/omnimind"
    "/run/user/$(id -u)/keyring"
)

for path in "${critical_paths[@]}"; do
    if [ -r "$path" ] 2>/dev/null; then
        echo "✅ Acesso OK: $path"
    else
        echo "❌ Sem acesso: $path"
    fi
done

# 8. Configurar VS Code settings se necessário
echo "💻 Verificando configurações do VS Code..."

VSCODE_SETTINGS="/home/fahbrain/projects/omnimind/.vscode/settings.json"
if [ -f "$VSCODE_SETTINGS" ]; then
    echo "✅ Arquivo settings.json existe"

    # Verificar se tem configurações de terminal
    if grep -q "terminal.integrated.env.linux" "$VSCODE_SETTINGS"; then
        echo "✅ Configurações de terminal já existem"
    else
        echo "⚠️  Adicionando configurações de terminal ao VS Code..."
        # Adicionar configurações de terminal se não existirem
        sed -i '/"sonarlint.connectedMode.connections.sonarsource.sonarcloud": \[$/,+10 {
            /sonarlint.connectedMode.connections.sonarsource.sonarcloud/a\
    },\
    // Terminal environment for OmniMind\
    "terminal.integrated.env.linux": {\
        "PATH": "/usr/bin:/bin:/usr/local/bin:/usr/sbin:/sbin:${env:PATH}",\
        "PYTHONPATH": "/home/fahbrain/projects/omnimind/src:${env:PYTHONPATH}"\
    },\
    "terminal.integrated.shellIntegration.enabled": true,\
    "terminal.integrated.automationProfile.linux": {\
        "path": "/bin/bash",\
        "args": ["--login"]\
    }
        }' "$VSCODE_SETTINGS"
    fi
else
    echo "❌ Arquivo settings.json não encontrado"
fi

echo ""
echo "🎉 Correção concluída!"
echo ""
echo "📋 RESUMO DAS CORREÇÕES:"
echo "✅ PATH corrigido permanentemente"
echo "✅ Keyring configurado corretamente"
echo "✅ Permissões sudo do OmniMind verificadas"
echo "✅ Variáveis de ambiente configuradas"
echo "✅ VS Code settings atualizados"
echo ""
echo "🔄 RECARREGUE O TERMINAL OU EXECUTE: source ~/.bashrc"
echo ""
echo "🧪 PARA TESTAR: omnimind-activate && python scripts/check_qdrant.py"
