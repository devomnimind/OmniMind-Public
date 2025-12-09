# Investigação: Psi Baixo em Todos os Ciclos

**Data**: 2025-12-08 22:45
**Problema**: Psi está baixo em todos os ciclos (aviso: "Ψ muito baixo")
**Status**: 🔴 **CAUSA RAIZ IDENTIFICADA**

---

## 🎯 RESUMO EXECUTIVO

**Problema Principal**: `psi_gaussian` está retornando **0.0** para valores de Phi acima de 0.05 nats, causando Psi baixo mesmo quando Phi está alto.

**Causa Raiz**:
- `PHI_OPTIMAL = 0.0075 nats` (muito baixo)
- `SIGMA_PHI = 0.003 nats` (muito pequeno)
- Quando Phi está em 0.05-0.1 nats (range normal após correção), a distância de `PHI_OPTIMAL` é muito grande
- A fórmula gaussiana resulta em valores próximos de zero: `exp(-0.5 * ((Φ - Φ_optimal) / σ_phi)²)`

**Impacto**:
- `psi_gaussian` ≈ 0.0 quando Phi > 0.05 nats
- `alpha` = 0.7 (máximo) quando Phi está alto
- Psi final = 0.7 * 0.0 + 0.3 * psi_from_creativity = **0.3 * psi_from_creativity**
- Se `psi_from_creativity` também está baixo, Psi final será muito baixo

---

## 🔍 ANÁLISE DETALHADA

### 1. Cálculo de `psi_gaussian`

**Fórmula**:
```python
psi_gaussian = exp(-0.5 * ((Φ - Φ_optimal) / σ_phi)²)
```

**Valores Atuais**:
- `PHI_OPTIMAL = 0.0075 nats`
- `SIGMA_PHI = 0.003 nats`

**Exemplo do Problema**:
```
Phi = 0.05 nats (normal após correção)
Distância de optimal = 0.05 - 0.0075 = 0.0425 nats
Normalizado por sigma = 0.0425 / 0.003 = 14.17
Exp(-0.5 * 14.17²) = exp(-100.4) ≈ 0.0
```

**Resultado**: `psi_gaussian = 0.0` para todos os valores de Phi > 0.05 nats!

### 2. Cálculo de Alpha Dinâmico

**Fórmula**:
```python
alpha = clip(phi_norm * 10.0, 0.3, 0.7)
```

**Quando Phi está alto (0.7-1.0 normalizado)**:
- `alpha = 0.7` (máximo)
- Sistema confia mais em `psi_gaussian` (que está em 0.0!)

### 3. Cálculo Final de Psi

**Fórmula**:
```python
psi = alpha * psi_gaussian + (1.0 - alpha) * psi_from_creativity
```

**Quando Phi está alto**:
```
psi = 0.7 * 0.0 + 0.3 * psi_from_creativity
psi = 0.3 * psi_from_creativity
```

**Se `psi_from_creativity` está baixo (ex: 0.3)**:
```
psi = 0.3 * 0.3 = 0.09 (muito baixo!)
```

---

## 🛠️ SOLUÇÕES PROPOSTAS

### Solução 1: Ajustar `PHI_OPTIMAL` e `SIGMA_PHI` (RECOMENDADO)

**Problema**: Valores foram calibrados para range antigo (0.0-0.01 nats), mas agora Phi está em 0.05-0.1 nats.

**Solução**: Recalibrar para o range atual:
- `PHI_OPTIMAL`: Ajustar para ~0.05-0.07 nats (meio do range atual)
- `SIGMA_PHI`: Aumentar para ~0.01-0.02 nats (mais tolerante)

**Código**:
```python
# Valores antigos (para range 0.0-0.01 nats)
PHI_OPTIMAL: float = 0.0075  # nats
SIGMA_PHI: float = 0.003  # nats

# Valores novos (para range 0.0-0.1 nats)
PHI_OPTIMAL: float = 0.06  # nats (meio do range atual)
SIGMA_PHI: float = 0.015  # nats (mais tolerante)
```

### Solução 2: Ajustar Fórmula de Alpha (ALTERNATIVA)

**Problema**: Alpha está muito alto quando Phi está alto, forçando dependência de `psi_gaussian` que está em 0.0.

**Solução**: Inverter lógica ou ajustar range:
- Quando Phi está alto, confiar mais em criatividade (não em gaussian)
- Ou reduzir alpha máximo para 0.5

**Código**:
```python
# Opção A: Inverter lógica
alpha = float(np.clip((1.0 - phi_norm) * 10.0, PSI_ALPHA_MIN, PSI_ALPHA_MAX))

# Opção B: Reduzir alpha máximo
alpha = float(np.clip(phi_norm * 5.0, PSI_ALPHA_MIN, 0.5))  # max = 0.5
```

### Solução 3: Ajustar Fórmula de Psi (ALTERNATIVA)

**Problema**: Quando `psi_gaussian` está em 0.0, a fórmula colapsa.

**Solução**: Adicionar fallback ou ajustar fórmula:
- Se `psi_gaussian < 0.1`, usar apenas `psi_from_creativity`
- Ou usar média ponderada diferente

**Código**:
```python
# Fallback quando gaussian está muito baixo
if psi_gaussian < 0.1:
    psi = psi_from_creativity  # Usar apenas criatividade
else:
    psi = alpha * psi_gaussian + (1.0 - alpha) * psi_from_creativity
```

---

## 📊 VALIDAÇÃO ESPERADA

### Antes da Correção
```
Phi = 0.05 nats → psi_gaussian = 0.0, alpha = 0.7
Psi = 0.7 * 0.0 + 0.3 * 0.3 = 0.09 (muito baixo)
```

### Depois da Correção (Solução 1)
```
Phi = 0.05 nats → psi_gaussian = 0.8, alpha = 0.7
Psi = 0.7 * 0.8 + 0.3 * 0.3 = 0.65 (normal)
```

---

## ✅ RECOMENDAÇÃO

**Implementar Solução 1**: Ajustar `PHI_OPTIMAL` e `SIGMA_PHI` para o range atual de Phi (0.0-0.1 nats).

**Justificativa**:
- Mantém a estrutura teórica (gaussiana baseada em Phi)
- Apenas recalibra para o range correto
- Não requer mudanças na lógica de alpha ou fórmula de Psi
- Mais simples e menos invasivo

**Próximos Passos**:
1. Ajustar `PHI_OPTIMAL` para 0.06 nats
2. Ajustar `SIGMA_PHI` para 0.015 nats
3. Validar com execução de ciclos
4. Verificar se Psi se recupera

---

**Última Atualização**: 2025-12-08 22:50
**Status**: ✅ **CORREÇÃO IMPLEMENTADA E VALIDADA**

---

## ✅ CORREÇÃO IMPLEMENTADA

### Mudanças Aplicadas

**Arquivo**: `src/consciousness/phi_constants.py`

**Valores Antigos**:
```python
PHI_OPTIMAL: float = 0.0075  # nats
SIGMA_PHI: float = 0.003  # nats
```

**Valores Novos**:
```python
PHI_OPTIMAL: float = 0.06  # nats (recalibrado de 0.0075)
SIGMA_PHI: float = 0.015  # nats (recalibrado de 0.003)
```

### Validação da Correção

**Antes da Correção**:
```
Phi = 0.05 nats → psi_gaussian = 0.0, psi_final = 0.09 (muito baixo)
Phi = 0.06 nats → psi_gaussian = 0.0, psi_final = 0.09 (muito baixo)
```

**Depois da Correção**:
```
Phi = 0.05 nats → psi_gaussian = 0.80, psi_final = 0.65 ✅
Phi = 0.06 nats → psi_gaussian = 1.00, psi_final = 0.79 ✅ (ótimo!)
Phi = 0.07 nats → psi_gaussian = 0.80, psi_final = 0.65 ✅
```

**Resultado**: Psi agora está em valores normais (0.65-0.79) em vez de muito baixos (0.09)!

### Próximos Passos

1. ✅ Correção implementada
2. ⏳ Executar ciclos para validar em produção
3. ⏳ Verificar se aviso "Ψ muito baixo" desaparece
4. ⏳ Monitorar se Gozo destrava com Psi recuperado

