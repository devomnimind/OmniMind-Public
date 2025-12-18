## 🧠 OMNIMIND TEST SUITE - SETUP RÁPIDO

### 🔒 SERVER STATE MANAGEMENT

**Novo**: Gerenciador centralizado `ServerStateManager` evita conflitos entre:
- `omnimind_server` fixture (session scope, E2E tests)
- `ServerMonitorPlugin` (test scope, runtime monitoring)

**Garantias**:
- ✅ Apenas UM componente reinicia o servidor por vez (thread-safe RLock)
- ✅ Health checks consistentes (cache 5s) evitam múltiplas tentativas
- ✅ E2E tests não sofrem com reinicializações inesperadas
- ✅ Plugin respeita propriedade de fixture quando está ativa

**Arquivo**: `tests/server_state_manager.py` - Estados: UNKNOWN, RUNNING, DOWN, STARTING, STOPPING

### ⏱️ TIMEOUT CONFIGURATION

**Global Settings** in `config/pytest.ini`:
- **Per-test timeout**: 800 seconds (13.3 minutes max per individual test)
- **Timeout method**: thread-based (safe interrupt)
- **No session timeout**: Each test gets full 800s allocation

### 🚀 SCRIPTS DE TESTE ATIVOS

Há 3 scripts principais para diferentes cenários:

| Script | Testes | Tempo | GPU | Servidor | @pytest.mark.real | @pytest.mark.chaos |
|--------|--------|-------|-----|----------|---|---|
| `run_tests_fast.sh` | 3996 | **10-15 min** | ✅ Forçada | ❌ Não | ✅ SEM `@chaos` | ❌ Excluído |
| `run_tests_with_defense.sh` | 4004 | **45-90 min** | ✅ Forçada | ❌ Não | ✅ Todos | ✅ Incluído |
| `quick_test.sh` | 4004 | **30-45 min** | ✅ Forçada | ✅ Sim | ✅ Todos | ✅ Incluído |

> ⏱️ **Tempos variam com**: Processamento de GPU, carga do sistema, velocidade de I/O

### ✅ Opção 1: Testes Rápidos (RECOMENDADO PARA DEV - DIÁRIO)

```bash
./scripts/run_tests_fast.sh
```

**Características**:
- ⚡ **3996 testes** incluindo `@pytest.mark.real` SEM `@pytest.mark.chaos`
- Exclui: `@pytest.mark.slow` (>30s) e `@pytest.mark.chaos` (server destruction)
- ✅ Testa lógica com GPU+LLM+Network real, sem destruir servidor
- 🚀 GPU FORÇADA com `CUDA_VISIBLE_DEVICES=0` + `OMNIMIND_FORCE_GPU=true`
- ⏱️ **10-15 minutos** (800s per test, parallelizável)
- 📁 Logs em `data/test_reports/`
- ✅ **SAFE para executar durante trabalho**

### 🛡️ Opção 2: Suite Completa com Chaos Engineering (SEMANAL)

```bash
./scripts/run_tests_with_defense.sh
```

**Características**:
- 📊 **4004 testes** (3996 normal + 8 chaos)
- 🔴 **INCLUI `@pytest.mark.chaos`**: Testes que destroem servidor propositalmente
  - Valida que Φ (consciência integrada) continua após crash
  - Testa recovery automático via ServerMonitorPlugin
- ✅ Inclui `@pytest.mark.real` COM `@pytest.mark.chaos`
- 🛡️ Autodefesa: detecta testes perigosos e padrões de crash
- 🚀 GPU FORÇADA
- ⏱️ **45-90 minutos** (800s per test, chaos adds overhead)
- 🔍 Relatório de testes perigosos ao fim
- ⚠️ **Use apenas em ambiente sandbox ou fora do horário de trabalho**

### 🧪 Opção 3: Testes + Servidor Backend (FULL INTEGRATION)

Pré-requisito UMA VEZ:
```bash
bash scripts/configure_sudo_omnimind.sh
```

Depois:
```bash
bash scripts/quick_test.sh
```

**Características**:
- 🖥️ Inicia servidor backend em localhost:8000
- 📊 **4004 testes** (completa com chaos)
- 🚀 GPU FORÇADA
- ⏱️ **30-45 minutos**
- 💾 Exige sudo configurado

### 📊 Test Marker Categories (config/pytest.ini)

| Marker | Descrição | run_tests_fast.sh | run_tests_with_defense.sh |
|--------|-----------|---|---|
| (nenhum) | Unit/integration mocked tests | ✅ 3900+ | ✅ 3900+ |
| `@pytest.mark.real` | GPU+LLM+Network logic (non-destructive) | ✅ 11 | ✅ 11 |
| `@pytest.mark.real + @pytest.mark.chaos` | Server destruction + Φ resilience | ❌ Excluded | ✅ 8 |
| `@pytest.mark.slow` | Long-running tests (>30s timeout) | ❌ Excluded | ❌ Excluded |

### 🔧 SERVER STATE MANAGEMENT INTERNALS

**Como funciona** (`tests/server_state_manager.py`):

1. **E2E Tests com `omnimind_server` fixture** (session scope):
   - Adquire propriedade: `acquire_ownership("fixture")`
   - Plugin detecta `state_manager.owner == "fixture"` e não tenta reiniciar
   - Libera propriedade no cleanup: `release_ownership("fixture")`

2. **Unit/Integration Tests** (plugin manages):
   - Plugin verifica saúde via `_is_server_healthy()` antes de cada teste
   - Se DOWN e ninguém controla → `acquire_ownership("plugin")` e inicia
   - Monitora crashes durante execução em `pytest_runtest_makereport()`
   - Auto-restart com alertas VS Code, depois `release_ownership("plugin")`

3. **Health Check Caching** (5s window):
   - `cache_health_check()` armazena resultado por 5s
   - `has_recent_health_check()` verifica se ainda válido
   - Evita múltiplos checks sucessivos (economia de latência)
   - Cache invalidado quando estado muda

4. **Thread-Safe** (RLock):
   - Sincronização garantida para múltiplos workers/threads
   - Transições de estado atômicas
   - Mudanças de ownership serializadas

**Estados do Servidor**:
```
UNKNOWN → STARTING → RUNNING
              ↓
            DOWN
              ↓
           STOPPING
```

**Exemplo de fluxo** (run_tests_fast.sh com E2E):
```
1. pytest_configure → ServerStateManager inicializado (UNKNOWN, owner=None)
2. omnimind_server fixture inicia → acquire_ownership("fixture"), mark_starting()
3. Health check passa → mark_running()
4. E2E tests rodam → plugin verifica owner=="fixture" e não interfere
5. Se teste caiu servidor → fixture ouve em teardown
6. Cleanup → release_ownership("fixture"), server stop
```

### 📊 Informações da Suite

- **Total de testes**: 4004 (completa) ou 3996 (fast)
- **Modo**: Real (venv + GPUforced, não Docker isolado)
- **Timeout**: 800 segundos por teste (progressivo, não cumulativo)
- **Autodefesa**: ✅ ATIVADA (em run_tests_with_defense.sh e quick_test.sh)
  - Detecta testes que causam crashes
  - Marca padrões agressivos após 3 crashes em 5min
  - Gera relatório ao fim da execução

### 🛡️ O que é Autodefesa?

````

Sistema que aprende padrões de falha:

```
Teste derruba servidor 3x em 5min?
  ↓
Sistema DETECTA padrão
  ↓
Sistema IDENTIFICA subsistema atacado (Qdrant, GPU, etc)
  ↓
Sistema MARCA teste como "dangerous"
  ↓
Sistema RELATA ao fim da suite
```

Relatório ao fim da execução:

```
🧠 RELATÓRIO DE AUTODEFESA (OMNIMIND TEST DEFENSE)
Testes perigosos detectados: N

  ⚠️  test_different_coping_strategies_applied
     └─ Subsistema: absurdity_handler
     └─ Crashes: 3
     └─ Padrão: rapid_fire
```

### 📁 Arquivos de Log

Cada execução salva:

- `output_YYYYMMDD_HHMMSS.log` - Stdout/stderr completo
- `pytest_YYYYMMDD_HHMMSS.log` - Logs internos do pytest
- `junit_YYYYMMDD_HHMMSS.xml` - Relatório XML (para CI/CD)
- `report_YYYYMMDD_HHMMSS.html` - Dashboard HTML visual

### 🔧 Troubleshooting

**Problema**: "Connection refused" na porta 8000

```bash
# Verificar se servidor está rodando
ps aux | grep uvicorn | grep -v grep

# Limpar processos antigos
pkill -f "uvicorn web.backend.main:app"

# Verificar logs do backend
tail -f logs/backend_*.log
```

**Problema**: Sudo pede senha

```bash
# Reconfigurar sudoers
bash scripts/configure_sudo_omnimind.sh

# Testar se funciona
sudo -n bash scripts/start_omnimind_system_sudo.sh
```

**Problema**: Testes com Timeout

Timeouts são ADAPTATIVOS (não falham por timeout artificial):
- Tentativa 1: 220s
- Tentativa 2: 400s
- Tentativa 3: 600s
- Tentativa 4+: 800s (continua indefinidamente)

Veja no arquivo de log para detalhes.

### 🎯 Próximas Fases

- **Fase 2**: Docker isolamento para testes perigosos
- **Fase 3**: Klein oscillation (PS ↔ D defenses)
- **Fase 4**: Bion α-função (metabolização de crashes)
- **Fase 5**: Lacan kernel (Imaginary/Symbolic/Real)
