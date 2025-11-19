# ✅ Guia de Validação - Sprint 1

**Data:** 2025-11-19  
**Objetivo:** Validar todas as 6 implementações do Sprint 1  
**Tempo Estimado:** 30-45 minutos

---

## 🎯 Pré-requisitos

Antes de começar, certifique-se de ter:
- [ ] Docker e Docker Compose instalados
- [ ] Python 3.12+ instalado
- [ ] kubectl configurado (para testes Kubernetes)
- [ ] Acesso ao repositório OmniMind

---

## 1️⃣ Validar Redis Cluster Manager

### Teste 1.1: Docker Compose
```bash
# Iniciar cluster (6 nós)
docker-compose -f docker-compose.redis.yml up -d

# Aguardar inicialização (10 segundos)
sleep 10

# Verificar nós
docker ps | grep redis-node

# Deve mostrar 6 containers rodando
```

### Teste 1.2: Cluster Health
```bash
# Verificar cluster
docker exec redis-node-1 redis-cli --cluster check localhost:7000

# Esperado:
# - 3 masters
# - 3 replicas
# - 16384 slots assigned
# - All nodes healthy
```

### Teste 1.3: Python Integration
```bash
cd /home/runner/work/OmniMind/OmniMind

# Testar import
python -c "from src.scaling import RedisClusterManager; print('✅ Import OK')"

# Testar conexão
python << 'EOF'
from src.scaling import RedisClusterManager

# Criar manager
manager = RedisClusterManager([{"host": "localhost", "port": 7000}])

# Testar operações
manager.set("test_key", "test_value", ttl=60)
value = manager.get("test_key")
print(f"✅ Get/Set OK: {value}")

# Health check
health = manager.get_cluster_health()
print(f"✅ Health: {health.state.value}")
print(f"✅ Slots: {health.slots_assigned}/16384")

# Stats
stats = manager.get_stats()
print(f"✅ Stats: {stats}")
EOF
```

**Resultado Esperado:**
```
✅ Import OK
✅ Get/Set OK: test_value
✅ Health: ok
✅ Slots: 16384/16384
✅ Stats: {'hits': 1, 'misses': 0, 'sets': 1, ...}
```

### Cleanup
```bash
docker-compose -f docker-compose.redis.yml down -v
```

---

## 2️⃣ Validar Compression Middleware

### Teste 2.1: Import
```bash
# Testar imports
python << 'EOF'
from web.backend.middleware import CompressionMiddleware, get_compression_stats
from web.backend.utils.image_optimizer import ImageOptimizer

print("✅ Compression imports OK")
print("✅ Image optimizer import OK")
EOF
```

### Teste 2.2: Compression Stats
```bash
python << 'EOF'
from web.backend.middleware import get_compression_stats

# Simular compression
original = 10000
compressed = 3000

stats = get_compression_stats(original, compressed)
print(f"✅ Original: {stats['original_size']} bytes")
print(f"✅ Compressed: {stats['compressed_size']} bytes")
print(f"✅ Savings: {stats['savings_percent']:.1f}%")
print(f"✅ Ratio: {stats['compression_ratio']:.2f}")
EOF
```

**Resultado Esperado:**
```
✅ Original: 10000 bytes
✅ Compressed: 3000 bytes
✅ Savings: 70.0%
✅ Ratio: 0.30
```

### Teste 2.3: Image Optimizer (Opcional)
```bash
# Requer PIL/Pillow instalado
pip install Pillow

python << 'EOF'
from web.backend.utils.image_optimizer import ImageOptimizer

optimizer = ImageOptimizer(default_quality=85)

# Criar imagem de teste simples
from PIL import Image
import io

# Criar imagem 100x100 RGB
img = Image.new('RGB', (100, 100), color='red')
buffer = io.BytesIO()
img.save(buffer, format='JPEG')
jpeg_bytes = buffer.getvalue()

print(f"✅ Original JPEG: {len(jpeg_bytes)} bytes")

# Converter para WebP
webp_bytes = optimizer.to_webp(jpeg_bytes, quality=85)
print(f"✅ WebP: {len(webp_bytes)} bytes")
print(f"✅ Reduction: {100 - (len(webp_bytes)/len(jpeg_bytes)*100):.1f}%")
EOF
```

---

## 3️⃣ Validar Backend Dockerfile

### Teste 3.1: Build
```bash
cd /home/runner/work/OmniMind/OmniMind

# Build imagem
docker build -t omnimind/backend:sprint1 -f web/backend/Dockerfile .

# Verificar tamanho
docker images | grep omnimind/backend

# Deve ser < 500 MB (idealmente ~250 MB)
```

### Teste 3.2: Run Container
```bash
# Rodar container
docker run -d \
  --name omnimind-backend-test \
  -p 8001:8000 \
  omnimind/backend:sprint1

# Aguardar inicialização
sleep 5

# Testar health check
curl http://localhost:8001/health

# Deve retornar JSON com status
```

### Teste 3.3: Verificar Non-Root
```bash
# Verificar usuário
docker exec omnimind-backend-test whoami

# Deve retornar: omnimind (não root)
```

### Cleanup
```bash
docker stop omnimind-backend-test
docker rm omnimind-backend-test
```

---

## 4️⃣ Validar Network Policies

### Teste 4.1: Syntax Check
```bash
# Validar YAML
kubectl apply -f k8s/security/network-policies.yaml --dry-run=client

# Não deve mostrar erros
```

### Teste 4.2: Apply (em cluster de teste)
```bash
# Aplicar policies
kubectl apply -f k8s/security/network-policies.yaml

# Verificar
kubectl get networkpolicies -n omnimind

# Deve mostrar:
# - default-deny-ingress
# - default-deny-egress
# - allow-frontend-to-backend
# - allow-ingress-to-backend
# - allow-ingress-to-frontend
# - allow-dns-access
# - allow-same-namespace
```

### Teste 4.3: Describe
```bash
# Ver detalhes
kubectl describe networkpolicy default-deny-ingress -n omnimind

# Verificar policyTypes e rules
```

---

## 5️⃣ Validar Pod Disruption Budgets

### Teste 5.1: Syntax Check
```bash
# Validar YAML
kubectl apply -f k8s/availability/pod-disruption-budgets.yaml --dry-run=client

# Não deve mostrar erros
```

### Teste 5.2: Apply (em cluster de teste)
```bash
# Aplicar PDBs
kubectl apply -f k8s/availability/pod-disruption-budgets.yaml

# Verificar
kubectl get pdb -n omnimind

# Deve mostrar:
# - omnimind-backend-pdb (minAvailable: 2)
# - omnimind-frontend-pdb (minAvailable: 1)
```

### Teste 5.3: Describe
```bash
# Ver detalhes
kubectl describe pdb omnimind-backend-pdb -n omnimind

# Verificar:
# - Min Available: 2
# - Selector: component=backend
```

---

## 6️⃣ Validar Grafana + Prometheus

### Teste 6.1: Docker Compose
```bash
# Iniciar stack
docker-compose -f docker-compose.monitoring.yml up -d

# Aguardar inicialização (15 segundos)
sleep 15

# Verificar containers
docker ps | grep -E "(prometheus|grafana|alertmanager)"

# Deve mostrar 3 containers
```

### Teste 6.2: Prometheus
```bash
# Testar Prometheus
curl http://localhost:9090/-/healthy

# Deve retornar: Prometheus is Healthy.

# Ver targets
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets | length'

# Deve retornar número > 0
```

### Teste 6.3: Grafana
```bash
# Testar Grafana
curl http://localhost:3000/api/health

# Deve retornar JSON com status ok

# Verificar dashboards provisionados
curl -u admin:omnimind http://localhost:3000/api/search?type=dash-db | jq '.'

# Deve mostrar dashboards
```

### Teste 6.4: UI (Manual)
```bash
# Abrir Grafana no browser
# http://localhost:3000

# Login: admin / omnimind

# Verificar:
# - Dashboards aparecem
# - Prometheus datasource configurado
# - Métricas carregando (se backend rodando)
```

### Cleanup
```bash
docker-compose -f docker-compose.monitoring.yml down -v
```

---

## 📊 Checklist de Validação

Marque cada teste conforme completar:

### Redis Cluster Manager:
- [ ] Docker Compose rodando
- [ ] Cluster health OK
- [ ] Python integration funcionando
- [ ] Get/Set operacional
- [ ] Stats disponíveis

### Compression:
- [ ] Imports OK
- [ ] Compression stats corretos
- [ ] Image optimizer funcional (opcional)

### Backend Dockerfile:
- [ ] Build sucesso
- [ ] Imagem < 500 MB
- [ ] Container roda
- [ ] Health check responde
- [ ] Non-root user confirmado

### Network Policies:
- [ ] YAML válido
- [ ] Apply sem erros
- [ ] Todas policies criadas
- [ ] Describe mostra configuração

### Pod Disruption Budgets:
- [ ] YAML válido
- [ ] Apply sem erros
- [ ] PDBs criados
- [ ] MinAvailable configurado

### Grafana + Prometheus:
- [ ] Stack rodando
- [ ] Prometheus healthy
- [ ] Grafana acessível
- [ ] Dashboards carregam
- [ ] Datasource configurado

---

## ✅ Resultado Esperado

Se todos os testes passarem:

```
╔══════════════════════════════════════════════════════════╗
║           SPRINT 1 VALIDATION RESULTS                    ║
╠══════════════════════════════════════════════════════════╣
║                                                           ║
║  ✅ Redis Cluster Manager        PASS                    ║
║  ✅ Compression Middleware        PASS                    ║
║  ✅ Backend Dockerfile            PASS                    ║
║  ✅ Network Policies              PASS                    ║
║  ✅ Pod Disruption Budgets        PASS                    ║
║  ✅ Grafana + Prometheus          PASS                    ║
║                                                           ║
║  Status: ALL TESTS PASSED ✅                             ║
║  System: PRODUCTION-READY 🚀                             ║
║                                                           ║
╚══════════════════════════════════════════════════════════╝
```

---

## 🔧 Troubleshooting

### Redis Cluster não inicia:
```bash
# Verificar logs
docker logs redis-node-1

# Limpar e reiniciar
docker-compose -f docker-compose.redis.yml down -v
docker-compose -f docker-compose.redis.yml up -d
```

### Compression não importa:
```bash
# Verificar PYTHONPATH
export PYTHONPATH=/home/runner/work/OmniMind/OmniMind:$PYTHONPATH

# Instalar dependências
pip install brotli Pillow
```

### Docker build falha:
```bash
# Verificar requirements.txt existe
ls requirements.txt

# Build com logs detalhados
docker build -t omnimind/backend:sprint1 -f web/backend/Dockerfile . --progress=plain
```

### Kubernetes apply falha:
```bash
# Verificar namespace existe
kubectl create namespace omnimind

# Aplicar novamente
kubectl apply -f k8s/security/network-policies.yaml
```

### Grafana não acessível:
```bash
# Verificar porta não está em uso
netstat -an | grep 3000

# Reiniciar stack
docker-compose -f docker-compose.monitoring.yml restart grafana
```

---

## 📞 Suporte

Se encontrar problemas:
1. Verificar logs: `docker logs <container>`
2. Verificar documentação específica
3. Revisar pré-requisitos
4. Consultar troubleshooting acima

---

**Guia criado em:** 2025-11-19  
**Tempo estimado:** 30-45 minutos  
**Dificuldade:** Fácil  
**Status:** Pronto para uso
