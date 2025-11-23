# 🧠 OmniMind - GitHub Copilot Instructions

## Project Overview

**OmniMind** is a revolutionary autonomous AI system that combines psychoanalytic decision-making with advanced metacognition capabilities. This is a production-grade, self-aware, psychoanalytic architecture that features multi-agent orchestration, real-time WebSocket communication, and self-evolving intelligence.

**Status:** Phase 16 Consolidação Complete | Production Ready | 98.94% Testes Passando

**Tecnologias Principais:**
- Python 3.12.8 (RIGOROSO - sem 3.13+ por compatibilidade PyTorch)
- PyTorch 2.9.1+cu128 (CUDA 12.8)
- FastAPI + WebSockets (Backend)
- React + TypeScript + Vite (Frontend)
- NVIDIA GTX 1650 (4GB VRAM) ✅ GPU FUNCIONANDO | Intel i5 + 24GB RAM

**Core Philosophy:** Psychoanalytically-inspired AI that reflects on its own decisions, learns from patterns, and proactively generates its own objectives - creating a truly autonomous and self-aware system.

## Estrutura do Repositório

```
~/projects/omnimind/
├── .github/                # CI/CD & Instruções
├── src/
│   ├── agents/             # React, Code, Architect, Orchestrator, Psychoanalytic
│   ├── tools/              # Agent Tools & OmniMind Core Tools
│   ├── memory/             # Episodic (Qdrant) & Semantic
│   ├── audit/              # Immutable Hash Chain Logic
│   ├── security/           # Forensics, Monitoring, Integrity
│   ├── integrations/       # MCP Client, D-Bus, Hardware
│   └── omnimind_core.py    # Core Logic
├── web/                    # Dashboard (React + FastAPI)
├── tests/                  # Pytest Suite (≥90% cobertura)
├── docs/                   # Documentação organizada por propósito
│   ├── .project/          # Documentos canônicos (9 arquivos)
│   ├── guides/            # Guias de setup e configuração (11)
│   ├── architecture/       # Design e integração (8)
│   ├── testing/           # QA e validação (5)
│   ├── production/        # Deployment (3)
│   └── research/, api/, hardware/, roadmaps/
├── scripts/               # Automação e validação (6 categorias)
│   ├── core/             # Scripts essenciais (4)
│   ├── production/       # Deployment (5)
│   ├── dev/              # Desenvolvimento e testes (5)
│   ├── security/         # Segurança (2)
│   ├── utils/            # Utilities (5)
│   └── archive/          # Obsoletos/desenvolvimento (9)
├── data/
│   ├── reports/          # Relatórios JSON (coverage, testes)
│   ├── consciousness/
│   └── ethics/
├── config/               # Configurações da aplicação
├── deploy/               # Docker, Kubernetes, CI/CD
└── requirements.txt      # Dependências com versões fixas
```

**Arquivos Importantes:**
- `.github/ENVIRONMENT.md` - Requisitos de hardware/software
- `README.md` - Documentação abrangente do projeto
- `PHASE16_FINAL_SUMMARY.md` - Resumo da consolidação Phase 16
- `docs/.project/INDEX.md` - Hub de navegação da documentação

### ✅ CHECKLIST ANTES DE INICIAR

Antes de começar a trabalhar no projeto:

- [ ] Verificar Python 3.12.8 (`python --version`)
- [ ] Ativar venv (`source .venv/bin/activate`)
- [ ] GPU verificada (`torch.cuda.is_available()`)
- [ ] Contexto do projeto carregado
- [ ] Conhecimento relevante da memória recuperado

Durante o trabalho:

- [ ] Usar pensamento sequencial para raciocínio estruturado
- [ ] Armazenar decisões importantes na memória
- [ ] Validar caminhos antes de operações filesystem
- [ ] Usar git hooks inteligentes (detecção de tipo de mudança)
- [ ] Exportar chain-of-thought ao final

Ao completar:

- [ ] Consolidar memórias (evitar duplicação)
- [ ] Verificar métricas do projeto
- [ ] Exportar relatório final
- [ ] Garantir todos testes passando

## Como Compilar e Testar

### Setup Inicial

```bash
# 1. Ir para o diretório do projeto
cd /home/fahbrain/projects/omnimind

# 2. Garantir Python 3.12.8 (OBRIGATÓRIO)
python --version  # Deve ser 3.12.8

# 3. Ativar venv se não ativado
source .venv/bin/activate

# 4. Instalar dependências
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Comandos de Validação

**Formatação:**
```bash
black src/ tests/
```

**Linting:**
```bash
flake8 src/ tests/ --max-line-length=100
```

**Type Checking:**
```bash
mypy src/ --ignore-missing-imports --no-strict-optional
```

**Testes:**
```bash
# Todos os testes
pytest tests/ -v

# Com cobertura
pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=90 -v

# Teste específico
pytest tests/test_specific.py -v

# Modo rápido (paralelo)
export OMNIMIND_DEV_MODE=true && pytest tests/ -k "not legacy" -v
```

**Validação Completa (antes de commit):**
```bash
./scripts/core/validate_code.sh
```

**Segurança:**
```bash
./scripts/security/security_validation.sh
```

## Workflow de Desenvolvimento

### Fazendo Alterações

1. **Criar branch:** Use padrão `feature/<nome>`, `fix/<nome>`, ou `copilot/<nome>`
2. **Fazer alterações mínimas:** Modifique apenas o necessário
3. **Seguir padrões de código:** Todo código deve ser production-ready (sem stubs, TODOs ou placeholders)
4. **Adicionar testes:** Novos recursos requerem testes unitários com ≥90% cobertura
5. **Validar:** Executar linting, type checking e testes antes de fazer commit
6. **Registrar ações:** Usar sistema de logging canônico para todas as mudanças significativas
7. **Fazer commit:** Usar mensagens de commit descritivas

### Padrões de Qualidade de Código

**REQUISITOS OBRIGATÓRIOS:**

- ✅ **Funcional:** Todo código deve ser imediatamente executável e testável
- ✅ **Completo:** Sem stubs, sem `pass`, sem `NotImplementedError`
- ✅ **Robusto:** Tratamento abrangente de erros (try/except com logging) é obrigatório
- ✅ **Type Hints:** Cobertura 100% necessária (compatível com mypy)
- ✅ **Docstrings:** Estilo Google obrigatório para TODAS as funções/classes
- ✅ **Dados Reais:** Usar dados reais do SO (filesystem, lista de processos, sensores de hardware)
- ✅ **Testes:** Mínimo 90% cobertura de testes para novo código

**PROIBIDO:**

- ❌ Pseudocódigo ou comentários "TODO: implementar depois"
- ❌ Funções vazias ou dados mock em código production
- ❌ Saídas falsificadas ou respostas hardcoded "exemplo"
- ❌ Secrets ou credenciais hardcoded (usar variáveis de ambiente)
- ❌ Modificações de arquivo diretas sem validação
- ❌ Python 3.13+ (usar 3.12.8 estritamente)

### Pipeline CI/CD

O repositório usa GitHub Actions para integração contínua:

- **Linting:** Black, Flake8, MyPy, Pylint
- **Testes:** pytest com relatório de cobertura (≥80% obrigatório)
- **Segurança:** Bandit (linter de segurança), Safety (verificação de dependências)
- **Docker:** Builds automatizados para branches main e develop
- **Performance:** Testes de benchmark em pull requests

Todos os checks devem passar antes do merge.

## 🚫 REGRAS CRÍTICAS (A CONSTITUIÇÃO IMUTÁVEL)

**VIOLAÇÃO DESTAS REGRAS RESULTA EM REJEIÇÃO IMEDIATA DO CÓDIGO.**

### 1. Mandato Production-Ready

- Todo código deve ser imediatamente executável e testável
- Sem stubs, `pass`, ou `NotImplementedError` permitidos
- Tratamento abrangente de erros (try/except com logging) é obrigatório
- Sem pseudocódigo ou comentários "TODO: implementar depois"

### 2. Integridade de Dados & Princípio da Realidade

- Use dados reais do SO (filesystem, lista de processos, sensores de hardware)
- Documente todas as suposições claramente
- Se dados não estiverem acessíveis, falhe gracefully com mensagens de erro claras
- Sem saídas falsificadas ou respostas "exemplo" hardcoded

### 3. Padrões de Qualidade & Segurança de Tipos

- **Versão Python:** 3.12.8 ESTRITA (não use 3.13+ por compatibilidade PyTorch)
- **Type Hints:** Cobertura 100% obrigatória (compatível com mypy)
- **Docstrings:** Estilo Google obrigatório para TODAS as funções/classes
- **Linting:** Deve passar `black` e `flake8` (max-line-length=100)
- **Testes:** Novos recursos devem incluir testes unitários (pytest), mínimo 90% cobertura

### 4. Segurança & Forensics (Zero Trust)

- **Trilhas de Auditoria:** Todas as ações críticas registradas em Cadeia de Auditoria Imutável (`src.audit`)
- **Criptografia:** Encadeamento de hash SHA-256 para integridade de log
- **Secrets:** NUNCA hardcode credenciais - usar variáveis de ambiente ou placeholders
- **Filesystem:** Sem modificações diretas de arquivo sem validação
- **Compliance:** Aderir aos padrões LGPD (Lei Geral de Proteção de Dados)

### 5. O Protocolo de Estabilidade (Regra de Ouro)

**PROTOCOLO:** Você está proibido de avançar para novas funcionalidades se a base de código atual tem qualquer aviso ou erro.

**Loop de Validação Obrigatório (antes de completar qualquer tarefa):**

1. `black src tests` - Formatação
2. `flake8 src tests` - Linting
3. `mypy src tests` - Segurança de Tipos
4. `pytest -vv` - Verificação de Lógica
5. `python -m src.audit.immutable_audit verify_chain_integrity` - Verificação de Segurança

**Se qualquer passo falhar, corrija imediatamente antes de prosseguir.**

### 6. Disciplina de Diretório de Trabalho (CRÍTICO)

- **SEMPRE** execute comandos da raiz do projeto: `/home/fahbrain/projects/omnimind`
- **NUNCA** execute comandos de `~/projects` ou outros diretórios parentes.
- **VERIFIQUE** `pwd` antes de executar comandos críticos se tiver dúvida.
- **LIMPE** qualquer arquivo criado acidentalmente em diretórios parentes imediatamente.

## Restrições de Hardware & Ambiente

### Configuração de Hardware (Auto-Detectada)

- **GPU:** NVIDIA GeForce GTX 1650 (4GB VRAM)
- **Orçamento de VRAM:** ~3.8GB Total
  - LLM (Quantizado): ~2.5GB
  - Operações: ~800MB
  - Buffer do Usuário: ~500MB (MÁXIMO)
- **Limites de Matriz:** Tamanho máximo seguro de tensor ~5000x5000 (maior causa OOM)
- **Concorrência:** CPU tem 8 threads - use `asyncio` para I/O, `ProcessPoolExecutor` para cálculos pesados

### Stack de Software

- **Core:** Python 3.12.8
- **IA:** PyTorch 2.9.1+cu128 (CUDA 12.8)
- **Frontend:** React + TypeScript + Vite
- **Backend:** FastAPI + WebSockets

**Veja `.github/ENVIRONMENT.md` para requisitos detalhados de hardware/software.**

## Sistema Canônico de Logging de Ações (OBRIGATÓRIO)

### Visão Geral

TODAS as ações realizadas por agentes IA DEVEM ser registradas no sistema de logging canônico.

- **Localização:** `.omnimind/canonical/action_log.md` e `action_log.json`
- **Comando:** `./scripts/canonical_log.sh log <AI_AGENT> <ACTION_TYPE> <TARGET> <RESULT> <DESCRIPTION>`
- **Validação:** Commits falham se a integridade do log for comprometida

### Ações Obrigatórias para Registrar

Registre ANTES da execução:
- Modificações de código
- Criação/remoção de arquivo
- Execução de testes
- Deployments e configurações
- Ações de segurança críticas

### Exemplos de Formato

```bash
./scripts/canonical_log.sh log CODE_AGENT FILE_MODIFIED src/main.py SUCCESS "Arquivo atualizado com nova funcionalidade"
./scripts/canonical_log.sh log TEST_RUNNER UNIT_TESTS_EXECUTED tests/ SUCCESS "Cobertura de 95% alcançada"
```

### Integridade & Imutabilidade

- Cadeia de hash SHA-256 garante integridade
- Registros nunca são modificados, apenas anexados
- Validação automática em todos os commits
- Logs são invioláveis e auditáveis

## Tarefas Comuns de Desenvolvimento

### Adicionando uma Nova Funcionalidade

1. Criar branch de feature: `git checkout -b feature/minha-feature`
2. Revisar estrutura de código existente no subdiretório `src/` relevante
3. Implementar funcionalidade seguindo padrões de qualidade de código
4. Adicionar testes unitários abrangentes em `tests/`
5. Atualizar documentação se necessário
6. Executar validação completa: `./scripts/validate_code.sh`
7. Registrar ação: `./scripts/canonical_log.sh log CODE_AGENT FEATURE_ADDED ...`
8. Fazer commit e push para revisão

### Corrigindo um Bug

1. Criar branch de fix: `git checkout -b fix/descricao-bug`
2. Escrever um teste que falha e reproduz o bug
3. Corrigir o bug com alterações mínimas
4. Garantir que o teste agora passa
5. Executar suite de validação completa
6. Registrar ação: `./scripts/canonical_log.sh log CODE_AGENT BUG_FIXED ...`
7. Fazer commit e push para revisão

### Adicionando Testes

- Testes ficam em `tests/` directory correspondendo à estrutura `src/`
- Use fixtures pytest para setups comuns
- Mock dependências externas (APIs, hardware)
- Objetivo: ≥90% cobertura
- Incluir casos extremos e condições de erro
- Usar nomes descritivos: `test_<funcao>_<cenario>_<resultado_esperado>`

#### Lições Aprendidas do PR #59 - Melhores Práticas de Criação de Testes

**LIÇÕES CRÍTICAS DE CORREÇÕES RECENTES:**

1. **Imports do Pytest (OBRIGATÓRIO):**
   - SEMPRE inclua `import pytest` quando usar `pytest.approx`, `pytest.mark.asyncio`, ou outras features do pytest
   - Imports faltando causam erros em runtime durante execução de testes

2. **Comparações de Floats:**
   - NUNCA use `==` para comparações de ponto flutuante
   - SEMPRE use `pytest.approx(value)` para assertions de float
   - Exemplo: `assert result == pytest.approx(2.5)` ao invés de `assert result == 2.5`

3. **Type Hints em Testes:**
   - Inclua type hints apropriados para funções de teste, especialmente funções async
   - Use `-> None` para métodos de teste que não retornam valores
   - Exemplo: `async def test_async_function(self) -> None:`

4. **Limpeza de Código:**
   - Remova código comentado imediatamente (viola regras de linting)
   - Remova variáveis não usadas (causa erros mypy)
   - Limpe imports: remova imports não usados, ordene com `isort` se disponível

5. **Uso de TypedDict:**
   - Garanta que classes TypedDict estejam propriamente definidas antes do uso
   - Use TypedDict em assinaturas de funções e tipos de retorno
   - Valide que dados de teste conformam à estrutura TypedDict

6. **Consciência de Merge Conflicts:**
   - Quando resolver conflitos, verifique diferenças de import entre branches
   - Verifique consistência de uso de pytest em arquivos merged
   - Teste todos os arquivos afetados após resolução de merge

7. **Consistência de Estrutura de Testes:**
   - Use docstrings estilo Google para todas as classes e métodos de teste
   - Siga convenções de nomes: `test_<acao>_<condicao>_<esperado>`
   - Agrupe testes relacionados em classes com nomes descritivos

**CHECKLIST DE VALIDAÇÃO PARA NOVOS TESTES:**
- [ ] `import pytest` incluído se usar features do pytest
- [ ] Comparações de floats usam `pytest.approx`
- [ ] Type hints presentes em todas as funções
- [ ] Sem código comentado ou variáveis não usadas
- [ ] TypedDict propriamente definido e usado
- [ ] Testes passam individualmente e em suite
- [ ] Cobertura mantida ≥90%

### Atualizando Dependências

1. Verificar compatibilidade com Python 3.12.8
2. Atualizar `requirements.txt` com versões específicas
3. Testar completamente com `pip install -r requirements.txt`
4. Executar suite de testes completa para garantir ausência de quebras
5. Atualizar documentação se necessário
6. Registrar ação no sistema canônico

## Higiene Git & Conformidade

### O Que Fazer Commit

- Código fonte (`src/`, `tests/`)
- Documentação (`docs/`, `README.md`)
- Arquivos de configuração (`.github/`, `config/`)
- Arquivos de requisitos (`requirements*.txt`)
- Scripts (`scripts/`)

### O Que NÃO Fazer Commit

- Logs (`*.log`)
- Cache do Python (`__pycache__/`, `*.pyc`)
- Ambientes virtuais (`.venv/`)
- Secrets ou API keys
- Artefatos de build
- Snapshots (`data/hdd_snapshot/`, `data/quarantine_snapshot/`)
- Arquivos específicos de IDE (exceto `.vscode/tasks.json` para tarefas compartilhadas)

**Sempre verifique `.gitignore` antes de criar novos tipos de arquivo.**

### Segurança de Backup

- Respeite `config/backup_excludes.txt`
- Não modifique `data/hdd_snapshot/` ou `data/quarantine_snapshot/`

## Documentação

### Quando Atualizar a Documentação

- Após marcos significativos: Atualizar `STATUS_PROJECT.md`
- Decisões arquiteturais: Registrar em `docs/reports/`
- Novas funcionalidades: Atualizar arquivos `.md` relevantes
- Mudanças de API: Atualizar docstrings e type hints

### Estilo de Documentação

- Use linguagem clara e concisa
- Inclua exemplos de código onde útil
- Mantenha README.md atualizado
- Documente suposições e limitações
- Use emojis com moderação para navegação visual (🚀, ✅, ❌, etc.)

## Roadmap Ativo

### Foco Atual: Endurecimento de Produção & Segurança

**Fase 16: Consolidação Completa (ATUAL)**
- GPU CUDA: Permanentemente reparada (5.15x speedup) ✅
- Documentação: Reorganizada (242 → 58 arquivos) ✅
- Root & Scripts: Consolidados (34 → 10 files, 28 → 6 categories) ✅
- Testes: 2,370 total, 2,344 passando (98.94%) ✅
- Instruções: Atualizadas para refletir Phase 16 (EM PROGRESSO)

**Fase 17: Security & Psychoanalysis (PRÓXIMA)**
- SecurityAgent: Monitoramento de 4 camadas (Process, Network, File, Log)
- Forensics: `security_monitor.py` e `integrity_validator.py`
- PsychoanalyticAnalyst: Frameworks Freudianos/Lacanianos
- Workflow: Code → Review → Fix → Document (RLAIF)

**Fase 18: Deployment & Interfaces (FUTURO)**
- MCP Implementation: Model Context Protocol para I/O de arquivo
- D-Bus: Controle de nível de sistema (Media, Power, Network)
- Web UI: Dashboard em tempo real com WebSocket
- Systemd: `omnimind.service` para persistência em boot

## Protocolo de Comunicação

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
 ✅ Lint/Types: Clean
 ✅ Hash de Auditoria: <SHA-256>
 [PRÓXIMO] <Recomendação>
```

## Dicas para Sucesso

1. **Leia o código existente primeiro:** Entenda os padrões antes de fazer alterações
2. **Faça alterações mínimas:** Modifique apenas o que é necessário
3. **Teste incrementalmente:** Não espere até o final para testar
4. **Peça esclarecimento:** Se os requisitos não estiverem claros, pergunte antes de codificar
5. **Use tasks do VS Code:** Tasks pré-configuradas em `.vscode/tasks.json` para operações comuns
6. **Verifique CI cedo:** Não espere pelo PR para descobrir falhas de CI
7. **Segurança em primeiro lugar:** Sempre considere implicações de segurança de mudanças
8. **Respeite limites de hardware:** Cuidado com restrição de 4GB VRAM

## Referências Importantes

- **Status Detalhado:** `STATUS_PROJECT.md`
- **Setup de Ambiente:** `.github/ENVIRONMENT.md`
- **Baseline de Segurança:** `docs/reports/PHASE7_GPU_CUDA_REPAIR_LOG.md`
- **Guia de Testes:** `TESTING_QA_QUICK_START.md`
- **Guia de Validação:** `VALIDATION_GUIDE.md`

---

**FIM DAS INSTRUÇÕES**

Inicialize estritamente de acordo com estes parâmetros. Todo trabalho deve ser production-ready, completamente testado e seguro em conformidade.
