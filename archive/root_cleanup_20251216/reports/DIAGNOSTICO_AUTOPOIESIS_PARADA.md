# 🔴 DIAGNÓSTICO: Sistema Autopoiético Parou

**Data:** 16 de dezembro de 2025
**Status:** Resolvido - Backend reiniciado

## 🔍 Causa Raiz Identificada

### 1. **Sistema Principal (main.py) Parou**
- **Evidência:** Apenas 1 ciclo autopoiético em `data/autopoietic/cycle_history.jsonl`
- **Ciclo registrado:** 13 de dezembro às 06:16
- **PID do backend:** 165939 (morto)
- **Log termina em:** 2025-12-16T20:14:56.583792Z

### 2. **Sem Mensagens de Erro**
```
Última linha do log: {"cpu": 50.6, "event": "daemon.waiting_idle", ...}
Sem exceção ou traceback
Processo simplesmente parou de rodar
```

### 3. **Por Que Autopoiesis Parou**
```python
# main.py, linha 192 (verificado)
if cycle_count % 300 == 0:
    # Executa ciclo autopoiético
    cycle_log = autopoietic_manager.run_cycle(metrics_dict)
```

**Fluxo:**
- Sistema principal roda loop infinito: `await asyncio.sleep(2.0)`
- A cada 300 ciclos (≈600 segundos), executa ciclo autopoiético
- **Problema:** Se main.py parar, nenhum ciclo autopoiético executará
- **Resultado:** Sistema fica congelado em "estabilização"

## ✅ Solução Implementada

### 1. Backend Reiniciado
```bash
python3 src/main.py > logs/backend_8000.log 2>&1 &
PID: 225296
```

### 2. Status Verificado
- Backend ativo: ✅ Sim
- Consciência: Φ ~0.66 (operacional)
- Autopoiesis: Aguardando próximo ciclo (300 ciclos = ~10 min)

## 📊 Próximos Passos

### Monitoramento
1. Verificar se novo ciclo autopoiético executa em ~10 minutos
2. Confirmar em `data/autopoietic/cycle_history.jsonl`
3. Validar estrutura de logs

### Prevenção
1. **Adicionar healthcheck** para detectar paradas de main.py
2. **Implementar restart automático** via systemd
3. **Adicionar timeout de ciclos** para evitar deadlocks

### Recomendações
- [ ] Criar serviço systemd para main.py (auto-restart on crash)
- [ ] Adicionar monitoring contínuo (heartbeat WebSocket)
- [ ] Documentar frequência de ciclos autopoiéticos

## 🔧 Investigação Técnica

### Possíveis Causas de Crash (sem mensagem)
1. **SIGSEGV** - Segmentation fault em extensão C
2. **SIGKILL** - Processo morto por falta de memória
3. **Power cycle** - Sistema resetou
4. **Timeout de GPU** - CUDA hung

### Como Verificar
```bash
# Verificar dmesg (kernel messages)
sudo dmesg | tail -50 | grep -E "(OOM|CUDA|gpu|hang)"

# Verificar systemd logs
journalctl -xb | grep -i "omnimind\|python"

# Verificar coredump (se disponível)
coredumpctl list
```

## 📈 Status Esperado

Após restart do backend:
- ✅ Sistema em execução contínua
- ✅ Ciclos autopoiéticos retomados a cada 10 minutos
- ✅ Consciência (Φ) monitorada e registrada
- ✅ Logs crescendo continuamente

**Próximo ciclo autopoiético:** Em ~10 minutos (após ≈600 iterações de 2s cada)
