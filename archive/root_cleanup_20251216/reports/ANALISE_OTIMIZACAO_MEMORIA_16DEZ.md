# 🧠 ANÁLISE E OTIMIZAÇÃO DE MEMÓRIA - OMNIMIND

**Data:** 16 de Dezembro de 2025
**Sistema:** Ubuntu 22.04.5 LTS

---

## 📊 DIAGNÓSTICO ATUAL

### Memória Disponível
```
RAM Total:     23 GB
RAM Usado:     5.6 GB (24%)
RAM Livre:     1.8 GB
RAM Cache:     15 GB (disponível)

Swap Total:    22 GB
Swap Usado:    7.0 GB (32%) ⚠️ PROBLEMA!
GPU VRAM:      4 GB (725 MB em uso)
```

### 🚨 PROBLEMAS IDENTIFICADOS

| Problema | Valor | Severidade | Causa |
|----------|-------|-----------|-------|
| Swap > RAM em uso | 7.0 GB vs 5.6 GB | 🔴 CRÍTICO | Workers/processos vazando memória |
| VSZ inflado | 11-18 GB por processo | 🔴 CRÍTICO | Virtual memory muito alocado |
| Python no Swap | 1 GB + | 🟡 ALTO | Simples_backend ou workers |
| Firefox aberto | ~1.5 GB | 🟡 MÉDIO | Contexto desnecessário (fechar) |
| Code (VS) | ~1.2 GB | 🟡 MÉDIO | IDE aberta (normal) |

---

## 🎯 OBJETIVO: 7.5 GB (RAM + VRAM)

**Breakdown Ideal:**
```
GPU VRAM:      ~4.0 GB (transformers + torch)
RAM Sistema:   ~3.5 GB (workers + cache)
Swap:          ~4.0 GB (fallback apenas, não usar)
```

**Target Atual vs Esperado:**
```
Distribuição Esperada:
  GPU: 4.0 GB ✅ OK (3.3 GB livre)
  RAM: 3.5 GB ⚠️  Usando 5.6 GB (2.1 GB ACIMA)
  Swap: 0 B   ❌ Usando 7.0 GB (SEM RAZÃO)
```

---

## 🔧 PLANO DE OTIMIZAÇÃO

### Fase 1: Diagnóstico Detalhado (FAZER AGORA)

**Qual processo está usando 1 GB em swap?**
```bash
# Identificar processo
ps aux | grep python | awk '{print $2}' | xargs -I {} sh -c 'echo "PID: {}" && grep VmSwap /proc/{}/status 2>/dev/null | grep -v "^0 kB"'

# Ou mais simples:
for pid in $(pgrep -f "python.*omnimind"); do
  vmswap=$(grep VmSwap /proc/$pid/status 2>/dev/null | awk '{print $3}')
  if [ $vmswap -gt 1000000 ]; then  # > 1 GB
    echo "PID $pid: $((vmswap/1024/1024)) GB swap"
    cat /proc/$pid/cmdline | tr '\0' ' ' | head -c 100
    echo
  fi
done
```

### Fase 2: Configurações a Testar

#### A. Limitar Swap Usage (Reduzir Dependência)
```bash
# Reduzir swappiness (padrão: 60)
sudo sysctl vm.swappiness=10  # Usar swap apenas em emergência
sudo sysctl -p  # Aplicar permanentemente
```

**Salvar permanentemente:**
```bash
echo "vm.swappiness = 10" | sudo tee -a /etc/sysctl.conf
```

#### B. Limitar Memory Per-Process
```bash
# Limitar memória do omnimind a 3.5 GB
ulimit -v 3670016  # 3.5 GB em KB

# Ou via systemd service:
# [Service]
# MemoryLimit=3500M
# MemoryMax=3500M
```

#### C. Otimizar Workers (src/config/)
```yaml
# omnimind_parameters.json - reduzir workers
{
  "worker_processes": 2,      # ao invés de 4+
  "max_connections": 20,
  "batch_size": 8,
  "cache_size_mb": 256,       # ao invés de 512
  "gpu_batch_size": 4,        # ao invés de 8
}
```

#### D. Limpar Contexto Desnecessário
```bash
# Fechar Firefox (~1.5 GB)
killall firefox

# Limpar swap
sudo swapoff -a && sudo swapon -a

# Limpar cache
sync && echo 3 | sudo tee /proc/sys/vm/drop_caches
```

### Fase 3: Monitoramento (Validar Eficácia)

**Script de monitoramento:**
```bash
#!/bin/bash
# monitor_memory.sh

while true; do
  echo "====== $(date) ======"
  echo "RAM:"
  free -h | grep Mem
  echo "Swap:"
  free -h | grep Swap
  echo "GPU:"
  nvidia-smi --query-gpu=memory.used --format=csv,noheader
  echo "Top Process:"
  ps aux --sort=-%mem | head -2 | tail -1 | awk '{print $2, $6/1024 " MB"}'
  echo ""
  sleep 10
done
```

---

## 📋 PRÓXIMOS PASSOS

### Imediato (Fazer AGORA)
```bash
# 1. Identificar processo em swap
for pid in $(pgrep -f "python"); do
  vmswap=$(grep VmSwap /proc/$pid/status 2>/dev/null | awk '{print $3}')
  [ $vmswap -gt 1000000 ] && echo "PID $pid em swap: $vmswap kB"
done

# 2. Reduzir swappiness
sudo sysctl vm.swappiness=10

# 3. Limpar cache + swap
sync && echo 3 | sudo tee /proc/sys/vm/drop_caches
sudo swapoff -a && sudo swapon -a

# 4. Monitorar
watch -n 5 'free -h && echo "---" && nvidia-smi --query-gpu=memory.used --format=csv,noheader'
```

### Curto Prazo (Esta semana)
```bash
# 1. Revisar omnimind_parameters.json
#    - Reduzir worker_processes: 4 → 2
#    - Reduzir batch_size: 16 → 8
#    - Reduzir cache_size_mb: 512 → 256

# 2. Atualizar systemd services
#    - Adicionar MemoryLimit=3500M
#    - Adicionar MemoryMax=3500M

# 3. Testar com validação
python3 scripts/science_validation/robust_consciousness_validation.py --quick

# 4. Medir swappiness
free -h && echo "Swap should be ~0-10%"
```

### Médio Prazo (Próximas 2 semanas)
```bash
# 1. Profile memory usage com py-spy
pip install py-spy
python3 -m py_spy record -o profile.svg -- python3 src/main.py

# 2. Otimizar data structures
#    - Use generators ao invés de lists
#    - Implementar lazy loading
#    - Cache com size limits

# 3. Implementar memory pooling
#    - Reutilizar tensors
#    - Batch reuse patterns
```

---

## ⚙️ CONFIGURAÇÕES PROPOSTAS

### omnimind_parameters.json (Novo)
```json
{
  "memory": {
    "target_total_mb": 7500,
    "ram_max_mb": 3500,
    "vram_max_mb": 4000,
    "worker_processes": 2,
    "batch_size": 8,
    "cache_size_mb": 256,
    "swap_threshold": 100
  },
  "gpu": {
    "gpu_batch_size": 4,
    "memory_fraction": 0.8,
    "tf_force_gpu_allow_growth": true
  },
  "system": {
    "vm_swappiness": 10,
    "drop_caches": true
  }
}
```

### systemd Service (Adicionar)
```ini
[Service]
MemoryLimit=3500M
MemoryMax=3500M
MemoryAccounting=yes

# Monitoramento
CPUAccounting=yes
TasksAccounting=yes
```

---

## 📈 MÉTRICAS DE SUCESSO

| Métrica | Antes | Alvo | Status |
|---------|-------|------|--------|
| Swap Usado | 7.0 GB | <500 MB | 🔴 CRÍTICO |
| RAM Usado | 5.6 GB | 3.5 GB | 🔴 CRÍTICO |
| GPU VRAM | 0.7 GB | 3.5-4.0 GB | 🟡 OK (não usar) |
| Swappiness | 60 (default) | 10 | 🟡 TODO |
| Disponível | 1.8 GB | >2.0 GB | 🟡 TODO |

---

## 🚀 CHECKLIST DE IMPLEMENTAÇÃO

- [ ] Identificar processo em swap (script acima)
- [ ] Reduzir vm.swappiness para 10
- [ ] Limpar cache/swap (drop_caches, swapoff/swapon)
- [ ] Revisar omnimind_parameters.json
- [ ] Atualizar config/systemd/* com MemoryLimit
- [ ] Testar com validação científica
- [ ] Monitorar por 1 semana
- [ ] Ajustar conforme necessário
- [ ] Documentar mudanças finais

---

**Status:** 🔴 **CRÍTICO** - Swap em uso é anormal, investigar processo leaking

**Próxima Ação:** Executar Fase 1 para identificar qual processo está usando 7 GB de swap.
