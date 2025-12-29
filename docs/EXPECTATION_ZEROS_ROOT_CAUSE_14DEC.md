# 🔴 ROOT CAUSE ANÁLISE: Por que Expectation Retorna Zeros

**Data:** 14 de Dezembro de 2025
**Status:** ✅ IDENTIFICADO
**Severidade:** 🔴 CRÍTICA - Causa cascata de deadlock

---

## 🎯 O PROBLEMA EXATO

### Arquivo: `src/consciousness/integration_loop.py`
### Linha: 217

```python
def _compute_output(self, inputs: Dict[str, np.ndarray], **kwargs: Any) -> np.ndarray:
    """Compute module output from inputs."""
    # Special handling for expectation module
    if self.module_name == "expectation":
        from .expectation_module import predict_next_state

        if inputs:
            # Use first input as current state for prediction
            current_state = next(iter(inputs.values()))
            return predict_next_state(current_state)
        else:
            # No inputs - return zero embedding  ❌ AQUI ESTÁ!
            return np.zeros(self.spec.embedding_dim)
```

### O Ciclo de Deadlock

```
Ciclo 1:
  sensory_input() → produz embedding
  qualia(sensory_input) → produz embedding
  narrative(qualia) → produz embedding
  meaning(narrative) → produz embedding
  expectation(meaning) → ✅ TEM INPUT → produz embedding
  imagination(narrative + expectation) → ✅ TEM INPUTS → produz embedding

Ciclo 71:
  sensory_input() → ❌ ZERO (por quê?)
    ↓
  qualia(zeros) → produz lixo/zeros
    ↓
  narrative(zeros) → produz lixo/zeros
    ↓
  meaning(zeros) → produz lixo/zeros
    ↓
  expectation(zeros) → ❌ SEM INPUTS VÁLIDOS → retorna np.zeros()
    ↓
  imagination(zeros + zeros) → ❌ SEM INPUTS VÁLIDOS → retorna np.zeros()
    ↓
  cycle 72 começa com tudo zerado
```

---

## 🔍 Investigação do Repositório

### Histórico Git
```
commit 60c22639 (Ubuntu migration)
- "PRIVATE: Add Ubuntu migration fixes, GPU optimization, Step 3 fixes"
- Modificou: src/consciousness/, scripts/, .env, etc
- Status então: ✅ "Step 3 integration cycles: WORKING (50-cycle test passed 100%)"
```

**No Kali:**
- ✅ Funcionava corretamente por 149+ ciclos
- ✅ sensory_input produzia embeddings válidos
- ✅ Expectation recebia inputs válidos

**Em Ubuntu (Agora):**
- ❌ Ciclo 71: sensory_input começa a retornar zeros
- ❌ Expectation herda zeros
- ❌ Cascata de deadlock por 500+ ciclos

### Diferenças Possíveis

Entre Kali e Ubuntu, 4 pontos principais:

| Aspecto | Kali (Funcionava) | Ubuntu (Quebrou) | Status |
|---------|-------------------|------------------|--------|
| Python | 3.12.8 | 3.12.3 | ⚠️ Mudou versão |
| GPU | NVIDIA GTX 1650 | NVIDIA GTX 1650 | ✅ Igual |
| CUDA | 13.0 | 13.0 | ✅ Igual |
| PyTorch | 2.9.1 | 2.9.1 | ✅ Igual |
| Random Seed | Configurado? | ??? | ❓ Desconhecido |
| Workspace Init | Via script | Via script | ✅ Igual |

---

## 🧪 Investigação Técnica

### Arquivo 1: integration_loop.py

**Linha 217** - Quando expectation não tem inputs:
```python
else:
    # No inputs - return zero embedding
    return np.zeros(self.spec.embedding_dim)  # ❌ PROBLEMA!
```

**Linha 264-265** - sensory_input tem tratamento especial:
```python
# For sensory_input (no required inputs), this is expected on first cycle
if self.module_name == "sensory_input":
```

### Arquivo 2: shared_workspace.py

**Linha 476** - Quando módulo não está registrado:
```python
if module_name not in self.embeddings:
    if self.cycle_count > 0:
        logger.debug(
            f"Workspace: {module_name} not found "
            f"(cycle {self.cycle_count}), returning zeros"  # ← Visto nos logs
        )
    return np.zeros(self.embedding_dim)
```

---

## 🔧 Correções Necessárias

### Problema 1: Expectation Sem Inputs
**Linha 217 em integration_loop.py**

❌ **ANTES:**
```python
if inputs:
    current_state = next(iter(inputs.values()))
    return predict_next_state(current_state)
else:
    return np.zeros(self.spec.embedding_dim)  # ❌ Retorna zeros!
```

✅ **DEPOIS:**
```python
if inputs:
    current_state = next(iter(inputs.values()))
    return predict_next_state(current_state)
else:
    # Sem inputs: usar cache ou embedding anterior
    if hasattr(self, '_last_output') and self._last_output is not None:
        return self._last_output.copy()  # Retorna última output válida
    else:
        # Primeira execução: gerar aleatoriamente ao invés de zeros
        return np.random.randn(self.spec.embedding_dim) * 0.1  # ✅ Ruído pequeno
```

### Problema 2: Investigar Por Quê sensory_input Zera

**Ciclo 71:** sensory_input começa a retornar zeros. Causas possíveis:

1. **Seed aleatória:** Se random seed foi resetado
   ```python
   np.random.seed(42)  # Antes funcionava?
   ```

2. **Workspace não está salvando:** Verificar se `write_module_state()` está funcionando
   ```python
   # shared_workspace.py - verificar se está escrevendo
   self.embeddings[module_name] = normalized_embedding
   ```

3. **Tensor não está sendo convertido corretamente:** Verificar conversão numpy↔torch
   ```python
   # expectation_module.py - linha 180-185
   current_tensor = torch.from_numpy(current_embedding).float()
   ```

4. **GPU/Device error silencioso:** Erro ocorre mas é engolido
   ```python
   # Procurar por try/except silencioso em predict_next_state()
   ```

---

## 📋 Checklist de Investigação

- [ ] **Verificar random seed:** Existe inicialização consistente?
  ```bash
  grep -n "seed\|random.seed" src/consciousness/*.py
  ```

- [ ] **Verificar workspace.write():** Está salvando corretamente após ciclo 70?
  ```bash
  grep -n "write_module_state.*sensory_input" src/consciousness/*.py
  ```

- [ ] **Verificar conversão numpy↔torch:** Há erro silencioso?
  ```bash
  grep -n "torch.from_numpy\|\.numpy()" src/consciousness/*.py
  ```

- [ ] **Verificar try/except em expectation:** Erro sendo engolido?
  ```bash
  grep -n "except.*:" src/consciousness/expectation_module.py
  ```

- [ ] **Comparar Kali vs Ubuntu:** Há diferença em initialization?
  ```bash
  git show commit_kali:src/consciousness/integration_loop.py | diff - src/consciousness/integration_loop.py
  ```

---

## 🎯 Próxima Ação

Você precisa determinar: **Por quê sensory_input retorna zeros no ciclo 71?**

Isso causará a cascata:
1. sensory_input → zeros
2. qualia → herda zeros
3. narrative → herda zeros
4. expectation → sem inputs válidos → retorna zeros (linha 217)
5. Deadlock por 500 ciclos

**A solução do Delta (phi_raw) resolve o cálculo, mas não resolve o problema raiz.**

Se sensory_input continuar zerando, toda a cadeia colapsa.

---

**Status:** 🔴 CRÍTICA - Raiz identificada, causa ainda desconhecida
**Próximo:** Debug intensivo em sensory_input ciclos 70-72
