# Guia Completo da Suíte de Testes OmniMind

**Versão:** 3.1 (Atualizado Dec 2025)
**Status:** Documentação Oficial

---

## 🔒 Gerenciamento de Estado do Servidor (Dez 2025)

**OTIMIZADO PARA SUITE COM 3900 TESTES**: Implementado `ServerStateManager` com cache agressivo:
- `omnimind_server` fixture (session scope, E2E tests)
- `ServerMonitorPlugin` (test scope, runtime monitoring)

**Resolve**:
- Race conditions entre fixture e plugin ao reiniciar servidor
- ✅ **Health check cache: 45s** (não 5s) - evita 3900+ checks
- ✅ **Timeout tolerante: 5s** (não 1s) - aceita servers lentos sob carga
- ✅ **Timeout ≠ DOWN** - apenas ConnectionError confirma crash
- ✅ **Cache-first strategy** - reutiliza health check recente
- Reinicializações desnecessárias durante E2E tests

**Estratégia com Sistema Ativo**:
```
3900 testes em paralelo + OmniMind sistema + VS Code + Copilot
→ CPU contencioso → servers respondem lento
→ Timeout não = DOWN (é apenas lentidão)
→ Cache 45s + Timeout 5s = balanceado
```

**Thread-safe**: RLock garante sincronização entre múltiplos workers

---

## ⏱️ Configuração de Timeout (Dez 2025)

**Global settings** in `config/pytest.ini`:
- **Per-test timeout**: 800 segundos (13.3 min max por teste, thread-based)
- **Timeout allocation**: Progressive (cada teste tem 800s inteiros, não cumulativo)
- **Server health check**:
  - **Timeout**: 5 segundos (tolerante para servidores sob carga)
  - **Cache**: 45 segundos (evita múltiplos checks durante suite)
  - **Diferenciação crítica**: Timeout ≠ ConnectionError

---

## 📊 Visão Geral - Distribuição de Testes

| Tipo | Quantidade | Incluído em run_tests_fast.sh | Descrição |
|------|-----------|---|---|
| Unit/Integration (mocked) | ~3900 | ✅ | Testes sem mocks, lógica pura |
| `@pytest.mark.real` (sem chaos) | 11 | ✅ | GPU+LLM+Network, não destroem servidor |
| `@pytest.mark.real` + `@pytest.mark.chaos` | 8 | ❌ | Server destruction (semanal) |
| `@pytest.mark.slow` | ? | ❌ | Timeout > 30s |
| **TOTAL run_tests_fast.sh** | **3996** | ✅ | Daily validation |
| **TOTAL run_tests_with_defense.sh** | **4004** | ✅ | Weekly (+ 8 chaos) |

### 📈 Test Markers Explained

```python
# Mocked unit test - included in run_tests_fast.sh
def test_basic_logic():
    pass

# Real GPU+LLM+Network test (non-destructive) - included in run_tests_fast.sh
@pytest.mark.real
def test_consciousness_metrics():
    pass

# Server destruction test - EXCLUDED from run_tests_fast.sh, ONLY in weekly
@pytest.mark.chaos
@pytest.mark.real
def test_phi_after_server_crash(kill_server):
    kill_server()  # BOOM - server destroyed
    pass

# Long-running test - ALWAYS excluded (>30s timeout)
@pytest.mark.slow
def test_complex_training():
    pass
```

### Para Executar Todos os Testes

```bash
# Daily: Fast suite (3996 tests, no server destruction)
./scripts/run_tests_fast.sh

# Weekly: Complete suite with chaos (4004 tests, includes server destruction)
./scripts/run_tests_with_defense.sh

# With specific markers
pytest -m "real"      # Only @pytest.mark.real tests (11 non-destructive)
pytest -m "chaos"     # Only @pytest.mark.chaos tests (8 destructive)
pytest -m "slow"      # Only @pytest.mark.slow tests
pytest -m "not slow and not chaos"  # Fast suite (same as run_tests_fast.sh)
```

---

## 🚀 Comandos Essenciais

### Execução Rápida

```bash
# Daily fast suite (RECOMENDADO)
./scripts/run_tests_fast.sh

# Weekly complete suite (com chaos engineering)
./scripts/run_tests_with_defense.sh

# Specific test file
pytest tests/consciousness/

# Specific markers
pytest -m "real"      # GPU+LLM tests
pytest -m "not slow"  # Fast tests
```

### Por Categoria

```bash
# Segurança
pytest tests/security/

# Agentes
pytest tests/agents/

# Consciousness module
pytest tests/consciousness/

# Sem testes lentos
pytest -m "not slow and not chaos"
```

---

## 🔍 Scripts de Teste

| Script | Testes | Tempo | Propósito |
|--------|--------|-------|----------|
| `run_tests_fast.sh` | 3996 | 10-15 min | ✅ Daily validation (GPU+LLM safe) |
| `run_tests_with_defense.sh` | 4004 | 45-90 min | 🛡️ Weekly (includes server destruction) |
| `quick_test.sh` | 4004 | 30-45 min | 🖥️ Full integration (requires sudo) |

### 1. Fast Suite (Diário)

```bash
./scripts/run_tests_fast.sh
```

- ✅ 3996 testes (sem `@pytest.mark.slow` ou `@pytest.mark.chaos`)
- ✅ Inclui `@pytest.mark.real` SEM `@pytest.mark.chaos` (seguro)
- 🚀 GPU forçada para CUDA device 0
- ⏱️ 800s por teste (progressivo)
- 📁 Logs: `data/test_reports/`

### 2. Complete Suite com Chaos (Semanal)

```bash
./scripts/run_tests_with_defense.sh
```

- 📊 4004 testes (3996 + 8 chaos)
- 🔴 Inclui `@pytest.mark.chaos` (server destruction tests)
- 🛡️ Autodefesa: detecta padrões perigosos
- ⚠️ Use fora do horário de trabalho

### 3. Full Integration com Backend

```bash
./scripts/quick_test.sh
```

- 🖥️ Inicia backend em localhost:8000
- 📊 4004 testes completos
- 💾 Requer sudo configurado
````

### 2. Verificar Dependências

```bash
python scripts/check_test_dependencies.py
```

Oferece instalação interativa de dependências faltantes.

### 3. Documentação Desatualizada

```bash
python scripts/check_outdated_documentation.py
```

Identifica documentos com estatísticas incorretas.

---

## 🎯 Estrutura da Suíte

```
tests/
├── agents/              # Testes de agentes
├── security/            # Testes de segurança
├── audit/              # Testes de auditoria
├── memory/             # Testes de memória
├── metacognition/      # Testes de metacognição
└── [outros módulos]    # 139 arquivos total
```

**Top 5 Arquivos com Mais Testes:**
1. `optimization/test_memory_optimization.py` - 41 testes
2. `test_collective_intelligence.py` - 40 testes
3. `test_observability.py` - 37 testes
4. `lacanian/test_desire_graph.py` - 35 testes
5. `lacanian/test_discourse_discovery.py` - 35 testes

---

## 🏗️ Arquitetura de Gerenciamento de Servidor

### Componentes Envolvidos

| Componente | Escopo | Responsabilidade |
|-----------|--------|-----------------|
| `ServerStateManager` | Global (singleton) | Coordena estado + propriedade + cache |
| `omnimind_server` fixture | Session | Inicia/para servidor, adquire propriedade |
| `ServerMonitorPlugin` | Test | Monitora saúde, respeita propriedade, usa cache |
| `pytest_runtest_setup` | Test | Verifica server UP antes de teste (com cache) |
| `pytest_runtest_makereport` | Test | Detecta crashes reais (ConnectionError apenas) |
| `pytest_runtest_teardown` | Test | Recuperação pós-crash |

### Otimizações para 3900 Testes Paralelos

**Problema Original**:
```
3900 testes × 2 health checks (setup + teardown) = 7800 checks
Com timeout 1s: 7800s = 130 minutos PERDIDOS em health checks
```

**Solução Implementada**:
```
✅ Health Check Cache: 45 segundos
   - 1 check → cached por 45s
   - Próximos 300+ testes reutilizam cache
   - Economia: ~7500 checks eliminadas

✅ Timeout Tolerante: 5 segundos
   - Antes: 1s timeout = muitos falsos positivos
   - Depois: 5s timeout = distingue timeout de DOWN

✅ Cache-First Strategy (pytest_runtest_setup):
   - Se cache válido e diz UP → pula health check
   - Só faz novo check se cache expirou (45s)
   - Diferencia timeout (normal, confiar em cache) de ConnectionError (DOWN)

✅ Lazy Checks (pytest_runtest_makereport):
   - Se cache recente diz UP → não refazer check
   - Só verifica se cache expirou
   - Reduz de ~3900 checks para ~50-100 checks por suite
```

### Diferenciação Crítica: Timeout vs ConnectionError

```python
# ANTES: Timeout = DOWN (ERRADO)
try:
    resp = session.get("/health/", timeout=1)
except requests.exceptions.Timeout:
    mark_down()  # ❌ ERRADO: timeout não = servidor DOWN

# DEPOIS: Timeout = lentidão normal (CERTO)
try:
    resp = session.get("/health/", timeout=5)
except requests.exceptions.Timeout:
    return True  # ✅ CORRETO: assume UP (é só lento)
except requests.exceptions.ConnectionError:
    return False  # ✅ CORRETO: porta fechada = DOWN
```

### Resultado Esperado

```
run_tests_fast.sh com 3900 testes:
  Antes: Múltiplos timeouts falsos → restart desnecessários → ~2-3 restarts
  Depois: Cache inteligente + timeout tolerante → 0-1 restarts (apenas crashs reais)

Tempo total:
  Antes: 15min (testes) + 2min (restart overhead) = 17min
  Depois: 15min (testes) + 0min (overhead) = 15min
```

---

## 🏗️ Arquitetura de Gerenciamento de Servidor (ANTIGA - veja acima)

### Fluxo de Operação

**Cenário 1: E2E Tests (run_tests_fast.sh com E2E)**

```
Session Start
    ↓
omnimind_server fixture
    ↓ acquire_ownership("fixture")
    ├─ mark_starting()
    ├─ Inicia servidor Python
    └─ mark_running()
    ↓
E2E tests executam
    ↓
Para cada teste E2E:
    ├─ pytest_runtest_setup
    │  └─ Plugin verifica: owner=="fixture" → confia na fixture
    ├─ Teste executa
    └─ pytest_runtest_teardown
       └─ Fixture monitora server state
    ↓
Session End
    ↓
omnimind_server teardown
    ├─ Termina processo servidor
    └─ release_ownership("fixture")
```

**Cenário 2: Unit/Integration Tests (run_tests_fast.sh sem E2E)**

```
Session Start
    ↓
ServerStateManager inicializado (owner=None)
    ↓
Para cada teste que precisa servidor:
    ├─ pytest_runtest_setup (plugin checks)
    │  ├─ _is_server_healthy()?
    │  ├─ Se DOWN: acquire_ownership("plugin") → _start_server()
    │  └─ mark_running()
    ├─ Teste executa
    └─ pytest_runtest_makereport
       ├─ Servidor caiu? mark_down()
       └─ Plugin: acquire_ownership("plugin") → _start_server()
           └─ release_ownership("plugin")
```

### Health Check Cache

**Problema original**: Múltiplos health checks sucessivos → latência acumulada

**Solução**: Cache de 5 segundos

```python
# Resultado cacheado por 5s
_last_health_check_time = time.time()
_last_health_check_result = is_healthy

# Próximo check dentro de 5s?
if has_recent_health_check():
    return get_cached_health_check()  # Rápido ✅
else:
    # Faz novo check HTTP
    resp = session.get("/health/", timeout=1)
```

### Estados e Transições

```
    ┌─────────────────────────────────────┐
    │  UNKNOWN (state inicial)            │
    └──────────────┬──────────────────────┘
                   │ acquire_ownership() + start
                   ↓
    ┌─────────────────────────────────────┐
    │  STARTING (processo iniciando)      │
    │  ✅ Plugin: wait com adaptive timeout│
    │  ❌ Plugin NÃO mata/re-inicia       │
    └──────────────┬──────────────────────┘
                   │ health check passou
                   ↓
    ┌─────────────────────────────────────┐
    │  RUNNING (servidor respondendo)     │
    │  ✅ Testes podem usar               │
    │  ✅ Health checks cacheados         │
    └──────┬──────────────────────────────┘
           │ health check falhou
           ↓
    ┌─────────────────────────────────────┐
    │  DOWN (sem resposta)                │
    │  ✅ Plugin detecta e reinicia       │
    └──────┬──────────────────────────────┘
           │ release_ownership() + cleanup
           ↓
    ┌─────────────────────────────────────┐
    │  STOPPING (encerramento)            │
    │  ❌ Nenhum teste pode usar          │
    └──────┬──────────────────────────────┘
           │ processo morreu
           ↓
         UNKNOWN
```

### Evitando Race Conditions

**Race condition original**:
```
Thread 1 (fixture): acquire_ownership("fixture")
Thread 2 (plugin): acquire_ownership("plugin") ← CONFLITO!
Resultado: Ambos tentam reiniciar → caos
```

**Solução com RLock**:
```python
def acquire_ownership(self, requester):
    with self._lock:  # RLock garante atomicidade
        if self._owner is not None and self._owner != requester:
            return False  # Outro componente já controla
        self._owner = requester
        return True
```

---

## 🐛 Problemas Comuns

### "No module named X"

**Solução:**
```bash
pip install -r requirements.txt
# ou
python scripts/check_test_dependencies.py
```

### Muitos testes pulados

**Causa:** Marcadores skipif baseados em hardware/ambiente

**Verificar:**
```bash
pytest -v -rs tests/  # Mostra razões dos skips
```

### Testes lentos

**Solução:**
```bash
pytest -m "not slow" tests/  # Executa apenas rápidos
```

---

## 📈 Métricas de Qualidade

| Métrica | Atual | Alvo |
|---------|-------|------|
| Cobertura | ~85% | ≥90% |
| Testes Executáveis | 78.7% | ≥95% |
| Módulos Críticos sem Testes | 25 | 0 |

---

## 📚 Documentação Completa

Para guia detalhado, consulte: `TESTE_SUITE_INVESTIGATION_REPORT.md`

Para análise JSON: `test_suite_analysis_report.json`

---

**Última atualização:** 2025-12-04
**Versão:** 2.1
