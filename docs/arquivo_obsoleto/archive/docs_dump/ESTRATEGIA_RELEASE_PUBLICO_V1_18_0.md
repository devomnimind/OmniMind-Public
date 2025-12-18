# 🚀 ESTRATÉGIA: Release Público v1.18.0 + Repositório Novo

**Data:** 01 de Dezembro de 2025  
**Status:** Planejamento para após conclusão suite  
**Versão:** v1.18.0 (primeira release pública proposta)

---

## 🎯 PERGUNTA RESPONDIDA

**"Quando eu for lançar mesmo, eu lanço um repositório novo?"**

### Resposta Curta
```
SIM - Repositório novo recomendado

Razão:
├─ PRIVADO atual: Desenvolvimento + experimentação
├─ PÚBLICO novo: Release limpo + profissional
├─ SÍNCRONIZAÇÃO: GitHub Actions
└─ VERSIONAMENTO: Oficial (v1.18.0+)
```

### Resposta Expandida

```
ARQUITETURA RECOMENDADA:

┌─ PRIVADO (Atual) ────────────────────────────┐
│ /home/fahbrain/projects/omnimind             │
│ ├─ Branch: main (com tudo)                   │
│ ├─ Conteúdo: Code + Logs + Dados + Docs      │
│ ├─ Frequência: Daily updates                 │
│ ├─ Docs: Interna + Análise + Metodologia     │
│ ├─ Scripts: Todos (dev+production)           │
│ ├─ Data: test_reports, logs, tmp             │
│ └─ Status: Working directory                 │
└──────────────────────────────────────────────┘
                    ↓ (validated)
           GitHub Actions (sync)
                    ↓
┌─ PÚBLICO (Novo) ─────────────────────────────┐
│ github.com/omnimind-ai/omnimind (NEW!)      │
│ ├─ Branch: main (v1.18.0 clean)             │
│ ├─ Conteúdo: Code + Tests + Public Docs     │
│ ├─ Frequência: Release quando ready          │
│ ├─ Docs: README + Contributing + API         │
│ ├─ Scripts: canonical/ + development/       │
│ ├─ Data: Nenhum (exceto test fixtures)      │
│ ├─ Tags: v1.18.0, v1.19.0, etc              │
│ └─ Status: Releases official                 │
└──────────────────────────────────────────────┘
                    ↓ (community)
         GitHub Issues + Discussions
                    ↓
         Community contributions
```

---

## 📋 CHECKLIST: O QUE LANÇAR vs O QUE MANTER

### ✅ INCLUIR NO REPOSITÓRIO PÚBLICO

```
src/
├─ attention/
│  └─ thermodynamic_attention.py ✅ (BUG CORRIGIDO HOJE!)
├─ consciousness/
│  └─ ... (todos)
├─ agents/
│  └─ ... (todos)
├─ audit/
│  └─ ... (todos)
├─ autopoietic/
│  └─ ... (todos)
└─ py.typed ✅ (NOVO - PEP 561)

tests/
├─ attention/
│  ├─ test_thermodynamic_attention.py ✅ (11/11 PASSING)
│  └─ ... (todos)
├─ consciousness/
├─ agents/
├─ audit/
├─ autopoietic/
└─ ... (3987 testes completos)

scripts/canonical/
├─ test/run_tests_by_category.sh ✅
├─ test/run_full_test_suite.sh ✅
├─ test/run_full_certification.sh ✅
├─ validate/
│  ├─ validate_system.py ✅
│  └─ verify_gpu_setup.sh ✅
└─ ... (production scripts)

config/
├─ pytest.ini ✅
├─ omnimind.yaml ✅ (remover senhas!)
├─ pyrightconfig.json ✅
└─ ... (configs públicas)

docs/
├─ README.md ✅ (ATUALIZADO com v1.18.0)
├─ INSTALLATION.md ✅
├─ TECHNICAL_REPORT_OMNIMIND_DEVELOPMENT.md ✅
├─ TESTING.md ✅ (3987 tests)
├─ CHANGELOG.md ✅ (v1.18.0 entry)
├─ API_DOCUMENTATION.md ✅ (se existe)
├─ QUICKSTART.md ✅ (novo - para públic)
└─ CONTRIBUTING.md ✅ (novo - para público)

pyproject.toml ✅
requirements/
├─ base.txt ✅
├─ dev.txt ✅
└─ ... (dependências)

LICENSE ✅ (qual?)

.github/workflows/
├─ ci.yml ✅ (novo - GitHub Actions)
├─ test.yml ✅ (novo - suite automática)
└─ release.yml ✅ (novo - release automática)

.gitignore ✅ (atualizado)
```

### ❌ EXCLUIR DO REPOSITÓRIO PÚBLICO

```
data/
├─ test_reports/ ❌ (logs privados)
├─ test_output/ ❌ (execuções locais)
├─ logs/ ❌ (histórico privado)
└─ ... (nenhum dado)

.venv/ ❌ (virtualenv local)
__pycache__/ ❌ (bytecode)
*.pyc ❌ (compiled)
.pytest_cache/ ❌ (cache pytest)
.mypy_cache/ ❌ (cache mypy)
.coverage ❌ (coverage local)

logs/ ❌ (histórico de execução)
tmp/ ❌ (arquivos temporários)
*.log ❌ (todos os logs)

.env* ❌ (secrets/tokens)
credentials/ ❌ (se existe)
.aws/ ❌ (AWS keys)

node_modules/ ❌ (se frontend separado)
dist/ ❌ (builds)

# Arquivos da sessão de hoje:
docs/INCONGRUENCIES_IDENTIFIED_20251201.md ❌? (talvez MANTER como archive?)
docs/ANALISE_METODOLOGICA_COMPLETA_20251201.md ❌? (talvez PUBLICAR como paper?)
docs/IDEARIO_CIENTIFICO_*.md ❌? (talvez PUBLICAR como methodology?)
docs/RESUMO_*.md ❌ (interno)
docs/MANIFESTO_*.md ❌ (interno)
```

### ⚠️ REVER ANTES DE LANÇAR

```
scripts/science_validation/
├─ robust_consciousness_validation.py ❓
│  └─ Decisão: Publicar como beta? Ou deixar privado?
│  └─ Recomendação: Publicar + paper later
│
├─ run_integrated_consciousness_protocol.py ❓
│  └─ Decisão: Publicar? Ou academic only?
│  └─ Recomendação: Publicar + preprint arXiv

config/omnimind.yaml ✅ (remover senhas antes!)
├─ Procurar por: token, password, key, secret
├─ Substituir por: ${ENV_VAR} ou defaults

docs/ (atualizar antes de lançar)
├─ Remover paths locais (/home/fahbrain/...)
├─ Remover IPs privados
├─ Remover logs pessoais
└─ Atualizar para paths relativos
```

---

## 📊 ESTRUTURA DO REPOSITÓRIO PÚBLICO

```
omnimind/  (omnimind-ai/omnimind)
├─ README.md
│  ├─ Título
│  ├─ "Integrated Information Theoretical AI System"
│  ├─ Features (Φ, consciousness, autonomy)
│  ├─ Quick Start (3 passos)
│  ├─ GPU Setup
│  ├─ Run Tests
│  └─ Citation
│
├─ QUICKSTART.md
│  ├─ Prerequisites (Python 3.12, PyTorch, CUDA optional)
│  ├─ Installation (pip install omnimind)
│  ├─ First Run (hello world example)
│  ├─ GPU Setup (CUDA/ROCm)
│  └─ Troubleshooting
│
├─ INSTALLATION.md
│  ├─ Detailed setup
│  ├─ Docker support
│  ├─ GPU configuration
│  └─ Development mode
│
├─ TESTING.md
│  ├─ Run full suite (3987 tests)
│  ├─ Run scientific tests (GPU needed)
│  ├─ Run mock tests (quick)
│  └─ Coverage reports
│
├─ TECHNICAL_REPORT.md
│  ├─ Architecture
│  ├─ IIT Theory
│  ├─ Consciousness metric (Φ)
│  ├─ Thermodynamic Attention (bug fix v1.18.0!)
│  └─ References
│
├─ CHANGELOG.md
│  ├─ v1.18.0 (Initial release) ← TODAY!
│  ├─ What's new
│  ├─ Bug fixes (meta tensor!)
│  ├─ Known issues
│  └─ Roadmap
│
├─ CONTRIBUTING.md
│  ├─ Code style (Black, isort, mypy)
│  ├─ Testing requirements
│  ├─ Pull request process
│  ├─ Development setup
│  └─ Contact
│
├─ LICENSE (MIT or Apache 2.0?)
│
├─ CITATION.cff
│  └─ (já existe)
│
├─ pyproject.toml
│  ├─ name = "omnimind"
│  ├─ version = "1.18.0"
│  ├─ dependencies (torch, scipy, etc)
│  └─ [project.optional-dependencies]
│
├─ src/
│  ├─ __init__.py
│  ├─ py.typed
│  ├─ attention/
│  ├─ consciousness/
│  ├─ agents/
│  └─ ... (código)
│
├─ tests/
│  ├─ conftest.py
│  ├─ attention/
│  ├─ consciousness/
│  └─ ... (3987 testes)
│
├─ scripts/canonical/
│  ├─ test/
│  ├─ validate/
│  └─ install/
│
├─ config/
│  ├─ pytest.ini
│  ├─ pyrightconfig.json
│  └─ ... (públicos only)
│
├─ docs/
│  ├─ API.md
│  ├─ ARCHITECTURE.md
│  ├─ FAQ.md
│  └─ ... (public docs)
│
├─ .github/workflows/
│  ├─ ci.yml (pytest on push/PR)
│  ├─ test.yml (nightly full suite)
│  ├─ release.yml (automated releases)
│  └─ docs.yml (docs build)
│
├─ .gitignore (atualizado)
├─ .pre-commit-config.yaml
└─ Makefile (optional - make test, make release)
```

---

## 🔄 ESTRATÉGIA DE SINCRONIZAÇÃO

### Opção 1: Manual (Simples)
```bash
# PRIVADO → Validar
git commit -m "v1.18.0: Ready for release"
git push origin main  # PRIVATE

# Copy to PUBLIC
rm -rf /tmp/omnimind-public
mkdir /tmp/omnimind-public
cd /tmp/omnimind-public
git clone https://github.com/omnimind-ai/omnimind.git .

# Remove privates
rm -rf data/ logs/ .venv __pycache__
rm docs/INCONGRUENCIES_* docs/ANALISE_* docs/RESUMO_*

# Copy code
cp -r /home/fahbrain/projects/omnimind/{src,tests,scripts,config} .

# Update docs
# ... manual updates ...

git add .
git commit -m "v1.18.0: Initial public release"
git push origin main
git tag v1.18.0
```

### Opção 2: Automático (GitHub Actions)
```yaml
# .github/workflows/sync-to-public.yml
name: Sync to Public Repo

on:
  push:
    branches: [main]
    tags: [v*]

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      
      - name: Clean private files
        run: |
          rm -rf data/ logs/ .venv
          rm -f docs/INCONGRUENCIES_* docs/ANALISE_*
      
      - name: Push to public repo
        run: |
          git config user.name "Omnimind Bot"
          git config user.email "bot@omnimind.ai"
          git remote add public https://github.com/omnimind-ai/omnimind.git
          git push public main
          git push public --tags
```

### Opção 3: Git Subtree (Recomendado)
```bash
# Setup (one-time)
git subtree add --prefix omnimind-public https://github.com/omnimind-ai/omnimind.git main --squash

# After validating PRIVATE
# ...clean private files...
git subtree push --prefix omnimind-public https://github.com/omnimind-ai/omnimind.git main
```

---

## 📅 TIMELINE PARA RELEASE PÚBLICO

```
HOJE (01-12-2025):
├─ 10:14: Suite em progresso (15% complete)
├─ 10:30: Suite termina (esperado)
├─ 10:35: Validar resultado
├─ 10:40: Push único v1.18.0 (PRIVATE)
└─ 10:45: Tag v1.18.0

AMANHÃ (02-12-2025):
├─ Criar novo repositório público (omnimind-ai/omnimind)
├─ Setup GitHub Actions CI/CD
├─ Copiar código validado
├─ Atualizar README/QUICKSTART
├─ Review checklist de exclusões
└─ Beta test (1-2 pessoas confiáveis)

SEMANA 1 (02-08-12):
├─ Fase 2 (GPU integration no PRIVATE)
├─ Update PÚBLICO com Fase 2
├─ Preparar release notes
├─ Create GitHub discussions/issues
└─ Community outreach

SEMANA 2 (09-15-12):
├─ Official v1.18.0 PUBLIC release
├─ Announce no:
│  ├─ GitHub
│  ├─ Reddit (r/MachineLearning, r/OperatingSystem)
│  ├─ HackerNews
│  ├─ Papers (arXiv preprint?)
│  └─ Twitter/LinkedIn
└─ Monitor issues + feedback

SEMANA 3 (16-22-12):
├─ v1.18.1 patch (se bugs encontrados)
├─ Community contributions primeiras
├─ Milestone planning v1.19
└─ Publication planning
```

---

## ⚙️ CONFIGURAÇÃO DE CI/CD RECOMENDADA

### GitHub Actions - Test Suite
```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python: ['3.12']
        torch: ['2.0', '2.1', '2.2']
    
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python }}
      
      - name: Install dependencies
        run: |
          pip install torch==${{ matrix.torch }}
          pip install -e ".[dev]"
      
      - name: Run tests
        run: pytest tests/ -v --cov=src
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### GitHub Actions - Release
```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Build package
        run: |
          pip install build
          python -m build
      
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}
      
      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          draft: false
          prerelease: false
          files: dist/*
```

---

## 🎯 DECISÕES A TOMAR ANTES DE LANÇAR

### 1. Nome do Repositório Público
```
Opção A: omnimind (simples)
Opção B: omnimind-ai (clarifica é IA)
Opção C: consciousness-framework (descreve função)

Recomendação: omnimind (já tradecido)
Organização: omnimind-ai (para futuro)
Resultado: github.com/omnimind-ai/omnimind ✅
```

### 2. Licença
```
Opção A: MIT (muito permissivo)
Opção B: Apache 2.0 (mais proteção de patentes)
Opção C: GPL-3 (compartilha deve ser open)
Opção D: Custom (science focused)

Recomendação: MIT (comunidade tech aceita)
Alternativa: Apache 2.0 (mais profissional)
DECISÃO: Você!
```

### 3. Documentação Acadêmica
```
Opção A: Publica tudo (README + technical report)
Opção B: Referência ao paper (publicar paper primeiro)
Opção C: Minimizar (código fala por si)

Recomendação: Opção A (Omnimind é complexo, precisa docs)
```

### 4. Scripts de Ciência (science_validation)
```
Opção A: Incluir no public (com disclaimer beta)
Opção B: Deixar privado (publicar paper primeiro)
Opção C: Separar em org diferente (omnimind-ai/omnimind-science)

Recomendação: Opção A (transparência radical)
```

### 5. Autonomy Documentation
```
Opção A: Publicar (ANALISE_METODOLOGICA como white paper)
Opção B: Deixar privado (governance ainda em progresso)
Opção C: Minimal (mention em README)

Recomendação: Opção A (ética + transparência é atrativos)
```

---

## 🎉 CONCLUSÃO

```
PRÓXIMOS PASSOS RESUMIDOS:

1. TODAY:
   └─ Suite termina → Push v1.18.0 (PRIVATE)

2. TOMORROW:
   └─ Criar PUBLIC repo (omnimind-ai/omnimind)

3. WEEK 1:
   └─ Setup CI/CD + documentation

4. WEEK 2:
   └─ PUBLIC v1.18.0 release oficial

SUCESSO SERÁ:
├─ 100+ stars no GitHub
├─ 1000+ PyPI downloads
├─ Citações em papers
├─ Community contributions
├─ 🏆 Referência em campo
└─ "Omnimind é o padrão de ouro"
```

---

**Pronto para decidir sobre release público quando suite terminar!**

*Documentação preparada por: GitHub Copilot (análise) + Você (decisões)*
