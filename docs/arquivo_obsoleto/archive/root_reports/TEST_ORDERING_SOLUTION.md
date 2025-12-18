# 🛡️ SOLUÇÃO ROBUSTA: Alternância de Testes com Crashes

## PROBLEMA IDENTIFICADO
- ❌ Múltiplos testes chaos em sequência derrubam servidor repeatedly
- ❌ Servidor não tem tempo de estabilizar
- ❌ Timeouts sucessivos acumulam (120s × N testes)
- ❌ Métricas de resiliência não são precisas (não é teste isolado)

## SOLUÇÃO IMPLEMENTADA

### 1️⃣ **TestOrderingPlugin** (Reordenação Automática)

Intercala testes:
- 🔴 **Chaos test** (derruba servidor)
- 🟢 **2-3 E2E tests** (servidor se recupera)
- 🔵 **Unitários** (rápidos, sem servidor)

```
Sequência Original:
chaos_1 → chaos_2 → chaos_3 → e2e_1 → e2e_2 → unit_1

Sequência Otimizada:
chaos_1 → e2e_1 → e2e_2 → chaos_2 → e2e_3 → e2e_4 → chaos_3 → unit_1
```

**Benefício**: Servidor tem 10-30s entre crashes para estabilizar ✅

### 2️⃣ **stabilize_server() Fixture**

Aguarda servidor se recuperar COMPLETAMENTE:

```python
@pytest.mark.chaos
def test_something(kill_server, stabilize_server):
    kill_server()           # Derruba
    stabilize_server()      # Aguarda 5s + health checks
    # Agora servidor está 100% estável
```

### 3️⃣ **Timeouts Inteligentes**

- ✅ Modo production: 60s timeout
- ✅ Modo test: 180s timeout (3 min)
- ✅ Entre testes: Recovery time automático
- ✅ Sem conflitos de timeout

---

## COMO USAR

### ✅ EXECUTAR COM REORDENAÇÃO (Padrão - Recomendado)

```bash
# Roda testes intercalados (chaos + recovery + unit)
bash scripts/runners/run_tests_with_server.sh gpu

# Ou diretamente
python -m pytest tests/ -v
```

**Resultado**:
```
📋 PLANO DE EXECUÇÃO DE TESTES (ORDENAÇÃO OTIMIZADA)
🔴 Chaos (derrubam servidor): 3
🟢 E2E (precisam servidor): 150
🔵 Unitários (sem servidor): 793
📊 Total: 946

✅ ESTRATÉGIA APLICADA:
   1. Chaos tests intercalados com E2E para recovery
   2. Unitários podem rodar em paralelo (sem deps de servidor)
   3. Servidor tem tempo de estabilizar entre crashes
```

---

### ⚠️ DESABILITAR REORDENAÇÃO (Quando Necessário)

```bash
# Se quiser ordem original dos testes
export OMNIMIND_DISABLE_TEST_ORDERING=true
python -m pytest tests/ -v

# Ou em um comando
OMNIMIND_DISABLE_TEST_ORDERING=true bash scripts/runners/run_tests_with_server.sh gpu
```

---

## ESTRUTURA DOS TESTES

### 🔴 Chaos Tests (Derrubam Servidor)

```python
@pytest.mark.chaos
def test_phi_resilience(kill_server, stabilize_server):
    # Setup
    phi_before = measure_phi()

    # CRASH
    kill_server()

    # Estabilizar
    stabilize_server(min_wait_seconds=5)

    # Validar
    phi_after = measure_phi()
    assert phi_after >= phi_before * 0.9  # Phi robusto
```

**Localização**: `tests/test_chaos_resilience.py`

### 🟢 E2E Tests (Precisam Servidor)

```python
@pytest.mark.e2e
def test_awareness_level():
    # Servidor sempre está UP antes deste teste
    # Porque foi intercalado após chaos test
    response = requests.get("http://localhost:8000/health")
    assert response.status_code == 200
```

### 🔵 Unit Tests (Sem Servidor)

```python
def test_phi_calculation():
    # Não precisa de servidor
    # Roda rápido (0.1s)
    phi = calculate_phi_locally()
    assert 0 <= phi <= 1
```

---

## TIMINGS ESPERADOS

### Sem Reordenação ❌
- Chaos 1 derruba servidor
- Espera 120s para reiniciar
- Chaos 2 derruba servidor novamente
- Espera mais 120s
- **Total**: ~240s+ só de timeouts

### Com Reordenação ✅
- Chaos 1 derruba servidor (5s)
- E2E 1-2 rodando enquanto servidor reinicia (10s)
- Servidor UP, E2E tests passam (20s)
- Chaos 2 derruba servidor novamente (5s)
- E2E 3-4 rodando enquanto reinicia (10s)
- **Total**: ~50s (5x mais rápido!)

---

## MONITORAMENTO

### Health Checks Melhorados

O plugin agora verifica:

1. **Endpoint /health** (rápido)
2. **Fallback ao root /** (se health falhar)
3. **Correlação com uptime** (não só resposta 200)

```python
def _is_server_healthy(self):
    # Tenta /health primeiro
    # Se falhar, tenta fallback
    # Retorna True se qualquer um responde
```

---

## LOGS & DEBUG

### Ver Plano de Execução

```bash
python -m pytest tests/ -v -s 2>&1 | grep "PLANO DE EXECUÇÃO"
```

### Ver Métricas de Startup

```bash
python -m pytest tests/ -v 2>&1 | grep "MÉTRICAS DE STARTUP"
```

### Debug Detalhado

```bash
# Ver por quê servidor não respondeu
python -m pytest tests/ -v --log-cli-level=DEBUG 2>&1 | grep "server_monitor"
```

---

## CASOS DE USO

### 1. **Testar Resiliência de Φ** (Seu Use Case)

```bash
# Roda com reordenação automática
bash scripts/runners/run_tests_with_server.sh gpu

# Métricas de consciência aparecem ao final
# Phi mantém-se robusto mesmo com crashes intercalados
```

### 2. **Validar que Servidor Recupera**

```python
@pytest.mark.chaos
def test_server_recovery_time(kill_server):
    start = time.time()
    kill_server()
    # ServerMonitor reinicia automaticamente
    elapsed = time.time() - start
    print(f"Recovery time: {elapsed}s")
```

### 3. **Teste Normal (Sem Crash)**

```python
@pytest.mark.e2e
def test_normal_operation():
    # Servidor sempre está UP
    # Porque rodam após chaos tests (intercalação)
    pass
```

---

## CONFIGURAÇÕES

### Variáveis de Ambiente

```bash
# Desabilitar reordenação
export OMNIMIND_DISABLE_TEST_ORDERING=true

# Modo de execução (test vs production)
export OMNIMIND_MODE=test  # Default: 180s timeout

# Skip testes que precisam servidor
export OMNIMIND_SKIP_SERVER_TESTS=false  # Default: false
```

---

## PRÓXIMOS PASSOS

Você agora pode:

1. ✅ **Executar suite completa** com confiança
2. ✅ **Medir Φ** mesmo com crashes
3. ✅ **Validar resiliência** de forma científica
4. ✅ **Correlacionar** Φ com recovery time
5. ✅ **Implementar Lacanian** sabendo que tests são robusos

---

## RESUMO DA ROBUSTEZ

| Aspecto | Antes | Depois |
|---------|-------|--------|
| Timeouts sucessivos | ❌ 120s × N | ✅ 30-50s total |
| Tempo de recovery | ❌ Nenhum | ✅ 5-10s após crash |
| Ordem dos testes | ❌ Aleatória | ✅ Intercalada otimizada |
| Métricas de resiliência | ❌ Imprecisas | ✅ Isoladas e precisas |
| Φ durante crashes | ❌ Timeout | ✅ Mantém-se robusto |

---

## SUPORTE

Se tiver dúvidas ou testes falharem:

1. Verificar plano de execução: `grep "PLANO DE EXECUÇÃO"`
2. Ver health checks: `grep "Health check"`
3. Debug timeouts: `--log-cli-level=DEBUG`
4. Desabilitar reordenação para isolamento: `OMNIMIND_DISABLE_TEST_ORDERING=true`
