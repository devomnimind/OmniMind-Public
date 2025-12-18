# 🚀 GUIA RÁPIDO: TESTAR FRONTEND CORRIGIDO

**Tempo estimado**: 5 minutos

---

## 📋 Pré-requisitos

```bash
✅ Python 3.10+ instalado
✅ Node.js 18+ instalado
✅ npm 9+ instalado
✅ Redis rodando (opcional, para full features)
```

---

## 🔄 Teste Rápido (5 minutos)

### Step 1: Iniciar Backend (2 min)

```bash
cd /home/fahbrain/projects/omnimind
source .venv/bin/activate

# Verificar que está no venv correto
python --version  # Deve ser 3.10+

# Iniciar backend
python -m uvicorn web.backend.main:app --host 0.0.0.0 --port 8000 --reload

# Esperado:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete
```

✅ Backend rodando? Confirmar que vê mensagens de startup.

---

### Step 2: Validar Credenciais (1 min)

**Em outro terminal**:

```bash
# Testar endpoint público de credenciais
curl -s http://localhost:8000/auth/credentials | python -m json.tool

# Resultado esperado:
# {
#   "user": "f483b52c30c2eaed",
#   "pass": "tazYUoFeR8Yzouduz2y0Mw"
# }
```

✅ Credenciais carregadas? Pronto para frontend!

---

### Step 3: Build Frontend (1 min)

```bash
cd /home/fahbrain/projects/omnimind/web/frontend

# Instalar dependências (já feito, mas confirmar)
npm install

# Build
npm run build

# Resultado esperado:
# ✓ 123 modules transformed
# dist/index.html    XX.XX KB │ gzip: X.XX KB
# dist/assets/*      XXX.XX KB │ gzip: XXX.XX KB
```

✅ Build completo? Pronto para rodar!

---

### Step 4: Rodar Frontend Dev (1 min)

```bash
cd /home/fahbrain/projects/omnimind/web/frontend

npm run dev

# Resultado esperado:
# ➜  Local:   http://localhost:5173/
# ➜  press h to show help
```

✅ Frontend rodando? Abrir no browser!

---

### Step 5: Verificar Dashboard (1 min)

Abrir browser: `http://localhost:5173`

**Esperado**:
```
✅ Nenhuma tela de login
✅ Dashboard carrega automaticamente
✅ Métricas visíveis:
   - Φ (Phi): valor com barra de progresso
   - ICI: com componentes (Temporal Coherence, etc)
   - PRS: com status
   - Anxiety, Flow, Entropy
✅ Timeline com histórico
✅ Sem erros de autenticação no console
```

---

## 🧪 Validação em Detalhes

### Console do Browser (F12)

**Procurar por**:

```javascript
// ✅ SUCESSO - Você verá:
[App] ✅ Auto-login successful com credenciais do backend
[authStore] Login successful, credentials saved
[ConsciousnessMetrics] Fetch bem-sucedido

// ❌ ERRO - Se vir:
[ConsciousnessMetrics] Sem autenticação, pulando fetch
Error: Not authenticated
```

---

### localStorage (F12 → Application → Local Storage)

**Procurar por chaves**:
```
omnimind_user: "f483b52c30c2eaed"
omnimind_pass: "tazYUoFeR8Yzouduz2y0Mw"
omnimind-auth: {"state": {"isAuthenticated": true, "username": "f483b52c30c2eaed"}}
```

✅ Tudo presente? Auto-login funcionou!

---

### Métricas Coerentes

**Validar em tempo real**:

1. Ler valor de **Φ (Phi)** no topo
2. Abrir **Metrics Timeline**
3. Ver que **é o mesmo valor** na timeline

✅ Valores iguais? Sincronização funciona!

---

### Labels Corretos

**Validar**:

```
ICI = 0.690 → "Coherent" [GREEN]  ✅ (Antes era "Fragmented" [RED])
ICI = 0.450 → "Partial Coherence" [YELLOW]
ICI = 0.200 → "Fragmented" [RED]
```

✅ Labels correspondem aos valores? Thresholds corretos!

---

## 🔧 Troubleshooting

### ❌ Erro: "Backend não está respondendo"

**Solução**:
```bash
# Verificar se backend está rodando
curl http://localhost:8000/health/

# Se não responder:
# 1. Verificar se porta 8000 está em uso
lsof -i :8000

# 2. Iniciar backend de novo
python -m uvicorn web.backend.main:app --port 8000
```

---

### ❌ Erro: "Credentials not found"

**Solução**:
```bash
# Verificar arquivo de credenciais
ls -la config/dashboard_auth.json

# Se não existir, criar:
echo '{"user": "admin", "pass": "omnimind2025!"}' > config/dashboard_auth.json
chmod 600 config/dashboard_auth.json
```

---

### ❌ Erro: "WebSocket connection refused"

**Solução** (esperado em dev):
- WebSocket pode não estar configurado
- Sistema cai back para HTTP polling
- Funciona normalmente, apenas mais lento
- Não é um erro crítico

---

### ❌ Dashboard em branco com erros de autenticação

**Solução**:
```bash
# 1. Limpar localStorage
# F12 → Application → Local Storage → limpar omnimind_*

# 2. Hard refresh browser
# Ctrl+Shift+R (não só Ctrl+R)

# 3. Reabrir http://localhost:5173
# Deve fazer auto-login novamente
```

---

### ❌ Métricas zeradas (Φ=0.0, ICI=0.0, etc)

**Solução**:
- Pode ser que workspace está vazio (primeira execução)
- Sistema precisa rodar ciclos para gerar dados
- Esperar 10-20 segundos para dados aparecerem
- Dados devem aparecer em Metrics Timeline após coleta

---

## ✅ Validação Completa (Checklist)

- [ ] Backend rodando em http://localhost:8000
- [ ] Endpoint `/auth/credentials` retorna JSON com user/pass
- [ ] Frontend rodando em http://localhost:5173
- [ ] Dashboard carrega **sem tela de login**
- [ ] Console mostra `[App] ✅ Auto-login successful`
- [ ] localStorage tem `omnimind_user`, `omnimind_pass`, `omnimind-auth`
- [ ] Métricas visíveis (Φ, ICI, PRS, Anxiety, Flow, Entropy)
- [ ] Timeline sincronizada com valores do topo
- [ ] ICI = 0.690 mostra "Coherent" [GREEN] (não "Fragmented" [RED])
- [ ] Labels correspondem aos valores
- [ ] Sem erros de autenticação no console

---

## 📊 Teste de Performance

### Tempo de Carregamento

```
Esperado:
  Backend startup: < 10s
  Frontend build: < 30s
  Dashboard first load: < 5s
  Auto-login: < 1s (invisível)
  Total: < 2 minutos
```

---

## 🎬 Demo Completo (5 minutos)

```bash
# Terminal 1: Backend
cd ~/projects/omnimind
python -m uvicorn web.backend.main:app --port 8000

# Terminal 2: Frontend
cd ~/projects/omnimind/web/frontend
npm run dev

# Browser: http://localhost:5173
# Ver dashboard carregar automaticamente! 🎉
```

---

## 📸 Screenshots Esperados

### Tela 1: Dashboard Carregada
```
🧠 OmniMind Dashboard
├─ Phi (Φ) Value: 0.690 [GREEN]
├─ Anxiety Level: 0.000 [GREEN]
├─ Flow State: 0.000 [RED/YELLOW]
├─ System Entropy: 0.000 [GREEN]
├─ ICI: 0.690 [GREEN] ✅ (antes era RED!)
├─ PRS: 0.000 [RED]
├─ Metrics Timeline (com histórico)
├─ Module Activity Heatmap
└─ Daemon Controls
```

### Tela 2: Console do Browser
```
[vite] connected
[App] ✅ Auto-login successful com credenciais do backend
[authStore] Login successful, credentials saved
[ConsciousnessMetrics] Fetch bem-sucedido
```

---

## 🚀 Próximo Passo (Opcional)

Se tudo funciona, pode:

1. **Testar com Redis**:
   ```bash
   redis-server
   ```

2. **Testar com mais ciclos**:
   - Dashboard deve mostrar evolução das métricas
   - Histórico deve atualizar em tempo real

3. **Deploy em produção**:
   - Usar HTTPS
   - Configurar CORS
   - Usar credenciais seguras

---

## ⏱️ Tempo Esperado

| Etapa | Tempo |
|-------|-------|
| Backend startup | 2-5s |
| Validar credenciais | 1s |
| Frontend build | 20-30s |
| Frontend dev server | 3-5s |
| Browser load + auto-login | 2-3s |
| **TOTAL** | **~2 minutos** |

---

## ✨ Resultado Esperado

```
🎉 SUCESSO! 🎉

Dashboard carregada e funcional:
✅ Auto-login sem tela de login
✅ Métricas sincronizadas
✅ Labels corretos
✅ Sem erros de autenticação
✅ Performance ótima

Pronto para usar! 🚀
```

