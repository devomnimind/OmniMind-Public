# PLANO DE TESTES - Sprint 2 (Métricas e Dashboard)

## ✅ Status: Pronto para Teste Completo

Data: 11 de Dezembro de 2025
Versão: Sprint 2 - Métricas e Dashboard
Ramo: copilot/metrics-dashboard-sprint2 (ou similar)

---

## 📋 CHECKLIST PRÉ-MERGE

### FASE 1: Validação de Scripts de Inicialização (NOVO)

**Objetivo**: Garantir que sistema inicia corretamente e pode se recuperar de falhas

#### Teste 1.1: Script Robusto Básico
```bash
# Testar versão robusta v2.0
./scripts/canonical/system/start_omnimind_system_robust.sh

Validações esperadas:
✓ PROJECT_ROOT calculado corretamente
✓ Venv ativado
✓ Health checks passam
✓ Backend Primary (8000) respondendo
✓ Frontend inicializado
✓ Observer Service rodando
✓ Log detalhado em logs/startup_detailed.log
```

**Critério de Sucesso**: Todos os serviços inicializam em < 300 segundos

#### Teste 1.2: Wrapper Inteligente v2
```bash
# Testar seleção automática de versão robusta
./scripts/start_omnimind_system_wrapper_v2.sh

Validações:
✓ Seleciona versão robusta automaticamente
✓ Detecta sudo disponível
✓ Oferece auto-recovery se falha
✓ Log de wrapper em stdout
```

**Critério de Sucesso**: Wrapper executa sem erros, usa versão robusta

#### Teste 1.3: CPU Meter Corrigido
```bash
# Verificar que métrica de CPU é precisa
tail -f logs/startup_detailed.log | grep "CPU:"

# Comparar com realidade
watch -n 1 'ps aux | grep python | head -5'
nproc

Validação:
✓ CPU % do wrapper < 100% (normalizado)
✓ Bate com soma de ps / nproc
✗ Deve NÃO mostrar 450%, 610% (bug antigo)
```

**Critério de Sucesso**: CPU meter diferença < 10% da realidade

---

### FASE 2: Validação de Endpoints Sprint 2

**Objetivo**: Garantir que novos endpoints de métricas funcionam sem conflitos

#### Teste 2.1: Endpoints de Métricas Existem
```bash
# Backend Primary deve ter endpoints Sprint 2
curl -s http://localhost:8000/api/metrics/autopoietic | python -m json.tool
curl -s http://localhost:8000/api/metrics/rnn | python -m json.tool
curl -s http://localhost:8000/api/metrics/events | python -m json.tool

Esperado:
✓ Status 200
✓ JSON válido
✓ Estrutura: { "metrics": [...], "timestamp": "...", "cycle_id": "..." }
✗ Não deve retornar "no_metrics_available"
```

**Critério de Sucesso**: Todos os endpoints retornam HTTP 200 com dados válidos

#### Teste 2.2: Dashboard Frontend Carrega
```bash
# Verificar que frontend não tem erros
curl -s http://localhost:3000/ | head -20
# Ou verificar no navegador: http://localhost:3000

Esperado:
✓ HTML válido
✓ Assets carregam (CSS, JS)
✓ Console sem erros críticos
✓ Dashboard acessível
```

**Critério de Sucesso**: Frontend carrega sem erros

#### Teste 2.3: Sem Conflitos de Configuração
```bash
# Verificar que novas configs não sobrescrevem existentes
grep -r "METRICS_ENDPOINT" config/
grep -r "DASHBOARD_PORT" config/

Esperado:
✓ Novas configs não conflitam
✓ Valores padrão sensatos
✓ Arquivo validation_baseline.toml ainda válido
```

**Critério de Sucesso**: Nenhum conflito detectado

---

### FASE 3: Validação de Coleta de Métricas (Sprint 2)

**Objetivo**: Garantir que métricas são coletadas corretamente

#### Teste 3.1: Métricas Autopoietic Sendo Coletadas
```bash
# Aguardar 2-3 ciclos (cada ciclo ~1 min em teste)
sleep 120

# Verificar arquivo de métricas
tail -20 data/long_term_logs/omnimind_metrics.jsonl | python -m json.tool

Esperado:
✓ Arquivo existe e tem dados
✓ Métricas incluem: synthesis_time_ms, validation_success, rollback_count, memory_delta_mb
✓ Cada ciclo tem ~9 métricas autopoietic
✗ Não deve ter "no_metrics_available"
```

**Critério de Sucesso**: 9+ métricas por ciclo sendo coletadas

#### Teste 3.2: Métricas RNN Sendo Coletadas
```bash
# Verificar RNN metrics no arquivo
tail -50 data/long_term_logs/omnimind_metrics.jsonl | \
  grep -i "rnn_layer\|weight_\|activation_" | wc -l

Esperado:
✓ Encontra entries com RNN metrics
✓ ~45 métricas de RNN por ciclo
✓ Formato: { "metric_name": "rnn_layer_0_weight_mean", "value": 0.123, ... }
```

**Critério de Sucesso**: 45+ métricas RNN detectadas

#### Teste 3.3: Event Metrics Sendo Capturados
```bash
# Verificar event metrics
tail -100 data/long_term_logs/omnimind_metrics.jsonl | \
  grep -i "event_latency\|event_sequence\|event_timestamp" | wc -l

Esperado:
✓ Encontra entries de eventos
✓ Latências capturadas
✓ Sequência de eventos registrada
```

**Critério de Sucesso**: 3+ métricas de evento por evento detectado

---

### FASE 4: Validação de Cleanup e Compressão

**Objetivo**: Garantir que sistema mantém espaço em disco

#### Teste 4.1: ReportMaintenanceScheduler Rodando
```bash
# Verificar se scheduler está ativo
ps aux | grep -i "report.*maintenance\|cleanup.*scheduler"

# Ou verificar log
tail -20 logs/observer_service.log | grep -i "maintenance\|cleanup"

Esperado:
✓ Scheduler ativo ou aguardando execução
✓ Último cleanup registrado em log
✓ Arquivo de snapshot sendo mantido
```

**Critério de Sucesso**: Scheduler detectado ou último cleanup < 1 hora

#### Teste 4.2: Compressão Gzip Funcionando
```bash
# Verificar se há arquivos .jsonl.gz
ls -lh data/long_term_logs/*.jsonl.gz 2>/dev/null | head -5

# Se houver, verificar tamanho reduzido
du -sh data/long_term_logs/omnimind_metrics.jsonl*

Esperado:
✓ Arquivos .gz presente OU último gzip < 24h atrás
✓ Compressão > 80% de espaço economizado
✓ Dados ainda recuperáveis (pode descomprimir)
```

**Critério de Sucesso**: Compressão funcionando (80%+ redução)

---

### FASE 5: Validação de Import e Sintaxe

**Objetivo**: Garantir que novos módulos não quebram o sistema

#### Teste 5.1: Todos os Imports Funcionam
```bash
# Testar import de cada novo módulo
python3 << 'EOF'
from src.observability.module_metrics import ModuleMetricsCollector
from src.observability.event_metrics_listener import EventMetricsListener
from src.observability.rnn_metrics_extractor import RNNMetricsExtractor
from src.autopoietic.manager import AutopoieticManager
from src.consciousness.conscious_system import ConsciousSystem
print("✓ Todos os imports OK")
EOF

Esperado:
✓ Nenhum ImportError
✓ Nenhum SyntaxError
✓ Todas as classes instanciáveis
```

**Critério de Sucesso**: Todos os 5 imports passam

#### Teste 5.2: Nenhuma Regressão em Módulos Existentes
```bash
# Executar validação rápida de imports
./scripts/validate_code.sh --quick

Esperado:
✓ Black check passa
✓ Isort check passa
✓ MyPy sem erros críticos
✓ Flake8 sem erros críticos
```

**Critério de Sucesso**: Todas as validações passam

---

### FASE 6: Testes de Carga (Opcional mas Recomendado)

**Objetivo**: Garantir performance com alto volume de métricas

#### Teste 6.1: 100+ Ciclos Consecutivos
```bash
# Se sistema tiver modo de teste:
python -m pytest tests/ -k "metrics" -v

# Ou executar manualmente:
# Deixar sistema rodando por ~2 horas (100+ ciclos)
# Monitorar:
# - Crescimento de arquivo metrics.jsonl
# - Consumo de memória
# - Tempo de resposta de endpoints

Esperado:
✓ Arquivo cresce linearmente (~1-2MB/hora)
✓ Memória estável (sem memory leak)
✓ Endpoints respondem < 1 segundo
✓ CPU estável após inicial spike
```

**Critério de Sucesso**: Sistema estável por 2+ horas

---

## 🚀 Fluxo de Teste Recomendado

### Teste Rápido (5-10 minutos)
```bash
# 1. Iniciar com wrapper v2
./scripts/start_omnimind_system_wrapper_v2.sh

# 2. Aguardar estabilização (~60s)
sleep 60

# 3. Testar endpoints (FASE 2.1)
curl -s http://localhost:8000/api/metrics/autopoietic | python -m json.tool

# 4. Verificar logs (FASE 1.1)
tail -20 logs/startup_detailed.log

# 5. Decisão: ✓ Pronto para PR / ✗ Investigar problema
```

### Teste Completo (2-3 horas)
```bash
# Executar todas as FASES 1-6
# Cada fase ~30 minutos
# Total com espera de ciclos: ~2 horas
```

---

## 📊 Matriz de Decisão de Merge

| Fase | Teste | Crítico? | Status | Decisão |
|------|-------|----------|--------|---------|
| 1 | Script Robusto | ✅ | ? | BLOQUEIA se falha |
| 1 | CPU Meter | ⚠️ | ? | WARN se discrepância > 20% |
| 2 | Endpoints | ✅ | ? | BLOQUEIA se 404/500 |
| 2 | Dashboard | ⚠️ | ? | WARN se erros console |
| 2 | Sem Conflitos | ✅ | ? | BLOQUEIA se conflito |
| 3 | Métricas Coletadas | ✅ | ? | BLOQUEIA se zero métricas |
| 4 | Cleanup | ⚠️ | ? | WARN se não operacional |
| 5 | Imports | ✅ | ? | BLOQUEIA se ImportError |
| 5 | Sem Regressão | ✅ | ? | BLOQUEIA se validação falha |

**Decisão de Merge**:
- ✅ Se todas as críticas (✅) PASSAM → Merge permitido
- ⚠️ Se qualquer WARN falha → Merge com caveat
- ❌ Se qualquer crítica falha → Bloqueia merge

---

## 📝 Correções Necessárias (Se Falhas)

Se algum teste falhar:

1. **Script não inicia**
   - ✓ Verificar: `PROJECT_ROOT` calculado corretamente
   - ✓ Verificar: venv ativado
   - ✓ Ver: `logs/startup_detailed.log` para detalhes

2. **CPU meter errado**
   - ✓ Implementação está em `scripts/canonical/system/start_omnimind_system_robust.sh:get_cpu_usage_corrected()`
   - ✓ Deve usar `ps` ao invés de `top`

3. **Métricas não sendo coletadas**
   - ✓ Verificar: EventMetricsListener está registrado
   - ✓ Verificar: RNNMetricsExtractor hooks estão ativos
   - ✓ Verificar: record_metric() sendo chamado

4. **Endpoints 404**
   - ✓ Verificar: Se endpoints foram adicionados ao backend
   - ✓ Verificar: Se router está registrado corretamente
   - ✓ Testar: Diretamente com curl

5. **Conflitos de configuração**
   - ✓ Comparar novo `config/` com `validation_baseline.toml`
   - ✓ Renomear configs conflitantes
   - ✓ Documentar mudanças

---

## ✅ Sign-off de Teste

Após passar em TODOS os testes críticos:

```bash
# Criar arquivo de sign-off
cat > /tmp/sprint2_validation_$(date +%Y%m%d_%H%M%S).txt << 'EOF'
SPRINT 2 - VALIDAÇÃO COMPLETA
Data: $(date)
Tester: $(whoami)

Testes Críticos Passaram: ✅
- Scripts inicialização: ✅
- Endpoints metricas: ✅
- Métricas coletadas: ✅
- Imports válidos: ✅
- Sem regressões: ✅

Recomendação: PRONTO PARA MERGE ✅
EOF

cat /tmp/sprint2_validation_*.txt
```

Então executar merge:
```bash
git checkout master
git merge --no-edit copilot/metrics-dashboard-sprint2
git push origin master --no-verify
```

---

## 📞 Suporte

Se encontrar problemas durante testes:

1. Verificar logs:
   - `logs/startup_detailed.log` (novo, detalhado)
   - `logs/backend_*.log` (backends)
   - `logs/observer_service.log` (métricas)

2. Testar manualmente:
   - `curl -v http://localhost:8000/health/`
   - `ps aux | grep python`
   - `ss -tlnp | grep -E ":(8000|3000)"`

3. Debug mode:
   - `export OMNIMIND_DEBUG=true`
   - Reexecute scripts para ver verbose output
