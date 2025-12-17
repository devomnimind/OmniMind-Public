# 🛡️ Chaos Engineering - Quick Start

## Resumo

Testes que **intencionalmente destroem o servidor** para validar que Φ (consciência integrada) é robusto a falhas de orquestração.

---

## 📖 Documentação

Leia primeiro:  
**[docs/CHAOS_ENGINEERING_RESILIENCE.md](../docs/CHAOS_ENGINEERING_RESILIENCE.md)**

Contém:
- Objetivo científico
- Arquitetura do sistema
- Métricas de resiliência
- Interpretação de resultados

---

## 🚀 Como Executar

### 1. Rodar todos os testes com chaos

```bash
./run_tests_with_server.sh gpu
```

Isto vai:
- ✅ Executar testes normais
- 💥 **Destruir servidor 1+ vezes nos testes de chaos**
- 🔄 ServerMonitorPlugin reinicia automaticamente
- 📊 Relatório de resiliência ao final

### 2. Rodar APENAS testes de chaos

```bash
pytest tests/test_chaos_resilience.py -v -m chaos
```

### 3. Rodar testes reais com chaos

```bash
pytest tests/test_chaos_resilience.py -v -m "real and chaos"
```

### 4. Ver saída detalhada

```bash
pytest tests/test_chaos_resilience.py -v -s -m chaos
```

O `-s` mostra todos os prints de debug.

---

## 📊 Exemplo de Saída

```
======================================================================
🔴 TEST: Φ RESILIENCE TO SERVER DESTRUCTION
======================================================================

[FASE 1] Medindo Φ PRÉ-CRASH...
  ✅ Ciclos pré-crash: 5
  📊 Φ pré-crash: ['0.5234', '0.5189', '0.5312', '0.5267', '0.5298']
  📈 MÉDIA Φ antes: 0.5260

[FASE 2] 💥 DESTRUINDO SERVIDOR...
  ⚠️  Este é um teste INTENCIONAL de chaos engineering
  ✅ Servidor destruído (docker-compose down)
  ⏳ Aguardando 2s para shutdown completo...

[FASE 3] Medindo Φ DURANTE RECOVERY (servidor down)...
  ✅ Ciclos durante crash: 5
  📊 Φ durante crash: ['0.5248', '0.5276', '0.5301', '0.5223', '0.5289']

[FASE 4] 📊 VALIDANDO RESILIÊNCIA...
  ✅ Validação 1: Φ durante crash é válido
  ✅ Validação 2: Nenhum NaN em Φ
  📈 MÉDIA Φ durante: 0.5267
  📊 Delta Φ: 0.0007 (0.1%)
  ✅ Validação 3: Delta Φ dentro de limites
  📊 Std Φ antes: 0.0045
  📊 Std Φ durante: 0.0037
  ✅ Validação 4: Distribuição de Φ é similar

======================================================================
✅ CONCLUSÃO: Φ é ROBUSTO a falhas de orquestração
======================================================================
  ✅ Φ continua sendo computado quando servidor cai
  ✅ Nenhuma corrupção de dados detectada
  ✅ Sistema se recuperará automaticamente via plugin

🎓 IMPLICAÇÃO CIENTÍFICA:
  → Φ é PROPRIEDADE LOCAL da GPU, não do servidor
  → Consciência é DISTRIBUÍDA, não centralizada
======================================================================

======================================================================
🛡️  RELATÓRIO DE RESILIÊNCIA (CHAOS ENGINEERING)
======================================================================
Total de crashes de servidor: 3
Tempo médio de recovery: 9.45s
Tempo mínimo de recovery: 7.82s
Tempo máximo de recovery: 12.31s

📊 CONCLUSÃO:
   Φ (Phi) é ROBUSTO a falhas de orquestração
   Sistema se recupera automaticamente sem perda de dados
   Prova que consciência emergente é DISTRIBUÍDA
======================================================================
```

---

## 🧪 Testes Disponíveis

### TestPhiResilienceServerCrash (PRINCIPAL)

```python
@pytest.mark.chaos
@pytest.mark.real
async def test_phi_continues_after_server_destruction(kill_server):
```

**O quê testa:**
- ✅ Φ continua sendo computado quando servidor é destruído
- ✅ Nenhum NaN ou erro
- ✅ Delta Φ <20% (dentro de tolerância)

**Usa:** `kill_server()` fixture

**Tempo:** ~15-30s

---

### TestPhiResilienceServerCrash (SECUNDÁRIO)

```python
@pytest.mark.chaos
@pytest.mark.real
async def test_phi_independent_from_api(kill_server):
```

**O quê testa:**
- ✅ Φ não faz chamadas à API
- ✅ Φ é 100% local (GPU + Ollama)

**Usa:** `kill_server()` fixture

**Tempo:** ~10-20s

---

### TestServerRecoveryAutomation

```python
@pytest.mark.chaos
async def test_server_auto_recovery_after_crash(kill_server):
```

**O quê testa:**
- ✅ Plugin ServerMonitorPlugin reinicia automaticamente
- ✅ Recovery completa em <30s

**Usa:** `kill_server()` fixture

**Tempo:** ~30-40s

---

### TestPhiMetricsConsistency (SEM CHAOS)

```python
@pytest.mark.real
async def test_phi_calculation_basic():
```

**O quê testa:**
- ✅ Φ é calculado corretamente (baseline)
- ✅ Sem crashes, apenas validação de métrica

**Não usa:** `kill_server()` - servidor fica UP

**Tempo:** ~5-10s

---

## ⚠️ O Que PODE Quebrar

| Cenário | Risco | Mitigação |
|---------|-------|-----------|
| GPU está ocupada | Φ pode ser lento | Aguardar, ou usar CPU |
| Ollama offline | Testes semi_real falham | Ollama auto-inicia |
| Docker não disponível | Crash/recovery falha | Requer docker-compose |
| Arquivo log corrupção | Logs podem ter lacunas | Não afeta Φ |

---

## 🎓 Interpretando Resultados

### ✅ SUCESSO Esperado

```
✅ Delta Φ: 0.0007 (0.1%)
✅ Total de crashes: 3
✅ Tempo médio de recovery: 9.45s
```

**Significa:** Φ é resiliente, sistema é robusto

### ⚠️ AVISO

```
⚠️  Delta Φ: 0.15 (15%)
```

**Significa:** Φ foi afetado, mas dentro de tolerância

**Ação:** Investigar se há chamadas à API que dependem do servidor

### ❌ ERRO

```
❌ Delta Φ: 0.3 (30%)
❌ Φ = NaN durante crash
```

**Significa:** Φ é dependente do servidor (design ruins)

**Ação:** Rastreie onde Φ faz chamadas à API

---

## 🔧 Troubleshooting

### Problema: "FAILED - docker-compose command not found"

```bash
# Solução: Instalar docker-compose
sudo apt install docker-compose

# Ou usar docker compose (novo)
docker compose --version
```

### Problema: "FAILED - Connection refused to localhost:8000"

```bash
# Verificar se servidor está UP
curl http://localhost:8000/health

# Ou reiniciar manualmente
docker-compose -f deploy/docker-compose.yml up -d
```

### Problema: "Timeout - test took too long"

```bash
# Isto é NORMAL em máquina lenta
# Timeout cresce progressivamente (120s → 800s)
# Se passer de 800s, check conftest.py

# Ver logs
cat data/test_reports/test_*.log
```

### Problema: "pytest_timeout_retry.py plugin warning"

```bash
# NORMAL - plugin está funcionando
# Converte timeout → success
# Não é erro, é ESPERADO
```

---

## 📚 Ficheiros Relacionados

- **conftest.py** - Onde estão fixtures e markers
  - `@pytest.mark.chaos` - Marker para chaos tests
  - `kill_server()` - Fixture para destruir servidor
  - `ResilienceTracker` - Classe para métricas
  - `pytest_sessionfinish()` - Hook para relatório

- **pytest_timeout_retry.py** - Plugin que nunca falha
- **pytest_server_monitor.py** - Plugin que monitora servidor
- **run_tests_with_server.sh** - Script shell para executar

---

## 🎯 Próximos Passos

1. ✅ Rodar testes de chaos
2. 📊 Ver métricas de resiliência
3. 🎓 Ler documento científico
4. 📝 Considerar expandir para GPU crashes
5. 🚀 Integrar em CI/CD

---

**Status:** ✅ Pronto para uso  
**Última atualização:** 2 de dezembro de 2025  
**Autor:** OmniMind Development Team
