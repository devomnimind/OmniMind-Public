# Módulo Ferramentas de Desenvolvimento

## 📋 Descrição Geral

**Debug, profiling, dev tools**

**Status**: DevOps

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
tools/
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
- Métricas específicas do módulo armazenadas em `data/tools/`
- Logs em formato estruturado para análise
- Contribuição para métricas globais do sistema

### Validação
- Testes unitários: `tests/tools/`
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
- ✅ Executar testes antes de commit: `pytest tests/tools/ -v`
- ✅ Validar que Φ não colapsa após mudanças
- ✅ Manter compatibilidade com interfaces existentes
- ❌ Não quebrar contratos de API sem migração
- ❌ Não desabilitar logging de auditoria

## 📦 Requisitos e Dependências

### Dependências Python
```python
# Ver requirements.txt para lista completa
# Dependências específicas do módulo listadas em requirements/tools.txt (se existir)
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
- **Suite de Testes**: `tests/tools/`
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

# 📁 TOOLS

**44 Classes | 118 Funções | 6 Módulos**

---

## 🏗️ Classes Principais

### `ASTParser`

Parser de código Python usando AST (Abstract Syntax Tree)

**Métodos principais:**

- `parse_file(filepath: str)` → `Optional[CodeStructure]`
  > Analisa arquivo Python e retorna estrutura completa.

Args:
    filepath: Caminh...
- `parse_source(source: str, filepath: str)` → `CodeStructure`
  > Analisa código-fonte Python.

Args:
    source: Código-fonte Python
    filepath...
- `validate_syntax(source: str)` → `tuple[bool, Optional[str]]`
  > Valida sintaxe de código Python.

Args:
    source: Código-fonte Python

Returns...
- `extract_imports(source: str)` → `List[str]`
  > Extrai todos os imports de código Python.

Args:
    source: Código-fonte Python...
- `find_function_calls(source: str)` → `List[str]`
  > Encontra todas as chamadas de função no código.

Args:
    source: Código-fonte ...

### `DependencyManager`

Advanced dependency management with security scanning and locking.

**Métodos principais:**

- `generate_lockfile()` → `DependencyLockfile`
  > Generate lockfile with all dependencies and their hashes.

Returns:
    Dependen...
- `save_lockfile(lockfile: DependencyLockfile)` → `None`
  > Save lockfile to disk....
- `load_lockfile()` → `Optional[DependencyLockfile]`
  > Load lockfile from disk....
- `verify_lockfile(lockfile: Optional[DependencyLockfile])` → `bool`
  > Verify that installed packages match lockfile.

Args:
    lockfile: Lockfile to ...
- `scan_vulnerabilities(use_osv: bool, use_safety: bool)` → `List[Vulnerability]`
  > Scan for security vulnerabilities in dependencies.

Args:
    use_osv: Use OSV (...

### `CodeGenerator`

AI-assisted code generator with templates and patterns.

**Métodos principais:**

- `generate_code(template_name: str, params: Dict[str, Any], output)` → `str`
  > Generate code from template.

Args:
    template_name: Name of template to use
 ...
- `generate_agent(agent_name: str, description: str, purpose: str, c)` → `str`
  > Generate a new agent class.

Args:
    agent_name: Name of agent class
    descr...
- `generate_test(module_name: str, module_path: str, class_name: st)` → `str`
  > Generate test cases for a class.

Args:
    module_name: Module name
    module_...
- `generate_api_endpoint(endpoint_name: str, description: str, prefix: str,)` → `str`
  > Generate FastAPI endpoint.

Args:
    endpoint_name: Endpoint function name
    ...
- `analyze_class_for_tests(class_obj: type)` → `List[str]`
  > Analyze a class and suggest test methods.

Args:
    class_obj: Class to analyze...

### `ToolsFramework`

Orquestrador de todas as ferramentas com 11 camadas

**Métodos principais:**

- `execute_tool(tool_name: str, **kwargs: Any)` → `Any`
  > Executa ferramenta por nome...
- `get_available_tools()` → `Dict[str, str]`
  > Lista ferramentas disponíveis por categoria...
- `get_tools_by_category(category: ToolCategory)` → `List[str]`
  > Retorna ferramentas de uma categoria...
- `verify_audit_chain()` → `bool`
  > Verifica integridade da cadeia de auditoria P0...
- `get_tool_stats()` → `Dict[str, Any]`
  > Estatísticas de uso de ferramentas...

### `SecurityAgentTool(AuditedTool)`

Wrapper around SecurityAgent with auditing.

**Métodos principais:**

- `agent()` → `Any`
  > Lazy load SecurityAgent to avoid circular imports....
- `execute(action: str, params: Optional[Dict[str, Any]])` → `Dict[str, Any]`

### `FileOperations`

Safe file operations with path validation.

**Métodos principais:**

- `read_file(path: str)` → `str`
  > Read file contents....
- `write_file(path: str, content: str)` → `str`
  > Write content to file....
- `list_files(path: str)` → `str`
  > List files in directory....

### `AuditedTool`

Base class for all tools with P0 immutable auditing.

**Métodos principais:**

- `execute(**kwargs: Any)` → `Any`
  > Abstract method - must be overridden by subclasses....

### `ShellExecutor`

Execute shell commands with whitelist and timeout.

**Métodos principais:**

- `execute(command: str)` → `str`
  > Execute whitelisted command....

### `SystemMonitor`

Monitor system resources.

**Métodos principais:**

- `get_info()` → `Dict[str, Any]`
  > Get current system metrics....
- `format_info(info: Dict[str, Any])` → `str`
  > Format system info as string....

### `DependencyLockfile`

Lockfile for dependency versions with hashes.

**Métodos principais:**

- `to_dict()` → `Dict[str, Any]`
  > Convert to dictionary....
- `from_dict(cls: Any, data: Dict[str, Any])` → `DependencyLockfile`
  > Create from dictionary....


## ⚙️ Funções Públicas

#### `__init__(allowed_dirs: List[str])` → `None`

#### `__init__(whitelist: List[str], timeout: int)` → `None`

#### `__init__()` → `None`

#### `__init__()` → `None`

*Initialize code generator....*

#### `__init__(requirements_file: Path, lockfile: Path)` → `None`

*Initialize dependency manager.

Args:
    requirements_file: Path to requirements.txt
    lockfile: ...*

#### `__init__()` → `None`

#### `__init__()` → `None`

#### `__init__()` → `None`

#### `__init__()` → `None`

#### `__init__()` → `None`

#### `__init__()` → `None`

#### `__init__()` → `None`

#### `__init__()` → `None`

#### `__init__(allowed_commands: Optional[List[str]])` → `None`

#### `__init__()` → `None`


## 📦 Módulos

**Total:** 6 arquivos

- `agent_tools.py`: Agent Tools for OmniMind
Provides safe file operations, shel...
- `ast_parser.py`: AST Parser Tool - Análise e Geração de Código Python usando ...
- `code_generator.py`: AI-Assisted Code Generation Tools for OmniMind.

Provides in...
- `dependency_manager.py`: Advanced Dependency Management System for OmniMind.

Provide...
- `omnimind_tools.py`: OmniMind Tools Framework - Sistema Completo de Ferramentas p...
- `tool_base.py`: Base classes for OmniMind Tools Framework.

This module cont...
