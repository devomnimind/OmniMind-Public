# OpenTelemetry Integration and External APIs - Implementation Guide

## 📋 Overview

This document describes the comprehensive observability and external integration features implemented for the OmniMind project, completing FRENTE 4 (Observability) and FRENTE 5 (External Integrations).

## 🎯 FRENTE 4: Observability (95% Complete)

### 1. OpenTelemetry Integration

**File**: `src/observability/opentelemetry_integration.py`

Full OpenTelemetry SDK integration with production-ready exporters.

#### Features:
- ✅ OTLP exporter (default)
- ✅ Console exporter (debugging)
- ✅ Jaeger exporter support
- ✅ Zipkin exporter support
- ✅ Distributed tracing
- ✅ Metrics collection

#### Usage Example:
```python
from src.observability import OpenTelemetryConfig, OpenTelemetryIntegration

# Configure OpenTelemetry
config = OpenTelemetryConfig(
    service_name="omnimind",
    environment="production",
    enable_console_export=True,
    enable_jaeger_export=True,
)

# Initialize
otel = OpenTelemetryIntegration(config)
otel.initialize()

# Get tracer for distributed tracing
tracer = otel.get_tracer("my-component")
with tracer.start_as_current_span("operation") as span:
    span.set_attribute("user_id", "12345")
    # Do work
    
# Get meter for metrics
meter = otel.get_meter("my-component")
counter = meter.create_counter("requests_total")
counter.add(1, {"endpoint": "/api/task"})

# Shutdown when done
otel.shutdown()
```

### 2. Performance Bottleneck Analyzer

**File**: `src/observability/performance_analyzer.py`

Automated analysis of performance bottlenecks from profiling data.

#### Features:
- ✅ Automated bottleneck detection
- ✅ Severity classification (LOW, MEDIUM, HIGH, CRITICAL)
- ✅ Category classification (CPU, I/O, Network, Memory, etc.)
- ✅ Actionable recommendations
- ✅ JSON report generation

#### Usage Example:
```python
from src.observability import (
    ContinuousProfiler, 
    ProfilingConfig,
    PerformanceAnalyzer
)

# Profile your code
profiler = ContinuousProfiler(ProfilingConfig())
profiler.start()
# ... run application ...
profiler.stop()

# Analyze for bottlenecks
samples = profiler.get_samples()
analyzer = PerformanceAnalyzer()
report = analyzer.analyze(samples, min_percentage=1.0)

# View results
print(f"Summary: {report.summary}")
for bottleneck in report.bottlenecks:
    print(f"[{bottleneck.severity.value}] {bottleneck.function_name}")
    print(f"  → {bottleneck.recommendation}")

# Save report
analyzer.save_report(report)
```

### 3. ML-Specific Grafana Dashboard

**File**: `grafana/dashboards/ml-performance-metrics.json`

Comprehensive dashboard for ML workload monitoring.

#### Panels:
- Model Inference Latency (p50, p95, p99)
- Model Throughput
- GPU Utilization
- GPU Memory Usage
- Model Accuracy
- Model Loss
- Token Generation Rate
- Cache Hit Rate
- Batch Size Distribution
- Training/Inference Split
- Active Model Instances
- Error Rate by Model

### 4. Prometheus Alerting Rules

**File**: `prometheus/alerts/omnimind_alerts.yml`

Production-ready alerting rules for comprehensive monitoring.

#### Alert Groups:
1. **Performance Alerts**
   - High/Critical Request Latency
   - High/Critical Error Rate

2. **ML Metrics Alerts**
   - High/Critical GPU Memory Usage
   - Low Model Accuracy
   - High Inference Latency
   - Low Token Generation Rate

3. **System Alerts**
   - High CPU/Memory Usage
   - Critical Memory/Disk Space

4. **Availability Alerts**
   - Service Down
   - Unusual High Request Rate
   - Low Cache Hit Rate

## 🌐 FRENTE 5: External Integrations (95% Complete)

### 1. Enhanced MCP Client

**File**: `src/integrations/mcp_client_enhanced.py`

Production-ready MCP client with advanced fault tolerance.

#### Features:
- ✅ Connection pooling
- ✅ Automatic retry with exponential backoff
- ✅ Circuit breaker pattern
- ✅ Comprehensive error handling
- ✅ Request statistics

#### Usage Example:
```python
from src.integrations import (
    EnhancedMCPClient,
    RetryConfig,
    CircuitBreakerConfig
)

# Configure retry and circuit breaker
retry_config = RetryConfig(
    max_retries=3,
    initial_backoff_ms=100,
    max_backoff_ms=5000
)

circuit_config = CircuitBreakerConfig(
    failure_threshold=5,
    timeout_seconds=60
)

# Create client
client = EnhancedMCPClient(
    endpoint="http://localhost:4321/mcp",
    retry_config=retry_config,
    circuit_breaker_config=circuit_config
)

# Use with automatic retries and circuit breaking
try:
    content = client.read_file("/path/to/file.txt")
    stats = client.get_stats()
    print(f"Success rate: {stats['success_rate']:.2%}")
except Exception as e:
    print(f"Error: {e}")
```

### 2. OAuth 2.0 Client

**File**: `src/integrations/oauth2_client.py`

Complete OAuth 2.0 implementation with modern security features.

#### Features:
- ✅ Authorization Code Flow
- ✅ Client Credentials Flow
- ✅ Refresh Token Support
- ✅ PKCE (Proof Key for Code Exchange)
- ✅ Automatic token refresh

#### Usage Example:
```python
from src.integrations import OAuth2Client, OAuth2Config

# Configure OAuth
config = OAuth2Config(
    client_id="your-client-id",
    client_secret="your-secret",
    authorization_endpoint="https://provider.com/oauth/authorize",
    token_endpoint="https://provider.com/oauth/token",
    redirect_uri="http://localhost:8080/callback",
    scope="read write"
)

oauth = OAuth2Client(config)

# 1. Get authorization URL (user visits this)
auth_url = oauth.get_authorization_url(use_pkce=True)
print(f"Visit: {auth_url}")

# 2. Exchange code for token (after redirect)
token = oauth.exchange_code_for_token(authorization_code)

# 3. Use token for API calls
headers = oauth.get_auth_headers()
# headers = {"Authorization": "Bearer <token>"}

# 4. Token auto-refreshes when needed
valid_token = oauth.get_valid_token()
```

### 3. Webhook Framework

**File**: `src/integrations/webhook_framework.py`

Complete webhook receiver and sender with security features.

#### Features:
- ✅ HMAC signature generation/validation
- ✅ Event handler registration
- ✅ Automatic retry with backoff
- ✅ Event types (PING, CREATE, UPDATE, DELETE, CUSTOM)

#### Receiver Example:
```python
from src.integrations import (
    WebhookReceiver,
    WebhookConfig,
    WebhookEventType
)

# Configure receiver
config = WebhookConfig(
    secret="my-webhook-secret",
    validate_signature=True
)

receiver = WebhookReceiver(config)

# Register event handlers
@receiver.on_event(WebhookEventType.CREATE)
def handle_create(event):
    print(f"Created: {event.payload}")

@receiver.on_event(WebhookEventType.UPDATE)
def handle_update(event):
    print(f"Updated: {event.payload}")

# Process incoming webhook
result = receiver.process_webhook(
    body=request_body,
    headers=request_headers
)
```

#### Sender Example:
```python
from src.integrations import (
    WebhookSender,
    WebhookEvent,
    WebhookEventType
)
import time
from uuid import uuid4

# Configure sender
config = WebhookConfig(secret="my-webhook-secret")
sender = WebhookSender(config)

# Create event
event = WebhookEvent(
    id=str(uuid4()),
    type=WebhookEventType.CREATE,
    timestamp=time.time(),
    payload={"user_id": "123", "action": "signup"}
)

# Send webhook (with automatic retries)
result = sender.send_webhook(
    url="https://external.com/webhook",
    event=event,
    max_retries=3
)

# Check stats
stats = sender.get_stats()
print(f"Success rate: {stats['success_rate']:.2%}")
```

## 🧪 Testing

### Test Coverage
- **test_enhanced_observability.py**: 15 tests
  - OpenTelemetry integration tests
  - Performance analyzer tests
  
- **test_enhanced_integrations.py**: 25 tests
  - Circuit breaker tests
  - Enhanced MCP client tests
  - OAuth 2.0 tests
  - Webhook framework tests

### Running Tests
```bash
# Run all enhanced tests
pytest tests/test_enhanced_observability.py tests/test_enhanced_integrations.py -v

# Run specific test class
pytest tests/test_enhanced_integrations.py::TestOAuth2Client -v

# Run with coverage
pytest tests/test_enhanced_*.py --cov=src --cov-report=html
```

## 📊 Monitoring Setup

### 1. Prometheus Configuration

Add to `prometheus.yml`:
```yaml
scrape_configs:
  - job_name: 'omnimind-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s
```

### 2. Grafana Dashboard Import

1. Access Grafana UI
2. Navigate to Dashboards → Import
3. Upload `grafana/dashboards/ml-performance-metrics.json`
4. Select Prometheus data source
5. Click Import

### 3. Alert Manager Configuration

The alerts are automatically loaded from `prometheus/alerts/omnimind_alerts.yml`.

## 🔐 Security Features

### 1. OAuth 2.0 Security
- ✅ PKCE (Proof Key for Code Exchange) for enhanced security
- ✅ State parameter for CSRF protection
- ✅ Secure token storage
- ✅ Automatic token refresh

### 2. Webhook Security
- ✅ HMAC-SHA256 signature validation
- ✅ Source allowlist
- ✅ Payload size limits
- ✅ Signature comparison using constant-time algorithm

### 3. Circuit Breaker
- ✅ Prevents cascading failures
- ✅ Automatic recovery testing
- ✅ Configurable thresholds
- ✅ Manual reset capability

## 📈 Performance Considerations

### OpenTelemetry
- Minimal overhead (~1-2% CPU)
- Batch span processing for efficiency
- Configurable sampling rates
- Async export to avoid blocking

### Circuit Breaker
- Lock-based thread safety
- Sliding window for failure tracking
- Configurable timeout and thresholds
- Low memory footprint

### Webhook Framework
- Async processing capability
- Retry with exponential backoff
- Connection pooling (when using enhanced client)
- Request/response timeouts

## 🚀 Production Deployment

### Environment Variables
```bash
# OpenTelemetry
export OTEL_SERVICE_NAME=omnimind
export OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4317

# OAuth (example)
export OAUTH_CLIENT_ID=your-client-id
export OAUTH_CLIENT_SECRET=your-secret

# Webhook
export WEBHOOK_SECRET=your-webhook-secret
```

### Docker Compose Integration
```yaml
services:
  omnimind:
    environment:
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
    depends_on:
      - otel-collector
      
  otel-collector:
    image: otel/opentelemetry-collector:latest
    ports:
      - "4317:4317"  # OTLP gRPC
      - "4318:4318"  # OTLP HTTP
```

## 📝 Migration Guide

### From Basic to Enhanced MCP Client
```python
# Before
from src.integrations import MCPClient
client = MCPClient()

# After
from src.integrations import EnhancedMCPClient
client = EnhancedMCPClient()
# Gains: retry logic, circuit breaker, stats
```

### Adding OpenTelemetry to Existing Code
```python
# 1. Initialize at startup
from src.observability import OpenTelemetryIntegration, OpenTelemetryConfig

config = OpenTelemetryConfig(service_name="omnimind")
otel = OpenTelemetryIntegration(config)
otel.initialize()

# 2. Instrument your code
tracer = otel.get_tracer()
with tracer.start_as_current_span("my_operation"):
    # Your existing code
    pass

# 3. Shutdown at exit
otel.shutdown()
```

## 🎓 Best Practices

### 1. OpenTelemetry
- Use semantic attribute names (e.g., `http.method`, `db.system`)
- Set appropriate sampling rates for production
- Export to dedicated collector, not directly to backend
- Use resource attributes to identify service instances

### 2. Circuit Breaker
- Set failure threshold based on expected error rate
- Use appropriate timeout for service recovery
- Monitor circuit state in production
- Implement fallback strategies

### 3. OAuth 2.0
- Always use PKCE for public clients
- Store refresh tokens securely
- Implement token rotation
- Use appropriate scopes (principle of least privilege)

### 4. Webhooks
- Always validate signatures
- Use HTTPS in production
- Implement idempotency
- Log all webhook events for audit

## 🔗 References

- [OpenTelemetry Python Docs](https://opentelemetry.io/docs/instrumentation/python/)
- [Prometheus Alerting Rules](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/)
- [Grafana Dashboard Best Practices](https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/best-practices/)
- [OAuth 2.0 RFC 6749](https://datatracker.ietf.org/doc/html/rfc6749)
- [PKCE RFC 7636](https://datatracker.ietf.org/doc/html/rfc7636)
- [Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html)

## 📞 Support

For issues or questions:
1. Check existing tests for usage examples
2. Review this documentation
3. Open an issue on GitHub with details and reproduction steps
