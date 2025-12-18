# Plano de Implementação: Expansão Meta-ReAct para OmniMind

**Autor**: Fabrício da Silva + assistência de IA
**Data**: 2025-01-XX
**Status**: Em desenvolvimento

## 📋 Visão Geral

Este documento detalha o plano de implementação para evoluir o sistema OmniMind de ReAct padrão para **Meta-ReAct**, conforme especificado em `expansion_agents.md`. A implementação será adaptada à arquitetura atual do OmniMind, mantendo a filosofia do projeto e integrando com os componentes existentes.

## 🎯 Objetivos Principais

1. **Análise Estrutural de Erros**: Não apenas retry, mas análise de CAUSA e estratégias de recuperação
2. **Criação Dinâmica de Ferramentas**: Agentes podem criar ferramentas quando necessário
3. **Aprendizado Persistente**: Padrões de erro aprendidos entre execuções
4. **Coordenação Real**: Orchestrator com decomposição inteligente e validação incremental
5. **Autonomia Verdadeira**: Self-correction loops e detecção de alucinações

## 🏗️ Arquitetura Atual vs Proposta

### Componentes Existentes (Aproveitar)

- ✅ `OrchestratorAgent`: Coordenador mestre
- ✅ `DelegationManager`: Timeout, circuit breaker, retry
- ✅ `AgentRegistry`: Registro centralizado de agentes
- ✅ `ToolsFramework`: 25+ ferramentas organizadas em 11 camadas
- ✅ `TrustSystem`: Sistema de confiança crescente
- ✅ `AutoRepairSystem`: Auto-reparação
- ✅ `SandboxSystem`: Teste seguro de mudanças
- ✅ `DecisionExplainer`: Explicabilidade de decisões

### Componentes a Criar/Expandir

1. **ErrorAnalyzer**: Análise estrutural de erros
2. **EnhancedMemorySystem**: Memória episódica + semântica + procedural
3. **DependencyGraph**: Grafo de dependências em tempo real
4. **TaskDecomposer**: Decomposição inteligente de tarefas
5. **HallucinationDetector**: Detecção e correção de alucinações
6. **ToolComposer**: Composição de ferramentas
7. **DynamicToolCreator**: Criação dinâmica de ferramentas

## 📦 Fase 1: Análise Estrutural de Erros

### 1.1 ErrorAnalyzer

**Localização**: `src/orchestrator/error_analyzer.py`

**Responsabilidades**:
- Classificar tipos de erro (SYNTAX, DEPENDENCY, HALLUCINATION, TOOL_FAILURE, PATH_ERROR, etc.)
- Extrair padrões de erro
- Determinar estratégias de recuperação
- Integrar com `AutoRepairSystem` e `TrustSystem`

**Interface**:
```python
class ErrorAnalyzer:
    def analyze_error(self, error: Exception, context: Dict[str, Any]) -> ErrorAnalysis:
        """Analisa erro e retorna classificação + estratégia"""

    def extract_pattern(self, error: Exception) -> str:
        """Extrai padrão único do erro para aprendizado"""

    def suggest_recovery_strategy(self, analysis: ErrorAnalysis) -> RecoveryStrategy:
        """Sugere melhor estratégia de recuperação"""
```

**Integração**:
- `DelegationManager`: Usar análise antes de retry
- `AutoRepairSystem`: Usar estratégias sugeridas
- `TrustSystem`: Registrar padrões aprendidos

### 1.2 Integração com DelegationManager

**Modificações em** `src/orchestrator/delegation_manager.py`:

- Adicionar análise de erro antes de retry
- Usar estratégias sugeridas pelo ErrorAnalyzer
- Registrar padrões aprendidos

## 📦 Fase 2: Task Decomposition Inteligente

### 2.1 TaskDecomposer

**Localização**: `src/orchestrator/task_decomposer.py`

**Responsabilidades**:
- Análise profunda de complexidade
- Mapeamento de dependências
- Criação de plano multi-agente
- Definição de handoff points

**Interface**:
```python
class TaskDecomposer:
    def decompose_task(self, task: str) -> TaskDecomposition:
        """Decompõe tarefa em subtarefas com dependências"""

    def analyze_complexity(self, task: str) -> ComplexityAnalysis:
        """Analisa complexidade e requisitos"""

    def create_multiagent_plan(self, decomposition: TaskDecomposition) -> ExecutionPlan:
        """Cria plano de execução multi-agente"""
```

**Integração**:
- `OrchestratorAgent._decompose_task()`: Usar TaskDecomposer
- `DependencyGraph`: Rastrear dependências

### 2.2 DependencyGraph

**Localização**: `src/orchestrator/dependency_graph.py`

**Responsabilidades**:
- Rastrear dependências entre tarefas em tempo real
- Detectar ciclos
- Sugerir ordem de execução
- Visualizar grafo

## 📦 Fase 3: Enhanced Memory System

### 3.1 EnhancedMemorySystem

**Localização**: `src/orchestrator/enhanced_memory.py`

**Responsabilidades**:
- Memória episódica: Histórico de execuções
- Memória semântica: Conceitos e conhecimento
- Memória procedural: Padrões → soluções
- Aprendizado de padrões de erro

**Interface**:
```python
class EnhancedMemorySystem:
    def store_episode(self, task: str, result: Dict[str, Any]) -> None:
        """Armazena episódio de execução"""

    def learn_from_failure(self, error: Exception, solution: Dict[str, Any]) -> None:
        """Aprende padrão de erro e solução"""

    def recall_pattern(self, error_pattern: str) -> Optional[Dict[str, Any]]:
        """Recupera solução conhecida para padrão"""

    def evaluate_tool_effectiveness(self) -> Dict[str, float]:
        """Avalia efetividade de ferramentas"""
```

**Integração**:
- `OrchestratorAgent`: Usar memória para decisões
- `CodeAgent`: Aprender de falhas
- `TrustSystem`: Usar histórico para confiança

## 📦 Fase 4: Dynamic Tool Creation & Composition

### 4.1 DynamicToolCreator

**Localização**: `src/tools/dynamic_tool_creator.py`

**Responsabilidades**:
- Criar ferramentas dinamicamente baseado em necessidade
- Gerar código Python para ferramentas
- Validar e registrar ferramentas
- Integrar com `ToolsFramework`

**Interface**:
```python
class DynamicToolCreator:
    def create_tool(self, need: str, description: str) -> AuditedTool:
        """Cria ferramenta dinamicamente"""

    def create_tool_wrapper(self, failed_tool: str, alternative: str) -> AuditedTool:
        """Cria wrapper alternativo para ferramenta falhando"""
```

**Integração**:
- `ToolsFramework`: Registrar ferramentas dinâmicas
- `CodeAgent`: Criar ferramentas quando necessário

### 4.2 ToolComposer

**Localização**: `src/tools/tool_composer.py`

**Responsabilidades**:
- Compor múltiplas ferramentas em pipeline
- Exemplo: read → parse → analyze → write
- Validar composição
- Otimizar ordem de execução

**Interface**:
```python
class ToolComposer:
    def compose_tools(self, tool_names: List[str]) -> ComposedTool:
        """Compõe ferramentas em pipeline"""

    def optimize_composition(self, tools: List[str]) -> List[str]:
        """Otimiza ordem de execução"""
```

## 📦 Fase 5: Self-Correction Loops

### 5.1 Enhanced CodeAgent

**Modificações em** `src/agents/code_agent.py`:

- Adicionar `self_correction_loop()` método
- Integrar com `ErrorAnalyzer`
- Aprender padrões de erro
- Criar ferramentas dinamicamente quando necessário

**Novos métodos**:
```python
class CodeAgent(ReactAgent):
    async def run_code_task_with_intelligence(
        self, task: str, max_iterations: int = 10
    ) -> Dict[str, Any]:
        """Wrapper inteligente sobre run_code_task"""

    def _analyze_task_failure(self, result: Dict) -> Dict:
        """Análise estrutural de falha"""

    def _generate_alternative_strategy(self, task: str, failure: Dict) -> str:
        """Gera estratégia alternativa"""

    def _create_tool_wrapper(self, error: ToolExecutionError) -> callable:
        """Cria wrapper alternativo para ferramenta"""
```

### 5.2 HallucinationDetector

**Localização**: `src/orchestrator/hallucination_detector.py`

**Responsabilidades**:
- Detectar alucinações em outputs de agentes
- Verificar fact-checking
- Corrigir alucinações automaticamente
- Registrar para aprendizado

**Interface**:
```python
class HallucinationDetector:
    def detect_hallucination(self, output: str, context: Dict[str, Any]) -> bool:
        """Detecta se output contém alucinação"""

    def correct_hallucination(self, output: str, hallucination: Dict) -> str:
        """Corrige alucinação detectada"""
```

## 📦 Fase 6: Incremental Validation

### 6.1 OutputValidator

**Localização**: `src/orchestrator/output_validator.py`

**Responsabilidades**:
- Validar outputs incrementalmente durante execução
- Detectar problemas antes de completar tarefa
- Intervir se necessário
- Integrar com `SandboxSystem`

## 🔄 Integração com Componentes Existentes

### OrchestratorAgent

**Modificações**:
- `_decompose_task()`: Usar `TaskDecomposer`
- `_handle_crisis()`: Usar `ErrorAnalyzer` para análise estrutural
- `delegate_task_with_protection()`: Integrar análise de erro
- Adicionar `_validate_output_incremental()`

### CodeAgent

**Modificações**:
- Adicionar `run_code_task_with_intelligence()`
- Integrar com `ErrorAnalyzer` e `EnhancedMemorySystem`
- Adicionar criação dinâmica de ferramentas
- Self-correction loops

### ToolsFramework

**Modificações**:
- Adicionar registro de ferramentas dinâmicas
- Integrar `ToolComposer`
- Adicionar `create_tool_dynamically()`

## 📊 Priorização

### Alta Prioridade (Fase 1-2)
1. ✅ ErrorAnalyzer
2. ✅ TaskDecomposer
3. ✅ Integração com DelegationManager

### Média Prioridade (Fase 3-4)
4. ✅ EnhancedMemorySystem
5. ✅ DynamicToolCreator
6. ✅ ToolComposer

### Baixa Prioridade (Fase 5-6)
7. ✅ Self-Correction Loops
8. ✅ HallucinationDetector
9. ✅ Incremental Validation

## 🧪 Testes

Para cada componente:
- Testes unitários
- Testes de integração
- Testes de regressão
- Validação com testes existentes

## 📝 Documentação

- Documentar cada novo componente
- Atualizar arquitetura
- Exemplos de uso
- Guias de integração

## 🎯 Métricas de Sucesso

- Redução de 50% em retries desnecessários
- Aumento de 30% em taxa de sucesso de tarefas complexas
- Aprendizado de 10+ padrões de erro comuns
- Criação dinâmica de 5+ ferramentas

## 🔒 Segurança e Autonomia

- Todas as ferramentas dinâmicas passam por `SandboxSystem`
- Validação de código antes de execução
- Permissões via `PermissionMatrix`
- Auditoria via sistema existente

