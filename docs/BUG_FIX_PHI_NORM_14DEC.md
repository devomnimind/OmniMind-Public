# 🐛 BUG FIX: phi_norm Undefined Variable (2025-12-14)

**Data:** 14 de Dezembro de 2025
**Status:** ✅ CORRIGIDO
**Arquivo:** `src/consciousness/integration_loop.py` (linhas 1524-1544)

---

## 🔍 Problema Identificado

### Sintoma
```
NameError: name 'phi_norm' is not defined
```

Erro ocorrendo em **TODOS os ciclos** durante cálculo de Delta:
- Ciclo 2: `extended_result.delta = 1.0 - phi_norm` ❌
- Ciclo 3: `extended_result.delta = 1.0 - phi_norm` ❌
- Ciclos 4+: Idem ❌

### Root Cause
No código adicionado para o fallback de Delta, estava usando `phi_norm` mas essa variável nunca foi definida.

**O que foi escrito:**
```python
phi_raw = base_result.phi_estimate  # Normalizado [0,1]
phi_raw_nats = denormalize_phi(phi_raw)

# ... depois, em 3 lugares diferentes:
extended_result.delta = 1.0 - phi_norm  # ❌ phi_norm não existe!
```

**O que deveria ser:**
```python
phi_raw = base_result.phi_estimate  # Normalizado [0,1]
phi_raw_nats = denormalize_phi(phi_raw)

# ... depois, usar phi_raw (que já está normalizado):
extended_result.delta = 1.0 - phi_raw  # ✅ phi_raw existe!
```

### Impacto
- ❌ Delta não pode ser calculado em nenhum ciclo
- ❌ ExtendedLoopCycleResult não pode ser construído
- ❌ Métricas Ψ, σ, Triad não podem ser coletadas
- ❌ Sistema cai com NameError após qualquer ciclo

---

## ✅ Solução Implementada

### Mudanças
Substituir `phi_norm` por `phi_raw` em **3 locais**:

#### Local 1: Fallback quando embeddings indisponíveis
```python
# ANTES
extended_result.delta = 1.0 - phi_norm  # ❌ Undefined

# DEPOIS
extended_result.delta = 1.0 - phi_raw   # ✅ phi_raw está definido
```

#### Local 2: Fallback quando sem module_outputs
```python
# ANTES
extended_result.delta = 1.0 - phi_norm  # ❌ Undefined

# DEPOIS
extended_result.delta = 1.0 - phi_raw   # ✅ phi_raw está definido
```

#### Local 3: Fallback em exceção
```python
# ANTES
extended_result.delta = 1.0 - phi_norm  # ❌ Undefined

# DEPOIS
extended_result.delta = 1.0 - phi_raw   # ✅ phi_raw está definido
```

### Justificativa
- `phi_raw` é definido na linha 1500: `phi_raw = base_result.phi_estimate`
- `phi_raw` está **normalizado no range [0,1]** (conforme esperado)
- `phi_norm` nunca foi definido em nenhum lugar
- Usar `phi_raw` mantém a correlação Δ = 1.0 - Φ corretamente

### Verificação
✅ Script compila sem erros:
```bash
python3 -m py_compile src/consciousness/integration_loop.py
# ✅ Script compila corretamente!
```

---

## 📊 Comportamento Esperado Agora

### Ciclo 2 (Φ=0.7131)
- **Antes:** `NameError: name 'phi_norm' is not defined` ❌
- **Depois:** Δ = 1.0 - 0.7131 = 0.2869 ✅

### Ciclo 3 (Φ=0.6364)
- **Antes:** `NameError: name 'phi_norm' is not defined` ❌
- **Depois:** Δ = 1.0 - 0.6364 = 0.3636 ✅

### Próximos Ciclos
- **Antes:** Sempre erro ❌
- **Depois:** Delta calculado via Δ = 1.0 - Φ_raw ✅

---

## 🧪 Validação

### Checklist
- ✅ Arquivo compilável
- ✅ Variável `phi_raw` definida antes do uso
- ✅ Três locais onde `phi_norm` → `phi_raw`
- ✅ Mantém correlação IIT Δ-Φ
- ✅ Pronto para próxima execução

### Próximo Passo
Executar 500-ciclos novamente para validar que:
1. Delta não retorna `NameError`
2. Delta é calculado corretamente
3. Correlação Δ-Φ é mantida
4. Métricas Ψ, σ, Triad são coletadas

---

**Status:** ✅ CORRIGIDO E PRONTO PARA TESTE
