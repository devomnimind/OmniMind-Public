# Free Service Alternatives for OmniMind

**Last Updated:** November 19, 2025  
**Purpose:** Document free and local-first alternatives to paid cloud services  
**Alignment:** Local-first principle from project rules

---

## Overview

OmniMind follows a **local-first** architecture, meaning:
1. All core functionality works without internet connection
2. External services are optional enhancements
3. Free alternatives are preferred over paid services
4. Data stays on your machine by default

---

## Service Comparison Matrix

### Vector Database

| Service | Type | Cost | Pros | Cons | Recommended |
|---------|------|------|------|------|-------------|
| **ChromaDB** | Local | Free | No server needed, easy setup | Limited scalability | ✅ **Yes (default)** |
| **Qdrant (local)** | Local | Free | Better performance | Requires server setup | ⚠️ Advanced use |
| **Qdrant Cloud** | Cloud | Paid | Managed, scalable | Costs $$$, data leaves machine | ❌ No |
| **Pinecone** | Cloud | Paid | Fast, reliable | Costs $$$, vendor lock-in | ❌ No |
| **Weaviate** | Local/Cloud | Free/Paid | Flexible | Complex setup | ⚠️ Alternative |

**Default Choice:** ChromaDB (local, zero configuration)

**Configuration:**
```json
{
  "vector_db": "chromadb",
  "chromadb_path": "data/chromadb"
}
```

**Migration from Qdrant:**
```python
# Old (Qdrant server required)
from qdrant_client import QdrantClient
client = QdrantClient(host="localhost", port=6333)

# New (ChromaDB, no server)
import chromadb
client = chromadb.PersistentClient(path="data/chromadb")
```

---

### Cache/Message Queue

| Service | Type | Cost | Pros | Cons | Recommended |
|---------|------|------|------|------|-------------|
| **fakeredis** | In-memory | Free | Zero setup, perfect for tests | Data lost on restart | ✅ **Yes (dev/test)** |
| **Redis (local)** | Local | Free | Production-ready, persistent | Requires server | ✅ **Yes (prod)** |
| **Redis Cloud** | Cloud | Paid | Managed | Costs $$$, latency | ❌ No |
| **Memcached** | Local | Free | Fast | No persistence | ⚠️ Alternative |

**Default Choice:** 
- Development/Testing: fakeredis
- Production: Local Redis server

**Configuration:**
```json
{
  "cache_backend": "fakeredis"  // or "redis"
}
```

**Installation (local Redis):**
```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# macOS
brew install redis
brew services start redis

# Verify
redis-cli ping  # Should return "PONG"
```

---

### Database

| Service | Type | Cost | Pros | Cons | Recommended |
|---------|------|------|------|------|-------------|
| **SQLite** | File-based | Free | Zero setup, portable | Single writer | ✅ **Yes (default)** |
| **PostgreSQL (local)** | Local | Free | Full SQL features, multi-user | Requires server | ✅ **Yes (prod)** |
| **Supabase** | Cloud | Free tier | Managed PostgreSQL, auth | Data on cloud, limits | ⚠️ Optional |
| **MySQL (local)** | Local | Free | Popular, well-supported | More complex than SQLite | ⚠️ Alternative |

**Default Choice:** SQLite (file-based, zero configuration)

**Configuration:**
```json
{
  "database": "sqlite",
  "database_path": "data/omnimind.db"
}
```

**Migration to PostgreSQL (optional):**
```bash
# Install PostgreSQL
sudo apt-get install postgresql

# Create database
sudo -u postgres createdb omnimind

# Update config
{
  "database": "postgresql",
  "database_url": "postgresql://localhost/omnimind"
}
```

---

### LLM Inference

| Service | Type | Cost | Pros | Cons | Recommended |
|---------|------|------|------|------|-------------|
| **llama.cpp (local)** | Local | Free | Fast, CPU/GPU support | Limited model sizes | ✅ **Yes (default)** |
| **Ollama (local)** | Local | Free | Easy model management | Higher resource usage | ✅ **Yes (alternative)** |
| **Transformers (local)** | Local | Free | Most models supported | Slower, more RAM | ⚠️ Fallback |
| **OpenAI API** | Cloud | Paid | Best quality | Costs $$$, data on cloud | ❌ No |
| **Anthropic API** | Cloud | Paid | Claude models | Costs $$$, data on cloud | ❌ No |

**Default Choice:** llama.cpp (CPU and GPU support)

**Configuration:**
```json
{
  "llm_backend": "llama_cpp",
  "model_path": "models/qwen2-7b-instruct.Q4_K_M.gguf"
}
```

**Model Recommendations:**
- **Low RAM (<8GB):** Qwen2-1.5B-Instruct (Q4 quantized) ~1GB
- **Medium RAM (8-16GB):** Qwen2-7B-Instruct (Q4 quantized) ~4GB
- **High RAM (16GB+):** Qwen2-7B-Instruct (Q8 quantized) ~7GB

---

### Model Storage

| Service | Type | Cost | Pros | Cons | Recommended |
|---------|------|------|------|------|-------------|
| **HuggingFace Hub** | Cloud | Free | Huge model library | Requires internet | ✅ **Yes (download only)** |
| **Local file system** | Local | Free | Always available | Manual management | ✅ **Yes (after download)** |
| **AWS S3** | Cloud | Paid | Scalable | Costs $$$, latency | ❌ No |

**Default Choice:** Download from HuggingFace, store locally

**Download Models:**
```bash
# Using HuggingFace CLI
pip install huggingface-hub
huggingface-cli download Qwen/Qwen2-7B-Instruct-GGUF \
  qwen2-7b-instruct-q4_k_m.gguf \
  --local-dir models/

# Models stored in: models/
```

---

### Audio Processing

| Service | Type | Cost | Pros | Cons | Recommended |
|---------|------|------|------|------|-------------|
| **Whisper (local)** | Local | Free | Excellent quality | Slow on CPU | ✅ **Yes (GPU)** |
| **Vosk (local)** | Local | Free | Fast on CPU | Lower quality | ✅ **Yes (CPU)** |
| **Google Speech API** | Cloud | Paid | Best quality | Costs $$$, privacy | ❌ No |
| **AssemblyAI** | Cloud | Paid | Good quality | Costs $$$, privacy | ❌ No |

**Default Choice:** 
- With GPU: OpenAI Whisper (local)
- CPU-only: Vosk (local)

**Installation:**
```bash
# Whisper (GPU recommended)
pip install openai-whisper

# Vosk (CPU-friendly)
pip install vosk
```

---

### Image Processing

| Service | Type | Cost | Pros | Cons | Recommended |
|---------|------|------|------|------|-------------|
| **YOLO (local)** | Local | Free | Fast, accurate | Requires training | ✅ **Yes** |
| **OmniParser (local)** | Local | Free | UI parsing | Limited to UI | ✅ **Yes (included)** |
| **Google Vision API** | Cloud | Paid | Best quality | Costs $$$, privacy | ❌ No |
| **AWS Rekognition** | Cloud | Paid | Good quality | Costs $$$, privacy | ❌ No |

**Default Choice:** YOLO for object detection, OmniParser for UI

**Installation:**
```bash
pip install ultralytics  # YOLOv8
```

---

### Authentication

| Service | Type | Cost | Pros | Cons | Recommended |
|---------|------|------|------|------|-------------|
| **JWT (local)** | Local | Free | Simple, stateless | Manual implementation | ✅ **Yes (default)** |
| **OAuth2 (local)** | Local | Free | Standard protocol | More complex | ⚠️ Advanced use |
| **Auth0** | Cloud | Free tier | Easy integration | Limits, vendor lock-in | ❌ No |
| **Supabase Auth** | Cloud | Free tier | Integrated with DB | Data on cloud | ❌ No |

**Default Choice:** JWT (JSON Web Tokens) with local validation

**Implementation:**
```python
# src/security/auth.py
import jwt
from datetime import datetime, timedelta

def generate_token(user_id: str, secret: str) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, secret, algorithm="HS256")

def verify_token(token: str, secret: str) -> dict:
    return jwt.decode(token, secret, algorithms=["HS256"])
```

---

## Cost Comparison

### Monthly Costs for Typical Workload

**Cloud-Based Stack (NOT recommended):**
- OpenAI API: $20-100/month
- Pinecone: $70/month
- Redis Cloud: $10/month
- Supabase Pro: $25/month
- **Total: $125-205/month** 💸

**Local-First Stack (recommended):**
- ChromaDB: $0
- fakeredis/Redis: $0
- SQLite: $0
- llama.cpp: $0
- **Total: $0/month** ✅

**One-time costs (local):**
- GPU (optional): $200-500 (used GTX 1650)
- Storage: $50 (1TB SSD)
- **Total: $250-550 one-time**

**Break-even:** ~2-4 months vs cloud services

---

## Performance Comparison

### Latency

| Operation | Cloud | Local |
|-----------|-------|-------|
| LLM inference | 500-2000ms | 100-500ms (GPU), 2000-5000ms (CPU) |
| Vector search | 50-200ms | 5-50ms |
| Database query | 20-100ms | 1-10ms |
| Cache lookup | 10-50ms | <1ms |

**Winner:** Local (lower latency in most cases)

### Privacy

| Aspect | Cloud | Local |
|--------|-------|-------|
| Data location | Third-party servers | Your machine |
| Encryption | In transit + at rest | Full control |
| Access logs | Visible to provider | Only you |
| Compliance | Depends on provider | Full control |

**Winner:** Local (complete privacy)

---

## Migration Guide

### From Paid Services to Free

#### 1. Migrate from Pinecone to ChromaDB

```python
# Export from Pinecone
import pinecone
pinecone.init(api_key="...")
index = pinecone.Index("omnimind")

# Get all vectors
vectors = index.fetch(ids=all_ids)

# Import to ChromaDB
import chromadb
client = chromadb.PersistentClient(path="data/chromadb")
collection = client.create_collection("omnimind")

# Add vectors
collection.add(
    ids=[v.id for v in vectors],
    embeddings=[v.values for v in vectors],
    metadatas=[v.metadata for v in vectors]
)
```

#### 2. Migrate from OpenAI to llama.cpp

```python
# Old (OpenAI API)
import openai
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)

# New (llama.cpp local)
from llama_cpp import Llama
llm = Llama(model_path="models/qwen2-7b-instruct.gguf")
response = llm.create_chat_completion(
    messages=[{"role": "user", "content": "Hello"}]
)
```

#### 3. Migrate from Supabase to SQLite

```python
# Old (Supabase)
from supabase import create_client
supabase = create_client(url, key)
data = supabase.table("users").select("*").execute()

# New (SQLite)
import sqlite3
conn = sqlite3.connect("data/omnimind.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM users")
data = cursor.fetchall()
```

---

## Hybrid Approach (Optional)

You can mix local and cloud services for specific use cases:

### Use Cloud For:
- Model downloads (HuggingFace Hub)
- Backups (encrypted, infrequent)
- Collaboration (shared models with team)

### Keep Local For:
- LLM inference (privacy, latency)
- Vector database (fast search)
- User data (privacy, compliance)
- Cache (ultra-low latency)

---

## Recommended Stack by Use Case

### Development & Testing
```json
{
  "vector_db": "chromadb",
  "cache_backend": "fakeredis",
  "database": "sqlite",
  "llm_backend": "llama_cpp",
  "auth": "jwt"
}
```

### Production (Single Machine)
```json
{
  "vector_db": "chromadb",
  "cache_backend": "redis",
  "database": "sqlite",
  "llm_backend": "llama_cpp",
  "auth": "jwt"
}
```

### Production (Multi-User)
```json
{
  "vector_db": "chromadb",
  "cache_backend": "redis",
  "database": "postgresql",
  "llm_backend": "llama_cpp",
  "auth": "oauth2"
}
```

### CI/CD Pipeline
```json
{
  "vector_db": "chromadb",
  "cache_backend": "fakeredis",
  "database": "sqlite",
  "llm_backend": "transformers",  // or skip LLM tests
  "auth": "jwt"
}
```

---

## Conclusion

**OmniMind's local-first approach provides:**
- ✅ Zero recurring costs
- ✅ Complete privacy control
- ✅ Lower latency (for most operations)
- ✅ No vendor lock-in
- ✅ Works offline
- ✅ Predictable performance

**Trade-offs:**
- ⚠️ Higher initial setup complexity
- ⚠️ Manual scaling (vs. auto-scaling cloud)
- ⚠️ You manage backups and updates

**Recommendation:** Start with the local-first stack and only add cloud services if absolutely necessary for your specific use case.

---

**References:**
- ChromaDB: https://www.trychroma.com/
- Redis: https://redis.io/
- SQLite: https://www.sqlite.org/
- llama.cpp: https://github.com/ggerganov/llama.cpp
- Whisper: https://github.com/openai/whisper

**Last Updated:** November 19, 2025  
**Status:** ✅ Production Ready
