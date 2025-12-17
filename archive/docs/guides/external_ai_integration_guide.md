# Guia de Uso - Provedores Externos de IA OmniMind

## Visão Geral

O OmniMind agora suporta integração com provedores externos de IA (Gemini, Copilot, OpenRouter) mantendo isolamento completo dos dados internos. Este guia mostra como configurar e usar essas capacidades.

## Configuração Inicial

### 1. Configurar Tokens de API

Adicione as seguintes variáveis de ambiente ao seu sistema:

```bash
# Google Gemini
export GOOGLE_AI_API_KEY="sua-chave-gemini-aqui"

# GitHub Copilot (OAuth ou Personal Access Token)
export GITHUB_TOKEN="seu-token-github-aqui"

# OpenRouter
export OPENROUTER_API_KEY="sua-chave-openrouter-aqui"
```

### 2. Arquivo de Configuração

O arquivo `config/external_ai_providers.yaml` já está configurado com as definições padrão. Para habilitar provedores específicos:

```yaml
providers:
  gemini:
    enabled: true
    # ... outras configurações

  copilot:
    enabled: true
    # ... outras configurações

  openrouter:
    enabled: true
    # ... outras configurações
```

### 3. Configuração Principal

Verifique se a configuração em `config/omnimind.yaml` inclui:

```yaml
ai:
  external_ai:
    enabled: true
    providers_config: "config/external_ai_providers.yaml"
    delegation_enabled: true
    isolation_level: "strict"
```

## Uso Programático

### Exemplo Básico de Delegação

```python
from src.integrations.task_delegation import TaskDelegationManager
from src.integrations.external_ai_providers import TaskSpec, TaskType

async def exemplo_delegacao():
    # Inicializa gerenciador
    manager = TaskDelegationManager()

    # Inicializa provedores
    await manager.initialize_providers()

    # Cria especificação de tarefa
    task_spec = TaskSpec(
        task_id="exemplo_001",
        task_type=TaskType.CODE_GENERATION,
        prompt="Crie uma função Python que calcula o fatorial de um número",
        context={"linguagem": "python", "dificuldade": "iniciante"}
    )

    # Delega tarefa
    resultado = await manager.delegate_task(task_spec)

    if resultado.success:
        print(f"Tarefa executada com sucesso!")
        print(f"Provedor usado: {resultado.provider_used}")
        print(f"Custo estimado: ${resultado.total_cost:.4f}")
        print(f"Conteúdo gerado: {resultado.execution_result.content}")
    else:
        print(f"Erro na delegação: {resultado.selection_reasoning}")

    # Fecha conexões
    await manager.close()

# Executa exemplo
import asyncio
asyncio.run(exemplo_delegacao())
```

### Exemplo com Arquivos de Contexto

```python
from src.integrations.external_ai_providers import TaskSpec, TaskType

async def exemplo_com_arquivos():
    manager = TaskDelegationManager()
    await manager.initialize_providers()

    # Tarefa com arquivos de contexto
    task_spec = TaskSpec(
        task_id="review_001",
        task_type=TaskType.CODE_REVIEW,
        prompt="Faça uma revisão completa deste código e sugira melhorias",
        files=[
            {
                "name": "calculadora.py",
                "content": '''
def soma(a, b):
    return a + b

def multiplicacao(a, b):
    return a * b

def divisao(a, b):
    return a / b
                '''
            }
        ]
    )

    resultado = await manager.delegate_task(task_spec)

    if resultado.success:
        print("Revisão de código:")
        print(resultado.execution_result.content)

    await manager.close()
```

## Segurança e Isolamento

### Níveis de Isolamento

O sistema oferece três níveis de isolamento:

1. **strict** (padrão): Máxima segurança, remove todos os dados sensíveis
2. **moderate**: Permite mais contexto, mas ainda remove dados críticos
3. **permissive**: Mínima filtragem (use apenas em desenvolvimento)

### Dados Automaticamente Removidos

O sistema automaticamente remove:
- Senhas, tokens, chaves API
- Endereços IP e emails
- Caminhos de arquivos do sistema
- Dados de configuração interna
- Informações de autenticação

### Exemplo de Isolamento

```python
from src.integrations.task_isolation import TaskIsolationEngine

# Prompt original com dados sensíveis
prompt_original = """
Desenvolva uma API REST usando FastAPI.
Conecte ao banco de dados PostgreSQL em 192.168.1.100:5432
Use as credenciais: user=admin, password=secret123
Token de API: sk-1234567890abcdef
"""

# Engine de isolamento
isolation_engine = TaskIsolationEngine()

# Simula isolamento
class MockTask:
    def __init__(self, prompt):
        self.prompt = prompt

isolated = await isolation_engine.isolate_context(MockTask(prompt_original))

print("Prompt isolado:")
print(isolated.prompt)
# Output: "Desenvolva uma API REST usando FastAPI.\nConecte ao banco de dados PostgreSQL em [IP_ADDRESS]:5432\nUse as credenciais: user=admin, password=[REDACTED]\nToken de API: [REDACTED]"
```

## Monitoramento e Estatísticas

### Verificar Estatísticas de Uso

```python
async def verificar_estatisticas():
    manager = TaskDelegationManager()
    await manager.initialize_providers()

    stats = await manager.get_delegation_stats()

    print("Estatísticas de Delegação:")
    print(f"Total de delegações: {stats['total_delegations']}")
    print(f"Taxa de sucesso: {stats['success_rate']:.2%}")
    print(f"Custo total: ${stats['total_cost']:.4f}")
    print(f"Latência média: {stats['average_latency']:.2f}s")

    print("\\nUso por provedor:")
    for provider, count in stats['provider_usage'].items():
        print(f"  {provider}: {count} tarefas")

    await manager.close()
```

## Configuração Avançada

### Regras de Seleção Personalizadas

```yaml
# Em external_ai_providers.yaml
task_delegation:
  provider_selection_rules:
    code_generation:
      priority_order: ["copilot", "openrouter", "gemini"]
      fallback_chain: ["copilot", "openrouter", "ollama"]

    analysis:
      priority_order: ["openrouter", "gemini", "copilot"]
      fallback_chain: ["openrouter", "gemini", "ollama"]

  selection_criteria:
    cost_priority: 0.4      # 40% peso no custo
    speed_priority: 0.3     # 30% peso na velocidade
    quality_priority: 0.3   # 30% peso na qualidade
```

### Rate Limiting Personalizado

```yaml
providers:
  gemini:
    rate_limits:
      requests_per_minute: 30    # Reduzido para controle
      tokens_per_minute: 50000   # Controle de uso de tokens
```

## Troubleshooting

### Problemas Comuns

1. **Rate Limit Excedido**
   ```
   Solução: Aguarde reset ou configure limites mais baixos
   ```

2. **Token Inválido**
   ```
   Solução: Verifique variáveis de ambiente e renovação de tokens
   ```

3. **Isolamento Muito Restritivo**
   ```
   Solução: Ajuste nível de isolamento ou personalize padrões proibidos
   ```

4. **Provedor Indisponível**
   ```
   Solução: Verifique conectividade e status dos serviços externos
   ```

### Logs de Debug

Para debug detalhado, configure:

```yaml
global_settings:
  log_level: "DEBUG"
```

### Teste de Conectividade

```python
async def testar_conectividade():
    manager = TaskDelegationManager()
    await manager.initialize_providers()

    # Testa cada provedor
    for name, provider in manager.providers.items():
        try:
            limits = await provider.check_rate_limits()
            print(f"✅ {name}: OK - {limits}")
        except Exception as e:
            print(f"❌ {name}: Erro - {e}")

    await manager.close()
```

## Considerações de Produção

### Custos
- Monitore uso regularmente
- Configure alertas de orçamento
- Use provedores gratuitos quando possível (Copilot)

### Performance
- Configure timeouts apropriados
- Monitore latência por provedor
- Implemente cache para resultados frequentes

### Segurança
- Renove tokens regularmente
- Monitore logs de auditoria
- Use isolamento strict em produção

### Escalabilidade
- Configure limites de concorrência
- Implemente filas para alta demanda
- Considere múltiplas chaves API por provedor

---

Esta integração permite que o OmniMind expanda suas capacidades usando AIs especializadas externamente, mantendo sempre a segurança e controle sobre os dados internos.</content>
<parameter name="filePath">/home/fahbrain/projects/omnimind/docs/guides/external_ai_integration_guide.md