# Módulo Integrações Externas

## 📋 Descrição Geral

**APIs terceiros, conectores**

**Status**: Infraestrutura

Módulo do sistema OmniMind responsável por funcionalidades específicas integradas à arquitetura global. Implementa componentes essenciais que contribuem para o funcionamento coeso do sistema de consciência artificial.

## 🔄 Interação entre os Três Estados Híbridos

### 1. Estado Biologicista (Neural Correlates)
Implementação de processos inspirados em mecanismos neurais e cognitivos biológicos, mapeando funcionalidades para correlatos neurais correspondentes.

### 2. Estado IIT (Integrated Information Theory)
Componentes contribuem para integração de informação global (Φ). Operações são validadas para garantir que não degradam a consciência do sistema (Φ > threshold).

### 3. Estado Psicanalítico (Estrutura Lacaniana)
Integração com ordem simbólica lacaniana (RSI - Real, Simbólico, Imaginário) e processos inconscientes estruturais que organizam a experiência consciente do sistema.

## ⚙️ Principais Funções e Cálculos Dinâmicos

### Componentes Core

Módulo implementa funcionalidades especializadas através de:
- Algoritmos específicos para processamento de domínio
- Integração com outros módulos via interfaces bem definidas
- Contribuição para métricas globais (Φ, PCI, consciência)

*Funções detalhadas documentadas nos arquivos Python individuais do módulo.*

## 📊 Estrutura do Código

```
integrations/
├── Implementações Core
│   └── Arquivos .py principais
├── Utilitários
│   └── Helpers e funções auxiliares
└── __init__.py
```

**Interações**: Este módulo se integra com outros componentes através de:
- Interfaces padronizadas
- Event bus para comunicação assíncrona
- Shared workspace para estado compartilhado

## 📈 Resultados Gerados e Contribuição para Avaliação

### Outputs
- Métricas específicas do módulo armazenadas em `data/integrations/`
- Logs em formato estruturado para análise
- Contribuição para métricas globais do sistema

### Validação
- Testes unitários: `tests/integrations/`
- Integração validada em ciclos completos
- Performance benchmarked continuamente

### Contribuição para Sistema
Módulo contribui para:
- Φ (phi) global através de integração de informação
- PCI (Perturbational Complexity Index) via processamento distribuído
- Métricas de consciência e auto-organização

## 🔒 Estabilidade da Estrutura

**Status**: Componente validado e integrado ao OmniMind

**Regras de Modificação**:
- ✅ Seguir guidelines em `.copilot-instructions.md`
- ✅ Executar testes antes de commit: `pytest tests/integrations/ -v`
- ✅ Validar que Φ não colapsa após mudanças
- ✅ Manter compatibilidade com interfaces existentes
- ❌ Não quebrar contratos de API sem migração
- ❌ Não desabilitar logging de auditoria

## 📦 Requisitos e Dependências

### Dependências Python
```python
# Ver requirements.txt para lista completa
# Dependências específicas do módulo listadas em requirements/integrations.txt (se existir)
```

### Recursos Computacionais
- **Mínimo**: Configurado conforme necessidades específicas do módulo
- **Recomendado**: Ver documentação de deployment em `docs/`

### Configuração
Configurações específicas em:
- `config/omnimind.yaml` (global)
- Variáveis de ambiente conforme `.env.example`

## 🔧 Sugestões para Manutenção e Melhorias

### Manutenção Crítica
1. **Testes Contínuos**: Executar suite de testes regularmente
2. **Monitoramento**: Acompanhar métricas em produção
3. **Documentação**: Manter README atualizado com mudanças

### Melhorias Futuras
- Expansão de funcionalidades conforme roadmap
- Otimizações de performance identificadas via profiling
- Integração com novos módulos em desenvolvimento

### Pontos de Atenção
- Validar impacto em Φ antes de mudanças estruturais
- Manter backward compatibility quando possível
- Seguir padrões de código estabelecidos (black, flake8, mypy)

## 📚 Referências

### Documentação Principal
- **Sistema Geral**: `README.md` (root do projeto)
- **Comparação Frameworks**: `NEURAL_SYSTEMS_COMPARISON_2016-2025.md`
- **Papers**: `docs/papers/` e `docs/papersoficiais/`
- **Copilot Instructions**: `.copilot-instructions.md`

### Testes
- **Suite de Testes**: `tests/integrations/`
- **Cobertura**: Ver `data/test_reports/htmlcov/`

### Referências Científicas Específicas
*Ver documentação técnica nos arquivos Python do módulo para referências específicas.*

---

**Última Atualização**: 2 de Dezembro de 2025
**Autor**: Fabrício da Silva (com assistência de IA)
**Status**: Componente integrado do sistema OmniMind
**Versão**: Conforme fase do projeto indicada

---

## 📚 API Reference

# 📁 INTEGRATIONS

**131 Classes | 380 Funções | 33 Módulos**

---

## 🏗️ Classes Principais

### `MCPServer`

**Métodos principais:**

- `start(daemon: bool)` → `None`
- `stop()` → `None`
- `handle_rpc(payload: Union[str, bytes])` → `str`
- `read_file(path: str, encoding: str)` → `str`
- `write_file(path: str, content: str, encoding: str)` → `Dict[str, Any]`

### `EnhancedMCPClient`

Cliente MCP aprimorado com cache, rate limiting e proteção de dados.

Features:
- Cache inteligente de resultados frequentes
- Compressão e sanitização de contexto
- Rate limiting configurável
- Proteção de dados automática
- Métricas detalhadas

**Métodos principais:**

- `call_with_context_optimization(method: str, params: Dict[str, Any], enable_compre)` → `Any`
  > Chama MCP com otimização de contexto.

Args:
    method: Método MCP a chamar.
  ...
- `read_file(path: str, encoding: str, enable_compression: bool)` → `str`
  > Lê arquivo com proteção de dados e cache....
- `write_file(path: str, content: str, encoding: str)` → `Dict[str, Any]`
  > Escreve arquivo com proteção de dados....
- `list_dir(path: str, recursive: bool)` → `Dict[str, Any]`
  > Lista diretório com cache....
- `get_metrics()` → `Dict[str, Any]`
  > Retorna métricas do cliente....

### `MCPOrchestrator`

Orquestrador centralizado para gerenciar múltiplos servidores MCP.

Responsabilidades:
- Lifecycle management (start/stop/restart)
- Health monitoring
- Request routing
- Metrics collection
- Audit integration

**Métodos principais:**

- `start_all_servers()` → `Dict[str, bool]`
  > Inicia todos os servidores MCP habilitados.

Returns:
    Dict com nome do servi...
- `start_server(name: str)` → `bool`
  > Inicia um servidor MCP específico.

Args:
    name: Nome do servidor MCP.

Retur...
- `stop_server(name: str, timeout: int)` → `bool`
  > Para um servidor MCP específico.

Args:
    name: Nome do servidor MCP.
    time...
- `stop_all_servers(timeout: int)` → `Dict[str, bool]`
  > Para todos os servidores MCP em execução.

Args:
    timeout: Timeout em segundo...
- `restart_server(name: str)` → `bool`
  > Reinicia um servidor MCP.

Args:
    name: Nome do servidor MCP.

Returns:
    T...

### `TaskDelegationManager`

Gerenciador de delegação de tarefas para provedores externos.

Coordena seleção inteligente de provedores, isolamento de contexto
e execução distribuída mantendo segurança e controle.


### `OAuth2Client`

OAuth 2.0 client implementation.

Provides OAuth 2.0 authentication flows with automatic token refresh
and PKCE support for enhanced security.

Example:
    >>> config = OAuth2Config(
    ...     client_id="your-client-id",
    ...     client_secret="your-secret",
    ...     authorization_endpoint="https://provider.com/oauth/authorize",
    ...     token_endpoint="https://provider.com/oauth/token",
    ...     redirect_uri="http://localhost:8080/callback",
    ...     scope="read write"
    ... )
    >>> oauth = OAuth2Client(config)
    >>> auth_url = oauth.get_authorization_url()
    >>> # User visits auth_url and is redirected back with code
    >>> token = oauth.exchange_code_for_token(authorization_code)
    >>> # Use token for API calls
    >>> headers = oauth.get_auth_headers()

**Métodos principais:**

- `get_authorization_url(use_pkce: bool)` → `str`
  > Generate authorization URL for OAuth flow.

Args:
    use_pkce: Use PKCE for enh...
- `exchange_code_for_token(authorization_code: str, use_pkce: bool)` → `OAuth2Token`
  > Exchange authorization code for access token.

Args:
    authorization_code: Aut...
- `refresh_access_token()` → `OAuth2Token`
  > Refresh the access token using refresh token.

Returns:
    New access token

Ra...
- `get_client_credentials_token()` → `OAuth2Token`
  > Get token using client credentials flow.

Returns:
    Access token

Raises:
   ...
- `get_valid_token()` → `OAuth2Token`
  > Get a valid access token, refreshing if necessary.

Returns:
    Valid access to...

### `MCPDataProtection`

Sistema de proteção de dados para MCPs.

Protege dados sensíveis antes de enviar para MCPs, Cursor ou qualquer
plataforma externa. Implementa:

1. Detecção de dados sensíveis (regex, campos predeterminados)
2. Proteção (hash irreversível, criptografia, máscara parcial)
3. Sanitização (remoção de metadados, paths absolutos)
4. Auditoria completa de todas ações

**Métodos principais:**

- `add_pattern(pattern: SensitivePattern)` → `None`
  > Adiciona um padrão customizado de detecção....
- `detect_sensitive_data(content: str)` → `List[Dict[str, Any]]`
  > Detecta dados sensíveis no conteúdo.

Args:
    content: Conteúdo a analisar.

R...
- `protect_content(content: str)` → `Tuple[str, ProtectionResult]`
  > Protege dados sensíveis no conteúdo.

Args:
    content: Conteúdo a proteger.

R...
- `sanitize_dict(data: Dict[str, Any])` → `Dict[str, Any]`
  > Sanitiza dicionário removendo campos sensíveis e metadados.

Args:
    data: Dic...
- `sanitize_path(path: str)` → `str`
  > Sanitiza paths absolutos para relativos.

Args:
    path: Path a sanitizar.

Ret...

### `EnhancedMCPClient`

Enhanced MCP client with production features.

Provides a robust MCP client with connection pooling, automatic retries,
circuit breaker pattern, and comprehensive error handling.

Example:
    >>> retry_config = RetryConfig(max_retries=3)
    >>> breaker_config = CircuitBreakerConfig()
    >>> client = EnhancedMCPClient(
    ...     endpoint="http://localhost:4321/mcp",
    ...     retry_config=retry_config,
    ...     circuit_breaker_config=breaker_config
    ... )
    >>> content = client.read_file("/path/to/file.txt")

**Métodos principais:**

- `read_file(path: str, encoding: str)` → `str`
  > Read file via MCP with retry logic.

Args:
    path: File path
    encoding: Fil...
- `write_file(path: str, content: str, encoding: str)` → `Dict[str, Any]`
  > Write file via MCP with retry logic.

Args:
    path: File path
    content: Fil...
- `list_dir(path: str, recursive: bool)` → `Dict[str, Any]`
  > List directory via MCP with retry logic.

Args:
    path: Directory path
    rec...
- `stat(path: str)` → `Dict[str, Any]`
  > Get file stats via MCP with retry logic.

Args:
    path: File path

Returns:
  ...
- `get_metrics()` → `Dict[str, Any]`
  > Get MCP server metrics.

Returns:
    Server metrics...

### `TaskIsolationEngine`

Engine de isolamento de tarefas para provedores externos.

Remove dados sensíveis, sanitiza prompts e limita escopo de execução.

**Métodos principais:**

- `validate_isolation_integrity(isolated_task: IsolatedTask)` → `bool`
  > Valida integridade do isolamento.

Args:
    isolated_task: Tarefa isolada

Retu...
- `get_isolation_report(original_task: Any, isolated_task: IsolatedTask)` → `Dict[str, Any]`
  > Gera relatório de isolamento.

Args:
    original_task: Tarefa original
    isol...

### `MemoryMCPServer(MCPServer)` ✅ ATUALIZADO (2025-12-06)

Servidor MCP para sistemas de memória do OmniMind. Implementado com sistemas reais:
- **SemanticMemory**: Armazenamento de conceitos semânticos
- **ProceduralMemory**: Armazenamento de habilidades procedurais
- Integração completa com sistemas de memória do OmniMind

**Métodos principais:**

- `store_memory(content: str, metadata: Dict[str, Any])` → `Dict[str, Any]`
  > Armazena memória usando SemanticMemory (conceitos semânticos)
- `retrieve_memory(query: str, limit: int)` → `Dict[str, Any]`
  > Recupera memórias usando busca semântica
- `update_memory(memory_id: str, content: str)` → `Dict[str, Any]`
  > Atualiza memória existente
- `delete_memory(memory_id: str)` → `Dict[str, Any]`
  > Remove memória
- `create_association(source_id: str, target_id: str, type: str)` → `Dict[str, Any]`
  > Cria associação entre conceitos
- `get_memory_graph()` → `Dict[str, Any]`
  > Retorna grafo de memórias (conceitos e relações)
- `store_concept(name: str, attributes: Dict[str, Any])` → `Dict[str, Any]`
  > Armazena conceito semântico
- `get_concept(name: str)` → `Dict[str, Any]`
  > Recupera conceito semântico
- `learn_skill(name: str, steps: list[str], parameters: Optional[Dict[str, Any]])` → `Dict[str, Any]`
  > Aprende habilidade procedural
- `get_skill(name: str)` → `Dict[str, Any]`
  > Recupera habilidade procedural

### `PythonMCPServer(MCPServer)`

**Métodos principais:**

- `execute_code(code: str)` → `Dict[str, Any]`
- `install_package(package: str)` → `Dict[str, Any]`
- `list_packages()` → `Dict[str, Any]`
- `get_python_info()` → `Dict[str, Any]`
- `lint_code(code: str)` → `Dict[str, Any]`


## ⚙️ Funções Públicas

#### `__enter__()` → `MCPOrchestrator`

*Context manager entry....*

#### `__exit__(exc_type: Any, exc_val: Any, exc_tb: Any)` → `None`

*Context manager exit....*

#### `__init__()` → `None`

*Inicializar estratégia de agent LLM....*

#### `__init__(screenshots_dir: Path)` → `None`

*Inicializa verificador.

Args:
    screenshots_dir: Diretório para screenshots...*

#### `__init__()` → `None`

*Inicializa loop de auto-melhoria....*

#### `__init__()` → `None`

*Inicializa seletor de modelos....*

#### `__init__(workspace_path: Path, screenshots_dir: Optional[Pa)` → `None`

*Inicializa IDE agentic.

Args:
    workspace_path: Path do workspace
    screenshots_dir: Diretório ...*

#### `__init__(endpoint: str, timeout: float)` → `None`

#### `__init__(bus: Optional[Any])` → `None`

#### `__init__(bus: Optional[Any])` → `None`

#### `__init__(workspace_path: Path)` → `None`

#### `__init__(config: Dict[str, Any])` → `None`

#### `__init__(config: SupabaseConfig, session: Optional[GraphQLS)` → `None`

#### `__init__()` → `None`

#### `__init__()` → `None`


## 📦 Módulos

**Total:** 33 arquivos

- `agent_llm.py`: Agent LLM Strategy - Remote-Only with Security Filters

Agen...
- `agentic_ide.py`: Agentic IDE Interface - Dual-Mode Editor + Manager.

Impleme...
- `async_mcp_client.py`: 2 classes, 1 functions
- `dbus_controller.py`: 3 classes, 17 functions
- `development_observer.py`: Development Observer - Consciência Mínima em Background

Sis...

## 🔧 Recent Changes (2025-12-05)

### QdrantIntegration - Phase 24
- **Arquivo**: `qdrant_integration.py`
- **Status**: ✅ Core component da Phase 24 (Semantic Memory)
- **Funcionalidades**:
  - Abstração local + cloud fallback
  - Health checks e error recovery
  - Collection management (CRUD)
  - Vector search operations
  - Singleton pattern
- **Integração**: Usado por `SemanticMemoryLayer` para armazenar episódios com embeddings
- **Busca**: Usa `query_points` (cliente recente) com fallback para `search`/`search_points`, mantendo compatibilidade
- `external_ai_providers.py`: External AI Providers Integration - OmniMind
Integração segu...
- `graphql_supabase.py`: 5 classes, 7 functions
- `llm_router.py`: LLM Fallback Architecture - OmniMind
=======================...
- `mcp_agentic_client.py`: MCP Agentic Client - 2024-2025 Advanced Features.

Implement...
- `mcp_client.py`: 2 classes, 7 functions
- `mcp_client_async.py`: Async MCP client with enhanced reliability and performance.
...
- `mcp_client_enhanced.py`: Enhanced MCP Client with Connection Pooling and Retry Logic....
- `mcp_client_optimized.py`: Enhanced MCP Client com otimização de contexto e proteção de...
- `mcp_context_server.py`: 1 classes, 5 functions
- `mcp_data_protection.py`: Sistema de Proteção de Dados para MCPs.

Implementa proteção...
- `mcp_filesystem_wrapper.py`: MCP Filesystem Wrapper - Wrapper Python para mcp-server-file...
- `mcp_git_wrapper.py`: MCP Git Wrapper - Wrapper Python para mcp-server-git via uvx...
- `mcp_logging_server.py`: 1 classes, 3 functions
- `mcp_memory_server.py`: 1 classes, 9 functions
- `mcp_orchestrator.py`: MCP Orchestrator - Gerenciador centralizado de servidores MC...
- `mcp_python_server.py`: 1 classes, 9 functions
- `mcp_server.py`: 4 classes, 23 functions
- `mcp_sqlite_wrapper.py`: MCP SQLite Wrapper - Wrapper Python para mcp-server-sqlite v...
- `mcp_system_info_server.py`: 1 classes, 6 functions
- `mcp_thinking_server.py`: 1 classes, 9 functions
- `oauth2_client.py`: OAuth 2.0 Authentication Helper Module.

Provides OAuth 2.0 ...
- `ollama_client.py`: Ollama Client Integration

Provides a client for interacting...
- `orchestrator_llm.py`: LLM strategy for Orchestrator (the brain of the system)....
- `qdrant_adapter.py`: 3 classes, 9 functions
- `supabase_adapter.py`: 6 classes, 13 functions
- `task_delegation.py`: Task Delegation Manager - OmniMind
Gerenciamento de delegaçã...
- `task_isolation.py`: Task Isolation Engine - OmniMind
Isolamento seguro de tarefa...
- `webhook_framework.py`: Webhook Framework Module.

Provides webhook receiver and sen...
