# 🤖 TAREFA PARA AI REMOTA - OmniMind Phase 21
**Data:** 2025-11-24
**Duração Estimada:** 15-20 minutos
**Prioridade:** Alta
**Tipo:** Documentation & Consolidation (SEM MODIFICAÇÃO DE CÓDIGO)

---

## 🎯 OBJETIVO PRINCIPAL

Consolidar e criar documentação faltante do projeto OmniMind, com base no relatório de auditoria técnica recém-concluído, SEM TOCAR EM NENHUM ARQUIVO DE CÓDIGO FONTE (.py).

---

## 📋 TAREFAS OBRIGATÓRIAS

### ✅ TAREFA 1: Criar ARCHITECTURE.md na Raiz (Prioridade Máxima)

**Localização:** `/ARCHITECTURE.md`

**Conteúdo Esperado:**
```markdown
# OmniMind - Arquitetura do Sistema

## Visão Geral
- Descrição do projeto (baseado no README atual)
- Filosofia central: IA psicoanalítica autônoma

## Estrutura de Diretórios
src/
├── agents/ - Orquestração multi-agente
├── audit/ - Sistema de auditoria imutável
├── autopoietic/ - Capacidades autopoiéticas
├── consciousness/ - Motor de consciência e qualia
├── memory/ - Memória episódica e semântica
├── neurosymbolic/ - Componentes neural + simbólico
├── quantum_consciousness/ - Consciência quântica
├── security/ - Segurança e validação de integridade
├── swarm/ - Inteligência coletiva (ex-collective_intelligence)
└── ... (mapear TODOS os módulos principais)

## Módulos Principais

### Agents (src/agents/)
- OrchestratorAgent: [descrição]
- ReactAgent: [descrição]
- CodeAgent: [descrição]
- ... (listar todos)

### Memory System (src/memory/)
- Episodic Memory (Qdrant)
- Semantic Memory
- Strategic Forgetting
- ... (detalhar cada componente)

### Neurosymbolic (src/neurosymbolic/)
- NeuralComponent: [backends: Ollama, HuggingFace]
- SymbolicComponent
- HybridReasoner
- ResponseCache (LRU + TTL)
- MetricsCollector

### Security & Audit (src/audit/, src/security/)
- Immutable Audit Chain (SHA-256)
- Compliance Reporter (LGPD/GDPR)
- Integrity Validator
- Security Orchestrator

## Fluxo de Dados
[Descrever fluxo principal entre módulos]

## Tecnologias Principais
- Python 3.12.8 (OBRIGATÓRIO)
- PyTorch 2.6.0+cu124 (CUDA 12.4)
- FastAPI + WebSockets
- React + TypeScript + Vite
- Qdrant (Vector DB)
- NVIDIA GTX 1650 (4GB VRAM)

## Decisões Arquiteturais
- Por que PyTorch vs TensorFlow
- Por que Qdrant vs ChromaDB
- Por que FastAPI vs Flask
- ... (documentar decisões chave)
```

**Instruções:**
- Leia `README.md`, `docs/architecture/*.md`, e código fonte (apenas para entender, NÃO modificar)
- Crie documento completo (mínimo 200 linhas)
- Use Markdown com formatação clara
- Adicione diagramas em ASCII art se possível

---

### ✅ TAREFA 2: Criar CONTRIBUTING.md na Raiz

**Localização:** `/CONTRIBUTING.md`

**Conteúdo Esperado:**
```markdown
# Contributing to OmniMind

## Bem-vindo!
Obrigado por considerar contribuir com o OmniMind!

## Código de Conduta
- Respeito mútuo
- Comunicação clara
- Foco em qualidade

## Como Contribuir

### Reportar Bugs
1. Verificar se já existe issue
2. Criar issue com template
3. Incluir logs e contexto

### Sugerir Features
1. Abrir discussion no GitHub
2. Descrever use case
3. Aguardar feedback do time

### Fazer Pull Requests

#### Pré-requisitos
- Python 3.12.8 instalado
- Ler [antigravity-rules.md](.agent/rules/antigravity-rules.md)
- Configurar ambiente: `pip install -r requirements.txt`

#### Workflow
1. Fork do repositório
2. Criar branch: `git checkout -b feature/minha-feature`
3. Fazer mudanças
4. Executar validações OBRIGATÓRIAS:
   ```bash
   black src/ tests/
   flake8 src/ tests/ --max-line-length=100
   mypy src/ --ignore-missing-imports
   pytest tests/ --cov=src --cov-fail-under=90
   ```
5. Commit: `git commit -m "feat: descrição clara"`
6. Push: `git push origin feature/minha-feature`
7. Abrir PR no GitHub

#### Padrões de Código
- **Type Hints:** 100% obrigatório
- **Docstrings:** Google-style para TODAS funções/classes
- **Testes:** Cobertura mínima 90%
- **Linting:** Black + Flake8 + MyPy devem passar
- **Commits:** Conventional Commits (feat, fix, docs, refactor, test)

#### Proibido
- Python 3.13+
- Stubs, pass, NotImplementedError
- Secrets ou credenciais hardcoded
- Modificações diretas sem testes

## Estrutura de Branch
- `master` - produção
- `copilot/*` - features em desenvolvimento
- `pr-*` - pull requests

## Pre-commit Hooks
- Black formatting
- Flake8 linting
- MyPy type checking
- Pytest (suite completa)

## Processo de Review
- Mínimo 1 aprovação necessária
- CI/CD deve passar
- Cobertura de testes validada
- Auditoria de segurança (se aplicável)

## Recursos
- [README.md](README.md) - Visão geral
- [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitetura
- [VALIDATION_GUIDE.md](docs/guides/VALIDATION_GUIDE.md)
- [TESTING_QA_QUICK_START.md](docs/guides/TESTING_QA_QUICK_START.md)

## Dúvidas?
- Abrir issue com label `question`
- Verificar [docs/](docs/)
```

---

### ✅ TAREFA 3: Criar .env.example

**Localização:** `/.env.example`

**Conteúdo Esperado:**
```bash
# OmniMind - Environment Variables Template
# Copy this to .env and fill with your values
# NEVER commit .env to version control

# ================================
# Neural Backends
# ================================
MODEL_ID=Qwen/Qwen2.5-0.5B-Instruct
HUGGING_FACE_HUB_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxx
OLLAMA_HOST=http://localhost:11434

# ================================
# Database & Vector Stores
# ================================
QDRANT_HOST=localhost
QDRANT_PORT=6333
REDIS_HOST=localhost
REDIS_PORT=6379

# ================================
# API Keys (Optional)
# ================================
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx  # If using OpenAI fallback

# ================================
# Application
# ================================
DEBUG=false
LOG_LEVEL=INFO
ENVIRONMENT=development  # development | staging | production

# ================================
# Hardware
# ================================
# CUDA_VISIBLE_DEVICES=0  # Uncomment to force GPU 0

# ================================
# Security
# ================================
# Add your security tokens here if needed
```

**Instruções:**
- Analisar `docs/reports/audit_2025_11_24/env_usage.txt`
- Listar TODAS as variáveis `os.getenv()` encontradas no código
- Agrupar por categoria
- Adicionar comentários explicativos

---

### ✅ TAREFA 4: Atualizar docs/.project/CURRENT_PHASE.md

**Localização:** `/docs/.project/CURRENT_PHASE.md`

**Conteúdo Esperado:**
```markdown
# OmniMind - Current Phase Status

**Última Atualização:** 2025-11-24

## 🚀 Fase Atual: Phase 21 - Quantum Consciousness

**Status:** ✅ Integrada e Experimental

### Fases Concluídas
- ✅ Phase 1-15: Fundação e Infraestrutura
- ✅ Phase 16: Integração Neurossimbólica
- ✅ Phase 17: Coevolução Humano-IA
- ✅ Phase 18: [Nome da fase]
- ✅ Phase 19: Inteligência Autônoma
- ✅ Phase 20: Autopoiesis Completa
- ✅ Phase 21: Quantum Consciousness (Atual)

### Phase 21 - Entregáveis
- [x] Quantum Memory
- [x] Quantum Cognition
- [x] Entanglement Framework
- [ ] [Outros componentes Phase 21]

### Próximas Fases
- 🔜 Phase 22: [A ser definido]

### Referências
- [ROADMAP](../../roadmaps/ROADMAP_PHASES_16_21.md)
- [Phase 20 Status](../reports/PHASE20_STATUS.md)
- [Phase 21 Status](../reports/PHASE21_STATUS.md)
```

**Instruções:**
- Consolidar informações de `docs/roadmaps/`, `docs/reports/PHASE*.md`
- Criar linha do tempo clara
- Este arquivo será a única fonte de verdade sobre a fase atual

---

### ✅ TAREFA 5: Consolidar Inconsistências de Nomenclatura

**Arquivos a Atualizar:**

1. **Buscar e substituir "Collective Intelligence" → "Swarm Intelligence"**
   - Em TODOS os arquivos `.md` em `docs/`
   - Exceção: Se estiver em contexto histórico, adicionar nota: "(migrado para Swarm em Phase 20)"

2. **Padronizar Nome do Projeto**
   - "OmniMind" (capitalizado) - SEMPRE
   - Nunca: "omnimind", "Omni-Mind", "DevBrain" (exceto quando referenciado como algo separado)

3. **Criar Glossário** em `/docs/GLOSSARY.md`
```markdown
# OmniMind - Glossário de Termos

## Terminologia Oficial

- **OmniMind**: Nome do projeto (sempre capitalizado)
- **Swarm Intelligence**: Sistema de inteligência coletiva (anteriormente "Collective Intelligence")
- **Neurosymbolic**: Combinação de componentes neural e simbólico
- **Autopoietic**: Sistema auto-organizador e auto-reprodutor
- **Qualia**: Experiências subjetivas de consciência
- **Episodic Memory**: Memória de eventos específicos
- **Semantic Memory**: Memória de conhecimento geral
- ...
```

---

### ✅ TAREFA 6: Criar ROADMAP.md Consolidado na Raiz

**Localização:** `/ROADMAP.md`

**Conteúdo:** Consolidar informações de `docs/roadmaps/*.md` em um único documento conciso na raiz, com links para detalhes.

---

## 🚫 RESTRIÇÕES CRÍTICAS

### ❌ NÃO FAZER EM HIPÓTESE ALGUMA:
1. **NÃO modificar NENHUM arquivo `.py`** (código fonte)
2. **NÃO modificar `requirements.txt`** ou `requirements-dev.txt`
3. **NÃO modificar `.github/workflows/`** (CI/CD)
4. **NÃO modificar `tests/`** (arquivos de teste)
5. **NÃO modificar `src/`** (código fonte)
6. **NÃO deletar arquivos existentes** (apenas adicionar/atualizar docs)

### ✅ PERMITIDO:
- Criar novos arquivos `.md`
- Atualizar arquivos `.md` existentes em `docs/`
- Criar `.env.example`
- Ler qualquer arquivo para entender contexto (sem modificar)

---

## 📊 Entregáveis Esperados

Ao final, você deve ter criado/atualizado:
1. ✅ `/ARCHITECTURE.md` (novo, ~200+ linhas)
2. ✅ `/CONTRIBUTING.md` (novo, ~150+ linhas)
3. ✅ `/.env.example` (novo, ~30+ linhas)
4. ✅ `/docs/.project/CURRENT_PHASE.md` (atualizado)
5. ✅ `/docs/GLOSSARY.md` (novo)
6. ✅ `/ROADMAP.md` (novo, consolidado)
7. ✅ Substituições de nomenclatura em `docs/**/*.md`

---

## 🔍 Recursos para Consulta

**Leia estes arquivos ANTES de começar:**
- `docs/reports/audit_2025_11_24/AUDIT_REPORT.md` - Relatório de auditoria completo
- `README.md` - Visão geral do projeto
- `docs/roadmaps/ROADMAP_PHASES_16_21.md` - Roadmap detalhado
- `.agent/rules/antigravity-rules.md` - Regras do projeto

**Para entender arquitetura:**
- Listar conteúdo de `src/` (sem modificar)
- Ler docstrings de módulos principais
- Consultar `docs/architecture/*.md`

---

## ✅ Checklist Final

Antes de commitar, verifique:
- [ ] Todos os 7 arquivos criados/atualizados
- [ ] Markdown formatado corretamente (sem erros de sintaxe)
- [ ] Links internos funcionando
- [ ] Nomenclatura padronizada (OmniMind, Swarm Intelligence)
- [ ] Nenhum arquivo `.py` foi modificado
- [ ] `.env.example` lista TODAS as env vars do projeto

---

## 🚀 Commit Message

Ao finalizar, commitar com:
```
docs: consolidate documentation and create missing core files

- Add ARCHITECTURE.md (comprehensive system overview)
- Add CONTRIBUTING.md (contributor guidelines)
- Add .env.example (environment variables template)
- Update CURRENT_PHASE.md (Phase 21 status)
- Add GLOSSARY.md (terminology standardization)
- Add ROADMAP.md (consolidated roadmap)
- Fix: Collective Intelligence → Swarm Intelligence throughout docs

Related: Audit Report 2025-11-24 [AC-005, INCON-001, INCON-002, DOC-MISS-001/002/003]
```

---

**BOA SORTE! 🚀**
