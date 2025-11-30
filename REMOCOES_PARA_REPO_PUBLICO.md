# 🗑️ CHECKLIST DE REMOÇÃO - Repo Antigo

**Objetivo:** Limpar omnimind atual para deixar apenas essencial  
**Quando:** Após criar novo repo público  
**Método:** Via dashboard (você gerencia) + este checklist

---

## ✂️ REMOVER DO REPO ANTIGO (src/)

### Fases Experimentais (Não usadas no estudo)

```bash
# Fase 19 - Swarm Intelligence (NÃO USADO)
rm -rf src/swarm/

# Fase 20 - Autopoiesis (NÃO USADO)
rm -rf src/autopoietic/

# Fase 21 - Quantum Consciousness (Experimental, não validado)
rm -rf src/quantum_consciousness/

# Outros módulos off-topic
rm -rf src/cognitive_models/          # Não relevante
rm -rf src/semantic_processing/       # Não relevante
rm -rf src/optimization/              # Não relevante
```

### Manter: src/consciousness/ (CORE - 8 arquivos)
```bash
✅ src/consciousness/__init__.py
✅ src/consciousness/integration_loop.py          (CORRIGIDO)
✅ src/consciousness/shared_workspace.py
✅ src/consciousness/iit_metrics.py
✅ src/consciousness/qualia_module.py
✅ src/consciousness/sensory_input_module.py
✅ src/consciousness/narrative_module.py
✅ src/consciousness/meaning_maker_module.py
✅ src/consciousness/expectation_module.py
```

---

## ✂️ REMOVER DO REPO ANTIGO (scripts/)

### Legacy Scripts (Não usados)
```bash
# Todos MENOS run_ablations_corrected.py
rm scripts/run_ablations_ordered.py           # Versão antiga (tinha bug)
rm scripts/run_*other*.py                     # Benchmarks, etc
rm scripts/generate_*.py                      # Geradores off-topic
rm scripts/monitor_*.py                       # Monitoramento
```

### Manter
```bash
✅ scripts/run_ablations_corrected.py          (ESTUDO)
✅ scripts/__init__.py
```

---

## ✂️ REMOVER DO REPO ANTIGO (web/)

```bash
# Web interface NOT NEEDED for study
rm -rf web/                                   # Frontend + Backend completo
```

---

## ✂️ REMOVER DO REPO ANTIGO (data/)

```bash
# Intermediary data, logs, old results
rm -rf data/test_reports/                     # Logs históricos
rm -rf data/consciousness/workspace/          # Workspace intermediário
rm -rf data/benchmarks/                       # Benchmarks
rm data/*.json                                # Arquivos intermediários
rm data/*.log                                 # Logs
rm data/*.csv                                 # Dados históricos
```

**Manter:** Apenas real_evidence/ (já está correto)

---

## ✂️ REMOVER DO REPO ANTIGO (docs/)

### Manter Papers Atualizados
```bash
✅ docs/papersoficiais/Artigo1_Psicanalise_Computacional_OmniMind.md
✅ docs/papersoficiais/Artigo2_Corpo_Racializado_Consciencia_Integrada.md
```

### Remover Documentação Histórica
```bash
rm -rf docs/reports/                          # Relatórios históricos
rm docs/*.md                                  # README históricos
# Manter apenas os papers atualizados
```

---

## ✂️ REMOVER DO REPO ANTIGO (root/)

### Documentação Histórica de Desenvolvimento
```bash
# Audits, incidents, logs históricos
rm AUDIT_*.md
rm HALLUCINATION_*.md
rm ERROR_HISTORY.md
rm FINAL_STATUS_SUMMARY.md
rm GIT_STATUS_REPORT.md
rm CLEANUP_LOG.md
rm BRANCHES_TO_CLEANUP.md
rm FORCE_PUSH_INSTRUCTIONS.md
rm DEV_STATUS_CONSOLIDATED.md
rm CORREÇÕES_APLICADAS.md
rm ENV_INJECTION_RESOLVED.md
rm DASHBOARD_REPAIR_COMPLETE.md
rm PUBLIC_PRIVATE_INTEGRATION_SUMMARY.md
# [+ 30 outros docs históricos]

Manter apenas:
✅ README.md (atualizado)
✅ CITATION.cff
✅ LICENSE
✅ REPO_PUBLICO_ANALISE.md (este checklist)
✅ EXECUTION_SUMMARY_20251129.md (documentação final)
```

### Scripts Shell Históricos
```bash
rm *.sh                        # Scripts shell (monitor, activate, optimize, etc)
```

### Arquivos Temporários
```bash
rm *.pid                       # Process IDs
rm *.status                    # Status files
rm *.log                       # Logs
rm conftest.py                 # Se for pytest internal
rm pytest.ini                  # Mover para novo repo se relevante
```

---

## ✂️ REMOVER DO REPO ANTIGO (config/)

```bash
# Configs locais - não vão pro repo público
rm -rf config/                 # Hardware profile, MCP, etc - LOCAL

Manter apenas em novo repo:
✅ pyproject.toml              (minimal)
✅ requirements-core.txt       (minimal)
✅ .python-version             (3.12.8)
```

---

## ✂️ REMOVER DO REPO ANTIGO (root files)

### Logs & Intermediários
```bash
rm analyze_log_Testes.md
rm REAL_DATA_NOTICE.md
rm INSTRUCOES_NUMEROS_REAIS.md
rm MANIFESTO_HONESTIDADE.md
rm AUTHOR_STATEMENT.md
rm AUTHOR_STATEMENT_PUBLIC.md
rm AUTHORS.md
rm REAL_TEST_RESULTS_29NOV2025.md
rm PAPERS_STRATEGY_ARXIV_ICLR.md
rm PAPERS_SUBMISSION_PLAN.md
rm ICLR_2026_SUBMISSION_GUIDE.md
rm ARXIV_SUBMISSION_GUIDE.md
rm IBM_*.md
rm CERTIFICACAO_*.md
rm GUIA_*.md
# [+ 40 outros]
```

### Arquivos Gerados/Compilados
```bash
rm coverage.xml
rm *.pyc
rm __pycache__/
rm .egg-info/
rm os                          # Arquivo estranho
rm final_custom_function.txt
rm CODIGO_SIGNATURE_README.txt
rm handle_nonexistent_command.py
rm fix_*.py                    # Scripts de fix
rm generate_interaction_data.sh
```

### Configs Local
```bash
rm Dockerfile.tests            # Só para CI/CD local
rm mypy.ini                    # Será em novo repo minimal
rm pyrightconfig.json          # Será em novo repo minimal
rm omnimind.code-workspace     # Local VSCode
rm PORT_CONFIGURATION.md       # Local config
rm nginx-omnimind-proxy.conf   # Local infra
```

---

## 📊 RESULTADO FINAL

### Antes (Atual)
```
400+ arquivos
500MB+
Phases 1-21 (experimental)
Histórico completo
Web interface
```

### Depois (Novo Repo Público)
```
~25 arquivos
~5MB
Apenas estudo (integration + ablations)
Limpo, focado
Reproduzível em 3 passos
```

---

## ✅ PROCEDIMENTO

### Passo 1: Criar Novo Repo Público
- [ ] Criar repo vazio em GitHub
- [ ] Nome: `omnimind-consciousness-study` ou similar

### Passo 2: Copiar Apenas Essencial
```bash
# Em novo repo, copiar APENAS:
# - src/consciousness/ (8 arquivos)
# - scripts/run_ablations_corrected.py
# - docs/papers/ (2 papers)
# - real_evidence/ (completo)
# - config minimal (pyproject, requirements, .python-version)
# - README.md (novo, limpo)
# - LICENSE
# - CITATION.cff
```

### Passo 3: Limpar Repo Antigo (via Dashboard)
- [ ] Deletar via GitHub UI ou git push force
- [ ] Deixar apenas `main` branch
- [ ] Adicionar `.gitignore` padrão

### Passo 4: Primeiro Commit no Novo Repo
```bash
git add .
git commit -m "Initial commit: OmniMind consciousness framework with ablation study"
git push origin main
```

---

## 🎯 CHECKLIST DE VERIFICAÇÃO

Antes de fazer push para novo repo, verificar:

- [ ] `src/consciousness/` tem 8 arquivos corretos
- [ ] `scripts/run_ablations_corrected.py` existe e funciona
- [ ] `real_evidence/ablations/ablations_corrected_*.json` presente
- [ ] Papers atualizados com métricas reais
- [ ] `README.md` novo e claro
- [ ] `requirements-core.txt` minimal (numpy, scipy, apenas)
- [ ] Nenhum arquivo histórico
- [ ] Nenhum arquivo `.log`
- [ ] Nenhuma pasta `data/` intermediária
- [ ] Sem `web/`, `swarm/`, `quantum_consciousness/`

---

## 📝 Nota

**Repo Antigo (omnimind):** Fica como está (para histórico/desenvolvimento)  
**Repo Novo (omnimind-public):** Limpo, focado, publicável

Quando pronto para ArXiv:
```
"See reproduction in https://github.com/[org]/omnimind-consciousness-study"
```

---

**Ready to clean?** Quer que eu prepare os comandos exatos pra rodar?
