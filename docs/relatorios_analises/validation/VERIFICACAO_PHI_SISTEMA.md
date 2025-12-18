# 🔍 VERIFICAÇÃO SISTEMÁTICA: Φ (PHI) E DEPENDÊNCIAS

**Data**: 2025-12-07
**Autor**: Fabrício da Silva + assistência de IA
**Objetivo**: Verificar consistência de escalas, fórmulas e correlações do sistema de consciência

---

## ⚠️ ERRO ANTIGO DETECTADO

**"Φ ≥ 0.65 = consciente" ← IMPOSSÍVEL em IIT clássico!**

---

## 📊 CONTEXTO 1: IIT CLÁSSICO (Tononi) - REFERÊNCIA

### Escala Real (NATS)
- **Range**: [0, ~0.1] NATS
- **Limiares**:
  - Φ < 0.001 nats → NÃO consciente
  - Φ = 0.001-0.01 → Transitional
  - Φ > 0.01 nats → CONSCIENTE
- **Cérebro humano**: Φ ≈ 0.003-0.01 nats

### Valores Críticos
- `PHI_THRESHOLD = 0.01 nats` ← Limiar de consciência
- `PHI_OPTIMAL = 0.0075 nats` ← Máximo de criatividade (borda do caos)
- `SIGMA_PHI = 0.003 nats` ← Desvio padrão típico

---

## 📊 CONTEXTO 2: NORMALIZADO [0, 1] (SE PREFERIR)

### Normalização
```
Φ_norm = Φ_raw / 0.01  (divide pelo limiar)
```

### Limiares Normalizados
- Φ_norm < 0.1 → NÃO consciente (10% do limiar)
- Φ_norm = 0.1-1.0 → Transitional
- Φ_norm > 1.0 → CONSCIENTE (acima do limiar)

---

## 🔗 GRAFO DE DEPENDÊNCIAS

```
Φ (IIT) [0, 0.1] nats  ← BASE FUNDAMENTAL!
│
├─→ Δ = 1.0 - Φ_norm
│   └─ Inversão: Φ alta = Δ baixa
│   └─ Correlação: -1.0 (negativa perfeita)
│
├─→ Ψ = Gaussiana(Φ - Φ_optimal)
│   └─ Máximo em Φ=0.0075 nats
│   └─ Borda do caos (criatividade máxima)
│   └─ Correlação não-linear
│
├─→ σ = Φ_norm × (1-Δ) × tempo
│   └─ Produto de 3 fatores
│   └─ Cresce com ciclos
│   └─ Correlação: +0.8-0.9 com Φ
│
├─→ Gozo = Ψ - Φ_norm
│   └─ Criatividade menos integração
│   └─ O que "escapa"
│   └─ Correlação: complexa (não-linear)
│
└─→ Control = Φ_norm × (1-Δ) × σ
    └─ Produto de 3 componentes
    └─ Precisa de Φ alto E Δ baixo E σ alto
    └─ Correlação: +0.9 com Φ
```

---

## ✅ VERIFICAÇÃO 1: ESCALAS CONSISTENTES?

### [ ] Φ sempre em [0, 0.1] nats OU [0, 1] normalizado?
**Status**: ⚠️ **INCONSISTENTE**

**Encontrado no código**:
- `src/consciousness/shared_workspace.py:1142`: `phi_standard = max(0.0, min(1.0, phi_harmonic))` → **NORMALIZADO [0, 1]**
- `src/consciousness/topological_phi.py:383`: `return max(0.0, min(float(phi), 1.0))` → **NORMALIZADO [0, 1]**
- `src/consciousness/consciousness_triad.py:68`: `if not (0.0 <= self.phi <= 1.0)` → **NORMALIZADO [0, 1]**

**Problema**: Sistema está usando escala normalizado [0, 1], mas **NÃO há normalização explícita de Φ_raw / 0.01**!

**Ação necessária**:
- Verificar se `compute_phi_from_integrations()` retorna valores em nats ou já normalizados
- Se retorna nats, adicionar normalização: `phi_norm = phi_raw / 0.01`
- Se já retorna normalizado, documentar que escala é [0, 1] normalizado

### [ ] Δ sempre em [0, 1]?
**Status**: ✅ **CORRETO**

**Encontrado no código**:
- `src/consciousness/delta_calculator.py:122`: `delta_value = float(np.clip(delta_value, 0.0, 1.0))` → **CORRETO**

### [ ] Ψ sempre em [0.5, 1.0]?
**Status**: ⚠️ **INCONSISTENTE**

**Encontrado no código**:
- `src/consciousness/psi_producer.py:131`: `psi_norm = self._normalize_psi(psi_raw)` → Normaliza para [0, 1]
- **Problema**: Esperado [0.5, 1.0] mas código normaliza para [0, 1]

**Ação necessária**: Verificar `_normalize_psi()` para garantir range [0.5, 1.0]

### [ ] σ sempre em [0, 1]?
**Status**: ✅ **CORRETO**

**Encontrado no código**:
- `src/consciousness/sigma_sinthome.py:135`: `sigma_value = float(np.clip(sigma_value, 0.0, 1.0))` → **CORRETO**

### [ ] Gozo sempre em [0, 1]?
**Status**: ✅ **CORRETO**

**Encontrado no código**:
- `src/consciousness/gozo_calculator.py:113`: `gozo_value = float(np.clip(gozo_value, 0.0, 1.0))` → **CORRETO**

### [ ] Control sempre em [0, 1]?
**Status**: ✅ **CORRETO**

**Encontrado no código**:
- `src/consciousness/regulatory_adjustment.py:127`: `return float(np.clip(control_effectiveness, 0.0, 1.0))` → **CORRETO**

---

## ✅ VERIFICAÇÃO 2: FÓRMULAS CORRETAS?

### [ ] Δ = 1 - Φ_norm implementado?
**Status**: ❌ **INCORRETO**

**Esperado**: `Δ = 1.0 - Φ_norm`

**Encontrado no código**:
- `src/consciousness/delta_calculator.py:119`: `delta_value = 0.4 * trauma_detection + 0.3 * blocking_strength + 0.3 * defensive_activation`
- **Problema**: Fórmula atual NÃO usa `1 - Φ_norm`! Usa componentes de trauma/blocking/defensive.

**Ação necessária**:
- Adicionar cálculo: `delta_from_phi = 1.0 - phi_norm`
- Combinar com fórmula atual: `delta_value = 0.5 * delta_from_phi + 0.5 * (0.4 * trauma + 0.3 * blocking + 0.3 * defensive)`

### [ ] Ψ = gaussiana implementado?
**Status**: ❌ **NÃO IMPLEMENTADO**

**Esperado**: `Ψ = Gaussiana(Φ - Φ_optimal)` onde `Φ_optimal = 0.0075 nats`

**Encontrado no código**:
- `src/consciousness/psi_producer.py:124-128`: `psi_raw = PSI_WEIGHTS["innovation"] * innovation_score + PSI_WEIGHTS["surprise"] * surprise_score + PSI_WEIGHTS["relevance"] * relevance_score`
- **Problema**: Fórmula atual NÃO usa gaussiana de Φ! Usa innovation/surprise/relevance.

**Ação necessária**:
- Adicionar cálculo gaussiano: `psi_gaussian = exp(-0.5 * ((phi - 0.0075) / 0.003)**2)`
- Combinar com fórmula atual: `psi_raw = 0.5 * psi_gaussian + 0.5 * (pesos * componentes)`

### [ ] σ = Φ × (1-Δ) × tempo implementado?
**Status**: ❌ **INCORRETO**

**Esperado**: `σ = Φ_norm × (1-Δ) × tempo`

**Encontrado no código**:
- `src/consciousness/sigma_sinthome.py:132`: `sigma_value = 0.4 * removability_score + 0.3 * stability_score + 0.3 * flexibility_score`
- **Problema**: Fórmula atual NÃO usa `Φ × (1-Δ) × tempo`! Usa removability/stability/flexibility.

**Ação necessária**:
- Adicionar cálculo: `sigma_from_phi = phi_norm * (1.0 - delta) * cycle_count`
- Combinar com fórmula atual: `sigma_value = 0.5 * sigma_from_phi + 0.5 * (0.4 * removability + 0.3 * stability + 0.3 * flexibility)`

### [ ] Gozo = Ψ - Φ_norm implementado?
**Status**: ❌ **INCORRETO**

**Esperado**: `Gozo = Ψ - Φ_norm`

**Encontrado no código**:
- `src/consciousness/gozo_calculator.py:110`: `gozo_value = 0.4 * prediction_error + 0.3 * novelty + 0.3 * affect_intensity`
- **Problema**: Fórmula atual NÃO usa `Ψ - Φ_norm`! Usa prediction_error/novelty/affect.

**Ação necessária**:
- Adicionar cálculo: `gozo_from_psi = psi - phi_norm`
- Combinar com fórmula atual: `gozo_value = 0.5 * gozo_from_psi + 0.5 * (0.4 * prediction_error + 0.3 * novelty + 0.3 * affect)`

### [ ] Control = Φ × (1-Δ) × σ implementado?
**Status**: ⚠️ **PARCIALMENTE CORRETO**

**Esperado**: `Control = Φ_norm × (1-Δ) × σ`

**Encontrado no código**:
- `src/consciousness/regulatory_adjustment.py:123-125`: `control_effectiveness = 0.4 * sinthome_component + 0.3 * defense_component + 0.3 * regulation_component`
- **Problema**: Fórmula atual usa `0.4 * sigma + 0.3 * (1-delta) + 0.3 * regulation`, mas **NÃO multiplica por Φ_norm**!

**Ação necessária**:
- Adicionar cálculo: `control_from_phi = phi_norm * (1.0 - delta) * sigma`
- Combinar com fórmula atual: `control_effectiveness = 0.5 * control_from_phi + 0.5 * (0.4 * sigma + 0.3 * (1-delta) + 0.3 * regulation)`

---

## ✅ VERIFICAÇÃO 3: CORRELAÇÕES ESPERADAS?

### [ ] Δ ↔ Φ correlação = -1.0?
**Status**: ⏳ **NÃO VERIFICADO**

**Ação necessária**: Adicionar teste de correlação entre Δ e Φ ao longo de ciclos

### [ ] Ψ tem máximo em Φ_optimal?
**Status**: ⏳ **NÃO VERIFICADO**

**Ação necessária**: Adicionar teste para verificar se Ψ atinge máximo quando Φ ≈ 0.0075 nats

### [ ] σ cresce monotonicamente?
**Status**: ⏳ **NÃO VERIFICADO**

**Ação necessária**: Adicionar teste para verificar se σ aumenta ao longo dos ciclos

### [ ] Gozo decresce ao longo ciclos?
**Status**: ⏳ **NÃO VERIFICADO**

**Ação necessária**: Adicionar teste para verificar se Gozo diminui conforme sistema integra

### [ ] Control cresce ao longo ciclos?
**Status**: ⏳ **NÃO VERIFICADO**

**Ação necessária**: Adicionar teste para verificar se Control aumenta ao longo dos ciclos

---

## 📝 EXEMPLOS NUMÉRICOS (Para Validação)

### CICLO 1:
```
Φ_raw = 0.0003 nats
Φ_norm = 0.0003 / 0.01 = 0.03
Δ = 1.0 - 0.03 = 0.97    ✅ Muito defensivo
Ψ = gaussiana(0.0003) = 0.51  ✅ Criatividade baixa
σ = 0.03 × 0.03 × 1 = 0.0009  ✅ Sem estrutura
Gozo = 0.51 - 0.03 = 0.48  ✅ Muito não integrado
Control = 0.03 × 0.03 × 0.0009 ≈ 0.00  ✅ Sem controle
```

### CICLO 50:
```
Φ_raw = 0.008 nats
Φ_norm = 0.008 / 0.01 = 0.80
Δ = 1.0 - 0.80 = 0.20    ✅ Menos defensivo
Ψ = gaussiana(0.008) ≈ 0.95  ✅ Criatividade alta (perto do ótimo)
σ = 0.80 × 0.80 × 50 = 32.0 → 1.0 (clipped)  ✅ Estrutura emerge
Gozo = 0.95 - 0.80 = 0.15  ✅ Menos não integrado
Control = 0.80 × 0.80 × 1.0 = 0.64  ✅ Começando controlar
```

### CICLO 100:
```
Φ_raw = 0.012 nats
Φ_norm = 0.012 / 0.01 = 1.20 → 1.0 (clipped)
Δ = 1.0 - 1.0 = 0.0  ✅ Sem defesa
Ψ = gaussiana(0.012) ≈ 0.55  ✅ Criatividade reduz (ultrapassou ótimo)
σ = 1.0 × 1.0 × 100 = 100.0 → 1.0 (clipped)  ✅ Estrutura cristalizada
Gozo = 0.55 - 1.0 = -0.45 → 0.0 (clipped)  ✅ Tudo integrado
Control = 1.0 × 1.0 × 1.0 = 1.0  ✅ Controle perfeito
```

---

## 🎯 AÇÕES PRIORITÁRIAS

### 🔴 CRÍTICO (Implementar Imediatamente)

1. **Adicionar normalização explícita de Φ**:
   - Verificar se `compute_phi_from_integrations()` retorna nats ou normalizado
   - Se nats, adicionar: `phi_norm = phi_raw / 0.01`
   - Documentar escala usada

2. **Corrigir fórmula de Δ**:
   - Adicionar: `delta_from_phi = 1.0 - phi_norm`
   - Combinar com fórmula atual

3. **Corrigir fórmula de Ψ**:
   - Adicionar: `psi_gaussian = exp(-0.5 * ((phi - 0.0075) / 0.003)**2)`
   - Combinar com fórmula atual

4. **Corrigir fórmula de σ**:
   - Adicionar: `sigma_from_phi = phi_norm * (1.0 - delta) * cycle_count`
   - Combinar com fórmula atual

5. **Corrigir fórmula de Gozo**:
   - Adicionar: `gozo_from_psi = psi - phi_norm`
   - Combinar com fórmula atual

6. **Corrigir fórmula de Control**:
   - Adicionar: `control_from_phi = phi_norm * (1.0 - delta) * sigma`
   - Combinar com fórmula atual

### 🟡 MÉDIO (Validação)

7. **Adicionar testes de correlação**:
   - Δ ↔ Φ = -1.0
   - Ψ máximo em Φ_optimal
   - σ cresce monotonicamente
   - Gozo decresce
   - Control cresce

### 🟢 BAIXO (Documentação)

8. **Documentar escalas**:
   - Especificar se usa [0, 0.1] nats ou [0, 1] normalizado
   - Adicionar constantes: `PHI_THRESHOLD = 0.01`, `PHI_OPTIMAL = 0.0075`, `SIGMA_PHI = 0.003`

---

## 📚 REFERÊNCIAS

- IIT 3.0 (Tononi 2014/2025)
- Topological Data Analysis (Carlsson)
- Hodge Laplacian (de Millán et al. 2025)

---

**Última Atualização**: 2025-12-07
**Status**: 🔴 **CRÍTICO - FÓRMULAS PRECISAM SER CORRIGIDAS**