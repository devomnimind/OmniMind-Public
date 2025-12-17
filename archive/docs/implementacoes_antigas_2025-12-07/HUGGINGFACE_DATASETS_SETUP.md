# 📚 HuggingFace Datasets Setup - OmniMind

**Data**: 5 de Dezembro de 2025
**Status**: ✅ Scripts Criados e Integrados
**Integração**: Phase 24 Semantic Memory

---

## 📋 Visão Geral

Configuração de datasets do HuggingFace para OmniMind, integrados com Phase 24 Semantic Memory.

**TIER 1 (Essential)**:
1. `armanc/scientific_papers` (ArXiv) - 12 GB
2. `CleverThis/dbpedia-ontology` - 0.8 GB
3. `allenai/qasper` - Small
4. `armanc/pubmed-rct20k` - PubMed RCT
5. `CleverThis/gene-ontology` - Gene Ontology (requer login)

**TIER 2 (Phase 26 Expansion)**:
6. `OSS-forge/HumanVsAICode` - Human vs AI code comparison
7. `TuringEnterprises/Turing-Open-Reasoning` - Open reasoning dataset
8. `openbmb/InfLLM-V2-data-5B` - Large-scale instruction data (5B items, ⚠️ use --limit!)

**Total TIER 1**: ~15-20 GB
**Total TIER 2**: Variable (InfLLM é muito grande, use --limit para testes)

---

## 🔐 Configuração de Credenciais

### Verificar Credenciais Existentes

O projeto já tem suporte para HuggingFace via:

1. **Environment Variables**:
   - `HF_TOKEN` (preferido)
   - `HUGGING_FACE_HUB_TOKEN` (alternativo)

2. **Arquivo de Token**:
   - `~/.huggingface/token`

3. **Configuração em YAML**:
   - `config/external_ai_providers.yaml` (já configurado)

### Como Configurar

```bash
# Opção 1: Via .env
echo "HF_TOKEN=your_token_here" >> .env

# Opção 2: Via huggingface-cli
huggingface-cli login

# Opção 3: Criar arquivo manualmente
mkdir -p ~/.huggingface
echo "your_token_here" > ~/.huggingface/token
```

### Verificar Credenciais

```bash
python scripts/setup_huggingface_datasets.py --check-only
```

---

## 🚀 Setup Rápido

### 1. Download dos Datasets

```bash
# Download TIER 1 (essential)
python scripts/setup_huggingface_datasets.py --tier 1 --limit 10000

# Ou download completo (demora mais)
python scripts/setup_huggingface_datasets.py --tier 1
```

**Tempo estimado**: 30-60 minutos (depende da conexão)

### 2. Carregar Datasets

```bash
# Carregar todos os datasets
python scripts/load_datasets_for_phi.py

# Carregar e armazenar papers em Phase 24
python scripts/load_datasets_for_phi.py --store-papers --limit 1000
```

---

## 📊 Estrutura de Dados

Após o setup, a estrutura será:

```
data/datasets/
├── scientific_papers_arxiv/     (12 GB)
│   └── [HuggingFace dataset format]
├── dbpedia_ontology/              (0.8 GB)
│   └── [HuggingFace dataset format]
└── qasper_qa/                    (small)
    └── [HuggingFace dataset format]
```

---

## 🔗 Integração com Phase 24

### Armazenamento Automático

Os papers podem ser automaticamente armazenados na Phase 24 Semantic Memory:

```bash
# Download e armazenar em Phase 24
python scripts/setup_huggingface_datasets.py --tier 1 --limit 10000
python scripts/load_datasets_for_phi.py --store-papers --limit 1000
```

### Busca Semântica

Após armazenar, os papers ficam disponíveis via semantic search:

```python
from memory.semantic_memory_layer import get_semantic_memory

semantic = get_semantic_memory()
results = semantic.retrieve_similar(
    "consciousness integrated information phi",
    top_k=10
)
```

---

## 📈 Datasets Disponíveis

### 1. Scientific Papers (ArXiv)

**Dataset**: `armanc/scientific_papers`
**Split**: `arxiv`
**Size**: 203,037 papers (completo) ou subset configurável
**Features**: `article`, `abstract`, `section_names`

**Uso**:
```python
from datasets import load_from_disk

papers = load_from_disk("data/datasets/scientific_papers_arxiv")
for paper in papers:
    print(paper['article']['title'])
```

### 2. DBpedia Ontology

**Dataset**: `CleverThis/dbpedia-ontology`
**Type**: RDF triples
**Size**: 40M triples, 9.5M entities
**Format**: `(subject, predicate, object)`

**Uso**:
```python
from datasets import load_from_disk

dbpedia = load_from_disk("data/datasets/dbpedia_ontology")
for row in dbpedia['data']:
    print(f"{row['subject']} → {row['predicate']} → {row['object']}")
```

### 3. QASPER (QA)

**Dataset**: `allenai/qasper`
**Type**: Q&A pairs
**Size**: 5,049 questions, 1,585 papers
**Format**: Questions with evidence-based answers

**Uso**:
```python
from datasets import load_from_disk

qasper = load_from_disk("data/datasets/qasper_qa")
for item in qasper['train']:
    print(f"Q: {item['question']}")
    print(f"A: {item['answer']}")
```

### 4. PubMed RCT20K

**Dataset**: `armanc/pubmed-rct20k`
**Type**: Research papers (PubMed)
**Size**: 20K papers
**Format**: Structured research papers

**Uso**:
```python
from datasets import load_from_disk

pubmed = load_from_disk("data/datasets/pubmed_rct20k")
for paper in pubmed['train']:
    print(paper['title'])
```

### 5. Gene Ontology

**Dataset**: `CleverThis/gene-ontology`
**Type**: Ontology (structured knowledge)
**Size**: Variable
**Format**: Gene ontology terms and relationships
**⚠️ Requer login**: `huggingface-cli login`

**Uso**:
```python
from datasets import load_from_disk

gene_ontology = load_from_disk("data/datasets/gene_ontology")
for entry in gene_ontology['data']:
    print(entry)
```

---

## 🎯 Estratégia Recomendada

### Fase 1: Setup Básico (AGORA)

```bash
# 1. Verificar credenciais
python scripts/setup_huggingface_datasets.py --check-only

# 2. Download subset (rápido para testar)
python scripts/setup_huggingface_datasets.py --tier 1 --limit 1000

# 3. Carregar e testar
python scripts/load_datasets_for_phi.py --store-papers --limit 100
```

### Fase 2: Setup Completo (Próxima Semana)

```bash
# Download completo
python scripts/setup_huggingface_datasets.py --tier 1

# Armazenar em Phase 24
python scripts/load_datasets_for_phi.py --store-papers --limit 10000
```

### Fase 3: TIER 2 (Phase 26 Expansion)

```bash
# Download TIER 2 datasets (com limite para testes)
python scripts/setup_huggingface_datasets.py --tier 2 --limit 10000

# Ou download completo (InfLLM é 5B items, demora muito!)
python scripts/setup_huggingface_datasets.py --tier 2
```

**TIER 2 Datasets**:
- `OSS-forge/HumanVsAICode`: Comparação código humano vs AI
- `TuringEnterprises/Turing-Open-Reasoning`: Dataset de raciocínio aberto
- `openbmb/InfLLM-V2-data-5B`: 5 bilhões de instruções (⚠️ use --limit!)

---

## 🔧 Troubleshooting

### Erro: "No HF_TOKEN found"

**Solução**: Configure token conforme seção "Configuração de Credenciais"

### Erro: "Token invalid or expired"

**Solução**:
1. Verifique se o token está correto
2. Gere novo token em https://huggingface.co/settings/tokens
3. Atualize `.env` ou `~/.huggingface/token`

### Erro: "Out of disk space"

**Solução**:
- Use `--limit` para baixar subset menor
- Limpe datasets antigos: `rm -rf data/datasets/*`

### Erro: "Rate limit exceeded"

**Solução**:
- Configure token (sem token há rate limits)
- Aguarde alguns minutos e tente novamente

---

## 📚 Referências

- **HuggingFace Datasets**: https://huggingface.co/datasets
- **Phase 24 Plan**: `docs/PHASE_24_25_IMPLEMENTATION_PLAN.md`
- **Semantic Awareness**: `docs/SEMANTIC_AWARENESS_INTEGRATION.md`
- **Memory README**: `src/memory/README.md`

---

## ✅ Checklist

- [ ] Credenciais HuggingFace configuradas
- [ ] Datasets TIER 1 baixados
- [ ] Datasets carregados e testados
- [ ] Papers armazenados em Phase 24 (opcional)
- [ ] Semantic search funcionando

---

**Autor**: Fabrício da Silva + assistência de IA (Copilot GitHub/Cursor/Gemini/Perplexity)
**License**: MIT

