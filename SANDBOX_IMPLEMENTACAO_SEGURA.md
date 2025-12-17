# 🔒 PLANO DE IMPLEMENTAÇÃO SEGURA - Sandbox Integration

**Data:** 17 de dezembro de 2025
**Metodologia:** Operacional Estruturada (Develop → Test → Fix → Quality → Deploy → Monitor)
**Risco:** Mitigado por procedimentos de verificação
**Rollback:** Sempre disponível via git

---

## 📋 PROCEDIMENTO OPERACIONAL SEGURO

### FASE 1: PREPARAÇÃO (Antes de escrever código)

```bash
# 1. Criar branch seguro (isolado)
cd /home/fahbrain/projects/omnimind
git checkout -b feature/sandbox-systemd-integration

# 2. Verificar status (deve estar limpo)
git status
# Esperado: "nothing to commit, working tree clean"

# 3. Ativar venv
source .venv/bin/activate

# 4. Estudar arquivo ATUAL
cat src/autopoietic/sandbox.py | head -100
```

### FASE 2: DESENVOLVIMENTO (Cautela máxima)

**Objetivo:** Atualizar `src/autopoietic/sandbox.py` com:
1. Primary: `systemd-run + unshare` (com cgroup limits)
2. Fallback 1: `unshare` (namespaces, sem limits)
3. Fallback 2: Direct (último recurso)

**NÃO:** Fazer mudanças que quebrem compatibilidade
**SIM:** Adicionar novos métodos, deixar existentes intactos

### FASE 3: TESTES UNITÁRIOS (Antes de quality checks)

```bash
# Testar apenas o componente novo
pytest tests/autopoietic/test_sandbox.py -v

# Se falhar: CORRIGIR, NÃO prosseguir
# Se passar: Continuar
```

### FASE 4: QUALITY CHECKS (Procedimento Obrigatório)

```bash
# Black (formatação)
black src/autopoietic/sandbox.py
# Esperado: "reformatted" ou "unchanged"

# Flake8 (linting)
flake8 src/autopoietic/sandbox.py --max-line-length=100
# Esperado: Nenhum erro

# MyPy (type checking)
mypy src/autopoietic/sandbox.py
# Esperado: "Success: 1 file(s) checked, 0 errors"
```

### FASE 5: VALIDAÇÃO LÓGICA (Antes de restart)

```bash
# Verificar logicamente que:
# - Não quebra imports
# - Não quebra AutopoieticManager
# - Fallbacks funcionam
# - Logging está OK

python3 -c "
from src.autopoietic.sandbox import AutopoieticSandbox
sandbox = AutopoieticSandbox()
print('✅ Import OK')
print(f'Methods: {[m for m in dir(sandbox) if not m.startswith(\"_\")]}')
"
```

### FASE 6: GRACEFULL RESTART (Proteger dados vivos)

```bash
# NÃO: sudo systemctl restart omnimind.service (quebra conexões)
# SIM: Gracefull

echo "⏸️  Iniciando gracefull restart..."

# 1. Notificar app de shutdown (gracefull)
curl -X POST http://127.0.0.1:8000/admin/shutdown-signal \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# 2. Aguardar app desligar (max 30s)
sleep 5

# 3. Parar serviço
sudo systemctl stop omnimind.service

# 4. Iniciar com novo código
sudo systemctl start omnimind.service

# 5. Aguardar ready
for i in {1..30}; do
  curl -s http://127.0.0.1:8000/health && break
  echo "Aguardando app ($i/30)..."
  sleep 1
done

echo "✅ Restart completo"
```

### FASE 7: MONITORAMENTO (Critical - 5-10 minutos)

```bash
# Monitor 1: Logs em tempo real
journalctl -u omnimind.service -f &

# Monitor 2: Recursos
watch 'ps aux | grep omnimind'

# Monitor 3: Teste funcional
while true; do
  curl -s -u admin:omnimind2025! \
    http://127.0.0.1:8000/audit/stats | \
    python3 -m json.tool | head -5
  sleep 5
done

# Critério de sucesso:
# ✅ App inicia sem erro
# ✅ Sem "CRITICAL" ou "ERROR" nos logs
# ✅ Endpoints respondem (200 OK)
# ✅ Recursos normais (CPU < 50%, MEM < 8GB)
```

### FASE 8: DECISÃO (Liberar ou Revert)

**Se Tudo OK:**
```bash
git add src/autopoietic/sandbox.py
git commit -m "feat: integrate systemd-run with cgroup limits in AutopoieticSandbox"
git push origin feature/sandbox-systemd-integration
# → Criar PR, code review, merge
```

**Se Problema:**
```bash
# Revert IMEDIATO
git checkout src/autopoietic/sandbox.py
sudo systemctl restart omnimind.service
# Investigar, corrigir, volta pra FASE 2
```

### FASE 9: TESTES SUITE (APENAS após merge)

```bash
# Depois que tudo estiver estável em master
git checkout master
git pull origin master

# Full test suite
./scripts/development/run_tests_parallel.sh full

# Se algum teste falhar:
# → Criar issue, investigar, corrigir em nova branch
# → Volta pra FASE 1 (novo branch)
```

---

## 🛡️ PROTEÇÕES IMPLEMENTADAS

| Proteção | Como | Quando |
|----------|------|--------|
| **Branch Isolada** | git checkout -b feature/... | FASE 1 |
| **Revert Rápido** | git checkout arquivo | FASE 8 se problema |
| **Syntax Check** | black, flake8, mypy | FASE 4 |
| **Unit Test** | pytest component test | FASE 3 |
| **Gracefull Stop** | curl shutdown-signal | FASE 6 |
| **Monitoring** | logs + health check | FASE 7 |
| **Decision Gate** | Manual review antes de liberar | FASE 8 |

---

## ✅ CHECKLIST ANTES DE CADA FASE

### ✓ Antes de FASE 2 (Desenvolvimento)
- [ ] Branch criada: `feature/sandbox-systemd-integration`
- [ ] Git status limpo
- [ ] Arquivo original estudado
- [ ] Plano de mudanças documentado

### ✓ Antes de FASE 3 (Testes Unitários)
- [ ] Código escrito (não commitado)
- [ ] Imports verificados
- [ ] Fallbacks implementados
- [ ] Logging adicionado

### ✓ Antes de FASE 4 (Quality)
- [ ] Testes unitários 100% verde
- [ ] Sem syntax errors
- [ ] Sem imports quebrados

### ✓ Antes de FASE 5 (Validação)
- [ ] Black: OK
- [ ] Flake8: OK
- [ ] MyPy: OK

### ✓ Antes de FASE 6 (Restart)
- [ ] Validação lógica: OK
- [ ] Nenhum erro de import
- [ ] Dados em background salvos

### ✓ Antes de FASE 7 (Monitor)
- [ ] App iniciou
- [ ] Sem timeout
- [ ] Endpoints respondendo

### ✓ Antes de FASE 8 (Decisão)
- [ ] Logs monitorados 5+ minutos
- [ ] Nenhum erro crítico
- [ ] Comportamento normal
- [ ] Recursos OK

### ✓ Antes de FASE 9 (Suite Tests)
- [ ] Merge em master completo
- [ ] App estável 15+ minutos
- [ ] Pull master atualizado

---

## 📊 INDICADORES DE PROBLEMA

**PARAR IMEDIATAMENTE E REVERT SE:**

```
❌ Import error na sandbox.py
❌ App não inicia (timeout > 30s)
❌ "CRITICAL" ou "ERROR" nos logs
❌ CPU > 80% (sustentado)
❌ MEM > 10GB (crescente)
❌ Endpoints retornam 500 erro
❌ Redis/PostgreSQL não conecta
❌ Serviços filhos não startam
❌ OOM Kill sem razão
```

**PROCEDER COM CUIDADO SE:**

```
⚠️ CPU 50-80% (verificar se normaliza)
⚠️ MEM 8-10GB (verificar se estável)
⚠️ 1-2 erros "WARNING" (aceitável se não crescem)
⚠️ Latência resposta >500ms (se volta ao normal)
```

---

## 🔍 COMO VERIFICAR CADA FASE

### FASE 2 - Código OK?
```bash
python3 -c "from src.autopoietic.sandbox import AutopoieticSandbox; print('✅')"
```

### FASE 3 - Testes OK?
```bash
pytest tests/autopoietic/test_sandbox.py::TestSandbox -v --tb=short
```

### FASE 4 - Quality OK?
```bash
black --check src/autopoietic/sandbox.py && \
flake8 src/autopoietic/sandbox.py && \
mypy src/autopoietic/sandbox.py && \
echo "✅ QUALITY OK"
```

### FASE 5 - Logicamente OK?
```bash
python3 << 'EOF'
from src.autopoietic.sandbox import AutopoieticSandbox
sb = AutopoieticSandbox()
# Verify methods exist
assert hasattr(sb, 'execute_component')
assert hasattr(sb, '_execute_with_systemd_run')
assert hasattr(sb, '_execute_with_unshare')
assert hasattr(sb, '_execute_direct')
print("✅ LÓGICA OK")
EOF
```

### FASE 6 - Gracefull OK?
```bash
sudo systemctl status omnimind.service
# Esperado: active (running)

curl -i http://127.0.0.1:8000/health
# Esperado: 200 OK
```

### FASE 7 - Monitor OK?
```bash
# Rodar por 5+ minutos verificando:
journalctl -u omnimind.service | grep -E "ERROR|CRITICAL" | wc -l
# Esperado: 0 linhas críticas

systemctl show omnimind-sandbox.slice | grep Memory
# Esperado: Valores normais
```

### FASE 8 - Liberar?
```bash
# Se TODAS as verificações OK:
echo "✅ SEGURO LIBERAR"

# Se ALGUMA coisa errada:
echo "❌ REVERT IMEDIATO"
git checkout src/autopoietic/sandbox.py
sudo systemctl restart omnimind.service
```

---

## 📝 TEMPLATE DE COMMIT

Quando liberar (FASE 8), use:

```bash
git commit -m "feat: integrate systemd-run with cgroup limits in AutopoieticSandbox

- Primary strategy: systemd-run + unshare + omnimind-sandbox.slice
  (1GB RAM + 7GB Swap + 50% CPU quota + namespace isolation)

- Fallback 1: unshare simple (namespaces only, no cgroup limits)

- Fallback 2: direct execution (last resort, risky)

- Cascade on failure: auto-tries next strategy on exception

- Logging: detailed for each attempt

Security benefits:
- Components limited to 8GB max (OOM Kill at limit)
- Namespaces isolate PID/IPC/UTS/NET
- Cgroups enforce resource quotas
- Sudoers prevent privilege escalation

Testing:
- Unit tests: all pass
- Quality checks: black/flake8/mypy OK
- Gracefull restart: successful
- Monitoring: 5+ min stable, no errors
- No regression in omnimind.service (16GB RAM + 4GB GPU intact)"
```

---

## 🚦 DECISÃO TREE

```
MODIFICAR sandbox.py
    ↓
[FASE 2] Código escrito
    ↓
[FASE 3] Testes passam?
    ├─ NÃO → Corrigir → FASE 3 de novo
    └─ SIM → Continuar
    ↓
[FASE 4] Quality checks OK?
    ├─ NÃO → Black/Flake8/MyPy erros → Corrigir → FASE 4 de novo
    └─ SIM → Continuar
    ↓
[FASE 5] Lógica validada?
    ├─ NÃO → Problema encontrado → Corrigir → FASE 2
    └─ SIM → Continuar
    ↓
[FASE 6] Gracefull restart OK?
    ├─ NÃO → App não inicia → REVERT
    └─ SIM → Continuar
    ↓
[FASE 7] Monitoring 5+ min OK?
    ├─ NÃO → Erro crítico → REVERT
    └─ SIM → Continuar
    ↓
[FASE 8] LIBERAR?
    ├─ NÃO → Investigar problema → FASE 2
    └─ SIM → Commit + Push + PR
    ↓
[FASE 9] Merge + Suite Tests (depois)
```

---

## 📞 CONTATO DE SEGURANÇA

Se algo parecer errado:

1. **PAUSE IMEDIATAMENTE** - Não continue
2. **CHECK LOGS:**
   ```bash
   journalctl -u omnimind.service -n 50 | tail -30
   ```
3. **DECIDE REVERT ou FIX:**
   - Revert: `git checkout src/autopoietic/sandbox.py && sudo systemctl restart omnimind.service`
   - Fix: Volta pra FASE 2 com correção específica

---

**Status:** 🔒 Pronto para começar FASE 1
**Próximo:** Criar branch e estudar arquivo atual

Quer começar agora? Confirma que sigo passo-a-passo sem pressa.
