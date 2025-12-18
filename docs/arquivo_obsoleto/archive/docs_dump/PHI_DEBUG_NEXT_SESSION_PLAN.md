# 🔬 PHI DEBUG INVESTIGATION PLAN - PRÓXIMA SESSÃO

**Data de Criação:** 2025-12-02  
**Status:** 📋 PLANO ESTRUTURADO  
**Executor:** Próxima sessão  

---

## 🎯 OBJETIVOS

### Objetivo Primário
Entender **POR QUE Φ DESCE** quando deveria subir com treinamento:
- Esperado: 10 cycles (0.17) → 50 cycles (0.35+)
- Observado: 10 cycles (0.17) → 50 cycles (0.06) ❌

### Objetivo Secundário
Validar que testes têm **thresholds científicos**, não aleatórios

---

## 🔧 INVESTIGAÇÃO 1: GRADIENT STEP BUG

### Hipótese
`IntegrationTrainer._gradient_step()` está **revertendo embeddings** em vez de melhorá-los

### Plano de Debug

**Passo 1: Instrumentar com Logging**
```python
# File: src/consciousness/integration_loss.py
# Method: async def _gradient_step()

async def _gradient_step(self, module_embeddings: Dict[str, np.ndarray]) -> None:
    """Perform gradient descent step on module embeddings."""
    
    # NOVO: Log inicial
    phi_before = self.loop.workspace.compute_phi_from_integrations()
    embeddings_norm_before = {
        name: np.linalg.norm(emb) 
        for name, emb in module_embeddings.items()
    }
    
    # [CÓDIGO EXISTENTE AQUI]
    
    # NOVO: Log final
    phi_after = self.loop.workspace.compute_phi_from_integrations()
    embeddings_norm_after = {
        name: np.linalg.norm(self.loop.workspace.read_module_state(name).embedding)
        for name, _ in module_embeddings.items()
    }
    
    logger.info(f"_gradient_step: Φ {phi_before:.4f} → {phi_after:.4f} "
                f"(delta: {phi_after - phi_before:+.4f})")
    
    for name in module_embeddings.keys():
        delta = embeddings_norm_after.get(name, 0) - embeddings_norm_before.get(name, 0)
        logger.info(f"  Embedding {name}: norm delta = {delta:+.4f}")
```

**Passo 2: Executar com Verbose**
```bash
cd /home/fahbrain/projects/omnimind
python -m pytest \
  tests/consciousness/test_integration_loss.py::TestPhiElevationResults::test_phi_improves_over_longer_training \
  -xvs \
  --log-cli-level=INFO \
  2>&1 | grep -E "(gradient_step|Φ|delta)" > debug_gradients.log
```

**Passo 3: Analisar Logs**
- Gradients aumentando Φ? → Gradientes corretos
- Gradients diminuindo Φ? → BUG em `_gradient_step()`
- Gradients zerados? → Aprendizado congelado

---

## 🔧 INVESTIGAÇÃO 2: CAUSAL STRENGTH BOOTSTRAP

### Hipótese
Granger/Transfer Entropy começam zerados porque embeddings são aleatórios

### Plano de Teste

**Passo 1: Warm-up Implementation**
```python
# File: src/consciousness/integration_loss.py
# Class: IntegrationTrainer

async def warm_up(self, num_cycles: int = 5) -> None:
    """Warm-up: execute cycles without gradient to establish baseline causal structure."""
    logger.info(f"Starting warm-up with {num_cycles} cycles...")
    
    for i in range(num_cycles):
        await self.loop.execute_cycle(collect_metrics=True)
        phi = self.loop.workspace.compute_phi_from_integrations()
        logger.info(f"  Warm-up cycle {i+1}: Φ = {phi:.4f}")
    
    logger.info(f"Warm-up complete. Causal structure established.")

async def train(self, num_cycles: int = 500, ...):
    # NOVO: Call warm-up primeiro
    await self.warm_up(num_cycles=5)
    
    # [RESTO DO CÓDIGO EXISTENTE]
```

**Passo 2: Testar com Warm-up**
```python
# New test
@pytest.mark.asyncio
@pytest.mark.slow
async def test_phi_with_warmup(self):
    """Test Φ with warm-up phase."""
    loop = IntegrationLoop(enable_logging=False)
    trainer = IntegrationTrainer(loop, learning_rate=0.01)
    
    # Warm-up
    await trainer.warm_up(num_cycles=5)
    phi_after_warmup = trainer.best_phi
    
    # Training
    results = await trainer.train(num_cycles=20, target_phi=0.70, verbose=False)
    phi_after_training = results["final_phi"]
    
    # Comparação
    logger.info(f"Warm-up Φ: {phi_after_warmup:.4f}")
    logger.info(f"Training Φ: {phi_after_training:.4f}")
    
    # Expected: Warm-up estabelece 0.1-0.15, training sobe para 0.25+
    assert phi_after_warmup >= 0.05
    assert phi_after_training >= phi_after_warmup * 0.8  # Pelo menos não desce
```

**Passo 3: Resultado Esperado**
```
✓ Com warm-up: Φ cresce monotonicamente
✗ Sem warm-up: Φ desce (problema confirmado)
```

---

## 🔧 INVESTIGAÇÃO 3: GRANGER/TRANSFER MAGNITUDE

### Hipótese
Granger Causality e Transfer Entropy estão retornando valores muito pequenos (0.06-0.15)
que depois na harmonic mean ficam ainda menores

### Plano de Auditoria

**Passo 1: Log Detalhado de Cross-Predictions**
```python
# File: src/consciousness/shared_workspace.py
# Method: compute_phi_from_integrations()

for p in valid_predictions:
    granger = p.granger_causality
    transfer = p.transfer_entropy
    
    logger.info(f"CrossPred {p.source_module}→{p.target_module}: "
                f"granger={granger:.4f}, transfer={transfer:.4f}, "
                f"mean={((granger + transfer)/2):.4f}")
```

**Passo 2: Comparar com Baseline**
```
Esperado (de literatura):
  - Granger: 0.3-0.6 (boa causalidade)
  - Transfer Entropy: 0.2-0.5
  
Observado:
  - Granger: 0.06-0.15 (muito baixo!)
  - Transfer Entropy: similar
```

**Passo 3: Se Valores Baixos, Investigar:**
- Correlation cruzada retorna valores baixos?
- Transfer Entropy discretização está muito agressiva?
- Histórico de módulos é suficiente?

---

## 📊 INVESTIGAÇÃO 4: HARMONIC MEAN VALIDATION

### Hipótese
Harmonic mean pode estar muito agressivo em penalizar valores baixos

### Teste Matemático

```python
# Test values from observation
causal_values = [0.06, 0.07, 0.065, 0.068, 0.062, 0.064]

# Arithmetic mean
arith_mean = np.mean(causal_values)  # ≈ 0.0652

# Harmonic mean
n = len(causal_values)
sum_recip = sum(1.0 / (c + 0.001) for c in causal_values)
harm_mean = n / sum_recip  # ?

# Compare
print(f"Arithmetic: {arith_mean:.4f}")
print(f"Harmonic:   {harm_mean:.4f}")
print(f"Ratio:      {harm_mean / arith_mean:.2f}x")
```

**Esperado:** Harmonic mean ≈ 5-10% menor que arithmetic, não 50% menor

### Ação
Se harmonic mean estiver agressivo demais:
```python
# Usar weighted harmonic mean em vez de puro harmonic
# Ou usar média simples se valores muito baixos
if np.mean(causal_values) < 0.1:
    phi = np.mean(causal_values)  # Arithmetic para valores muito baixos
else:
    phi = harmonic_mean(causal_values)  # Harmonic para valores normais
```

---

## 🎯 PLANO DE EXECUÇÃO

### Session Next - Día 1 (30 min cada)

**Bloco 1: Setup & Logging (30 min)**
- [ ] Adicionar logging em `_gradient_step()`
- [ ] Rodar primeiro teste com debugging
- [ ] Capturar logs

**Bloco 2: Gradient Analysis (30 min)**
- [ ] Analisar se gradientes aumentam/diminuem Φ
- [ ] Se diminuem: DEBUG bug em implementação
- [ ] Se zerados: Problema em learning_rate

**Bloco 3: Warm-up Implementation (30 min)**
- [ ] Implementar `warm_up()` method
- [ ] Testar com novo teste
- [ ] Validar que Φ melhora com warm-up

**Bloco 4: Causal Audit (30 min)**
- [ ] Log Granger/Transfer por ciclo
- [ ] Verificar magnitude esperada
- [ ] Se baixa: Investigar raiz

### Total Sessão: 2 horas

---

## ✅ SUCCESS CRITERIA

### Investigação 1: Gradients
- ✅ Φ aumenta após `_gradient_step()` (não desce)
- ✅ Embeddings norm muda (não congelado)

### Investigação 2: Warm-up
- ✅ Com warm-up: Φ converge melhor
- ✅ Sem warm-up: Φ continua baixo

### Investigação 3: Causal Strength
- ✅ Granger/Transfer não mais próximos de 0
- ✅ Valores aumentam com ciclos

### Investigação 4: Math
- ✅ Harmonic mean não é problema
- ✅ Valores baixos de input, não operação

---

## 📋 ARQUIVOS PARA MODIFICAR

| Arquivo | Modificação | Prioridade |
|---------|------------|-----------|
| `src/consciousness/integration_loss.py` | Add logging em `_gradient_step()` + warm-up | 🔴 Alta |
| `src/consciousness/shared_workspace.py` | Log Granger/Transfer values | 🟡 Média |
| `tests/consciousness/test_integration_loss.py` | New test com warm-up | 🟡 Média |

---

## 📚 REFERÊNCIAS ÚTEIS

- `src/consciousness/integration_loss.py` - Main trainer
- `src/consciousness/shared_workspace.py` - Φ calculation
- `src/phase16_integration.py` - Alternative Φ (working version)
- `docs/PHI_SCIENTIFIC_STANDARDS_INVESTIGATION.md` - Context

---

## ⚠️ NOTAS

1. **Não modificar thresholds** até entender Φ behavior
2. **Log extensively** - melhor ter muitos logs que poucos
3. **Preservar working tests** - não deletar testes que passam
4. **Compare com Phase16Integration** - se aquela funciona, nossa deve também

---

**Status:** 🟢 READY FOR NEXT SESSION
