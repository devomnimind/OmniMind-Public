# 🔍 AUDITORIA: 3 Scripts Instalação + Dependências (16 DEC 2025)

## 📌 RESUMO EXECUTIVO

Você tem **3 scripts principais** para inicializar o OmniMind em Sistema OS. Aqui está o que cada um faz e o que eles chamam.

---

## 🔴 SCRIPT 1: `install_systemd_services.sh`

**Status**: ❌ **DEPRECATED (NÃO USE)**
**Localização**: `scripts/canonical/install/install_systemd_services.sh`

### O Que Faz?
- Tentava instalar `omnimind-backend.service` (versão OLD)
- Criava conflito com `omnimind.service` (novo)

### Por Que Não Usar?
```
❌ Serviço foi removido
❌ Substituído por omnimind.service
❌ Paths desatualizadas
```

### Usar em Vez?
```bash
✅ ./scripts/systemd/install_all_services.sh
```

---

## 🟢 SCRIPT 2: `setup_security_privileges.sh`

**Status**: 🟢 **ATIVO E FUNCIONAL**
**Localização**: `scripts/canonical/install/setup_security_privileges.sh`

### O Que Faz?
1. Valida arquivo sudoers em `config/sudoers.d/omnimind`
2. Instala em `/etc/sudoers.d/omnimind`
3. Define perms 0440
4. Concede NOPASSWD para:
   - Network monitoring (`tc`, `iptables`, `ss`, `netstat`)
   - Process monitoring (`pgrep`, `ps`, `pkill`)
   - System audit (`auditctl`, `ausearch`)
   - Log monitoring (`tail`, `journalctl`)
   - Service control (systemctl para omnimind-* ONLY)

### Como Usar?
```bash
sudo ./scripts/canonical/install/setup_security_privileges.sh
```

### Verificar?
```bash
sudo -l -U fahbrain | grep -A 20 NOPASSWD
```

### Dependências de Arquivo
- **Lê**: `config/sudoers.d/omnimind`
- **Escreve**: `/etc/sudoers.d/omnimind` (requer sudo)
- **Valida**: Usa `visudo -cf` (sistema)

---

## 🟢 SCRIPT 3: `start_omnimind_system_robust.sh` ⭐ **RECOMENDADO**

**Status**: 🟢 **VERSÃO ROBUSTA v2.0**
**Localização**: `scripts/canonical/system/start_omnimind_system_robust.sh`

### O Que Faz?

Inicialização completa com 4 fases:

#### **Fase 1: Check Serviços Existentes**
- Verifica se ports 8000, 8080, 3001 já têm processos
- Decide se precisa restart

#### **Fase 1.5: Backend Cluster**
Chama → **`run_cluster.sh`**
```bash
$ scripts/canonical/system/run_cluster.sh
├─ Inicia: Primary (8000) - 2 workers Uvicorn
├─ Inicia: Secondary (8080) - 2 workers Uvicorn
└─ Inicia: Fallback (3001) - 2 workers Uvicorn
```

#### **Fase 2: Health Checks** (até 300s)
- Aguarda backend 8000 estar healthy
- 100 retries para porta 8000
- 30 retries para porta 8080
- 50 retries para porta 3001

#### **Fase 2.5: CPU Stabilization**
- Espera 60s para carregar modelos
- Verifica CPU < 50%

#### **Fase 3: Serviços Secundários**
Chama → **`run_mcp_orchestrator.py`**
```bash
$ scripts/canonical/system/run_mcp_orchestrator.py
└─ Orquestra MCPs (agents)
```

Chama → **`run_observer_service.py`**
```bash
$ scripts/canonical/system/run_observer_service.py
└─ Observabilidade do sistema
```

Inicia → **React Frontend** (se existe em `web/frontend`)

#### **Fase 4: Monitoring**
- Inicia Observer Service
- Inicia eBPF Monitor (se bpftrace disponível)

### Como Usar?
```bash
./scripts/canonical/system/start_omnimind_system_robust.sh
```

### Dependências de Scripts (Chama)
```
1. run_cluster.sh
   └─ 3 Uvicorn backends em paralelo

2. run_mcp_orchestrator.py
   └─ MCP Agent Orchestration

3. run_observer_service.py
   └─ System Monitoring
```

### Lê Arquivos
- `config/omnimind.yaml`
- `.env`
- `config/dashboard_auth.json`

### Escreve Logs
- `logs/startup_detailed.log` (principal)
- `logs/backend_8000.log`
- `logs/backend_8080.log`
- `logs/backend_3001.log`
- `logs/mcp_orchestrator.log`
- `logs/observer_service.log`
- `logs/main_cycle.log`
- `logs/frontend.log`

---

## 🗺️ MAPA VISUAL DE DEPENDÊNCIAS

```
┌─ start_omnimind_system_robust.sh (ENTRY POINT) ⭐
│
├─→ Phase 1.5: run_cluster.sh
│   ├─ Port 8000 (Primary) → logs/backend_8000.log
│   ├─ Port 8080 (Secondary) → logs/backend_8080.log
│   └─ Port 3001 (Fallback) → logs/backend_3001.log
│
├─→ Phase 3: run_mcp_orchestrator.py
│   └─ MCP Agent Orchestration → logs/mcp_orchestrator.log
│
├─→ Phase 3: run_observer_service.py
│   └─ System Monitoring → logs/observer_service.log
│
└─→ Phase 3: React Frontend (se existe)
    └─ http://localhost:3000
```

---

## ⏱️ TEMPO TOTAL

**~5-10 minutos** para inicialização completa

---

## ✅ CHECKLIST DE SETUP COMPLETO

```bash
# 1. Python 3.12.12
python --version

# 2. venv ativado
source .venv/bin/activate

# 3. GPU Stack instalado
pip list | grep qiskit  # 1.2.4
pip list | grep aer-gpu # 0.15.1

# 4. System databases
redis-cli ping  # PONG
curl http://localhost:6333/health  # 200

# 5. Segurança
sudo -l -U fahbrain | grep NOPASSWD

# 6. Inicializar sistema
./scripts/canonical/system/start_omnimind_system_robust.sh

# 7. Verificar
curl http://localhost:8000/health/  # 200
curl http://localhost:3000/          # 200
```

---

## 🔗 PRÓXIMAS ETAPAS

1. **Se ainda não instalou databases** → Execute:
   ```bash
   ./scripts/systemd/install_all_services.sh
   ```

2. **Se precisa segurança** → Execute:
   ```bash
   sudo ./scripts/canonical/install/setup_security_privileges.sh
   ```

3. **Para inicializar o sistema** → Execute:
   ```bash
   ./scripts/canonical/system/start_omnimind_system_robust.sh
   ```

---

## 📚 DOCUMENTAÇÃO COMPLETA

Para documentação detalhada (com tabelas e problemas comuns):

📖 **[scripts/INDEX_SCRIPTS_INSTALLED_DEPS.md](scripts/INDEX_SCRIPTS_INSTALLED_DEPS.md)**

---

## ✨ TL;DR (Resumo em 1 minuto)

| Script | Status | Uso | O Que Faz |
|--------|--------|-----|-----------|
| `install_systemd_services.sh` | ❌ DEPRECATED | ❌ NÃO USE | Conflita com novo serviço |
| `setup_security_privileges.sh` | 🟢 ATIVO | `sudo ./script` | Instala `/etc/sudoers.d/omnimind` |
| `start_omnimind_system_robust.sh` | 🟢 RECOMENDADO | `./script` | **Inicia tudo (3 backends + services)** |

**Fluxo**: Setup Segurança → Iniciar Sistema → Verificar Health

**Tempo**: ~5-10 minutos total

---

**Criado**: 16 de Dezembro de 2025
**Status**: ✅ Todos os 3 scripts auditados e mapeados
