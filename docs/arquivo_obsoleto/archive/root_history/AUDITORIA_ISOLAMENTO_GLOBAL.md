# 🔍 AUDITORIA GLOBAL DE ISOLAMENTO - Sandbox/Namespaces

**Data:** 17 de dezembro de 2025
**Status:** 🚨 CRÍTICO - Auditoria em progresso
**Objetivo:** Mapear TODAS as chamadas de código dinâmico que precisam de isolamento

## 1. Varredura de Execução Dinâmica - ENCONTRADO

### Código Dinâmico ATIVO (Precisa Isolamento):

#### 🔴 ALTA PRIORIDADE - Autopoiesis (Já sendo isolado)
- **Arquivo:** `src/autopoietic/sandbox.py`
- **Método:** `AutopoieticSandbox.execute_component()`
- **Status:** ✅ IMPLEMENTADO com unshare
- **Isolamento:** `--pid --ipc --uts --net` + resource limits
- **Resultado:** Rastreado com `isolation` field

#### 🟡 MÉDIA PRIORIDADE - Subprocess Diretos (Não isolados)
1. **Arquivo:** `scripts/indexing/vectorize_omnimind.py`
   - **Linha:** 557, 564
   - **Tipo:** `subprocess.run()` com `shell=True`
   - **Uso:** Comando do sistema (NDArray loading)
   - **Risco:** Alto (shell=True)
   - **Ação:** Converter para isolado

2. **Arquivo:** `scripts/monitoring/monitor.py`
   - **Linha:** 93
   - **Tipo:** `subprocess.run()`
   - **Uso:** Monitoramento de sistema
   - **Risco:** Médio
   - **Ação:** Permitido (sistema, não dinâmico)

3. **Arquivo:** `scripts/monitoring/monitor_control.py`
   - **Linha:** 36
   - **Tipo:** `subprocess.Popen()`
   - **Uso:** Controle de processos
   - **Risco:** Médio
   - **Ação:** Permitido (sistema, não dinâmico)

4. **Arquivo:** `web/backend/main.py`
   - **Linha:** 1342 (comentário)
   - **Uso:** "would need sandboxing/validation"
   - **Status:** TODO comentado
   - **Ação:** Identificar e isolante

#### 🟠 ATENÇÃO - LLM/Chat Dinâmico (Backend)
- **Arquivo:** `web/backend/main.py`
- **Tipo:** Chat API que poderia gerar código
- **Status:** Precisa de validação
- **Ação:** Revisar fluxo de geração de prompts

### Scripts de Teste (Simulação)
- **Arquivo:** `scripts/development/run_sinthome_simulation.py`
- **Tipo:** Automação de frontend (browser)
- **Risco:** Baixo (UI, não execução)
- **Ação:** Monitorar

## 2. Sudoers INCORRETO - Necessário Revisar

### Atual (Incompleto):
```sudoers
fahbrain ALL=(ALL) NOPASSWD: /usr/bin/systemd-run *
fahbrain ALL=(ALL) NOPASSWD: /usr/bin/systemd-nspawn *
fahbrain ALL=(ALL) NOPASSWD: /bin/bash -c *
```

### Problemas:
1. ❌ Falta regras para gerenciamento de processos sandbox
2. ❌ Falta regras para monitoramento de redis/postgresql
3. ❌ `bash -c *` é MUITO permissivo (qualquer comando)
4. ❌ Falta proteção para `pkill` - pode matar processos do usuário!
5. ❌ Falta regras específicas para `unshare`

### Necessário:
```sudoers
# 🛡️ ISOLAMENTO DE PROCESSO
fahbrain ALL=(ALL) NOPASSWD: /usr/bin/unshare *
fahbrain ALL=(ALL) NOPASSWD: /usr/bin/systemd-run *
fahbrain ALL=(ALL) NOPASSWD: /usr/bin/systemd-nspawn *

# 🔒 COMANDO RESTRITO (apenas sandbox cleanup)
# Processa apenas dentro de /tmp/autopoiesis_sandbox_* ou cgroup omnimind
fahbrain ALL=(ALL) NOPASSWD: /bin/bash -c "pkill -9 -f 'unshare.*python3' 2>/dev/null || true"

# 📊 MONITORAMENTO SEGURO (read-only)
fahbrain ALL=(ALL) NOPASSWD: /usr/bin/systemctl status redis-server
fahbrain ALL=(ALL) NOPASSWD: /usr/bin/systemctl status postgresql
fahbrain ALL=(ALL) NOPASSWD: /usr/bin/journalctl -u omnimind.service
fahbrain ALL=(ALL) NOPASSWD: /bin/ps aux

# ⏹️ RESTART SEGURO (apenas omnimind services)
fahbrain ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart omnimind*.service

# 🚫 EXPLÍCITO - NÃO PERMITIDO
# (reboot, shutdown, kill -9 de processos do usuário, etc)
```

## 3. Arquitetura de Isolamento GLOBAL Recomendada

### Camadas de Segurança:

```
USUÁRIO (fahbrain)
    ↓
[REQUEST] → FastAPI Backend
    ↓
[DYNAMIC CODE?]
    ├─→ SIM: Enviar para AutopoieticSandbox
    │        ↓
    │        unshare --pid --ipc --uts --net
    │        ↓
    │        Resource limits (100MB, 30s)
    │        ↓
    │        Execute component.run()
    │        ↓
    │        [Resultado isolado] ← seguro retornar ao backend
    │
    └─→ NÃO: Executar direto (é sistema confiável)
```

### Tipos de Código:

**DEVE SER ISOLADO:**
- ✅ Código gerado por CodeSynthesizer
- ✅ Código LLM gerado dinamicamente
- ✅ Scripts de autopoiesis
- ✅ Eval/exec de prompts
- ✅ Cualquer subprocess.run() com shell=True

**PODE EXECUTAR DIRETO:**
- ✅ Scripts sys.path validados (scripts/canonical/)
- ✅ Imports de src/
- ✅ Chamadas a serviços conhecidos (redis, postgresql)
- ✅ Monitoramento/logging

## 4. Proteção de Processos do Usuário

### Problema:
```bash
# ❌ ERRADO - Pode matar seu próprio processo
sudo pkill -9 -f "python3"  # Mata TUDO que roda python3!
```

### Solução com Cgroups:

```bash
# 1. Criar cgroup omnimind
sudo cgcreate -g cpuacct,memory:omnimind/sandbox

# 2. Executar componentes via cgroup
sudo cgexec -g cpuacct,memory:omnimind/sandbox \
  unshare --pid --ipc --uts --net \
  python3 component.py

# 3. Matar APENAS sandbox (nunca o usuário)
sudo pkill -9 --cgroup omnimind/sandbox
```

### Sudoers com proteção:

```sudoers
# 🛡️ Allowed: Kill ONLY omnimind sandbox processes
fahbrain ALL=(ALL) NOPASSWD: /bin/bash -c "pkill -9 --cgroup omnimind/sandbox"

# 🚫 NOT allowed (commented out, would fail):
# fahbrain ALL=(ALL) NOPASSWD: /bin/pkill *
```

## 5. Restart Automático

### Atual (Não existe):
```
⚠️ Sem recovery automático quando sobrecarga
```

### Recomendado:

```bash
# systemd-tmpfiles para restart automático
systemctl restart omnimind.service

# Recovery script com validações
/bin/bash -c '
  if [ $(free -m | awk "NR==2{print 100-$NF/1024}")>90 ]; then
    echo "🚨 Memory >90%, restarting...";
    systemctl restart omnimind.service
  fi
'
```

### Systemd Unit com restart policy:
```ini
[Service]
Restart=on-failure
RestartSec=5
StartLimitInterval=60
StartLimitBurst=3
```
## 6. Memory Management com Swap (8GB dedicado)

### Problema Original:
- Limite de RAM apenas: 512MB (muito restritivo)
- Componentes autopoiéticos ficavam limitados
- Swap de 24GB não estava sendo usado
- Loop infinito não conseguia alocar suficiente

### Solução Implementada (Definitiva):
```ini
[Scope]
MemoryLimit=8G              # Total: RAM + Swap combinados
MemorySwapLimit=8G          # Permite usar swap quando RAM acaba
CPUQuota=50%                # CPU ainda limitada
TasksMax=infinity           # Sem limite de tasks dentro do cgroup
```

### Como Funciona:
1. **Primeira alocação**: Usa RAM do sistema (rápido)
2. **RAM cheia**: Sistema move para swap automaticamente (mais lento, OK)
3. **8GB atingido**: Processo é **encerrado** (protege máquina)
4. **Isolação**: Nunca afeta RAM do usuário Fabrício

### Performance:
- RAM allocation: ~1-100 microsegundos
- Swap allocation: ~1-10 milisegundos (mais lento, aceitável para autopoiesis)
- Trade-off: **Funcionalidade > Velocidade** (para processamento em loop)

### Monitoramento em Tempo Real:
```bash
# Ver uso atual
systemctl show omnimind-sandbox.scope -p MemoryCurrent

# Ver limite
systemctl show omnimind-sandbox.scope -p MemoryLimit

# Watch contínuo
watch 'systemctl show omnimind-sandbox.scope | grep Memory'

# Logs de OOM kill
sudo journalctl -f | grep MemoryMax
```

### Proteção do Sistema:
- ✅ Cgroup omnimind-sandbox isolado
- ✅ **1GB RAM máximo** + **7GB Swap máximo** = 8GB total
- ✅ Não afeta outros serviços
- ✅ Swap não é problema (24GB disponível)
- ✅ Autopoiesis pode rodar em loop indefinido

### Integração com Systemd (Automática):
```bash
# Slice com limites
/etc/systemd/system/omnimind-sandbox.slice
[Slice]
MemoryMax=1G
MemorySwapMax=7G
CPUQuota=50%

# Service vinculado ao slice
/etc/systemd/system/omnimind.service.d/sandbox.conf
[Service]
Slice=omnimind-sandbox.slice
MemoryAccounting=yes

# Resultado: omnimind.service sempre roda com limites automaticamente
# Quando: sudo systemctl start omnimind.service
# Como: Herda limites do slice omnimind-sandbox.slice
```

### Ativação:
```bash
# Aplicar limites ao serviço
sudo systemctl restart omnimind.service

# Verificar
sudo systemctl show omnimind.service --property=Slice
systemctl show omnimind-sandbox.slice --property=MemoryMax
```
## 6. Checklist de Implementação

### FASE 1 - Imediata (Hoje):
- [ ] Revisar sudoers - adicionar `unshare` específico
- [ ] Remover `bash -c *` genérico
- [ ] Testar isolamento com componente simples
- [ ] Documentar permissões restritas

### FASE 2 - Curto Prazo (1-2 dias):
- [ ] Migrar `subprocess.run()` com shell=True para sandbox
- [ ] Implementar proteção de processos (cgroups)
- [ ] Configurar restart automático via systemd
- [ ] Testar full test suite com isolamento

### FASE 3 - Médio Prazo (1 semana):
- [ ] Integrar LLM gerado dinamicamente com sandbox
- [ ] Implementar logging de isolamento em real-time
- [ ] Adicionar monitoring de CPU/mem dentro do sandbox
- [ ] Validar que nenhum processo do usuário é morto

### FASE 4 - Produção:
- [ ] Deploy com sudoers restrito
- [ ] Monitoria contínua de violações
- [ ] Alertas se sandbox falha

## 7. Linhas Específicas a Corrigir

### vectorize_omnimind.py (Shell=True)
```python
# ❌ ANTES (INSEGURO)
result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)

# ✅ DEPOIS (ISOLADO)
result = subprocess.run(
    cmd_split,  # Sem shell=True
    capture_output=True,
    text=True,
    timeout=10,
    preexec_fn=lambda: resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
)
# OU para código dinâmico:
sandbox = AutopoieticSandbox()
result = sandbox.execute_component(code, "component_name")
```

## 8. Monitoramento em Tempo Real

### Que coletar:
- Isolamento method usado (unshare vs direct vs fallback)
- CPU time consumido vs limite (30s)
- Memory consumido vs limite (100MB)
- Timeout events
- Security validation failures
- Processo PID (sandboxed, não pode ser do usuário)

### Prometheus metrics:
```
omnimind_sandbox_executions_total{isolation="unshare"}
omnimind_sandbox_cpu_seconds_total
omnimind_sandbox_memory_bytes_max
omnimind_sandbox_timeouts_total
omnimind_sandbox_security_violations_total
```

## Status Final

| Item | Status | Prioridade |
|------|--------|-----------|
| Autopoiesis isolado | ✅ DONE | 🔴 CRÍTICO |
| Sudoers restrito | 🚫 TODO | 🔴 CRÍTICO |
| Process protection | 🚫 TODO | 🔴 CRÍTICO |
| Subprocess migration | 🚫 TODO | 🟡 ALTA |
| Restart automático | 🚫 TODO | 🟡 ALTA |
| Monitoring/Logging | 🚫 TODO | 🟠 MÉDIA |
| Full test validation | 🚫 TODO | 🟡 ALTA |

---

**Próximos Passos:**
1. Revisar /etc/sudoers.d/omnimind com proteção de processos
2. Testar unshare + cgroups
3. Validar que testes rodam com novo isolamento
4. Integrar monitoramento
