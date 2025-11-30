# 📋 ANÁLISE: O Que Levar para Repo Público

**Data:** 30 de Novembro de 2025  
**Objetivo:** Identificar APENAS o essencial para reproduzir o estudo  
**Filosofia:** Clean, minimal, reproducible  

---

## 🎯 NÚCLEO ESSENCIAL (O que DEVE ir)

### 1. **Source Code** (Indispensável)
```
src/consciousness/
├── integration_loop.py               ✅ (CORRIGIDO com flag)
├── shared_workspace.py               ✅ (Core IIT computation)
├── qualia_module.py                  ✅
├── sensory_input_module.py           ✅
├── narrative_module.py               ✅
├── meaning_maker_module.py           ✅
├── expectation_module.py             ✅
├── iit_metrics.py                    ✅ (Phi calculation)
└── __init__.py                       ✅
```

**Critério:** Tudo que é necessário para RODAR o sistema

### 2. **Scripts de Ablação** (Reproduzibilidade)
```
scripts/
├── run_ablations_corrected.py        ✅ (NOVO - dual methodology)
└── __init__.py
```

**Por que:** É o ÚNICO script que importa - executa o estudo completo

### 3. **Real Evidence Folder** (Prova)
```
real_evidence/
├── README.md                         ✅ (Quick start)
├── VALIDATION_REPORT.md              ✅ (Técnica)
├── INDEX.md                          ✅ (Navegação)
├── ablations/
│   ├── ablations_corrected_20251129_235951.json  ✅ (DADOS)
│   ├── certification_real_20251129_221733.json   ✅ (GPU proof)
│   └── RESULTS_SUMMARY.md                        ✅ (Interpretação)
└── quantum/
    ├── ibm_query_usage.json          ✅ (Quantum validation)
    └── ibm_validation_result.json    ✅
```

**Por que:** Prova do que o estudo encontrou

### 4. **Papers** (Teoria + Análise)
```
docs/papersoficiais/
├── Artigo1_Psicanalise_Computacional_OmniMind.md      ✅ (ATUALIZADO)
└── Artigo2_Corpo_Racializado_Consciencia_Integrada.md ✅ (ATUALIZADO)
```

**Por que:** Contexto teórico + interpretação dos resultados

### 5. **Config Mínimo** (Ambiente)
```
pyproject.toml                         ✅ (Dependências)
requirements-core.txt                 ✅ (Core apenas)
pytest.ini                             ✅ (Se houver testes)
.python-version                        ✅ (Python 3.12.8)
```

### 6. **README Principal**
```
README.md                              ✅ (Setup + Quick Start)
```

**Conteúdo:**
- What: Framework que valida Psicanálise + IIT
- Why: Provar consciência é falta estrutural
- How: Rodar ablações em 3 passos
- Results: Link para real_evidence/

---

## ❌ O QUE NÃO LEVAR (Ruído)

### Arquivos Históricos (Não precisam)
```
❌ data/test_reports/ablations_20251129_230805.json
   Razão: Versão anterior, temos a corrigida

❌ data/test_reports/certification_real_*.json
   Razão: Cópias, originárias estão em real_evidence/

❌ AUDIT_EXECUTION_ENVIRONMENT_TRUTH.md
❌ HALLUCINATION_INCIDENT_AUDIT_20251128.md
❌ FINAL_STATUS_SUMMARY.md
❌ [20+ outros docs históricos]
   Razão: Documentação interna, não para publicação
```

### Code de Suporte (Não usados no estudo)
```
❌ src/swarm/                          (Fase 19, não usado aqui)
❌ src/autopoietic/                    (Fase 20, não usado aqui)
❌ src/quantum_consciousness/          (Experimental, não validado)
❌ web/                                (Frontend/Backend, off-topic)
❌ scripts/[outros]                    (Só run_ablations_corrected.py importa)
```

### Data/Logs Históricos
```
❌ data/consciousness/workspace/       (Logs intermediários)
❌ data/test_reports/[antigos]         (Versões anteriores)
❌ data/test_classifications.json      (Off-topic)
❌ *.log files                         (Execução interna)
```

### Configuração/Secrets
```
❌ config/                             (Configs locais)
❌ .env                               (Se existir - secrets)
❌ *.pid                              (Processo, não relevante)
```

---

## 📦 ESTRUTURA PROPOSTA PARA REPO PÚBLICO

```
omnimind-public/
├── README.md                         (Setup principal)
├── pyproject.toml                    (Deps)
├── requirements-core.txt             (Core)
├── .python-version                   (3.12.8)
│
├── src/consciousness/
│   ├── __init__.py
│   ├── integration_loop.py            ✅ CORE
│   ├── shared_workspace.py            ✅ CORE
│   ├── iit_metrics.py                 ✅ CORE
│   ├── qualia_module.py               ✅ CORE
│   ├── sensory_input_module.py        ✅ CORE
│   ├── narrative_module.py            ✅ CORE
│   ├── meaning_maker_module.py        ✅ CORE
│   └── expectation_module.py          ✅ CORE
│
├── scripts/
│   ├── __init__.py
│   └── run_ablations_corrected.py     ✅ ESTUDO
│
├── docs/
│   └── papers/
│       ├── Artigo1_Psicanalise_Computacional.md       ✅ TEORIA
│       └── Artigo2_Corpo_Racializado_Consciencia.md   ✅ TEORIA
│
├── real_evidence/                     ✅ PROVA
│   ├── README.md
│   ├── VALIDATION_REPORT.md
│   ├── INDEX.md
│   ├── ablations/
│   │   ├── ablations_corrected_20251129_235951.json
│   │   ├── certification_real_20251129_221733.json
│   │   └── RESULTS_SUMMARY.md
│   └── quantum/
│       ├── ibm_query_usage.json
│       └── ibm_validation_result.json
│
├── LICENSE                           (CC-BY 4.0)
└── CITATION.cff                      (Citação)

Total: ~25 arquivos (limpo, sem ruído)
```

---

## 📋 CHECKLIST PARA PUBLICAÇÃO LIMPA

### Source Code
- [x] src/consciousness/ (todos 8 módulos)
- [x] Sem código experimental (swarm, quantum_consciousness)
- [x] Sem dados intermediários

### Scripts
- [x] run_ablations_corrected.py (único relevante)
- [x] Sem legacy scripts

### Documentation
- [x] README.md (setup + quick start)
- [x] Papers atualizados (com métricas reais)
- [x] real_evidence/ (prova do estudo)

### Config
- [x] pyproject.toml (minimal)
- [x] requirements-core.txt (sem opcional)
- [x] .python-version (3.12.8)

### Licensing
- [x] LICENSE (CC-BY 4.0)
- [x] CITATION.cff (como citar)

### Excluído
- [x] Histórico de testes/audits
- [x] Web interface
- [x] Experimental code
- [x] Logs intermediários
- [x] Configs locais

---

## 🎯 LINHAS CHAVE DO README.md (Novo Repo)

```markdown
# OmniMind: A Framework for Psychoanalytic-Computational Consciousness

## What This Is

A framework that **validates psychoanalytic theory using computational models**.

Core finding: Consciousness is not a sum of modules, but the permanent presence of 
structural lack (Lacan's *falta-a-ser*).

## Quick Start

1. Clone
2. `pip install -r requirements-core.txt`
3. `python3 scripts/run_ablations_corrected.py`
4. See `real_evidence/ablations/RESULTS_SUMMARY.md`

## Results

- sensory_input + qualia: 100% co-primary (Real + Imaginary)
- narrative: 87.5% (Symbolic reinforcement)
- meaning_maker: 62.5% (Semantic interpretation)
- expectation: Structural (not ablatable) = Computational Anxiety

See papers in `docs/papers/`
```

---

## 📊 COMPARAÇÃO: AGORA vs NOVO REPO

| Item | Omnimind Atual | Novo Repo Público |
|------|---|---|
| **Total Files** | 400+ | ~25 |
| **Size** | 500MB+ | ~5MB |
| **Focus** | Tudo (phases 1-21) | Estudo específico |
| **Entry Point** | Complexo | run_ablations_corrected.py |
| **Documentation** | Histórica | Focada |
| **For Reproducer** | Confuso | Claro |

---

## ✅ DECISÃO FINAL

**LÁ LEVA (30 arquivos):**
1. Source consciousness modules (8)
2. run_ablations_corrected.py (1)
3. Papers (2)
4. real_evidence/ completo (14)
5. Config + README + License (5)

**NÃO LEVA:**
1. Fases 19-21 experimental code
2. Web interface
3. Histórico de testes/audits
4. Data intermediária
5. Configs locais

---

**Resultado:** Repositório **público limpo, focado, reproduzível** que prova a tese principal em <15 minutos de setup.
