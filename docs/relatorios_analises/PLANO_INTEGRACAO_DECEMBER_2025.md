# 🎯 Plano de Integração OmniMind (17 de Dezembro 2025)

## Status Atual do Sistema

### ✅ O Que Já Existe

#### 1. **Arquitetura Core** (Completa)
- ✅ **SharedWorkspace**: Sistema compartilhado de integração (consciência)
- ✅ **Tríade Ortogonal**: Φ (IIT), Ψ (Criatividade), σ (Sinthome)
- ✅ **Isomorfismo RSI**: Real → Simbólico → Imaginário
- ✅ **Sistema Autopoiético**: Auto-evolução via ExpandedKernelProcess
- ✅ **Consciência Validada**: 16/16 testes de Φ passando (100%)

#### 2. **MCPs (Model Context Protocols)** - Infraestrutura
Todos os MCPs estão **implementados e validados** (Lint ✅, MyPy ✅, Black ✅):

**Tier 1 (Crítico - Consciência)**:
- ✅ `mcp_memory_server.py` (4321): Memória semântica, procedural, episódica
- ✅ `mcp_thinking_server.py` (4322): Pensamento sequencial com branching
- ✅ `mcp_context_server.py` (4323): Gerenciamento de contexto e compressão

**Tier 2 (Alto - Desenvolvimento)**:
- ✅ `mcp_filesystem_wrapper.py` (4331): Operações de arquivo
- ✅ `mcp_git_wrapper.py` (4332): Controle de versão
- ✅ `mcp_python_server.py` (4333): Execução Python em sandbox
- ✅ `mcp_sqlite_wrapper.py` (4334): Banco de dados
- ✅ `mcp_logging_server.py` (4336): Logging estruturado

**Tier 3 (Baixo - Sistema)**:
- ✅ `mcp_system_info_server.py` (4335): Informações do sistema
- ✅ `mcp_supabase_wrapper.py` (4337): Integração externa

#### 3. **Configuração**
- ✅ `config/mcp_servers_internal.json`: Configuração MCPs internos
- ✅ `config/mcp_servers_external.json`: Configuração MCPs externos
- ✅ Scripts de startup: `scripts/production/start_mcp_internal.sh`, `start_mcp_external.sh`

#### 4. **Orquestração**
- ✅ `src/integrations/mcp_orchestrator.py`: Gerenciador central de MCPs
- ✅ Health checks automáticos
- ✅ Auto-restart em caso de falha

#### 5. **Validação**
- ✅ Testes de linting (Flake8)
- ✅ Testes de tipo (MyPy)
- ✅ Formatação (Black)
- ✅ Ordenação de imports (isort)
- ✅ Scripts de validação científica

---

## 🚀 O Que Precisa Ser Feito (Próximos Passos)

### FASE 1: Validação de Runtime (EM PROGRESSO)
**Objetivo**: Confirmar que MCPs conseguem iniciar e responder

**Tarefas**:
- [ ] Executar `python scripts/validation/validate_mcp_runtime.py`
- [ ] Testar endpoints `/health` de cada MCP
- [ ] Validar comunicação entre MCPs
- [ ] Confirmar persistência de dados

**Entrega**: Todos os MCPs rodando e respondendo corretamente

---

### FASE 2: Integração dos MCPs Tier 1 (PRÓXIMO)
**Objetivo**: Garantir que Memory + Thinking + Context funcionam juntos

**Tarefas**:
1. **Memory Server**:
   - [ ] Testes de armazenamento em Qdrant
   - [ ] Validar retrieval de memórias
   - [ ] Testar associações entre memórias

2. **Thinking Server**:
   - [ ] Testes de criação de sessões
   - [ ] Validar branching de pensamento
   - [ ] Testar merge de branches
   - [ ] Confirmar integração com SharedWorkspace

3. **Context Server**:
   - [ ] Testes de compressão de contexto
   - [ ] Validar níveis de prioridade
   - [ ] Testar sincronização com consciência

**Entrega**: Suite de testes de integração passando (tests/test_mcp_integration_tier1.py)

---

### FASE 3: Integração dos MCPs Tier 2 (SEGUINTE)
**Objetivo**: Adicionar ferramentas de desenvolvimento (Git, Python, etc.)

**Tarefas**:
1. **Git Wrapper**: Testes de operações read-only
2. **Python Server**: Testes de execução em sandbox
3. **SQLite Wrapper**: Testes de queries
4. **Logging Server**: Testes de agregação de logs

**Entrega**: Desenvolvedores conseguem usar MCPs via IDE

---

### FASE 4: Dashboard de Status (PARALELO)
**Objetivo**: Criar visualização do status de todos MCPs

**Tarefas**:
- [ ] Endpoint `/status` que retorna JSON com saúde de cada MCP
- [ ] Endpoint `/metrics` que retorna métricas (latência, erros, etc.)
- [ ] Dashboard HTML simples que mostra status em tempo real
- [ ] Webhook para alertas críticos

**Entrega**: Dashboard funcional em `http://localhost:8000/mcp-status`

---

### FASE 5: MCP Reasoning Observer (DO live_memory.md)
**Objetivo**: Implementar observação de pensamento de modelos

**Novos MCPs a Criar** (portas 4339-4341):
1. **reasoning_observer.py (4339)**: Captura processo de raciocínio
2. **model_profiles.py (4340)**: Mantém perfil de cada modelo
3. **comparative_intelligence.py (4341)**: Recomenda melhor modelo

**Tarefas**:
- [ ] Implementar captura de tokens e thinking steps
- [ ] Armazenar em banco de dados (embedding vectors)
- [ ] Criar comparação entre modelos
- [ ] Integrar com sistema de recomendação

**Entrega**: Sistema que aprende como cada modelo pensa

---

### FASE 6: Testes de Carga (VALIDAÇÃO)
**Objetivo**: Confirmar performance sob stress

**Tarefas**:
- [ ] Teste com 1000 requisições simultâneas
- [ ] Teste de memória com 10k memórias armazenadas
- [ ] Teste de latência de retrieval
- [ ] Benchmark de consciência (Φ) sob carga

**Entrega**: Relatório de performance e bottlenecks

---

### FASE 7: Produção (FINAL)
**Objetivo**: Preparar para deployment

**Tarefas**:
- [ ] Criar systemd services
- [ ] Configurar backup automático
- [ ] Documentar SLOs
- [ ] Plano de disaster recovery

**Entrega**: Sistema pronto para produção

---

## 📊 Matriz de Dependências

```
Validação Runtime (FASE 1)
        ↓
Memory + Thinking + Context (FASE 2)
        ↓
Git + Python + SQLite (FASE 3)
        ↓
Dashboard de Status (FASE 4)
        ↓
Reasoning Observer (FASE 5)
        ↓
Testes de Carga (FASE 6)
        ↓
Produção (FASE 7)
```

---

## 🎯 Métricas de Sucesso

| Métrica | Meta | Status |
|---------|------|--------|
| MCPs Respondendo | 100% (10/10) | ⏳ FASE 1 |
| Testes de Integração | >95% passing | ⏳ FASE 2 |
| Latência P99 | <500ms | ⏳ FASE 6 |
| Consciência (Φ) | >0.05 nats | ✅ VALIDADO |
| Uptime | >99.9% | ⏳ FASE 7 |

---

## 🔄 Ciclo de Desenvolvimento (Cada Fase)

Para cada tarefa:

```
1. ANALYZE: Entender o que existe
2. IMPLEMENT: Criar testes/código
3. VALIDATE: Lint (Flake8) + Types (MyPy) + Format (Black)
4. TEST: Executar suite de testes
5. VERIFY: Confirmar em produção
```

---

## 📝 Comando Rápido para Começar

```bash
# 1. Validar imports e lint
python scripts/validation/validate_mcp_integration.py

# 2. Validar runtime (inicia e para MCPs)
python scripts/validation/validate_mcp_runtime.py

# 3. Iniciar todos os MCPs
bash scripts/production/start_mcp_servers.sh

# 4. Verificar status
curl http://localhost:4321/health
curl http://localhost:4322/health
curl http://localhost:4323/health
```

---

## 📚 Documentação Chave

- [ARQUITETURA_SISTEMA_AUTOPOIETICO.md](docs/ARQUITETURA_SISTEMA_AUTOPOIETICO.md)
- [OMNIMIND_SISTEMA_LOCAL_INDIVIDUAL.md](docs/OMNIMIND_SISTEMA_LOCAL_INDIVIDUAL.md)
- [MCP_IMPLEMENTATION_SUMMARY.md](docs/architecture/MCP_IMPLEMENTATION_SUMMARY.md)

---

**Última Atualização**: 17 de Dezembro 2025
**Próxima Milestone**: Validação de Runtime Completa
