# Enterprise Deployment Guide

Complete guide for deploying OmniMind in production environments with high availability, scalability, and monitoring.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Docker Deployment](#docker-deployment)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [Multi-Node Scaling](#multi-node-scaling)
5. [Monitoring & Observability](#monitoring--observability)
6. [Security Best Practices](#security-best-practices)
7. [Backup & Recovery](#backup--recovery)
8. [Performance Tuning](#performance-tuning)

## Prerequisites

### System Requirements

**Minimum:**
- CPU: 4 cores
- RAM: 8 GB
- Disk: 50 GB SSD
- OS: Ubuntu 20.04+ / Debian 11+ / RHEL 8+

**Recommended (Production):**
- CPU: 8+ cores
- RAM: 16+ GB
- Disk: 200+ GB NVMe SSD
- OS: Ubuntu 22.04 LTS
- GPU: NVIDIA GPU with 4GB+ VRAM (optional, for ML workloads)

### Software Requirements

- Docker 24.0+
- Docker Compose 2.20+
- Kubernetes 1.28+ (for K8s deployment)
- kubectl CLI
- Helm 3.12+ (optional, for package management)

## Docker Deployment

### Single-Host Production Deployment

1. **Clone the repository:**
```bash
git clone https://github.com/fabs-devbrain/OmniMind.git
cd OmniMind
```

2. **Configure environment:**
```bash
cp .env.template .env
# Edit .env with your production values
nano .env
```

3. **Build and start services:**
```bash
docker-compose up -d
```

4. **Verify deployment:**
```bash
docker-compose ps
docker-compose logs -f
```

5. **Access the dashboard:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: "3.9"
services:
  backend:
    image: ghcr.io/fabs-devbrain/omnimind/backend:latest
    restart: always
    ports:
      - "8000:8000"
    environment:
      OMNIMIND_ENV: production
      LOG_LEVEL: INFO
    volumes:
      - omnimind-data:/app/data
      - omnimind-logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G

  frontend:
    image: ghcr.io/fabs-devbrain/omnimind/frontend:latest
    restart: always
    ports:
      - "3000:4173"
    environment:
      VITE_API_BASE: http://backend:8000
    depends_on:
      - backend
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:4173"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

volumes:
  omnimind-data:
  omnimind-logs:
```

Deploy:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Kubernetes Deployment

### Prerequisites

1. **Kubernetes cluster setup:**
```bash
# Verify cluster access
kubectl cluster-info
kubectl get nodes
```

2. **Install NGINX Ingress Controller:**
```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml
```

3. **Install cert-manager (for TLS):**
```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

### Deploy OmniMind

1. **Apply base manifests:**
```bash
kubectl apply -f k8s/base/deployment.yaml
```

2. **Verify deployment:**
```bash
kubectl get pods -n omnimind
kubectl get services -n omnimind
kubectl get ingress -n omnimind
```

3. **Check pod logs:**
```bash
kubectl logs -n omnimind -l app=omnimind,component=backend -f
```

### Production Configuration

1. **Update secrets:**
```bash
kubectl create secret generic omnimind-secrets \
  --from-literal=OMNIMIND_DASHBOARD_USER=admin \
  --from-literal=OMNIMIND_DASHBOARD_PASS=<strong-password> \
  -n omnimind --dry-run=client -o yaml | kubectl apply -f -
```

2. **Configure ingress hostname:**
```bash
# Edit k8s/base/deployment.yaml
# Replace omnimind.example.com with your domain
kubectl apply -f k8s/base/deployment.yaml
```

3. **Enable monitoring:**
```bash
kubectl apply -f k8s/monitoring/
```

### Horizontal Pod Autoscaling

The deployment includes HPA configurations:

**Backend HPA:**
- Min replicas: 3
- Max replicas: 10
- CPU threshold: 70%
- Memory threshold: 80%

**Frontend HPA:**
- Min replicas: 2
- Max replicas: 5
- CPU threshold: 70%

Monitor autoscaling:
```bash
kubectl get hpa -n omnimind
kubectl describe hpa omnimind-backend-hpa -n omnimind
```

## Multi-Node Scaling

### Architecture

OmniMind supports distributed task execution across multiple nodes:

```
┌─────────────────────────────────────────┐
│        Load Balancer / Ingress          │
└─────────────┬───────────────────────────┘
              │
    ┌─────────┴─────────┐
    │                   │
┌───▼───┐          ┌───▼───┐
│ Node 1│          │ Node 2│
│ (Coord│          │       │
│ -inator│         │       │
└───┬───┘          └───┬───┘
    │                  │
    └────────┬─────────┘
             │
      ┌──────┴──────┐
      │  Shared     │
      │  Storage    │
      └─────────────┘
```

### Setup Multi-Node Cluster

1. **Initialize coordinator:**
```python
from src.scaling.multi_node import ClusterCoordinator, NodeInfo

# Create coordinator
coordinator = ClusterCoordinator(
    node_id="coordinator-1",
    load_balancing_strategy="least_loaded"
)

# Register worker nodes
coordinator.register_node(NodeInfo(
    node_id="worker-1",
    hostname="worker-1.local",
    ip_address="192.168.1.10",
    port=8000,
    cpu_cores=8,
    memory_gb=16.0,
    max_concurrent_tasks=10,
    capabilities={"cpu_tasks", "io_tasks"}
))

await coordinator.start()
```

2. **Submit distributed tasks:**
```python
from src.scaling.multi_node import DistributedTask

task = DistributedTask(
    task_id="task-001",
    task_type="cpu_intensive",
    payload={"data": "..."},
    priority=5
)

success = coordinator.submit_task(task)
```

3. **Monitor cluster:**
```python
status = coordinator.get_cluster_status()
print(f"Active nodes: {status['active_nodes']}")
print(f"Load: {status['load_percentage']}%")
```

### Load Balancing Strategies

**Least Loaded (Default):**
- Routes tasks to node with lowest load factor
- Best for balanced workload distribution

**Round Robin:**
- Cycles through available nodes
- Predictable distribution pattern

**Random:**
- Randomly selects available nodes
- Useful for testing and development

## Monitoring & Observability

### Prometheus Metrics

OmniMind exposes metrics at `/metrics` endpoint:

**System Metrics:**
- `omnimind_cpu_usage_percent`
- `omnimind_memory_usage_percent`
- `omnimind_disk_usage_percent`

**Application Metrics:**
- `omnimind_tasks_total` (counter)
- `omnimind_tasks_duration_seconds` (histogram)
- `omnimind_api_requests_total` (counter)
- `omnimind_websocket_connections` (gauge)

**Cluster Metrics:**
- `omnimind_cluster_nodes_total`
- `omnimind_cluster_nodes_active`
- `omnimind_cluster_load_percentage`

### Grafana Dashboard

Import dashboard from `k8s/monitoring/grafana-dashboard.json`

Key panels:
- System resource utilization
- API request rates and latency
- Task execution metrics
- WebSocket connection health
- Cluster status overview

### Logging

**Structured logging with levels:**
```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Debug information")
logger.info("Informational message")
logger.warning("Warning condition")
logger.error("Error occurred")
logger.critical("Critical failure")
```

**Centralized logging:**
```bash
# Using ELK stack
kubectl apply -f k8s/monitoring/elasticsearch.yaml
kubectl apply -f k8s/monitoring/fluentd.yaml
kubectl apply -f k8s/monitoring/kibana.yaml
```

## Security Best Practices

### 1. Network Security

**Firewall Configuration:**
```bash
# Allow only necessary ports
ufw allow 22/tcp  # SSH
ufw allow 80/tcp  # HTTP
ufw allow 443/tcp # HTTPS
ufw enable
```

**TLS/SSL Configuration:**
```bash
# Let's Encrypt with cert-manager
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

### 2. Authentication & Authorization

**Basic Auth (Development):**
```bash
# Set credentials
export OMNIMIND_DASHBOARD_USER=admin
export OMNIMIND_DASHBOARD_PASS=<strong-password>
```

**OAuth2 (Production):**
See `docs/OAUTH_SETUP.md` for OAuth2 integration

### 3. Secret Management

**Using Kubernetes Secrets:**
```bash
kubectl create secret generic omnimind-secrets \
  --from-file=credentials.json \
  -n omnimind
```

**Using HashiCorp Vault:**
```bash
# Install Vault CSI driver
helm install vault hashicorp/vault
```

### 4. Image Security

**Scan images for vulnerabilities:**
```bash
docker scan ghcr.io/fabs-devbrain/omnimind/backend:latest
```

**Use minimal base images:**
- Backend: `python:3.12-slim`
- Frontend: `node:18-alpine` → `nginx:alpine`

## Backup & Recovery

### Data Backup

**1. Database backup (if using PostgreSQL/MongoDB):**
```bash
# PostgreSQL
kubectl exec -n omnimind <pod> -- pg_dump > backup.sql

# MongoDB
kubectl exec -n omnimind <pod> -- mongodump --out /backup
```

**2. Persistent volume backup:**
```bash
# Using velero
velero backup create omnimind-backup \
  --include-namespaces omnimind \
  --storage-location default
```

**3. Configuration backup:**
```bash
kubectl get all -n omnimind -o yaml > omnimind-backup.yaml
```

### Disaster Recovery

**1. Restore from backup:**
```bash
velero restore create --from-backup omnimind-backup
```

**2. Verify restoration:**
```bash
kubectl get pods -n omnimind
kubectl logs -n omnimind <pod>
```

**3. Health check:**
```bash
curl http://omnimind.example.com/health
```

## Performance Tuning

### Backend Optimization

**1. Adjust worker processes:**
```bash
# In Dockerfile or k8s manifest
CMD ["uvicorn", "web.backend.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "4"]
```

**2. Enable HTTP/2:**
```yaml
# In nginx ingress annotation
nginx.ingress.kubernetes.io/http2-push-preload: "true"
```

**3. Connection pooling:**
```python
# In application code
from fastapi import FastAPI
app = FastAPI(
    swagger_ui_parameters={"persistAuthorization": True},
    docs_url="/docs"
)
```

### Database Optimization

**1. Index critical fields:**
```sql
CREATE INDEX idx_task_status ON tasks(status);
CREATE INDEX idx_task_created_at ON tasks(created_at);
```

**2. Connection pooling:**
```python
# PostgreSQL with SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True
)
```

### Caching Strategy

**1. Redis for session management:**
```bash
# Install Redis
helm install redis bitnami/redis -n omnimind
```

**2. Application-level caching:**
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_operation(param):
    # Cached result
    pass
```

## Troubleshooting

### Common Issues

**1. Pods in CrashLoopBackOff:**
```bash
kubectl describe pod <pod-name> -n omnimind
kubectl logs <pod-name> -n omnimind --previous
```

**2. High memory usage:**
```bash
# Check resource limits
kubectl top pods -n omnimind

# Adjust limits
kubectl set resources deployment omnimind-backend \
  --limits=memory=4Gi -n omnimind
```

**3. Slow response times:**
```bash
# Check metrics
kubectl port-forward -n omnimind svc/omnimind-backend 8000:8000
curl http://localhost:8000/metrics
```

### Support

- GitHub Issues: https://github.com/fabs-devbrain/OmniMind/issues
- Documentation: https://github.com/fabs-devbrain/OmniMind/docs
- Community: Discord/Slack (links in README)
