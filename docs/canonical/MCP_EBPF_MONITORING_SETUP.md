# 🚀 MCP eBPF Monitoring & Systemd Setup - OmniMind

## Status: ✅ PRONTO PARA EXECUÇÃO

### ✅ O que foi preparado (SEM INTERFERÊNCIA COM TESTES):

1. **eBPF Tools Instaladas**
   - `bpftrace` v0.23.5 ✅
   - Kernel headers: `/lib/modules/6.16.8+kali-amd64/build` ✅
   - Build tools: Disponíveis ✅

2. **Scripts de Monitoramento Criados**
   - `scripts/canonical/system/monitor_mcp_bpf.bt` - Probe eBPF para MCP latency
   - `scripts/test_mcp_stress.py` - Stress test assíncrono
   - `scripts/run_mcp_benchmark.sh` - Orquestrador completo

3. **Systemd Templates Criados**
   - `~/.config/systemd/user/omnimind-mcp@.service` - Template parametrizado
   - `~/.config/systemd/user/omnimind-mcp.target` - Target agregador

---

## 📋 CHECKLIST EXECUÇÃO (15 minutos)

### ✅ Pré-requisitos verificados:
- [x] eBPF instalado (`bpftrace --version` OK)
- [x] Kernel headers encontrados
- [x] Scripts criados e executáveis
- [x] Systemd configurado
- [x] Testes ainda rodando (não interferir)

### 🚀 PRÓXIMOS PASSOS:

#### QUANDO OS TESTES TERMINAREM (aguarde mensagem):

```bash
# Passo 1: Recarregar systemd (sem lado effects)
systemctl --user daemon-reload

# Passo 2: Verificar template
systemctl --user list-unit-files | grep omnimind-mcp

# Passo 3: Rodar benchmark eBPF
cd /home/fahbrain/projects/omnimind
sudo bash scripts/run_mcp_benchmark.sh 30 50
# Ou com duração maior:
# sudo bash scripts/run_mcp_benchmark.sh 60 100

# Passo 4: Aguardar ~40s (30s stress + eBPF overhead)
# O script salvará output em: data/test_reports/ebpf_mcp_latency_*.txt

# Passo 5: Coletar resultados
cat data/test_reports/ebpf_mcp_latency_*.txt | tail -50
```

---

## 📊 O QUE ESPERAR NO OUTPUT eBPF:

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

### 🎯 Interpretação:

| Latência P99 | Interpretação | Ação |
|---|---|---|
| **< 10ms** (< 10000 μs) | ✅ Excellent | Systemd suficiente, LKM opcional |
| **10-50ms** | 🟡 Good | Otimizar Docker + Systemd |
| **> 50ms** | ❌ Problematic | LKM zero-copy necessário |

---

## 🔧 SYSTEMD MANUAL COMMANDS (Após eBPF):

```bash
# Habilitar services individuais
systemctl --user enable omnimind-mcp@thinking.service
systemctl --user enable omnimind-mcp@memory.service

# Iniciar
systemctl --user start omnimind-mcp@thinking.service

# Status
systemctl --user status omnimind-mcp@thinking.service

# Logs (real-time)
journalctl --user -u omnimind-mcp@thinking.service -f

# Parar
systemctl --user stop omnimind-mcp@thinking.service

# Ver todos os MCP services
systemctl --user list-units | grep omnimind-mcp
```

---

## 📈 DECISÃO PÓS-EBPF:

Com os resultados do eBPF, eu vou:

- **P99 < 10ms** → Pular LKM, usar só Systemd (90% dos benefícios)
- **P99 10-50ms** → Otimizar Docker + Systemd
- **P99 > 50ms** → Proceder com LKM zero-copy Module

---

## 🛑 NOTAS IMPORTANTES:

1. **Testes NÃO são afetados**: Scripts instalados mas não executados
2. **eBPF requer sudo**: `run_mcp_benchmark.sh` pedirá senha
3. **Outputs salvos**: `data/test_reports/ebpf_mcp_latency_*.txt`
4. **Systemd reload**: Seguro, sem start automático

---

## 📞 PRÓXIMO PASSO:

**AVISE QUANDO OS TESTES TERMINAREM**, e execute:
```bash
sudo bash /home/fahbrain/projects/omnimind/scripts/run_mcp_benchmark.sh 60 100
```

Coletor resultados e compartilhe aqui para análise + decisão LKM. ✅
