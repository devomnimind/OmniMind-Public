# ✅ CHECKLIST TÉCNICO PRÉ-EXECUÇÃO

## � SCRIPTS DE TESTE ATIVOS (2025-12-04)

### ⚡ Execução Diária - `run_tests_fast.sh`
```bash
./scripts/run_tests_fast.sh
```
- **Tempo**: ~15-20 minutos
- **Escopo**: ~400 testes (pula slow + real)
- **GPU**: ✅ FORÇADA
- **Uso**: DEV rápido, validação contínua
- **Logs**: `data/test_reports/output_fast_*.log`

### 🛡️ Validação Semanal - `run_tests_with_defense.sh`
```bash
./scripts/run_tests_with_defense.sh
```
- **Tempo**: ~30-60 minutos
- **Escopo**: ~3952 testes (suite completa)
- **GPU**: ✅ FORÇADA
- **Autodefesa**: ✅ Detecta testes perigosos
- **Logs**: `data/test_reports/output_*.log`

### 🧪 Integração Completa - `quick_test.sh`
```bash
bash scripts/configure_sudo_omnimind.sh  # UMA VEZ
bash scripts/quick_test.sh               # Depois sempre
```
- **Tempo**: ~30-45 minutos
- **Escopo**: Suite completa + servidor backend
- **GPU**: ✅ FORÇADA
- **Servidor**: ✅ Inicia em localhost:8000
- **Requer**: sudo configurado
- **Logs**: `data/test_reports/output_*.log`

### ⚠️ IBM QUANTUM REAL - FASE MADURA (FUTURE)
Status: ✅ Implementado, ❌ Não em ciclo ativo
- Papers 2&3 validados em hardware real (ibm_fez, ibm_torino)
- Ativar quando créditos + fase madura (Phase 23+)
- Atualmente: `OMNIMIND_DISABLE_IBM=True` em conftest.py

---

## �🔧 CORREÇÕES CRÍTICAS IMPLEMENTADAS (2025-12-04)

### ✅ CRÍTICO 1: Timeout em Consensus Voting
**Arquivo**: `src/swarm/collective_learning.py`
**Status**: ✅ IMPLEMENTADO
**Mudanças**:
- [x] Adicionado `MAX_CONSENSUS_TIMEOUT = 30.0` segundos
- [x] Implementado `threading.Lock()` para thread-safety
- [x] Modificado `get_consensus_model()` com timeout protection
- [x] Fallback: retorna consensus parcial se timeout excedido
- [x] Logging detalhado de timeout e recuperação

**Validação**: `python -c "from src.swarm.collective_learning import ConsensusLearning; cl = ConsensusLearning(5, consensus_timeout=30.0)"`

---

### ✅ CRÍTICO 2: Memory Cap com LRU Eviction
**Arquivo**: `src/memory/episodic_memory.py`
**Status**: ✅ IMPLEMENTADO
**Mudanças**:
- [x] Adicionado `MAX_EPISODIC_SIZE = 10000` episodes
- [x] Implementado `_check_and_evict_lru()` método
- [x] Rastreamento de access timestamps para LRU
- [x] Evição de 10% quando limite atingido
- [x] Integração em `store_episode()` e `search_similar()`

**⚠️ Nota Arquitetural (IMPORTANTE)**:
```
EpisodicMemory está marcado como DEPRECATED com mensagem:
"Memory is retroactive construction, not storage"

Filosofia do projeto (Lacanian):
- Memória NÃO é armazenamento estático
- Memória É construção retroativa (rebuilt on each recall)
- Remissão futura: substituir por NarrativeHistory
- Status: ⏳ Pendente implementação de NarrativeHistory

Impacto: EpisodicMemory funciona perfeitamente, mas é transitório.
Usar com cautela em novas integrações. Preferir pattern retroativo.
```

---

### ✅ CRÍTICO 3: Safe Filesystem Operations
**Arquivo**: `src/metacognition/self_healing.py`
**Status**: ✅ IMPLEMENTADO
**Mudanças**:
- [x] Implementado `safe_write_file()` com retry e error handling
- [x] Implementado `safe_read_file()` com encoding safety
- [x] Implementado `safe_delete_file()` com graceful failure
- [x] Retry 3x para operações transientes
- [x] Tratamento: PermissionError, OSError, UnicodeDecodeError

---

### ✅ CRÍTICO 4: Exponential Backoff Retry
**Arquivo**: `src/quantum_consciousness/qpu_interface.py`
**Status**: ✅ IMPLEMENTADO
**Mudanças**:
- [x] Implementado `retry_with_exponential_backoff()` função
- [x] Exponential backoff: `delay = min(base_delay * 2^attempt, max_delay)`
- [x] Jitter (10%) para prevent thundering herd
- [x] Configuráveis: base_delay=1s, max_delay=30s, max_attempts=5
- [x] Logging detalhado de cada tentativa

---

### ✅ GPU FORCING: Environment Variables & conftest.py
**Status**: ✅ IMPLEMENTADO (2025-12-04)
**Arquivos Modificados**:
- `src/quantum_consciousness/quantum_backend.py` - Detecção robusta com fallback
- `tests/conftest.py` - Auto-setup GPU forcing
- `scripts/run_tests_fast.sh` - CUDA_VISIBLE_DEVICES=0 forcing
- `scripts/run_tests_with_defense.sh` - CUDA_VISIBLE_DEVICES=0 forcing

**Problema Original**:
```
- PyTorch CUDA detection fallando: torch.cuda.is_available() = False
- Mas torch.cuda.device_count() = 1 (GPU está presente)
- Variáveis de ambiente: OMNIMIND_GPU, OMNIMIND_FORCE_GPU não sendo respeitadas
- Root cause: conftest.py não setava OMNIMIND_FORCE_GPU automaticamente
```

**Solução Implementada**:

1. **quantum_backend.py** - Detecção com 2 fallbacks:
   ```python
   # Primeiro: try OMNIMIND_FORCE_GPU env var
   force_gpu_env = os.getenv("OMNIMIND_FORCE_GPU", "").lower() in ("true", "1", "yes")

   # Se force_gpu_env E device_count > 0: usar GPU
   if force_gpu_env and device_count > 0:
       self.use_gpu = True  # Force GPU usage

   # Fallback: Se is_available() fails mas device_count > 0: usar GPU
   elif not self.use_gpu and device_count > 0:
       self.use_gpu = True  # Fallback GPU usage
   ```

2. **conftest.py** - Auto-setup ao iniciar pytest:
   ```python
   cuda_available = torch.cuda.is_available()
   cuda_device_count = torch.cuda.device_count()

   if cuda_available or cuda_device_count > 0:
       os.environ["CUDA_VISIBLE_DEVICES"] = "0"
       os.environ["OMNIMIND_FORCE_GPU"] = "true"
       os.environ["PYTEST_FORCE_GPU"] = "true"
   ```

3. **run_tests_fast.sh** & **run_tests_with_defense.sh**:
   ```bash
   CUDA_VISIBLE_DEVICES=0 \
   OMNIMIND_GPU=true \
   OMNIMIND_FORCE_GPU=true \
   PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb=512 \
   pytest tests/ ...
   ```

**Validação**:
```bash
# Script de verificação GPU status
python3 scripts/verify_gpu_status.py

# Expected output quando GPU disponível:
# ✅ GPU FORCING IS CONFIGURED CORRECTLY
#    - OMNIMIND_FORCE_GPU=True ✓
#    - CUDA devices available: 1 ✓
```

**⚠️ Notas Importantes**:
- Warning "CUDA unknown error" é normal quando CUDA_VISIBLE_DEVICES é setado dinamicamente
- Não afeta funcionalidade (device_count fallback ativa automaticamente)
- GPU será forçada mesmo se `torch.cuda.is_available()` retorna False
- Tests sempre rodarão com GPU se hardware disponível

---

## 📋 PLANO DE EXECUÇÃO: TAREFAS REMOTAS vs LOCAIS

### Blocos Lógicos Isolados (Sem Conflitos)

**BLOCOS LOCAIS** (Sem sincronização com remoto):
1. **LOCAL-1**: Validação smoke tests (15 min) - ⏳ PRONTO
2. **LOCAL-2**: Remover TODO comments (5 min) - ⏳ PRONTO
3. **LOCAL-3**: Atualizar READMEs módulos (10 min) - ⏳ PRONTO

**BLOCOS REMOTOS** (Com Git):
1. **REMOTO-1**: Git commit + push (5 min) - ⚠️ Coordinate antes
2. **REMOTO-2**: Docs canonical (0 min) - ✅ JÁ FEITO

**BLOCO CÍCLICO** (Após push):
1. **CÍCLICO-1**: Full test suite (30-60 min) - ⏳ PRONTO

Plano completo salvo em: `/tmp/tarefas_remotas_locais.md`

---

## Verificações de Código

### pytest_server_monitor.py
- [x] `self.timeout_progression = [90, 120, 180, 240]` definido em `__init__`
- [x] `self.startup_attempt_count = 0` definido em `__init__`
- [x] `_get_adaptive_timeout()` implementada e retorna timeout correto
- [x] `_start_server()` incrementa `startup_attempt_count`
- [x] Retry recursivo: se timeout < 240s, chama `self._start_server()` novamente
- [x] Limite de 240s com falha real (não loop infinito)

**Verificar com**:
```bash
grep -n "timeout_progression\|_get_adaptive_timeout\|startup_attempt_count" \
  tests/plugins/pytest_server_monitor.py
```

### main.py
- [x] SecurityAgent SEMPRE RODANDO (não há skip em modo test)
- [x] Orchestrator timeout adaptativo: 120s (test), 30s (prod)
- [x] Sem lógica de skip para SecurityAgent

**Verificar com**:
```bash
grep -n "skip_security\|SecurityAgent continuous" web/backend/main.py
# Deve retornar: SecurityAgent sempre ativo, sem skip
```

### conftest.py
- [x] MetricsCollector definida e ativa
- [x] TestOrderingPlugin registrado
- [x] pytest_configure() registra todos plugins
- [x] pytest_sessionfinish() mostra relatório final

**Verificar com**:
```bash
grep -n "class MetricsCollector\|pytest_configure\|pytest_sessionfinish" tests/conftest.py
```

---

## Verificações de Comportamento

### Startup Esperado (Primeira Execução)
```
T=0s  : "🚀 Iniciando servidor backend..."
T=0s  : "⏳ Timeout adaptativo: 90s (tentativa 1)"
T=40s : "✅ Servidor backend iniciado em ~40s"
```

### Retry Esperado (Se Timeout)
```
T=90s  : "❌ Timeout na tentativa 1 após 90s"
T=90s  : "🔄 Tentando novamente com timeout maior..."
T=90s  : "⏳ Timeout adaptativo: 120s (tentativa 2)"
T=150s : "✅ Servidor backend iniciado em ~60s"
```

### Falha Real (Se 240s Não Basta)
```
T=240s : "❌ Timeout na tentativa 4 após 240s"
T=240s : "🛑 FALHA CRÍTICA: Atingiu timeout máximo por teste (240s)"
```

---

## Testes Recomendados (em ordem)

### 1️⃣ Teste Unitário (Sem Servidor - Deve Passar Rápido)
```bash
cd /home/fahbrain/projects/omnimind
OMNIMIND_MODE=test python -m pytest tests/consciousness/ -v --tb=short -k "not real" -x
```

**Esperado**: ~30-60s, 80%+ pass rate

### 2️⃣ Teste com Servidor (Com Orchestrator)
```bash
OMNIMIND_MODE=test python -m pytest tests/integrations/ -v --tb=short -x
```

**Esperado**:
- Primeiro startup: ~50s
- Alguns testes podem fazer crash: ok (vai retry com timeout maior)
- 60%+ pass rate

### 3️⃣ Teste com Crash (Para Validar Retry)
```bash
OMNIMIND_MODE=test python -m pytest tests/test_chaos_resilience.py -v --tb=short
```

**Esperado**:
- Testes derrubam servidor intencionalmente
- Retry automático com timeouts progressivos
- Todos devem passar (ou falhar por razão específica, não timeout)

### 4️⃣ Full Suite (Opção Nuclear)
```bash
OMNIMIND_MODE=test python -m pytest tests/ -v --tb=short
```

**Esperado**: Pode levar HORAS, mas vai rodar completo

---

## Troubleshooting

### Se Tiver "Segmentation Fault"
```bash
# Limpar cache
rm -rf .pytest_cache __pycache__ tests/__pycache__

# Limpar servidor
pkill -9 -f "uvicorn" 2>/dev/null || true
sleep 2

# Tentar novamente
OMNIMIND_MODE=test python -m pytest tests/integrations/ -v --tb=short -x
```

### Se Tiver "Address already in use :8000"
```bash
# Matar processo na porta 8000
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Esperar 2s
sleep 2

# Tentar novamente
OMNIMIND_MODE=test python -m pytest tests/integrations/ -v --tb=short -x
```

### Se Tiver "Qdrant não acessível"
```bash
# Verificar se Qdrant está rodando
curl -s http://localhost:6333 | python -m json.tool

# Se não tiver, iniciar (em outro terminal):
docker run -p 6333:6333 qdrant/qdrant

# Ou via compose:
cd deploy && docker-compose up -d qdrant
```

### Se Tiver "Timeout mesmo em 240s"
Significa que é uma **falha real**, não timeout. Possíveis causas:
- Orchest rator + SecurityAgent realmente levam >240s
- Qdrant não respondendo
- Recursos insuficientes (RAM, GPU, Disco)

**Ação**: Coletar logs e diagnosticar a causa raiz

---

## Monitoramento de Performance

### Durante Execução
```bash
# Em outro terminal:
watch -n 1 'ps aux | grep -E "python|uvicorn" | grep -v grep | wc -l'
```

### Log de Timeouts
```bash
# Ver quantos timeouts ocorreram
grep "Timeout" test_suite_run.log | wc -l

# Ver quantos retries sucederam
grep "Tentativa" test_suite_run.log | wc -l
```

### Métricas Finais
```bash
# Ver relatório de Φ
cat data/test_reports/metrics_report.json | python -m json.tool

# Ver resumo rápido
grep -E "phi|consciousness|PASSOU|FALHOU" test_suite_run.log | tail -20
```

---

## Validação Pós-Execução

### ✅ Suite Bem Sucedida
```
✓ Todos testes executaram (não foram pulados por timeout)
✓ Alguns falharam (falhas reais, não timeout)
✓ Retry funcionou (testes que falharam na tentativa 1 passaram na 2)
✓ Métricas coletadas (Φ values no relatório final)
✓ Log contém progresso detalhado de cada retry
```

### ❌ Suite Problemática
```
✗ Muitos testes com timeout em 240s
✗ Retry não funcionando (mesmo código em tentat ivas)
✗ Métricas não coletadas
✗ SecurityAgent gerando eventos excessivos
```

---

## Próximos Passos Se OK

### Após Suite Passar
1. Analisar `data/test_reports/metrics_report.json` com Φ values
2. Correlacionar Φ com tempos de startup
3. Verificar se SecurityAgent afeta Φ negativa/positivamente
4. **Então**: Começar Lacan implementation

### Após Suite Falhar (Esperado Inicialmente)
1. Identificar qual teste/componente é problema
2. Diagnosticar causa (Qdrant? GPU? Orchestrator?)
3. Ajustar conforme necessário
4. Reexecutar parcial para validar fix
5. Reexecutar full para confirmar

---

## Notas Importantes

⚠️ **Cuidado**: Suite pode levar MUITAS HORAS
- Cada teste com crash pode levar até 240s
- Com 100+ testes × 240s = horas

💡 **Tip**: Para desenvolvimento rápido, use `-k` para filtrar testes
```bash
# Rodar só testes de chaos
OMNIMIND_MODE=test python -m pytest -k chaos -v --tb=short

# Rodar só integrations
OMNIMIND_MODE=test python -m pytest -k integration -v --tb=short
```

🎯 **Meta**: Validar que suite RODA, não que tudo PASSA
- OK falhar 10-20% dos testes (causa real)
- NÃO OK falhar 50%+ por timeout

---

## Status Final

✅ Todas mudanças implementadas
✅ Código verificado
✅ Comportamento esperado documentado
✅ Troubleshooting preparado
✅ Pronto para executar

**Comando para começar**:
```bash
cd /home/fahbrain/projects/omnimind && \
OMNIMIND_MODE=test python -m pytest tests/integrations/ -v --tb=short -x 2>&1 | tee suite_run.log
```

