# Correções de Imports e Dependências - 13 de Dezembro de 2025

## 📊 Resumo

- **Status**: ✅ RESOLVIDO
- **Problemas Corrigidos**: 3 erros de import + 1 circular import
- **Dependências Instaladas**: 3 pacotes
- **Arquivos Modificados**: 5 arquivos

---

## 🔧 Problemas Identificados e Corrigidos

### 1. ❌ Circular Import: `agents.py` ↔ `agent_monitor.py`

**Erro Original**:
```
cannot import name 'AgentStatus' from partially initialized module 'web.backend.routes.agents'
(most likely due to a circular import)
```

**Causa**:
```
agents.py (linha 19) → importa agent_monitor
agent_monitor.py (linha 13) → importa AgentStatus, AgentType de agents.py
↑ CIRCULAR!
```

**Solução**: ✅ IMPLEMENTADA
- Criado novo arquivo: `web/backend/routes/enums.py`
- Movidas classes `AgentStatus` e `AgentType` para `enums.py`
- Atualizado `agents.py` para importar de `enums.py`
- Atualizado `agent_monitor.py` para importar de `enums.py`
- Atualizado `tests/test_agent_monitor.py` para importar de `enums.py`

**Arquivos Afetados**:
- ✅ `web/backend/routes/enums.py` (NOVO - 26 linhas)
- ✅ `web/backend/routes/agents.py` (linhas 1-27)
- ✅ `web/backend/monitoring/agent_monitor.py` (linhas 1-13)
- ✅ `tests/test_agent_monitor.py` (linhas 1-8)

**Validação**:
```python
from web.backend.routes.agents import AgentStatus
from web.backend.monitoring.agent_monitor import AgentMonitor
# ✅ Sem circular dependency!
```

---

### 2. ❌ Cache de Transformers: Matching Impreciso

**Erro Original**:
```
sentence-transformers/all-MiniLM-L6-v2: ❌ Não encontrado
all-MiniLM-L6-v2: ✅ cache
```

**Problema**: O offline_mode.py procurava por nome exato mas não normalizava caminhos

**Solução**: ✅ IMPLEMENTADA
- Adicionada função `normalize_model_name()` que remove prefixos (sentence-transformers/)
- Melhorado matching com `case-insensitive` comparação
- Atualizado `get_model_path()` para normalizar nomes

**Arquivo Afetado**:
- ✅ `src/utils/offline_mode.py` (linhas 55-95 + 98-120)

**Mudanças**:
```python
# Antes
if any(model_name in m for m in cache_models):

# Depois
def normalize_model_name(name: str) -> str:
    return name.split("/")[-1].lower()  # Remove prefixo

for cached_model in cache_models:
    if normalized_search in normalize_model_name(cached_model):
        # Match flexível!
```

---

### 3. ❌ ModuleNotFoundError: `playwright`

**Erro Original**:
```
ERROR collecting tests/manual/test_playwright_direct.py
ModuleNotFoundError: No module named 'playwright'
```

**Dependências Afetadas**:
- `tests/manual/test_playwright_direct.py` - linha 3
- `tests/manual/test_ui_integration.py` - linha 4

**Solução**: ✅ INSTALADA
```bash
pip install playwright
# Result: playwright 1.57.0 instalado
```

---

### 4. ❌ ModuleNotFoundError: `opentelemetry.exporter`

**Erro Original**:
```
ERROR collecting tests/test_enhanced_observability.py
ModuleNotFoundError: No module named 'opentelemetry.exporter'
```

**Dependências Afetadas**:
- `tests/test_enhanced_observability.py` - linha 11
- `src/observability/opentelemetry_integration.py` - linha 14

**Solução**: ✅ INSTALADAS
```bash
pip install opentelemetry-exporter-otlp-proto-grpc opentelemetry-exporter-otlp
# Result:
#   opentelemetry-exporter-otlp 1.39.1
#   opentelemetry-exporter-otlp-proto-grpc 1.39.1
```

---

### 5. ✅ qiskit-ibm-runtime já Instalado

**Status**: Já foi instalado na etapa anterior

```bash
pip list | grep qiskit
# Result: qiskit-ibm-runtime 0.24.0 (já instalado)
```

---

## 📦 Dependências Instaladas (Sessão 13/12/2025)

| Pacote | Versão | Propósito |
|--------|--------|----------|
| pytest-html | 4.1.1 | Geração de relatórios HTML para testes |
| pytest-mock | 3.15.1 | Fixture `mocker` para mocking em testes |
| qiskit-ibm-runtime | 0.24.0 | Runtime IBM Quantum para validação real em QPU |
| playwright | 1.57.0 | Automação de UI para testes end-to-end |
| opentelemetry-exporter-otlp | 1.39.1 | Observabilidade distribuída (traces/metrics) |
| opentelemetry-exporter-otlp-proto-grpc | 1.39.1 | GRPC exporter para OpenTelemetry |

---

## ✅ Validações Executadas

### 1. Compile Check
```bash
python -m py_compile \
  web/backend/routes/enums.py \
  web/backend/routes/agents.py \
  web/backend/monitoring/agent_monitor.py \
  src/utils/offline_mode.py \
  tests/test_agent_monitor.py
# Result: ✅ Todos compilam sem erros
```

### 2. Circular Import Test
```python
from web.backend.routes.agents import AgentStatus, AgentType
from web.backend.monitoring.agent_monitor import AgentMonitor
# Result: ✅ Import sem circular dependency
```

### 3. Offline Mode Test
```python
from src.utils.offline_mode import setup_offline_mode
setup_offline_mode()
# Result: ✅ Models encontrados e normalizados corretamente
```

### 4. Import Dependencies Test
```python
from playwright.async_api import async_playwright
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
# Result: ✅ Todos os imports resolvidos
```

---

## 📋 Arquivos Modificados

### Novos Arquivos
- ✅ `web/backend/routes/enums.py` (26 linhas - enum centralizadas)

### Arquivos Alterados
| Arquivo | Linhas | Mudança |
|---------|--------|---------|
| web/backend/routes/agents.py | 1-27 | Remover enums, importar de enums.py |
| web/backend/monitoring/agent_monitor.py | 1-13 | Atualizar import de agents → enums |
| src/utils/offline_mode.py | 55-95, 98-120 | Melhorar matching de modelos |
| tests/test_agent_monitor.py | 1-8 | Atualizar import de agents → enums |

---

## 🚀 Próximos Passos

1. **Executar testes novamente**:
   ```bash
   ./scripts/run_tests_fast.sh
   ```

2. **Validar suite completa**:
   ```bash
   python -m pytest tests/ -v --tb=short -m "not chaos"
   ```

3. **Executar validação científica (opcional)**:
   ```bash
   python scripts/science_validation/robust_consciousness_validation.py --quick
   ```

4. **Testar QPU IBM (após validação)**:
   ```bash
   python -c "from src.quantum_consciousness.auto_ibm_loader import detect_and_load_ibm_backend; detect_and_load_ibm_backend()"
   ```

---

## 📊 Resumo de Correções

| Item | Status | Detalhes |
|------|--------|----------|
| Circular Import | ✅ RESOLVIDO | Enums centralizadas em enums.py |
| Cache de Modelos | ✅ CORRIGIDO | Matching normalizado e case-insensitive |
| playwright | ✅ INSTALADO | 1.57.0 |
| opentelemetry | ✅ INSTALADO | 1.39.1 + proto-grpc |
| qiskit-ibm-runtime | ✅ VERIFICADO | 0.24.0 (pronto para QPU) |
| pytest-html | ✅ INSTALADO | 4.1.1 (relatórios HTML) |
| pytest-mock | ✅ INSTALADO | 3.15.1 (mocker fixture) |

---

## 🎯 Estado Final

✅ **Todos os imports resolvidos**
✅ **Circular dependency eliminada**
✅ **Todas as dependências instaladas**
✅ **Sistema pronto para executar suite de testes completa**
✅ **QPU IBM Runtime disponível para validação real**

**Data**: 13 de Dezembro de 2025
**Status**: COMPLETO
