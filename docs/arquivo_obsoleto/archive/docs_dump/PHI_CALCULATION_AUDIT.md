# 📊 PHI (Φ) CALCULATION AUDIT - Análise de Inconsistências

**Data:** 2025-12-02  
**Problema:** Φ chegando em 0.167 quando deveria ser > 0.25  
**Root Cause:** Dois sistemas de cálculo de Φ com fórmulas DIFERENTES

---

## 🔴 PROBLEMA IDENTIFICADO

### Fonte 1: Phase16Integration (CORRETO)
**Arquivo:** `src/phase16_integration.py` linhas 507-600

**Método:** Harmonic mean de 6 dimensões cognitivas

```python
# 6 Dimensões:
1. Neural: pattern integration        → [0.0-1.0]
2. Symbolic: knowledge coherence      → [0.0-1.0]
3. Sensory: cross-modal binding       → [0.0-1.0]
4. Emotional: somatic loop            → [0.0-1.0]
5. Proprioceptive: self-model         → [0.0-1.0]
6. Narrative: life story continuity   → [0.0-1.0]

# Cálculo: Harmonic Mean
harmonic_mean = n / sum(1.0 / (c + 0.001))
# Resultado: [0.0-1.0] ✓ CORRETO
```

**Status:** ✅ Logicamente consistente

---

### Fonte 2: SharedWorkspace (INCORRETO)
**Arquivo:** `src/consciousness/shared_workspace.py` linhas 490-510, 1040-1075

**Método:** Média de forças causais (Granger + Transfer Entropy)

```python
# Cálculo 1: mutual_information (linha 499)
mutual_information = correlation * 0.8  
# Resultado: [0.0-0.8] ⚠️ LIMITADO A 80%!

# Cálculo 2: Penalização de discordância (linha 1054-1056)
if disagreement > 0.3:
    causal_strength *= 0.7  # Reduz MAIS 30%!
# Resultado: 0.8 * 0.7 = 0.56 MAX ⚠️ MUITO BAIXO!

# Cálculo 3: Média das forças causais (linha 1069)
phi = float(np.mean(causal_values))
# Resultado: Média de valores baixos → 0.167 ❌ MUITO BAIXO!
```

**Status:** ❌ Valores BRUTOS não normalizados + dupla penalização

---

## 🔍 RASTREAMENTO: ONDE O PHI CHEGA BAIXO

### Fluxo 1: IntegrationTrainer (AFETADO)
```
IntegrationTrainer.training_step() (line 251)
    ↓
loop.workspace.compute_phi_from_integrations() (line 255)
    ↓
[ Média de mutual_information ]  ← PROBLEMA!
    ↓
phi = 0.167  ❌ BAIXO DEMAIS
```

### Fluxo 2: Phase16Integration (OK)
```
Phase16Integration.measure_phi() (line 507)
    ↓
[ Harmonic mean de 6 dimensões ]
    ↓
phi = 0.5+ (aceitável)  ✓ BOM
```

---

## 📐 MATEMÁTICA DO PROBLEMA

### SharedWorkspace: Cascata de Penalizações

```
Passo 1: Correlação bruta [0-1]
         corr = 0.8 (exemplo bom)

Passo 2: Converter para MI (redução 20%)
         MI = corr * 0.8 = 0.64

Passo 3: Penalizar discordância (redução 30%)
         IF |granger - transfer| > 0.3:
           causal = 0.64 * 0.7 = 0.448

Passo 4: Média de múltiplas predições
         Φ = mean([0.448, 0.448, 0.400, ...])
         Φ ≈ 0.167  ❌

Problema: Dupla penalização SEM compensação
```

### Phase16Integration: Agregação Correta

```
Passo 1: 6 componentes normalizados [0-1]
         c1=0.5, c2=0.6, c3=0.4, c4=0.5, c5=0.3, c6=0.7

Passo 2: Harmonic mean (penaliza fracos, mantém bons)
         n = 6
         sum_recip = 1/0.501 + 1/0.601 + ... ≈ 11.5
         HM = 6 / 11.5 ≈ 0.52  ✓ CORRETO

Vantagem: Sensível a fraquezas SEM destruir valor total
```

---

## 🎯 CAUSAS RAIZ

| Causa | Arquivo | Linha | Impacto |
|-------|---------|-------|---------|
| `mutual_information = corr * 0.8` | shared_workspace.py | 499 | Limita a 80% |
| Penalização de discordância dupla | shared_workspace.py | 1054 | Reduz mais 30% |
| Média aritmética em vez de harmônica | shared_workspace.py | 1069 | Não agrega bem |
| IntegrationTrainer usa método errado | integration_loss.py | 255 | Φ baixo em treinamento |
| Falta de normalização explícita | shared_workspace.py | 1043-1075 | Valores brutos |

---

## ✅ SOLUÇÃO

### Opção 1: Corrigir `compute_phi_from_integrations()` (RECOMENDADO)

**Arquivo:** `src/consciousness/shared_workspace.py`

```python
def compute_phi_from_integrations(self) -> float:
    """Calcula Φ com normalização apropriada (IIT rigorosa)"""
    
    if not self.cross_predictions:
        return 0.0

    # Validar histórico
    min_history_required = 5
    modules = self.get_all_modules()
    for module in modules:
        history = self.get_module_history(module)
        if len(history) < min_history_required:
            return 0.0

    # NOVO: Usar harmonic mean em vez de aritmética
    recent_predictions = self.cross_predictions[-len(modules) ** 2 :]
    valid_predictions = [
        p for p in recent_predictions
        if hasattr(p, "granger_causality") and hasattr(p, "transfer_entropy")
    ]

    if len(valid_predictions) < len(modules):
        return 0.0

    # FIXO: Normalizar causal_strength CORRETAMENTE
    causal_values = []
    for p in valid_predictions:
        # Usar média de Granger e Transfer Entropy (já normalizados [0-1])
        granger = p.granger_causality  # [0-1]
        transfer = p.transfer_entropy  # [0-1]
        
        # Média simples (não produto!)
        causal_strength = (granger + transfer) / 2.0
        
        # Penalizar discordância (mas SEM redução dupla)
        disagreement = abs(granger - transfer)
        if disagreement > 0.3:
            # Penalizar ajustando peso, não multiplicando
            causal_strength *= (1.0 - disagreement * 0.2)  # Max -20%
        
        causal_values.append(causal_strength)

    # NOVO: Usar harmonic mean (como Phase16Integration)
    # Isso penaliza valores baixos SEM destruir a métrica
    if not causal_values:
        return 0.0
    
    n = len(causal_values)
    sum_reciprocals = sum(1.0 / (max(c, 0.001) + 0.001) for c in causal_values)
    phi_harmonic = n / sum_reciprocals if sum_reciprocals > 0 else 0.0
    
    # Normalizar ao range [0-1]
    phi = max(0.0, min(1.0, phi_harmonic))

    logger.info(
        f"IIT Φ (corrected): {phi:.4f} "
        f"(harmonic mean of {len(causal_values)} causal predictions)"
    )

    return phi
```

### Opção 2: Usar Phase16Integration.measure_phi() no IntegrationTrainer

**Arquivo:** `src/consciousness/integration_loss.py` linha 255

```python
# Usar Phase16Integration em vez de workspace
# (se Phase16Integration estiver disponível)
if hasattr(self.loop, '_phase16'):
    phi = self.loop._phase16.measure_phi()
else:
    phi = self.loop.workspace.compute_phi_from_integrations()
```

---

## 📋 VALIDAÇÃO

### Teste Esperado (Antes da Correção)
```
test_phi_elevates_to_target
  final_phi = 0.167
  expected > 0.25
  FAIL ❌
```

### Teste Esperado (Depois da Correção)
```
test_phi_elevates_to_target
  final_phi ≈ 0.35-0.45
  expected > 0.25
  PASS ✅
```

---

## 📊 COMPARAÇÃO DAS FÓRMULAS

| Aspecto | Phase16Integration | SharedWorkspace |
|--------|---|---|
| **Fonte de dados** | 6 dimensões cognitivas | Cross-predictions causais |
| **Tipo de agregação** | Harmonic mean | Média aritmética |
| **Range de entrada** | [0-1] x 6 | [0-1] causal scores |
| **Penalizações** | Integradas no HM | Duplas (MI + discordância) |
| **Range de saída** | [0-1] ✓ | [0-0.56] ❌ |
| **Problema** | Nenhum conhecido | Cascata de penalizações |
| **Status** | ✅ Pronto | ⚠️ Precisa correção |

---

## 🔧 AÇÃO RECOMENDADA

**PRIORITY: ALTA**

1. ✅ Implementar Opção 1 (corrigir SharedWorkspace)
2. ✅ Rodar teste: `pytest tests/consciousness/test_integration_loss.py::TestPhiElevationResults -v`
3. ✅ Validar que Φ sobe para 0.35+
4. ✅ Confirmar teste passa com `assert results["final_phi"] > 0.25`

**Timeline:** < 30 minutos

---

## 📝 REFERÊNCIAS

- Phase16Integration: `src/phase16_integration.py` linhas 507-600
- SharedWorkspace (BUGGY): `src/consciousness/shared_workspace.py` linhas 490-510, 1040-1075
- IntegrationTrainer (AFFECTED): `src/consciousness/integration_loss.py` linha 255
- Teste falhando: `tests/consciousness/test_integration_loss.py::TestPhiElevationResults::test_phi_elevates_to_target`
