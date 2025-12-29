# 🚀 GUIA DE EXECUÇÃO - Validação CUDA Atualizada (12 Dezembro 2025)

## Status Atual

✅ **Script preparado_gpu_validation.sh**: Novo (detecta GPU, limpa processos)
✅ **Script run_500_cycles_scientific_validation.py**: Atualizado com flags quantum
✅ **GTX 1650 detectada**: 4GB VRAM, Driver 580.95.05, CUDA 13.0
✅ **Processos extras removidos**: Uvicorn 8080, 3001 podem ser mortos

## Modo Rápido - Validação em 15 minutos (RECOMENDADO PARA AGORA)

### Passo 1: Executar com wrapper de preparação GPU

```bash
cd /home/fahbrain/projects/omnimind
chmod +x scripts/prepare_gpu_validation.sh
./scripts/prepare_gpu_validation.sh --quick
```

**O que faz**:
- ✅ Detecta GPU (GTX 1650)
- ✅ Mata uvicorn 8080, 3001 (libera 300 MiB GPU)
- ✅ Verifica memória RAM/Swap disponível
- ✅ Seleciona modo quantum automaticamente
- ✅ Executa 3 ciclos (smoke test)
- ⏱️ Tempo: ~5-10 minutos

**Esperado**:
```
GPU: NVIDIA GeForce GTX 1650 (4096MiB)
Driver: 580.95.05
Ciclo 1-3: Φ > 0.1
Sem crashes "CUDA error: out of memory"
```

### Passo 2: Validar Resultados

```bash
# Verificar métricas foram salvos
cat data/monitor/phi_500_cycles_scientific_validation_latest.json | jq '.phi_progression'

# Esperar por: [0.15, 0.71, 0.64] (ou similar)
```

---

## Modo Completo - 50 Ciclos em Modo Clássico (30-45 minutos)

### Se o teste rápido passar, executar:

```bash
cd /home/fahbrain/projects/omnimind
./scripts/prepare_gpu_validation.sh --cycles 50 --disable-quantum
```

**Flags**:
- `--cycles 50`: Executar 50 ciclos (não 500)
- `--disable-quantum`: Usar apenas RNN clássico (sem quantum modules)

**O que faz**:
- ✅ Testa IntegrationLoop estável
- ✅ Valida RNN φ computation
- ✅ Menos consumo GPU (~300MB vs 1000MB)
- ⏱️ Tempo: ~30-45 minutos

**Esperado**:
```
Ciclo 50: Φ ≈ 0.5-0.7 (convergência)
GPU memory: ~1.5 GB em uso
Sem crashes OOM
```

---

## Modo Quantum Leve - 50 Ciclos com Simulador Leve (1-2 horas)

### Se modo clássico passar:

```bash
cd /home/fahbrain/projects/omnimind
./scripts/prepare_gpu_validation.sh --cycles 50 --quantum-lite
```

**Flags**:
- `--cycles 50`: 50 ciclos
- `--quantum-lite`: 16 qubits simulador (vs 32+ full)

**O que faz**:
- ✅ Testa módulos quantum com limite de qubits
- ✅ Valida hybrid classical-quantum integration
- ⏱️ Tempo: ~1-2 horas

**Esperado**:
```
Ciclo 50: Φ ≈ 0.5-0.7
GPU memory: ~2.5 GB em uso
Quantum circuits: 16 qubits
```

---

## Modo Completo - 500 Ciclos Full Quantum (8-12 horas)

### APENAS se os 50 ciclos quantum-lite passarem sem crashes:

```bash
cd /home/fahbrain/projects/omnimind
./scripts/prepare_gpu_validation.sh --cycles 500
```

**Sem flags**: Modo quantum completo

**O que faz**:
- ✅ Validação científica completa (IIT papers)
- ✅ 500 ciclos com métricas completas
- ⏱️ Tempo: ~8-12 horas

**Esperado**:
```
Φ trajectory: 0.1 → 0.5 → 0.7 (convergência)
Ψ (Deleuze): 0.3-0.7
σ (Lacan): 0.01-0.12
Sem crashes
```

---

## Troubleshooting

### ❌ "CUDA error: out of memory" nos 3 primeiros ciclos

```bash
# Solução 1: Matar programas extras
pkill -f "vscode\|code"
pkill -f "chrome\|firefox"

# Solução 2: Usar modo clássico
./scripts/prepare_gpu_validation.sh --quick --disable-quantum

# Solução 3: Aumentar swap
sudo fallocate -l 8G /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### ❌ "Module expectation failed"

```bash
# Problema: quantum_unconscious module tentando usar quantum sem GPU

# Solução: Usar --disable-quantum
./scripts/prepare_gpu_validation.sh --disable-quantum
```

### ⚠️ "Limite de processos já no máximo"

```bash
# Se aparecer durante inicialização
# Significa: ulimit -u já está no máximo (sistema bem configurado)
# Script vai funcionar mesmo assim
```

---

## Testes Granulares para Componentes Individuais

### Teste de Importação Rápido (< 1 segundo)

```bash
cd /home/fahbrain/projects/omnimind
python -c "
from src.consciousness.integration_loop import IntegrationLoop
from src.consciousness.shared_workspace import SharedWorkspace
print('✅ Imports OK')
print(f'GPU available: {__import__(\"torch\").cuda.is_available()}')
"
```

### Teste de GPU Básico (< 5 segundos)

```bash
python -c "
import torch
import nvidia_ml_py3 as nvmlpy

nvmlpy.nvmlInit()
handle = nvmlpy.nvmlDeviceGetHandleByIndex(0)
mem = nvmlpy.nvmlDeviceGetMemoryInfo(handle)
print(f'GPU Memory: {mem.free / 1e9:.1f}GB free')
print(f'CUDA: {torch.cuda.is_available()}')
print(f'Compute Capability: {torch.cuda.get_device_capability(0)}')
"
```

### Teste do ExpectationModule (< 30 segundos)

```bash
python -c "
import os
os.environ['CUDA_LAUNCH_BLOCKING'] = '1'
from src.consciousness.expectation_module import get_expectation_module

em = get_expectation_module(embedding_dim=256)
print(f'✅ ExpectationModule loaded on: {em.device}')
"
```

### Teste de 1 Ciclo (< 2 minutos)

```bash
./scripts/prepare_gpu_validation.sh --quick --cycles 1
```

---

## Comparação de Modos

| Modo | Ciclos | Tempo | GPU | Quantum | Risco OOM |
|------|--------|-------|-----|---------|-----------|
| `--quick` | 3 | 5-10m | 300MB | Full | Baixo ✅ |
| `--disable-quantum` | 50 | 30-45m | 800MB | Não | Baixíssimo ✅ |
| `--quantum-lite` | 50 | 1-2h | 2.5GB | Leve | Médio ⚠️ |
| Padrão (500) | 500 | 8-12h | 3.5GB | Full | Alto ❌ |

---

## Próximos Passos

1. **AGORA**: Executar `./scripts/prepare_gpu_validation.sh --quick`
2. **Se passar**: Executar `--cycles 50 --disable-quantum`
3. **Se pass**: Executar `--cycles 50 --quantum-lite`
4. **Se pass**: Executar `--cycles 500` (full)

---

## Variáveis de Ambiente

Caso precise ajustar manualmente:

```bash
# Mais agressivo na compactação (mais GC)
export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:32"

# Modo sync (padrão, lento mas estável)
export CUDA_LAUNCH_BLOCKING="1"

# Modo async (rápido, instável no GTX 1650)
export CUDA_LAUNCH_BLOCKING="0"

# Limitar threads OpenMP
export OMP_NUM_THREADS="4"
export NUMEXPR_NUM_THREADS="4"
export QISKIT_NUM_THREADS="4"
```

---

**Última Atualização**: 12 Dezembro 2025, 17:30 UTC
**Status**: 🟢 Pronto para Execução
**Recomendação**: Comece com `--quick`, progresso gradualmente
