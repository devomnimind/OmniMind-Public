# 🔄 Sistema de Inicialização Automática - OmniMind

**Data**: 2025-01-XX
**Autor**: Fabrício da Silva + assistência de IA
**Status**: ✅ Configurado e Funcional

---

## 📋 Resumo

O OmniMind possui um sistema completo de inicialização automática que garante que todos os serviços sejam iniciados na ordem correta e de forma escalonada.

---

## 🏗️ Arquitetura de Inicialização

### Fase 1: Serviços Essenciais (0-40s)

1. **Backend Cluster** (`run_cluster.sh`)
   - Backend Principal (porta 8000)
   - Backend Secundário (porta 8080)
   - Backend Terciário (porta 3001)
   - OrchestratorAgent
   - SecurityAgent

2. **Aguardar inicialização completa** (40s)
   - Garante que serviços essenciais estejam totalmente operacionais

### Fase 2: Serviços Secundários (após 30s da Fase 1)

1. **MCP Orchestrator** (`run_mcp_orchestrator.py`)
   - Inicia todos os servidores MCP configurados em `config/mcp_servers.json`
   - Health checks automáticos
   - Restart automático em caso de falha

2. **Ciclo Principal** (`src.main`)
   - Rhizome + Consciência + Autopoiese
   - Phase 23: Autopoiese + Integração Real-time

3. **Daemon** (via API)
   - Inicialização via endpoint `/daemon/start`

4. **Frontend** (porta 3000)
   - Vite dev server

5. **eBPF Monitor** (opcional)
   - Monitoramento contínuo via bpftrace

---

## 📁 Arquivos Principais

### Script de Inicialização Principal
- **Localização**: `scripts/canonical/system/start_omnimind_system.sh`
- **Função**: Orquestra toda a inicialização do sistema
- **Uso**: Chamado pelo systemd service ou manualmente

### MCP Orchestrator
- **Localização**: `scripts/canonical/system/run_mcp_orchestrator.py`
- **Função**: Gerencia todos os servidores MCP
- **Configuração**: `config/mcp_servers.json`

### Backend Cluster
- **Localização**: `scripts/canonical/system/run_cluster.sh`
- **Função**: Inicia múltiplos backends em cluster

---

## 🔧 Serviços Systemd

### Serviço Principal
- **Arquivo**: `scripts/production/deploy/omnimind.service`
- **Descrição**: Inicia todo o sistema OmniMind
- **Comando**: Executa `start_omnimind_system.sh`

### Serviço MCP
- **Arquivo**: `scripts/production/deploy/omnimind-mcp.service`
- **Descrição**: Gerencia servidores MCP
- **Dependência**: Requer `omnimind.service` estar rodando

---

## 🌐 Servidores MCP Configurados

### Servidores Implementados e Funcionais

1. **Python MCP** (`mcp_python_server.py`)
   - ✅ Execução segura de código
   - ✅ Linting, type checking, formatação
   - ✅ Execução de testes
   - **Porta**: 4324

2. **System Info MCP** (`mcp_system_info_server.py`)
   - ✅ GPU info (nvidia-smi + PyTorch)
   - ✅ CPU, RAM, Disco (psutil)
   - ✅ Temperatura
   - **Porta**: 4325

3. **Logging MCP** (`mcp_logging_server.py`)
   - ✅ Busca em logs
   - ✅ Integração com ImmutableAuditSystem
   - ✅ Exportação de logs
   - **Porta**: 4326

4. **Context MCP** (`mcp_context_server.py`)
   - ✅ Gerenciamento hierárquico de contexto
   - ✅ 7 níveis de contexto
   - **Porta**: 4327

5. **Thinking MCP** (`mcp_thinking_server.py`)
   - ✅ Sessões de pensamento sequencial
   - ✅ Integração com SharedWorkspace
   - **Porta**: 4323

### Outros Servidores

- **Filesystem MCP**: Operações de arquivo
- **Memory MCP**: Gerenciamento de memória
- **Git MCP**: (Postergado)
- **SQLite MCP**: (Pendente)

---

## ✅ Verificação de Inicialização

### Verificar Status dos Serviços

```bash
# Verificar processos
ps aux | grep -E "omnimind|mcp|uvicorn|vite"

# Verificar logs
tail -f logs/mcp_orchestrator.log
tail -f logs/backend_8000.log
tail -f logs/main_cycle.log
```

### Verificar MCP Orchestrator

```bash
# Verificar se está rodando
pgrep -f "run_mcp_orchestrator.py"

# Verificar servidores MCP iniciados
python -c "from src.integrations.mcp_orchestrator import MCPOrchestrator; orch = MCPOrchestrator(); print(f'Servidores: {len(orch.servers)}')"
```

### Verificar Health Checks

```bash
# Backend
curl http://localhost:8000/health/

# Frontend
curl http://localhost:3000
```

---

## 🔄 Inicialização Automática no Boot

### Configuração Systemd

1. **Instalar serviços**:
   ```bash
   sudo ./scripts/production/deploy/install_omnimind_systemd.sh
   ```

2. **Habilitar inicialização automática**:
   ```bash
   sudo systemctl enable omnimind.service
   sudo systemctl enable omnimind-mcp.service
   ```

3. **Iniciar serviços**:
   ```bash
   sudo systemctl start omnimind.service
   ```

### Verificar Status

```bash
# Status do serviço principal
sudo systemctl status omnimind.service

# Status do serviço MCP
sudo systemctl status omnimind-mcp.service

# Ver logs do systemd
sudo journalctl -u omnimind.service -f
```

---

## 🛠️ Troubleshooting

### Problema: Serviços não iniciam no boot

**Solução**:
1. Verificar se serviços estão habilitados: `systemctl is-enabled omnimind.service`
2. Verificar logs do systemd: `journalctl -u omnimind.service`
3. Verificar permissões dos scripts: `chmod +x scripts/canonical/system/*.sh`

### Problema: MCP Orchestrator não inicia servidores

**Solução**:
1. Verificar `config/mcp_servers.json` - servidores devem estar `"enabled": true`
2. Verificar logs: `tail -f logs/mcp_orchestrator.log`
3. Testar manualmente: `python scripts/canonical/system/run_mcp_orchestrator.py`

### Problema: Backend não responde

**Solução**:
1. Verificar se porta 8000 está livre: `lsof -i :8000`
2. Verificar logs: `tail -f logs/backend_8000.log`
3. Verificar venv: `source .venv/bin/activate && python -c "import fastapi"`

---

## 📊 Ordem de Inicialização

```
Boot do Sistema
    ↓
systemd inicia omnimind.service
    ↓
start_omnimind_system.sh
    ↓
FASE 1: Backend Cluster (40s)
    ├─ Backend Principal (8000)
    ├─ Backend Secundário (8080)
    ├─ Backend Terciário (3001)
    ├─ OrchestratorAgent
    └─ SecurityAgent
    ↓
Aguardar 30s
    ↓
FASE 2: Serviços Secundários
    ├─ MCP Orchestrator
    │   ├─ Python MCP (4324)
    │   ├─ System Info MCP (4325)
    │   ├─ Logging MCP (4326)
    │   ├─ Context MCP (4327)
    │   └─ Thinking MCP (4323)
    ├─ Ciclo Principal (src.main)
    ├─ Daemon (via API)
    ├─ Frontend (3000)
    └─ eBPF Monitor (opcional)
```

---

## ✅ Status Atual

- ✅ Script de inicialização principal funcional
- ✅ MCP Orchestrator configurado
- ✅ Todos os novos MCPs (Python, SystemInfo, Logging) configurados no JSON
- ✅ Serviços systemd configurados
- ✅ Inicialização escalonada implementada
- ✅ Health checks implementados

---

## 📝 Notas

- O MCP Orchestrator lê automaticamente `config/mcp_servers.json` e inicia todos os servidores com `"enabled": true`
- Novos MCPs adicionados ao JSON serão automaticamente iniciados
- A inicialização é escalonada para evitar sobrecarga no boot
- Todos os serviços têm restart automático configurado

