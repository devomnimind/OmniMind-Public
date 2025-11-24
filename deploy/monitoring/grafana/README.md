# Grafana Dashboards for OmniMind

This directory contains Grafana dashboards and provisioning configurations for monitoring OmniMind.

## 📊 Available Dashboards

### 1. System Metrics Dashboard
**File:** `dashboards/system-metrics.json`

Monitors infrastructure-level metrics:
- CPU Usage (per instance)
- Memory Usage (MB)
- Disk I/O (read/write rates)
- Network Traffic (rx/tx rates)
- GPU Utilization (if available)

### 2. Application Metrics Dashboard
**File:** `dashboards/application-metrics.json`

Monitors application-level metrics:
- Request Rate (requests/sec)
- Response Time (p50, p95, p99 percentiles)
- Error Rate (4xx, 5xx errors)
- Active Connections
- Cache Hit Rate
- Throughput

### 3. Business Metrics Dashboard
**File:** `dashboards/business-metrics.json` (to be created)

Would monitor business-level metrics:
- Tasks Processed
- Agent Utilization
- Success Rate
- Processing Time Distribution

### 4. Multi-Modal Dashboard
**File:** `dashboards/multimodal-metrics.json` (to be created)

Would monitor multi-modal AI metrics:
- Vision Processing Operations
- Audio Processing Operations
- Fusion Operations
- Embodied Intelligence Actions

## 🚀 Quick Start

### Using Docker Compose

```bash
# Start monitoring stack (Prometheus + Grafana)
docker-compose -f docker-compose.monitoring.yml up -d

# Access Grafana
open http://localhost:3000

# Default credentials:
# Username: admin
# Password: omnimind

# Access Prometheus
open http://localhost:9090
```

### Manual Setup

1. **Start Prometheus:**
```bash
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v $(pwd)/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

2. **Start Grafana:**
```bash
docker run -d \
  --name=grafana \
  -p 3000:3000 \
  -v $(pwd)/grafana/provisioning:/etc/grafana/provisioning \
  -v $(pwd)/grafana/dashboards:/etc/grafana/dashboards \
  -e "GF_SECURITY_ADMIN_PASSWORD=omnimind" \
  grafana/grafana
```

3. **Access Dashboards:**
- Open http://localhost:3000
- Login with admin/omnimind
- Dashboards will be auto-loaded

## 📁 Directory Structure

```
grafana/
├── README.md                           # This file
├── dashboards/                         # Dashboard JSON files
│   ├── system-metrics.json            # System infrastructure
│   └── application-metrics.json       # Application performance
├── provisioning/
│   ├── datasources/
│   │   └── prometheus.yaml            # Prometheus datasource config
│   └── dashboards/
│       └── dashboards.yaml            # Dashboard provisioning config
```

## 🔧 Configuration

### Datasource Configuration

Edit `provisioning/datasources/prometheus.yaml` to change Prometheus URL:

```yaml
datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090  # Change this
```

### Dashboard Auto-Loading

Dashboards are automatically loaded from `dashboards/*.json` on Grafana startup.

To add new dashboards:
1. Create JSON file in `dashboards/`
2. Restart Grafana or wait for auto-reload

### Customization

Dashboards can be edited directly in Grafana UI:
1. Open dashboard
2. Click "Dashboard settings" (gear icon)
3. Edit as needed
4. Export JSON to save changes

## 📊 Metrics Reference

### System Metrics

| Metric | Description | Unit |
|--------|-------------|------|
| `process_cpu_seconds_total` | CPU time used | seconds |
| `process_resident_memory_bytes` | Memory usage | bytes |
| `node_disk_read_bytes_total` | Disk read | bytes |
| `node_disk_written_bytes_total` | Disk write | bytes |
| `node_network_receive_bytes_total` | Network RX | bytes |
| `node_network_transmit_bytes_total` | Network TX | bytes |
| `omnimind_gpu_utilization` | GPU usage | percent |

### Application Metrics

| Metric | Description | Unit |
|--------|-------------|------|
| `http_requests_total` | Total HTTP requests | count |
| `http_request_duration_seconds` | Request latency | seconds |
| `omnimind_active_connections` | Active connections | count |
| `omnimind_cache_hits_total` | Cache hits | count |
| `omnimind_cache_misses_total` | Cache misses | count |

## 🎯 Best Practices

### 1. Dashboard Organization
- Use folders to organize dashboards by category
- Tag dashboards for easy searching
- Use consistent naming conventions

### 2. Panel Design
- Set appropriate time ranges
- Use percentiles (p50, p95, p99) for latency
- Add alert thresholds visually

### 3. Performance
- Limit query time range for heavy queries
- Use dashboard variables for filtering
- Cache dashboard JSON for faster load

### 4. Alerts
- Configure alerts in Prometheus alert rules
- Use Grafana only for visualization
- Set up notification channels (Slack, PagerDuty)

## 🔍 Troubleshooting

### Dashboards Not Loading

Check Grafana logs:
```bash
docker logs omnimind-grafana
```

Verify provisioning:
```bash
docker exec omnimind-grafana ls -la /etc/grafana/provisioning/dashboards
```

### No Data in Panels

Check Prometheus is scraping:
```bash
# Visit Prometheus UI
open http://localhost:9090/targets

# Verify metrics exist
curl http://localhost:9090/api/v1/label/__name__/values | jq
```

Check backend is exposing metrics:
```bash
curl http://localhost:8000/metrics
```

### Slow Dashboard Loading

- Reduce time range (e.g., last 15m instead of 24h)
- Simplify queries (use recording rules)
- Increase Prometheus memory

## 📞 Support

For issues or questions:
1. Check Grafana docs: https://grafana.com/docs/
2. Check Prometheus docs: https://prometheus.io/docs/
3. Review logs: `docker logs omnimind-grafana`
4. Verify metrics endpoint: http://localhost:8000/metrics

## 🔄 Updates

To update dashboards:
```bash
# Pull latest dashboards
git pull

# Restart Grafana to reload
docker-compose -f docker-compose.monitoring.yml restart grafana
```

## 📝 License

Same as OmniMind project license.
