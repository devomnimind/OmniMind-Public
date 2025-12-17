# 🧠 Guia de Uso: MCPs Prioritários OmniMind

**Data:** 2025-11-21
**Versão:** 1.0.0
**Público-alvo:** AIs trabalhando no projeto OmniMind

---

## 📋 INTRODUÇÃO

Este guia explica como utilizar os servidores MCP (Model Context Protocol) prioritários configurados para o projeto OmniMind. Os MCPs facilitam o trabalho de AIs, fornecendo ferramentas estruturadas, auditadas e conformes com as regras do projeto.

### Benefícios para AIs

✅ **Acesso estruturado ao código** - Navegação e modificação segura
✅ **Memória persistente** - Conhecimento mantido entre sessões
✅ **Raciocínio auditável** - Chain-of-thought documentado
✅ **Conformidade automática** - Segurança e auditoria integradas
✅ **Performance otimizada** - Processamento 100% local

---

## 🚀 QUICK START

### Pré-requisitos

```bash
# 1. Python 3.12.8 (OBRIGATÓRIO)
python --version  # Deve ser 3.12.x

# 2. Qdrant local (para Memory MCP)
docker run -d -p 6333:6333 qdrant/qdrant:v1.7.3

# 3. Dependências instaladas
pip install -r requirements.txt
```

### Inicialização dos MCPs

```python
from src.integrations.mcp_orchestrator import MCPOrchestrator

# Inicializar orquestrador
orchestrator = MCPOrchestrator()

# Iniciar todos servidores habilitados
results = orchestrator.start_all_servers()

print(f"Servidores iniciados: {sum(results.values())}/{len(results)}")

# Verificar status
for name, status in orchestrator.get_all_statuses().items():
    print(f"{name}: running={status.running}, healthy={status.healthy}")
```

### Context Manager (Recomendado)

```python
from src.integrations.mcp_orchestrator import MCPOrchestrator

# Uso com context manager (inicia e para automaticamente)
with MCPOrchestrator() as orchestrator:
    # Trabalhar com MCPs
    status = orchestrator.get_all_statuses()
    print(f"MCPs ativos: {sum(s.running for s in status.values())}")
    
# MCPs são parados automaticamente ao sair do contexto
```

---

## 🗂️ TIER 1: MCPs CRÍTICOS

### 1️⃣ Filesystem MCP

**Propósito:** Acesso seguro e auditado ao filesystem do projeto.

#### Operações Disponíveis

```python
from src.integrations.mcp_client import MCPClient

# Conectar ao Filesystem MCP
fs_client = MCPClient(endpoint="http://127.0.0.1:4321/filesystem")

# 1. Ler arquivo
content = fs_client.read_file("src/agents/orchestrator_agent.py")
print(f"Arquivo tem {len(content)} caracteres")

# 2. Listar diretório
files = fs_client.list_dir("src/agents", recursive=False)
print(f"Arquivos encontrados: {files}")

# 3. Obter metadados
metadata = fs_client.stat("README.md")
print(f"Tamanho: {metadata['size']} bytes")
print(f"Modificado: {metadata['modified']}")

# 4. Escrever arquivo (com auditoria automática)
result = fs_client.write_file(
    path="docs/temp/nota.md",
    content="# Nota\n\nConteúdo da nota."
)
print(f"Escrita concluída: {result}")
```

#### Caminhos Permitidos

✅ **Permitidos:**
- `src/` - Código-fonte
- `tests/` - Testes
- `docs/` - Documentação
- `config/` - Configurações
- `scripts/` - Scripts
- `web/` - Frontend/Backend web

❌ **Proibidos:**
- `.git/` - Diretório Git (usar Git MCP)
- `.venv/` - Ambiente virtual
- `logs/` - Logs (somente leitura via Logging MCP)
- `__pycache__/` - Cache Python
- `.omnimind/hsm/` - Secrets management

#### Melhores Práticas

1. **Sempre validar paths antes de escrever**
   ```python
   path = "src/new_feature/module.py"
   # Verificar se path é permitido
   if not path.startswith(tuple(["src/", "tests/", "docs/"])):
       raise ValueError(f"Path não permitido: {path}")
   ```

2. **Usar read antes de write para evitar sobrescrever**
   ```python
   # Ler conteúdo existente
   try:
       existing = fs_client.read_file(path)
       # Decidir se pode sobrescrever
   except FileNotFoundError:
       # Arquivo não existe, seguro criar
       pass
   ```

3. **Auditoria é automática** - Todas operações são logadas

---

### 2️⃣ Memory MCP

**Propósito:** Memória persistente baseada em grafo semântico com Qdrant.

#### Armazenar Conhecimento

```python
from src.integrations.mcp_memory_client import MemoryMCPClient

# Conectar ao Memory MCP
memory = MemoryMCPClient()

# Armazenar conhecimento sobre código
memory.store_memory(
    content="O OrchestratorAgent usa análise psicoanalítica (Freud/Lacan) para delegação de tarefas",
    metadata={
        "category": "code_knowledge",
        "source_file": "src/agents/orchestrator_agent.py",
        "confidence": 0.95,
        "tags": ["psicoanálise", "delegação", "agentes"]
    },
    category="code_knowledge"
)

# Armazenar decisão de design
memory.store_memory(
    content="Decidimos usar Qdrant local em vez de cloud para garantir 100% privacidade de dados",
    metadata={
        "category": "decisions",
        "date": "2025-11-21",
        "reason": "compliance_lgpd",
        "impact": "high"
    },
    category="decisions"
)

# Armazenar padrão identificado
memory.store_memory(
    content="Padrão: Todos os agentes herdam de AgentProtocol e implementam execute_task()",
    metadata={
        "category": "patterns",
        "pattern_type": "architecture",
        "files": ["src/agents/*.py"]
    },
    category="patterns"
)
```

#### Buscar Conhecimento

```python
# Busca semântica
results = memory.retrieve_memory(
    query="Como funciona a delegação de tarefas no orquestrador?",
    top_k=5,
    filters={"category": "code_knowledge"}
)

for result in results:
    print(f"Score: {result.score:.2f}")
    print(f"Conteúdo: {result.content}")
    print(f"Metadata: {result.metadata}")
    print("---")

# Buscar decisões anteriores sobre um tema
decisions = memory.retrieve_memory(
    query="decisões sobre privacidade e armazenamento de dados",
    top_k=3,
    filters={"category": "decisions"}
)
```

#### Criar Associações (Grafo de Conhecimento)

```python
# Obter IDs dos memories relacionados
orchestrator_id = "mem_123abc"
psych_analyst_id = "mem_456def"

# Criar relação
memory.create_association(
    id1=orchestrator_id,
    id2=psych_analyst_id,
    relation_type="uses"  # "uses", "extends", "implements", "requires", etc.
)

# Navegar grafo
graph = memory.get_memory_graph(
    start_id=orchestrator_id,
    depth=2  # Profundidade de navegação
)

print(f"Nós relacionados: {len(graph['nodes'])}")
print(f"Relações: {len(graph['edges'])}")
```

#### Consolidação de Memórias

```python
# Consolidar memórias similares (evitar duplicação)
consolidation_report = memory.consolidate_memories(
    category="code_knowledge",
    strategy="semantic_similarity",  # ou "temporal", "frequency"
    threshold=0.9  # Similaridade mínima para mesclar
)

print(f"Memórias antes: {consolidation_report['before_count']}")
print(f"Memórias depois: {consolidation_report['after_count']}")
print(f"Mescladas: {consolidation_report['merged_count']}")
```

#### Coleções Disponíveis

1. **code_knowledge** - Conhecimento sobre o código
2. **decisions** - Decisões de design/implementação
3. **patterns** - Padrões identificados
4. **errors** - Erros e suas soluções
5. **ai_sessions** - Memória de sessões de trabalho

---

### 3️⃣ Sequential Thinking MCP

**Propósito:** Raciocínio sequencial estruturado e auditável (chain-of-thought).

#### Iniciar Sessão de Raciocínio

```python
from src.integrations.mcp_thinking_client import ThinkingMCPClient

# Conectar ao Sequential Thinking MCP
thinking = ThinkingMCPClient()

# Iniciar nova sessão
session_id = thinking.start_thinking_session(
    task_description="Implementar validação de tipos para novo módulo de memória"
)

print(f"Sessão iniciada: {session_id}")
```

#### Adicionar Etapas de Raciocínio

```python
# Etapa 1: Observação
thinking.add_thought_step(
    session_id=session_id,
    content="O módulo atual não valida tipos de entrada, causando erros em runtime",
    step_type="observation"
)

# Etapa 2: Hipótese
thinking.add_thought_step(
    session_id=session_id,
    content="Adicionar type hints e usar mypy pode prevenir esses erros",
    step_type="hypothesis"
)

# Etapa 3: Análise
thinking.add_thought_step(
    session_id=session_id,
    content="""
    Opções analisadas:
    1. Type hints + mypy (leve, integrado com CI)
    2. Pydantic (robusto, mas overhead)
    3. Runtime validation manual (trabalhoso)
    
    Recomendação: Type hints + mypy (alinhado com padrões do projeto)
    """,
    step_type="analysis"
)

# Etapa 4: Decisão
thinking.add_thought_step(
    session_id=session_id,
    content="Decisão: Implementar type hints completos e configurar mypy strict",
    step_type="decision"
)

# Etapa 5: Ação
thinking.add_thought_step(
    session_id=session_id,
    content="Adicionando type hints em src/memory/episodic_memory.py",
    step_type="action"
)

# Etapa 6: Reflexão
thinking.add_thought_step(
    session_id=session_id,
    content="Type hints adicionados. mypy --strict passou. Solução efetiva e alinhada com projeto.",
    step_type="reflection"
)
```

#### Branching (Múltiplas Hipóteses)

```python
# Criar branch para explorar alternativa
branch_id = thinking.branch_thinking(
    session_id=session_id,
    branch_name="alternative_pydantic"
)

# Adicionar pensamentos na branch
thinking.add_thought_step(
    session_id=branch_id,
    content="Explorando Pydantic como alternativa...",
    step_type="hypothesis"
)

# Comparar branches e escolher melhor
main_quality = thinking.evaluate_thinking_quality(session_id)
alt_quality = thinking.evaluate_thinking_quality(branch_id)

print(f"Qualidade main: {main_quality}")
print(f"Qualidade alternativa: {alt_quality}")

# Mesclar branch vencedora (se necessário)
if alt_quality > main_quality:
    thinking.merge_thinking_branches(
        session_id=session_id,
        branches=[branch_id]
    )
```

#### Recuperar Histórico

```python
# Obter histórico completo da sessão
history = thinking.get_thinking_history(session_id)

print(f"Total de etapas: {len(history['steps'])}")

for step in history['steps']:
    print(f"[{step['step_type']}] {step['content'][:50]}...")
```

#### Exportar para Auditoria

```python
# Exportar chain-of-thought para auditoria
export_path = thinking.export_thinking_chain(
    session_id=session_id,
    format="markdown"  # ou "json", "html"
)

print(f"Chain-of-thought exportado para: {export_path}")
# Arquivo é automaticamente adicionado ao sistema de auditoria
```

#### Retomar Sessão Anterior

```python
# Retomar sessão interrompida
thinking.resume_thinking_session(session_id)

# Continuar adicionando etapas
thinking.add_thought_step(
    session_id=session_id,
    content="Retomando trabalho após interrupção...",
    step_type="observation"
)
```

---

## 🥈 TIER 2: MCPs ALTA PRIORIDADE

### 4️⃣ Context Management MCP

**Propósito:** Gerenciar contexto hierárquico em 7 níveis.

```python
from src.integrations.mcp_context_client import ContextMCPClient

context = ContextMCPClient()

# Adicionar contexto de projeto (nível 1 - permanente)
context.push_context(
    level="project",
    data={
        "name": "OmniMind",
        "version": "1.0.0",
        "python_version": "3.12.8",
        "architecture": "multi-agent psychoanalytic"
    }
)

# Adicionar contexto de sessão (nível 2)
context.push_context(
    level="session",
    data={
        "session_id": "sess_2025_11_21_001",
        "goal": "Implementar MCPs prioritários",
        "started_at": "2025-11-21T10:00:00Z"
    }
)

# Adicionar contexto de tarefa (nível 3)
context.push_context(
    level="task",
    data={
        "task_id": "task_123",
        "description": "Criar Filesystem MCP wrapper",
        "priority": "critical"
    }
)

# Obter contexto completo (hierárquico)
full_context = context.get_full_context()
print(f"Contexto total: {len(full_context)} níveis")

# Comprimir contexto se muito grande
if context.get_token_count() > 80000:
    compressed = context.compress_context(strategy="semantic")
    print(f"Contexto comprimido: {compressed['tokens_saved']} tokens economizados")
```

---

### 5️⃣ Git MCP

**Propósito:** Operações Git auditadas e seguras.

```python
from src.integrations.mcp_git_client import GitMCPClient

git = GitMCPClient()

# Ver status
status = git.git_status()
print(f"Branch atual: {status['branch']}")
print(f"Arquivos modificados: {len(status['modified'])}")

# Ver diff
diff = git.git_diff(path="src/integrations/mcp_orchestrator.py")
print(diff)

# Adicionar arquivos
git.git_add(["src/integrations/mcp_orchestrator.py"])

# Commit (auditado automaticamente)
result = git.git_commit(
    message="feat: Adicionar MCP Orchestrator",
    files=["src/integrations/mcp_orchestrator.py"]
)
print(f"Commit: {result['commit_hash']}")

# Listar branches
branches = git.git_branch_list()
print(f"Branches: {branches}")

# Ver histórico
log = git.git_log(n=5)
for commit in log:
    print(f"{commit['hash'][:7]} - {commit['message']}")
```

---

### 6️⃣ Python Environment MCP

**Propósito:** Executar código Python com isolamento e validação.

```python
from src.integrations.mcp_python_client import PythonMCPClient

python = PythonMCPClient()

# Executar código (isolado)
result = python.execute_code(
    code="""
import sys
print(f"Python: {sys.version}")
print(f"Executando em ambiente isolado")
""",
    timeout=5
)

print(result['stdout'])

# Lint código
lint_result = python.lint_code(
    code="def func(x,y): return x+y",
    linter="flake8"
)
print(f"Lint issues: {lint_result['issues']}")

# Type check
type_result = python.type_check(
    code="""
def add(x: int, y: int) -> int:
    return x + y

result: str = add(1, 2)  # Erro de tipo
"""
)
print(f"Type errors: {type_result['errors']}")

# Formatar código
formatted = python.format_code(
    code="def func( x , y ): return x + y",
    formatter="black"
)
print(formatted)
```

---

## 🥉 TIER 3: MCPs COMPLEMENTARES

### 7️⃣ SQLite MCP

```python
from src.integrations.mcp_sqlite_client import SQLiteMCPClient

db = SQLiteMCPClient()

# Executar query
results = db.execute_query(
    db_name="cache",
    query="SELECT * FROM computation_cache WHERE key = ?",
    params=["feature_embeddings_v1"]
)

# Inserir dados
db.execute_query(
    db_name="metrics",
    query="INSERT INTO performance_metrics (name, value, timestamp) VALUES (?, ?, ?)",
    params=["mcp_latency", 45.2, time.time()]
)
```

---

### 8️⃣ System Info MCP

```python
from src.integrations.mcp_system_info_client import SystemInfoMCPClient

sysinfo = SystemInfoMCPClient()

# Obter info da GPU
gpu_info = sysinfo.get_gpu_info()
print(f"GPU: {gpu_info['name']}")
print(f"VRAM disponível: {gpu_info['vram_available_mb']} MB")

# Info da CPU
cpu_info = sysinfo.get_cpu_info()
print(f"CPU load: {cpu_info['load_percent']}%")

# Memória
mem_info = sysinfo.get_memory_info()
print(f"RAM disponível: {mem_info['available_gb']} GB")
```

---

## 🔒 SEGURANÇA E AUDITORIA

### Auditoria Automática

Todas as operações nos MCPs são automaticamente auditadas:

```python
from src.audit.immutable_audit import get_audit_system

audit = get_audit_system()

# Ver logs recentes de MCPs
logs = audit.query_logs(
    category="filesystem_mcp",
    limit=10
)

for log in logs:
    print(f"[{log['timestamp']}] {log['action']}: {log['data']}")
```

### Validação de Integridade

```python
# Verificar integridade da cadeia de auditoria
integrity_ok = audit.verify_chain_integrity()
print(f"Integridade da auditoria: {'OK' if integrity_ok else 'FALHA'}")
```

---

## 📊 MONITORAMENTO E MÉTRICAS

### Exportar Métricas

```python
from src.integrations.mcp_orchestrator import MCPOrchestrator

orchestrator = MCPOrchestrator()
metrics = orchestrator.export_metrics()

print(f"Servidores rodando: {metrics['running_servers']}/{metrics['total_servers']}")
print(f"Servidores saudáveis: {metrics['healthy_servers']}")

for name, server_metrics in metrics['servers'].items():
    print(f"\n{name}:")
    print(f"  Requests: {server_metrics['total_requests']}")
    print(f"  Error rate: {server_metrics['error_rate']:.2%}")
    print(f"  Avg response: {server_metrics['avg_response_time_ms']:.2f}ms")
```

---

## 🛠️ TROUBLESHOOTING

### Servidor não inicia

```python
# Verificar logs de erro
status = orchestrator.get_server_status("filesystem")
if status.error_message:
    print(f"Erro: {status.error_message}")

# Tentar reiniciar
success = orchestrator.restart_server("filesystem")
print(f"Reinício: {'sucesso' if success else 'falha'}")
```

### Performance lenta

```python
# Verificar métricas
metrics = orchestrator.export_metrics()
for name, m in metrics['servers'].items():
    if m['avg_response_time_ms'] > 100:
        print(f"ALERTA: {name} com latência alta: {m['avg_response_time_ms']}ms")
```

---

## 📚 EXEMPLOS PRÁTICOS

### Workflow Completo: Implementar Nova Feature

```python
from src.integrations.mcp_orchestrator import MCPOrchestrator
from src.integrations.mcp_thinking_client import ThinkingMCPClient
from src.integrations.mcp_memory_client import MemoryMCPClient
from src.integrations.mcp_client import MCPClient

# 1. Iniciar MCPs
with MCPOrchestrator() as orchestrator:
    thinking = ThinkingMCPClient()
    memory = MemoryMCPClient()
    fs = MCPClient(endpoint="http://127.0.0.1:4321/filesystem")
    
    # 2. Iniciar sessão de raciocínio
    session_id = thinking.start_thinking_session(
        task_description="Implementar novo módulo de analytics"
    )
    
    # 3. Buscar conhecimento relevante
    relevant_knowledge = memory.retrieve_memory(
        query="padrões de implementação de módulos",
        top_k=3
    )
    
    thinking.add_thought_step(
        session_id=session_id,
        content=f"Conhecimento recuperado: {len(relevant_knowledge)} memórias relevantes",
        step_type="observation"
    )
    
    # 4. Analisar código existente
    existing_modules = fs.list_dir("src/", recursive=True)
    analytics_exists = any("analytics" in f for f in existing_modules)
    
    thinking.add_thought_step(
        session_id=session_id,
        content=f"Módulo analytics existe: {analytics_exists}",
        step_type="observation"
    )
    
    # 5. Tomar decisão
    thinking.add_thought_step(
        session_id=session_id,
        content="Decisão: Criar novo módulo src/analytics/ seguindo padrão do projeto",
        step_type="decision"
    )
    
    # 6. Implementar
    code = '''"""
Módulo de analytics do OmniMind.
"""

def analyze_performance():
    pass
'''
    
    fs.write_file("src/analytics/__init__.py", code)
    
    thinking.add_thought_step(
        session_id=session_id,
        content="Módulo criado com sucesso",
        step_type="action"
    )
    
    # 7. Armazenar conhecimento
    memory.store_memory(
        content="Criado módulo src/analytics/ seguindo padrão do projeto",
        metadata={
            "category": "code_knowledge",
            "date": "2025-11-21",
            "files": ["src/analytics/__init__.py"]
        },
        category="code_knowledge"
    )
    
    # 8. Reflexão
    thinking.add_thought_step(
        session_id=session_id,
        content="Feature implementada com sucesso. Conhecimento armazenado para futuras referências.",
        step_type="reflection"
    )
    
    # 9. Exportar chain-of-thought
    thinking.export_thinking_chain(session_id, format="markdown")
    
print("Workflow completo executado com sucesso!")
```

---

## ✅ CHECKLIST PARA AIs

Antes de começar a trabalhar no projeto:

- [ ] MCPs iniciados (`orchestrator.start_all_servers()`)
- [ ] Qdrant rodando (para Memory MCP)
- [ ] Auditoria verificada (`audit.verify_chain_integrity()`)
- [ ] Contexto de projeto carregado
- [ ] Conhecimento relevante recuperado da memória

Durante o trabalho:

- [ ] Usar Sequential Thinking para raciocínio estruturado
- [ ] Armazenar decisões importantes na memória
- [ ] Validar paths antes de operações de filesystem
- [ ] Commitar com mensagens descritivas (via Git MCP)
- [ ] Exportar chain-of-thought ao final

Ao finalizar:

- [ ] Consolidar memórias (evitar duplicação)
- [ ] Verificar métricas dos MCPs
- [ ] Exportar relatório final
- [ ] Parar MCPs gracefully

---

## 📖 REFERÊNCIAS

- **Análise de MCPs:** `docs/architecture/MCP_PRIORITY_ANALYSIS.md`
- **Configuração:** `config/mcp_servers.json`
- **MCP Orchestrator:** `src/integrations/mcp_orchestrator.py`
- **Auditoria:** `src/audit/immutable_audit.py`

---

**Guia criado por:** GitHub Copilot Agent
**Para:** AIs trabalhando no projeto OmniMind
**Data:** 2025-11-21
