# 📋 ÍNDICE DE SCRIPTS INSTALAÇÃO SYSTEM OS + DEPENDÊNCIAS
**Data**: 16 de Dezembro de 2025
**Status**: 🟢 Auditado e Consolidado

---

## 📌 RESUMO EXECUTIVO

Três scripts **entrypoint** principais gerenciam a inicialização do OmniMind:

| Script | Localização | Propósito | Status |
|--------|------------|----------|--------|
| **install_systemd_services** | `scripts/canonical/install/` | ❌ DEPRECATED | Referencia novo script |
| **setup_security_privileges** | `scripts/canonical/install/` | 🟢 ATIVO | Instala sudoers |
| **start_omnimind_system_robust** | `scripts/canonical/system/` | 🟢 RECOMENDADO | Inicialização robusta v2.0 |

---

## 🔴 SCRIPT 1: install_systemd_services.sh

**Status**: ❌ **DEPRECATED (NÃO USE)**

**Localização**:
```
scripts/canonical/install/install_systemd_services.sh
```

**O que faz**:
- ❌ Tentava instalar o serviço systemd `omnimind-backend.service` (OLD)
- ❌ Criava conflitos com `omnimind.service` (novo)
- ❌ Import paths desatualizadas

**Por que deprecated**:
```
❌ omnimind-backend.service foi removido
❌ Substituído por omnimind.service (único, correto)
❌ Code ainda referencia paths desatualizados
```

**Substituição (USE ISTO)**:
```bash
scripts/systemd/install_all_services.sh
```

**Referência**: Sim, existe
```
✅ scripts/systemd/install_all_services.sh (NOVO - USE ESTE)
```

**O que fazer**:
```bash
# ❌ NÃO USE ISTO:
./scripts/canonical/install/install_systemd_services.sh

# ✅ USE ISTO:
./scripts/systemd/install_all_services.sh
```

---

## 🟢 SCRIPT 2: setup_security_privileges.sh

**Status**: 🟢 **ATIVO E FUNCIONAL**

**Localização**:
```
scripts/canonical/install/setup_security_privileges.sh
```

**O que faz**:
1. ✅ Valida arquivo sudoers em `config/sudoers.d/omnimind`
2. ✅ Instala em `/etc/sudoers.d/omnimind`
3. ✅ Define permissões (0440)
4. ✅ Concede NOPASSWD para:
   - Network monitoring (tc, iptables, ss, netstat)
   - Process monitoring (pgrep, ps, pkill)
   - System audit (auditctl, ausearch)
   - Log monitoring (tail, journalctl)
   - Service management (systemctl para omnimind-* ONLY)

**Uso Correto**:
```bash
sudo ./scripts/canonical/install/setup_security_privileges.sh
```

**Valida**:
- ✅ Arquivo sudoers em `config/sudoers.d/omnimind`
- ✅ Sintaxe está correta
- ✅ Perms: 0440

**Output esperado**:
```
✅ Sudoers configuration is valid
✅ OmniMind security privileges installed successfully!
```

**Onde se registra**:
- Sistema: `/etc/sudoers.d/omnimind`
- Logs: `/var/log/auth.log` (sistema)
- OmniMind: `logs/security_validation.jsonl`

**Verificar após instalação**:
```bash
sudo -l -U fahbrain | grep -A 20 NOPASSWD
```

**Dependências de arquivo**:
- **Lê**: `config/sudoers.d/omnimind`
- **Escreve**: `/etc/sudoers.d/omnimind` (requer sudo)
- **Valida**: Usa `visudo -cf` (verificação nativa do sistema)

---

## 🟢 SCRIPT 3: start_omnimind_system_robust.sh (RECOMENDADO)

**Status**: 🟢 **ATIVO - VERSÃO ROBUSTA v2.0**

**Localização**:
```
scripts/canonical/system/start_omnimind_system_robust.sh
```

**O que faz**:
Inicialização completa do OmniMind com 4 fases de validação:

### Fase 1: Verificação de Serviços Existentes
```bash
# Verifica se ports 8000, 8080, 3001 já têm processos
# Se sim: decide se precisa restart
# Se não: prepara para iniciar novo cluster
```

### Fase 1.5: Inicializar Backend Cluster
```bash
# Chama run_cluster.sh (executa 3 backends em paralelo)
# Ports: 8000 (Primary), 8080 (Secondary), 3001 (Fallback)
# Cada backend: 2 workers Uvicorn
```

### Fase 2: Health Check Essenciais (até 300s)
```bash
# Aguarda backend 8000 estar healthy
# Verifica 8080, 3001 (não-crítico se falharem)
# Retry logic: up to 100 tentativas para porta 8000
```

### Fase 2.5: Estabilização de CPU
```bash
# Espera 60s para carregamento de modelos
# Verifica CPU < 50% (ou timeout após 30s)
```

### Fase 3: Serviços Secundários
```bash
# Inicia MCP Orchestrator
# Inicia Main Cycle
# Inicia Frontend (React)
```

### Fase 4: Monitoramento
```bash
# Inicia Observer Service
# Inicia eBPF Monitor (se disponível)
```

**Uso Correto**:
```bash
./scripts/canonical/system/start_omnimind_system_robust.sh
```

**Dependências de Scripts** (Chama):
```
1. scripts/canonical/system/run_cluster.sh (EXECUTA 3 BACKENDS)
   └─ Inicia: Primary (8000), Secondary (8080), Fallback (3001)

2. scripts/canonical/system/run_mcp_orchestrator.py (PYTHON)
   └─ Orquestrador MCP para agentes

3. scripts/canonical/system/run_observer_service.py (PYTHON)
   └─ Serviço de observabilidade/monitoring
```

**Dependências de Arquivos** (Lê/Escreve):
```
✅ Lê:
   - config/omnimind.yaml
   - .env
   - config/dashboard_auth.json
   - Credenciais ambiente

✅ Escreve:
   - logs/startup_detailed.log (principal)
   - logs/backend_8000.log
   - logs/backend_8080.log
   - logs/backend_3001.log
   - logs/mcp_orchestrator.log
   - logs/observer_service.log
   - logs/main_cycle.log
   - logs/frontend.log
   - data/monitor/
   - data/autopoietic/synthesized_code/

✅ Cria diretórios:
   - logs/
   - data/autopoietic/synthesized_code/
   - data/monitor/
```

**Variáveis de Ambiente**:
```bash
# GPU Configuration
CUDA_HOME="/usr"
CUDA_path="/usr"
LD_LIBRARY_PATH="/usr/lib/x86_64-linux-gnu"
CUDA_VISIBLE_DEVICES="0"
PYTORCH_CUDA_ALLOC_CONF="backend:cudaMallocAsync"

# Controle de inicialização
OMNIMIND_PROJECT_ROOT (opcional)
OMNIMIND_DEBUG (opcional, default: false)
OMNIMIND_AUTO_RECOVERY (opcional, default: true)
```

**Output esperado**:
```
🚀 Iniciando Sistema OmniMind Completo (Versão Robusta v2.0)...
════ FASE 1: Verificação de Serviços Existentes ════
════ FASE 1.5: Inicialização Backend Cluster ════
════ FASE 2: Health Check Essenciais ════
════ FASE 2.5: Estabilização de CPU ════
════ FASE 3: Inicialização Serviços Secundários ════
════ FASE 4: Monitoramento e Observabilidade ════
✨ Sistema OmniMind Inicializado (Versão Robusta v2.0)
```

**Health Checks Validados**:
- ✅ Backend Primary (8000): essential mode, 100 retries, 5s timeout
- ✅ Backend Secondary (8080): secondary mode, 30 retries, 5s timeout
- ✅ Backend Fallback (3001): fallback mode, 50 retries, 10s timeout
- ✅ CPU stability check: < 50%
- ✅ Response time monitoring

---

## 🔗 DEPENDÊNCIAS E CHAMADAS

### start_omnimind_system_robust.sh → run_cluster.sh

**Caminho**:
```
scripts/canonical/system/start_omnimind_system_robust.sh
    ↓
    chmod +x "$PROJECT_ROOT/scripts/canonical/system/run_cluster.sh"
    ↓
scripts/canonical/system/run_cluster.sh
```

**O que run_cluster.sh faz**:
1. ✅ Mata processos antigos (pkill python web/backend/main.py)
2. ✅ Configura PYTHONPATH
3. ✅ Inicia 3 backends em paralelo via nohup:
   - `uvicorn web.backend.main:app --port 8000` (Primary)
   - `uvicorn web.backend.main:app --port 8080` (Secondary)
   - `uvicorn web.backend.main:app --port 3001` (Fallback)
4. ✅ Salva PIDs em `logs/backend_XXXX.pid`
5. ✅ Logs em `logs/backend_XXXX.log`

**Variáveis configuráveis**:
```bash
OMNIMIND_WORKERS=2          # workers por backend (default)
OMNIMIND_BACKENDS=3         # quantos backends (default)
OMNIMIND_WORKERS_VALIDATION=2  # durante validação científica
```

---

### start_omnimind_system_robust.sh → run_mcp_orchestrator.py

**Caminho**:
```
scripts/canonical/system/start_omnimind_system_robust.sh
    ↓
if ! pgrep -f "run_mcp_orchestrator.py" > /dev/null; then
    nohup python "$PROJECT_ROOT/scripts/canonical/system/run_mcp_orchestrator.py" > "$PROJECT_ROOT/logs/mcp_orchestrator.log" 2>&1 &
```

**O que faz** (assumido, arquivo Python):
- ✅ Orquestra MCPs (Model Context Protocol)
- ✅ Gerencia agentes de IA
- ✅ Log: `logs/mcp_orchestrator.log`

**Status**: ✅ Arquivo existe
```
scripts/canonical/system/run_mcp_orchestrator.py
```

---

### start_omnimind_system_robust.sh → run_observer_service.py

**Caminho**:
```
scripts/canonical/system/start_omnimind_system_robust.sh
    ↓
if ! pgrep -f "run_observer_service.py" > /dev/null; then
    nohup python "$PROJECT_ROOT/scripts/canonical/system/run_observer_service.py" > "$PROJECT_ROOT/logs/observer_service.log" 2>&1 &
```

**O que faz** (assumido, arquivo Python):
- ✅ Observabilidade do sistema
- ✅ Coleta de métricas
- ✅ Log: `logs/observer_service.log`

**Status**: ✅ Arquivo existe
```
scripts/canonical/system/run_observer_service.py
```

---

## 📊 MAPA DE DEPENDÊNCIAS VISUAL

```
start_omnimind_system_robust.sh (MAIN ENTRY POINT)
│
├─ Fase 0: Setup (variáveis de ambiente, PROJECT_ROOT)
│
├─ Fase 1.5: Backend Cluster
│   └─ run_cluster.sh
│       ├─ Backend Primary (uvicorn port 8000)
│       ├─ Backend Secondary (uvicorn port 8080)
│       └─ Backend Fallback (uvicorn port 3001)
│
├─ Fase 2: Health Checks
│   ├─ unified_health_check(8000, essential)
│   ├─ unified_health_check(8080, secondary)
│   └─ unified_health_check(3001, fallback)
│
├─ Fase 2.5: CPU Stabilization
│   └─ check_cpu_stable()
│
├─ Fase 3: Secondary Services
│   ├─ run_mcp_orchestrator.py
│   ├─ run_main_cycle.py (não documentado, assumido)
│   └─ React Frontend (se existe web/frontend)
│
└─ Fase 4: Monitoring
    ├─ run_observer_service.py
    └─ eBPF Monitor (se bpftrace disponível)
```

---

## 🛠️ FLUXO DE USO RECOMENDADO

### 1️⃣ Setup Inicial (Uma vez)
```bash
# Instalar serviços systemd (Redis, PostgreSQL, Qdrant)
./scripts/systemd/install_all_services.sh

# Instalar sudoers para segurança
sudo ./scripts/canonical/install/setup_security_privileges.sh

# Verificar instalação
sudo -l -U fahbrain | grep NOPASSWD
```

### 2️⃣ Iniciar Sistema OmniMind
```bash
# Iniciar com todas as fases
./scripts/canonical/system/start_omnimind_system_robust.sh

# Verificar se tudo subiu
curl http://localhost:8000/health/
curl http://localhost:3000/  # Frontend
```

### 3️⃣ Monitoramento
```bash
# Ver logs detalhados
tail -f logs/startup_detailed.log

# Verificar backends
ps aux | grep uvicorn | grep -v grep

# Verificar MCP Orchestrator
pgrep -f "run_mcp_orchestrator.py"

# Verificar Observer
pgrep -f "run_observer_service.py"
```

---

## ⚠️ PROBLEMAS COMUNS

### Problema 1: Port 8000 já em uso
```bash
# Solução
lsof -i :8000
kill -9 <PID>

# Ou deixar run_cluster.sh limpara (pkill faz isto)
./scripts/canonical/system/run_cluster.sh
```

### Problema 2: Backend não fica healthy
```bash
# Verificar logs
tail -f logs/backend_8000.log

# Problemas possíveis:
# - GPU não disponível
# - Modelo não carregado
# - Port em uso
# - Import error no código
```

### Problema 3: MCP Orchestrator não inicia
```bash
# Verificar se já está rodando
pgrep -f "run_mcp_orchestrator.py"

# Verificar logs
tail -f logs/mcp_orchestrator.log

# Verificar se arquivo existe
ls -la scripts/canonical/system/run_mcp_orchestrator.py
```

---

## 📝 CHECKLIST DE SETUP COMPLETO

- [ ] 1. System databases instalados: `./scripts/systemd/install_all_services.sh`
- [ ] 2. Redis verificado: `redis-cli ping`
- [ ] 3. PostgreSQL verificado: `psql -U postgres -c "SELECT 1"`
- [ ] 4. Qdrant verificado: `curl http://localhost:6333/health`
- [ ] 5. Sudoers instalado: `sudo ./scripts/canonical/install/setup_security_privileges.sh`
- [ ] 6. GPU disponível: `nvidia-smi`
- [ ] 7. Python 3.12.12 em .venv: `python --version`
- [ ] 8. Requirements instalados: `pip list | grep qiskit`
- [ ] 9. Sistema inicializado: `./scripts/canonical/system/start_omnimind_system_robust.sh`
- [ ] 10. Backends health: `curl http://localhost:8000/health/`

---

**Última Atualização**: 16 de Dezembro de 2025
**Status**: 🟢 Todos os scripts auditados e documentados
