# 🚀 Guia de Instalação Detalhada - OmniMind Systemd

**Data:** 23 de novembro de 2025
**Versão:** 1.0.0
**Status:** ✅ VALIDADO E IMUTÁVEL

---

## 📋 Pré-requisitos

### Sistema Operacional
- **Linux** com systemd (Ubuntu 20.04+, CentOS 8+, Debian 10+)
- **Kernel** 4.15+ (para Docker)
- **Arquitetura** x86_64 ou ARM64

### Dependências
```bash
# Docker 20.10+
docker --version

# Docker Compose v2.0+
docker-compose --version

# Git (para clone do repositório)
git --version

# Curl (para testes)
curl --version
```

### Recursos Mínimos
- **CPU:** 2 cores
- **RAM:** 4GB
- **Disco:** 20GB disponível
- **Rede:** Conexão internet para downloads

---

## 📦 Instalação das Dependências

### 1. Instalar Docker

```bash
# Remover versões antigas
sudo apt-get remove docker docker-engine docker.io containerd runc

# Atualizar repositório
sudo apt-get update

# Instalar dependências
sudo apt-get install ca-certificates curl gnupg lsb-release

# Adicionar chave GPG oficial do Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Adicionar repositório
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker Engine
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Verificar instalação
sudo docker run hello-world
```

### 2. Configurar Docker sem sudo

```bash
# Criar grupo docker
sudo groupadd docker

# Adicionar usuário ao grupo
sudo usermod -aG docker $USER

# Reiniciar sessão ou executar:
newgrp docker

# Verificar
docker run hello-world
```

### 3. Instalar Docker Compose (se necessário)

```bash
# Docker Compose v2 (incluído no docker-compose-plugin)
docker compose version

# Ou instalar v1 se necessário
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

---

## 📥 Clonagem e Configuração do Projeto

### 1. Clonar Repositório

```bash
# Clonar projeto
cd /home/fahbrain/projects
git clone <REPOSITORIO_OMNIMIND>
cd omnimind

# Verificar estrutura
ls -la
```

### 2. Configurar Ambiente Virtual Python

```bash
# Instalar pyenv (opcional mas recomendado)
curl https://pyenv.run | bash

# Adicionar ao ~/.bashrc
echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init --path)"' >> ~/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
source ~/.bashrc

# Instalar Python 3.12.8
pyenv install 3.12.8
pyenv local 3.12.8

# Criar ambiente virtual
python -m venv .venv
source .venv/bin/activate

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configurar Arquivo .env

```bash
# Copiar template
cp .env.template .env

# Editar variáveis necessárias
vim .env

# Variáveis mínimas obrigatórias:
OMNIMIND_DASHBOARD_USER=dashboard
OMNIMIND_DASHBOARD_PASS=omnimind
QDRANT_URL=http://qdrant:6333
REDIS_URL=redis://redis:6379
```

---

## 🔧 Instalação dos Serviços Systemd

### 1. Executar Instalação Automática

```bash
# Entrar no diretório do projeto
cd /home/fahbrain/projects/omnimind

# Executar script de instalação
./install/scripts/install_systemd.sh
```

**Saída esperada:**
```
🚀 Instalando OmniMind como serviços systemd...
📦 Instalando omnimind.service...
Created symlink /etc/systemd/system/multi-user.target.wants/omnimind.service → /etc/systemd/system/omnimind.service.
✅ omnimind.service instalado
📦 Instalando omnimind-backend.service...
✅ omnimind-backend.service instalado
📦 Instalando omnimind-frontend.service...
✅ omnimind-frontend.service instalado
📦 Instalando omnimind-mcp.service...
✅ omnimind-mcp.service instalado
📦 Instalando omnimind-qdrant.service...
✅ omnimind-qdrant.service instalado

🎯 Para iniciar o OmniMind:
  sudo systemctl start omnimind

📊 Para verificar status:
  sudo systemctl status omnimind

🔄 Para reiniciar após atualizações:
  sudo systemctl restart omnimind
```

### 2. Verificar Instalação

```bash
# Verificar arquivos instalados
ls -la /etc/systemd/system/omnimind-*

# Recarregar systemd
sudo systemctl daemon-reload

# Verificar status dos serviços
sudo systemctl list-units --type=service | grep omnimind
```

---

## 🚀 Inicialização dos Serviços

### Ordem Recomendada de Inicialização

```bash
# 1. Iniciar Qdrant (base de dados)
sudo systemctl start omnimind-qdrant

# 2. Iniciar Backend (API)
sudo systemctl start omnimind-backend

# 3. Iniciar Frontend (interface web)
sudo systemctl start omnimind-frontend

# 4. Iniciar MCP (servidores de contexto)
sudo systemctl start omnimind-mcp
```

### Inicialização Completa

```bash
# Iniciar todos os serviços de uma vez
sudo systemctl start omnimind-*

# Ou usar o serviço principal (se configurado)
sudo systemctl start omnimind
```

---

## ✅ Validação da Instalação

### 1. Verificar Status dos Serviços

```bash
# Status completo
sudo systemctl status omnimind-*

# Status específico
sudo systemctl status omnimind-backend --no-pager
```

**Status esperado:**
```
● omnimind-backend.service - OmniMind Backend API
     Loaded: loaded (/etc/systemd/system/omnimind-backend.service; enabled; vendor preset: disabled)
     Active: active (running) since Sun 2025-11-23 09:12:48 -03; 5s ago
   Main PID: 164768 (docker-compose)
      Tasks: 11 (limit: 28227)
     Memory: 13.4M
        CPU: 68ms
     CGroup: /system.slice/omnimind-backend.service
```

### 2. Verificar Containers Docker

```bash
# Listar containers OmniMind
docker ps | grep deploy-

# Saída esperada:
# deploy-qdrant-1     qdrant/qdrant:latest   "./entrypoint.sh"   2 minutes ago   Up 2 minutes   0.0.0.0:6333->6333/tcp
# deploy-backend-1    omnimind-backend       "uvicorn web.b..."  2 minutes ago   Up 2 minutes   0.0.0.0:8000->8000/tcp
# deploy-frontend-1   omnimind-frontend      "/docker-entryp..." 2 minutes ago   Up 2 minutes   0.0.0.0:3000->80/tcp
```

### 3. Testar Endpoints

```bash
# Testar Qdrant
curl http://localhost:6333/collections

# Testar Backend
curl http://localhost:8000/health

# Testar Frontend
curl -I http://localhost:3000
```

### 4. Executar Validação Completa

```bash
# Executar script de validação
./install/validation/validate_installation.sh
```

---

## 🔧 Configuração Avançada

### 1. Configurar Reinício Automático

```bash
# Verificar configuração atual
sudo systemctl show omnimind-backend --property=Restart

# Modificar política de reinício (se necessário)
sudo vim /etc/systemd/system/omnimind-backend.service

# Adicionar ou modificar:
# Restart=on-failure
# RestartSec=5
# StartLimitIntervalSec=300
# StartLimitBurst=3

# Recarregar e reiniciar
sudo systemctl daemon-reload
sudo systemctl restart omnimind-backend
```

### 2. Configurar Limites de Recursos

```bash
# Verificar limites atuais
sudo systemctl show omnimind-backend --property=MemoryLimit

# Adicionar limites no arquivo .service
sudo vim /etc/systemd/system/omnimind-backend.service

# Adicionar:
# MemoryLimit=1G
# CPUQuota=50%

# Recarregar
sudo systemctl daemon-reload
sudo systemctl restart omnimind-backend
```

### 3. Configurar Logs

```bash
# Verificar logs
sudo journalctl -u omnimind-backend --no-pager -n 50

# Configurar rotação de logs
sudo vim /etc/systemd/journald.conf

# Modificar:
# SystemMaxUse=100M
# SystemMaxFileSize=10M

# Reiniciar journald
sudo systemctl restart systemd-journald
```

---

## 🔄 Atualização do Sistema

### Procedimento de Atualização

```bash
# 1. Parar serviços
sudo systemctl stop omnimind-*

# 2. Fazer backup (se necessário)
# docker-compose -f deploy/docker-compose.yml exec qdrant backup

# 3. Atualizar código
git pull origin main

# 4. Reconstruir imagens (se Dockerfile mudou)
docker-compose -f deploy/docker-compose.yml build

# 5. Reiniciar serviços
sudo systemctl start omnimind-*

# 6. Verificar funcionamento
./install/validation/validate_installation.sh
```

---

## 🆘 Recuperação de Desastres

### Reset Completo

```bash
# PARAR TUDO
sudo systemctl stop omnimind-*
docker stop $(docker ps -q --filter "name=deploy-")

# LIMPAR
docker-compose -f deploy/docker-compose.yml down -v
docker system prune -f
sudo systemctl disable omnimind-*

# REMOVER ARQUIVOS DE SERVIÇO
sudo rm /etc/systemd/system/omnimind-*.service
sudo systemctl daemon-reload

# REINSTALAR
./install/scripts/install_systemd.sh
sudo systemctl start omnimind-*

# VALIDAR
./install/validation/validate_installation.sh
```

---

## 📊 Monitoramento Contínuo

### Configurar Monitoramento Automático

```bash
# Instalar scripts de monitoramento
chmod +x install/validation/*.sh

# Executar monitoramento contínuo
./install/validation/monitor_services.sh

# Ou configurar cron para verificações periódicas
crontab -e

# Adicionar:
# */5 * * * * /home/fahbrain/projects/omnimind/install/validation/validate_installation.sh
# * * * * * /home/fahbrain/projects/omnimind/install/validation/health_check.sh
```

---

## 🔒 Configurações de Segurança

### 1. Configurar Firewall

```bash
# Instalar ufw
sudo apt install ufw

# Permitir apenas portas necessárias
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 3000/tcp  # Frontend
sudo ufw allow 8000/tcp  # Backend
sudo ufw allow 6333/tcp  # Qdrant

# Habilitar firewall
sudo ufw enable
```

### 2. Configurar SELinux/AppArmor

```bash
# Verificar status
sudo apparmor_status

# Se necessário, configurar políticas para Docker
sudo vim /etc/apparmor.d/docker

# Reiniciar AppArmor
sudo systemctl restart apparmor
```

### 3. Configurar Usuário Dedicado

```bash
# Criar usuário omnimind
sudo useradd -r -s /bin/false omnimind

# Modificar arquivos .service para usar este usuário
sudo vim /etc/systemd/system/omnimind-backend.service
# User=omnimind

# Ajustar permissões
sudo chown -R omnimind:omnimind /home/fahbrain/projects/omnimind
```

---

## 📞 Suporte e Troubleshooting

Para problemas durante a instalação:

1. **Verificar logs de instalação:** `install/logs/installation.log`
2. **Consultar troubleshooting:** `install/docs/TROUBLESHOOTING.md`
3. **Executar validação:** `./install/validation/validate_installation.sh`
4. **Verificar documentação:** `install/docs/`

### Informações para Suporte

```bash
# Coletar informações do sistema
uname -a
docker --version
docker-compose --version
systemctl --version

# Status dos serviços
sudo systemctl status omnimind-*

# Logs recentes
sudo journalctl -u omnimind-backend --no-pager -n 20

# Configuração de rede
ip addr show
sudo netstat -tlnp | grep -E ':(3000|8000|6333)'
```

---

**✅ GUIA DE INSTALAÇÃO COMPLETO E DETALHADO**