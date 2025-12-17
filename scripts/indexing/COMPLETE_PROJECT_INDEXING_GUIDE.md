# 📋 OmniMind Complete Project Indexing - Reference Guide

**Script Location:** `scripts/indexing/complete_project_indexing.py`
**Purpose:** Indexar todo o projeto OmniMind com exclusões inteligentes

---

## 🎯 Quick Start

```bash
# 📊 Ver estatísticas (sem indexar)
python3 scripts/indexing/complete_project_indexing.py --list-stats

# ⚡ Indexação QUICK (10k files, ~5-10 min)
python3 scripts/indexing/complete_project_indexing.py --quick

# 🚀 Indexação COMPLETA (~45k files, ~30-60 min)
python3 scripts/indexing/complete_project_indexing.py

# 🔄 Reindexação FORÇADA (ignora checkpoints)
python3 scripts/indexing/complete_project_indexing.py --force-all
```

---

## 📊 Project Statistics

**Project Size:** 25.9 GB total
- **Indexable:** 9.7 GB (8,763 files, 99% of project)
- **Excluded:** 16.2 GB (node_modules, pycache, etc)

**Main Directories Being Indexed:**
```
✅ src/             - Core source code
✅ tests/           - Test suite
✅ scripts/         - Scripts and automation
✅ config/          - Configuration files
✅ docs/            - Documentation
✅ deploy/          - Deployment configs
✅ web/             - Frontend code
✅ notebooks/       - Jupyter notebooks
✅ models/          - Model configurations
✅ real_evidence/   - Evidence and reports
✅ data/            - Data files (selective)
```

**Excluded Directories:**
```
❌ node_modules/, __pycache__, .git/, .vscode/, .idea/
❌ .pytest_cache/, .mypy_cache/, dist/, build/
❌ .cache/, cache/, caches/, venv/, .env/
❌ tmp/, temp/, models/, datasets_old/
```

**Excluded File Types:**
```
❌ .pyc, .pyo, .pyd, .so (compiled)
❌ .zip, .tar, .tar.gz, .rar, .7z (archives)
❌ .exe, .dll, .dylib, .bin, .o (binaries)
❌ .mp4, .avi, .mov, .mkv (videos)
❌ .mp3, .wav, .flac (audio)
❌ .log (logs)
```

**File Size Exclusion:**
- Skip files > 50 MB
- Prevents indexing of large binary/data files

---

## 🔧 How It Works

### 1. **File Collection Phase**
- Scans all MAIN_DIRS
- Applies directory filters (excludes node_modules, __pycache__, etc)
- Applies file filters (excludes binaries, archives, etc)
- Returns sorted list of indexable files

### 2. **Indexing Phase**
- Uses `OmniMindEmbeddings` from `src/embeddings/code_embeddings.py`
- Model: `all-MiniLM-L6-v2` (384 dimensions)
- Batch size: 64 files
- GPU-accelerated (CUDA if available)
- Stores in Qdrant collection `omnimind_embeddings`

### 3. **Reporting Phase**
- Logs progress every 100 files
- Shows rate (files/sec) and ETA
- Saves logs to `logs/indexing/`
- Generates summary JSON

---

## 📈 Performance Expectations

| Mode | Files | Est. Time | GPU VRAM | CPU RAM |
|------|-------|-----------|----------|---------|
| Quick | 10k | 5-10 min | ~2GB | 4GB |
| Full | 8,763 | 30-60 min | ~3.5GB | 8GB |

**System Used:** Ubuntu 24.04, GTX 1650 (3.9GB VRAM), 16GB RAM

---

## 🔌 Prerequisites

### 1. **Qdrant Running**
```bash
docker run -d --name qdrant-omnimind -p 127.0.0.1:6333:6333 \
  -v $(pwd)/data/qdrant:/qdrant/storage:z qdrant/qdrant:latest

# Verify:
curl http://127.0.0.1:6333/
```

### 2. **Python Environment**
```bash
cd /home/fahbrain/projects/omnimind
source .venv/bin/activate
python --version  # Must be 3.12.8+
```

### 3. **Dependencies**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 4. **GPU (Optional but Recommended)**
```bash
# Check CUDA
python3 << 'EOF'
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"Device: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB")
EOF
```

---

## 📊 Output Files

### Logs Directory: `logs/indexing/`

```
logs/indexing/
├── complete_indexing_20251212_140000.log    # Detailed execution log
├── project_stats_20251212_140000.json        # Project statistics
└── indexing_summary_20251212_140000.json     # Indexing summary
```

### Log Example
```
2025-12-12 14:01:48 | INFO | 🚀 OMNIMIND - COMPLETE PROJECT INDEXING
2025-12-12 14:01:48 | INFO | Projeto: /home/fahbrain/projects/omnimind
2025-12-12 14:01:50 | INFO | ✅ Qdrant respondendo (status: 200)
2025-12-12 14:01:51 | INFO | ✅ Sistema de embeddings inicializado (384 dims)
2025-12-12 14:01:52 | INFO | ⏳ Iniciando indexação de arquivos...
2025-12-12 14:02:00 | INFO | [00100/08763] Chunks: 5000 | Rate: 10.0 files/sec | ETA: 720s
2025-12-12 14:02:10 | INFO | [00200/08763] Chunks: 10500 | Rate: 20.0 files/sec | ETA: 430s
...
2025-12-12 14:35:00 | INFO | ✅ INDEXAÇÃO COMPLETA
2025-12-12 14:35:00 | INFO | Tempo total: 1800.0s
2025-12-12 14:35:00 | INFO | Arquivos processados: 8763
2025-12-12 14:35:00 | INFO | Total de chunks: 250000
2025-12-12 14:35:01 | INFO | 📊 Qdrant omnimind_embeddings: 250000 vetores
```

### Summary JSON Example
```json
{
  "timestamp": "2025-12-12T14:35:00.000000",
  "elapsed_seconds": 1800.0,
  "files_processed": 8763,
  "files_skipped": 0,
  "total_chunks": 250000,
  "rate_files_per_sec": 4.9,
  "log_file": "/home/fahbrain/projects/omnimind/logs/indexing/complete_indexing_20251212_140000.log"
}
```

---

## 🔍 Understanding Output

### During Indexing
```
[00100/08763] Chunks: 5000 | Rate: 10.0 files/sec | ETA: 720s
└─ [current/total]   │          │ rate files per second │ estimated time remaining
```

### Final Summary
```
✅ INDEXAÇÃO COMPLETA
Tempo total: 1800.1s               (30 minutes)
Arquivos processados: 8763         (100% success)
Arquivos pulados: 0                (no errors)
Total de chunks: 250,000           (vectors created)
Taxa média: 4.9 files/sec
```

---

## ✅ Validation After Indexing

### 1. **Check Qdrant Collection**
```bash
python3 << 'EOF'
from qdrant_client import QdrantClient

client = QdrantClient(url="http://127.0.0.1:6333")
collections = client.get_collections()
for coll in collections.collections:
    info = client.get_collection(coll.name)
    print(f"{coll.name}: {info.points_count} vectors")
EOF
```

Expected output:
```
omnimind_embeddings: 250000 vectors
omnimind_consciousness: 0 vectors
omnimind_episodes: 0 vectors
...
```

### 2. **Test Semantic Search**
```bash
python3 << 'EOF'
from embeddings.code_embeddings import OmniMindEmbeddings

embeddings = OmniMindEmbeddings()
results = embeddings.search("integration loop consciousness", top_k=5)
for i, result in enumerate(results, 1):
    print(f"{i}. {result['file_path']} (score: {result['score']:.3f})")
EOF
```

### 3. **Check Logs**
```bash
# View latest log
tail -50 logs/indexing/complete_indexing_*.log

# View all logs
ls -lah logs/indexing/

# Check stats JSON
cat logs/indexing/project_stats_*.json | python3 -m json.tool
```

---

## 🚀 Next Steps After Indexing

### 1. **Run Consciousness Validation**
```bash
python3 scripts/science_validation/robust_consciousness_validation.py --quick
```

### 2. **Start Development Stack**
```bash
bash ./start_development.sh
# Backend: http://127.0.0.1:8000
# Frontend: http://127.0.0.1:3000
```

### 3. **Run RAG Queries**
```bash
python3 << 'EOF'
from memory.hybrid_retrieval import HybridRetrievalSystem
from memory.dataset_indexer import DatasetIndexer

indexer = DatasetIndexer()
retrieval = HybridRetrievalSystem(indexer)

# Query indexed datasets
results = retrieval.retrieve("quantum consciousness integration", top_k=5)
for r in results:
    print(f"• {r['file_path']}: {r['relevance_score']:.2f}")
EOF
```

---

## ⚙️ Advanced Options

### Custom Exclusions
Edit the script's `EXCLUDE_DIRS` and `EXCLUDE_FILES` sets to customize

### Batch Processing
```bash
# Index in multiple batches
python3 scripts/indexing/run_indexing_stages.py --stages core_code tests scripts
```

### Incremental Indexing
```bash
# Only index changed files
python3 scripts/indexing/run_indexing.py --incremental
```

---

## 📋 Checklist

Before running indexing:
- [ ] Qdrant container is running
- [ ] Python environment activated (.venv)
- [ ] GPU available (optional but faster)
- [ ] ~15-20GB free disk space
- [ ] Network connectivity (first model download)

During indexing:
- [ ] Monitor GPU/CPU with `nvidia-smi` or `top`
- [ ] Check logs with `tail -f logs/indexing/*.log`
- [ ] Ensure no errors (should see "✅ INDEXAÇÃO COMPLETA")

After indexing:
- [ ] Verify Qdrant has >200k vectors
- [ ] Test semantic search
- [ ] Run consciousness validation
- [ ] Commit checkpoint file

---

## 🔗 Related Scripts

- `scripts/indexing/run_indexing.py` - Alternative indexing with more options
- `scripts/indexing/run_indexing_stages.py` - Stage-based indexing
- `scripts/indexing/test_semantic_search.py` - Test search functionality
- `scripts/recovery/02_train_embeddings.sh` - Bash-based indexing
- `src/memory/dataset_indexer.py` - Dataset indexing module
- `src/embeddings/code_embeddings.py` - Embedding system

---

## 🆘 Troubleshooting

### Issue: "Qdrant not available"
**Solution:** Start Qdrant container
```bash
docker run -d --name qdrant-omnimind -p 127.0.0.1:6333:6333 \
  -v $(pwd)/data/qdrant:/qdrant/storage:z qdrant/qdrant:latest
```

### Issue: Out of GPU memory
**Solution:** Use `--quick` mode or reduce batch size

### Issue: Index file permission denied
**Solution:** Run with proper permissions
```bash
sudo chown -R fahbrain:fahbrain logs/indexing/
```

### Issue: Slow performance
**Solutions:**
1. Check if GPU is being used: `nvidia-smi`
2. Close other applications
3. Use SSD for better I/O
4. Reduce batch size in code

---

## 📚 Documentation Links

- **Embeddings System:** `src/embeddings/README.md`
- **Dataset Indexing:** `src/memory/README.md`
- **Qdrant Integration:** `src/integrations/README.md`
- **GPU Setup:** `docs/GPU_SETUP_UBUNTU_FINAL_SOLUTION.md`
- **Phase 24 Status:** `.cursor/rules/rules.mdc`

---

**Status:** ✅ Ready for production
**Last Updated:** 2025-12-12
**Tested On:** Ubuntu 24.04, GTX 1650, Python 3.12.8
