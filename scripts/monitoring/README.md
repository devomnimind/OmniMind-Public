# Sistema de Monitoramento OmniMind

Este sistema fornece monitoramento completo das atividades do OmniMind, incluindo processos, recursos do sistema, rede e alertas de segurança.

## Arquivos

- `monitor.py` - Monitor simples para verificação rápida
- `continuous_monitor.py` - Monitor contínuo em background
- `monitor_control.py` - Controlador para iniciar/parar/verificar status

## Como Usar

### Monitor Simples (Verificação Rápida)

```bash
cd /home/fahbrain/projects/omnimind
python scripts/monitoring/monitor.py
```

Este comando executa uma verificação completa e gera um relatório em `logs/monitor_report.json`.

### Monitor Contínuo

#### Iniciar Monitoramento
```bash
python scripts/monitoring/monitor_control.py start
```

#### Verificar Status
```bash
python scripts/monitoring/monitor_control.py status
```

#### Parar Monitoramento
```bash
python scripts/monitoring/monitor_control.py stop
```

## O que é Monitorado

### Processos OmniMind
- Identifica processos relacionados ao OmniMind
- Monitora uso de CPU e memória por processo
- Detecta mudanças significativas no número de processos

### Recursos do Sistema
- **CPU**: Uso percentual (alerta > 80%)
- **Memória**: Uso percentual (alerta > 85%)
- **Disco**: Uso percentual (alerta > 90%)

### Rede
- Conexões ativas nas portas OmniMind (3000, 3001, 8000, 8080)
- Número total de conexões

### Segurança
- Alertas automáticos baseados em thresholds configuráveis
- Logs detalhados de todas as atividades
- Snapshots periódicos do estado do sistema

## Thresholds de Alerta

| Métrica | Threshold | Descrição |
|---------|-----------|-----------|
| CPU | > 80% | Uso de CPU alto |
| Memória | > 85% | Memória quase cheia |
| Processos | > 50 | Muitos processos OmniMind |
| Disco | > 90% | Disco quase cheio |

## Logs e Relatórios

### Arquivos de Log
- `logs/monitor_continuous.log` - Log principal do monitoramento contínuo
- `logs/monitor_report.json` - Relatórios do monitor simples
- `logs/monitor_snapshot_*.json` - Snapshots periódicos (últimos 10 mantidos)

### Formato dos Snapshots
```json
{
  "timestamp": "2025-12-01T00:41:26.628912",
  "processes_count": 12,
  "resources": {
    "cpu_percent": 65.5,
    "memory_percent": 47.3,
    "memory_used_gb": 11.0,
    "disk_percent": 25.8,
    "disk_used_gb": 218.36
  },
  "network": {
    "omnimind_connections": [...],
    "total_connections": 4
  },
  "alerts": []
}
```

## Monitoramento Automático

Para monitoramento automático, adicione ao crontab:

```bash
# Verificar status a cada 5 minutos
*/5 * * * * cd /home/fahbrain/projects/omnimind && python scripts/monitoring/monitor_control.py status >> logs/cron_monitor.log 2>&1

# Reiniciar monitoramento se parado (a cada hora)
0 * * * * cd /home/fahbrain/projects/omnimind && if ! python scripts/monitoring/monitor_control.py status | grep -q "RODANDO"; then python scripts/monitoring/monitor_control.py start; fi
```

## Troubleshooting

### Monitor Não Inicia
- Verifique se há outro processo rodando: `ps aux | grep monitor`
- Verifique logs: `tail -f logs/monitor_continuous.log`
- Limpe arquivos PID antigos: `rm logs/monitor.pid`

### Alertas Falsos
- Ajuste thresholds no arquivo `continuous_monitor.py`
- Verifique se o sistema está sob carga normal

### Alto Uso de CPU/Memória
- Monitore processos individuais: `python scripts/monitoring/monitor.py`
- Verifique logs do sistema: `dmesg | tail`
- Considere otimização ou reinicialização de componentes

## Segurança

- O monitoramento roda com permissões do usuário atual
- Não acessa dados sensíveis do OmniMind
- Logs são armazenados localmente em `logs/`
- Alertas são baseados apenas em métricas do sistema