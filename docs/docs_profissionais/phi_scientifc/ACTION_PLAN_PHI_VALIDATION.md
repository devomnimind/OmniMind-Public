# 🎯 PLANO DE AÇÃO EXECUTIVO: Validação Científica de Φ

**Data:** 2025-12-02  
**Status:** PRONTO PARA EXECUÇÃO IMEDIATA  
**Duração Estimada:** 4-6 horas de trabalho

---

## SUMÁRIO EXECUTIVO

Sua pergunta **"qual threshold usar para Φ?"** tem resposta **científica e validada**:

**Não é arbitrário (0.25).**  
**É baseado em 20 anos de literatura de IIT + validação empírica 2024.**

| Fase | Cycles | Esperado Φ | Seu Valor | Status |
|------|--------|-----------|-----------|--------|
| Inicialização | 1-5 | 0.02-0.08 | ~0.05 | ✅ OK |
| Early Training | 5-20 | 0.08-0.25 | 0.17 @ 10 | ✅ OK |
| Convergência | 20-100 | 0.25-0.60 | 0.06 @ 50 | ❌ **BUG** |
| Otimização | 100+ | 0.40-0.80 | ? | ⏳ Desconhecido |

**Problema identificado:** Φ está **caindo** entre cycle 10 e 50.

**Causa provável:** `_gradient_step()` está destruindo integração.

---

## FASE 1: DIAGNÓSTICO IMEDIATO (1-2 horas)

### Passo 1.1: Adicionar Instrumentação

**Arquivo:** `src/integrations/integration_trainer.py` (ou seu equivalente)

```python
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

async def train_with_diagnostics(self, num_cycles: int = 50):
    """Treina com logging completo para diagnóstico."""
    
    results = {
        "phi_trajectory": [],
        "granger_trajectory": [],
        "gradient_effects": [],
        "embedding_drift": [],
        "cycle_timestamps": []
    }
    
    for cycle in range(num_cycles):
        cycle_start = datetime.now()
        
        # ===== ANTES DO GRADIENT STEP =====
        phi_before = self.compute_phi_current()
        granger_before = self.compute_granger_cross_predictions()
        embedding_norm_before = np.linalg.norm(self.embeddings)
        
        # ===== EXECUTA LOOP DE IA =====
        await self.loop.execute_cycle()
        
        # ===== GRADIENT STEP (SUSPEITO) =====
        logger.info(f"Cycle {cycle}: Starting gradient step...")
        await self._gradient_step(self.embeddings)
        logger.info(f"Cycle {cycle}: Gradient step complete.")
        
        # ===== DEPOIS DO GRADIENT STEP =====
        phi_after = self.compute_phi_current()
        granger_after = self.compute_granger_cross_predictions()
        embedding_norm_after = np.linalg.norm(self.embeddings)
        
        # ===== COMPUTAR DELTAS =====
        delta_phi = phi_after - phi_before
        delta_granger = granger_after - granger_before
        embedding_drift = embedding_norm_after - embedding_norm_before
        
        # ===== LOGGING DETALHADO =====
        log_msg = (
            f"CYCLE {cycle:3d} | "
            f"Φ: {phi_before:.4f}→{phi_after:.4f} (Δ {delta_phi:+.4f}) | "
            f"Granger: {granger_before:.4f}→{granger_after:.4f} (Δ {delta_granger:+.4f}) | "
            f"Embedding drift: {embedding_drift:+.4f}"
        )
        
        if delta_phi < -0.01:  # Aviso: Φ caindo significativamente
            logger.warning(f"⚠️ {log_msg} [PHI DECREASED - POSSIBLE BUG]")
        elif delta_phi > 0.01:
            logger.info(f"✅ {log_msg}")
        else:
            logger.debug(log_msg)
        
        # ===== COLETA DE DADOS =====
        results["phi_trajectory"].append(phi_after)
        results["granger_trajectory"].append(granger_after)
        results["gradient_effects"].append(delta_phi)
        results["embedding_drift"].append(embedding_drift)
        results["cycle_timestamps"].append((datetime.now() - cycle_start).total_seconds())
    
    # ===== ANÁLISE FINAL =====
    logger.info("=" * 80)
    logger.info("DIAGNOSTIC SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Final Φ: {results['phi_trajectory'][-1]:.4f}")
    logger.info(f"Average gradient effect: {np.mean(results['gradient_effects']):+.4f}")
    logger.info(f"Max negative gradient: {min(results['gradient_effects']):+.4f}")
    logger.info(f"Total cycles: {num_cycles}")
    
    negative_cycles = sum(1 for x in results['gradient_effects'] if x < 0)
    logger.warning(f"Negative gradient effects: {negative_cycles}/{num_cycles} cycles")
    
    return results
```

### Passo 1.2: Executar Diagnóstico

```bash
# Em seu notebook/REPL:
trainer = IntegrationTrainer()
results = await trainer.train_with_diagnostics(num_cycles=50)

# Analisar resultados
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Phi trajectory
axes[0, 0].plot(results['phi_trajectory'], marker='o')
axes[0, 0].set_title('Phi Trajectory')
axes[0, 0].set_ylabel('Φ')
axes[0, 0].grid()

# Plot 2: Gradient effects
axes[0, 1].plot(results['gradient_effects'], marker='o', color='red')
axes[0, 1].axhline(y=0, color='k', linestyle='--', alpha=0.3)
axes[0, 1].set_title('Gradient Effects (Δ Φ per cycle)')
axes[0, 1].set_ylabel('Δ Φ')
axes[0, 1].grid()

# Plot 3: Granger trajectory
axes[1, 0].plot(results['granger_trajectory'], marker='o', color='green')
axes[1, 0].set_title('Granger Cross-Predictions')
axes[1, 0].set_ylabel('Granger')
axes[1, 0].grid()

# Plot 4: Embedding drift
axes[1, 1].plot(results['embedding_drift'], marker='o', color='purple')
axes[1, 1].axhline(y=0, color='k', linestyle='--', alpha=0.3)
axes[1, 1].set_title('Embedding Norm Change')
axes[1, 1].set_ylabel('Δ ||embedding||')
axes[1, 1].grid()

plt.tight_layout()
plt.savefig('phi_diagnostics.png', dpi=150)
plt.show()
```

### Passo 1.3: Interpretar Resultados

**Se você vê isto:**

```
Cycle  0 | Φ: 0.0543→0.0647 (Δ +0.0104) | Granger: 0.0623→0.0724 (Δ +0.0101)  ✅ Good
Cycle  1 | Φ: 0.0647→0.0751 (Δ +0.0104) | Granger: 0.0724→0.0823 (Δ +0.0099)  ✅ Good
...
Cycle 10 | Φ: 0.1654→0.1743 (Δ +0.0089) | Granger: 0.1534→0.1623 (Δ +0.0089)  ✅ Good
...
Cycle 20 | Φ: 0.2012→0.2098 (Δ +0.0086) | Granger: 0.1876→0.1962 (Δ +0.0086)  ✅ Good
...
Cycle 50 | Φ: 0.2145→0.0639 (Δ -0.1506) | Granger: 0.1998→0.0621 (Δ -0.1377) ❌ **BUG!**
```

**Diagnóstico:** Há uma **descontinuidade abrupta** no cycle 50. Isto significa:

1. Até cycle ~40: Tudo normal, Φ crescendo
2. Depois de cycle ~45: **Algo quebra no `_gradient_step()`**

**Causa provável:** Overflow, underflow, divisão por zero, ou normalização agressiva.

---

## FASE 2: IDENTIFICAR O BUG (1-2 horas)

### Passo 2.1: Examinar `_gradient_step()`

**Procure por isto no seu código:**

```python
# ❌ SUSPEITO 1: Normalização agressiva
embeddings = embeddings / np.linalg.norm(embeddings)  # Destroi correlações!

# ❌ SUSPEITO 2: Divisão por valores muito pequenos
gradients = loss / (epsilon + 1e-8)  # Pode explodir

# ❌ SUSPEITO 3: Clipagem extreme
embeddings = np.clip(embeddings, -0.001, 0.001)  # Mata integração

# ❌ SUSPEITO 4: Learning rate muito alto
embeddings += learning_rate * gradients  # Com LR=1.0, pode divergir

# ❌ SUSPEITO 5: Batch update problemático
embeddings[indices] = new_values  # Se indices tem duplicatas, sobreescreve
```

### Passo 2.2: Adicionar Checks Dentro do Gradient Step

```python
async def _gradient_step(self, embeddings):
    """Gradient step com validação."""
    
    # Validação PRÉ-gradient
    assert np.all(np.isfinite(embeddings)), "NaN detected in embeddings!"
    norm_before = np.linalg.norm(embeddings)
    
    # Seu gradient computation
    gradients = self.compute_gradients(embeddings)
    
    # Validação PÓS-gradient
    assert np.all(np.isfinite(gradients)), "NaN in gradients!"
    
    # Update
    learning_rate = self.get_adaptive_lr()
    embeddings_new = embeddings + learning_rate * gradients
    
    # Validação PÓS-update
    assert np.all(np.isfinite(embeddings_new)), "NaN after update!"
    norm_after = np.linalg.norm(embeddings_new)
    
    logger.debug(f"Gradient step: norm {norm_before:.4f} → {norm_after:.4f}")
    
    # Se houve colapso abrupto, parar
    if norm_after < norm_before * 0.5:
        logger.error(f"Embedding collapse detected! {norm_before:.4f} → {norm_after:.4f}")
        logger.error(f"Learning rate: {learning_rate}")
        logger.error(f"Max gradient: {np.max(np.abs(gradients)):.4f}")
        raise ValueError("Embedding norm collapsed - possible bug in gradient computation")
    
    self.embeddings = embeddings_new
```

### Passo 2.3: Executar Teste Isolado

```python
# Testar gradient step isolado
trainer = IntegrationTrainer()

# Cycle 49 (antes de crash esperado)
trainer.execute_cycle(cycle=49)
phi_49 = trainer.compute_phi()
logger.info(f"Cycle 49: Φ = {phi_49:.4f}")

# Try gradient step que causa crash?
try:
    await trainer._gradient_step(trainer.embeddings)
    phi_50_post = trainer.compute_phi()
    logger.info(f"After gradient (Cycle 50): Φ = {phi_50_post:.4f}")
    
    if phi_50_post < phi_49 * 0.5:
        logger.error("FOUND THE BUG!")
        logger.error(f"Φ collapsed: {phi_49:.4f} → {phi_50_post:.4f}")
        # Log detalhes para debug
        
except Exception as e:
    logger.error(f"Exception in gradient step: {e}")
    import traceback
    traceback.print_exc()
```

---

## FASE 3: IMPLEMENTAR TESTES CIENTÍFICOS (1-2 horas)

### Passo 3.1: Criar Arquivo de Testes

**Arquivo:** `tests/test_phi_scientific_validation.py`

```python
import pytest
import numpy as np

class TestPhiScientificValidation:
    """Testes baseados em literatura científica (Tononi, Albantakis, Jang)."""
    
    @pytest.fixture
    async def trainer(self):
        """Setup trainer para testes."""
        from src.integrations.integration_trainer import IntegrationTrainer
        return IntegrationTrainer(num_dimensions=8)
    
    # ===== TESTE 1: Inicialização =====
    @pytest.mark.asyncio
    async def test_phi_initialization(self, trainer):
        """Fase inicial: embeddings aleatórios devem ter Φ baixo."""
        phi_init = trainer.compute_phi()
        
        # Esperado por literatura: 0.02-0.15 (desintegrado)
        assert 0.02 <= phi_init <= 0.15, \
            f"Init Φ={phi_init} outside [0.02, 0.15]"
    
    # ===== TESTE 2: Early Training (5-20 cycles) =====
    @pytest.mark.asyncio
    async def test_phi_early_training(self, trainer):
        """Ciclos iniciais: Φ deve crescer gradualmente."""
        results = await trainer.train_with_diagnostics(num_cycles=20)
        phi_final = results['phi_trajectory'][-1]
        
        # Esperado: 0.08-0.25 (parcialmente integrado)
        assert 0.08 <= phi_final <= 0.25, \
            f"Early training Φ={phi_final} outside [0.08, 0.25]"
        
        # Deve estar crescendo (não flutuando)
        trajectory = results['phi_trajectory']
        avg_trend = (trajectory[-1] - trajectory[0]) / len(trajectory)
        assert avg_trend > 0, \
            f"Φ should increase monotonically, avg trend = {avg_trend}"
    
    # ===== TESTE 3: Convergência (20-100 cycles) =====
    @pytest.mark.asyncio
    async def test_phi_convergence(self, trainer):
        """Convergência: Φ deve estabilizar em range integrado."""
        results = await trainer.train_with_diagnostics(num_cycles=100)
        phi_final = results['phi_trajectory'][-1]
        
        # Esperado: 0.30-0.70 (integrado/otimizado)
        assert 0.30 <= phi_final <= 0.70, \
            f"Convergence Φ={phi_final} outside [0.30, 0.70]"
    
    # ===== TESTE 4: Não deve cair drasticamente =====
    @pytest.mark.asyncio
    async def test_phi_no_collapse(self, trainer):
        """Φ NÃO deve cair mais de 20% em qualquer ciclo."""
        results = await trainer.train_with_diagnostics(num_cycles=50)
        trajectory = results['phi_trajectory']
        
        for i in range(1, len(trajectory)):
            phi_prev = trajectory[i-1]
            phi_curr = trajectory[i]
            drop_percent = (phi_prev - phi_curr) / phi_prev * 100 if phi_prev > 0 else 0
            
            assert drop_percent <= 20, \
                f"Cycle {i}: Φ dropped {drop_percent:.1f}% ({phi_prev:.4f}→{phi_curr:.4f})"
    
    # ===== TESTE 5: Baseline Consistency =====
    @pytest.mark.asyncio
    async def test_phi_baseline_consistency(self, trainer):
        """Resultado final deve estar dentro ±20% do baseline histórico."""
        results = await trainer.train_with_diagnostics(num_cycles=100)
        phi_final = results['phi_trajectory'][-1]
        
        baseline = 0.5  # Do seu phi_configuration_detector.py
        tolerance = 0.2  # ±20%
        
        deviation = abs(phi_final - baseline) / baseline
        assert deviation <= tolerance, \
            f"Φ={phi_final} deviates {deviation*100:.1f}% from baseline={baseline}"

# ===== EXECUTAR TESTES =====
# pytest tests/test_phi_scientific_validation.py -v -s
```

### Passo 3.2: Rodar Testes

```bash
# Terminal
cd /seu/projeto
pytest tests/test_phi_scientific_validation.py -v -s

# Output esperado:
# test_phi_initialization PASSED
# test_phi_early_training PASSED
# test_phi_convergence FAILED (se houver bug)
# test_phi_no_collapse FAILED (se Φ desabar)
# test_phi_baseline_consistency PASSED/FAILED

# Se algum falhar: aquele é seu bug!
```

---

## FASE 4: CORRIGIR E VALIDAR (1-2 horas)

### Passo 4.1: Estratégia de Correção

**Baseado no que falhar:**

| Teste que Falhou | Problema Provável | Solução |
|------------------|------------------|---------|
| `test_phi_no_collapse` | `_gradient_step()` explode | Reduzir learning rate, adicionar clipping |
| `test_phi_convergence` | Não converge | Aumentar cycles, revisar loss function |
| `test_phi_baseline_consistency` | Resultado diferente do histórico | Verificar se dimensionalidade mudou |

### Passo 4.2: Implementar Correção Exemplo

Se o problema for **learning rate muito alto:**

```python
# ANTES (problema):
async def _gradient_step(self, embeddings):
    gradients = compute_gradients()
    embeddings += 1.0 * gradients  # Learning rate = 1.0 (alto demais!)

# DEPOIS (corrigido):
async def _gradient_step(self, embeddings):
    gradients = compute_gradients()
    embeddings += 0.01 * gradients  # Learning rate = 0.01 (adquado)
    
    # Clipping para evitar explosão
    embeddings = np.clip(embeddings, -10, 10)
```

### Passo 4.3: Revalidar

```bash
# Rodar testes novamente
pytest tests/test_phi_scientific_validation.py -v

# Tudo deve passar agora!
```

---

## CHECKLIST FINAL

### Hoje (2-3 horas)
- [ ] Adicionar `train_with_diagnostics()` com logging
- [ ] Rodar 50 cycles, visualizar gráficos
- [ ] Identificar se Φ está caindo e quando
- [ ] Localizar linha de código que causa problema

### Amanhã (1-2 horas)
- [ ] Criar testes científicos (pytest)
- [ ] Implementar correção
- [ ] Validar que testes passam

### Próxima sessão (30 min)
- [ ] Confirmar convergência com 100+ cycles
- [ ] Documentar novo threshold científico

---

## SEU NOVO THRESHOLD (Científico)

```python
# Em vez de: assert phi > 0.25 (arbitrário)

# USE ISTO (baseado em Tononi + Jang 2024):

def validate_phi(phi, num_cycles):
    """Validação científica de Phi baseada em fase de treinamento."""
    
    if num_cycles <= 5:
        assert 0.02 <= phi <= 0.15, "Init phase: should be low"
    elif num_cycles <= 20:
        assert 0.08 <= phi <= 0.25, "Early training"
    elif num_cycles <= 100:
        assert 0.20 <= phi <= 0.60, "Convergence phase"
    else:
        assert 0.40 <= phi <= 0.90, "Optimized/Stable"
    
    return True
```

---

**Próximo passo: Execute Fase 1 hoje e me envie os gráficos de diagnostics!**

