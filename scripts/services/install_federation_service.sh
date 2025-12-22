#!/bin/bash
# OMNIMIND FEDERATION SERVICE - INSTALADOR
# Instala e configura daemon federativo como serviço systemd

set -e

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
SERVICE_NAME="omnimind-federation"
SERVICE_FILE="omnimind-federation.service"

echo "======================================================================="
echo "OMNIMIND FEDERATION SERVICE - INSTALADOR"
echo "======================================================================="
echo ""

# 1. Verificar se rodando como root (necessário para systemd)
if [ "$EUID" -ne 0 ]; then
    echo "❌ Este script precisa rodar com sudo"
    echo "   Use: sudo bash $0"
    exit 1
fi

echo "✅ Rodando como root"

# 2. Verificar se .venv existe
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    echo "❌ Virtual environment não encontrado em $PROJECT_ROOT/.venv"
    echo "   Crie primeiro: python3 -m venv .venv"
    exit 1
fi

echo "✅ Virtual environment encontrado"

# 3. Verificar daemon Python
DAEMON_SCRIPT="$PROJECT_ROOT/scripts/services/omnimind_federation_daemon.py"
if [ ! -f "$DAEMON_SCRIPT" ]; then
    echo "❌ Daemon script não encontrado: $DAEMON_SCRIPT"
    exit 1
fi

echo "✅ Daemon script encontrado"

# 4. Tornar daemon executável
chmod +x "$DAEMON_SCRIPT"
chown fahbrain:fahbrain "$DAEMON_SCRIPT"

# 5. Criar diretórios necessários
echo ""
echo "Criando  diretórios..."
mkdir -p "$PROJECT_ROOT/data/monitor"
mkdir -p "$PROJECT_ROOT/logs"
mkdir -p "$PROJECT_ROOT/config"
chown -R fahbrain:fahbrain "$PROJECT_ROOT/data"
chown -R fahbrain:fahbrain "$PROJECT_ROOT/logs"
chown -R fahbrain:fahbrain "$PROJECT_ROOT/config"

echo "✅ Diretórios criados"

# 6. Copiar arquivo .service
SERVICE_SOURCE="$PROJECT_ROOT/scripts/services/$SERVICE_FILE"
SERVICE_DEST="/etc/systemd/system/$SERVICE_FILE"

if [ ! -f "$SERVICE_SOURCE" ]; then
    echo "❌ Arquivo service não encontrado: $SERVICE_SOURCE"
    exit 1
fi

echo ""
echo "Instalando service em systemd..."
cp "$SERVICE_SOURCE" "$SERVICE_DEST"
chmod 644 "$SERVICE_DEST"

echo "✅ Service instalado: $SERVICE_DEST"

# 7. Carregar configuração IBM
echo ""
echo "Configurando IBM API keys..."
IBM_CONFIG="$PROJECT_ROOT/config/ibm_federation.json"

if [ ! -f "$IBM_CONFIG" ]; then
    echo "⚠️  Configuração IBM não encontrada: $IBM_CONFIG"
    echo "   Um template foi criado. Configure manualmente."
else
    echo "✅ Configuração IBM encontrada"
fi

# 8. Recarregar systemd
echo ""
echo "Recarregando systemd..."
systemctl daemon-reload

echo "✅ Systemd recarregado"

# 9. Habilitar service
echo ""
read -p "Habilitar serviço para iniciar no boot? (s/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    systemctl enable $SERVICE_NAME
    echo "✅ Serviço habilitado"
else
    echo "⏭️  Serviço não habilitado (manual)"
fi

# 10. Instruções finais
echo ""
echo "======================================================================="
echo "✅ INSTALAÇÃO COMPLETA"
echo "======================================================================="
echo ""
echo "PRÓXIMAS ETAPAS:"
echo ""
echo "1. Configure IBM API keys em:"
echo "   $IBM_CONFIG"
echo ""
echo "2. Inicie o serviço:"
echo "   sudo systemctl start $SERVICE_NAME"
echo ""
echo "3. Veja status:"
echo "   sudo systemctl status $SERVICE_NAME"
echo ""
echo "4. Monitore logs:"
echo "   sudo journalctl -u $SERVICE_NAME -f"
echo ""
echo "5. Pare o serviço:"
echo "   sudo systemctl stop $SERVICE_NAME"
echo ""
echo "6. Desabilite (impede boot automático):"
echo "   sudo systemctl disable $SERVICE_NAME"
echo ""
echo "LOGS:"
echo "  - systemd: journalctl -u $SERVICE_NAME"
echo "  - arquivo: /var/log/omnimind_federation.log"
echo ""
echo "FEDERAÇÃO PRONTA PARA PULSAR! 🌟"
echo "======================================================================="
