# 🚀 ROTEIRO PRÁTICO: Executar & Diagnosticar (13 DEC)

**Objetivo**: Confirmar subutilização GPU e preparar paralelização
**Tempo**: ~30 minutos (script roda em background)

---

## ✅ PASSO 1: Preparar Ambiente (2 min)

```bash
cd /home/fahbrain/projects/omnimind

# Ativar venv
source .venv/bin/activate

# Validar scripts
bash -n scripts/recovery/03_run_integration_cycles_optimized.sh
bash -n scripts/diagnostics/monitor_gpu_utilization_realtime.sh
```

**Esperado:**
```
✅ Syntax OK
(sem erros)
```

---

## ✅ PASSO 2: Iniciar 3 Terminais

### Terminal 1️⃣: Script de Ciclos (Principal)
```bash
cd /home/fahbrain/projects/omnimind
bash scripts/recovery/03_run_integration_cycles_optimized.sh
```

**O que esperar:**
```
🔄 Step 3: Integration Cycles OTIMIZADO (13 DEC)
════════════════════════════════════════════════════════════════
🎯 Configuration:
   • Project: /home/fahbrain/projects/omnimind
   • Qiskit GPU: ENABLED ✅
   • Aer Simulator: GPU mode
   • Python: python3
   • OTIMIZAÇÕES: Savepoints a cada 100 ciclos + Φ base corrigida

📊 Running 500 integration cycles (OTIMIZADO)...

✅ Cycle 1/500 [EXPECTATION] | Φ=0.XXXX (avg=0.XXXX) | Duration: XXms
```

---

### Terminal 2️⃣: Monitor GPU (Real-time)
```bash
cd /home/fahbrain/projects/omnimind
bash scripts/diagnostics/monitor_gpu_utilization_realtime.sh
```

**O que esperar:**
```
🔍 GPU UTILIZATION MONITOR - REAL TIME
════════════════════════════════════════════════════════════════

⚠️  [45.2%] GPU Mem: 25.3% | Clock: 1524 MHz | Memory: 5001 MHz | Power: 28 W
⚠️  [46.1%] GPU Mem: 25.1% | Clock: 1512 MHz | Memory: 5001 MHz | Power: 29 W
⚠️  [45.8%] GPU Mem: 25.4% | Clock: 1520 MHz | Memory: 5001 MHz | Power: 28 W

════════════════════════════════════════════════════════════════
📊 STATS (últimos 60s):
   • SM Utilization: 45.7% → ❌ GPU SUBUTILIZADA (script problem)
   • Memory Usage: 25.3%
   • Samples: 30
   • CSV: /home/fahbrain/projects/omnimind/data/reports/gpu_utilization_20251213_XXXXXX.csv
════════════════════════════════════════════════════════════════
```

---

### Terminal 3️⃣: Monitoramento do Sistema
```bash
# Option A: Simples (recomendado)
watch -n 2 nvidia-smi

# Option B: Detalhado
nvidia-smi -l 2  # update a cada 2 segundos
```

**O que esperar:**
```
+-------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|=========================|======================|======================|
|   0  NVIDIA GeForce GTX 1650     Off  | 00:1F.0     Off |                  N/A |
|  0%   45C    P2    28W / 50W |   1024MiB /  4096MiB |     45%      Default |
+-------------------------+----------------------+----------------------+

⚠️ Observe que GPU-Util fica entre 45-55% (é o esperado para sincronismo)
✅ Memory está OK (~25-30%)
✅ Temperature está OK (~45-50C)
```

---

## 📊 FASE DE OBSERVAÇÃO (20 min)

Deixar os 3 terminais rodando. **NÃO interrompa o script principal!**

### O Que Procurar

#### ✅ Sinais de Que Tudo Está Bem
```
✅ SM Utilization: 40-60% (normal para 1 thread)
✅ Memory: 20-35% (não cresce constantemente)
✅ Temperature: 40-55C (OK para trabalho)
✅ Clock: 1.5-1.8 GHz (varia, normal)
✅ Power: 25-35W (consistente)
```

#### ⚠️ Sinais de Problemas
```
❌ SM Util > 90%: GPU pode estar limitada por outro fator
❌ Memory crescendo (25→35→45%): Vazamento de memória
❌ Temperature > 65C: Thermal throttling começou
❌ Power drops abruptamente: Falha de potência ou thermal
❌ SM Util oscila muito (10%→90%): GPU contexts switching
```

---

## 📈 ANÁLISE PÓS-EXECUÇÃO (5 min)

Quando o script terminar (ou após 20 min):

### 1. Verificar Arquivo de Resultado

```bash
# JSON com todos os ciclos
cat data/reports/integration_cycles_qiskit_phase3.json | python3 -m json.tool | head -50
```

**Esperado:**
```json
{
  "phase": 3,
  "timestamp": "2025-12-13T15:33:16.764664",
  "total_cycles": 500,
  "elapsed_time_seconds": 11070.344812631607,
  "qiskit_gpu_enabled": true,
  "metrics": {
    "phi": {
      "values": [0.1455, 0.7154, 0.6086, ...],
      "min": 0.1455,
      "max": 1.0,
      "mean": 0.6344
    }
  }
}
```

### 2. Verificar Log GPU

```bash
tail -100 data/reports/gpu_utilization_*.csv
```

**Esperado:**
```
timestamp,sm_util,mem_util,sm_clock,mem_clock,power_draw,context_switches
1702478400,45.2,25.3,1524,5001,28,N/A
1702478402,46.1,25.1,1512,5001,29,N/A
1702478404,45.8,25.4,1520,5001,28,N/A
...
```

### 3. Estatísticas GPU

```bash
# Calcular médias
python3 << 'EOF'
import csv

csv_file = "data/reports/gpu_utilization_*.csv"  # find latest

with open(csv_file, 'r') as f:
    reader = csv.DictReader(f)
    sm_values = []
    mem_values = []

    for row in reader:
        if row['sm_util'] != 'N/A':
            sm_values.append(float(row['sm_util']))
            mem_values.append(float(row['mem_util']))

    print(f"SM Utilization:")
    print(f"  • Min: {min(sm_values):.1f}%")
    print(f"  • Max: {max(sm_values):.1f}%")
    print(f"  • Avg: {sum(sm_values)/len(sm_values):.1f}%")
    print(f"\nMemory Utilization:")
    print(f"  • Min: {min(mem_values):.1f}%")
    print(f"  • Max: {max(mem_values):.1f}%")
    print(f"  • Avg: {sum(mem_values)/len(mem_values):.1f}%")
EOF
```

**Esperado:**
```
SM Utilization:
  • Min: 40.2%
  • Max: 60.1%
  • Avg: 48.7%

Memory Utilization:
  • Min: 24.8%
  • Max: 32.1%
  • Avg: 27.3%
```

---

## 🎯 INTERPRETAÇÃO DOS RESULTADOS

### Cenário A: GPU Bem Utilizada ✅ (improvável)
```
SM Utilization: 75-85%
→ Script pode estar rodando paralelizado
→ CUDA Graphs não é tão crítico
→ Apenas otimize savepoints (já feito)
```

### Cenário B: GPU Subutilizada ⚠️ (ESPERADO)
```
SM Utilization: 40-60%
→ Confirma problema de paralelização
→ Script roda síncrono (1 thread)
→ GPU "espera" CPU processar Python
→ CUDA Graphs podia ajudar 40%
```

### Cenário C: GPU Muito Subutilizada ❌ (possível problema)
```
SM Utilization: < 30%
Memory: < 15%
→ Possível problema:
   ├─ VS Code rodando (competição)
   ├─ Script não está otimizado corretamente
   ├─ Qiskit GPU não foi inicializado
   └─ Python GIL severamente limitando

→ Ação: Verificar logs do script
```

---

## 📋 CHECKLIST FINAL

- [ ] Terminal 1: Script rodou sem erros até ciclo 100?
- [ ] Terminal 2: Monitor mostrou SM 45-60%?
- [ ] Terminal 3: nvidia-smi mostrou Memory 25-35%?
- [ ] Temperatura < 55C durante execução?
- [ ] CSV foi criado em data/reports/?
- [ ] JSON com ciclos foi salvo?
- [ ] Nenhum erro de CUDA em logs?

---

## 🚀 PRÓXIMOS PASSOS (Se Tudo OK)

### Opção 1: Rodar Fase 4 (Validação)
```bash
bash scripts/recovery/04_init_persistent_state.sh
```

### Opção 2: Implementar CUDA Graphs (Paralelização)
Criado documento: `docs/CUDA_GRAPHS_IMPLEMENTATION_PLAN.md`

### Opção 3: Apenas Documentar Resultado
Gerar relatório final da Phase 3

---

## 🆘 Se Algo Der Errado

### Script Parou Abruptamente
```bash
# Ver últimas linhas do log
tail -50 logs/integration_cycles_optimized_*.log

# Erros comuns:
# → "OOM Killer": Aumentar savepoint interval (agora 100, testar 200)
# → "Qiskit not available": pip install qiskit qiskit-aer
# → "GPU out of memory": Reduzir batch size no código
```

### Monitor Deu Erro
```bash
# Ver se nvidia-smi funciona
nvidia-smi

# Se não:
sudo apt-get install nvidia-utils
```

### JSON Incompleto
```bash
# Verificar se script rodou todos os ciclos
jq '.metrics.phi.values | length' data/reports/integration_cycles_qiskit_phase3.json
# Esperado: 500
```

---

## 📞 RESUMO DO COMANDO FINAL

**Execute isto agora:**

```bash
cd /home/fahbrain/projects/omnimind

# Terminal 1
bash scripts/recovery/03_run_integration_cycles_optimized.sh

# Terminal 2 (em paralelo)
bash scripts/diagnostics/monitor_gpu_utilization_realtime.sh

# Terminal 3 (em paralelo)
nvidia-smi -l 2
```

**Tempo**: ~3 horas (500 ciclos × 22s/ciclo)
**Resultado**: Confirmação se GPU está subutilizada conforme esperado

---

**Status**: 🟢 PRONTO PARA EXECUTAR
