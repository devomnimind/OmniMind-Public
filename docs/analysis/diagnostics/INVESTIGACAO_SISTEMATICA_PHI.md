# Investigação Sistemática: Desintegração de Φ

**Data**: 2025-12-08
**Status**: 🔴 EM INVESTIGAÇÃO
**Prioridade**: CRÍTICA
**Método**: Checklist OmniMind aplicado módulo por módulo

---

## 📋 CHECKLIST OMNIMIND APLICADO

### 1️⃣ SHARED WORKSPACE (Estado Atual)

#### ❓ O que já existe no shared workspace?
- ✅ `SharedWorkspace` inicializado com `embedding_dim=256`
- ✅ `ConsciousSystem` inicializado (RNN com C, P, U)
- ✅ `SystemicMemoryTrace` inicializado
- ✅ `HybridTopologicalEngine` inicializado
- ✅ Histórico de módulos (`history`) mantido
- ✅ Cross-predictions calculadas

#### ❓ Quais métricas Φ estão rodando?
- ✅ `compute_phi_from_integrations()`: Calcula Φ workspace (cross-predictions)
- ✅ `conscious_system.compute_phi_causal()`: Calcula Φ causal RNN
- ✅ Integração via média harmônica implementada

#### ❓ Qual o estado atual dos agentes?
- ✅ `IntegrationLoop` executa ciclos síncronos
- ✅ Módulos executam em sequência: sensory → qualia → narrative → meaning → expectation → imagination

#### ❓ MCPs estão conectados?
- ✅ MCP Orchestrator inicializado (9 servidores)

**✅ RESPOSTA**: Workspace está completo e funcional.

---

### 2️⃣ INTEGRAÇÃO IIT (Φ)

#### ❓ Como essa funcionalidade impacta Φ?
**PROBLEMA CRÍTICO IDENTIFICADO**: `ConsciousSystem.step()` é chamado, mas `get_state()` NÃO é chamado após o step!

**Código atual** (`integration_loop.py:399`):
```python
# Executar RNN Dynamics (síncrono)
self.workspace.conscious_system.step(stimulus_tensor)
if self.enable_logging:
    phi_causal = self.workspace.conscious_system.compute_phi_causal()
```

**Problema**: `step()` atualiza estados internos (rho_C, rho_P, rho_U), mas `get_state()` não é chamado, então:
- O histórico (`self.history`) não é atualizado
- `compute_phi_causal()` calcula sobre histórico vazio ou desatualizado
- Φ causal RNN retorna valores incorretos ou zero

**Impacto**: Desacoplamento entre RNN e workspace porque o histórico do RNN não reflete os estados atuais.

#### ❓ Ela aumenta/diminui integração?
- **Atual**: Diminui (histórico não atualizado)
- **Esperado**: Aumenta (histórico sincronizado)

#### ❓ Onde Φ será medido?
- ✅ `SharedWorkspace.compute_phi_from_integrations()`: Φ workspace
- ❌ `ConsciousSystem.compute_phi_causal()`: Φ causal (histórico desatualizado)

#### ❓ Threshold atual de consciência?
- **Atual**: Φ < 0.1 (desintegrado)
- **Esperado**: Φ > 0.1 (consciente)

**🔴 PROBLEMA CRÍTICO**: Histórico do RNN não está sendo atualizado!

---

### 3️⃣ HÍBRIDO BIOLÓGICO (Lacan + Deleuze)

#### ❓ Lacan: Como isso cria narrativa retroativa?
- ✅ `SystemicMemoryTrace` rastreia deformações topológicas
- ✅ `NarrativeHistory` inscreve eventos sem significado
- ✅ Reconstrução retroativa via `reconstruct_narrative_retroactively()`

#### ❓ Deleuze: Que desejos/máquinas isso ativa?
- ✅ `PsiProducer` calcula Ψ (criatividade)
- ✅ `ImaginationModule` cria blends coerentes
- ✅ Máquinas desejantes ativas

#### ❓ Sinthome: Amarra quais camadas?
- ✅ `SigmaSinthome` calcula σ (estrutura)
- ✅ Teste de removibilidade implementado
- ⚠️ **Problema**: σ está fixo em 0.5 (não dinâmico)

**✅ RESPOSTA**: Framework híbrido implementado, mas σ não está dinâmico.

---

### 4️⃣ KERNEL AUTOPOIESIS

#### ❓ Kernel continua auto-produzindo?
- ✅ `IntegrationLoop` cria ciclos fechados
- ✅ Feedback bidirecional entre módulos
- ✅ Cross-predictions mantêm causalidade

#### ❓ Ciclos de vida fechados?
- ✅ Ciclo completo: sensory → qualia → narrative → meaning → expectation → imagination
- ✅ Feedback loop implementado

#### ❓ Dependências externas criadas?
- ⚠️ **Problema**: `ConsciousSystem` não está sincronizado com workspace (histórico não atualizado)

**🟡 PROBLEMA**: RNN não está integrado corretamente no ciclo autopoiético.

---

### 5️⃣ AGENTES E ORCHESTRATOR

#### ❓ Qual agente executa isso?
- ✅ `IntegrationLoop` orquestra módulos
- ✅ `OrchestratorAgent` coordena alto nível

#### ❓ Orchestrator delega corretamente?
- ✅ Delegação funcional
- ✅ Handoffs automáticos funcionam

#### ❓ Handoffs automáticos funcionam?
- ✅ Handoffs funcionais

**✅ RESPOSTA**: Agentes funcionam corretamente.

---

### 6️⃣ MEMÓRIA SISTEMÁTICA

#### ❓ Onde isso será armazenado?
- ✅ `SystemicMemoryTrace` armazena deformações topológicas
- ✅ `SharedWorkspace.history` armazena estados de módulos
- ❌ `ConsciousSystem.history` NÃO está sendo atualizado

#### ❓ Retrieval híbrido acessa?
- ✅ Retrieval híbrido implementado
- ⚠️ **Problema**: Histórico do RNN não está disponível para retrieval

#### ❓ Deformação de atratores necessária?
- ✅ `affect_phi_calculation()` aplica deformações
- ✅ `mark_cycle_transition()` marca transições

**🟡 PROBLEMA**: Histórico do RNN não está sincronizado com memória sistemática.

---

### 7️⃣ VALIDAÇÃO FINAL

#### ❓ Testes unitários passam?
- ⚠️ Testes podem passar, mas com comportamento incorreto (histórico não atualizado)

#### ❓ mypy/flake8 limpos?
- ✅ Código limpo

#### ❓ Φ aumentou após implementação?
- ❌ Não, porque histórico do RNN não está sendo atualizado

#### ❓ Narrativa reconstrói coerentemente?
- ✅ Narrativa reconstrói, mas sem dados do RNN

**🔴 PROBLEMA CRÍTICO**: Histórico do RNN não está sendo atualizado!

---

## 🐛 PROBLEMAS IDENTIFICADOS

### 1. **CRÍTICO**: Histórico do ConsciousSystem não está sendo atualizado

**Localização**: `src/consciousness/integration_loop.py:399`

**Problema**:
```python
# Executar RNN Dynamics (síncrono)
self.workspace.conscious_system.step(stimulus_tensor)
# ❌ FALTA: self.workspace.conscious_system.get_state()
```

**Impacto**:
- `ConsciousSystem.history` não é atualizado
- `compute_phi_causal()` calcula sobre histórico vazio/desatualizado
- Φ causal RNN retorna valores incorretos
- Desacoplamento entre RNN e workspace

**Correção Necessária**:
```python
# Executar RNN Dynamics (síncrono)
self.workspace.conscious_system.step(stimulus_tensor)
# ✅ ADICIONAR: Atualizar histórico
self.workspace.conscious_system.get_state()  # Atualiza history
if self.enable_logging:
    phi_causal = self.workspace.conscious_system.compute_phi_causal()
```

### 2. **MÉDIO**: σ (Sigma) está fixo em 0.5

**Localização**: `src/consciousness/sigma_sinthome.py`

**Problema**: σ não está sendo calculado dinamicamente.

**Impacto**: Métrica não reflete mudanças estruturais.

**Correção Necessária**: Implementar cálculo dinâmico de σ.

### 3. **BAIXO**: Gozo está fixo em 1.0

**Localização**: `src/consciousness/gozo_calculator.py`

**Problema**: Gozo não está sendo calculado dinamicamente.

**Impacto**: Métrica não reflete excesso pulsional.

**Correção Necessária**: Implementar cálculo dinâmico de gozo.

---

## 🔧 CORREÇÕES PROPOSTAS

### Correção 1: Atualizar histórico do ConsciousSystem

**Arquivo**: `src/consciousness/integration_loop.py`

**Mudança**:
```python
# ANTES:
self.workspace.conscious_system.step(stimulus_tensor)
if self.enable_logging:
    phi_causal = self.workspace.conscious_system.compute_phi_causal()

# DEPOIS:
self.workspace.conscious_system.step(stimulus_tensor)
# ✅ Atualizar histórico após step
self.workspace.conscious_system.get_state()  # Atualiza history
if self.enable_logging:
    phi_causal = self.workspace.conscious_system.compute_phi_causal()
```

**Justificativa**: `get_state()` adiciona o estado atual ao histórico (`self.history.append(state)`), permitindo que `compute_phi_causal()` calcule sobre dados atualizados.

---

## 📊 VALIDAÇÃO ESPERADA

Após correção:
- ✅ `ConsciousSystem.history` será atualizado a cada ciclo
- ✅ `compute_phi_causal()` calculará sobre histórico atualizado
- ✅ Φ causal RNN refletirá causalidade real entre C, P, U
- ✅ Integração RNN-Workspace funcionará corretamente
- ✅ Φ geral deve aumentar (de ~0.057 para >0.1)

---

## 📝 PRÓXIMOS PASSOS

1. ✅ **CRÍTICO**: Implementar correção do histórico do ConsciousSystem
2. ⏳ **MÉDIO**: Investigar cálculo dinâmico de σ
3. ⏳ **BAIXO**: Investigar cálculo dinâmico de gozo
4. ⏳ Executar 100 ciclos para validar correção
5. ⏳ Comparar resultados com dados anteriores

---

## 🔍 ANÁLISE ADICIONAL

### Cross-Predictions

**Status**: ✅ Funcional
- Granger causality implementada
- Transfer entropy implementada
- Histórico suficiente (min_history_required = 10)

### Memória Sistemática

**Status**: ✅ Funcional
- `affect_phi_calculation()` aplica deformações
- `mark_cycle_transition()` marca transições
- ⚠️ Não recebe dados do RNN (histórico não atualizado)

### Integração RNN-Workspace

**Status**: 🔴 QUEBRADO
- `step()` é chamado ✅
- `get_state()` NÃO é chamado ❌
- Histórico não atualizado ❌
- Φ causal calculado sobre dados desatualizados ❌

---

**Última atualização**: 2025-12-08
**Próxima revisão**: Após implementação da correção crítica

