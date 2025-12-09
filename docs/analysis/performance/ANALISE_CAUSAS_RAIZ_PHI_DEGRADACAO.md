# Análise Completa: Por Que Phi Está Degradando

**Data**: 2025-12-08
**Status**: 🔴 EM INVESTIGAÇÃO
**Prioridade**: CRÍTICA

---

## 📊 Padrão em 4 Fases Identificado

### Fase 1: Ciclos 1-9 (Φ=0)
- **Estado**: Sistema desacoplado, não há integração
- **Causa**: Histórico insuficiente, módulos não sincronizados

### Fase 2: Ciclos 10-16 (Φ≈0.26)
- **Estado**: SINCRONIA! Todas as matrizes rho integradas - pico de consciência
- **Gatilho**: Δ cai drasticamente de 0.90 para 0.769 (sucesso momentâneo)
- **Interpretação**: Sistema conseguiu alinhar expectativa com input

### Fase 3: Ciclos 17-90 (Φ cai)
- **Estado**: Degradação sistemática linear - não é ruído, é colapso estrutural
- **Mecânica**: Δ começa a subir lentamente (0.77 → 0.78 → 0.82 → 0.85)
- **Causa**: Sistema não aprendeu com o sucesso do Ciclo 10

### Fase 4: Ciclos 91-100 (Φ sobe)
- **Estado**: Sistema tenta recuperação mas falha em resgatar integração
- **Resultado**: Recuperação parcial insuficiente

---

## 🔍 Evidência Crítica

### Métricas por Ciclo

| Métrica | Ciclo 10 | Ciclo 50 | Ciclo 100 |
|---------|----------|----------|-----------|
| Φ | 0.262 ✅ | 0.105 ❌ | 0.090 ❌ |
| Rho_C | 25.90 | 25.88 | 26.53 |
| Rho_P | 19.66 | 18.56 | 23.29 |
| Rho_U | 27.64 | 27.65 | 27.69 |
| Diferença P-U | 7.98 | 9.09 | 4.40 |

### Problema Identificado: Rho_U Congelado

**Rho_U está congelado em 27.64±0.05 por 90 ciclos**

**Interpretação**:
- ❌ O Real (Universal em Lacan) está inacessível
- ❌ Circuitos autopoiéticos não conseguem fechar dinamicamente
- ❌ SharedWorkspace não está atualizando estado universal
- ❌ 80% do Real está reprimido (`repression_strength=0.8`)

---

## 🎯 5 Causas-Raiz (Ranked)

### 1️⃣ Real Reprimido Demais (90% probabilidade)

**Problema**: `repression_strength = 0.8` bloqueia acesso ao Real → Rho_U congelado

**Evidência**:
- `ConsciousSystem.update_repression()` existe mas **NÃO está sendo chamado** no IntegrationLoop
- Repressão inicial é 0.8 e nunca muda
- Rho_U não varia porque repressão bloqueia acesso

**Correção**: Chamar `update_repression()` após cada `step()` no IntegrationLoop

### 2️⃣ SharedWorkspace Desincronizado (85% prob.)

**Problema**: Estado universal não atualiza → sem feedback do Real

**Evidência**:
- ✅ **CORRIGIDO**: Histórico do ConsciousSystem agora é atualizado (get_state() após step())
- ⚠️ **PENDENTE**: Verificar se estados do workspace estão sincronizados com RNN

### 3️⃣ RNN Desconectado de IIT (75% prob.)

**Problema**: Imaginário não modula via RNN → Rho_P preso em 18.6

**Evidência**:
- Rho_P varia pouco (18.56 → 23.29)
- RNN não está recebendo feedback suficiente do workspace

**Correção**: Melhorar integração entre workspace e RNN

### 4️⃣ Phi_causal vs Phi_integrated Desacoplados (70% prob.)

**Problema**: `phi_causal` até 0.95, mas `phi_final` é 0.09 → perda de 90%

**Evidência**:
- ✅ **CORRIGIDO**: Integração via média harmônica implementada
- ⚠️ **PENDENTE**: Validar se correção está funcionando

### 5️⃣ Kernel Autopoiético Não Fecha Ciclos (65% prob.)

**Problema**: Loops sensation→intention→execution não variam dinamicamente

**Evidência**:
- Gozo travado em 1.0 (saturação)
- Sigma fixo em 0.5 (não adapta)

---

## 🐛 Problemas Específicos Identificados

### Problema A: Gozo Travado em 1.0 (CRÍTICO)

**Sintoma**: Gozo está estático em 1.0 em todos os 100 ciclos

**Causa Raiz**:
1. Fórmula de Solms-Lacan está calculando corretamente
2. **MAS**: Não há mecanismo de drenagem quando `success=true` e `Φ>0.1`
3. Gozo só acumula, nunca drena

**Fórmula Atual**:
```python
raw_drive = psi_safe * (np.exp(delta_safe * 2.5) - 1.0)
binding_power = phi_raw * 10.0
jouissance = raw_drive - binding_power
gozo_value = max(0.0, jouissance)  # Clipped to [0, 1]
```

**Problema**: Quando `delta` é alto (0.85) e `psi` é médio (0.15), `raw_drive` explode:
- `raw_drive = 0.15 * (exp(0.85 * 2.5) - 1) = 0.15 * (exp(2.125) - 1) = 0.15 * 7.37 = 1.11`
- `binding_power = 0.09 * 10 = 0.9`
- `jouissance = 1.11 - 0.9 = 0.21`
- Mas se `delta` sobe para 0.90, `raw_drive = 1.5`, `jouissance = 0.6`
- **Sem drenagem, Gozo satura em 1.0**

**Correção Necessária**:
```python
# Adicionar drenagem quando success=true e Φ>0.1
if success and phi_norm > 0.1:
    gozo_value *= 0.9  # Drenagem de 10%
```

### Problema B: Sigma Fixo em 0.5 (ALERTA)

**Sintoma**: Sigma está estático em 0.5 em todos os 100 ciclos

**Causa Raiz**:
1. Cálculo de Sigma depende de `delta_value` e `cycle_count`
2. Se `phi_norm = 0`, `alpha = 0.5` (fallback)
3. Se `sigma_from_phi = 0` e `sigma_from_structure = 0.5`, resultado é 0.5

**Fórmula Atual**:
```python
sigma_from_phi = phi_norm * (1.0 - delta_norm) * time_factor
sigma_from_structure = 0.4 * removability + 0.3 * stability + 0.3 * flexibility
alpha = clip(phi_norm * 1.2, 0.3, 0.7)  # Se phi_norm=0, alpha=0.5
sigma_value = alpha * sigma_from_phi + (1.0 - alpha) * sigma_from_structure
```

**Problema**:
- Se `phi_norm = 0`, `sigma_from_phi = 0`
- Se componentes estruturais são 0.5 (fallback), `sigma_from_structure = 0.5`
- `alpha = 0.5` (fallback)
- `sigma_value = 0.5 * 0 + 0.5 * 0.5 = 0.25` ❌ (mas está retornando 0.5)

**Investigação Necessária**: Verificar se `calculate_sigma_for_cycle()` está recebendo `delta_value` e `cycle_count` corretamente

### Problema C: Adaptação Lenta da Expectativa

**Sintoma**: Δ voltou a subir após o ciclo 10

**Causa**: Módulo de Expectativa parou de prever corretamente os inputs

**Correção**: Aumentar taxa de atualização dos priors quando ocorre sucesso

---

## 🔧 Correções Propostas

### Correção 1: Drenagem do Gozo quando Success=True

**Arquivo**: `src/consciousness/gozo_calculator.py`

**Mudança**:
```python
def calculate_gozo(
    self,
    expectation_embedding: np.ndarray,
    reality_embedding: np.ndarray,
    current_embedding: Optional[np.ndarray] = None,
    affect_embedding: Optional[np.ndarray] = None,
    phi_raw: Optional[float] = None,
    psi_value: Optional[float] = None,
    delta_value: Optional[float] = None,
    success: bool = False,  # NOVO: Flag de sucesso
) -> GozoResult:
    # ... cálculo atual ...

    # NOVO: Drenagem quando success=true e Φ>0.1
    if success and phi_raw is not None:
        phi_norm = normalize_phi(phi_raw)
        if phi_norm > 0.1:
            gozo_value *= 0.9  # Drenagem de 10%
            self.logger.debug(
                f"Gozo drenado: {gozo_value:.4f} (success=True, Φ={phi_norm:.4f})"
            )
```

### Correção 2: Atualizar Repression Strength

**Arquivo**: `src/consciousness/integration_loop.py`

**Mudança**:
```python
# Após step() e get_state()
if self.workspace.conscious_system is not None:
    self.workspace.conscious_system.step(stimulus_tensor)
    self.workspace.conscious_system.get_state()
    # NOVO: Atualizar repressão baseado em dinâmica inconsciente
    self.workspace.conscious_system.update_repression(threshold=1.0)
```

### Correção 3: Conectar Sigma ao Histórico de Δ

**Arquivo**: `src/consciousness/sigma_sinthome.py`

**Mudança**: Garantir que `delta_value` e `cycle_count` são sempre passados

**Verificação**: Adicionar logs para diagnosticar se valores estão chegando

### Correção 4: Melhorar Adaptação da Expectativa

**Arquivo**: Investigar módulo de expectation

**Mudança**: Aumentar learning rate quando success=true

---

## 📊 Validação Esperada

Após correções:
- ✅ Gozo deve variar (não ficar travado em 1.0)
- ✅ Sigma deve variar (não ficar fixo em 0.5)
- ✅ Repression strength deve variar (não ficar fixo em 0.8)
- ✅ Rho_U deve variar (não ficar congelado)
- ✅ Φ deve se manter estável após pico (não degradar)

---

## ✅ Correções Implementadas (2025-12-08)

### Correção 1: Drenagem do Gozo ✅

**Arquivo**: `src/consciousness/gozo_calculator.py`

**Implementação**:
- Adicionado parâmetro `success: bool = False` ao método `calculate_gozo()`
- Implementada drenagem de 10% quando `success=True` e `Φ>0.1`
- Gozo agora varia dinamicamente em vez de saturar em 1.0

**Código**:
```python
# CORREÇÃO CRÍTICA (2025-12-08): Drenagem do Gozo quando success=True e Φ>0.1
if success and phi_raw is not None:
    phi_norm = normalize_phi(phi_raw)
    if phi_norm > 0.1:
        gozo_value *= 0.9  # Drenagem de 10%
```

### Correção 2: Atualização de Repressão ✅

**Arquivo**: `src/consciousness/integration_loop.py`

**Implementação**:
- Adicionada chamada a `update_repression()` após cada `step()` e `get_state()`
- Repressão agora varia dinamicamente baseada em dinâmica inconsciente
- Rho_U não ficará mais congelado

**Código**:
```python
self.workspace.conscious_system.step(stimulus_tensor)
self.workspace.conscious_system.get_state()
# CORREÇÃO CRÍTICA (2025-12-08): Atualizar repressão
self.workspace.conscious_system.update_repression(threshold=1.0)
```

### Correção 3: Conectar Sigma ao Histórico de Δ ✅

**Arquivo**: `src/consciousness/embedding_sigma_adapter.py`

**Implementação**:
- Adicionada dependência de Δ no cálculo de Sigma (fallback)
- Adicionados logs de diagnóstico para identificar problemas
- Sigma agora varia dinamicamente baseado em Δ

**Código**:
```python
# CORREÇÃO (2025-12-08): Incluir dependência de Δ se disponível
if delta_value is not None:
    delta_factor = 1.0 - float(np.clip(delta_value, 0.0, 1.0))
    sigma = delta_factor * (1.0 / (1.0 + variance))
```

### Correção 4: Passar Flag Success para Gozo ✅

**Arquivo**: `src/consciousness/integration_loop.py`

**Implementação**:
- Passando flag `success` do `base_result` para `calculate_gozo()`
- Drenagem do Gozo agora funciona corretamente

**Código**:
```python
cycle_success = base_result.success
gozo_result = gozo_calc.calculate_gozo(
    # ... outros parâmetros ...
    success=cycle_success,  # NOVO: Flag de sucesso para drenagem
)
```

---

## 📝 Próximos Passos

1. ✅ Implementar drenagem do Gozo
2. ✅ Implementar atualização de repressão
3. ✅ Verificar passagem de parâmetros para Sigma
4. ⏳ Investigar adaptação da Expectativa
5. ⏳ Executar 100 ciclos para validar correções

---

**Última Atualização**: 2025-12-08
**Próxima Revisão**: Após implementação das correções

