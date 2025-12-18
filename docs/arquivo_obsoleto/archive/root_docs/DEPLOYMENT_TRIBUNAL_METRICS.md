# 🚀 Guia de Deployment - Tribunal Metrics Fix

**Data**: 9 de dezembro de 2025
**Versão**: 1.0
**Status**: ✅ Pronto para Produção

---

## 📋 Sumário Executivo

O sistema de visualização do Tribunal foi completamente corrigido e melhorado:

- ✅ **Frontend Error Fix**: Implementação null-safe em TribunalStatus
- ✅ **Novo Componente**: TribunalMetricsVisual com visualizações completas
- ✅ **Novo Endpoint**: GET /api/tribunal/metrics com interpretação de dados
- ✅ **Dashboard Integration**: Ambos componentes integrados e funcionando
- ✅ **Type Safety**: Sem erros TypeScript, build pronto para produção

---

## 🔄 Fluxo de Deployment

### Pré-requisitos
```bash
# Backend
- Python 3.9+
- FastAPI rodando
- Daemon monitor funcional

# Frontend
- Node.js 18+
- React 18+
- npm/yarn working
```

### Passo 1: Atualizar Backend
```bash
cd /home/fahbrain/projects/omnimind

# Verificar se o arquivo foi modificado
git diff web/backend/routes/tribunal.py

# Confirmar mudanças (ou fazer merge)
git add web/backend/routes/tribunal.py
```

**O que muda**:
- Novo método `get_metrics()` no router tribunal
- Função auxiliar `_interpret_metrics()` para análise
- Sem breaking changes nos endpoints existentes

### Passo 2: Atualizar Frontend
```bash
cd /home/fahbrain/projects/omnimind/web/frontend

# Verificar mudanças
git diff src/components/TribunalStatus.tsx
git diff src/services/api.ts
git diff src/components/Dashboard.tsx

# Confirmar mudanças
git add src/components/
git add src/services/api.ts

# Build para produção
npm run build
# Resultado: dist/ pronto para servir
```

**O que muda**:
- 3 componentes existentes atualizados
- 1 novo componente adicionado
- Null-safe implementation
- Sem breaking changes na API consumida

### Passo 3: Testes
```bash
# Test script
./test_tribunal_fix.sh

# Verificar endpoints
curl -s -u admin:omnimind2025! \
  http://localhost:8000/api/tribunal/activity | python3 -m json.tool

curl -s -u admin:omnimind2025! \
  http://localhost:8000/api/tribunal/metrics | python3 -m json.tool

# Verificar frontend
curl -s http://localhost:3000 | grep TribunalMetrics
```

---

## 📊 Arquivos Alterados

### Backend
```
web/backend/routes/tribunal.py
├── NOVO: _interpret_metrics() function
├── UPDATE: get_activity() → safe status handling
└── NOVO: get_metrics() endpoint

Lines changed: ~180 (adição)
Breaking changes: NENHUMA
```

### Frontend
```
web/frontend/src/components/
├── TribunalStatus.tsx (UPDATE)
│   ├── Null-safe: status, activityScore, proposals
│   └── Dynamic colors based on status
├── Dashboard.tsx (UPDATE)
│   └── Import + render TribunalMetricsVisual
└── TribunalMetricsVisual.tsx (NEW)
    ├── Status Indicators
    ├── Summary Metrics
    ├── Attack Distribution
    ├── Raw Metrics Details
    └── Recommendations

web/frontend/src/services/
└── api.ts (UPDATE)
    ├── FIX: getTribunalActivity() mapping
    └── NEW: getTribunalMetrics() method

Total lines: ~380 (novo componente)
Breaking changes: NENHUMA
```

---

## ✅ Validação Pré-Deployment

```bash
# 1. TypeScript Check
cd web/frontend && npm run type-check
# Expected: ✅ No errors

# 2. Build Check
npm run build
# Expected: ✅ dist/ created, ready for production

# 3. Backend Import Check
cd /home/fahbrain/projects/omnimind
python3 -c "from web.backend.routes.tribunal import router; print('✅ Route imports OK')"

# 4. API Endpoint Validation
# (requer backend rodando)
curl -s -u admin:omnimind2025! \
  http://localhost:8000/api/tribunal/metrics | python3 -c "import sys, json; json.load(sys.stdin); print('✅ Valid JSON')"

# 5. Database/Cache Check
ls -la data/long_term_logs/daemon_status_cache.json
# Expected: arquivo existe com dados válidos
```

---

## 🚀 Procedimento de Deployment

### Cenário 1: Development (Imediato)
```bash
# 1. Parar serviços antigos
pkill -9 -f 'uvicorn|vite.*frontend' || true

# 2. Reiniciar backend
cd /home/fahbrain/projects/omnimind
./scripts/canonical/system/start_ultrasimple.sh

# 3. Reiniciar frontend
cd web/frontend
npm run dev

# 4. Verificar no browser
# http://localhost:3000
# Login: admin/omnimind2025!
# Procure: "Tribunal do Diabo" no Dashboard
```

### Cenário 2: Production (Staged)
```bash
# 1. Build frontend
cd /home/fahbrain/projects/omnimind/web/frontend
npm run build

# 2. Servir frontend (exemplo nginx)
# Copiar dist/* para /var/www/html ou similar
# Configurar proxy para backend

# 3. Deploy backend
# (conforme seu processo de deployment)
# Executar em: http://your-api.com:8000

# 4. Testar endpoints
curl -s -u admin:password http://your-api.com:8000/api/tribunal/metrics

# 5. Verificar frontend
# Acessar: http://your-frontend.com
# Procure componente Tribunal no Dashboard
```

### Cenário 3: Docker
```dockerfile
# Dockerfile.frontend
FROM node:18-alpine
WORKDIR /app
COPY web/frontend ./
RUN npm install && npm run build

# Dockerfile.backend
FROM python:3.11-slim
WORKDIR /app
COPY . ./
RUN pip install -r requirements.txt
CMD ["uvicorn", "web.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build & Deploy
docker build -f Dockerfile.frontend -t omnimind-frontend .
docker build -f Dockerfile.backend -t omnimind-backend .

docker run -d -p 3000:80 omnimind-frontend
docker run -d -p 8000:8000 omnimind-backend
```

---

## 🔍 Rollback Procedure (se necessário)

```bash
# 1. Salvar versão atual (backup)
git stash

# 2. Revert para versão anterior
git revert HEAD

# 3. Redeployar
# (conforme seu processo)

# 4. Se tudo estiver bem, pode descartar
git stash drop
```

---

## 📈 Monitoramento Pós-Deployment

### Logs
```bash
# Backend
tail -f logs/omnimind.log | grep tribunal

# Frontend (browser console)
# F12 → Console → verificar sem erros
```

### Health Checks
```bash
# Health endpoint
curl -s http://localhost:8000/health/ | python3 -m json.tool

# Tribunal endpoints
curl -s -u admin:omnimind2025! \
  http://localhost:8000/api/tribunal/activity | python3 -m json.tool

curl -s -u admin:omnimind2025! \
  http://localhost:8000/api/tribunal/metrics | python3 -m json.tool
```

### Performance
```bash
# Verificar tempo de resposta
time curl -s -u admin:omnimind2025! \
  http://localhost:8000/api/tribunal/metrics > /dev/null

# Expected: < 500ms para ambos endpoints
```

### Errors
```bash
# Monitorar errors no backend
grep -i "error\|exception" logs/omnimind.log | tail -20

# Monitorar errors no frontend (browser)
# F12 → Console → Network → verificar requisições
```

---

## 📝 Checklist de Deployment

- [ ] Backend testado localmente
- [ ] Frontend build successful
- [ ] TypeScript sem erros
- [ ] Endpoints respondendo (ambos)
- [ ] Componentes renderizando sem erros
- [ ] Auto-refresh funcionando (30s)
- [ ] Null-safe implementation validada
- [ ] Database/cache com dados válidos
- [ ] Credential/Auth confirmado
- [ ] CORS configurado corretamente

---

## 🆘 Troubleshooting

### Erro: "Endpoint retorna 404"
```bash
# Verificar se tribunal.py está registrado no main.py
grep -n "tribunal" web/backend/main.py

# Esperado:
# from web.backend.routes import tribunal
# app.include_router(tribunal.router)
```

### Erro: "data.status is undefined"
```
✅ RESOLVIDO - Frontend agora tem null-safe checks
Se persistir:
1. Limpar cache do browser (Ctrl+Shift+Del)
2. Hard refresh (Ctrl+F5)
3. Verificar network tab no DevTools
```

### Erro: "GET /api/tribunal/metrics returns empty"
```bash
# Verificar daemon monitor
curl -s -u admin:omnimind2025! \
  http://localhost:8000/daemon/status

# Verificar cache file
cat data/long_term_logs/daemon_status_cache.json | python3 -m json.tool
```

### Performance Lenta
```bash
# Verificar CPU/Memory
htop -p $(pgrep -f uvicorn)

# Verificar queries lentas
grep "duration" logs/omnimind.log | sort -t= -k2 -nr | head -5
```

---

## 📞 Suporte

Se encontrar problemas:

1. **Verificar logs**: `tail -f logs/omnimind.log`
2. **Verificar network**: F12 → Network tab
3. **Verificar cache**: `data/long_term_logs/daemon_status_cache.json`
4. **Executar testes**: `./test_tribunal_fix.sh`
5. **Limpar e reiniciar**: `pkill -9 -f uvicorn; ./scripts/canonical/system/start_ultrasimple.sh`

---

## 📚 Documentação Relacionada

- [TRIBUNAL_METRICS_FIX.md](./docs/TRIBUNAL_METRICS_FIX.md) - Resumo técnico completo
- [SEQUENTIAL_INITIALIZATION_STRATEGY.md](./docs/SEQUENTIAL_INITIALIZATION_STRATEGY.md) - Estratégia de inicialização
- [QUICK_START_SEQUENTIAL.md](./QUICK_START_SEQUENTIAL.md) - Quick start

---

**Status Final**: ✅ **READY FOR PRODUCTION**

Todas as mudanças foram testadas, validadas e documentadas. Sistema pronto para deployment.

