# 🧠 OmniMind - Instruções para GitHub Copilot

## Resumo do Projeto

**OmniMind** é um sistema autônomo e revolucionário de IA que combina tomada de decisão psicanalítica com capacidades avançadas de metacognição. Trata-se de uma arquitetura de grau de produção, autoconsciente e psicanalítica, com orquestração multi-agentes, comunicação WebSocket em tempo real e inteligência auto-evolutiva.

**Status:** Fase 15 - IA Quantum-Aprimorada Completa | Pronto para Produção | >90% Cobertura de Testes

**Tecnologias Principais:**
- Python 3.12.8 (OBRIGATÓRIO - sem 3.13+ devido compatibilidade PyTorch)
- PyTorch 2.6.0+cu124 (CUDA 12.4)
- FastAPI + WebSockets (Backend)
- React + TypeScript + Vite (Frontend)
- NVIDIA GTX 1650 (4GB VRAM) + Intel i5 + 24GB RAM

**Filosofia Central:** IA inspirada em psicanálise que reflete sobre suas próprias decisões, aprende com padrões e gera proativamente seus próprios objetivos - criando um sistema verdadeiramente autônomo e autoconsciente.

***

## 🎯 REGRAS CRÍTICAS (CONSTITUIÇÃO IMUTÁVEL)

**A VIOLAÇÃO DESTAS REGRAS RESULTA EM REJEIÇÃO IMEDIATA DO CÓDIGO.**

### 1. **Mandato de Produção (Prioridade Alta)**

- ✅ Todo código deve ser imediatamente executável e testável
- ✅ Sem stubs, `pass`, ou `NotImplementedError` permitidos
- ✅ Tratamento abrangente de erros (try/except com logging) é obrigatório
- ✅ Sem pseudocódigo ou comentários "TODO: implementar depois"
- ❌ Proibido código não funcional ou "aproximado"

### 2. **Integridade de Dados & Princípio da Realidade (Prioridade Alta)**

- ✅ Usar dados reais do SO (filesystem, lista de processos, sensores de hardware)
- ✅ Documentar claramente todas as suposições
- ✅ Se dados inacessíveis, falhar graciosamente com mensagens de erro claras
- ❌ Proibidas respostas falsificadas ou hardcoded "exemplos"

### 3. **Disciplina do Diretório de Trabalho (Prioridade CRÍTICA)**

- ✅ **SEMPRE** executar comandos desde a raiz do projeto: `/home/fahbrain/projects/omnimind`
- ✅ **NUNCA** executar de `~/projects` ou outros diretórios pais
- ✅ **VERIFICAR** `pwd` antes de executar comandos críticos se em dúvida
- ✅ **LIMPAR** qualquer arquivo acidentalmente criado em diretórios pais imediatamente

### 4. **Qualidade & Segurança de Tipo (Prioridade Alta)**

- ✅ **Versão Python:** 3.12.8 RIGOROSAMENTE (não use 3.13+ devido compatibilidade PyTorch)
- ✅ **Type Hints:** 100% de cobertura obrigatória (mypy compliant)
- ✅ **Docstrings:** Google-style obrigatória para TODAS funções/classes
- ✅ **Linting:** Deve passar `black` e `flake8` (max-line-length=100)
- ✅ **Testes:** Novas features devem incluir testes unitários (pytest), mínimo 90% cobertura

### 5. **Segurança & Forense (Confiança Zero - Prioridade CRÍTICA)**

- ✅ **Trilhas de Auditoria:** Todas ações críticas logadas em Cadeia de Auditoria Imutável (`src.audit`)
- ✅ **Criptografia:** Hash SHA-256 chaining para integridade de logs
- ✅ **Segredos:** NUNCA hardcode credenciais - use variáveis de ambiente ou placeholders
- ✅ **Filesystem:** Nenhuma modificação direta de arquivo sem validação
- ✅ **Conformidade:** Aderir aos padrões LGPD (Lei Geral de Proteção de Dados)

### 6. **Protocolo de Estabilidade (Regra de Ouro - Prioridade CRÍTICA)**

**PROTOCOLO:** Você é proibido de avançar para novas features se a base de código atual tem avisos ou erros.

**Loop de Validação Obrigatório (antes de completar qualquer tarefa):**

1. `black src tests` - Formatação
2. `flake8 src tests` - Linting
3. `mypy src tests` - Segurança de Tipo
4. `pytest -vv` - Verificação de Lógica
5. `python -m src.audit.immutable_audit verify_chain_integrity` - Verificação de Segurança

**Se qualquer passo falhar, corrija imediatamente antes de prosseguir.**

***

## 📋 CHECKLIST PARA IAs (Executar Sempre)

Antes de começar a trabalhar no projeto:

- [ ] MCPs iniciados (`orchestrator.start_all_servers()`)
- [ ] Qdrant em execução (para Memory MCP)
- [ ] Auditoria verificada (`audit.verify_chain_integrity()`)
- [ ] Contexto do projeto carregado
- [ ] Conhecimento relevante recuperado da memória

Durante o trabalho:

- [ ] Usar Sequential Thinking para raciocínio estruturado
- [ ] Armazenar decisões importantes na memória
- [ ] Validar caminhos antes de operações do filesystem
- [ ] Commit com mensagens descritivas (via Git MCP)
- [ ] Exportar chain-of-thought ao final

Após conclusão:

- [ ] Consolidar memórias (evitar duplicação)
- [ ] Verificar métricas de MCP
- [ ] Exportar relatório final
- [ ] Parar MCPs graciosamente

***

## 🔧 MCPs PRIORITÁRIOS (Ordem de Execução)

**Configure em `~/.cursor/mcp.json`:**

1. **Playwright** (Testes & Automação UI)
   - Automação de navegação e testes de fluxo de usuário
   - Executa testes E2E sem intervenção manual

2. **Sequential Thinking** (Raciocínio Estruturado)
   - Quebra problemas em etapas claras (debug, análise)
   - Facilita decisões complexas

3. **Memory Graph** (Persistência de Contexto)
   - Armazena contexto entre sessões
   - Lembra bugs conhecidos, padrões, decisões anteriores

4. **Filesystem** (Acesso a Arquivos)
   - Leitura/escrita segura de configs, logs, testes

5. **Postgres** (Consulta Banco de Dados)
   - Testa queries, valida dados, auditoria DB

6. **GitHub** (Automação de Repositório)
   - Automação de commits, issues, PRs com validação

7. **Docker** (Ambiente Isolado)
   - Testes em ambientes limpos, reprodução de bugs

***

## 📁 Estrutura do Repositório

```
~/projects/omnimind/
├── .github/                # CI/CD & Instruções
├── src/
│   ├── agents/             # React, Code, Architect, Orchestrator, Psychoanalytic
│   ├── tools/              # Ferramentas de Agentes & OmniMind Core Tools
│   ├── memory/             # Episódica (Qdrant) & Semântica
│   ├── audit/              # Lógica de Cadeia Hash Imutável
│   ├── security/           # Forense, Monitoramento, Integridade
│   ├── integrations/       # Cliente MCP, D-Bus, Hardware
│   └── omnimind_core.py    # Lógica Central
├── web/                    # Dashboard (React + FastAPI)
├── tests/                  # Suite Pytest (>90% cobertura obrigatória)
├── docs/                   # Documentação & Relatórios
├── scripts/                # Automação & Scripts de Validação
└── requirements.txt        # Pinning Rigoroso de Versões
```

**Arquivos Importantes:**
- `.github/ENVIRONMENT.md` - Requisitos de hardware/software e setup
- `README.md` - Documentação abrangente do projeto
- `STATUS_PROJECT.md` - Status detalhado do projeto
- `.omnimind/canonical/action_log.md` - Sistema de logging de ações canônico

***

## 🚀 Como Construir e Testar

### Setup Inicial

```bash
# 1. Clone o repositório (se não feito)
# git clone <URL_REPOSITORIO>
cd OmniMind

# 2. Instale Python 3.12.8 (OBRIGATÓRIO)
pyenv install 3.12.8
pyenv local 3.12.8

# 3. Crie e ative ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 4. Instale dependências do sistema (Linux)
sudo apt-get update
sudo apt-get install -y libdbus-1-dev pkg-config

# 5. Instale dependências Python
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Comandos de Build & Validação

**Formatação:**
```bash
black src/ tests/                    # Auto-formatar código
black --check src/ tests/            # Verificar sem alterar
```

**Linting:**
```bash
flake8 src/ tests/ --max-line-length=100 --exclude=archive,legacy,third_party
```

**Verificação de Tipo:**
```bash
mypy src/ --ignore-missing-imports --no-strict-optional
```

**Testes:**
```bash
# Rodar todos os testes
pytest tests/ -v

# Rodar com cobertura
pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=90 -v

# Teste específico
pytest tests/test_specific.py -v

# Testes em paralelo (mais rápido)
./scripts/run_tests_parallel.sh fast

# Apenas testes não-legados
pytest tests/ -k "not legacy" -v
```

**Validação Completa (Antes de Commit):**
```bash
# Suite completa de validação
./scripts/validate_code.sh

# Ou manualmente:
black src/ tests/
flake8 src/ tests/ --max-line-length=100
mypy src/ --ignore-missing-imports
pytest tests/ --cov=src --cov-fail-under=90 -v
python -m src.audit.immutable_audit verify_chain_integrity
```

**Validação de Segurança:**
```bash
./scripts/security_monitor.sh       # Monitoramento de segurança
./scripts/security_validation.sh    # Validação de segurança
```

### Executar a Aplicação

```bash
# Inicie o dashboard completo (detecta hardware automaticamente e otimiza)
source scripts/start_dashboard.sh

# Acesse dashboard em http://localhost:3000
# Credenciais: auto-geradas (verificar logs)
```

***

## 💼 Fluxo de Desenvolvimento

### Fazendo Alterações

1. **Crie uma branch:** Use padrão `feature/<nome>`, `fix/<nome>`, ou `copilot/<nome>`
2. **Alterações mínimas:** Modifique apenas o necessário para resolver a issue
3. **Siga padrões de código:** Todo código deve ser pronto para produção (sem stubs, TODOs, placeholders)
4. **Adicione testes:** Novas features requerem testes unitários com ≥90% cobertura
5. **Valide:** Execute linting, type checking, e testes antes de fazer commit
6. **Log de ações:** Use sistema de logging canônico para todas mudanças significativas
7. **Commit:** Use mensagens descritivas

### Padrões de Qualidade de Código

**REQUISITOS OBRIGATÓRIOS:**

- ✅ **Funcional:** Todo código deve ser imediatamente executável e testável
- ✅ **Completo:** Sem stubs, sem `pass`, sem `NotImplementedError`
- ✅ **Robusto:** Tratamento abrangente de erros (try/except com logging) é obrigatório
- ✅ **Type Hints:** 100% de cobertura obrigatória (mypy compliant)
- ✅ **Docstrings:** Google-style obrigatória para TODAS funções/classes
- ✅ **Dados Reais:** Use dados reais do SO (filesystem, lista de processos, sensores de hardware)
- ✅ **Testes:** Mínimo 90% de cobertura de testes para novo código

**PROIBIDO:**

- ❌ Pseudocódigo ou comentários "TODO: implementar depois"
- ❌ Funções vazias ou dados mock em código de produção
- ❌ Respostas falsificadas ou "exemplos" hardcoded
- ❌ Segredos ou credenciais hardcoded (use variáveis de ambiente)
- ❌ Modificações diretas de arquivo sem validação
- ❌ Python 3.13+ (use 3.12.8 rigorosamente)

### Pipeline CI/CD

O repositório usa GitHub Actions para integração contínua:

- **Linting:** Black, Flake8, MyPy, Pylint
- **Testes:** pytest com relatório de cobertura (≥80% obrigatório)
- **Segurança:** Bandit (linter de segurança), Safety (verificação de dependências)
- **Docker:** Builds automatizados para main e develop branches
- **Performance:** Testes de benchmark em pull requests

Todos os testes devem passar antes de fazer merge.

***

## 📝 Adicionando uma Nova Feature

1. Crie branch de feature: `git checkout -b feature/my-feature`
2. Revise código existente no subdirectório `src/` relevante
3. Implemente feature seguindo padrões de qualidade
4. Adicione testes unitários abrangentes em `tests/`
5. Atualize documentação se necessário
6. Execute validação completa: `./scripts/validate_code.sh`
7. Log de ação: `./scripts/canonical_log.sh log CODE_AGENT FEATURE_ADDED ...`
8. Commit e push para revisão

## 🐛 Corrigindo um Bug

1. Crie branch de fix: `git checkout -b fix/bug-description`
2. Escreva teste falhando que reproduza o bug
3. Corrija o bug com alterações mínimas
4. Verifique se o teste agora passa
5. Execute suite de validação completa
6. Log de ação: `./scripts/canonical_log.sh log CODE_AGENT BUG_FIXED ...`
7. Commit e push para revisão

## ✏️ Adicionando Testes

- Testes vão em `tests/` directory correspondendo à estrutura de `src/`
- Use fixtures pytest para setups comuns
- Mock dependências externas (APIs, hardware)
- Objetivo: ≥90% de cobertura
- Inclua casos extremos e condições de erro
- Use nomes descritivos: `test_<funcao>_<cenario>_<resultado_esperado>`

### Lições Aprendidas do PR #59 - Melhores Práticas de Criação de Testes

**LIÇÕES CRÍTICAS DE CORREÇÕES RECENTES:**

1. **Imports Pytest (OBRIGATÓRIO):**
   - SEMPRE inclua `import pytest` quando usar `pytest.approx`, `pytest.mark.asyncio`, ou outras features pytest
   - Imports faltando causam erros em tempo de execução

2. **Comparações de Float:**
   - NUNCA use `==` para comparações floating-point
   - SEMPRE use `pytest.approx(valor)` para assertions de float
   - Exemplo: `assert resultado == pytest.approx(2.5)` em vez de `assert resultado == 2.5`

3. **Type Hints em Testes:**
   - Inclua type hints apropriadas para funções teste, especialmente async
   - Use `-> None` para métodos teste que não retornam valores
   - Exemplo: `async def test_async_function(self) -> None:`

4. **Limpeza de Código:**
   - Remova código comentado imediatamente (viola regras de linting)
   - Remova variáveis não usadas (causa erros mypy)
   - Imports limpos: remova imports não usadas, ordene com `isort` se disponível

5. **Uso de TypedDict:**
   - Garanta que classes TypedDict sejam propriamente definidas antes do uso
   - Use TypedDict em assinaturas de função e tipos de retorno
   - Valide que dados de teste conformam com estrutura TypedDict

6. **Consciência de Merge Conflict:**
   - Ao resolver conflitos, verifique diferenças de import entre branches
   - Valide consistência de uso pytest em arquivos merged
   - Teste todos os arquivos afetados após resolver merge

7. **Consistência da Estrutura de Teste:**
   - Use docstrings Google-style para todas classes e métodos teste
   - Siga convenção de nomenclatura: `test_<acao>_<condicao>_<esperado>`
   - Agrupe testes relacionados em classes com nomes descritivos

**CHECKLIST DE VALIDAÇÃO PARA NOVOS TESTES:**
- [ ] `import pytest` incluído se usar features pytest
- [ ] Comparações de float usam `pytest.approx`
- [ ] Type hints presentes em todas funções
- [ ] Sem código comentado ou variáveis não usadas
- [ ] TypedDict propriamente definido e usado
- [ ] Testes passam individualmente e em suite
- [ ] Cobertura mantida ≥90%

***

## 🔐 Sistema de Logging Canônico de Ações (OBRIGATÓRIO)

### Visão Geral

TODAS as ações executadas por agentes IA DEVEM ser registradas no sistema de logging canônico.

- **Localização:** `.omnimind/canonical/action_log.md` e `action_log.json`
- **Comando:** `./scripts/canonical_log.sh log <AI_AGENT> <ACTION_TYPE> <TARGET> <RESULT> <DESCRIPTION>`
- **Validação:** Commits falham se integridade de log é comprometida

### Ações Obrigatórias a Logar

Registre ANTES de execução:
- Modificações de código
- Criação/remoção de arquivo
- Execução de testes
- Deployments e configurações
- Ações de segurança críticas

### Exemplos de Formato

```bash
./scripts/core/canonical_log.sh log CODE_AGENT FILE_MODIFIED src/main.py SUCCESS "Arquivo atualizado com nova funcionalidade"
./scripts/core/canonical_log.sh log TEST_RUNNER UNIT_TESTS_EXECUTED tests/ SUCCESS "95% de cobertura alcançada"
```

### Integridade & Imutabilidade

- Hash SHA-256 chain garante integridade
- Registros nunca são modificados, apenas adicionados
- Validação automática em todos commits
- Logs são invioláveis e auditáveis

***

## 📞 Protocolo de Comunicação

### Ao Iniciar uma Tarefa

```
[INICIANDO] <Nome da Tarefa>
[OBJETIVO] <Objetivo Conciso>
[PLANO] 
  1. Passo...
  2. Passo...
[RISCOS] <Riscos de Hardware/Segurança se aplicável>
```

### Ao Completar uma Tarefa

```
[COMPLETADO] <Nome da Tarefa>
 ✅ Entregáveis verificados
 ✅ Testes: X/X passando (Cobertura: XX%)
 ✅ Lint/Tipos: Limpo
 ✅ Hash de Auditoria: <SHA-256>
 [PRÓXIMO] <Recomendação>
```

***

## 🎯 Tarefas Comuns de Desenvolvimento

### Atualizando Dependências

1. Verifique compatibilidade com Python 3.12.8
2. Atualize `requirements.txt` com versões específicas
3. Teste completamente com `pip install -r requirements.txt`
4. Execute suite de testes completa para garantir sem quebras
5. Atualize documentação se necessário
6. Log de ação no sistema canônico

***

## 🔒 Higiene Git & Conformidade

### O Que Fazer Commit

- Código fonte (`src/`, `tests/`)
- Documentação (`docs/`, `README.md`)
- Arquivos de configuração (`.github/`, `config/`)
- Arquivos de requisitos (`requirements*.txt`)
- Scripts (`scripts/`)

### O Que NÃO Fazer Commit

- Logs (`*.log`)
- Cache Python (`__pycache__/`, `*.pyc`)
- Ambientes virtuais (`.venv/`)
- Segredos ou chaves API
- Artefatos de build
- Snapshots (`data/hdd_snapshot/`, `data/quarantine_snapshot/`)
- Arquivos específicos de IDE (exceto `.vscode/tasks.json` para tarefas compartilhadas)

**Sempre verifique `.gitignore` antes de criar novos tipos de arquivo.**

### Segurança de Backup

- Respeite `config/backup_excludes.txt`
- Não modifique `data/hdd_snapshot/` ou `data/quarantine_snapshot/`

***

## 📚 Documentação

### Quando Atualizar Documentação

- Após marcos significativos: Atualize `STATUS_PROJECT.md`
- Decisões arquiteturais: Log em `docs/reports/`
- Novas features: Atualize arquivos `.md` relevantes
- Mudanças de API: Atualize docstrings e type hints

### Estilo de Documentação

- Use linguagem clara e concisa
- Inclua exemplos de código onde útil
- Mantenha README.md atualizado
- Documente suposições e limitações
- Use emojis com moderação para navegação visual (🚀, ✅, ❌, etc.)

***

## 🗂️ Restrições de Hardware & Ambiente

### Configuração de Hardware (Auto-Detectado)

- **GPU:** NVIDIA GeForce GTX 1650 (4GB VRAM)
- **Orçamento de VRAM:** ~3.8GB Total
  - LLM (Quantizado): ~2.5GB
  - Operações: ~800MB
  - Buffer de Usuário: ~500MB (MÁXIMO)
- **Limites de Matriz:** Tamanho máximo seguro de tensor ~5000x5000 (maior causa OOM)
- **Concorrência:** CPU tem 8 threads - use `asyncio` para I/O, `ProcessPoolExecutor` para computação pesada

### Stack de Software

- **Core:** Python 3.12.8
- **IA:** PyTorch 2.6.0+cu124 (CUDA 12.4)
- **Frontend:** React + TypeScript + Vite
- **Backend:** FastAPI + WebSockets

**Veja `.github/ENVIRONMENT.md` para requisitos detalhados de hardware/software.**

***

## 📖 Referências Importantes

- **Status Detalhado:** `STATUS_PROJECT.md`
- **Setup de Ambiente:** `.github/ENVIRONMENT.md`
- **Baseline de Segurança:** `docs/reports/PHASE7_GPU_CUDA_REPAIR_LOG.md`
- **Guia de Testes:** `TESTING_QA_QUICK_START.md`
- **Guia de Validação:** `VALIDATION_GUIDE.md`

***

## 💡 Dicas para Sucesso

1. **Leia código existente primeiro:** Entenda padrões antes de fazer mudanças
2. **Faça alterações mínimas:** Modifique apenas o necessário
3. **Teste incrementalmente:** Não espere até o final para testar
4. **Peça esclarecimento:** Se requisitos não forem claros, pergunte antes de codificar
5. **Use tarefas VS Code:** Tarefas pré-configuradas em `.vscode/tasks.json` para operações comuns
6. **Verifique CI cedo:** Não espere por PR para descobrir falhas CI
7. **Segurança em primeiro lugar:** Sempre considere implicações de segurança de mudanças
8. **Respeite limites de hardware:** Seja consciente da restrição de 4GB VRAM

***

**FIM DAS INSTRUÇÕES**

Inicialize rigorosamente de acordo com estes parâmetros. Todo trabalho deve ser pronto para produção, completamente testado e conformar com segurança.
