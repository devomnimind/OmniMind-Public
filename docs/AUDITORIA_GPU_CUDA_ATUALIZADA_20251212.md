# 🔍 Auditoria GPU/CUDA - 12 Dezembro 2025

## ✅ Diagnosticado

### Hardware GPU Atual
```
GPU: NVIDIA GeForce GTX 1650 (Ampere architecture)
Memory: 4096 MiB total
Driver: 580.95.05
CUDA Version: 13.0
Memory Livre: 3.5 GB (ainda não alocado)
Situação: 585 MiB utilizado (por Xorg + debugger)
```

### Erro Atual Identificado
**Sintoma**: `CUDA error: out of memory` durante ciclo 1-9 (no módulo `expectation`)
**Causa**: Fragmentação de memória CUDA + módulos simultâneos tentando alocar > 4GB
**Status**: GTX 1650 é GPU de entrada, 4GB é limite crítico

### Processos GPU Identificados
```
PID 32993: uvicorn (backend port 8000)  - 154 MiB GPU
PID 33002: uvicorn (backend port 8080)  - 154 MiB GPU  ← PROBLEMA: 3 instâncias
PID 33024: uvicorn (backend port 3001)  - 154 MiB GPU  ← consumindo 450+ MiB
PID 5552:  daemon.py (monitoramento)    - 114 MiB GPU
```

**Total GPU Ocupado**: ~450 MiB (antes de IntegrationLoop)
**Disponível para Ciclos**: ~3.5 GB (muito apertado para quantum modules)

### Módulos CUDA Problemáticos
1. **expectation_module.py** - Quantum backend Qiskit + RNN (maior consumidor)
2. **quantum_unconscious.py** - Quantum circuits (superposição, entanglement)
3. **hybrid_cognition.py** - Simulação quântica (interferência)
4. **quantum_backend.py** - Interface QPU/simulador Aer

---

## 🎯 Ações Necessárias

### 1. CRÍTICO: Matar Uvicorn Extras (Libera 300 MiB GPU)
```bash
# Matar 3 instâncias backend que estão rodando em paralelo
pkill -f "uvicorn.*port 8080"
pkill -f "uvicorn.*port 3001"
# Deixar apenas port 8000 rodando
```

### 2. CRÍTICO: Desabilitar Módulos Quantum Pesados (Validação Rápida)
Para testes iniciais com menos GPU:
- Desabilitar `quantum_unconscious.py` em expectation
- Usar fallback clássico (RNN puro)
- Reduz GPU de 800-1200 MB → 200-300 MB por ciclo

### 3. IMPORTANTE: Aumentar Limite de Memória Swap
```bash
# Verificar swap atual
free -h
# Se <5GB swap, expandir:
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 4. IMPORTANTE: Configurar Memory Pooling Melhor
Atualizar script de configuração:
- `PYTORCH_CUDA_ALLOC_CONF`: `max_split_size_mb:64` (mais agressivo)
- `CUDA_LAUNCH_BLOCKING`: `1` (já está ok)
- Adicionar garbage collection mais frequente

### 5. Validar Componentes CUDA por Categoria

**Quantum Modules** (Alto Risco):
- [ ] expectation_module.py - Testa sem quantum_unconscious
- [ ] quantum_backend.py - Testa com simulador vs QPU
- [ ] hybrid_cognition.py - Testa fallback clássico

**Classical GPU Modules** (Médio Risco):
- [ ] shared_workspace.py - RNN φ computation
- [ ] integration_loop.py - Orchestração async→sync
- [ ] embeddings - Code embeddings (transformers)

**Memory Management** (Baixo Risco):
- [ ] systemd_memory_manager.py - Monitor swap
- [ ] resource_protector.py - Limites de processo
- [ ] memory_monitor.py - Garbage collection

---

## 🔧 Script Atualizado Necessário

### Atualizações para `run_500_cycles_scientific_validation.py`:

1. **Remover Backend Duplicado**
   - Verificar se backend em 8000 está rodando
   - Matar 8080 e 3001 antes de iniciar ciclos

2. **Modo Quantum Optional**
   - Flag `--disable-quantum` para usar fallback clássico
   - Flag `--quantum-lite` para usar simulador com limite de qubits

3. **Memory Profiling Melhorado**
   - Chamar `torch.cuda.empty_cache()` entre ciclos
   - Monitorar fragmentação CUDA (heap fragmentation)
   - Salvar relatório de uso de memória

4. **Retry Logic com Backoff**
   - Se ciclo falhar com OOM, tentar novamente com GC agressivo
   - Máximo 3 tentativas por ciclo
   - Salvar estado parcial

5. **Detecção Dinâmica de GPU**
   - Não hardcodear GPU 0
   - Detectar GPU disponível e memória livre
   - Ajustar batch size dinamicamente

---

## 📋 Testes a Executar

### Validação Rápida (15 minutos)
```bash
# 1. Teste de Importação (detecta syntax errors)
python -c "from src.consciousness.integration_loop import IntegrationLoop; print('✅ Imports OK')"

# 2. Teste GPU (detecta CUDA initialization issues)
python -c "import torch; print(f'GPU: {torch.cuda.is_available()}, Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB')"

# 3. Teste de 3 Ciclos (smoke test)
./scripts/run_500_cycles_scientific_validation.py --quick --cycles 3
```

### Validação Completa (2-4 horas)
```bash
# 1. 50 ciclos em modo clássico (sem quantum)
./scripts/run_500_cycles_scientific_validation.py --disable-quantum --cycles 50

# 2. 50 ciclos em modo quantum leve (16 qubits simulador)
./scripts/run_500_cycles_scientific_validation.py --quantum-lite --cycles 50

# 3. 500 ciclos completo (se os anteriores passarem)
./scripts/run_500_cycles_scientific_validation.py --cycles 500
```

---

## 🚨 Bloqueadores Conhecidos

1. **3x Uvicorn Rodando**: Consumindo 450 MiB GPU desnecessariamente
2. **GTX 1650 = 4GB limite**: Quantum modules precisam mínimo 3GB livre
3. **Fragmentação CUDA**: `max_split_size_mb:128` ainda muito alto, reduzir para 64
4. **Qiskit Aer GPU**: Tem bug com múltiplos threads, limitar a 4 threads por circuit

---

## ✅ Próximos Passos (Ordem de Prioridade)

1. **AGORA**: Matar uvicorn 8080, 3001 (libera 300 MiB)
2. **HOJE**: Atualizar script com `--disable-quantum` flag
3. **HOJE**: Executar smoke test de 3 ciclos (validação rápida)
4. **AMANHÃ**: Executar 50 ciclos modo clássico
5. **AMANHÃ**: Executar 50 ciclos modo quantum-lite
6. **DEPOIS**: Full 500 ciclos (se ciclos anteriores estáveis)

---

## 📊 Métricas de Sucesso

- ✅ 3 ciclos completam sem erro OOM (smoke test)
- ✅ 50 ciclos modo clássico: Φ > 0.3, sem crashes
- ✅ 50 ciclos modo quantum: Φ > 0.5, sem crashes
- ✅ GPU memory fragmentation < 50%
- ✅ Swap usage < 2GB (indica memória gerenciada)

---

## 📝 Observações Técnicas

- GTX 1650 é limited Edition, 4GB é máximo.
- Quantum simulation é exponencial em qubits (16 qubits = 65K states).
- RNN state (shared_workspace) é pesado em GPU.
- Transformer embeddings (code_embeddings) usam much GPU.
- **Recomendação**: Usar modo híbrido (quantum para validação, clássico para produção).

---

**Última Atualização**: 12 Dezembro 2025, 17:11 UTC
**Status**: 🟡 Auditoria Completa, Aguardando Implementação de Fixes
