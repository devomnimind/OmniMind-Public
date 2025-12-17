# Configuração de Timeouts - OmniMind

## ⏱️ Modelo de Timeout Progressivo

Os testes do OmniMind usam um modelo de **timeout PROGRESSIVO POR TESTE INDIVIDUAL**, não timeout global acumulativo.

### Estrutura

```
┌─────────────────────────────────────────────────────────┐
│ PYTEST SESSION (todos os testes)                         │
├─────────────────────────────────────────────────────────┤
│ Test 1: test_phase16_integration                        │
│ ├─ Timeout Individual: 240s (primeira tentativa)        │
│ ├─ Pode ser retentado até: 240→400→600→800s (adaptativo)│
│ └─ Servidor startup: 120-180s (cycle_timeout=180)       │
│                                                          │
│ Test 2: test_heavy_computational                        │
│ ├─ Timeout Individual: 600s                             │
│ └─ ...                                                   │
│                                                          │
│ Test N: test_simple                                     │
│ ├─ Timeout Individual: 30s (default)                    │
│ └─ ...                                                   │
└─────────────────────────────────────────────────────────┘
```

**Importante**: Cada teste tem seu próprio orçamento de tempo, **não** é acumulativo.

## 🎯 Categorias de Testes e Timeouts

### 1. Testes Ollama/Phase (240s base)

Padrão: `phase16_integration`, `neurosymbolic`, `neural_component`, `cognitive`, `_inference`

```python
# tests/conftest.py - linha 342-347
ollama_paths = [
    "phase16_integration",
    "neurosymbolic",
    "neural_component",
    "free_energy_lacanian",
    "cognitive",
    "_inference",
]
```

**Timeout**: 240s individual (adaptativo até 400s se necessário)

**Razão**: Ollama local em produção é lento
- Modelo `qwen2:7b-instruct` tipicamente leva 60-100s por chamada
- Servidor OmniMind startup: 120-180s
- Buffer para integração completa: 240s

### 2. Testes E2E (400s base)

Padrão: `test_e2e_integration`, `test_dashboard_live`, `test_endpoint`

**Timeout**: 400s individual (adaptativo até 600s)

### 3. Testes Pesados/Computacionais (600s base)

Padrão: `consciousness`, `quantum_consciousness`, `quantum_ai`

**Timeout**: 600s individual (adaptativo até 800s)

### 4. Chaos Tests (800s máximo)

Padrão: `test_chaos_resilience`

**Timeout**: 800s individual (máximo permitido)

**Razão**: Destrução intencional de servidor + recovery

### 5. Testes Padrão (300s base)

Todos os outros

**Timeout**: 300s individual

## 🔄 Mecânica do Server Monitor

[ver: tests/plugins/pytest_server_monitor.py]

### Ciclo de Startup

```
1. Inicia servidor via script
   └─ timeout do script: 240s (aumentado para ambiente híbrido)

2. Aguarda servidor ficar saudável
   ├─ cycle_timeout: 240s (aguarda uma vez, aumentado para ambiente híbrido)
   ├─ Se OK: sucesso ✅
   └─ Se timeout: reinicia e retenta

3. Loop com restart intermediário
   ├─ total_timeout = _get_adaptive_timeout() (240-800s)
   ├─ Se elapsed_total >= total_timeout: erro final
   └─ Senão: volta a passo 1 (restart)
```

### Timeouts Adaptativos por Tentativa

```python
# tests/plugins/pytest_server_monitor.py - linha ~421
timeout_progression = [
    220,   # Tentativa 1: 220s (Orchestrator + SecurityAgent startup)
    400,   # Tentativa 2: 400s (recovery time para múltiplos ciclos)
    600,   # Tentativa 3: 600s (permite 3+ ciclos completos)
    800,   # Tentativa 4+: 800s (máximo)
]
```

**Aplicação**:
- Test 1 recebe index 0 → 220s total
- Se Test 1 derrubar servidor → Test 2 recebe index 1 → 400s total
- Se Test 2 derrubar servidor → Test 3 recebe index 2 → 600s total
- Etc.

## ⚙️ Configuração do pytest.ini

```ini
# config/pytest.ini - linha 35-36
addopts =
    --timeout=800
    --timeout_method=thread
```

**Nota**: Esse `--timeout=800` é complementar, não é o timeout real que controla testes.
O timeout real vem do marcador `@pytest.mark.timeout(valor)` adicionado dinamicamente.

## 📊 Motivo da Estrutura Atual

**OmniMind em Produção**:
- Rodando com dados REAIS do SO (filesystem, processos, sensores)
- LLM local (Ollama qwen2:7b) em máquina de desenvolvimento
- Múltiplas atividades simultâneas (VS Code, extensões, agentes, etc.)
- Developing + Science + Production = sistema LENTO

**Timeouts longos são ESPERADOS e CORRETOS**:
- ✅ Não indica falha
- ✅ Indica carga real do sistema
- ⚠️ Será otimizado em fases finais (refino de modelos + tunagem de hardware)

## 🚀 Alternativas para Acelerar (Futuro)

Se precisar acelerar testes antes da fase final:

1. **Usar Phi ao invés de Qwen** (mais leve)
   ```bash
   # Baixar modelo Phi
   ollama pull phi:latest
   # Configurar em .env
   OLLAMA_MODEL=phi:latest
   ```

2. **Usar modo Mock/Semi-Real**
   ```python
   @pytest.mark.mock  # Sem LLM
   @pytest.mark.semi_real  # Sem integração LLM completa
   ```

3. **Parallelize testes independentes**
   ```bash
   pytest -n auto  # Com pytest-xdist
   ```

## ✅ Verificação da Configuração

Para confirmar que testes recebem timeout correto:

```bash
# Veja os timeouts atribuídos
pytest tests/test_phase16_integration.py -v --collect-only | grep -i timeout

# Rode e veja logs de startup
pytest tests/test_phase16_integration.py -v -s --tb=short
```

Procure por:
```
   ⏳ Timeout adaptativo: XXXs (ciclo de restart: 180s)
```

## 📚 Referências

- [pytest-timeout plugin](https://pytest-timeout.readthedocs.io/)
- [tests/plugins/pytest_server_monitor.py](../tests/plugins/pytest_server_monitor.py)
- [tests/conftest.py](../tests/conftest.py) - linhas 330-425
- [config/pytest.ini](../config/pytest.ini)
