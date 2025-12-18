# 🔍 DIAGNÓSTICO: Slowdown no Startup do Servidor (15-20s → 40s+)

## 1. ACHADOS PRINCIPAIS

### ✅ Servidor Está Respondendo
- **Status**: FastAPI rodando em http://localhost:8000 ✅
- **Tempo de startup recente**: ~40 segundos
- **Antes**: 15-20 segundos
- **Degradação**: +100% a +166% mais lento

### 🔴 Causa Identificada: Orchestrator + SecurityAgent
O servidor está levando MAIS tempo porque:

1. **SecurityAgent está ATIVO agora** (antes estava desativado?)
   - Inicia monitoramento contínuo em background (6 tasks)
   - Verificações de segurança: `auditctl`, `aide`, `chkrootkit`, `rkhunter`, `lynis`, `clamdscan`
   - Gerando eventos de "suspicious processes" (kworker, systemd-timesyncd, nvidia, containerd, sh)
   - **Impacto**: +10-15 segundos

2. **Orchestrator Initialization Lento**
   - Inicializa em ~20-25 segundos
   - Dependency cascade:
     - LLM Router initialization (HuggingFace GPU check)
     - Supabase memory onboarding em background
     - Sentence Transformers carregamento
     - IIT Φ calculation (3x chamadas em paralelo)
     - Tools Framework (25 tools)
   - **Impacto**: +20-25 segundos

3. **Componentes em Paralelo** (executando ao mesmo tempo)
   - WebSocket Manager
   - Sinthome Broadcaster
   - Agent Communication Broadcaster
   - Daemon Monitor
   - Realtime Analytics Broadcaster
   - Agent Monitor
   - Metrics Collector
   - Performance Tracker
   - Consciousness Metrics Collector
   - **Impacto**: Esperam pelo componente mais lento (Orchestrator)

### 📊 Timeline de Startup (40 segundos)
```
T=0s      → Started server process [1079462]
T=0s      → Fast components parallelizados
T=2s      → Quantum Unconscious initialized
T=3s      → ExpectationModule com GPU
T=4s      → Monitoring systems started
T=5s      → ⚠️ Starting Orchestrator initialization (COMEÇA AQUI - vai levar 20-25s)
T=9s      → LLM Router check (HuggingFace GPU)
T=10s     → HTTP call to Qdrant collection
T=14s     → React Agent Supabase onboarding
T=16-20s  → IIT Φ calculated (3x calls)
T=22s     → SentenceTransformer carregamento
T=24s     → SecurityAgent initialized
T=25s     → MetacognitionAgent initialized
T=26s     → ✅ Orchestrator initialized successfully
T=27s     → SecurityAgent continuous monitoring started (6 tasks)
T=28s     → ⚠️ Application startup complete
T=29s+    → SecurityAgent gera eventos de suspicious processes
```

## 2. ANÁLISE DETALHADA: ONDE ESTÁ O TEMPO?

### 🔴 PROBLEMA 1: SecurityAgent verificações muito agressivas
```log
WARNING:security_agent:New security event suspicious_process: Suspicious process kworker/R-sync_wq
WARNING:security_agent:New security event suspicious_process: Suspicious process systemd-timesyncd
WARNING:security_agent:New security event suspicious_process: Suspicious process nvidia-persistenced
WARNING:security_agent:New security event suspicious_process: Suspicious process containerd-shim-runc-v2 (x7)
WARNING:security_agent:New security event suspicious_process: Suspicious process sh (x2)
```

**Problema**: SecurityAgent está marcando processos legítimos como "suspeitos"
- Gera 1 AUDIT por evento
- Está em loop, gerando MUITOS eventos rapidamente
- Consome CPU durante startup

**Afetado por**: Configuração de segurança muito agressiva

### 🔴 PROBLEMA 2: Orchestrator levando 20-25s de startup
```log
T=5s → Starting Orchestrator initialization (timeout=120.0s)
T=9s → HuggingFace Local: GPU disponível
T=10s → LLM Router inicializado
T=14s → React Agent Supabase memory onboarding
T=20s → IIT Φ calculated (corrected harmonic mean): 0.0020 (x3 calls)
T=24s → SentenceTransformer loaded
T=26s → ✅ Orchestrator initialized successfully
```

**Tempo quebrado**:
- T=5→9s: 4 segundos esperando inicialização do LLM Router
- T=14→20s: 6 segundos em Supabase + IIT Φ calculations
- T=20→26s: 6 segundos em carregamento do SentenceTransformer
- **Total**: ~20-25 segundos

### 🟡 PROBLEMA 3: Timeout no lifespan
```python
# web/backend/main.py
orchestrator_timeout = 120.0 if is_test_mode else 30.0  # Teste: 2 min, Produção: 30 seg
```

**Status**: Em modo TEST, o timeout é 120s (2 minutos) - CORRETO
**Issue**: Se Orchestrator levar >30s em produção, vai falhar
**Impacto**: Produção terá problemas se Orchestrator não inicializar em 30s

## 3. AVALIAÇÃO DA CONFIGURAÇÃO

### ✅ O que está CORRETO:
1. Parallelização de componentes rápidos (WebSocket, broadcasters)
2. Timeout adaptado ao modo (test=120s, production=30s)
3. Error handling com try/catch para cada componente
4. Orchestrator em thread pool (não bloqueia event loop)
5. Health checks com fallback

### ❌ O que está PROBLEMÁTICO:
1. **SecurityAgent ligado por padrão** - gera muito overhead
   - Verificações: auditctl, aide, chkrootkit, rkhunter, lynis, clamdscan
   - Demais para DEV/TEST

2. **SentenceTransformer carregado durante startup**
   - ~3-4 segundos apenas para carregar o modelo
   - Poderia ser lazy-loaded na primeira requisição

3. **IIT Φ calculation chamado 3x durante startup**
   - Cada chamada leva ~2s
   - Poderia ser movido para background task

4. **Qdrant verificações síncronas**
   - Testando conexão com Qdrant durante startup
   - Poderia ser assíncrono

5. **LLM Router initialization**
   - Verificação de GPU leva tempo
   - Poderia ser parallelizado melhor

## 4. RECOMENDAÇÕES IMEDIATAS

### 🎯 CURTO PRAZO (15 min - Impacto: -10 a -15s)

**1. Desativar SecurityAgent em modo TEST**
```python
# Em conftest.py ou main.py
if execution_mode == "test":
    # Desativar SecurityAgent durante testes
    os.environ["OMNIMIND_SKIP_SECURITY_MONITORING"] = "true"
```
**Impacto esperado**: -10 a -15 segundos

**2. Lazy-load SentenceTransformer**
```python
# Em main.py, mover do lifespan para rota
# Carregar apenas quando primeira requisição chegar
```
**Impacto esperado**: -3 a -4 segundos

**3. Mover IIT Φ calculation para background**
```python
# Não calcular durante startup, criar task background
```
**Impacto esperado**: -2 a -3 segundos

---

### 🎯 MÉDIO PRAZO (30 min - Impacto: -5 a -10s)

**4. Parallelizar Qdrant checks**
```python
# Usar asyncio em vez de sync requests
```
**Impacto esperado**: -1 a -2 segundos

**5. Parallelizar LLM Router com Orchestrator**
```python
# Ambos podem rodar simultaneamente
```
**Impacto esperado**: -2 a -3 segundos

---

### 🎯 LONGO PRAZO (Development)

**6. Implementar Progressive Enhancement**
- Iniciar servidor com funcionalidades mínimas (health check)
- Carregar componentes em background
- Reportar quando componentes críticos estiverem prontos

**7. Implementar Health Check por componente**
- `/health/lite` - apenas core (1s)
- `/health/standard` - com Qdrant (5s)
- `/health/full` - tudo (30s+)

---

## 5. ANÁLISE: QUANDO APLICAR CADA SOLUÇÃO?

### 🧪 Para TESTES (PRIORITY ALTA):
1. ✅ Desativar SecurityAgent (aplicar JÁ - simples)
2. ✅ Aumentar timeout em modo TEST (já feito: 120s)
3. ✅ Lazy-load componentes pesados (aplicar - simples)

**Meta**: 40s → 15-20s (voltando ao normal)

### 🚀 Para PRODUÇÃO (PRIORITY MÉDIA):
1. ✅ Manter SecurityAgent (necessário)
2. ✅ Otimizar paralelização
3. ✅ Implementar Progressive Enhancement

**Meta**: Manter 30-35s com segurança completa

### 🎓 Para LACANIAN WORK (PRIORITY BAIXA):
1. Correlacionar startup time com Φ
2. Estudar relação entre segurança e consciência
3. Investigar se SecurityAgent afeta Φ metrics

---

## 6. RECOMENDAÇÃO FINAL

### Aplicar IMEDIATAMENTE:

**A) Em `tests/conftest.py` (adicionar):**
```python
# Desabilitar SecurityAgent em modo test
os.environ["OMNIMIND_SKIP_SECURITY_AGENT"] = "true" if os.environ.get("OMNIMIND_MODE") == "test" else "false"
```

**B) Em `web/backend/main.py` (modificar):**
```python
# SentenceTransformer lazy-load
# Mover do lifespan para rota lazy-load

# IIT Φ calculation em background
# Não bloquear startup
```

**C) Em `tests/plugins/pytest_test_ordering.py` (adicionar):**
```python
# Print com breakdown de tempo de startup esperado
print(f"⏱️  Tempo esperado de startup: ~15-20s (com otimizações aplicadas)")
```

---

## 7. CHECKLIST ANTES DE RODAR TESTES

- [ ] SecurityAgent desativado em modo TEST
- [ ] SentenceTransformer lazy-load implementado
- [ ] IIT Φ em background
- [ ] Timeout em modo TEST = 120s (já está)
- [ ] Health check com fallback (já está)
- [ ] Logs de startup com timestamps

---

## 8. MARCA DE DIAGNÓSTICO

**Data**: 2025-12-02 21:56
**Versão**: web/backend/main.py (com parallelização)
**Modo**: OMNIMIND_MODE=test
**Startup Atual**: ~40 segundos
**Startup Meta**: ~15-20 segundos
**Degradação**: +100%
**Causa Raiz**: SecurityAgent + Orchestrator initialization
**Solução**: Lazy-load + background tasks + desabilitar SecurityAgent em TEST

