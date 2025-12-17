# 📋 PLANO: Análise de Logs e Classificação Dinâmica de Erros

**Data**: 2025-12-07
**Autor**: Fabrício da Silva + assistência de IA
**Status**: ⏳ PLANEJAMENTO

---

## 🎯 OBJETIVO

Verificar e atualizar scripts de análise de logs para classificação dinâmica de diversos tipos de erros:
- ✅ `fail`, `failed` (já suportado)
- ❌ `entropy warning` (NÃO suportado)
- ❌ `meta cognition analysis/action failed` (NÃO suportado - não executar testes)

Verificar se logs têm debug suficiente para análise completa.

---

## 📊 SITUAÇÃO ATUAL

### Scripts de Análise Encontrados:

1. **`scripts/analyze_test_log.py`** ✅
   - Classifica: `FAILED`, `ERROR`, `SKIPPED`, `PASSED`
   - Padrões de erro: `CUDA_OOM`, `AttributeError`, `TimeoutError`, `ConnectionError`, `AssertionError`, `ModuleNotFound`, `PhiCollapse`, `StructuralFailure`
   - ❌ **FALTA**: `entropy warning`, `meta cognition analysis/action failed`

2. **`scripts/omnimind_log_forensics.py`** ✅
   - Análise forense profunda
   - Métricas de consciência (Φ, ICI, PRS)
   - Tracebacks completos
   - ❌ **FALTA**: `entropy warning`, `meta cognition analysis/action failed`

3. **`scripts/utilities/analysis/analyze_logs.py`** ✅
   - Padrões: `error`, `warning`, `exception`, `resource_state`, `task_failure`
   - ❌ **FALTA**: `entropy warning`, `meta cognition analysis/action failed`

### Tipos de Erros do Teste Atual (45 failed):

1. **AssertionError** (maioria):
   - `assert False`
   - `assert X == Y`
   - `AssertionError: assert {...} == {...}`

2. **AttributeError**:
   - `'IntegrationTrainer' object has no attribute 'integration_l...'`

3. **ValueError**:
   - `Embedding for conscious_module has wrong shape: (256,) != (768,)`

4. **torch.OutOfMemoryError**:
   - `CUDA out of memory. Tried to allocate 46.00 MiB`

5. **TimeoutError** (já tratado como medição)

---

## 🔍 ANÁLISE NECESSÁRIA

### 1. Entropy Warning
**Onde procurar**:
- `src/consciousness/` - cálculos de entropia
- `src/metrics/` - métricas de entropia
- Logs com padrão: `entropy.*warning|WARNING.*entropy`

**Padrão esperado**:
```python
# Exemplo de log esperado:
"WARNING: Entropy threshold exceeded: entropy=0.95 (threshold=0.9)"
"WARNING [entropy]: High entropy detected in module X"
```

### 2. Meta Cognition Analysis/Action Failed
**Onde procurar**:
- `src/metacognition/metacognition_agent.py`
- `src/agents/orchestrator_agent.py` - método `run_metacognition_analysis`
- Logs com padrão: `meta.*cogn.*analysis.*failed|meta.*cogn.*action.*failed`

**Padrão esperado**:
```python
# Exemplo de log esperado:
"ERROR: Metacognition analysis failed: <reason>"
"WARNING: Metacognition action failed: <action> - skipping tests"
"Metacognition analysis failed: <error> - not executing tests"
```

**Comportamento esperado**: ❌ **NÃO EXECUTAR TESTES** quando detectado

---

## 📝 PLANO DE AÇÃO

### FASE 1: Verificação de Logs (Debug Suficiente)

#### 1.1 Verificar Nível de Debug nos Logs
- [ ] Verificar `config/pytest.ini` - `--log-cli-level=DEBUG`
- [ ] Verificar `scripts/run_tests_fast.sh` - logs verbosos
- [ ] Verificar se logs contêm:
  - Stack traces completos
  - Contexto de execução
  - Valores de variáveis críticas
  - Timestamps precisos

#### 1.2 Verificar Padrões de Log
- [ ] Buscar `entropy.*warning` nos logs existentes
- [ ] Buscar `meta.*cogn.*analysis.*failed` nos logs existentes
- [ ] Verificar se padrões estão sendo logados corretamente

**Comando de verificação**:
```bash
# Verificar se entropy warnings estão nos logs
grep -r "entropy.*warning\|WARNING.*entropy" data/test_reports/ --include="*.log" -i

# Verificar se meta cognition failures estão nos logs
grep -r "meta.*cogn.*analysis.*failed\|meta.*cogn.*action.*failed" data/test_reports/ --include="*.log" -i
```

---

### FASE 2: Atualização de Scripts de Análise

#### 2.1 Atualizar `scripts/analyze_test_log.py`

**Adicionar padrões**:
```python
error_patterns = {
    # ... padrões existentes ...
    'EntropyWarning': r'entropy.*warning|WARNING.*entropy|entropy.*threshold.*exceeded',
    'MetacognitionAnalysisFailed': r'meta.*cogn.*analysis.*failed|metacognition.*analysis.*failed',
    'MetacognitionActionFailed': r'meta.*cogn.*action.*failed|metacognition.*action.*failed',
}
```

**Adicionar classificação especial**:
```python
# Se MetacognitionAnalysisFailed ou MetacognitionActionFailed detectado:
# → Marcar como CRITICAL
# → Sugerir: "NÃO EXECUTAR TESTES - Meta cognition failure detected"
```

#### 2.2 Atualizar `scripts/omnimind_log_forensics.py`

**Adicionar ao PATTERNS**:
```python
'entropy_warning': re.compile(r'entropy.*warning|WARNING.*entropy|entropy.*threshold.*exceeded', re.IGNORECASE),
'metacognition_analysis_failed': re.compile(r'meta.*cogn.*analysis.*failed|metacognition.*analysis.*failed', re.IGNORECASE),
'metacognition_action_failed': re.compile(r'meta.*cogn.*action.*failed|metacognition.*action.*failed', re.IGNORECASE),
```

**Adicionar contadores**:
```python
self.metacognition_failures = {
    'analysis_failed': 0,
    'action_failed': 0,
    'entropy_warnings': 0,
}
```

#### 2.3 Atualizar `scripts/utilities/analysis/analyze_logs.py`

**Adicionar padrões**:
```python
self.patterns = {
    # ... padrões existentes ...
    "entropy_warning": re.compile(r"entropy.*warning|WARNING.*entropy", re.IGNORECASE),
    "metacognition_failure": re.compile(
        r"meta.*cogn.*(?:analysis|action).*failed|metacognition.*(?:analysis|action).*failed",
        re.IGNORECASE
    ),
}
```

**Adicionar detecção de anomalias**:
```python
# Se metacognition_failure detectado:
# → Severidade: CRITICAL
# → Recomendação: "NÃO EXECUTAR TESTES - Meta cognition failure detected"
```

---

### FASE 3: Classificação Dinâmica

#### 3.1 Criar Sistema de Classificação Dinâmica

**Arquivo**: `scripts/utilities/analysis/dynamic_error_classifier.py`

```python
class DynamicErrorClassifier:
    """Classificador dinâmico de erros baseado em padrões."""

    ERROR_CATEGORIES = {
        'ASSERTION': ['AssertionError', 'assert False', 'assert X == Y'],
        'ATTRIBUTE': ['AttributeError', 'object has no attribute'],
        'VALUE': ['ValueError', 'wrong shape', 'invalid value'],
        'MEMORY': ['CUDA out of memory', 'OutOfMemoryError'],
        'TIMEOUT': ['TimeoutError', 'TIMEOUT', 'timed out'],
        'ENTROPY_WARNING': ['entropy.*warning', 'WARNING.*entropy', 'entropy.*threshold'],
        'METACOGNITION_ANALYSIS_FAILED': ['meta.*cogn.*analysis.*failed', 'metacognition.*analysis.*failed'],
        'METACOGNITION_ACTION_FAILED': ['meta.*cogn.*action.*failed', 'metacognition.*action.*failed'],
    }

    CRITICAL_CATEGORIES = [
        'METACOGNITION_ANALYSIS_FAILED',
        'METACOGNITION_ACTION_FAILED',
    ]

    def classify_error(self, error_message: str) -> Dict[str, Any]:
        """Classifica erro dinamicamente."""
        # ...
```

#### 3.2 Integrar com Scripts Existentes

- [ ] Integrar `DynamicErrorClassifier` em `analyze_test_log.py`
- [ ] Integrar em `omnimind_log_forensics.py`
- [ ] Integrar em `analyze_logs.py`

---

### FASE 4: Comportamento "Não Executar Testes"

#### 4.1 Detecção Pré-Teste

**Arquivo**: `scripts/pre_test_validation.py`

```python
def check_metacognition_health() -> bool:
    """Verifica saúde de meta cognição antes de executar testes."""
    # Se meta cognition analysis/action failed:
    # → Retornar False
    # → Logar: "CRITICAL: Meta cognition failure detected - NOT EXECUTING TESTS"
    # → Exit com código especial
```

#### 4.2 Integração com Scripts de Teste

- [ ] Atualizar `scripts/run_tests_fast.sh` para verificar meta cognição antes
- [ ] Atualizar `scripts/run_tests_with_defense.sh` para verificar meta cognição antes

---

## 🔍 VERIFICAÇÃO DE DEBUG SUFICIENTE

### Checklist de Debug:

- [ ] **Stack Traces Completos**: ✅ (pytest --tb=long)
- [ ] **Contexto de Execução**: ✅ (--log-cli-level=DEBUG)
- [ ] **Valores de Variáveis**: ⚠️ (verificar se suficiente)
- [ ] **Timestamps Precisos**: ✅ (datetime nos logs)
- [ ] **Métricas de Consciência**: ✅ (Φ, ICI, PRS)
- [ ] **Estado do Sistema**: ⚠️ (verificar se suficiente)

### Comandos de Verificação:

```bash
# Verificar nível de debug
grep "log-cli-level" scripts/run_tests_fast.sh

# Verificar se logs têm stack traces
grep -c "Traceback" data/test_reports/pytest_fast_*.log

# Verificar se logs têm métricas
grep -c "phi\|ICI\|PRS" data/test_reports/pytest_fast_*.log
```

---

## 📊 PRIORIDADES

### 🔴 ALTA PRIORIDADE:
1. ✅ Verificar se `entropy warning` está sendo logado
2. ✅ Verificar se `meta cognition analysis/action failed` está sendo logado
3. ✅ Adicionar padrões aos scripts de análise
4. ✅ Implementar comportamento "não executar testes"

### 🟡 MÉDIA PRIORIDADE:
1. ⚠️ Melhorar debug de valores de variáveis
2. ⚠️ Melhorar debug de estado do sistema
3. ⚠️ Criar classificador dinâmico

### 🟢 BAIXA PRIORIDADE:
1. ⚠️ Otimizar performance de análise
2. ⚠️ Adicionar visualizações

---

## 📝 PRÓXIMOS PASSOS

1. **Executar verificação de logs** (FASE 1)
2. **Atualizar scripts de análise** (FASE 2)
3. **Implementar classificador dinâmico** (FASE 3)
4. **Implementar comportamento "não executar testes"** (FASE 4)

---

**Última Atualização**: 2025-12-07
**Status**: ⏳ Aguardando aprovação para execução

