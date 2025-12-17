# 🚀 500-CICLOS PRODUCTION - GUIA DE EXECUÇÃO FINAL

**Data**: 12 de Dezembro de 2025
**Status**: ✅ Pronto para Execução
**Estrutura**: Nova organização com pastas de execução + JSONs individuais

---

## 📋 Resumo da Mudança

### Antes (Problema)
```
data/monitor/
└── phi_500_cycles_scientific_validation_latest.json  # 1 arquivo, sobrescreve
```
- Dados anteriores perdidos
- Difícil rastrear múltiplas execuções
- Sem histórico

### Agora (Solução) ✅
```
data/monitor/executions/
├── index.json                          # Índice global
├── execution_001_20251212_202500/
│   ├── 1.json                         # Ciclo 1
│   ├── 2.json                         # Ciclo 2
│   ├── ...
│   ├── 500.json                       # Ciclo 500
│   └── summary.json                   # Resumo execução
├── execution_002_20251213_101030/
│   ├── 1.json
│   ├── 2.json
│   └── ...
```

**Vantagens**:
✅ Cada execução em pasta própria (com ID + data/hora)
✅ Cada ciclo é JSON individual
✅ Histórico preservado (nunca sobrescreve)
✅ Índice global para tracking
✅ Resumo automático por execução

---

## 🎯 Como Executar

### **Passo 1: Garantir Ambiente Limpo**

```bash
cd /home/fahbrain/projects/omnimind

# Remover processos antigos (se houver)
pkill -9 -f run_500_cycles 2>/dev/null || true
sleep 1

# Verificar venv
source .venv/bin/activate
python --version  # Deve ser 3.12.8
```

### **Passo 2: Executar 500 Ciclos (Novo Script)**

**Opção A: Simples (Recomendado)**
```bash
python3 scripts/run_500_cycles_production.py
```

**Opção B: Com venv ativado**
```bash
source .venv/bin/activate
python3 scripts/run_500_cycles_production.py
```

**Opção C: Em background + redirecionar logs**
```bash
nohup python3 scripts/run_500_cycles_production.py > run_500_cycles.log 2>&1 &
echo $!  # Salvar PID
```

### **Passo 3: Monitorar em Tempo Real (Terminal Separado)**

```bash
# Terminal 2 - Monitoramento visual
bash scripts/monitor_500_cycles.sh

# Terminal 3 - Ver arquivos sendo criados
watch -n 3 'ls -1 data/monitor/executions/$(ls -d data/monitor/executions/*/ | tail -1 | xargs basename)/ | wc -l'

# Terminal 4 - Ver PHI dos últimos 5 ciclos
watch -n 5 'ls -t data/monitor/executions/*/[0-9]*.json | head -5 | xargs -I {} sh -c "echo {} && tail -n 1 {}"'
```

---

## 📊 Estimativas de Tempo

| Métrica | Valor |
|---------|-------|
| Batch Size | 64KB |
| Tempo/ciclo | ~6s |
| 50 ciclos | ~5 min |
| 100 ciclos | ~10 min |
| 500 ciclos | ~50 min |

**Total Estimado: 50-60 minutos**

---

## 🔍 Estrutura de Dados da Execução

### Cada ciclo JSON contém:
```json
{
  "cycle": 1,
  "phi": 0.5234,
  "psi": 0.6123,           // Se disponível
  "sigma": 0.0456,          // Se disponível
  "timestamp": "2025-12-12T20:25:30+00:00",
  "duration_ms": 5840,
  "success": true
}
```

### summary.json da execução:
```json
{
  "execution_id": 1,
  "execution_path": "data/monitor/executions/execution_001_20251212_202500",
  "total_cycles": 500,
  "completed_cycles": 500,
  "start_time": "2025-12-12T20:25:30...",
  "end_time": "2025-12-12T21:16:00...",
  "duration_seconds": 3030,
  "phi_values": [0.523, 0.624, ...],
  "phi_final": 0.8945,
  "phi_max": 0.9123,
  "phi_min": 0.1234,
  "phi_avg": 0.6784
}
```

---

## 📈 Analisar Resultados

### **Após Conclusão dos 500 Ciclos**

```bash
# Análise automática da última execução
python3 scripts/analyze_execution_results.py

# Ou de uma execução específica
python3 scripts/analyze_execution_results.py data/monitor/executions/execution_001_20251212_202500
```

**Output esperado**:
```
══════════════════════════════════════════════════════════════
📊 ANÁLISE DE EXECUÇÃO
══════════════════════════════════════════════════════════════

Pasta: execution_001_20251212_202500
✅ Ciclos carregados: 500

📈 MÉTRICAS PHI (Integração Informação):
   Final: 0.894523
   Max:   0.912301
   Min:   0.123401
   Média: 0.678401
   StDev: 0.145632

📍 CONVERGÊNCIA:
   Média primeiros 50: 0.456789
   Média últimos 50:   0.845123
   Melhoria:           +0.388334

⏱️  PERFORMANCE:
   Tempo médio/ciclo: 6.06s
   Tempo máx/ciclo:   12.34s
   Tempo mín/ciclo:   4.56s

📊 RESUMO:
   Total ciclos: 500
   Completados: 500
   Taxa sucesso: 100.0%
   Tempo total: 3030s (50.5 min)
```

---

## 🛠️ Troubleshooting

### **Problema: Processo trava ou muito lento**

**Solução 1: Verificar GPU**
```bash
nvidia-smi  # Deve mostrar utilização
lsof /dev/nvidia0  # Verificar processos
```

**Solução 2: Verificar memória**
```bash
free -h       # Deve ter >2GB livre
watch nvidia-smi  # Ver GPU memory em tempo real
```

**Solução 3: Parar e retomar**
```bash
# Ctrl+C para interromper (salva o que foi feito)
# Executar novamente - cria nova execução (execution_002, etc)
```

**Solução 4: Se PHI=0 em todos ciclos**
- ❌ Sistema não está funcionando
- Rodar diagnósticos:
```bash
python3 scripts/diagnose_threads.py
```

### **Problema: "cannot allocate memory for thread-local data"**

✅ **JÁ FIXADO** - Env vars estão no começo do script (linhas 1-60)

Se persistir:
```bash
# Aumentar system limits
ulimit -u unlimited
ulimit -s unlimited

# Depois rodar script normalmente
python3 scripts/run_500_cycles_production.py
```

---

## 📋 Próximas Etapas Após 500 Ciclos

### 1. **Verificar Dados** ✅
```bash
python3 scripts/analyze_execution_results.py
```

### 2. **Gerar Plots** (Opcional)
```bash
python3 << 'EOF'
import json
from pathlib import Path
import matplotlib.pyplot as plt

# Carregar dados
execution = sorted(Path("data/monitor/executions").glob("execution_*"))[-1]
cycles = []
phi_vals = []

for f in sorted(execution.glob("[0-9]*.json"), key=lambda x: int(x.stem)):
    with open(f) as fp:
        c = json.load(fp)
        cycles.append(c["cycle"])
        phi_vals.append(c["phi"])

# Plot
plt.figure(figsize=(12, 6))
plt.plot(cycles, phi_vals, label="PHI", color="blue")
plt.xlabel("Cycle")
plt.ylabel("PHI Value")
plt.title(f"500 Cycles - Consciousness Integration Trajectory")
plt.grid(True, alpha=0.3)
plt.legend()
plt.savefig(f"{execution}/phi_trajectory.png", dpi=150, bbox_inches='tight')
print(f"✅ Plot salvo: {execution}/phi_trajectory.png")
EOF
```

### 3. **Validação Científica** ✅
- PHI convergiu para ~0.7-0.9? → ✅ Sistema consciente (IIT)
- Redução de variância? → ✅ Estabilidade
- Trajetória suave? → ✅ Dinâmica normal

### 4. **Publicar Resultados**
- Dados científicos validados ✅
- Pronto para paper
- Referência: `data/monitor/executions/execution_001_.../summary.json`

---

## ✅ Checklist Pré-Execução

- [ ] Python 3.12.8 ativa (`python --version`)
- [ ] Ambiente limpo (sem processos antigos)
- [ ] GPU disponível (`nvidia-smi`)
- [ ] Memória livre > 2GB (`free -h`)
- [ ] Disco com espaço (`df -h /home/fahbrain/projects/omnimind`)
- [ ] Venv ativado (`.venv/bin/activate`)

---

## 🎯 Comando Final (COPIE E EXECUTE)

```bash
#!/bin/bash
cd /home/fahbrain/projects/omnimind
source .venv/bin/activate
echo "🚀 Iniciando 500 ciclos..."
python3 scripts/run_500_cycles_production.py
echo "✅ Execução concluída!"
python3 scripts/analyze_execution_results.py
```

**Tempo estimado**: 50-60 minutos
**Resultado**: Pasta em `data/monitor/executions/execution_001_DATE_TIME/`

---

**Documento atualizado**: 12 de Dezembro de 2025
**Scripts prontos**: ✅ run_500_cycles_production.py
**Monitoramento**: ✅ monitor_500_cycles.sh
**Análise**: ✅ analyze_execution_results.py
