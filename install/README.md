# 🚀 OmniMind Systemd Installation Guide
## Guia Completo de Instalação e Configuração

**Data:** 23 de novembro de 2025
**Versão:** 1.0.0
**Status:** ✅ VALIDADO E IMUTÁVEL

---

## 📋 Visão Geral

Este guia documenta o processo completo de instalação e configuração dos serviços OmniMind via systemd. Todos os arquivos nesta pasta são **imutáveis e validados** após extensivos testes de produção.

### 🎯 Objetivos Alcançados

- ✅ **Transição Completa para Systemd**: Todos os serviços gerenciados pelo systemd
- ✅ **Isolamento em Containers**: Cada serviço roda em container Docker dedicado
- ✅ **Monitoramento Automático**: Reinício automático e logs centralizados
- ✅ **Dependências Resolvidas**: Ordem correta de inicialização
- ✅ **Validação Funcional**: Todos os endpoints testados e operacionais

---

## 📁 Estrutura da Pasta

```
install/
├── scripts/           # Scripts de instalação executáveis
│   ├── install_systemd.sh
│   └── start_mcp_servers.sh
├── systemd/           # Arquivos de serviço systemd
│   ├── omnimind-backend.service
│   ├── omnimind-frontend.service
│   ├── omnimind-mcp.service
│   └── omnimind-qdrant.service
├── docs/              # Documentação completa
│   ├── INSTALLATION.md
│   ├── TROUBLESHOOTING.md
│   ├── VALIDATION.md
│   └── PROCESSES.md
├── logs/              # Logs de instalação e testes
└── validation/        # Scripts de validação
```

---

## ⚡ Instalação Rápida

### Pré-requisitos

```bash
# Docker e Docker Compose instalados
docker --version
docker-compose --version

# Permissões sudo para instalação de serviços
sudo -v
```

### Comando de Instalação

```bash
cd /home/fahbrain/projects/omnimind

# Executar instalação completa
./install/scripts/install_systemd.sh

# Verificar status
sudo systemctl status omnimind-*
```

### Verificação Final

```bash
# Testar endpoints
curl http://localhost:8000/health
curl http://localhost:3000
curl http://localhost:6333/collections

# Verificar logs
sudo journalctl -u omnimind-backend --no-pager -n 10
```

---

## 🔧 Serviços Instalados

### 1. OmniMind Qdrant (Base de Dados Vetorial)
- **Arquivo:** `systemd/omnimind-qdrant.service`
- **Porta:** 6333
- **Dependências:** Nenhuma
- **Status:** ✅ Validado

### 2. OmniMind Backend (API FastAPI)
- **Arquivo:** `systemd/omnimind-backend.service`
- **Porta:** 8000
- **Dependências:** qdrant, redis
- **Status:** ✅ Validado

### 3. OmniMind Frontend (Dashboard React)
- **Arquivo:** `systemd/omnimind-frontend.service`
- **Porta:** 3000
- **Dependências:** backend
- **Status:** ✅ Validado

### 4. OmniMind MCP (Model Context Protocol)
- **Arquivo:** `systemd/omnimind-mcp.service`
- **Porta:** Dinâmica
- **Dependências:** Nenhuma
- **Status:** ✅ Validado

---

## 📊 Status de Produção

| Serviço | Status | Porta | Endpoint | Validação |
|---------|--------|-------|----------|-----------|
| Qdrant | ✅ Active | 6333 | `/collections` | OK |
| Backend | ✅ Active | 8000 | `/health` | OK |
| Frontend | ✅ Active | 3000 | `/` | OK |
| MCP | ✅ Active | - | - | OK |

---

## 🚨 Troubleshooting

Para problemas comuns, consulte:
- `docs/TROUBLESHOOTING.md` - Problemas frequentes e soluções
- `docs/PROCESSES.md` - Detalhes dos processos de instalação
- `logs/installation.log` - Log completo da instalação

### Comandos Úteis

```bash
# Reiniciar todos os serviços
sudo systemctl restart omnimind-*

# Ver logs em tempo real
sudo journalctl -u omnimind-backend -f

# Parar todos os serviços
sudo systemctl stop omnimind-*

# Verificar uso de portas
sudo netstat -tlnp | grep -E ':(3000|8000|6333)'
```

---

## 🔒 Segurança

- Todos os serviços rodam como usuário `root` (configurado para produção)
- Logs centralizados no journald do systemd
- Reinício automático em caso de falha
- Isolamento completo em containers Docker

---

## 📈 Monitoramento

### Métricas Principais

- **CPU/Memória:** Monitorados pelo systemd
- **Logs:** Centralizados no journalctl
- **Health Checks:** Endpoints dedicados
- **Reinícios:** Automáticos com backoff

### Comandos de Monitoramento

```bash
# Status completo
sudo systemctl status omnimind-*

# Uso de recursos
sudo systemctl show omnimind-backend --property=CPUUsageNS,MemoryCurrent

# Logs dos últimos 100 linhas
sudo journalctl -u omnimind-backend --no-pager -n 100
```

---

## 🔄 Atualizações

**IMPORTANTE:** Esta instalação é **imutável**. Para atualizações:

1. Pare todos os serviços
2. Atualize o código fonte
3. Reinicie os serviços
4. Valide funcionalidade

```bash
sudo systemctl stop omnimind-*
# ... atualizar código ...
sudo systemctl start omnimind-*
```

---

## 📞 Suporte

Para suporte técnico:
- Verificar logs: `sudo journalctl -u omnimind-* --no-pager`
- Validar endpoints: Scripts em `validation/`
- Documentação completa: `docs/`

---

**✅ INSTALAÇÃO VALIDADA E PRONTA PARA PRODUÇÃO**