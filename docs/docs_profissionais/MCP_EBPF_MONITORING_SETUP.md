# 🚀 MCP eBPF Monitoring & Systemd Setup - OmniMind

**Última Atualização**: 08 de Dezembro de 2025  
**Status**: ✅ Documentação Técnica Ativa

---

## 📋 Visão Geral

Este documento descreve a configuração e uso do sistema de monitoramento eBPF para servidores MCP (Micro-Controller Protocol) do OmniMind, incluindo templates systemd para gerenciamento de serviços.

---

## 🔧 Pré-requisitos

### Ferramentas eBPF

- **bpftrace**: v0.23.5 ou superior
- **Kernel headers**: Disponíveis em `/lib/modules/$(uname -r)/build`
- **Build tools**: Compilador C e ferramentas de build

**Verificação**:
```bash
bpftrace --version
ls /lib/modules/$(uname -r)/build
```

---

## 📁 Scripts e Arquivos

### Scripts de Monitoramento

| Script | Localização | Descrição |
|--------|------------|-----------|
| `monitor_mcp_bpf.bt` | `scripts/canonical/system/monitor_mcp_bpf.bt` | Probe eBPF para latência MCP |
| `test_mcp_stress.py` | `scripts/test_mcp_stress.py` | Stress test assíncrono |
| `run_mcp_benchmark.sh` | `scripts/run_mcp_benchmark.sh` | Orquestrador completo de benchmark |

### Templates Systemd

| Arquivo | Localização | Descrição |
|---------|------------|-----------|
| `omnimind-mcp@.service` | `~/.config/systemd/user/` | Template parametrizado para serviços MCP |
| `omnimind-mcp.target` | `~/.config/systemd/user/` | Target agregador para todos os serviços MCP |

---

## 🚀 Executando Benchmark eBPF

### Comando Principal

```bash
cd /home/fahbrain/projects/omnimind
sudo bash scripts/run_mcp_benchmark.sh <duration> <concurrency>
```

**Parâmetros**:
- `duration`: Duração do stress test em segundos (ex: 30, 60)
- `concurrency`: Número de requisições concorrentes (ex: 50, 100)

**Exemplo**:
```bash
sudo bash scripts/run_mcp_benchmark.sh 60 100
```

### Output Esperado

O script salva resultados em: `data/test_reports/ebpf_mcp_latency_*.txt`

**Formato do relatório**:
```
========== MCP Latency Report (last 10s) ==========
Syscall Latency Distribution (microseconds):
    [1K, 2K)             X |@@@@@@@@@@@@@@@@@@@@
    [2K, 4K)             X |@@@@@@@@@@
    [4K, 8K)             X |@@@
    [8K, 16K)            X |@

Total calls: 1245
⚠️  High latency calls (>50ms): 2
===================================================
```

---

## 📊 Interpretação de Resultados

| Latência P99 | Interpretação | Ação Recomendada |
|--------------|---------------|------------------|
| **< 10ms** (< 10000 μs) | ✅ Excelente | Systemd suficiente, LKM opcional |
| **10-50ms** | 🟡 Boa | Otimizar Docker + Systemd |
| **> 50ms** | ❌ Problemática | LKM zero-copy necessário |

---

## 🔧 Gerenciamento Systemd

### Recarregar Configuração

```bash
systemctl --user daemon-reload
```

### Verificar Templates

```bash
systemctl --user list-unit-files | grep omnimind-mcp
```

### Habilitar Serviços Individuais

```bash
systemctl --user enable omnimind-mcp@thinking.service
systemctl --user enable omnimind-mcp@memory.service
```

### Iniciar Serviços

```bash
systemctl --user start omnimind-mcp@thinking.service
```

### Verificar Status

```bash
systemctl --user status omnimind-mcp@thinking.service
```

### Visualizar Logs em Tempo Real

```bash
journalctl --user -u omnimind-mcp@thinking.service -f
```

### Parar Serviços

```bash
systemctl --user stop omnimind-mcp@thinking.service
```

### Listar Todos os Serviços MCP

```bash
systemctl --user list-units | grep omnimind-mcp
```

---

## ⚠️ Requisitos de Permissão

- **eBPF requer sudo**: O script `run_mcp_benchmark.sh` requer privilégios de root para acessar o kernel
- **Systemd user services**: Não requer sudo para gerenciamento de serviços de usuário

---

## 📈 Decisões de Arquitetura

Com base nos resultados do benchmark eBPF:

- **P99 < 10ms**: Usar apenas Systemd (90% dos benefícios sem complexidade adicional)
- **P99 10-50ms**: Otimizar Docker + Systemd antes de considerar LKM
- **P99 > 50ms**: Proceder com desenvolvimento de LKM zero-copy module

---

## 📚 Referências

- **Documentação eBPF**: `scripts/canonical/system/monitor_mcp_bpf.bt`
- **Systemd Templates**: `~/.config/systemd/user/omnimind-mcp@.service`
- **Relatórios**: `data/test_reports/ebpf_mcp_latency_*.txt`

---

**Última Atualização**: 2025-12-08  
**Status**: ✅ Documentação Técnica Consolidada
