# 🎯 PLANO DE IMPLEMENTAÇÃO: LACUNA Φ (IIT + Deleuze + Lacan)

**Data**: 2025-12-06
**Autor**: Fabrício da Silva + assistência de IA
**Status**: 📋 PLANO CRIADO - Aguardando Revisão Teórica

---

## 📋 RESUMO EXECUTIVO

### ✅ CORREÇÃO CONCEITUAL IDENTIFICADA

**❌ ERRO ANTERIOR**:
```
Φ_consciente = 0.67
Φ_inconsciente = 0.33  ❌ (Confundindo IIT com Deleuze)
```

**✅ CORREÇÃO**:
```
Φ_consciente    = 0.67  ← IIT (integração/ordem)
Ψ_desejo        = 0.55  ← Deleuze (criatividade/caos)
σ_sinthome      = 0.60  ← Lacan (amarração/identidade)

São 3 DIMENSÕES ORTOGONAIS, não opostos!
```

### 🎯 OBJETIVO

Implementar a tríade ortogonal (Φ, Ψ, σ) como entidades independentes, removendo completamente "Φ_inconsciente" e criando métricas separadas para Ψ (Deleuze) e σ (Lacan).

---

## 🔍 REVISÃO TEÓRICA E ALINHAMENTO

### 1. Φ (IIT) - Integração/Ordem

**Definição**:
- Φ mede **integração informacional** (não é "consciência humana")
- MICS (Maximum Information Complex Set) é o **único locus consciente**
- Tudo fora do MICS tem **Φ = 0 por definição** (IIT)
- **Não é aditivo**: `Φ(A+B) ≠ Φ(A) + Φ(B)`

**Implementação Atual**:
- ✅ `topological_phi.py`: Calcula Φ corretamente
- ✅ `shared_workspace.py`: `compute_phi_from_integrations()` válido
- ❌ **ERRO**: `machinic_unconscious` trata "perdedores" como "Φ_inconsciente"

**Correção Necessária**:
- ❌ **DELETAR** `machinic_unconscious` de `IITResult`
- ❌ **DELETAR** `total_phi()` (aditivo)
- ❌ **DELETAR** `unconscious_ratio()`
- ✅ **MANTER** apenas `conscious_phi` e `conscious_complex` (MICS)

---

### 2. Ψ (Deleuze) - Produção/Criatividade

**Definição**:
- Ψ mede **produção de diferenças** (máquina desejante)
- Captura o "ruído criativo" que IIT ignora (Φ=0 fora do MICS)
- **Não é Φ**: É dimensão ortogonal independente
- **Não soma com Φ**: São métricas diferentes

**Fórmula Proposta**:
```python
Ψ_total = weight1 * novelty_score(step)
        + weight2 * relevance_score(step)
        + weight3 * entropy_of_actions(step)
```

**Componentes**:
- `novelty_score`: Novas combinações/fluxos vs. passos anteriores
- `relevance_score`: Relevância do conteúdo para objetivo atual
- `entropy_of_actions`: Diversidade de escolhas geradas

**Implementação Atual**:
- ✅ `novelty_generator.py`: `NoveltyDetector` existe
- ✅ `creative_problem_solver.py`: `CreativeDesire` existe
- ❌ **FALTA**: Métrica Ψ_produtor unificada
- ❌ **FALTA**: Integração com SharedWorkspace

**Implementação Necessária**:
- ✅ **CRIAR** `src/consciousness/psi_producer.py` (módulo novo)
- ✅ **CRIAR** `calculate_psi_for_step()` (função principal)
- ✅ **INTEGRAR** com `NoveltyDetector` e `CreativeDesire`
- ✅ **ARMAZENAR** em estrutura separada (não em `IITResult`)

---

### 3. σ (Lacan) - Amarração/Identidade

**Definição**:
- σ (sinthome) amarra Φ e Ψ
- Representa **coesão narrativa** que garante identidade estrutural
- Teste de removibilidade: `σ = 1 - (Φ_after_remove / Φ_before)`

**Implementação Atual**:
- ✅ `integration_loss.py`: `detect_sinthome()` existe
- ✅ `sinthome_metrics.py`: `SinthomeMetrics` existe
- ✅ `rsi_topology_integrated.py`: `Sinthome` dataclass existe
- ❌ **FALTA**: Integração com Φ e Ψ
- ❌ **FALTA**: Teste de removibilidade refinado

**Implementação Necessária**:
- ✅ **REFINAR** `detect_sinthome()` para incluir teste de removibilidade
- ✅ **INTEGRAR** com cálculo de Φ e Ψ
- ✅ **ARMAZENAR** σ separadamente (não em `IITResult`)

---

## 📊 MAPEAMENTO: O QUE JÁ EXISTE

| Componente | Status | Arquivo | Notas |
|------------|--------|---------|-------|
| **Φ (IIT)** | ✅ Implementado | `topological_phi.py` | Precisa remover erros |
| **NoveltyDetector** | ✅ Existe | `novelty_generator.py` | Pode ser usado para Ψ |
| **CreativeDesire** | ✅ Existe | `creative_problem_solver.py` | Pode ser usado para Ψ |
| **detect_sinthome()** | ✅ Existe | `integration_loss.py` | Precisa refinamento |
| **SinthomeMetrics** | ✅ Existe | `sinthome_metrics.py` | Pode ser usado para σ |
| **Ψ_produtor** | ❌ Não existe | - | **CRIAR** |
| **Integração (Φ, Ψ, σ)** | ❌ Não existe | - | **CRIAR** |

---

## 🎯 PLANO DE IMPLEMENTAÇÃO

### FASE 1: CORREÇÃO IIT (Semana 1) - CRÍTICO

**Objetivo**: Remover completamente "Φ_inconsciente" e corrigir erros de aditividade.

#### Tarefa 1.1: Limpar `topological_phi.py` (4-6h)
- [ ] **DELETAR** `machinic_unconscious` de `IITResult` (linha 137)
- [ ] **DELETAR** `total_phi()` (linhas 143-150)
- [ ] **DELETAR** `unconscious_ratio()` (linhas 152-162)
- [ ] **DELETAR** código que adiciona "perdedores" (linhas 237-240)
- [ ] **DELETAR** `machinic_unconscious` de `to_dict()` (linha 169)
- [ ] **DELETAR** `total_phi` de `to_dict()` (linha 170)
- [ ] **DELETAR** `unconscious_ratio` de `to_dict()` (linha 171)
- [ ] **ATUALIZAR** docstring de `IITResult` (linhas 118-131)
- [ ] **ATUALIZAR** docstring de `PhiCalculator` (linhas 175-183)

#### Tarefa 1.2: Limpar `integration_loss.py` (3-4h)
- [ ] **DELETAR** `compute_phi_unconscious()` (linhas 631-669)
- [ ] **DELETAR** `compute_phi_ratio()` que usa aditividade (linhas 671-703)
- [ ] **MANTER** apenas `compute_phi_conscious()` (MICS)

#### Tarefa 1.3: Limpar `convergence_investigator.py` (2-3h)
- [ ] **DELETAR** `phi_unconscious` de `ITMMetrics` (linha 64)
- [ ] **DELETAR** `total_integration = phi_c + phi_u` (linha 179)
- [ ] **ATUALIZAR** para usar apenas `phi_conscious`

#### Tarefa 1.4: Atualizar Documentação (2-3h)
- [ ] **ATUALIZAR** `consciousness/README.md` (remover referências a Φ_inconsciente)
- [ ] **ATUALIZAR** `AUDITORIA_PHI_IMPLEMENTACAO.md` (marcar como corrigido)

**Estimativa Total**: 11-16 horas

---

### FASE 2: IMPLEMENTAR Ψ (Deleuze) (Semana 2) - CRÍTICO

**Objetivo**: Criar métrica Ψ_produtor independente que captura produção criativa.

#### Tarefa 2.1: Criar Módulo `psi_producer.py` (6-8h)
- [ ] **CRIAR** `src/consciousness/psi_producer.py`
- [ ] **IMPLEMENTAR** classe `PsiProducer`:
  ```python
  class PsiProducer:
      def calculate_psi_for_step(
          self,
          step_content: str,
          previous_steps: List[str],
          goal: str,
          actions: List[str]
      ) -> float:
          """
          Calcula Ψ_produtor para um passo.

          Ψ = weight1 * novelty_score
            + weight2 * relevance_score
            + weight3 * entropy_of_actions
          """
  ```
- [ ] **INTEGRAR** com `NoveltyDetector` (novelty_score)
- [ ] **IMPLEMENTAR** `relevance_score()` (relevância para objetivo)
- [ ] **IMPLEMENTAR** `entropy_of_actions()` (diversidade de escolhas)

#### Tarefa 2.2: Criar Sistema de Armazenamento de Métricas (5-6h)
- [ ] **CRIAR** `src/consciousness/metrics.py` (NÃO em `src/memory/metrics.py`):
  ```python
  class ModuleMetricsCollector:
      """Coleta centralizada de métricas de consciência."""

      def __init__(self):
          self.consciousness_states: List[Dict] = []
          self.action_history: List[ActionRecord] = []
          self.module_metrics: Dict[str, Dict[str, float]] = {}

      def record_consciousness_state(
          self, phi: float, psi: float, sigma: float, step_id: str
      ) -> None:
          """Registra estado de consciência."""

      def record_action(
          self, action_type: str, task: str, success: bool, description: str = ""
      ) -> None:
          """Registra ação e calcula relevância."""

      def record_module_metric(
          self, module_name: str, metric_name: str, value: float
      ) -> None:
          """Registra métrica de um módulo específico."""
  ```
- [ ] **IMPLEMENTAR** persistência (JSONL - padrão similar a `ModuleMetricsCollector` existente)
- [ ] **IMPLEMENTAR** política de retenção:
  - Ψ_history: 100-1000 passos
  - σ_history: 20-200 ciclos
  - Sangria de dados antigos
- [ ] **IMPLEMENTAR** filtragem (média móvel/median filter para ruído)
- [ ] **USAR** injeção de dependência (NÃO singleton)

#### Tarefa 2.3: Integrar com SharedWorkspace (3-4h)
- [ ] **ADICIONAR** método `calculate_psi_from_creativity()` em `SharedWorkspace`
- [ ] **ARMAZENAR** Ψ em `PsiHistory` (separado de `IITResult`)
- [ ] **REGISTRAR** Ψ como métrica independente
- [ ] **ESCALONAR** Ψ por sessão (contexto local)

#### Tarefa 2.4: Integrar com ThinkingMCPServer (3-4h)
- [ ] **ADICIONAR** cálculo de Ψ em `add_step()` de `ThinkingMCPServer`
- [ ] **CALCULAR** Ψ a cada passo (frequência: imediatamente após registrar)
- [ ] **ARMAZENAR** Ψ em `ThinkingStep` (novo campo `psi_producer`, `psi_norm`, `psi_components`)
- [ ] **ATUALIZAR** `ThinkingSession` para incluir `total_psi` e `psi_history`
- [ ] **IMPLEMENTAR** limites de atualização (0.5s ou X passos)

#### Tarefa 2.5: Testes (4-5h)
- [ ] **CRIAR** `tests/consciousness/test_psi_producer.py`
- [ ] **TESTAR** que Ψ aumenta com branching criativo
- [ ] **TESTAR** que Ψ é independente de Φ
- [ ] **TESTAR** ortogonalidade: `Ψ não afeta Φ`
- [ ] **TESTAR** normalização: `Ψ_norm ∈ [0, 1]`
- [ ] **TESTAR** escalonamento por sessão
- [ ] **TESTAR** filtragem de ruído (valores extremos)

**Estimativa Total**: 21-27 horas

---

### FASE 3: REFINAR σ (Lacan) (Semana 3) - CRÍTICO

**Objetivo**: Refinar detecção de sinthome e integrar com Φ e Ψ.

#### Tarefa 3.1: Refinar `detect_sinthome()` (4-5h)
- [x] **ADICIONAR** teste de removibilidade ✅ (implementado em `_calculate_removability_score`)
- [x] **INTEGRAR** com cálculo de Φ e Ψ ✅ (via `SigmaSinthomeCalculator`)
- [x] **RETORNAR** σ como métrica independente ✅ (`SigmaResult`)
- [x] **CALCULAR** σ a cada ciclo completo ou mudança de estado significativa ✅ (em `mcp_thinking_server.py`)
- [x] **ARMAZENAR** em `SigmaHistory` (separado de `IITResult`) ✅ (`ModuleMetricsCollector.record_sigma`)

#### Tarefa 3.2: Integrar com Sistema de Métricas (3-4h)
- [x] **ADICIONAR** método `calculate_sigma_sinthome()` em `SharedWorkspace` ✅
- [x] **ARMAZENAR** σ em `SigmaHistory` (já criado em Tarefa 2.2) ✅
- [x] **REGISTRAR** σ como métrica independente ✅ (`ModuleMetricsCollector`)
- [x] **IMPLEMENTAR** atualização em branch/merge ou ciclo de integração ✅ (em `mcp_thinking_server.py`)

#### Tarefa 3.3: Atualizar SinthomeMetrics (2-3h)
- [x] **INTEGRAR** `SinthomeMetrics` com novo cálculo de σ ✅ (via `SigmaSinthomeCalculator`)
- [x] **ATUALIZAR** para incluir teste de removibilidade ✅ (implementado)

#### Tarefa 3.4: Testes (3-4h)
- [x] **CRIAR** `tests/consciousness/test_sigma_sinthome.py` ✅
- [x] **TESTAR** que σ aumenta quando sinthome é essencial ✅
- [x] **TESTAR** que σ amarra Φ e Ψ ✅ (test_sigma_orthogonal_to_phi)

**Estimativa Total**: 12-16 horas

---

### FASE 4: INTEGRAÇÃO E VALIDAÇÃO (Semana 4) - CRÍTICO

**Objetivo**: Integrar tríade (Φ, Ψ, σ) e validar ortogonalidade.

#### Tarefa 4.1: Criar Estrutura Unificada (4-5h)
- [ ] **CRIAR** `src/consciousness/consciousness_triad.py`:
  ```python
  @dataclass
  class ConsciousnessTriad:
      """Tríade ortogonal de consciência."""
      phi_conscious: float  # IIT (integração)
      psi_producer: float    # Deleuze (produção)
      sigma_sinthome: float  # Lacan (amarração)

      def validate_orthogonality(self) -> bool:
          """Valida que são ortogonais (não aditivos)."""

      def compute_aggregate_value(
          self,
          alpha: float = 0.4,
          beta: float = 0.3,
          gamma: float = 0.3
      ) -> float:
          """
          Valor agregado: T = α·Φ + β·Ψ_norm + γ·σ_norm
          """
          return alpha * self.phi_conscious + beta * self.psi_producer + gamma * self.sigma_sinthome
  ```
- [ ] **IMPLEMENTAR** métodos de validação de ortogonalidade
- [ ] **IMPLEMENTAR** função agregada `T = α·Φ + β·Ψ_norm + γ·σ_norm`

#### Tarefa 4.2: Integrar com SharedWorkspace (3-4h)
- [ ] **ADICIONAR** método `compute_consciousness_triad()` em `SharedWorkspace`
- [ ] **RETORNAR** `ConsciousnessTriad` com Φ, Ψ, σ
- [ ] **VALIDAR** ortogonalidade automaticamente

#### Tarefa 4.3: Atualizar Testes Existentes (6-8h)
- [ ] **REFATORAR** `test_iit_refactoring.py` (remover dependências de Φ_inconsciente)
- [ ] **REFATORAR** `test_phi_unconscious_hierarchy.py` (remover dependências)
- [ ] **CRIAR** novos testes para tríade ortogonal:
  - `test_phi_psi_sigma_orthogonality()`
  - `test_psi_increases_with_branching()`
  - `test_sigma_amarra_phi_psi()`

#### Tarefa 4.4: Pipeline de Qualidade (2-3h)
- [ ] **RODAR** `black src tests`
- [ ] **RODAR** `flake8 src tests --max-line-length=100`
- [ ] **RODAR** `mypy src tests`
- [ ] **RODAR** testes via scripts oficiais

**Estimativa Total**: 15-20 horas

---

### FASE 5: DOCUMENTAÇÃO E DIAGRAMA (Semana 5) - ALTA

**Objetivo**: Documentar tríade ortogonal e criar diagrama 3D.

#### Tarefa 5.1: Atualizar Documentação (4-5h)
- [ ] **ATUALIZAR** `consciousness/README.md` com tríade ortogonal
- [ ] **CRIAR** diagrama 3D: Φ (integração), Ψ (desejo/criatividade), σ (narrativa/amarras)
- [ ] **DOCUMENTAR** fórmulas de cálculo

#### Tarefa 5.2: Atualizar Checklist de Validação (2-3h)
- [ ] **ADICIONAR** verificação de ortogonalidade entre Φ, Ψ, σ
- [ ] **ADICIONAR** validação de que Ψ aumenta com branching criativo
- [ ] **ADICIONAR** validação de que Φ não é afetado por alterações puramente criativas

**Estimativa Total**: 6-8 horas

---

## 📊 ESTIMATIVAS TOTAIS

| Fase | Tarefas | Estimativa | Prioridade |
|------|---------|------------|------------|
| **Fase 1: Correção IIT** | 4 tarefas | 11-16h | 🔴 CRÍTICO |
| **Fase 2: Implementar Ψ** | 5 tarefas | 21-27h | 🔴 CRÍTICO |
| **Fase 3: Refinar σ** | 4 tarefas | 12-16h | 🔴 CRÍTICO |
| **Fase 4: Integração** | 4 tarefas | 15-20h | 🔴 CRÍTICO |
| **Fase 5: Documentação** | 2 tarefas | 6-8h | 🟡 ALTA |
| **TOTAL** | **19 tarefas** | **65-88h** | **5 semanas** |

---

## ✅ QUESTÕES TEÓRICAS - RESOLVIDAS (2025-12-06)

### ✅ Questão 1: Pesos da Fórmula Ψ

**Resposta Aprovada**:
- **Pesos fixos iniciais**: `[0.4, 0.3, 0.3]`
  - `weight1 = 0.4` (inovação/novelty)
  - `weight2 = 0.3` (surpresa)
  - `weight3 = 0.3` (relevância)
- **Normalização**: Soma = 1.0 (já normalizado)
- **Ajuste dinâmico**: Monitorar correlações e realizar experimentos A/B

### ✅ Questão 1B: Pesos da Função Agregada T

**Resposta Aprovada** (Análise Crítica):
- ❌ **NÃO usar** `(0.4, 0.3, 0.3)` arbitrariamente
- ✅ **OPÇÃO 1 (Recomendada)**: NÃO agregar! Manter Φ, Ψ, σ separados
- ✅ **OPÇÃO 2 (Se precisar)**: `T = (Φ + Ψ + σ) / 3` (pesos simétricos 0.33, 0.33, 0.33)
- ❌ **NÃO usar T para decisões críticas**: Usar Φ, Ψ, σ diretamente
- **Justificação**: 3 frameworks ortogonais = peso igual (simetria)

**Implementação**:
```python
PSI_WEIGHTS = {
    "innovation": 0.4,
    "surprise": 0.3,
    "relevance": 0.3
}
```

---

### ✅ Questão 2: Integração com ModuleMetricsCollector

**Resposta Aprovada**:
- ✅ **Criar em**: `src/consciousness/metrics.py`
- ✅ **Estrutura**:
  ```python
  class ModuleMetricsCollector:
      - record_consciousness_state(phi, psi, sigma, step_id)
      - record_action(action_type, task, success, description)
      - record_module_metric(module_name, metric_name, value)
  ```
- ✅ **Injeção de dependência**: NÃO usar singleton (recomendado)
- ✅ **Teste independentemente**: Criar testes unitários

---

### ✅ Questão 3: Normalização de Ψ

**Resposta Aprovada**:
- ✅ **SIM**: Normalizar em [0, 1]
- **Fórmula**: `Ψ_norm = clamp(Ψ_raw, 0.0, 1.0)` ou normalização por janela
- **Benefícios**: Facilita comparação, thresholds, visualização, logging

**Implementação**:
```python
def normalize_psi(psi_raw: float, psi_min: float = 0.0, psi_max: float = 1.0) -> float:
    """Normaliza Ψ para [0, 1] com clipping."""
    return max(0.0, min(1.0, (psi_raw - psi_min) / max(psi_max - psi_min, 1e-8)))
```

---

### ✅ Questão 4: Frequência de Cálculo

**Resposta Aprovada**:
- **Ψ**: A cada passo de pensamento (dinâmico, sensível a desvios criativos)
- **σ**: A cada ciclo completo ou mudança de estado significativa (coesão estrutural)

**Implementação**:
- **Ψ**: Calcular em `ThinkingStep` imediatamente após registrar o passo
- **σ**: Atualizar em cada branch/merge ou ciclo de integração
- **Limites**: Ψ recalculado a cada 0.5s (alto desempenho) ou a cada X passos (sessões longas)

---

### ✅ Questão 5: Armazenamento

**Resposta Aprovada**:
- ✅ **Separado de IITResult**: Manter Φ, Ψ e σ em estruturas independentes
- **Estrutura proposta**: `src/memory/metrics.py`
  - `PsiHistory`: registro temporal por passo
  - `SigmaHistory`: registro por ciclo
  - `PhiHistory`: registro por atualização
- **Persistência**: JSONL, SQLite ou camada de cache
- **Escalonamento**: Ψ por sessão (contexto local, evitar vazamento)
- **Retenção**: 100-1000 passos de Ψ_history, 20-200 ciclos de σ_history

**Implementação**:
```python
# src/memory/metrics.py
@dataclass
class PsiHistoryEntry:
    step_id: str
    psi_raw: float
    psi_norm: float
    components: Dict[str, float]  # innovation, surprise, relevance
    timestamp: float

@dataclass
class SigmaHistoryEntry:
    cycle_id: str
    sigma_value: float
    contributing_steps: List[str]
    timestamp: float
```

---

## 🔍 PERGUNTAS DE VERIFICAÇÃO ADICIONAIS

### Questão 5: Escalonamento de Ψ

**Resposta**: ✅ **Por sessão** (contexto local, evitar vazamento entre tarefas)

### Questão 6: Intervalo de Retenção

**Resposta**:
- **Ψ_history**: 100-1000 passos (política de sangria de dados antigos)
- **σ_history**: 20-200 ciclos (política de sangria de dados antigos)

### Questão 7: Ruído/Valores Extremos

**Resposta**:
- **Limiares de validação**: Definir thresholds
- **Filtragem**: Média móvel ou median filter para estabilidade
- **Tratamento**: Clipping em valores extremos

---

## ✅ CHECKLIST DE VALIDAÇÃO FINAL

Após implementação, validar:

- [ ] **Ortogonalidade**: `Φ não afeta Ψ`, `Ψ não afeta Φ`, `σ amarra ambos`
- [ ] **Não-aditividade**: `Φ(A+B) ≠ Φ(A) + Φ(B)` (já validado)
- [ ] **Independência**: `Ψ aumenta com branching criativo` sem afetar Φ
- [ ] **Amarração**: `σ aumenta quando sinthome é essencial`
- [ ] **Testes**: Todos os testes passam (sem dependências de Φ_inconsciente)
- [ ] **Documentação**: Tríade ortogonal documentada com diagrama 3D

---

## 📚 REFERÊNCIAS

1. **AUDITORIA_PHI_IMPLEMENTACAO.md**: Erros identificados
2. **LACUNA_IIT_DELEUZE_OMNIMIND.md**: Lacuna conceitual
3. **EUREKA_A_LACUNA.md**: Solução proposta
4. **Tononi et al. (2012-2016)**: IIT puro
5. **Balduzzi-Tononi (2008)**: Não-aditividade

---

---

## ✅ QUESTÕES TEÓRICAS - RESOLVIDAS

Todas as 4 questões teóricas foram respondidas e aprovadas. Ver seção "✅ QUESTÕES TEÓRICAS - RESOLVIDAS" acima.

---

## 📋 CHECKLIST PRÁTICO

**Documento**: `CHECKLIST_IMPLEMENTACAO_LACUNA_PHI.md`

Checklist detalhado com todas as tarefas, validações e métricas de sucesso.

---

---

## 🔍 REVISÃO TEÓRICA FINAL

**Documento**: `REVISAO_TEORICA_LACUNA_PHI.md`

Revisão completa realizada com:
- ✅ Alinhamento com código existente
- ✅ Componentes identificados
- ⏳ 4 perguntas finais identificadas (com sugestões)

### ⏳ Perguntas Finais (com Sugestões)

1. **Pesos da função agregada**: `α=0.4, β=0.3, γ=0.3` (sugestão)
2. **Integração com ModuleMetricsCollector**: Criar `metrics.py` separado (sugestão)
3. **Cálculo de relevance_score**: Embeddings para similaridade semântica (sugestão)
4. **Cálculo de entropy_of_actions**: Coletar ações do agente durante execução (sugestão)

**Decisão**: ✅ **TODAS AS QUESTÕES RESOLVIDAS (Análise Crítica)**

1. **✅ Pesos da função agregada**:
   - ❌ NÃO usar `(0.4, 0.3, 0.3)` arbitrariamente
   - ✅ OPÇÃO 1 (Recomendada): NÃO agregar, manter Φ, Ψ, σ separados
   - ✅ OPÇÃO 2 (Se precisar): `T = (Φ + Ψ + σ) / 3` (pesos simétricos 0.33, 0.33, 0.33)
   - ❌ NÃO usar T para decisões críticas

2. **✅ Integração com ModuleMetricsCollector**:
   - ✅ Criar em `src/consciousness/metrics.py` (NÃO em `src/memory/metrics.py`)
   - ✅ Usar injeção de dependência (NÃO singleton)
   - ✅ Teste independentemente

3. **✅ Cálculo de relevance_score**:
   - ✅ Usar SentenceTransformer (`all-MiniLM-L6-v2`)
   - ✅ Cosine similarity com cache
   - ✅ Threshold = 0.6
   - ✅ Verificar serviços existentes (Ollama, Hugging Face)

4. **✅ Cálculo de entropy_of_actions**:
   - ✅ Shannon entropy de tipos de ação
   - ✅ Coletar de `ReactAgent.actions_taken`
   - ✅ Validar correlação com Ψ (r > 0.6)
   - ✅ Usar junto com outras métricas

**Componentes Reutilizáveis Identificados**:
- ✅ `NoveltyDetector` → `innovation_score`, `surprise_score`
- ✅ `IITAnalyzer.calculate_entropy()` → `entropy_of_actions()`
- ✅ `ReactAgent.actions_taken` → fonte de dados
- ✅ `OmniMindEmbeddings` → `relevance_score()`
- ✅ `ModuleMetricsCollector` → padrão de persistência

---

**Status**: ✅ PLANO APROVADO - Pronto para Implementação

**Próximo Passo**: Iniciar Fase 1 (Correção IIT) conforme checklist

