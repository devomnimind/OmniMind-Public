# Arquitetura Multi-Provedor IA - OmniMind External AI Assistants
# Proposta de Integração Segura para Gemini, Copilot, OpenRouter

## 🎯 Objetivo
Expandir capacidades do OmniMind integrando assistentes IA externos (Gemini, Copilot, OpenRouter) com delegação segura de tarefas, mantendo isolamento completo dos dados do programa.

## 🏗️ Arquitetura Proposta

### 1. Camada de Abstração de Provedores
```python
# src/integrations/external_ai_providers.py
class ExternalAIProvider(ABC):
    """Interface abstrata para provedores externos de IA"""
    
    @abstractmethod
    async def execute_task(self, task: TaskSpec) -> TaskResult:
        """Executa tarefa de forma isolada"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> ProviderCapabilities:
        """Retorna capacidades do provedor"""
        pass

class GeminiProvider(ExternalAIProvider):
    """Google Gemini integration"""
    
class CopilotProvider(ExternalAIProvider):
    """GitHub Copilot integration"""
    
class OpenRouterProvider(ExternalAIProvider):
    """OpenRouter multi-model integration"""
```

### 2. Sistema de Delegação Segura
```python
# src/integrations/task_delegation.py
class TaskDelegationManager:
    """Gerencia delegação segura de tarefas para AIs externas"""
    
    def __init__(self):
        self.providers = {
            "gemini": GeminiProvider(),
            "copilot": CopilotProvider(),
            "openrouter": OpenRouterProvider()
        }
        self.task_isolation = TaskIsolationEngine()
    
    async def delegate_task(self, task_spec: TaskSpec) -> TaskResult:
        """Delega tarefa para provedor apropriado com isolamento"""
        # 1. Seleciona provedor baseado na tarefa
        provider = self._select_provider(task_spec)
        
        # 2. Isola contexto da tarefa
        isolated_context = await self.task_isolation.isolate_context(task_spec)
        
        # 3. Executa tarefa externamente
        result = await provider.execute_task(isolated_context)
        
        # 4. Valida e sanitiza resultado
        validated_result = await self._validate_result(result)
        
        return validated_result
```

### 3. Configuração de Provedores Externos
```yaml
# config/external_ai_providers.yaml
providers:
  gemini:
    enabled: true
    api_key_env: "GOOGLE_AI_API_KEY"
    models:
      - "gemini-1.5-pro"
      - "gemini-1.5-flash"
    rate_limits:
      requests_per_minute: 60
      tokens_per_minute: 1000000
  
  copilot:
    enabled: true
    auth_method: "oauth"  # ou "pat"
    github_token_env: "GITHUB_TOKEN"
    models:
      - "copilot-chat"
    rate_limits:
      requests_per_hour: 2000
  
  openrouter:
    enabled: true
    api_key_env: "OPENROUTER_API_KEY"
    models:
      - "anthropic/claude-3-opus"
      - "openai/gpt-4-turbo"
      - "google/gemini-pro"
    rate_limits:
      requests_per_minute: 100
      credits_per_month: 500

task_delegation:
  isolation_level: "strict"  # strict, moderate, permissive
  allowed_task_types:
    - "code_generation"
    - "code_review"
    - "documentation"
    - "analysis"
    - "optimization"
  forbidden_patterns:
    - ".*password.*"
    - ".*secret.*"
    - ".*token.*"
    - ".*key.*"
```

### 4. Isolamento de Contexto
```python
# src/integrations/task_isolation.py
class TaskIsolationEngine:
    """Isola contexto de tarefas para execução externa segura"""
    
    async def isolate_context(self, task_spec: TaskSpec) -> IsolatedTask:
        """Remove dados sensíveis e limita escopo"""
        
        # Sanitiza prompt
        clean_prompt = self._sanitize_prompt(task_spec.prompt)
        
        # Remove referências a dados internos
        clean_context = self._remove_internal_references(task_spec.context)
        
        # Limita arquivos permitidos
        allowed_files = self._filter_allowed_files(task_spec.files)
        
        return IsolatedTask(
            prompt=clean_prompt,
            context=clean_context,
            files=allowed_files,
            metadata=task_spec.metadata
        )
```

### 5. Integração com Sistema de Agentes
```python
# src/agents/external_ai_agent.py
class ExternalAIAgent(BaseAgent):
    """Agent que delega tarefas para AIs externas"""
    
    def __init__(self, delegation_manager: TaskDelegationManager):
        self.delegation_manager = delegation_manager
    
    async def execute(self, task: AgentTask) -> AgentResult:
        """Executa tarefa delegando para AI externa apropriada"""
        
        # Converte tarefa do agent para spec de delegação
        task_spec = self._convert_to_task_spec(task)
        
        # Delega execução
        result = await self.delegation_manager.delegate_task(task_spec)
        
        # Converte resultado de volta para formato do agent
        return self._convert_to_agent_result(result)
```

## 🔐 Segurança e Isolamento

### Princípios de Segurança:
1. **Zero Trust**: Toda tarefa externa é isolada e validada
2. **Data Sanitization**: Remoção automática de dados sensíveis
3. **Rate Limiting**: Controle rigoroso de uso de APIs
4. **Audit Trail**: Log completo de todas as delegações
5. **Fallback Local**: Capacidade de fallback para Ollama local

### Mecanismos de Isolamento:
- **Prompt Sanitization**: Regex patterns para remover dados sensíveis
- **Context Filtering**: Apenas arquivos/dados explicitamente permitidos
- **Result Validation**: Verificação de segurança dos resultados
- **Resource Limits**: Limites de CPU/memória para execuções externas

## 🚀 Implementação Gradual

### Fase 1: Infraestrutura Base
- [ ] Criar interfaces abstratas de provedores
- [ ] Implementar sistema de isolamento básico
- [ ] Configuração inicial de provedores

### Fase 2: Provedores Individuais
- [ ] Gemini integration
- [ ] Copilot integration  
- [ ] OpenRouter integration

### Fase 3: Integração Completa
- [ ] Sistema de delegação inteligente
- [ ] Integração com agentes existentes
- [ ] Monitoramento e métricas

### Fase 4: Produção
- [ ] Testes de segurança abrangentes
- [ ] Documentação completa
- [ ] Monitoramento em produção

## 📊 Benefícios Esperados

1. **Capacidades Expandidas**: Acesso a modelos state-of-the-art
2. **Flexibilidade**: Escolha dinâmica do melhor modelo por tarefa
3. **Custo-Otimizado**: Uso inteligente de diferentes provedores
4. **Segurança**: Isolamento completo dos dados internos
5. **Escalabilidade**: Capacidade de expansão horizontal

## 🔧 Configuração Inicial

Para começar, adicionar ao `config/omnimind.yaml`:

```yaml
external_ai:
  enabled: true
  providers_config: "config/external_ai_providers.yaml"
  delegation_enabled: true
  isolation_level: "strict"
  audit_enabled: true
```

Esta arquitetura permite que o OmniMind use assistentes externos como Gemini, Copilot e OpenRouter para executar tarefas específicas, mantendo completo isolamento dos dados do programa e controle rigoroso sobre o que é compartilhado.</content>
<parameter name="filePath">/home/fahbrain/projects/omnimind/docs/architecture/external_ai_integration_architecture.md