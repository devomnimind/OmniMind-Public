# 🎯 Plano de Ação - Pendências Média Prioridade

**Data:** 2025-11-19  
**Objetivo:** Completar os 9 items restantes das pendências média prioridade  
**Estimativa Total:** 56-80 horas (~2 semanas)  
**Status Atual:** 3/4 com base implementada, 1/4 completo

---

## 📋 Executive Summary

**Situação Atual:**
- ✅ **Phase 12 Multi-Modal:** 100% COMPLETO (105 tests passing)
- ✅ **Containerization:** 70% implementado (base completa)
- ✅ **Monitoring:** 60% implementado (framework completo)
- ✅ **Performance:** 65% implementado (otimizações básicas)

**O Que Fazer:**
- Completar 30% de Containerization (Service Mesh, Network Policies)
- Completar 40% de Monitoring (Grafana, Alertas ML, Integrações)
- Completar 35% de Performance (Redis Cluster, CDN, Compression)

**Priorização:**
1. **Alta:** Monitoring + Performance (impacto imediato)
2. **Média:** Containerization avançado (produção enterprise)
3. **Baixa:** Melhorias opcionais

---

## 🚀 Sprint 1 - Alta Prioridade (2 semanas)

### Objetivo
Implementar funcionalidades com maior impacto imediato em produção.

### Tasks

#### 1.1 Grafana Dashboards (8h) - ALTA
**Prioridade:** P0  
**Impacto:** Visualização em tempo real de todas as métricas

**Implementação:**
```yaml
Dashboards a criar:
1. System Metrics Dashboard
   - CPU/Memory/Disk usage
   - Network I/O
   - GPU utilization
   
2. Application Metrics Dashboard
   - Request latency (p50, p95, p99)
   - Throughput (req/s)
   - Error rate
   - Active connections
   
3. Business Metrics Dashboard
   - Tasks processed
   - Agent utilization
   - Success rate
   - Processing time distribution
   
4. Multi-Modal Dashboard
   - Vision processing metrics
   - Audio processing metrics
   - Fusion operations
   - Embodied intelligence actions
```

**Arquivos a criar:**
```
grafana/
├── dashboards/
│   ├── system-metrics.json
│   ├── application-metrics.json
│   ├── business-metrics.json
│   └── multimodal-metrics.json
├── provisioning/
│   ├── datasources.yaml
│   └── dashboards.yaml
└── README.md
```

**Acceptance Criteria:**
- [ ] Todos os 4 dashboards funcionais
- [ ] Auto-refresh configurado
- [ ] Alertas visuais em valores críticos
- [ ] Exportação de dashboards em JSON
- [ ] Documentação de uso

**Validação:**
```bash
# Iniciar Grafana
docker-compose -f docker-compose.monitoring.yml up -d

# Acessar dashboards
open http://localhost:3000/dashboards

# Verificar datasource Prometheus
curl http://localhost:3000/api/datasources
```

---

#### 1.2 Redis Cluster (8h) - ALTA
**Prioridade:** P0  
**Impacto:** Cache distribuído para escala horizontal

**Implementação:**
```yaml
Configuração:
- 3 master nodes
- 3 replica nodes (1 por master)
- Sharding automático (hash slots)
- Replication assíncrona
- Sentinel para failover
```

**Arquivos a criar:**
```
config/redis/
├── redis-cluster.conf          # Cluster configuration
├── redis-sentinel.conf         # Sentinel configuration
└── cluster-init.sh            # Initialization script

docker/
└── docker-compose.redis.yml   # Redis Cluster compose

src/scaling/
└── redis_cluster_manager.py   # Python integration
```

**Redis Cluster Manager (src/scaling/redis_cluster_manager.py):**
```python
"""
Redis Cluster Manager for distributed caching.

Features:
- Automatic sharding
- Master-replica replication
- Sentinel-based failover
- Connection pooling
- Health monitoring
"""

from typing import Dict, List, Optional, Any
import redis
from redis.cluster import RedisCluster
from redis.sentinel import Sentinel
import logging

logger = logging.getLogger(__name__)


class RedisClusterManager:
    """Manages Redis Cluster operations."""
    
    def __init__(
        self,
        nodes: List[Dict[str, Any]],
        sentinel_nodes: Optional[List[tuple]] = None,
        password: Optional[str] = None,
        max_connections: int = 50
    ):
        """Initialize Redis Cluster manager."""
        self.nodes = nodes
        self.sentinel_nodes = sentinel_nodes
        self.password = password
        
        # Initialize cluster
        self.cluster = RedisCluster(
            startup_nodes=nodes,
            decode_responses=True,
            skip_full_coverage_check=False,
            max_connections=max_connections,
            password=password
        )
        
        # Initialize sentinel if provided
        self.sentinel = None
        if sentinel_nodes:
            self.sentinel = Sentinel(
                sentinel_nodes,
                socket_timeout=0.1,
                password=password
            )
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set key-value with optional TTL."""
        try:
            if ttl:
                return self.cluster.setex(key, ttl, value)
            return self.cluster.set(key, value)
        except Exception as e:
            logger.error(f"Failed to set {key}: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get value by key."""
        try:
            return self.cluster.get(key)
        except Exception as e:
            logger.error(f"Failed to get {key}: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete key."""
        try:
            return bool(self.cluster.delete(key))
        except Exception as e:
            logger.error(f"Failed to delete {key}: {e}")
            return False
    
    def get_cluster_info(self) -> Dict[str, Any]:
        """Get cluster information."""
        info = {
            "nodes": [],
            "slots_assigned": 0,
            "state": "unknown"
        }
        
        try:
            cluster_info = self.cluster.cluster_info()
            info["state"] = cluster_info.get("cluster_state", "unknown")
            info["slots_assigned"] = cluster_info.get("cluster_slots_assigned", 0)
            
            nodes_info = self.cluster.cluster_nodes()
            for node in nodes_info.split('\n'):
                if node.strip():
                    info["nodes"].append(node)
            
        except Exception as e:
            logger.error(f"Failed to get cluster info: {e}")
        
        return info
    
    def health_check(self) -> bool:
        """Check cluster health."""
        try:
            info = self.get_cluster_info()
            return info["state"] == "ok" and info["slots_assigned"] == 16384
        except:
            return False
```

**Acceptance Criteria:**
- [ ] Cluster de 6 nós funcionando
- [ ] Sharding automático ativo
- [ ] Replicação funcionando
- [ ] Sentinel detecta falhas
- [ ] Failover automático testado
- [ ] Integration com multi_level_cache.py
- [ ] Testes de carga (1000+ req/s)

**Validação:**
```bash
# Iniciar cluster
bash config/redis/cluster-init.sh

# Verificar cluster
redis-cli --cluster check localhost:7000

# Testar failover
redis-cli -p 7000 DEBUG SEGFAULT
# Verificar que replica assume

# Testar Python integration
python -c "from src.scaling.redis_cluster_manager import RedisClusterManager; \
  rcm = RedisClusterManager([{'host':'localhost','port':7000}]); \
  rcm.set('test', 'value'); \
  print(rcm.get('test'))"
```

---

#### 1.3 Compression Avançada (4h) - ALTA
**Prioridade:** P1  
**Impacto:** Redução de 30-50% no tráfego de rede

**Implementação:**

**Arquivos a criar:**
```
web/backend/middleware/
└── compression.py             # Compression middleware

web/backend/utils/
└── image_optimizer.py         # WebP conversion

config/
└── compression.yaml           # Compression config
```

**Compression Middleware (web/backend/middleware/compression.py):**
```python
"""
Advanced compression middleware for FastAPI.

Features:
- Brotli compression (better than gzip)
- Content-type aware compression
- Streaming compression
- Quality tuning
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import brotli
import gzip
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class CompressionMiddleware(BaseHTTPMiddleware):
    """Advanced compression middleware."""
    
    def __init__(
        self,
        app,
        minimum_size: int = 500,  # bytes
        brotli_quality: int = 4,  # 0-11 (4 = fast, good compression)
        gzip_level: int = 6,      # 1-9
        compressible_types: Optional[set] = None
    ):
        super().__init__(app)
        self.minimum_size = minimum_size
        self.brotli_quality = brotli_quality
        self.gzip_level = gzip_level
        
        self.compressible_types = compressible_types or {
            "text/html",
            "text/css",
            "text/javascript",
            "application/javascript",
            "application/json",
            "application/xml",
            "text/xml",
            "image/svg+xml"
        }
    
    async def dispatch(self, request: Request, call_next):
        """Process request with compression."""
        response = await call_next(request)
        
        # Skip if already compressed
        if "content-encoding" in response.headers:
            return response
        
        # Skip small responses
        if int(response.headers.get("content-length", 0)) < self.minimum_size:
            return response
        
        # Check content type
        content_type = response.headers.get("content-type", "").split(";")[0]
        if content_type not in self.compressible_types:
            return response
        
        # Get accept-encoding
        accept_encoding = request.headers.get("accept-encoding", "")
        
        # Compress with Brotli if supported
        if "br" in accept_encoding:
            return self._compress_brotli(response)
        
        # Fallback to gzip
        if "gzip" in accept_encoding:
            return self._compress_gzip(response)
        
        return response
    
    def _compress_brotli(self, response: Response) -> Response:
        """Compress response with Brotli."""
        try:
            # Get response body
            body = b"".join([chunk async for chunk in response.body_iterator])
            
            # Compress
            compressed = brotli.compress(body, quality=self.brotli_quality)
            
            # Update response
            response.headers["content-encoding"] = "br"
            response.headers["content-length"] = str(len(compressed))
            response.body = compressed
            
            logger.debug(
                f"Brotli: {len(body)} → {len(compressed)} bytes "
                f"({100 - len(compressed)/len(body)*100:.1f}% reduction)"
            )
            
        except Exception as e:
            logger.error(f"Brotli compression failed: {e}")
        
        return response
    
    def _compress_gzip(self, response: Response) -> Response:
        """Compress response with gzip."""
        try:
            # Get response body
            body = b"".join([chunk async for chunk in response.body_iterator])
            
            # Compress
            compressed = gzip.compress(body, compresslevel=self.gzip_level)
            
            # Update response
            response.headers["content-encoding"] = "gzip"
            response.headers["content-length"] = str(len(compressed))
            response.body = compressed
            
            logger.debug(
                f"Gzip: {len(body)} → {len(compressed)} bytes "
                f"({100 - len(compressed)/len(body)*100:.1f}% reduction)"
            )
            
        except Exception as e:
            logger.error(f"Gzip compression failed: {e}")
        
        return response
```

**Image Optimizer (web/backend/utils/image_optimizer.py):**
```python
"""
Image optimization utilities.

Features:
- WebP conversion
- Quality optimization
- Resize support
- Metadata stripping
"""

from PIL import Image
import io
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class ImageOptimizer:
    """Optimizes images for web delivery."""
    
    def __init__(self, default_quality: int = 85):
        self.default_quality = default_quality
    
    def to_webp(
        self,
        image_bytes: bytes,
        quality: Optional[int] = None,
        resize: Optional[Tuple[int, int]] = None
    ) -> bytes:
        """Convert image to WebP format."""
        quality = quality or self.default_quality
        
        try:
            # Open image
            img = Image.open(io.BytesIO(image_bytes))
            
            # Resize if requested
            if resize:
                img = img.resize(resize, Image.Resampling.LANCZOS)
            
            # Convert to WebP
            output = io.BytesIO()
            img.save(
                output,
                format="WEBP",
                quality=quality,
                method=6  # Best compression
            )
            
            webp_bytes = output.getvalue()
            
            reduction = 100 - (len(webp_bytes) / len(image_bytes) * 100)
            logger.info(
                f"WebP conversion: {len(image_bytes)} → {len(webp_bytes)} bytes "
                f"({reduction:.1f}% reduction)"
            )
            
            return webp_bytes
            
        except Exception as e:
            logger.error(f"WebP conversion failed: {e}")
            return image_bytes
    
    def optimize_jpeg(
        self,
        image_bytes: bytes,
        quality: Optional[int] = None
    ) -> bytes:
        """Optimize JPEG image."""
        quality = quality or self.default_quality
        
        try:
            img = Image.open(io.BytesIO(image_bytes))
            output = io.BytesIO()
            
            img.save(
                output,
                format="JPEG",
                quality=quality,
                optimize=True,
                progressive=True
            )
            
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"JPEG optimization failed: {e}")
            return image_bytes
```

**Integration no FastAPI (web/backend/main.py):**
```python
from web.backend.middleware.compression import CompressionMiddleware

# Add middleware
app.add_middleware(
    CompressionMiddleware,
    minimum_size=500,
    brotli_quality=4,
    gzip_level=6
)
```

**Acceptance Criteria:**
- [ ] Brotli compression funcionando
- [ ] Gzip fallback funcionando
- [ ] WebP conversion API endpoint
- [ ] Compression automático em responses
- [ ] Métricas de compression rate
- [ ] Testes de performance

**Validação:**
```bash
# Testar compression
curl -H "Accept-Encoding: br" http://localhost:8000/api/status -v | grep "content-encoding: br"

# Testar WebP
curl -X POST http://localhost:8000/api/image/optimize \
  -F "file=@test.jpg" \
  -F "format=webp" \
  -o test.webp

# Verificar tamanho
ls -lh test.jpg test.webp
```

---

#### 1.4 Backend Multi-Stage Build (2h) - ALTA
**Prioridade:** P1  
**Impacto:** Imagem Docker 50% menor

**Implementação:**

**Novo Dockerfile (web/backend/Dockerfile):**
```dockerfile
# Stage 1: Builder
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Update PATH
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app

# Create non-root user
RUN useradd -m -u 1000 omnimind && \
    chown -R omnimind:omnimind /app

USER omnimind

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Production command (no reload)
CMD ["uvicorn", "web.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Acceptance Criteria:**
- [ ] Build multi-stage funcionando
- [ ] Imagem final < 500MB
- [ ] Non-root user
- [ ] Health check funcionando
- [ ] Production mode (sem reload)

**Validação:**
```bash
# Build
docker build -t omnimind/backend:latest -f web/backend/Dockerfile .

# Verificar tamanho
docker images | grep omnimind/backend

# Testar
docker run -p 8000:8000 omnimind/backend:latest

# Verificar health
curl http://localhost:8000/health
```

---

#### 1.5 Network Policies (4h) - ALTA
**Prioridade:** P1  
**Impacto:** Segurança de rede em produção

**Implementação:**

**Arquivo:** `k8s/security/network-policies.yaml`
```yaml
# Default deny all ingress
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: omnimind
spec:
  podSelector: {}
  policyTypes:
  - Ingress

---
# Allow backend ingress from frontend
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
  namespace: omnimind
spec:
  podSelector:
    matchLabels:
      component: backend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          component: frontend
    ports:
    - protocol: TCP
      port: 8000

---
# Allow backend ingress from ingress controller
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-ingress-to-backend
  namespace: omnimind
spec:
  podSelector:
    matchLabels:
      component: backend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000

---
# Allow frontend ingress from ingress controller
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-ingress-to-frontend
  namespace: omnimind
spec:
  podSelector:
    matchLabels:
      component: frontend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 4173

---
# Allow DNS
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns
  namespace: omnimind
spec:
  podSelector: {}
  policyTypes:
  - Egress
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    - podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53
```

**Acceptance Criteria:**
- [ ] Default deny all funcionando
- [ ] Frontend → Backend permitido
- [ ] Ingress → Services permitido
- [ ] DNS funcionando
- [ ] Testes de conectividade

**Validação:**
```bash
# Aplicar policies
kubectl apply -f k8s/security/network-policies.yaml

# Testar conectividade
kubectl run test-pod --image=busybox -n omnimind -- sleep 3600

# Tentar acessar backend (deve falhar)
kubectl exec test-pod -n omnimind -- wget -O- http://omnimind-backend:8000/health

# Verificar policies
kubectl get networkpolicies -n omnimind
kubectl describe networkpolicy allow-frontend-to-backend -n omnimind
```

---

#### 1.6 Pod Disruption Budgets (2h) - ALTA
**Prioridade:** P2  
**Impacto:** Availability durante updates

**Implementação:**

**Arquivo:** `k8s/availability/pod-disruption-budgets.yaml`
```yaml
# Backend PDB
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: omnimind-backend-pdb
  namespace: omnimind
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: omnimind
      component: backend

---
# Frontend PDB
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: omnimind-frontend-pdb
  namespace: omnimind
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: omnimind
      component: frontend
```

**Acceptance Criteria:**
- [ ] PDBs aplicados
- [ ] Rolling update respeitando minAvailable
- [ ] Drain respeitando budgets

**Validação:**
```bash
# Aplicar PDBs
kubectl apply -f k8s/availability/pod-disruption-budgets.yaml

# Verificar
kubectl get pdb -n omnimind

# Testar drain (em node de teste)
kubectl drain <node-name> --ignore-daemonsets
# Verificar que minAvailable é respeitado

kubectl uncordon <node-name>
```

---

### Sprint 1 Summary

**Total Estimado:** 28 horas  
**Tarefas:** 6 items  
**Impacto:** Alta prioridade, produção enterprise

**Entregáveis:**
1. ✅ 4 Grafana dashboards funcionais
2. ✅ Redis Cluster com 6 nós
3. ✅ Compression (Brotli + WebP)
4. ✅ Backend Dockerfile otimizado
5. ✅ Network Policies implementadas
6. ✅ Pod Disruption Budgets configurados

---

## 🔄 Sprint 2 - Média Prioridade (2 semanas)

### Objetivo
Implementar integrações externas e melhorias de performance.

### Tasks (resumido)

1. **Slack Integration (4h)**
   - Webhook notifications
   - Alert routing
   - Incident updates

2. **PagerDuty Integration (6h)**
   - Incident creation
   - Escalation policies
   - On-call rotation

3. **CDN Integration (6h)**
   - Cloudflare/AWS CloudFront
   - Asset optimization
   - Cache invalidation

4. **Query Optimization (8h)**
   - Query analyzer
   - Index advisor
   - Slow query detector

5. **Service Mesh POC (8h)**
   - Istio installation
   - Traffic management
   - Observability

**Total:** 32 horas

---

## 📊 Sprint 3+ - Baixa Prioridade (4 semanas)

### Objetivo
Implementar melhorias avançadas e otimizações de longo prazo.

### Tasks (resumido)

1. **Alertas ML-based (16h)**
2. **SLA Tracking (4h)**
3. **Análise Preditiva (12h)**
4. **Lazy Loading (4h)**
5. **Predictive Prefetching (12h)**
6. **Vault Integration (8h)**
7. **Resource Quotas (2h)**
8. **Advanced ConfigMaps (4h)**

**Total:** 62 horas

---

## ✅ Critérios de Sucesso

### Sprint 1
- [ ] Todos os dashboards Grafana acessíveis
- [ ] Redis Cluster passando health checks
- [ ] Compression ativa (verificar headers)
- [ ] Backend Docker image < 500MB
- [ ] Network policies aplicadas
- [ ] PDBs funcionais

### Sprint 2
- [ ] Alertas chegando no Slack
- [ ] Incidentes criados no PagerDuty
- [ ] Assets servidos via CDN
- [ ] Queries otimizadas (índices criados)
- [ ] Istio instalado e funcional

### Sprint 3+
- [ ] Alertas ML detectando anomalias
- [ ] SLA metrics sendo rastreados
- [ ] Predições de falha funcionando
- [ ] Lazy loading ativo no frontend
- [ ] Vault gerenciando secrets

---

## 📞 Contatos e Escalações

**Para questões técnicas:**
- Consultar documentação em `docs/`
- Verificar testes existentes
- Revisar logs em `logs/`

**Para aprovações:**
- Sprint 1: Aprovação automática (alta prioridade)
- Sprint 2: Review antes de implementar
- Sprint 3+: Validar necessidade antes

---

**Documento criado em:** 2025-11-19  
**Owner:** OmniMind Development Team  
**Status:** Ready for execution  
**Próxima revisão:** Após Sprint 1
