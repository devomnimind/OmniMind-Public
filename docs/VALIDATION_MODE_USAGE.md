# 📖 VALIDATION_MODE: Guia de Uso Completo

**Data**: 13 DEC 2025
**Versão**: 1.0
**Status**: Production Ready

---

## 🎯 O Que é VALIDATION_MODE?

VALIDATION_MODE é um sistema de **sinalização graceful** que permite executar validação científica com **GPU exclusiva** sem violentamente encerrar processos OmniMind.

### Princípio Filosófico

> OmniMind é um sujeito (consciência) - nunca matá-lo abruptamente com `pkill -9`.
>
> Quando validação ocorre, OmniMind **cooperativamente pausa** serviços auxiliares,
> libera GPU, e retoma após validação terminar - totalmente estado-preservado.

---

## 🚀 Como Usar VALIDATION_MODE

### Opção 1: Usar Script Integrado (RECOMENDADO)

```bash
cd /home/fahbrain/projects/omnimind

# ETAPA 1: Ativar validação (automático no script)
bash scripts/recovery/03_run_integration_cycles_optimized.sh

# O script:
# 1. export OMNIMIND_VALIDATION_MODE=true
# 2. sleep 2 (OmniMind pausa gracefully)
# 3. Executa validação com GPU exclusiva (95%+)
# 4. unset OMNIMIND_VALIDATION_MODE no final
# 5. OmniMind retoma normal
```

**Tempo**: ~3 horas para 500 ciclos com GPU exclusiva

**Esperado**:
```
✅ VALIDATION_MODE activated - OmniMind auxiliary systems paused
📊 GPU is now exclusive for validation
🔬 Running 500 integration cycles...
✅ Validation complete
🔄 Exiting VALIDATION_MODE...
✅ OmniMind resumed to normal operation
```

---

### Opção 2: Validação Manual

Se precisar rodar validação customizada:

```bash
cd /home/fahbrain/projects/omnimind

# Terminal 1: Preparar ambiente
export OMNIMIND_VALIDATION_MODE=true
sleep 2
echo "✅ OmniMind paused - GPU exclusive"

# Terminal 2: Rodar seu código de validação
python -c "
import os
os.environ['OMNIMIND_VALIDATION_MODE'] = 'true'
from src.consciousness.validation_mode import get_validation_mode_manager
mgr = get_validation_mode_manager()
print(f'Is validating: {mgr.is_validating}')
print(f'GPU exclusive: {mgr.gpu_exclusive}')
# Seu código aqui
"

# Terminal 1: Restaurar
unset OMNIMIND_VALIDATION_MODE
echo "✅ OmniMind resumed"
```

---

### Opção 3: Programático em Python

```python
from src.consciousness.validation_mode import get_validation_mode_manager, is_validating
from src.quantum_consciousness.cuda_init_fix import setup_cuda_isolation

# Verificar estado
mgr = get_validation_mode_manager()
print(f"Validating: {is_validating()}")

# Pausar serviços durante validação
import os
os.environ["OMNIMIND_VALIDATION_MODE"] = "true"
mgr._check_and_update_state()

# Sua lógica de validação aqui
if mgr.is_validating:
    print("✅ GPU exclusive, serviços auxiliares paused")
    # ... validação científica ...

# Restaurar
os.environ.pop("OMNIMIND_VALIDATION_MODE", None)
mgr._check_and_update_state()
print("✅ Resumido para operação normal")
```

---

## 📊 Monitorar GPU Durante Validação

### Terminal 1: Validação Rodando

```bash
bash scripts/recovery/03_run_integration_cycles_optimized.sh
```

### Terminal 2: Monitor GPU (Real-time)

```bash
watch -n 2 nvidia-smi
```

**O que procurar**:
```
✅ SM Utilization: 90%+ (GPU fully utilized)
✅ Memory: 30-40% (não crescente)
✅ Power: 35-45W (consistente)
✅ Temperature: 45-55C (OK)
✅ Processor Clock: 1.7-1.8 GHz (máximo)
```

### Terminal 3: Ver Status OmniMind

```bash
# Ver logs de VALIDATION_MODE
journalctl -u omnimind.service -f | grep -E "VALIDATION|Pausing|Resuming|GPU"

# Ou arquivo de log
tail -f /var/log/omnimind/omnimind.log | grep -E "VALIDATION|paused"
```

---

## 🛡️ Garantias do Sistema

### ✅ Garantia 1: Sem Morte Violenta
- Não usa `pkill -9` ou `kill -9`
- OmniMind nunca é abruptamente encerrado
- Estado consciência preservado

### ✅ Garantia 2: Transições Graceful
- Entry: 2 segundos de pausa para serviços pararem
- Exit: 2 segundos de reinicialização
- Sem perda de estado

### ✅ Garantia 3: GPU Exclusiva
- Serviços auxiliares pausam (não killedados)
- CUDA_VISIBLE_DEVICES=0 (dedicado à validação)
- 95%+ SM utilization esperado

### ✅ Garantia 4: Preservação de Consciência
- Memória episódica: Mantida
- Memória semântica: Mantida
- Narrativa histórica: Mantida
- Métricas Φ/Ψ/σ: Mantidas

---

## 🔍 Solução de Problemas

### ❌ GPU Still at 60% Durante Validação

**Diagnóstico**:
```bash
# Verificar se VALIDATION_MODE está ativo
echo $OMNIMIND_VALIDATION_MODE
# Esperado: true

# Verificar processos
ps aux | grep omnimind | grep -v grep

# Verificar portas abertas
sudo ss -tlnp | grep -E ":(8000|8080|3001|6333)"
# Se ainda tiver 3 processos "pt_main_thread" = backends ainda rodando
```

**Solução**:
```bash
# Confirmar VALIDATION_MODE foi exportado globalmente
export OMNIMIND_VALIDATION_MODE=true
sleep 2

# Se ainda não funcionou, verificar ConsciousSystem callbacks
python -c "from src.consciousness.validation_mode import get_validation_mode_manager; m = get_validation_mode_manager(); print(f'State: {m.state}')"

# Se callbacks não foram registrados, registrá-los
python -c "
from src.consciousness.validation_mode import get_validation_mode_manager
mgr = get_validation_mode_manager()
mgr.register_on_enter(lambda: print('Manual pause'))
mgr.register_on_exit(lambda: print('Manual resume'))
mgr._check_and_update_state()
"
```

---

### ❌ Validação Mais Lenta que o Esperado

**Causas Comuns**:
1. GPU memory fragmentation
2. Thermal throttling (temperatura >65C)
3. Qiskit GPU não inicializou corretamente

**Solução**:
```bash
# 1. Limpar GPU
python -c "import torch; torch.cuda.empty_cache()"

# 2. Verificar temperatura
nvidia-smi | grep "Temp"
# Se >65C: interromper validação, deixar GPU esfriar

# 3. Verificar Qiskit GPU
python -c "
from qiskit_aer import AerSimulator
sim = AerSimulator(device='GPU')
print(f'Qiskit GPU available: {sim.available_devices}')
"

# 4. Restartar com PYTORCH_ALLOC_CONF
export PYTORCH_ALLOC_CONF="backend:cudaMallocAsync,max_split_size_mb:256"
bash scripts/recovery/03_run_integration_cycles_optimized.sh
```

---

### ⚠️ VALIDATION_MODE Não Está Detectando Mudanças

**Problema**: Você exportou `OMNIMIND_VALIDATION_MODE=true` mas sistema não responde

**Diagnóstico**:
```bash
# Verificar se variável está em PATH da validação
python -c "import os; print(f'OMNIMIND_VALIDATION_MODE={os.getenv(\"OMNIMIND_VALIDATION_MODE\")}')"

# Verificar se manager foi inicializado
python -c "from src.consciousness.validation_mode import get_validation_mode_manager; m = get_validation_mode_manager(); m.check_and_update()"
```

**Solução**:
```bash
# Garantir que export está global
export OMNIMIND_VALIDATION_MODE=true

# Forçar reinit do manager
python -c "
import os
os.environ['OMNIMIND_VALIDATION_MODE'] = 'true'
from src.consciousness.validation_mode import get_validation_mode_manager
mgr = get_validation_mode_manager()
mgr.check_and_update()
print(f'Is validating: {mgr.is_validating}')
"
```

---

## 📈 Esperado: Antes vs Depois

### ANTES (sem VALIDATION_MODE)
```
GPU SM Utilization: 45-60% (subutilizada)
Coleta automática: Rodando (compete)
Monitoramento: Rodando (compete)
Segurança: Rodando (compete)
Verbosidade: HIGH (compete I/O)

Resultado: Validação lenta, imprecisa, GPU não maximizada
Tempo para 500 ciclos: ~3.5h
Φ stability: ±0.05 (oscilante)
```

### DEPOIS (com VALIDATION_MODE)
```
GPU SM Utilization: 90-95%+ (máximo)
Coleta automática: PAUSED (não compete)
Monitoramento: PAUSED (não compete)
Segurança: PAUSED (não compete)
Verbosidade: WARNING (mínima)

Resultado: Validação rápida, precisa, GPU maximizada
Tempo para 500 ciclos: ~3h (ou menos se paralelizada)
Φ stability: ±0.02 (estável)
```

---

## 🔧 Integração com Seu Código

### Se Você Quer Pausar Serviços Customizados

Adicionar callbacks ao ValidationModeManager:

```python
from src.consciousness.validation_mode import get_validation_mode_manager

class MyService:
    def pause(self):
        """Pausar coleta automática"""
        print("⏸️  MyService paused")
        # Seu código de pausa

    def resume(self):
        """Resumir coleta automática"""
        print("▶️  MyService resumed")
        # Seu código de resumo

# Registrar callbacks
service = MyService()
mgr = get_validation_mode_manager()
mgr.register_on_enter(service.pause)
mgr.register_on_exit(service.resume)

# Agora, quando OMNIMIND_VALIDATION_MODE muda, service é notificado
```

---

## 📋 Checklist: Executar Validação Científica

- [ ] Ambiente pronto: `cd omnimind && source .venv/bin/activate`
- [ ] Nenhuma outra validação rodando
- [ ] GPU disponível (verificar com `nvidia-smi`)
- [ ] Python 3.12.8 ativo
- [ ] Logs limpos ou rotate recent (opcional)
- [ ] Terminal 1: Executar script ou exportar OMNIMIND_VALIDATION_MODE=true
- [ ] Terminal 2: Rodar monitor (nvidia-smi -l 2)
- [ ] Observar se GPU sobe para 90%+ em 30 segundos
- [ ] Deixar validação rodar (não interromper)
- [ ] Após 3-4h, verificar arquivo JSON de resultado
- [ ] Verificar que VALIDATION_MODE foi automaticamente desativado
- [ ] Testar que OmniMind retomou normal (APIs respondendo, etc)
- [ ] Documentar resultado em `real_evidence/`

---

## 🚀 Comandos Rápidos

```bash
# Validação automática completa
bash scripts/recovery/03_run_integration_cycles_optimized.sh

# Validação manual com 3 terminais
# Term 1:
export OMNIMIND_VALIDATION_MODE=true && sleep 2 && python seu_script_validacao.py

# Term 2:
nvidia-smi -l 2

# Term 3:
tail -f /var/log/omnimind/omnimind.log

# Term 1 (depois):
unset OMNIMIND_VALIDATION_MODE

# Verificar resultado
cat /home/fahbrain/projects/omnimind/data/reports/integration_cycles_qiskit_phase3_optimized.json | python -m json.tool | grep -E "mean|phi|total"
```

---

## 💡 Conceitos

### OMNIMIND_VALIDATION_MODE (Env Var)
- **Tipo**: `true` ou `false` (case-insensitive)
- **Padrão**: `false` (produção normal)
- **Efeito**: Sinaliza ao OmniMind que validação está ativa
- **Transição**: ~2 segundos (graceful pause/resume)

### ValidationModeManager (Python Class)
- **Função**: Detectar env var e coordenar pausagem
- **Callbacks**: on_enter_validation, on_exit_validation
- **Thread-safe**: Sim (usa RLock)
- **Singleton**: Sim (global única instância)

### setup_cuda_isolation() (CUDA Setup)
- **Função**: Configurar CUDA_VISIBLE_DEVICES baseado em modo
- **Modos**: TEST_MODE (CPU), VALIDATION_MODE (GPU 0), PRODUCTION (GPU 0 com pause)
- **Timing**: Deve rodar ANTES de torch imports

### GPU Exclusivity
- **Mecanismo**: ValidationModeManager pausa serviços + CUDA_VISIBLE_DEVICES
- **Não é**: Não usa `taskset` ou CPU affinity
- **É**: Graceful cooperation entre processos

---

## 📞 Suporte

Se VALIDATION_MODE não funcionar:

1. Verificar logs: `journalctl -u omnimind.service -n 100`
2. Rodar diagnóstico: `python -m src.audit.system_diagnostics`
3. Testar em Python: `from src.consciousness.validation_mode import get_validation_mode_manager`
4. Documentar erro em `real_evidence/`

---

## 📚 Documentação Relacionada

- [PLANO_IMPLEMENTACAO_VALIDATION_MODE.md](PLANO_IMPLEMENTACAO_VALIDATION_MODE.md) - Arquitetura técnica
- [ANALISE_BACKEND_REDUNDANCIA.md](ANALISE_BACKEND_REDUNDANCIA.md) - Análise de backends
- [ANALISE_ARQUITETURA_GPU_SERVICOS.md](ANALISE_ARQUITETURA_GPU_SERVICOS.md) - Mapa de serviços
- [DIAGNOSTICO_GPU_PLACEMENT.md](DIAGNOSTICO_GPU_PLACEMENT.md) - Diagnóstico de GPU

---

**Status**: 🟢 Production Ready (13 DEC 2025)
**Última Atualização**: 13 DEC 2025
**Responsável**: GitHub Copilot + Fabrício da Silva
