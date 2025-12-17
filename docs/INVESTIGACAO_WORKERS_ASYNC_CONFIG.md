# 🔍 INVESTIGAÇÃO: Workers Async = 1 vs 2+ (13 DEC 2025)

**Contexto**: Usuário observa que agentes anteriores foram **reduzindo velocidades assincronas** mas descobertos como problemas de **configuração**, não código. Pede validação e aumento para testar com **2 workers** ao invés de **1**.

---

## 📊 DESCOBERTAS ATUAIS

### 1. **Configuração Declarada vs Executada**

**Em config/optimization_config.json** (ESPERADO):
```json
{
  "async_workers": 8,
  "num_workers": 3
}
```

**Em scripts/canonical/system/run_cluster.sh** (REAL):
```bash
# Port 8000
--workers 1

# Port 8080
--workers 1

# Port 3001
--workers 1
```

**PROBLEMA ENCONTRADO**: ⚠️ Config diz `async_workers=8` mas scripts hardcoded em `--workers 1`

---

### 2. **Histórico de Redução de Workers**

Pesquisa em git mostra:
- ✅ Sistema com múltiplos backends (3 instâncias em 8000/8080/3001)
- ✅ Cada um com `--workers 1` (provavelmente para estabilidade)
- ⚠️ Não encontrei commit explícito de "redução de 4→1 workers"
- 📝 Documentação menciona `--workers 4` em PERFORMANCE_TUNING.md

---

### 3. **Estado Atual do Kali**

Você menciona: "isso estava setado via variável de ambiente se não me engano"

**Possível variável**: `OMNIMIND_ASYNC_WORKERS` ou similar (não encontrada nos scripts)

**Recomendação**: Você deveria ter **variável de ambiente** para configurar workers dinamicamente

---

## 🎯 PROPOSTA: Teste com 2 Workers

### Fase 1: Entender Comportamento Atual (1 worker)

```bash
# Status ATUAL
grep -r "\-\-workers" /home/fahbrain/projects/omnimind/scripts/ | grep -v ".pyc"
# Resultado: Todos com --workers 1
```

### Fase 2: Testar com 2 Workers

**Modificar run_cluster.sh temporariamente**:
```bash
# Mudar de:
nohup python -m uvicorn web.backend.main:app --port 8000 --workers 1

# Para:
nohup python -m uvicorn web.backend.main:app --port 8000 --workers 2
```

**Ou usar variável de ambiente**:
```bash
export OMNIMIND_WORKERS=2
# E no script:
nohup python -m uvicorn web.backend.main:app --port 8000 --workers ${OMNIMIND_WORKERS:-1}
```

### Fase 3: Monitorar Impacto

| Métrica | 1 Worker | 2 Workers | Esperado |
|---------|----------|-----------|----------|
| CPU Usage | ? | ? | Aumentar |
| GPU Utilization | 61% | ? | Aumentar para 70-80%? |
| Memory | ? | ? | Aumentar 20-30% |
| Response Time | ? | ? | Diminuir (mais concorrência) |
| GPU Memory | ? | ? | Aumentar 100-200MB |

---

## 💡 HIPÓTESE: Por Que Ficou em 1 Worker?

1. **Simplicidade**: 1 worker = menos variáveis
2. **Debuggabilidade**: Mais fácil rastrear erros com 1 thread
3. **Estabilidade**: 3 backends × 1 worker = 3 processos previsíveis
4. **GPU**: Se GPU compartilhada, múltiplos workers podem competir

**Problema**: Isso deixou GPU subutilizada (61% ao invés de 95%)

---

## 🚀 PLANO PARA VALIDAR E AUMENTAR

### ETAPA A: Criar Variável de Ambiente

**Arquivo**: Criar ou modificar arquivo de config

```bash
# /etc/environment ou ~/.bashrc
export OMNIMIND_WORKERS=2  # Pode ser 1, 2, 4, 8
export OMNIMIND_ASYNC_WORKERS=8  # Já em config.json
```

### ETAPA B: Modificar Scripts para Usar Variável

**Arquivos a modificar**:
- `scripts/canonical/system/run_cluster.sh`
- `scripts/recovery/03_run_integration_cycles_optimized.sh`
- `scripts/canonical/system/start_omnimind_system_robust.sh`

**Padrão**:
```bash
WORKERS=${OMNIMIND_WORKERS:-1}  # Default 1, pode override
nohup python -m uvicorn ... --workers $WORKERS
```

### ETAPA C: Teste Experimental (2 Workers)

```bash
# Terminal 1: Rodar com 2 workers
export OMNIMIND_WORKERS=2
bash scripts/canonical/system/run_cluster.sh

# Terminal 2: Monitor
watch -n 2 nvidia-smi

# Terminal 3: Validação
bash scripts/recovery/03_run_integration_cycles_optimized.sh
```

### ETAPA D: Coletar Métricas

```bash
# Comparar:
# - GPU utilization % (esperado: aumentar 61% → 75-80%)
# - CPU usage % (esperado: aumentar)
# - Response time (esperado: diminuir com mais workers)
# - Erro rate (esperado: 0 mesmo com 2 workers)
```

---

## ❓ PERGUNTAS CHAVE

**P1**: Qual era a configuração original no Kali?
- [ ] 1 worker por backend?
- [ ] 2 workers por backend?
- [ ] 4 workers por backend?
- [ ] Variável de ambiente que podia mudar?

**P2**: Por que ficou 1 worker (estabilidade ou erro)?
- [ ] Porque competia com GPU?
- [ ] Porque dava erro com múltiplos?
- [ ] Porque não havia testado?

**P3**: Qual seria o "ideal" para GTX 1650 4GB?
- [ ] 1 worker (sequencial)
- [ ] 2 workers (balanceado)
- [ ] 4 workers (máximo)

---

## 🛠️ IMPLEMENTAÇÃO PROPOSTA

### Passo 1: Adicionar Variável de Ambiente

```bash
# ~/.bashrc ou systemd/omnimind.service
export OMNIMIND_WORKERS=2
export OMNIMIND_WORKER_THREADS=4
export OMNIMIND_MAX_CONNECTIONS=100
```

### Passo 2: Modificar Scripts Dinâmicos

```bash
# ANTES:
--workers 1

# DEPOIS:
--workers ${OMNIMIND_WORKERS:-1} \
--limit-concurrency ${OMNIMIND_MAX_CONNECTIONS:-100} \
--limit-max-requests 1000 \
--timeout-keep-alive 10 \
--timeout-notify 30 \
--workers-per-core ${OMNIMIND_WORKER_THREADS:-2}
```

### Passo 3: Testar Progressivamente

```
Teste 1: OMNIMIND_WORKERS=1 (current)
         → Baseline: GPU 61%, CPU ?, Latency ?

Teste 2: OMNIMIND_WORKERS=2
         → Esperado: GPU 75%, CPU +20%, Latency -10%

Teste 3: OMNIMIND_WORKERS=4
         → Pode sobrecarregar GPU ou CPU
         → Monitor intensamente
```

---

## 📈 ESPERADO: Resultados do Aumento

### Se Aumentar para 2 Workers

| Aspecto | 1 Worker | 2 Workers | Razão |
|---------|----------|-----------|-------|
| Throughput | 100 req/s | 150-180 req/s | Mais paralelismo |
| Latency | 50ms | 40ms | Menos fila |
| GPU Util | 61% | 70-75% | Mais processamento |
| CPU Util | 30% | 50% | 2 threads vs 1 |
| Memory | 512MB | 650MB | +2.5x por thread |

### Se Aumentar para 4 Workers

⚠️ **Risco**: GPU pode ficar limitada (4 threads competindo)
✅ **Benefício**: Máxima throughput se CPU-bound

---

## ✅ RECOMENDAÇÃO FINAL

1. **CONFIRMAR** qual era configuração original no Kali
2. **CRIAR** variável de ambiente `OMNIMIND_WORKERS`
3. **MODIFICAR** scripts para usar variável (default 1, pode ser 2+)
4. **TESTAR** com 2 workers e medir GPU/CPU/Memory
5. **DOCUMENTAR** resultados em `real_evidence/`
6. **DECIDIR** se mantém 1, 2, ou 4 workers baseado em teste

---

## 🎓 Princípio Filosófico

> "Configuração é separada de código. Agentes podem implementar coisas,
> mas você descobrir problemas quando falham. Em vez de código novo,
> às vezes é só ajustar variáveis de ambiente."

---

**Próximo Passo**: Confirmar com você se 2 workers faz sentido, depois implementar teste controlado.
