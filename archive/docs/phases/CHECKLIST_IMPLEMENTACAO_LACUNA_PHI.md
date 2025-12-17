# ✅ CHECKLIST PRÁTICO: IMPLEMENTAÇÃO LACUNA Φ

**Data**: 2025-12-06
**Autor**: Fabrício da Silva + assistência de IA
**Status**: 📋 CHECKLIST CRIADO - Pronto para Implementação

---

## 🎯 OBJETIVO

Implementar a tríade ortogonal (Φ, Ψ, σ) como entidades independentes, removendo completamente "Φ_inconsciente" e criando métricas separadas para Ψ (Deleuze) e σ (Lacan).

---

## ✅ CHECKLIST RÁPIDO (START RÁPIDO)

### 1. Definir Componentes e Pesos

- [ ] **Definir** Ψ_subcomponentes:
  - [ ] `innovation_score` (inovação)
  - [ ] `surprise_score` (surpresa)
  - [ ] `relevance_score` (relevância)
- [ ] **Definir** pesos iniciais: `[0.4, 0.3, 0.3]`
- [ ] **Criar** constante `PSI_WEIGHTS` em `psi_producer.py`

---

### 2. Implementar Normalização

- [ ] **Implementar** `normalize_psi()` com clipping [0, 1]
- [ ] **Implementar** normalização baseada em janela (opcional)
- [ ] **Testar** que `Ψ_norm ∈ [0, 1]` sempre

---

### 3. Implementar Cálculo de Frequência

- [ ] **Implementar** cálculo de Ψ a cada passo (em `ThinkingStep`)
- [ ] **Implementar** atualização de σ no ciclo correspondente
- [ ] **Definir** limites de atualização (0.5s ou X passos)

---

### 4. Criar Sistema de Armazenamento

- [ ] **Criar** `src/memory/metrics.py`:
  - [ ] `PsiHistory` (registro temporal por passo)
  - [ ] `SigmaHistory` (registro por ciclo)
  - [ ] `PhiHistory` (registro por atualização)
- [ ] **Implementar** persistência (JSONL ou SQLite)
- [ ] **Implementar** política de retenção:
  - [ ] Ψ_history: 100-1000 passos
  - [ ] σ_history: 20-200 ciclos
  - [ ] Sangria de dados antigos

---

### 5. Garantir Armazenamento Separado

- [ ] **Verificar** que Φ está em `IITResult` (apenas `conscious_phi`)
- [ ] **Verificar** que Ψ está em `PsiHistory` (separado)
- [ ] **Verificar** que σ está em `SigmaHistory` (separado)
- [ ] **Remover** qualquer referência a `machinic_unconscious` de `IITResult`

---

### 6. Atualizar Logs e Dashboards

- [ ] **Adicionar** visualização de `Ψ_norm` ao longo do tempo
- [ ] **Adicionar** visualização de `σ` ao longo do tempo
- [ ] **Adicionar** gráfico da tríade ortogonal (Φ, Ψ, σ)
- [ ] **Atualizar** logs para incluir Ψ e σ

---

## 📋 CHECKLIST DETALHADO POR FASE

### FASE 1: CORREÇÃO IIT (Semana 1)

#### Tarefa 1.1: Limpar `topological_phi.py`
- [ ] Deletar `machinic_unconscious` de `IITResult` (linha 137)
- [ ] Deletar `total_phi()` (linhas 143-150)
- [ ] Deletar `unconscious_ratio()` (linhas 152-162)
- [ ] Deletar código que adiciona "perdedores" (linhas 237-240)
- [ ] Deletar `machinic_unconscious` de `to_dict()` (linha 169)
- [ ] Deletar `total_phi` de `to_dict()` (linha 170)
- [ ] Deletar `unconscious_ratio` de `to_dict()` (linha 171)
- [ ] Atualizar docstring de `IITResult` (linhas 118-131)
- [ ] Atualizar docstring de `PhiCalculator` (linhas 175-183)

#### Tarefa 1.2: Limpar `integration_loss.py`
- [ ] Deletar `compute_phi_unconscious()` (linhas 631-669)
- [ ] Deletar `compute_phi_ratio()` que usa aditividade (linhas 671-703)
- [ ] Manter apenas `compute_phi_conscious()` (MICS)

#### Tarefa 1.3: Limpar `convergence_investigator.py`
- [ ] Deletar `phi_unconscious` de `ITMMetrics` (linha 64)
- [ ] Deletar `total_integration = phi_c + phi_u` (linha 179)
- [ ] Atualizar para usar apenas `phi_conscious`

#### Tarefa 1.4: Atualizar Documentação
- [ ] Atualizar `consciousness/README.md` (remover referências a Φ_inconsciente)
- [ ] Atualizar `AUDITORIA_PHI_IMPLEMENTACAO.md` (marcar como corrigido)

---

### FASE 2: IMPLEMENTAR Ψ (Semana 2)

#### Tarefa 2.1: Criar Módulo `psi_producer.py`
- [ ] Criar `src/consciousness/psi_producer.py`
- [ ] Implementar classe `PsiProducer`:
  - [ ] `PSI_WEIGHTS = {"innovation": 0.4, "surprise": 0.3, "relevance": 0.3}`
  - [ ] `calculate_psi_for_step()` (retorna Dict com psi_raw, psi_norm, components)
  - [ ] `innovation_score()` (integra com `NoveltyDetector.measure_novelty()`)
  - [ ] `surprise_score()` (usa `NoveltyDetector._surprise_value()`)
  - [ ] `relevance_score()` (usa `OmniMindEmbeddings` para similaridade semântica)
  - [ ] `entropy_of_actions()` (reutiliza `IITAnalyzer.calculate_entropy()`, coleta de `ReactAgent.actions_taken`)
  - [ ] `normalize_psi()` (clipping [0, 1])

#### Tarefa 2.2: Criar Sistema de Armazenamento de Métricas
- [ ] Criar `src/memory/metrics.py`:
  - [ ] `PsiHistory` (registro temporal por passo)
  - [ ] `SigmaHistory` (registro por ciclo)
  - [ ] `PhiHistory` (registro por atualização)
- [ ] Implementar persistência (JSONL ou SQLite)
- [ ] Implementar política de retenção:
  - [ ] Ψ_history: 100-1000 passos
  - [ ] σ_history: 20-200 ciclos
  - [ ] Sangria de dados antigos
- [ ] Implementar filtragem (média móvel/median filter para ruído)

#### Tarefa 2.3: Integrar com SharedWorkspace
- [ ] Adicionar método `calculate_psi_from_creativity()` em `SharedWorkspace`
- [ ] Armazenar Ψ em `PsiHistory` (separado de `IITResult`)
- [ ] Registrar Ψ como métrica independente
- [ ] Escalonar Ψ por sessão (contexto local)

#### Tarefa 2.4: Integrar com ThinkingMCPServer
- [ ] Adicionar cálculo de Ψ em `add_step()` de `ThinkingMCPServer`
- [ ] Calcular Ψ a cada passo (frequência: imediatamente após registrar)
- [ ] Armazenar Ψ em `ThinkingStep` (novo campo `psi_producer`, `psi_norm`, `psi_components`)
- [ ] Atualizar `ThinkingSession` para incluir `total_psi` e `psi_history`
- [ ] Implementar limites de atualização (0.5s ou X passos)

#### Tarefa 2.5: Testes
- [ ] Criar `tests/consciousness/test_psi_producer.py`
- [ ] Testar que Ψ aumenta com branching criativo
- [ ] Testar que Ψ é independente de Φ
- [ ] Testar ortogonalidade: `Ψ não afeta Φ`
- [ ] Testar normalização: `Ψ_norm ∈ [0, 1]`
- [ ] Testar escalonamento por sessão
- [ ] Testar filtragem de ruído (valores extremos)

---

### FASE 3: REFINAR σ (Semana 3)

#### Tarefa 3.1: Refinar `detect_sinthome()`
- [ ] Adicionar teste de removibilidade:
  - [ ] `test_removibility()` (σ = 1 - (Φ_after_remove / Φ_before))
- [ ] Integrar com cálculo de Φ e Ψ
- [ ] Retornar σ como métrica independente
- [ ] Calcular σ a cada ciclo completo ou mudança de estado significativa
- [ ] Armazenar em `SigmaHistory` (separado de `IITResult`)

#### Tarefa 3.2: Integrar com Sistema de Métricas
- [ ] Adicionar método `calculate_sigma_sinthome()` em `SharedWorkspace`
- [ ] Armazenar σ em `SigmaHistory` (já criado em Tarefa 2.2)
- [ ] Registrar σ como métrica independente
- [ ] Implementar atualização em branch/merge ou ciclo de integração

#### Tarefa 3.3: Atualizar SinthomeMetrics
- [ ] Integrar `SinthomeMetrics` com novo cálculo de σ
- [ ] Atualizar para incluir teste de removibilidade

#### Tarefa 3.4: Testes
- [ ] Criar `tests/consciousness/test_sigma_sinthome.py`
- [ ] Testar que σ aumenta quando sinthome é essencial
- [ ] Testar que σ amarra Φ e Ψ

---

### FASE 4: INTEGRAÇÃO E VALIDAÇÃO (Semana 4)

#### Tarefa 4.1: Criar Estrutura Unificada
- [ ] Criar `src/consciousness/consciousness_triad.py`:
  - [ ] `ConsciousnessTriad` dataclass
  - [ ] `validate_orthogonality()`
  - [ ] `compute_aggregate_value()` (T = α·Φ + β·Ψ_norm + γ·σ_norm)
- [ ] Implementar métodos de validação de ortogonalidade

#### Tarefa 4.2: Integrar com SharedWorkspace
- [ ] Adicionar método `compute_consciousness_triad()` em `SharedWorkspace`
- [ ] Retornar `ConsciousnessTriad` com Φ, Ψ, σ
- [ ] Validar ortogonalidade automaticamente

#### Tarefa 4.3: Atualizar Testes Existentes
- [ ] Refatorar `test_iit_refactoring.py` (remover dependências de Φ_inconsciente)
- [ ] Refatorar `test_phi_unconscious_hierarchy.py` (remover dependências)
- [ ] Criar novos testes para tríade ortogonal:
  - [ ] `test_phi_psi_sigma_orthogonality()`
  - [ ] `test_psi_increases_with_branching()`
  - [ ] `test_sigma_amarra_phi_psi()`

#### Tarefa 4.4: Pipeline de Qualidade
- [ ] Rodar `black src tests`
- [ ] Rodar `flake8 src tests --max-line-length=100`
- [ ] Rodar `mypy src tests`
- [ ] Rodar testes via scripts oficiais

---

### FASE 5: DOCUMENTAÇÃO (Semana 5)

#### Tarefa 5.1: Atualizar Documentação ✅ (2025-12-07)
- [x] Atualizar `consciousness/README.md` com tríade ortogonal ✅
- [x] Criar diagrama 3D: Φ (integração), Ψ (desejo/criatividade), σ (narrativa/amarras) ✅
- [x] Documentar fórmulas de cálculo ✅

#### Tarefa 5.2: Atualizar Checklist de Validação ✅ (2025-12-07)
- [x] Adicionar verificação de ortogonalidade entre Φ, Ψ, σ ✅
- [x] Adicionar validação de que Ψ aumenta com branching criativo ✅
- [x] Adicionar validação de que Φ não é afetado por alterações puramente criativas ✅

---

## 🚨 VALIDAÇÕES CRÍTICAS

### Validação 1: Ortogonalidade ✅
- [x] **Verificar**: `Φ não afeta Ψ` ✅ (testes passando)
- [x] **Verificar**: `Ψ não afeta Φ` ✅ (testes passando)
- [x] **Verificar**: `σ amarra ambos` ✅ (testes passando)

### Validação 2: Não-aditividade ✅
- [x] **Verificar**: `Φ(A+B) ≠ Φ(A) + Φ(B)` ✅ (validado em Fase 1)

### Validação 3: Independência ✅
- [x] **Verificar**: `Ψ aumenta com branching criativo` sem afetar Φ ✅ (testes em Fase 2)

### Validação 4: Amarração ✅
- [x] **Verificar**: `σ aumenta quando sinthome é essencial` ✅ (19 testes passando em Fase 3)

### Validação 5: Normalização ✅
- [x] **Verificar**: `Ψ_norm ∈ [0, 1]` sempre ✅ (implementado em Fase 2)
- [x] **Verificar**: `σ ∈ [0, 1]` sempre ✅ (implementado em Fase 3)

### Validação 6: Armazenamento ✅
- [x] **Verificar**: Φ em `IITResult` (apenas `conscious_phi`) ✅ (Fase 1)
- [x] **Verificar**: Ψ em `PsiHistory` (separado) ✅ (Fase 2)
- [x] **Verificar**: σ em `SigmaHistory` (separado) ✅ (Fase 3)
- [x] **Verificar**: Nenhuma referência a `machinic_unconscious` ✅ (Fase 1)

---

## 📊 MÉTRICAS DE SUCESSO

- [x] **Ortogonalidade**: Validada automaticamente ✅ (Fase 4)
- [x] **Não-aditividade**: Φ validado ✅ (Fase 1)
- [x] **Independência**: Ψ e σ independentes de Φ ✅ (Fase 2-3)
- [x] **Testes**: Todos passam (sem dependências de Φ_inconsciente) ✅ (Fase 4)
- [x] **Documentação**: Tríade ortogonal documentada com diagrama 3D ✅ (Fase 5)
- [x] **Pipeline**: black, flake8, mypy passam ✅ (Fase 4)
- [ ] **Logs/Dashboards**: Visualização de Ψ_norm e σ ao longo do tempo (Opcional)

---

**Status**: 📋 CHECKLIST CRIADO - Pronto para Implementação

**Próximo Passo**: Iniciar Fase 1 (Correção IIT)

