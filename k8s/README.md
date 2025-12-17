# Implantação Kubernetes

Este diretório contém manifests Kubernetes para implantar OmniMind em produção.

## Estrutura de Diretórios

```
k8s/
├── base/               # Manifests de implantação base
│   └── deployment.yaml # Configuração principal de implantação
├── staging/            # Overlays de ambiente staging
└── production/         # Overlays de ambiente produção
```

## Início Rápido

### Pré-requisitos

- Cluster Kubernetes (1.28+)
- CLI kubectl configurada
- Controlador NGINX Ingress
- cert-manager (para TLS)

### Implantar no Kubernetes

1. **Criar namespace e implantar:**
```bash
kubectl apply -f k8s/base/deployment.yaml
```

2. **Verificar implantação:**
```bash
kubectl get pods -n omnimind
kubectl get services -n omnimind
kubectl get ingress -n omnimind
```

3. **Verificar logs:**
```bash
kubectl logs -n omnimind -l app=omnimind,component=backend -f
```

## Componentes

### Implantação Backend
- **Réplicas:** 3 (com HPA 3-10)
- **Recursos:**
  - Requests: 250m CPU, 512Mi memória
  - Limits: 1000m CPU, 2Gi memória
- **Probes:** Verificações de liveness e readiness
- **Auto-scaling:** Baseado em CPU (70%) e Memória (80%)

### Implantação Frontend
- **Réplicas:** 2 (com HPA 2-5)
- **Recursos:**
  - Requests: 100m CPU, 128Mi memória
  - Limits: 200m CPU, 256Mi memória
- **Probes:** Verificações de liveness e readiness
- **Auto-scaling:** Baseado em CPU (70%)

### Ingress
- **TLS:** Let's Encrypt via cert-manager
- **Caminhos:**
  - `/api` → Serviço backend
  - `/ws` → WebSocket (Backend)
  - `/` → Serviço frontend

## Configuração

### Atualizar Secrets

```bash
kubectl create secret generic omnimind-secrets \
  --from-literal=OMNIMIND_DASHBOARD_USER=admin \
  --from-literal=OMNIMIND_DASHBOARD_PASS=<your-password> \
  -n omnimind --dry-run=client -o yaml | kubectl apply -f -
```

### Atualizar Hostname do Ingress

Edite `k8s/base/deployment.yaml` e substitua `omnimind.example.com` pelo seu domínio.

### Configuração de Storage

A implantação usa PersistentVolumeClaim para armazenamento de dados:
- **Tamanho:** 10Gi
- **Storage Class:** standard (ajuste conforme necessário)

Para usar uma storage class diferente:
```bash
kubectl patch pvc omnimind-data -n omnimind -p '{"spec":{"storageClassName":"fast-ssd"}}'
```

## Monitoramento

### Visualizar Status de Auto-scaling

```bash
kubectl get hpa -n omnimind
kubectl describe hpa omnimind-backend-hpa -n omnimind
```

### Visualizar Uso de Recursos

```bash
kubectl top pods -n omnimind
kubectl top nodes
```

### Visualizar Logs

```bash
# Logs do backend
kubectl logs -n omnimind -l component=backend --tail=100 -f

# Logs do frontend
kubectl logs -n omnimind -l component=frontend --tail=100 -f
```

## Scaling

### Scaling Manual

```bash
# Escalar backend
kubectl scale deployment omnimind-backend -n omnimind --replicas=5

# Escalar frontend
kubectl scale deployment omnimind-frontend -n omnimind --replicas=3
```

### Atualizar Limites HPA

```bash
# Aumentar réplicas máximas do backend
kubectl patch hpa omnimind-backend-hpa -n omnimind \
  -p '{"spec":{"maxReplicas":15}}'
```

## Solução de Problemas

### Pods Não Iniciando

```bash
kubectl describe pod <pod-name> -n omnimind
kubectl logs <pod-name> -n omnimind --previous
```

### Serviço Não Acessível

```bash
# Verificar serviço
kubectl get svc -n omnimind
kubectl describe svc omnimind-backend -n omnimind

# Verificar ingress
kubectl get ingress -n omnimind
kubectl describe ingress omnimind-ingress -n omnimind
```

### Problemas SSL/TLS

```bash
# Verificar certificado
kubectl get certificate -n omnimind
kubectl describe certificate omnimind-tls -n omnimind

# Verificar logs do cert-manager
kubectl logs -n cert-manager -l app=cert-manager
```

## Limpeza

```bash
kubectl delete -f k8s/base/deployment.yaml
```

Ou deletar apenas o namespace:
```bash
kubectl delete namespace omnimind
```

## Configuração Avançada

### Limites de Recursos Customizados

Edite a implantação e ajuste requests/limits de recursos:

```yaml
resources:
  requests:
    memory: "1Gi"
    cpu: "500m"
  limits:
    memory: "4Gi"
    cpu: "2000m"
```

### Múltiplos Ambientes

Use Kustomize para configurações específicas de ambiente:

```bash
# Base + Overlay staging
kubectl apply -k k8s/staging/

# Base + Overlay produção
kubectl apply -k k8s/production/
```

## Segurança

### Políticas de Rede

Aplique políticas de rede para restringir tráfego:

```bash
kubectl apply -f k8s/security/network-policies.yaml
```

### Padrões de Segurança de Pod

A implantação segue os Padrões de Segurança de Pod:
- Sem containers privilegiados
- Execução de usuário não-root
- Sistema de arquivos raiz somente leitura quando possível

## Suporte

Para guia detalhado de implantação, veja [ENTERPRISE_DEPLOYMENT.md](../docs/ENTERPRISE_DEPLOYMENT.md)
