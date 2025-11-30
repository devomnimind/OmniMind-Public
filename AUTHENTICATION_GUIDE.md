# 🔐 OmniMind Authentication Configuration

**Status**: ✅ FUNCIONANDO

## Credentials

- **Username**: `admin`
- **Password**: `omnimind2025!`
- **Method**: HTTP Basic Authentication

## Configuração de Autenticação

### Backend (.env)
```bash
OMNIMIND_DASHBOARD_USER=admin
OMNIMIND_DASHBOARD_PASS=omnimind2025!
```

### Frontend (.env.local)
```bash
VITE_API_URL=
VITE_DASHBOARD_USER=admin
VITE_DASHBOARD_PASS=omnimind2025!
```

## Como Funciona

### 1. Backend (FastAPI)
- Recebe HTTP Basic Auth no header `Authorization: Basic <base64>`
- Valida credenciais usando função `_verify_credentials()`
- Retorna 200 OK com dados reais de metrics
- Retorna 401 Unauthorized se credenciais inválidas

**Teste**:
```bash
curl -u admin:omnimind2025! http://127.0.0.1:8000/daemon/status
```

### 2. Frontend (React + Vite)
- Carrega credenciais padrão do `.env.local` (variáveis VITE_*)
- Login.tsx auto-preenche username/password
- apiService encoda credenciais em Base64
- Envia no header `Authorization: Basic <base64>`
- Proxy Vite encaminha requisição para backend:8000

**Fluxo**:
```
User -> Frontend (3000) -> Vite Proxy -> Backend (8000)
  (browser)              (same origin)   (API)
```

### 3. Proxy Configuration
**vite.config.ts**:
```typescript
proxy: {
  '/daemon': {
    target: 'http://localhost:8000',
    changeOrigin: true,
    secure: false,
  }
}
```

## Endpoints Protegidos (requer auth)

```bash
GET /daemon/status
  ├─ Authorization: Basic admin:omnimind2025! (encoded)
  └─ Returns: Real consciousness metrics (Phi, Anxiety, Flow, Entropy)

POST /daemon/start
  ├─ Authorization: Required
  └─ Starts daemon

POST /daemon/stop
  ├─ Authorization: Required
  └─ Stops daemon

POST /daemon/reset-metrics
  ├─ Authorization: Required
  └─ Resets metrics
```

## Endpoints Públicos (sem auth)

```bash
GET /                    # API running message
GET /health             # Health check
GET /api/v1/status      # Status nominal
```

## Troubleshooting

### ❌ "Invalid credentials or server unavailable"

**Verificar credenciais**:
```bash
# Backend
curl -v -u admin:omnimind2025! http://127.0.0.1:8000/daemon/status

# Frontend (via proxy)
curl -v -u admin:omnimind2025! http://127.0.0.1:3000/daemon/status
```

**Verificar .env files**:
```bash
# Backend credentials
cat /home/fahbrain/projects/omnimind/.env | grep OMNIMIND_DASHBOARD

# Frontend credentials
cat /home/fahbrain/projects/omnimind/web/frontend/.env.local | grep VITE_DASHBOARD
```

### ❌ Frontend não está carregando credenciais

**Solução**:
1. Verificar se `.env.local` existe
2. Verificar se variáveis começam com `VITE_`
3. Reiniciar dev server: `npm run dev`
4. Limpar cache do navegador (Ctrl+Shift+Delete)

### ❌ "401 Unauthorized"

**Causas possíveis**:
1. Credenciais inválidas (typo)
2. Backend não está rodando
3. PYTHONPATH incorreto
4. .env não está sendo carregado

**Debug backend**:
```bash
# Verificar se backend está rodando
ps aux | grep uvicorn

# Verificar se .env está sendo carregado
python -c "import os; print(os.getenv('OMNIMIND_DASHBOARD_USER'))"
```

## Testes Rápidos

### Test 1: Backend auth
```bash
curl -u admin:omnimind2025! http://127.0.0.1:8000/daemon/status
# Deve retornar 200 OK com JSON metrics
```

### Test 2: Frontend proxy
```bash
curl -u admin:omnimind2025! http://127.0.0.1:3000/daemon/status
# Deve retornar 200 OK (via proxy)
```

### Test 3: Base64 encoding
```bash
echo -n "admin:omnimind2025!" | base64
# Deve retornar: YWRtaW46b21uaW1pbmQyMDI1IQ==

# Verificar no header
curl -H "Authorization: Basic YWRtaW46b21uaW1pbmQyMDI1IQ==" http://127.0.0.1:8000/daemon/status
```

### Test 4: Login flow
```bash
# Abrir browser
open http://127.0.0.1:3000

# Credenciais devem estar pré-preenchidas
# Username: admin
# Password: omnimind2025!

# Clicar Login
# Deve autenticar e mostrar dashboard
```

## Logs Debug

### Backend (uvicorn)
```
INFO:src.api.routes.daemon:Daemon status retrieved successfully
INFO:     127.0.0.1:54688 - "GET /daemon/status HTTP/1.1" 200 OK
```

### Frontend (browser console)
```
[ApiService] Credentials set for user: admin
[ApiService] GET http://127.0.0.1:8000/daemon/status
[ApiService] Auth header: Basic YWRt...
[ApiService] Response: 200 OK
[Login] Authentication successful, daemon status: {...}
```

## Variáveis de Ambiente Finais

| Variável | Valor | Local |
|----------|-------|-------|
| OMNIMIND_DASHBOARD_USER | admin | .env |
| OMNIMIND_DASHBOARD_PASS | omnimind2025! | .env |
| VITE_DASHBOARD_USER | admin | .env.local |
| VITE_DASHBOARD_PASS | omnimind2025! | .env.local |
| VITE_API_URL | (empty) | .env.local |

---

**Last Updated**: 30 Nov 2025
**Status**: ✅ Authentication system fully configured and tested
