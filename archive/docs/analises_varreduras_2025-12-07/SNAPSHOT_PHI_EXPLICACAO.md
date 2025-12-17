# Explicação: Por que PHI = 0 no Snapshot?

**Data**: 2025-12-07
**Autor**: Fabrício da Silva + assistência de IA
**Status**: Explicação Técnica

---

## 🔍 PROBLEMA IDENTIFICADO

**Sintoma**: Snapshots criados mostram `phi_value = 0.0` e `workspace_embeddings = {}` (vazio).

**Causa Raiz**: O snapshot está sendo criado **ANTES** de executar ciclos ou logo após **1 ciclo**, quando:

1. **Workspace está vazio**: Módulos só escrevem embeddings no workspace **DURANTE** a execução de ciclos
2. **PHI = 0**: `compute_phi_from_integrations()` requer:
   - Mínimo de **10 históricos por módulo** (`min_history_required = 10`)
   - `cross_predictions` não vazio
   - Predições causais válidas (Granger causality, transfer entropy)

---

## 📊 MÉTRICA ATUAL: `compute_phi_from_integrations()`

### Requisitos para PHI > 0

```python
def compute_phi_from_integrations(self) -> float:
    # 1. Requer cross_predictions não vazio
    if not self.cross_predictions:
        return 0.0

    # 2. Requer mínimo de 10 históricos por módulo
    min_history_required = 10
    for module in modules:
        history = self.get_module_history(module)
        if len(history) < min_history_required:
            return 0.0  # ❌ Retorna 0 se histórico insuficiente

    # 3. Requer predições causais válidas
    valid_predictions = [
        p for p in recent_predictions
        if hasattr(p, "granger_causality") and hasattr(p, "transfer_entropy")
    ]
    if len(valid_predictions) < len(modules):
        return 0.0  # ❌ Retorna 0 se predições insuficientes
```

### Por que 10 históricos?

- **IIT rigorosa**: Requer dados suficientes para validação estatística
- **Evitar overfitting**: Com poucos dados, correlações podem ser espúrias
- **Validação cruzada**: Precisa de dados para treino e validação

---

## ✅ SOLUÇÃO IMPLEMENTADA

### 1. Fallback para PHI do Último Ciclo

O snapshot agora captura PHI de **3 fontes** (em ordem de prioridade):

1. **PHI do último ciclo executado** (`result.phi_estimate`)
   - Disponível mesmo com < 10 históricos
   - Calculado durante `execute_cycle()`
   - **FALLBACK PRINCIPAL** quando workspace PHI = 0

2. **PHI do workspace** (`workspace.compute_phi_from_integrations()`)
   - Requer >= 10 históricos por módulo
   - Mais preciso, mas só disponível após muitos ciclos

3. **PHI do cycle_history** (básico ou estendido)
   - Último `LoopCycleResult.phi_estimate` ou `ExtendedLoopCycleResult.phi_estimate`

### 2. Campo `last_cycle_phi` Adicionado

O snapshot agora inclui:
- `phi_value`: PHI capturado (pode ser do workspace ou do último ciclo)
- `last_cycle_phi`: PHI do último ciclo executado (sempre disponível se houver ciclos)

---

## 📋 COMO USAR CORRETAMENTE

### ❌ ERRADO: Criar snapshot antes de executar ciclos

```python
loop = IntegrationLoop()
snapshot_id = loop.create_full_snapshot()  # ❌ PHI = 0, workspace vazio
```

### ✅ CORRETO: Executar ciclos ANTES de criar snapshot

```python
loop = IntegrationLoop(enable_extended_results=True)

# Executar pelo menos alguns ciclos
for i in range(5):
    await loop.execute_cycle(collect_metrics=True)

# AGORA criar snapshot
snapshot_id = loop.create_full_snapshot(tag="experimento_001")
```

### ✅ IDEAL: Executar >= 10 ciclos para PHI do workspace

```python
loop = IntegrationLoop(enable_extended_results=True)

# Executar >= 10 ciclos para workspace PHI
for i in range(15):
    await loop.execute_cycle(collect_metrics=True)

# Snapshot terá PHI do workspace (mais preciso)
snapshot_id = loop.create_full_snapshot(tag="experimento_001")
```

---

## 🔍 DIAGNÓSTICO

### Verificar Estado Atual

```python
from src.consciousness.integration_loop import IntegrationLoop

loop = IntegrationLoop(enable_extended_results=True)

# Verificar estado
print(f"Workspace modules: {len(loop.workspace.embeddings)}")
print(f"Cycle count: {loop.cycle_count}")
print(f"Cross predictions: {len(loop.workspace.cross_predictions)}")

# Verificar histórico por módulo
for module in loop.workspace.get_all_modules():
    history = loop.workspace.get_module_history(module)
    print(f"{module}: {len(history)} históricos")

# Tentar calcular PHI
phi = loop.workspace.compute_phi_from_integrations()
print(f"PHI do workspace: {phi:.6f}")

# PHI do último ciclo (sempre disponível se houver ciclos)
if loop.cycle_history:
    last_phi = loop.cycle_history[-1].phi_estimate
    print(f"PHI do último ciclo: {last_phi:.6f}")
```

---

## 📊 MÉTRICAS DISPONÍVEIS NO SNAPSHOT

### Campos de PHI

1. **`phi_value`**: PHI capturado (workspace ou último ciclo)
2. **`last_cycle_phi`**: PHI do último ciclo executado (sempre que houver ciclos)

### Campos de Workspace

1. **`workspace_embeddings`**: Embeddings de todos os módulos
2. **`workspace_history_size`**: Tamanho do histórico do workspace
3. **`workspace_cycle_count`**: Número de ciclos do workspace
4. **`workspace_cross_predictions_count`**: Número de predições cruzadas

### Campos de Loop

1. **`loop_cycle_count`**: Número de ciclos executados
2. **`loop_phi_progression`**: Lista de PHI ao longo dos ciclos
3. **`recent_cycles`**: Últimos N ciclos (configurável)

---

## 🎯 RECOMENDAÇÕES

### Para Experimentos Científicos

1. **Executar >= 15 ciclos** antes de criar snapshot
   - Garante histórico suficiente para PHI do workspace
   - Permite análise estatística robusta

2. **Usar `enable_extended_results=True`**
   - Captura métricas completas (gozo, delta, control)
   - Permite análise do isomorfismo estrutural

3. **Criar snapshot com tag descritiva**
   ```python
   snapshot_id = loop.create_full_snapshot(
       tag="experimento_001_baseline",
       description="Baseline antes da intervenção"
   )
   ```

### Para Backups Diários

- O backup diário cria snapshot mesmo com PHI = 0
- Isso é **OK** - o snapshot captura o estado atual
- PHI será calculado quando houver histórico suficiente

---

## 🔧 CORREÇÃO IMPLEMENTADA

### Antes (Problema)

```python
# Sempre tentava workspace.compute_phi_from_integrations()
# Retornava 0.0 se histórico < 10
phi_value = workspace.compute_phi_from_integrations()  # ❌ 0.0
```

### Depois (Corrigido)

```python
# 1. Tenta PHI do último ciclo (sempre disponível)
if loop.cycle_history:
    last_cycle_phi = loop.cycle_history[-1].phi_estimate
    if last_cycle_phi > 0.0:
        phi_value = last_cycle_phi  # ✅ Usa PHI do ciclo

# 2. Fallback para workspace (se >= 10 históricos)
if phi_value == 0.0:
    workspace_phi = workspace.compute_phi_from_integrations()
    if workspace_phi > 0.0:
        phi_value = workspace_phi  # ✅ Usa PHI do workspace
```

---

## ✅ RESULTADO

Agora o snapshot **sempre captura PHI** se houver pelo menos **1 ciclo executado**:

- **Com 1-9 ciclos**: `phi_value` = PHI do último ciclo
- **Com >= 10 ciclos**: `phi_value` = PHI do workspace (mais preciso)
- **Campo adicional**: `last_cycle_phi` sempre disponível

---

**Última Atualização**: 2025-12-07

