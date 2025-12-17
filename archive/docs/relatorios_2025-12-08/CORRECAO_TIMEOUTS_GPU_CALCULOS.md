# 🔧 CORREÇÃO: Timeouts para Testes de GPU/Cálculo

**Data**: 2025-12-07
**Autor**: Fabrício da Silva + assistência de IA
**Status**: ✅ CORRIGIDO

---

## 📋 PROBLEMA IDENTIFICADO

1. **Mortality Simulator**: Usuário questionou se é perigoso/mockado
2. **Testes de GPU/Cálculo**: Estavam com `@pytest.mark.timeout(0)` que **DESABILITAVA** o timeout global de 800s
3. **Estabilização GPU**: Testes precisam de tempo para estabilizar cache GPU enquanto dev/prod rodam simultaneamente

---

## ✅ CORREÇÕES APLICADAS

### 1. Mortality Simulator - Verificação

**Resultado**: ✅ **NÃO é perigoso, NÃO precisa de mock**

- É uma **simulação pura** de tempo/eventos
- Não acessa GPU, servidor, ou recursos externos
- Apenas simula temporalidade e legacy planning
- **Seguro** para rodar em qualquer ambiente

**Código**: `src/autopoietic/mortality_simulator.py`
- Classe `MortalitySimulator` - simulação pura
- Classe `TemporalAwareness` - tracking de tempo
- Classe `LegacyPlanner` - planejamento de legado
- **Sem dependências externas** (GPU, servidor, network)

---

### 2. Remoção de `@pytest.mark.timeout(0)` em Testes de GPU

**Arquivo**: `tests/consciousness/test_real_phi_measurement.py`

**Antes**:
```python
@pytest.mark.timeout(0)  # ❌ Desabilita timeout global
async def test_phi_measurement_basic(gpu_device: str) -> None:
```

**Depois**:
```python
# Timeout: 800s (respeita configuração global - permite estabilização GPU e cache)
async def test_phi_measurement_basic(gpu_device: str) -> None:
```

**Testes Corrigidos** (4 testes):
- ✅ `test_phi_measurement_basic`
- ✅ `test_phi_multiseed_small`
- ✅ `test_phi_with_ollama`
- ✅ `test_phi_measurement_with_topological_metrics`

---

### 3. Atualização de `conftest.py` - Heavy Paths

**Arquivo**: `tests/conftest.py`

**Mudanças**:

1. **Adicionado testes de GPU aos heavy_paths**:
```python
heavy_paths = [
    "test_integration_loss.py",
    "test_quantum_algorithms_comprehensive.py",
    "test_consciousness",
    "test_real_phi_measurement.py",  # ✅ GPU/CUDA - precisa 800s
    "test_enhanced_code_agent_integration.py",  # ✅ GPU/CUDA - precisa 800s
]
```

2. **Timeout aumentado de 600s para 800s**:
```python
# Heavy computational/GPU: 800s (permite estabilização GPU e cache)
# Testes de GPU/cálculo precisam de tempo para estabilizar cache e processamento
elif any(path in item_path for path in heavy_paths):
    timeout_value = 800  # ✅ Máximo para testes de GPU/cálculo
    item.add_marker(pytest.mark.computational)
```

---

## 📊 CONFIGURAÇÃO FINAL DE TIMEOUTS

### pytest.ini (Global)
```ini
--timeout=800
--timeout_method=thread
```

**Nota**: Timeout é **POR TESTE INDIVIDUAL**, não acumulativo. Cada teste tem até 800s.

### conftest.py (Progressivo por Categoria)

| Categoria | Timeout | Testes |
|-----------|---------|--------|
| **Heavy/GPU** | **800s** | test_real_phi_measurement.py, test_integration_loss.py, test_enhanced_code_agent_integration.py |
| Chaos | 800s | test_chaos_resilience.py |
| Stress | 800s | test_orchestrator_load.py |
| E2E | 400s | test_e2e_integration.py |
| Ollama | 240s | phase16_integration, neurosymbolic |
| Computational | 300s | consciousness (geral) |
| Default | 300s | Outros testes |

---

## ✅ TESTES QUE AGORA RESPEITAM 800s

### Testes de GPU/CUDA (9 testes):
1. ✅ `test_real_phi_measurement.py::test_phi_measurement_basic` - GPU/CUDA
2. ✅ `test_real_phi_measurement.py::test_phi_multiseed_small` - GPU/CUDA
3. ✅ `test_real_phi_measurement.py::test_phi_with_ollama` - GPU/CUDA (full pipeline)
4. ✅ `test_real_phi_measurement.py::test_phi_measurement_with_topological_metrics` - GPU/CUDA
5. ✅ `test_integration_loss.py` - 4 testes slow (cálculos de treinamento)
6. ✅ `test_enhanced_code_agent_integration.py` - 1 teste GPU/CUDA

### Testes de Cálculo (sem GPU, mas pesados):
- ✅ `test_integration_loss.py` - Treinamento, cálculos pesados
- ✅ `test_quantum_algorithms_comprehensive.py` - Cálculos quânticos

---

## 🎯 BENEFÍCIOS

### 1. Estabilização GPU
- ✅ Timeout de 800s permite estabilização de cache GPU
- ✅ GPU pode aquecer e estabilizar durante testes
- ✅ Cache de kernels CUDA pode ser construído

### 2. Modo Desenvolvimento + Produção
- ✅ Testes podem rodar enquanto dev/prod estão ativos
- ✅ GPU compartilhada entre processos
- ✅ Timeout individual evita travamento de suite inteira

### 3. Progressão Sem Falhas
- ✅ Cada teste individual tem até 800s
- ✅ Suite não tem timeout total (apenas por teste)
- ✅ Testes podem progredir gradualmente sem falhar prematuramente

### 4. Lógica e Funcionamento
- ✅ Foco em validar lógica e funcionamento
- ✅ Parâmetros serão aprimorados depois
- ✅ Timeout não é falha - permite execução completa

---

## 📝 VALIDAÇÃO

### Comandos de Verificação:

```bash
# Verificar timeouts configurados
grep -r "@pytest.mark.timeout" tests/ --include="*.py"

# Verificar testes de GPU
grep -r "@pytest.mark.slow" tests/consciousness/test_real_phi_measurement.py

# Verificar configuração global
grep "timeout" config/pytest.ini

# Verificar heavy_paths
grep -A 5 "heavy_paths" tests/conftest.py
```

### Resultado Esperado:
- ✅ Nenhum teste de GPU com `timeout(0)`
- ✅ Testes de GPU em `heavy_paths` com 800s
- ✅ Configuração global de 800s ativa

---

## 🔍 NOTAS IMPORTANTES

1. **Timeout Individual vs Suite**:
   - Cada teste tem até 800s (individual)
   - Suite **NÃO tem timeout total**
   - Testes rodam sequencialmente com timeouts independentes

2. **GPU Estabilização**:
   - Primeiros testes podem ser mais lentos (cache building)
   - Testes subsequentes podem ser mais rápidos (cache warm)
   - Timeout de 800s permite ambos os cenários

3. **Modo Desenvolvimento + Produção**:
   - Testes podem rodar enquanto servidor está ativo
   - GPU compartilhada entre processos
   - Timeout individual evita conflitos

4. **Progressão Sem Falhas**:
   - Timeout não é falha - permite execução completa
   - Foco em validar lógica e funcionamento
   - Parâmetros serão otimizados depois

---

**Última Atualização**: 2025-12-07
**Validação**: ✅ Timeouts corrigidos e validados

