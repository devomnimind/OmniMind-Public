# Quick Reference: Observability & Scaling Features

## Distributed Tracing

```python
from src.observability import DistributedTracer, TraceConfig, SpanKind

# Initialize tracer
config = TraceConfig(
    service_name="omnimind",
    exporter_type="console",  # or "jaeger", "zipkin"
    sample_rate=1.0
)
tracer = DistributedTracer(config)

# Use context manager (recommended)
with tracer.trace("operation_name") as span:
    span.set_attribute("user_id", "123")
    span.add_event("processing_started")
    # ... do work ...

# Manual span management
span = tracer.start_span("operation", kind=SpanKind.SERVER)
try:
    # ... do work ...
    span.set_status(SpanStatus.OK)
except Exception as e:
    span.set_status(SpanStatus.ERROR, str(e))
finally:
    span.end()

# Export traces
tracer.export_traces()
```

## Custom Metrics

```python
from src.observability import CustomMetricsExporter, MetricsConfig, MLMetrics

# Initialize exporter
config = MetricsConfig(
    prometheus_port=9090,
    export_format="prometheus",  # or "json", "both"
)
exporter = CustomMetricsExporter(config)

# Record metrics
exporter.record_counter("requests_total", 1, {"endpoint": "/api"})
exporter.record_gauge("cpu_usage", 75.5)
exporter.record_histogram("latency_ms", 123.4)

# ML-specific metrics
ml_metrics = MLMetrics(
    model_inference_latency_ms=50.0,
    gpu_utilization_percent=80.0,
    tokens_per_second=25.0
)
exporter.record_ml_metrics(ml_metrics)

# Export metrics
prometheus_text = exporter.export_prometheus()
json_text = exporter.export_json()
```

## Log Aggregation

```python
from src.observability import LogAggregator, LogConfig, LogLevel, LogPattern, AlertSeverity

# Initialize aggregator
config = LogConfig(
    log_level=LogLevel.INFO,
    enable_pattern_detection=True
)
aggregator = LogAggregator(config)

# Add custom pattern
pattern = LogPattern(
    name="api_error",
    regex=r"api.*error",
    severity=AlertSeverity.HIGH,
    description="API errors"
)
aggregator.add_pattern(pattern)

# Log events
aggregator.log(LogLevel.INFO, "User logged in", "auth", {"user_id": "123"})
aggregator.log(LogLevel.ERROR, "API error occurred")

# Get alerts and analytics
alerts = aggregator.get_alerts()
analytics = aggregator.analyze()
summary = analytics.get_summary()

# Export logs
json_logs = aggregator.export_logs("json")
es_logs = aggregator.export_logs("elasticsearch")
```

## Continuous Profiling

```python
from src.observability import ContinuousProfiler, FlameGraphGenerator, ProfilingConfig

# Initialize profiler
config = ProfilingConfig(
    sample_interval_seconds=60,
    max_samples=1000
)
profiler = ContinuousProfiler(config)

# Decorator approach
@profiler.profile
def expensive_function():
    # ... complex computation ...
    pass

# Manual profiling
profiler.start()
# ... run application ...
profiler.stop()

# Get top functions
top_funcs = profiler.get_top_functions(limit=10)

# Generate flame graph
generator = FlameGraphGenerator()
samples = profiler.get_samples()
flame_graph = generator.generate(samples)
generator.save_svg(flame_graph, "profile.svg")
generator.save_json(flame_graph, "profile.json")
```

## GPU Resource Pool

```python
from src.scaling import GPUResourcePool, GPUPoolConfig, GPUTask, GPUDevice

# Initialize pool
config = GPUPoolConfig(
    auto_discover_gpus=True,
    enable_load_balancing=True
)
pool = GPUResourcePool(config)

# Or manually add GPUs
gpu = GPUDevice(
    device_id=0,
    name="NVIDIA RTX 3090",
    total_memory_mb=24576,
    compute_capability="8.6"
)
pool.add_gpu(gpu)

# Create task
task = GPUTask(
    task_id="inference_1",
    required_memory_mb=4096,
    min_compute_capability="7.0"
)

# Allocate GPU
device_id = pool.allocate_gpu(task)
if device_id is not None:
    # ... use GPU ...
    pool.release_gpu(task.task_id)
else:
    print("Task queued, waiting for GPU")

# Get statistics
stats = pool.get_pool_stats()
print(f"Available GPUs: {stats['available_gpus']}")
```

## Database Connection Pool

```python
from src.scaling import DatabaseConnectionPool, PoolConfig

# Initialize pool
config = PoolConfig(
    pool_size=10,
    max_overflow=5,
    pool_pre_ping=True,
    pool_timeout_seconds=30
)

pool = DatabaseConnectionPool(
    "postgresql://user:pass@localhost/db",
    config
)

# Use connection
with pool.get_connection() as conn:
    result = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    
# Get statistics
stats = pool.get_stats()
print(f"Active: {stats['active_connections']}")
print(f"Idle: {stats['idle_connections']}")

# Close all connections (during shutdown)
pool.close_all()
```

## Multi-Level Cache

```python
from src.scaling import MultiLevelCache, CacheConfig, CacheLevel, EvictionPolicy

# Configure each level
l1_config = CacheConfig(
    max_size_bytes=10*1024*1024,  # 10MB
    eviction_policy=EvictionPolicy.LRU
)
l2_config = CacheConfig(
    max_size_bytes=100*1024*1024,  # 100MB
    eviction_policy=EvictionPolicy.LRU
)
l3_config = CacheConfig(
    max_size_bytes=1024*1024*1024,  # 1GB
    eviction_policy=EvictionPolicy.TTL
)

cache = MultiLevelCache(l1_config, l2_config, l3_config)

# Direct usage
cache.set("user:123", user_data, ttl_seconds=3600)
user = cache.get("user:123")
cache.delete("user:123")

# Function decorator
@cache.cache_decorator(ttl_seconds=300, level=CacheLevel.L1)
def get_user_profile(user_id):
    # ... expensive database query ...
    return profile

# Get statistics
stats = cache.get_stats()
print(f"L1 hit rate: {stats['l1']['hit_rate']}")
print(f"Total hits: {stats['total_hits']}")

# Clear all caches
cache.clear()
```

## Integration Example

```python
from src.observability import (
    DistributedTracer, TraceConfig,
    CustomMetricsExporter, MetricsConfig,
    LogAggregator, LogConfig, LogLevel
)
from src.scaling import MultiLevelCache, CacheConfig

# Initialize all components
tracer = DistributedTracer(TraceConfig(service_name="omnimind"))
metrics = CustomMetricsExporter(MetricsConfig())
logs = LogAggregator(LogConfig())
cache = MultiLevelCache(
    CacheConfig(max_size_bytes=10*1024*1024),
    CacheConfig(max_size_bytes=100*1024*1024),
    CacheConfig(max_size_bytes=1024*1024*1024)
)

# Use together
def process_request(request_id):
    with tracer.trace("process_request") as span:
        span.set_attribute("request_id", request_id)
        
        # Check cache
        cached = cache.get(f"request:{request_id}")
        if cached:
            metrics.record_counter("cache_hits", 1)
            logs.log(LogLevel.INFO, f"Cache hit for {request_id}")
            return cached
        
        # Process request
        try:
            result = expensive_operation()
            cache.set(f"request:{request_id}", result)
            metrics.record_counter("requests_processed", 1)
            metrics.record_histogram("processing_time_ms", span.duration_ms())
            logs.log(LogLevel.INFO, f"Request processed: {request_id}")
            return result
        except Exception as e:
            metrics.record_counter("errors", 1, {"type": type(e).__name__})
            logs.log(LogLevel.ERROR, f"Error processing {request_id}: {e}")
            raise
```

## Configuration Best Practices

### Development
```python
# Distributed Tracing
TraceConfig(
    enabled=True,
    sample_rate=1.0,  # Trace everything
    exporter_type="console"
)

# Metrics
MetricsConfig(
    export_interval_seconds=5,
    export_format="json"
)

# Logging
LogConfig(
    log_level=LogLevel.DEBUG,
    enable_pattern_detection=True
)
```

### Production
```python
# Distributed Tracing
TraceConfig(
    enabled=True,
    sample_rate=0.1,  # Sample 10%
    exporter_type="jaeger",
    exporter_endpoint="http://jaeger:14268/api/traces"
)

# Metrics
MetricsConfig(
    export_interval_seconds=15,
    export_format="prometheus",
    prometheus_port=9090
)

# Logging
LogConfig(
    log_level=LogLevel.INFO,
    enable_pattern_detection=True,
    max_log_entries=50000,
    retention_hours=24
)
```

## Performance Tips

1. **Tracing:** Use sampling in production (sample_rate < 1.0)
2. **Metrics:** Export at reasonable intervals (15-60s)
3. **Logging:** Set appropriate log level (INFO or WARNING in prod)
4. **Caching:** Size L1 cache based on hot data working set
5. **GPU Pool:** Enable load balancing for multi-GPU setups
6. **DB Pool:** Size pool based on concurrent workload

## Troubleshooting

### No traces appearing
- Check `enabled=True` in TraceConfig
- Verify exporter configuration
- Check `~/.omnimind/traces/` directory

### Metrics not exporting
- Verify Prometheus port is accessible
- Check export interval configuration
- Review `~/.omnimind/metrics/` directory

### Logs not aggregating
- Check log level threshold
- Verify pattern detection is enabled
- Review `~/.omnimind/logs/aggregated/` directory

### Cache not working
- Check cache size configuration
- Verify TTL settings
- Review eviction policy

### GPU allocation failing
- Verify GPUs are discovered (auto_discover_gpus=True)
- Check memory requirements vs available memory
- Review GPU pool statistics
