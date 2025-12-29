# 🚀 QUICK START - MCP Optimization Phase 2

## Status: READY TO INTEGRATE

All 3 core modules are created and syntax-validated. Moving to integration phase.

---

## Module Import Patterns (Copy-Paste Ready)

### 1. Cache Integration Pattern
```python
# In any MCP handler file
from src.integrations.mcp_cache import get_mcp_cache, RequestType

async def handle_request(self, request):
    """Standard MCP request handler with cache"""
    cache = get_mcp_cache()

    # Create cache key from request
    cache_key = f"{request.mcp_type}:{request.method}:{hash(str(request.params))}"

    # Try cache first
    cached_value = await cache.get(cache_key)
    if cached_value is not None:
        return cached_value

    # Process request
    result = await self.process_request(request)

    # Store in cache (L1 + L2)
    await cache.put(cache_key, result, levels="L1L2")

    return result
```

### 2. Compression Integration Pattern
```python
# In context MCP handler
from src.integrations.mcp_semantic_compression import get_semantic_compressor

async def get_context_response(self, query: str):
    """Context response with semantic compression"""
    compressor = get_semantic_compressor()

    # Get full context
    full_context = await fetch_full_context(query)

    # Compress semantically (75% reduction)
    compressed = await compressor.compress(
        context_data=full_context,
        target_tokens=25000,  # From 100k baseline
        preserve_critical=True
    )

    return compressed
```

### 3. Rate Limiter Integration Pattern
```python
# In orchestrator
from src.integrations.mcp_dynamic_rate_limiter import (
    get_rate_limiter,
    RequestPriority
)

async def distribute_requests(self, requests: list):
    """Distribute requests with rate limiting"""
    limiter = get_rate_limiter(initial_rps=100)

    tasks = []
    for request in requests:
        # Determine priority
        priority = (
            RequestPriority.CRITICAL if request.is_critical
            else RequestPriority.HIGH if request.is_important
            else RequestPriority.NORMAL
        )

        # Submit with rate limiting
        try:
            task = limiter.submit_request(
                coro=process_mcp_request(request),
                priority=priority,
                timeout_seconds=30
            )
            tasks.append(task)
        except Exception as e:
            logger.warning(f"Request rejected: {e}")

    # Execute all with RPS control
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

---

## File Locations Reference

| Module | Path | Lines | Status |
|--------|------|-------|--------|
| Cache | `src/integrations/mcp_cache.py` | 380 | ✅ Ready |
| Compression | `src/integrations/mcp_semantic_compression.py` | 400 | ✅ Ready |
| Rate Limiter | `src/integrations/mcp_dynamic_rate_limiter.py` | 500 | ✅ Ready |
| Diagnostic | `docs/DIAGNOSTICO_MCP_OTIMIZACAO_13DEC.md` | 400 | ✅ Done |
| Summary | `docs/IMPLEMENTACAO_MCP_FASE1_COMPLETA.md` | 300 | ✅ Done |

---

## Integration Checklist - Phase 2

### Step 1: Cache Integration (2-3 hours)
- [ ] Edit `src/mcp_servers/mcp_memory_server.py`
  - Add import: `from src.integrations.mcp_cache import get_mcp_cache`
  - Wrap main handler with cache pattern
  - Test: Run memory MCP, verify cache creates data/mcp_cache_L2.jsonl

- [ ] Edit `src/mcp_servers/mcp_context_server.py`
  - Same cache pattern
  - Verify cache hit rate > 50%

- [ ] Edit `src/mcp_servers/mcp_thinking_server.py`
  - Same cache pattern
  - Monitor eviction rate (should be low if cache sized correctly)

### Step 2: Compression Integration (1-2 hours)
- [ ] Edit `src/mcp_servers/mcp_context_server.py`
  - Add import: `from src.integrations.mcp_semantic_compression import get_semantic_compressor`
  - In context response handler, add:
    ```python
    compressor = get_semantic_compressor()
    response = await compressor.compress(response, target_tokens=25000)
    ```
  - Verify compression metadata in response

### Step 3: Rate Limiter Integration (1-2 hours)
- [ ] Edit `src/core/mcp_orchestrator.py`
  - Add import: `from src.integrations.mcp_dynamic_rate_limiter import get_rate_limiter, RequestPriority`
  - Initialize in __init__: `self.limiter = get_rate_limiter(initial_rps=100)`
  - Wrap request distribution with limiter pattern
  - Add health check logging every 60s

### Step 4: Configuration Updates (30 min)
- [ ] Edit `config/mcp_servers.json`
  - Increase `max_concurrent_requests`: 100 → 500
  - Set `enable_rate_limiting`: true
  - Set `cache_enabled`: true (for all MCPs)
  - Add `compression_enabled`: true (for context MCP only)

### Step 5: Testing (2-3 hours)
- [ ] Unit tests for each integrated module
- [ ] Load test: 100 req/s → 500 req/s
- [ ] Monitor: CPU, Memory, Cache hit rate
- [ ] Verify: <1% error rate under sustained load

---

## Expected Results After Phase 2

### Throughput
```
Before: 0 req/s (infinite crash loop)
After:  500+ req/s (sustainable)
Improvement: ∞x
```

### Cache Efficiency
```
Hit Rate: >70% (typical workloads)
Access Time L1: 10-100µs
Access Time L2: 100-500µs
Memory Saved: 50-60% token reduction
```

### Token Usage
```
Before: 100,000 tokens per context
After:  25,000 tokens per context (75% reduction)
Savings: 75% less API calls, less memory
```

### System Health
```
CPU Usage: < 50% (was stuck at 95-100%)
Memory: Stable, no leaks
Disk: L2 cache uses ~10MB max
Uptime: >99.9% (was 0%)
```

---

## Validation Metrics

After each step, verify these metrics:

### After Cache Integration
```bash
# In logs or monitoring:
✅ cache_hits > cache_misses (ratio should be 2:1 or better)
✅ eviction_count < 50 (shouldn't evict often)
✅ No "cache.get() error" messages
✅ data/mcp_cache_L2.jsonl file exists and growing
```

### After Compression Integration
```bash
# In response metadata:
✅ compression_ratio > 0.7 (75% reduction confirmed)
✅ critical_items_preserved == true
✅ compression_time_ms < 100
✅ No "compression failed" errors
```

### After Rate Limiter Integration
```bash
# In stats output:
✅ requests_dropped < 1% (drop rate acceptable)
✅ avg_queue_depth < 50 (no major backlog)
✅ health_status in ["HEALTHY", "NORMAL"]
✅ rps_current matches rps_target
```

---

## Troubleshooting

### If Cache Not Working
```python
# Debug: Check cache initialization
from src.integrations.mcp_cache import get_mcp_cache
cache = get_mcp_cache()
print(cache.stats())  # Should show hits > 0 after requests

# Check L2 file
ls -lah data/mcp_cache_L2.jsonl  # Should exist and have content
```

### If Compression Too Slow
```python
# Profile compression
import time
start = time.time()
result = await compressor.compress(data, target_tokens=25000)
elapsed = time.time() - start
print(f"Compression took {elapsed*1000:.1f}ms")
# Should be < 100ms. If > 200ms, reduce target_tokens to 10000
```

### If Rate Limiter Dropping Requests
```python
# Check health status
health = await limiter.check_system_health()
print(health)  # If stressed, reduce incoming request rate

# Adjust initial RPS if needed
limiter = get_rate_limiter(initial_rps=50)  # Was 100, reduce if too aggressive
```

---

## Commands for Phase 2

### Start fresh (kill old MCPs)
```bash
pkill -f "mcp_omnimind|mcp_orchestrator" 2>/dev/null || true
sleep 2
# Now restart with new code
```

### Monitor during integration
```bash
# Terminal 1: Watch logs
tail -f logs/mcp_orchestrator.log | grep -E "(cache|compression|rate_limit|ERROR)"

# Terminal 2: Monitor system
watch -n 1 'ps aux | grep mcp_omnimind | grep -v grep | wc -l'

# Terminal 3: Monitor cache (if added logging)
tail -f data/mcp_cache_L2.jsonl | tail -5
```

### Load test (after integration)
```bash
# Using Apache Bench (if available)
ab -n 1000 -c 50 http://localhost:8000/health

# Or using curl loop
for i in {1..1000}; do curl -s http://localhost:8000/health &>/dev/null & done; wait
```

---

## Next Session Prep

When continuing Phase 2 integration:

1. **Check status:**
   ```bash
   git status  # See modified files
   git diff src/mcp_servers/  # Review changes
   ```

2. **Test syntax:**
   ```bash
   python -m py_compile src/mcp_servers/*.py  # Check for syntax errors
   ```

3. **Run quick validation:**
   ```bash
   ./scripts/validate_code.sh  # black, flake8, mypy
   ```

4. **Then start integration** in this order:
   - memory MCP (cache only)
   - context MCP (cache + compression)
   - thinking MCP (cache only)
   - orchestrator (rate limiter)

---

## Emergency Rollback

If something breaks during integration:

```bash
# Revert last file
git checkout -- src/mcp_servers/mcp_memory_server.py

# Revert all Phase 2 changes
git checkout -- src/mcp_servers/

# Or nuke and restart
git clean -fd src/
git reset --hard HEAD
```

---

**Status:** 🟢 PHASE 1 COMPLETE - READY FOR PHASE 2
**Next Task:** Begin cache integration in memory MCP
**Estimated Phase 2 Duration:** 8-10 hours total
**Target Completion:** Same day (if 8+ hours available)

---

Generated: 2025-12-13 14:55 UTC
