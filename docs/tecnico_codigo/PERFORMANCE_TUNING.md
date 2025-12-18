# OmniMind Performance Tuning Guide

## Overview

This guide provides comprehensive performance optimization techniques for OmniMind, including benchmark results, tuning recommendations, and monitoring strategies.

## Quick Performance Check

Execute o diagnóstico de performance para verificar o estado atual:

```bash
# Diagnóstico rápido de performance
python scripts/canonical/diagnose/diagnose.py --check-performance

# Verificar métricas do sistema
curl http://localhost:8000/api/metrics
```

**Nota**: O benchmark `PHASE7_COMPLETE_BENCHMARK_AUDIT.py` não existe mais. Use os scripts de diagnóstico e métricas da API.

## Benchmark Results

### Hardware Baseline (GTX 1650)

Baseado em testes validados (Novembro-Dezembro 2025):

```
CPU Performance:
  - Throughput: 253.21 GFLOPS (5000x5000 matrix multiply)
  - Cores: 4 physical / 8 threads
  - Architecture: Intel i5 10th Gen

GPU Performance:
  - Throughput: 1149.91 GFLOPS (5000x5000 matrix multiply)
  - Acceleration: 4.5x vs CPU
  - Memory: 4GB VRAM
  - Memory Bandwidth: 12.67 GB/s
  - CUDA Version: 12.4
  - PyTorch: 2.5.1+cu124 (atualizado Dezembro 2025)

System Memory:
  - Total: 24GB RAM
  - Available: ~18.5GB for operations
  - Swap: Configurado (varia)
```

**Nota**: PyTorch atualizado para 2.5.1+cu124 (Dezembro 2025).

### API Performance Targets

```
Endpoint Response Times (P95):
  - Health Check: < 10ms
    - GET /api/v1/health/
    - GET /api/v1/health/{check_name}
  - Task Submission: < 100ms
    - POST /api/tasks/
  - Task Status: < 50ms
    - GET /api/tasks/{task_id}
  - Metrics: < 100ms
    - GET /api/metrics
    - GET /api/omnimind/metrics/real
  - Orchestration: < 30s (depende da complexidade da tarefa)
    - POST /tasks/orchestrate

WebSocket:
  - Connection Latency: < 100ms
  - Message Latency: < 50ms
  - Concurrent Connections: 50+
  - Endpoint: ws://localhost:8000/ws

Throughput:
  - API Requests: 100+ req/s
  - Task Orchestration: 10 tarefas concorrentes (configurável)
  - Database Operations: 1000+ ops/s
```

**Configuração atual** (`config/agent_config.yaml`):
```yaml
performance:
  max_concurrent_tasks: 1  # Ajustável baseado em RAM disponível
  task_timeout: 300  # 5 minutos
  retry_attempts: 3
```

## Optimization Strategies

### 1. GPU Acceleration

**When to Use:**
- Large batch processing
- Model inference
- Vector operations
- Embedding generation

**Configuration:**

```yaml
# config/agent_config.yaml
gpu:
  device: "cuda:0"
  gpu_layers: -1  # Auto-gerenciado (Ollama gerencia)
  offload_ratio: 0.95

model:
  name: "phi:latest"  # Modelo padrão (Microsoft Phi)
  provider: "ollama"
  base_url: "http://localhost:11434"
  temperature: 0.7
  max_tokens: 2048
```

**Variáveis de ambiente CUDA** (definir via shell/script, não em código Python):
```bash
export CUDA_HOME=/usr
export CUDA_PATH=/usr
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu
```

**Memory Constraints (GTX 1650 - 4GB VRAM):**

```python
# Safe batch sizes for 4GB VRAM:
safe_batch_sizes = {
    "embeddings": 64,           # ~1GB
    "llm_inference": 8,         # ~2.5GB
    "matrix_operations": 5000,  # ~190MB per matrix
}

# Avoid OOM:
unsafe_batch_sizes = {
    "embeddings": 256,          # Would use ~4GB
    "llm_inference": 32,        # Would use ~10GB
    "matrix_operations": 10000, # Would use ~760MB
}
```

**Enable GPU in Code:**

```python
import torch

# Check availability
if torch.cuda.is_available():
    device = torch.device("cuda")
    print(f"Using GPU: {torch.cuda.get_device_name(0)}")
else:
    device = torch.device("cpu")
    print("Using CPU")

# Move tensors to GPU
tensor = tensor.to(device)
```

### 2. Database Optimization

**Qdrant Configuration:**

```yaml
# docker-compose.yml or Qdrant config
services:
  qdrant:
    environment:
      - QDRANT__STORAGE__OPTIMIZERS__INDEXING_THRESHOLD=10000
      - QDRANT__STORAGE__OPTIMIZERS__MAX_SEGMENT_SIZE=100000
      - QDRANT__STORAGE__WAL__WAL_CAPACITY_MB=256
    resources:
      limits:
        memory: 4G
```

**Query Optimization:**

```python
# Use filters to reduce search space
from qdrant_client.models import Filter, FieldCondition

results = client.search(
    collection_name="episodes",
    query_vector=embedding,
    limit=10,
    query_filter=Filter(
        must=[
            FieldCondition(
                key="timestamp",
                range={"gte": recent_timestamp}
            )
        ]
    )
)
```

### 3. API Server Tuning

**Uvicorn Configuration:**

```bash
# Development
uvicorn web.backend.main:app --reload

# Production (multiple workers)
uvicorn web.backend.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --limit-concurrency 100 \
  --timeout-keep-alive 5

# With Gunicorn (recommended for production)
gunicorn web.backend.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

**Worker Count Calculation:**

```
Optimal Workers = (2 x CPU Cores) + 1

Examples:
- 4 cores: 9 workers
- 8 cores: 17 workers
- 16 cores: 33 workers

For OmniMind (Intel i5 10th Gen, 4 cores):
  Recommended: 4-8 workers
```

### 4. Concurrency Limits

**Task Orchestration:**

```yaml
# config/agent_config.yaml
orchestrator:
  max_concurrent_tasks: 10  # Adjust based on available RAM
  max_iterations: 5
  timeout_seconds: 300

# Memory-constrained environments:
orchestrator:
  max_concurrent_tasks: 3
  max_iterations: 3
  timeout_seconds: 180
```

**WebSocket Connections:**

```python
# web/backend/websocket_manager.py
MAX_CONNECTIONS = 50  # Default
MAX_SUBSCRIPTIONS_PER_CLIENT = 10

# High-traffic scenarios:
MAX_CONNECTIONS = 100
MAX_SUBSCRIPTIONS_PER_CLIENT = 20
```

### 5. Caching Strategies

**LLM Response Caching:**

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_embedding(text: str):
    """Cache embeddings for frequently used text."""
    return model.encode(text)
```

**API Response Caching:**

```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

# Initialize cache
FastAPICache.init(RedisBackend(redis), prefix="omnimind-cache")

# Cache endpoint
@app.get("/tasks")
@cache(expire=60)  # Cache for 60 seconds
async def list_tasks():
    return get_tasks()
```

### 6. Memory Management

**Python GC Tuning:**

```python
import gc

# Aggressive garbage collection
gc.set_threshold(700, 10, 10)  # Default: (700, 10, 10)

# For memory-constrained environments:
gc.set_threshold(400, 5, 5)

# Periodic forced collection
import schedule
schedule.every(5).minutes.do(gc.collect)
```

**Model Loading:**

```python
# Load models on-demand instead of at startup
class LazyModelLoader:
    def __init__(self):
        self._model = None

    @property
    def model(self):
        if self._model is None:
            self._model = load_model()
        return self._model
```

### 7. Logging Optimization

**Production Logging:**

```yaml
# config/omnimind.yaml
logging:
  level: WARNING  # Reduce from DEBUG
  format: json    # Faster parsing
  async: true     # Non-blocking
  buffer_size: 1000
```

**Code Configuration:**

```python
import logging

# Disable debug logging in production
if not DEBUG_MODE:
    logging.getLogger("omnimind").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.ERROR)
```

### 8. Network Optimization

**HTTP/2 Support:**

```bash
# Install hypercorn for HTTP/2
pip install hypercorn

# Run with HTTP/2
hypercorn web.backend.main:app \
  --bind 0.0.0.0:8000 \
  --workers 4
```

**Connection Pooling:**

```python
import httpx

# Use connection pooling for external requests
limits = httpx.Limits(max_connections=100, max_keepalive_connections=20)
client = httpx.AsyncClient(limits=limits)
```

## Monitoring & Profiling

### 1. Real-time Monitoring

**Built-in Metrics:**

```bash
# API metrics
curl -u user:pass http://localhost:8000/metrics

# Performance tracker
curl -u user:pass http://localhost:8000/api/v1/performance/summary
```

**System Monitoring:**

```bash
# CPU/Memory/GPU
htop

# GPU-specific
nvidia-smi -l 1

# Disk I/O
iotop
```

### 2. Application Profiling

**Memory Profiling:**

```bash
# Install profiler
pip install memory-profiler

# Profile specific function
python -m memory_profiler script.py

# Or use decorator
@profile
def expensive_function():
    pass
```

**CPU Profiling:**

```bash
# Install py-spy
pip install py-spy

# Profile running process
py-spy top --pid <omnimind_pid>

# Generate flamegraph
py-spy record -o profile.svg --pid <omnimind_pid>
```

**Request Tracing:**

```python
# Enable OpenTelemetry
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

@app.get("/tasks")
async def list_tasks():
    with tracer.start_as_current_span("list_tasks"):
        # Your code here
        pass
```

### 3. Database Profiling

**Qdrant Query Analysis:**

```python
import time

start = time.perf_counter()
results = client.search(...)
duration = time.perf_counter() - start

print(f"Query took {duration:.3f}s")

# Log slow queries
if duration > 1.0:
    logger.warning(f"Slow query: {duration:.3f}s")
```

## Performance Tuning Checklist

### Initial Setup
- [ ] Run baseline benchmark
- [ ] Configure GPU if available
- [ ] Set appropriate worker count
- [ ] Configure database parameters
- [ ] Enable caching

### Production Deployment
- [ ] Use production logging level (WARNING/ERROR)
- [ ] Enable connection pooling
- [ ] Configure memory limits
- [ ] Set up monitoring
- [ ] Implement rate limiting

### Ongoing Optimization
- [ ] Monitor API response times
- [ ] Track memory usage trends
- [ ] Profile slow endpoints
- [ ] Optimize database queries
- [ ] Review and clear caches

## Common Performance Issues

### 1. Slow API Responses

**Symptoms:**
- Response times > 5 seconds
- Request timeouts

**Solutions:**
```bash
# 1. Increase workers
uvicorn web.backend.main:app --workers 8

# 2. Enable caching
export OMNIMIND_ENABLE_CACHE=true

# 3. Reduce log verbosity
export LOG_LEVEL=WARNING
```

### 2. High Memory Usage

**Symptoms:**
- OOM errors
- System swapping
- Slow performance

**Solutions:**
```yaml
# Reduce batch sizes
orchestrator:
  max_concurrent_tasks: 3

# Limit model cache
model:
  cache_size: 100  # Reduce from 1000
```

### 3. GPU Not Utilized

**Symptoms:**
- nvidia-smi shows 0% GPU usage
- Slower than CPU

**Solutions:**
```bash
# 1. Verify GPU available
python -c "import torch; print(torch.cuda.is_available())"

# 2. Reload nvidia module
sudo modprobe -r nvidia_uvm
sudo modprobe nvidia_uvm

# 3. Enable in config
export OMNIMIND_USE_GPU=true
```

## Advanced Optimizations

### 1. Mixed Precision Training

```python
import torch

# Enable automatic mixed precision
scaler = torch.cuda.amp.GradScaler()

with torch.cuda.amp.autocast():
    output = model(input)
    loss = criterion(output, target)
```

### 2. Batch Processing

```python
# Process in batches instead of one-by-one
def process_batch(items, batch_size=32):
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        results = model.process(batch)
        yield from results
```

### 3. Async Processing

```python
import asyncio

# Use async for I/O bound operations
async def process_async(items):
    tasks = [process_item(item) for item in items]
    results = await asyncio.gather(*tasks)
    return results
```

## Benchmarking Tools

### Run Benchmarks

```bash
# Diagnóstico completo do sistema
python scripts/canonical/diagnose/diagnose.py --full

# Verificação rápida de performance
python scripts/canonical/diagnose/diagnose.py --check-performance

# Benchmark de modelos LLM
python scripts/benchmark_llm_models.py

# Análise de suite de testes
python scripts/analyze_test_suite.py
```

**Nota**: O benchmark `PHASE7_COMPLETE_BENCHMARK_AUDIT.py` não existe mais. Use os scripts de diagnóstico disponíveis.

### Continuous Benchmarking

```bash
# Add to CI/CD
pytest tests/benchmarks/ --benchmark-only

# Monitor regression
python scripts/compare_benchmarks.py \
  logs/benchmark_baseline.json \
  logs/benchmark_current.json
```

## Additional Resources

- [Troubleshooting Guide](./TROUBLESHOOTING.md)
- [Interactive API Playground](./INTERACTIVE_API_PLAYGROUND.md)
- [Quick Start Guide](../canonical/QUICK_START.md)
- [Technical Checklist](../canonical/TECHNICAL_CHECKLIST.md)
- [System Initialization](../canonical/omnimind_system_initialization.md)

## 📘 Referências Técnicas

- **`web/backend/main.py`**: Define inicialização do FastAPI, routers e sistema de monitoramento
- **`config/agent_config.yaml`**: Centraliza configurações de modelo, GPU, performance e orquestração
- **`src/monitor/resource_protector.py`**: Fornece limites por modo (dev/test/prod) e handlers de CPU/RAM/DISCO
- **`scripts/run_tests_fast.sh`**: Suite rápida de testes (diária, ~15-20 min)
- **`scripts/run_tests_with_defense.sh`**: Suite completa de testes (semanal, ~45-90 min)
- **`scripts/canonical/diagnose/diagnose.py`**: Ferramenta de diagnóstico automatizado

---

**Autor**: Fabrício da Silva + assistência de IA (Copilot GitHub/Cursor/Gemini/Perplexity)
