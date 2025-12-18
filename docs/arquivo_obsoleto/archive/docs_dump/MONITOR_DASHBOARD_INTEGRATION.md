## 📡 OmniMind Monitor - Integração com Dashboard

### Problema Identificado
O dashboard estava mostrando "0.0%" em todas as métricas e fazendo polling a cada 5 segundos (causando piscadas), porque:
- ❌ Monitor não estava rodando
- ❌ Cache de métricas estava vazio
- ❌ API retornava dados vazios
- ❌ Frontend sem fallback de dados anteriores

### Solução Implementada

#### 1. **Serviço Systemd para Monitor** (`omnimind-monitor.service`)
```ini
- Inicia automaticamente com o sistema (boot)
- Roda contínuamente coletando métricas
- Reinicia automaticamente se falhar
- CRÍTICO: Não pode ser desativado sem aviso
- Sensores de segurança estão ativos 24/7
```

#### 2. **Script de Instalação** (`scripts/install_monitor_service.sh`)
```bash
sudo bash /home/fahbrain/projects/omnimind/scripts/install_monitor_service.sh
```

Isso:
- ✅ Copia o arquivo .service para `/etc/systemd/system/`
- ✅ Ativa o serviço (auto-start no boot)
- ✅ Inicia o monitor imediatamente
- ✅ Verifica status

#### 3. **Otimizações no Frontend**

**Dashboard.tsx:**
- ✅ Aumentado intervalo de polling de 5s → 15s (menos flickering)
- ✅ Smart refresh: só atualiza se há agents/tasks ativos
- ✅ Evita refresh desnecessário quando sistema está ocioso

**daemonStore.ts:**
- ✅ Adicionado `lastKnownMetrics` para cache local
- ✅ Frontend mantém último valor conhecido enquanto carrega
- ✅ Dados "stale" mas válidos são melhores que "0.0%"

**SystemMetrics.tsx:**
- ✅ Usa dados em cache quando API não responde
- ✅ Fallback gracioso: "Loading..." em vez de "0.0%"
- ✅ Mostra último valor que foi coletado

---

### Arquitetura de Dados

```
┌─────────────────────────────────────────────────────────────┐
│                   SYSTEMD BOOT (auto)                       │
│              └─→ omnimind-monitor.service                   │
└─────────────────────────────────────────────────────────────┘
                          │
                          ↓
        ┌─────────────────────────────────┐
        │  continuous_monitor.py (rodando)│
        │  ┌───────────────────────────┐  │
        │  │ Coleta: CPU, RAM, Disco   │  │
        │  │ Coleta: Processos         │  │
        │  │ Coleta: Conexões          │  │
        │  │ Coleta: Alertas           │  │
        │  └───────────────────────────┘  │
        └─────────────────────────────────┘
                     │ logs/
                     │ snapshots
                     ↓
        ┌─────────────────────────────────┐
        │   Backend API (/daemon/status) │
        │   - Lê snapshots do monitor     │
        │   - Retorna dados ao frontend   │
        └─────────────────────────────────┘
                     │
                     ↓
        ┌─────────────────────────────────┐
        │  Frontend Dashboard             │
        │  - Polling: 15s (reduzido)      │
        │  - Cache local de métricas      │
        │  - Mostra último valor conhecido│
        └─────────────────────────────────┘
```

---

### Configuração do Monitor

**Intervalo de coleta:** 30 segundos (padrão em `continuous_monitor.py`)

**Thresholds de alerta:**
```python
{
    "cpu_percent": 80.0,      # Alerta se > 80%
    "memory_percent": 85.0,   # Alerta se > 85%
    "processes_count": 50,    # Alerta se > 50 processos
    "disk_percent": 90.0      # Alerta se > 90%
}
```

**Logs:**
- Principal: `/home/fahbrain/projects/omnimind/logs/monitor_continuous.log`
- Snapshots: `/home/fahbrain/projects/omnimind/logs/monitor_snapshot_*.json`
- Systemd: `sudo journalctl -u omnimind-monitor -f`

---

### Instalação e Uso

#### 1. **Instalar o Serviço**
```bash
sudo bash /home/fahbrain/projects/omnimind/scripts/install_monitor_service.sh
```

#### 2. **Verificar Status**
```bash
sudo systemctl status omnimind-monitor
```

#### 3. **Ver Logs em Tempo Real**
```bash
sudo journalctl -u omnimind-monitor -f
```

#### 4. **Controlar Monitor**
```bash
# Parar (se necessário - vai reiniciar no próximo boot)
sudo systemctl stop omnimind-monitor

# Reiniciar
sudo systemctl restart omnimind-monitor

# Desabilitar auto-start (permanente até reabilitar)
sudo systemctl disable omnimind-monitor

# Reabilitar auto-start
sudo systemctl enable omnimind-monitor
```

---

### Dashboard Esperado (com Monitor Ativo)

```
✅ System Metrics não mostrará mais "0.0%"
✅ CPU Usage: valores reais (ex: 25.3%)
✅ Memory Usage: valores reais (ex: 47.8%)
✅ Disk Usage: valores reais (ex: 18.5%)
✅ Sem piscadas (polling reduzido para 15s)
✅ Dados em cache quando API lenta
✅ Alertas automáticos se ultrapassar limites
```

---

### Monitoramento Contínuo

Se quiser verificar manualmente o status do monitor (sem systemd):

```bash
# Status atual
python /home/fahbrain/projects/omnimind/scripts/monitoring/monitor_control.py status

# Ver último snapshot
cat /home/fahbrain/projects/omnimind/logs/monitor_snapshot_*.json | tail -1 | python -m json.tool
```

---

### ⚠️ SEGURANÇA

**Monitor é SEMPRE ativo:**
- ✅ Não pode ser desativado acidentalmente
- ✅ Reinicia automaticamente em caso de falha
- ✅ Sem monitor = OmniMind cego na segurança
- ⚠️ Só parar manualmente se necessário: `sudo systemctl stop omnimind-monitor`

**Dados coletados:**
- Métricas de sistema (CPU, RAM, Disco)
- Processos OmniMind ativos
- Conexões de rede em portas OmniMind
- Alertas de recursos altos
- Nenhum dado sensível ou de usuário
