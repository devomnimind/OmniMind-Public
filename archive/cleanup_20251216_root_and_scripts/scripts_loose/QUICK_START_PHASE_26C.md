# 🚀 QUICK START - Phase 26C Integration

**Data**: 5 de Dezembro de 2025
**Status**: Scripts prontos, datasets baixados ✅

---

## ⚡ COMANDOS RÁPIDOS

### 1. Armazenar Papers em Phase 24

```bash
cd /home/fahbrain/projects/omnimind
source .venv/bin/activate
python scripts/load_datasets_for_phi.py --store-papers --limit 1000
```

**O que faz**:
- Carrega papers do dataset `scientific_papers_arxiv`
- Armazena em Phase 24 Semantic Memory (Qdrant)
- Torna papers disponíveis para semantic search

**Tempo estimado**: 10-15 minutos (depende do número de papers)

---

### 2. Construir Knowledge Base de Soluções

```bash
python scripts/build_solutions_knowledge_base.py --from-datasets --limit 100
```

**O que faz**:
- Extrai soluções de papers científicos
- Extrai patterns de QA do QASPER
- Cria `data/known_solutions.json` (usado por Phase 26C Solution Lookup Engine)

**Tempo estimado**: 5-10 minutos

---

### 3. Verificar Resultados

```bash
# Verificar papers armazenados
python scripts/load_datasets_for_phi.py

# Verificar knowledge base criada
ls -lh data/known_solutions.json

# Verificar datasets disponíveis
ls -lh data/datasets/
```

---

## 📋 CHECKLIST

- [ ] Datasets baixados (`data/datasets/` contém scientific_papers, dbpedia, qasper)
- [ ] Papers armazenados em Phase 24 (executar comando 1)
- [ ] Knowledge base de soluções criada (executar comando 2)
- [ ] Validar integração (executar comando 3)

---

## 🔧 TROUBLESHOOTING

### Erro: "No datasets found"

**Solução**: Execute primeiro:
```bash
python scripts/setup_huggingface_datasets.py --tier 1 --limit 1000
```

### Erro: "Qdrant not available"

**Solução**: Inicie Qdrant:
```bash
docker-compose -f deploy/docker-compose.yml up -d qdrant
```

### Erro: "Module not found"

**Solução**: Instale dependências:
```bash
pip install datasets sentence-transformers qdrant-client
```

---

## 📚 PRÓXIMOS PASSOS

Após executar os comandos acima:

1. **Revisar** `docs/PHASE_26C_INTEGRATED_ROADMAP.md`
2. **Implementar** Problem Detection Engine (Fase 4.1)
3. **Implementar** Solution Lookup Engine (Fase 4.2)

---

**Autor**: OmniMind Development
**Status**: Guia Ativo

