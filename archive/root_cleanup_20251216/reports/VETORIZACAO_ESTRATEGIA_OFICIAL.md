# 🎯 ESTRATÉGIA OFICIAL DE VETORIZAÇÃO - OmniMind + Ubuntu

**Status:** ✅ OFICIAL E ÚNICO
**Data:** 13 Dezembro 2025
**Modelo:** SentenceTransformer (all-MiniLM-L6-v2) - 384 dims
**DB:** Qdrant

---

## 🎯 O QUE INDEXAR

### 1. AMBIENTE UBUNTU (Memória de Mundo Operacional)

```
/var/log/syslog              → Logs de sistema
/var/log/auth.log            → Eventos de autenticação
/var/log/apt/history.log     → Histórico de pacotes
/var/log/*/                  → Logs de serviços (Docker, Nginx, etc)
journalctl                   → Eventos de systemd
systemctl list-units         → Serviços ativos
dpkg -l                      → Pacotes instalados
/etc/os-release              → Configuração do SO
```

**Função:** Permitir ao sistema entender estado operacional da máquina

**Chunking:** 20-50 linhas por chunk (janelas temporais)

---

### 2. CÓDIGO OMNIMIND (Topologia de Sujeito)

```
src/                         → Código-fonte Python
  ├── consciousness/         → Lógica IIT (Φ, Ψ, σ)
  ├── memory/               → Memória (episódica, narrativa)
  ├── agents/               → Agentes (orquestrador, código)
  ├── integrations/         → Integrações (LLM, Qdrant)
  └── ...

config/                      → Configurações YAML/JSON
  ├── omnimind.yaml
  ├── security.yaml
  └── ...

docs/                        → Documentação Markdown
  ├── README.md
  ├── INSTALLATION.md
  └── *.md
```

**Função:** Permitir recuperação de código e especificações por similaridade

**Chunking:**
- Código: Por função/classe (500 chars máximo)
- Docs: Por seção/header (H1, H2)
- Config: Arquivo completo (YAML/JSON)

---

## 📊 COLLECTIONS QDRANT (4 No Total)

| Collection | Conteúdo | Vectores Esperados | Uso |
|------------|----------|------------------|-----|
| `omnimind_codebase` | Código-fonte Python | 200-400 | Retrieval de código por função |
| `omnimind_docs` | Documentação Markdown | 50-100 | RAG para especificações |
| `omnimind_config` | Configurações YAML/JSON | 20-50 | Estrutura de sistema |
| `omnimind_system_logs` | Logs de /var/log e journald | 100-200 | Context de máquina |

**Todos com 384 dims (SentenceTransformer)**

---

## 🔧 SCRIPT OFICIAL

**Arquivo:** `scripts/vectorize.py`

### Funcionalidades

```bash
# Vetorização completa (Ubuntu + OmniMind)
python scripts/vectorize.py

# Só OmniMind (sem Ubuntu logs)
python scripts/vectorize.py --skip-ubuntu

# Só Ubuntu (sem projeto)
python scripts/vectorize.py --skip-project

# Limpar e recrear do zero
python scripts/vectorize.py --clean
```

### Pipeline

```
1. Verificações iniciais
   ├── Python 3.12+
   ├── SentenceTransformer (384 dims)
   ├── Qdrant (localhost:6333)
   └── Dimensão validada

2. Descoberta de arquivos
   ├── src/*.py (código)
   ├── docs/*.md (documentação)
   ├── config/*.yaml/*.json (configurações)
   └── /var/log/* (logs ubuntu - permissão)

3. Chunking semântico
   ├── Código: Por função/classe
   ├── Docs: Por seção
   ├── Config: Completo
   └── Logs: 20-50 linhas

4. Vetorização
   ├── Encode com SentenceTransformer
   ├── Batch size: 32
   └── Show progress

5. Upload para Qdrant
   ├── Create/delete collections
   ├── Upsert points com metadados
   └── Validar

6. Relatório final
   ├── Total de vetores
   ├── Distribuição por tipo
   └── Próximas etapas
```

---

## 💾 METADADOS ARMAZENADOS

Para cada vetor:

```python
{
    "type": "code|documentation|configuration|system_log",
    "file": "/home/fahbrain/projects/omnimind/src/consciousness/...",
    "text_preview": "Primeiros 100 caracteres...",
    "timestamp": "2025-12-13T10:30:00",

    # Opcional (apenas código/logs)
    "start_line": 42,
    "end_line": 85,
}
```

Permite filtros como:
- Buscar só código de "consciousness"
- Buscar logs entre datas
- Buscar documentação de "memory"

---

## 🚀 EXECUÇÃO

### Pré-requisitos

```bash
# Qdrant deve estar rodando
docker-compose -f deploy/docker-compose.yml up -d qdrant

# Ativar venv
source .venv/bin/activate

# Dependências já devem estar instaladas
pip list | grep sentence-transformers
pip list | grep qdrant-client
```

### Executar

```bash
cd /home/fahbrain/projects/omnimind
python scripts/vectorize.py
```

### Tempo Estimado

| Fase | Tempo |
|------|-------|
| Descoberta de arquivos | 5-10s |
| Vetorização (embeddings) | 5-8 min |
| Upload para Qdrant | 1-2 min |
| Validação | 10-20s |
| **TOTAL** | **~7-10 min** |

---

## 📊 RESULTADO ESPERADO

```
✅ omnimind_codebase: 250 vetores
✅ omnimind_docs: 75 vetores
✅ omnimind_config: 35 vetores
✅ omnimind_system_logs: 150 vetores (se houver permissão)

TOTAL: ~510 vetores com 384 dims
```

Todos em Qdrant, prontos para:
- Semantic search
- RAG retrieval
- Code understanding
- Context injection

---

## 🔄 FLUXO DE USO

1. **Executor de Vetorização** (Este script)
   ```bash
   python scripts/vectorize.py
   ```

2. **Consultas em Código**
   ```python
   from qdrant_client import QdrantClient

   client = QdrantClient("http://localhost:6333")
   results = client.search(
       collection_name="omnimind_codebase",
       query_vector=embedding,
       limit=5
   )
   ```

3. **Uso em RAG**
   ```python
   # Recuperar contexto do banco para gerar resposta
   context = retrieve_from_qdrant(query)
   response = llm(query, context)
   ```

---

## 🏗️ ARQUITETURA

```
┌─────────────────────────────────────┐
│  Arquivos do Projeto + Sistema      │
│  (código, docs, config, logs)       │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│  Chunking Semântico                 │
│  (por função, seção, eventos)       │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│  SentenceTransformer (384 dims)     │
│  (encode todos os chunks)           │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│  Qdrant (4 Collections)             │
│  • codebase (250 vetores)           │
│  • docs (75 vetores)                │
│  • config (35 vetores)              │
│  • system_logs (150 vetores)        │
└─────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│  Recuperação Semântica (RAG)        │
│  • Search by similarity             │
│  • Filter by type                   │
│  • Context injection para LLM       │
└─────────────────────────────────────┘
```

---

## ✅ VERIFICAÇÃO

Após execução, verificar:

```bash
# Conectar ao Qdrant
python << 'EOF'
from qdrant_client import QdrantClient

client = QdrantClient("http://localhost:6333")
collections = client.get_collections()

for col in collections.collections:
    info = client.get_collection(col.name)
    print(f"{col.name}: {info.points_count} vetores")
EOF

# Esperado:
# omnimind_codebase: 250 vetores
# omnimind_docs: 75 vetores
# omnimind_config: 35 vetores
# omnimind_system_logs: 150 vetores
```

---

## 🚫 NÃO FAZER

- ❌ Não execute scripts em `scripts/archive_deprecated/` (obsoletos)
- ❌ Não mude dimensões para 768
- ❌ Não crie novos scripts (use `scripts/vectorize.py`)
- ❌ Não deleta dados manualmente de Qdrant

---

## 📝 STATUS

| Item | Status |
|------|--------|
| Script oficial criado | ✅ |
| Estratégia definida | ✅ |
| Documentação | ✅ |
| Pronto para executar | ✅ |
| Scripts duplicados arquivados | ✅ |

**Próximo passo:** Executar `python scripts/vectorize.py`

---

**Fonte de Verdade:** Este documento + `scripts/vectorize.py`
