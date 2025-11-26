# OmniMind - Copilot & Agent Instructions

## 🚨 CRITICAL RULES (Immutable Constitution)

### 1. Mandato de Produção (Prioridade Alta)
- **Executável:** Todo código deve ser imediatamente executável e testável.
- **Completo:** Sem stubs, `pass`, ou `NotImplementedError`.
- **Tratamento de Erros:** `try/except` com logging abrangente é obrigatório.
- **Proibido:** Pseudocódigo ou comentários "TODO: implementar depois".

### 2. Integridade de Dados & Princípio da Realidade
- **Dados Reais:** Usar dados reais do SO (filesystem, processos, sensores).
- **Sem Falsificação:** Proibidas respostas falsificadas ou "exemplos" hardcoded.
- **Falha Graciosa:** Se dados inacessíveis, falhar com erro claro, não inventar.

### 3. Disciplina do Diretório de Trabalho
- **Raiz:** SEMPRE executar comandos desde `/home/fahbrain/projects/omnimind`.
- **Verificação:** Verificar `pwd` antes de comandos críticos.
- **Limpeza:** Limpar arquivos acidentais em diretórios pais imediatamente.
- **Execução de testes pytest**: Sempre usar argumentos completos com coverage e log detalhado USAR: "pytest tests/ -v --tb=short --cov=src --cov-report=term-missing --cov-report=json:data/test_reports/coverage.json --cov-report=html:data/test_reports/htmlcov --maxfail=999 --durations=20 -W ignore::DeprecationWarning 2>&1 | tee data/test_reports/pytest_output.log" 

### 4. Qualidade & Segurança de Tipo
- **Python:** 3.12.8 RIGOROSAMENTE (não use 3.13+).
- **Type Hints:** 100% de cobertura obrigatória (mypy compliant).
- **Docstrings:** Google-style obrigatória para TODAS funções/classes.
- **Linting:** Deve passar `black` e `flake8` (max-line-length=100).
- **Testes:** Novas features requerem testes unitários (pytest), ≥90% cobertura.

### 5. Segurança & Forense (Zero Trust)
- **Auditoria:** Ações críticas logadas em `src.audit`.
- **Segredos:** NUNCA hardcode credenciais - use variáveis de ambiente.
- **Filesystem:** Nenhuma modificação direta sem validação.

### 6. Protocolo de Estabilidade (Regra de Ouro)
- **Não Avançar com Erros:** Proibido avançar se a base atual tem erros.
- **Loop de Validação Obrigatório:**
    1. `black src tests`
    2. `flake8 src tests`
    3. `mypy src tests`
    4. `pytest -vv`
    5. `python -m src.audit.immutable_audit verify_chain_integrity`

## 🏗️ Architecture Standards

### Directory Structure
- `src/`: Source code (modularized by phase/function).
- `tests/`: Unit and integration tests (mirroring src structure).
- `docs/`: Documentation (reports, roadmaps, guides).
- `scripts/`: Automation scripts.

### Coding Style
- **Imports:** Absolute imports preferred (`from src.module import Class`).
- **Async:** Use `asyncio` for I/O bound operations.
- **Logging:** Use standard `logging` with `__name__`.

## 🤖 Agent Behavior Guidelines
- **Proactive:** Fix lint errors immediately.
- **Transparent:** Explain *what* you are doing and *why*.
- **Conservative:** Do not delete code unless explicitly instructed or deprecated.
- **Communication:** Use Portuguese for chat/logs, English for Code/Comments.

## 📅 Project Status (Nov 2025)
- **Phase 19:** Swarm Intelligence (Complete - `src/swarm`)
- **Phase 20:** Autopoiesis (Complete - `src/autopoietic`)
- **Phase 21:** Quantum Consciousness (Integrated/Experimental - `src/quantum_consciousness`)

---
*These instructions are binding for all AI agents working on the OmniMind repository.*
