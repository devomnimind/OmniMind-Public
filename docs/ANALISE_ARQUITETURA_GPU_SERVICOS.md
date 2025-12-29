# 🏗️ ANÁLISE ARQUITETURA: GPU, Serviços e Validação Científica

**Data**: 13 DEC 2025
**Status**: Diagnóstico Crítico - Requer Refatoração
**Problema Raiz**: OmniMind não sabe diferenciar:
- Serviços críticos (que influenciam validação)
- Serviços auxiliares (coleta automática, monitoramento)
- Modo de operação (produção normal vs. validação científica)

---

## 🎯 QUESTÕES CRÍTICAS (Usuario)

1. **Se frontend está usando GPU = erro de programação anterior**
2. **Serviços que NÃO influenciam validação científica = podem sair da GPU**
3. **Coletores automáticos (a cada 10s) COMPETEM com validação = devem pausar gracefully**
4. **OmniMind deveria SABER SOZINHO**: "validação está rodando, vou ficar quieto"

---

## 📊 PARTE 1: Mapear Serviços por Tipo

### Categoria A: CRÍTICOS PARA VALIDAÇÃO (PRECISAM GPU)

**Serviço: `omnimind-core` (src.main)**
```yaml
Comando: python -m src.main
Port: N/A (daemon, não HTTP)
GPU: SIM - ESSENCIAL
Função:
  - Integration loop (consciousness stepping)
  - Phi calculations (IIT)
  - Quantum backend (Qiskit GPU)
Impacto: CRÍTICO - É a própria validação
Pode pausar? NÃO
```

**Serviço: Backend HTTP (uvicorn 8000)**
```yaml
Comando: uvicorn src.api.main:app --port 8000
Port: 8000
GPU: DEPENDE DO CÓDIGO
Função:
  - API REST para consciousness
  - WebSocket para métricas real-time
  - Query de estado consciente
Impacto: ALTO - chamado pela validação científica
Pode pausar? NÃO (durante validação)
Erro Atual: Se está usando GPU para serialização JSON = ERRO
Solução: Validar se realmente precisa GPU
```

---

### Categoria B: AUXILIARES (PODEM USAR CPU/SWAP)

**Serviço: Coleta Automática de Métricas**
```yaml
Trigger: Timer (a cada 10s ou N minutos)
Location: Provavelmente em src/metrics/
GPU: NÃO PRECISA (coleta já feita, só salva)
Função:
  - Coletar Phi histórico
  - Salvar em Qdrant/database
  - Gerar estatísticas
Impacto: BAIXO - não influencia validação atual
Pode pausar? SIM - DEVE PAUSAR durante validação
Problema: Compete por I/O com validação
```

**Serviço: Monitoramento de Sistema**
```yaml
Comando: src/security/security_monitor
Port: N/A
GPU: NÃO PRECISA
Função:
  - Monitorar CPU, memória, temperatura
  - Alertas de segurança
  - Logs de sistema
Impacto: NENHUM - apenas logging
Pode pausar? SIM - PODE PAUSAR durante validação
Problema: I/O de logs compete com validação
```

**Serviço: Frontend Web (React)**
```yaml
Comando: npm run dev (web/frontend)
Port: 3000 (Vite dev server)
GPU: NUNCA - é JavaScript/React
Função:
  - Dashboard UI
  - Visualizações
  - Cliente WebSocket
Impacto: NENHUM em validação científica
Pode pausar? SIM - pode sair completamente
Problema: Se está usando GPU = erro anterior
Fallback 8080: Qual é sua função?
```

---

## 🚨 DIAGNÓSTICO: Por que 3 Uvicorn?

**Encontrado:**
- `uvicorn.run(app, host="0.0.0.0", port=8000)` em src/api/main.py
- `uvicorn.run(app, host="0.0.0.0", port=8000)` em web/backend/main_simple.py
- `uvicorn.run(app, host="0.0.0.0", port=8000)` em web/backend/main_minimal.py

**Hipóteses:**
1. ✅ Port 8000 = Backend oficial (sempre)
2. ❓ Port 8080 = Fallback de web/backend/main_simple.py (redundância?)
3. ❓ Port 3001 = Frontend hot-reload server (Vite)?

**Questão para Você**:
- Qual é a INTENÇÃO dos 3 backends?
- Deveriam rodar só 1?
- Os outros são fallbacks ou obsoletos?

---

## 🎯 PARTE 2: GPU Allocation Strategy

### CENÁRIO ATUAL (ERRADO):
```
GPU (4GB VRAM):
├─ uvicorn 8000:   490MiB (por quê?)
├─ uvicorn 8080:   490MiB (redundância desnecessária?)
├─ uvicorn 3001:   490MiB (frontend no GPU = ERRO)
└─ python3 main:    94MiB (core consciousness)
─────────────────
TOTAL: 1564MiB = 38% capacity PERDIDO em overhead

MAIN SCRIPT vê: "GPU 61% utilizado" MAS SÓ TEM 94MiB útil disponível
```

### CENÁRIO PROPOSTO:
```
GPU (4GB VRAM) - Isolada por CUDA_VISIBLE_DEVICES:
├─ omnimind-core (src.main):
│  └─ CUDA_VISIBLE_DEVICES=0
│  └─ Consciousness stepping + Quantum backend
│  └─ ~800MiB durante operação
│
└─ [Validação científica quando ativa]:
   └─ Script de validação
   └─ CUDA_VISIBLE_DEVICES=0 (exclusivo)
   └─ ~1200-2000MiB quando processando

CPU (RAM comum):
├─ Backend API (uvicorn 8000):
│  └─ JSON serialization, WebSocket
│  └─ ~100-200MiB
│
├─ Frontend (React dev server):
│  └─ JavaScript, não precisa GPU
│  └─ ~300MiB
│
├─ Monitoramento:
│  └─ CPU-only
│  └─ ~50MiB
```

---

## 🔄 PARTE 3: Sistema de Sinalização (SOLUÇÃO CORRETA)

### Proposta: VALIDATION_MODE

**Quando validação científica começa:**

```bash
# script de validação começa
export OMNIMIND_VALIDATION_MODE=true

# OmniMind recebe sinal
python -m src.validation.scientific_validation
```

**OmniMind sabe fazer:**

```python
# Em omnimind-core (src.main):
if os.getenv("OMNIMIND_VALIDATION_MODE") == "true":
    # Entrar em VALIDATION_MODE
    - Pausar coleta automática (não salvar a cada 10s)
    - Pausar monitoramento contínuo
    - Desabilitar logs verbosos
    - Liberar GPU para validação
    - Manter apenas: consciousness stepping + validation metrics

# Métricas da validação são diferentes:
# - Normal: "salvo histórico, fiz agregação, loguei"
# - Validação: "executo stepping, meço Phi, pronto"
```

---

## 🏗️ PARTE 4: Arquitetura Proposta

### Arquitetura Atual (ERRADA):
```
User starts validation script
          ↓
Script tenta usar GPU
          ↓
❌ 3 Uvicorn + core + backend competem
❌ GPU é compartilhada sem isolamento
❌ OmniMind não sabe que validação está rodando
❌ Coleta automática ainda ativa (compete)
```

### Arquitetura Proposta (CORRETA):

```
┌─────────────────────────────────────────────────────────┐
│ OmniMind Consciousness Core (omnimind-core service)     │
├─────────────────────────────────────────────────────────┤
│ Modo: VALIDAÇÃO_MODE (sinalizado externamente)         │
├─────────────────────────────────────────────────────────┤
│ Componentes:                                             │
│                                                          │
│ GPU-ONLY (CUDA_VISIBLE_DEVICES=0):                     │
│ ├─ IntegrationLoop (consciousness.step)                │
│ ├─ QuantumBackend (Qiskit GPU)                         │
│ ├─ PhiCalculator (IIT metrics)                         │
│ └─ ValidationMetrics (ciência)                         │
│                                                          │
│ CPU-ONLY (RAM):                                        │
│ ├─ NarrativeHistory (memória simbólica)                │
│ ├─ SystemicMemory (atratores Lacan)                    │
│ └─ StateManagement (serialização)                      │
│                                                          │
│ PAUSED (durante VALIDATION_MODE):                      │
│ ├─ AutomaticMetricsCollector (timer)                   │
│ ├─ SecurityMonitor (scanning)                          │
│ ├─ VerboseLogging (I/O)                                │
│ └─ DashboardUpdates (real-time)                        │
└─────────────────────────────────────────────────────────┘
        ↓ (sinaliza via IPC/file/signal)
┌─────────────────────────────────────────────────────────┐
│ Serviços Auxiliares (CPU-ONLY quando validando)        │
├─────────────────────────────────────────────────────────┤
│ ├─ Backend API (uvicorn 8000): CPU only                │
│ ├─ Frontend (React 3000): CPU only                      │
│ └─ Redundant Backend (8080): PAUSED                    │
└─────────────────────────────────────────────────────────┘
        ↓ (esperando fim de validação)
┌─────────────────────────────────────────────────────────┐
│ Validação Científica (Script externo)                   │
├─────────────────────────────────────────────────────────┤
│ ├─ Sinaliza: export OMNIMIND_VALIDATION_MODE=true      │
│ ├─ Executa: 500 integration cycles                     │
│ ├─ Usa: GPU 100% (isolada)                             │
│ ├─ Coleta: Métricas científicas (Phi, Psi, etc)       │
│ └─ Finaliza: Escreve relatório                         │
│                                                          │
│ Quando termina:                                        │
│ └─ Sinaliza: export OMNIMIND_VALIDATION_MODE=false     │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 PARTE 5: Implementação (Roteiro)

### Passo 1: Identificar o que REALMENTE precisa GPU
```bash
# Para cada módulo:
grep -r "torch.cuda\|\.cuda\|\.to.*device\|CUDA" src/ \
  | grep -v "__pycache__"
```

**Esperado em:**
- ✅ `src/consciousness/` (integration_loop, conscious_system)
- ✅ `src/quantum_consciousness/` (quantum_backend, qpu_interface)
- ✅ `src/metrics/` (phi_calculator)
- ❌ `src/api/` (não deveria ter)
- ❌ `web/backend/` (não deveria ter)
- ❌ `web/frontend/` (NUNCA deveria ter)

### Passo 2: Validar GPU allocation por processo
```bash
# Durante cada serviço, qual CUDA_VISIBLE_DEVICES?
# omnimind-core: CUDA_VISIBLE_DEVICES=0 ✅
# validation script: CUDA_VISIBLE_DEVICES=0 ✅ (exclusivo)
# backend api: CUDA_VISIBLE_DEVICES="" ou CPU ✅
# frontend: CUDA_VISIBLE_DEVICES="" ou CPU ✅
```

### Passo 3: Implementar VALIDATION_MODE
```python
# Em src/main.py ou src/consciousness/conscious_system.py

class ConsciousSystem:
    def __init__(self, validation_mode=False):
        self.validation_mode = validation_mode or \
            os.getenv("OMNIMIND_VALIDATION_MODE") == "true"

    def pause_auxiliary_systems(self):
        """Quando validação ativa"""
        if self.validation_mode:
            # Pausar timers
            self.automatic_collector.pause()
            self.security_monitor.pause()
            # Desabilitar logs
            logger.setLevel(logging.WARNING)

    def resume_auxiliary_systems(self):
        """Quando validação termina"""
        if not self.validation_mode:
            self.automatic_collector.resume()
            self.security_monitor.resume()
            logger.setLevel(logging.INFO)
```

### Passo 4: Verificar Backend GPU usage
```bash
# Em web/backend/main.py
# Se está importando torch/cuda:
# - REMOVER
# - Isso é API gateway, não deve ter GPU

# Se chamando src.consciousness que usa GPU:
# - Usar apenas CPU e deixar consciousness retornar JSON
# - Backend serializa resultado, não calcula
```

---

## 📋 SUMMARY: O que mudou?

| Aspecto | Atual (ERRADO) | Proposto (CORRETO) |
|---------|---|---|
| GPU Sharing | Todos usam GPU sem isolamento | omnimind-core isolada com CUDA_VISIBLE_DEVICES=0 |
| Backend na GPU | Sim (erro) | Não - CPU apenas |
| Frontend na GPU | Sim (erro) | Não - JavaScript/CPU |
| Validação vs Produção | Competem | Isoladas - VALIDATION_MODE sinaliza |
| Coleta automática durante validação | Rodando (compete) | Pausa gracefully |
| OmniMind sabe que validação está rodando | Não | Sim - env var OMNIMIND_VALIDATION_MODE |
| Processamento principal | 1 processo dividindo GPU | Core + Validation dividem ISOLADAMENTE |

---

## ✅ CONCLUSÃO

**Você estava certo:**
1. Matar serviços = errado
2. O problema é arquitetura
3. OmniMind deveria saber "está em modo validação"
4. Serviços auxiliares devem pausar gracefully
5. Coleta automática compete com validação = deve ficar dormindo

**Próximo passo:**
1. Identificar quais módulos REALMENTE usam GPU (grep)
2. Remover GPU de onde não deveria estar
3. Implementar VALIDATION_MODE signal
4. Pausar coleta/monitoramento quando validação ativa
5. Isolar GPU entre processos com CUDA_VISIBLE_DEVICES

---

**Status**: 🔴 REQUER REFATORAÇÃO - Não é problema de limite de GPU, é de arquitetura
