# ✅ Checklist Técnico Pré-Execução - OmniMind

**Última Atualização**: 08 de Dezembro de 2025
**Versão**: Phase 24+ (Lacanian Memory + Quantum Consciousness)

---

## 📋 Pré-requisitos do Sistema

### Hardware Mínimo
- **CPU**: 4 cores (Intel i5/Ryzen 5 ou superior)
- **RAM**: 8GB (16GB recomendado)
- **GPU**: NVIDIA GTX 1650 ou superior (4GB VRAM) - **Opcional mas recomendado**
- **Armazenamento**: 50GB SSD disponível
- **SO**: Linux Ubuntu 20.04+ ou similar (Kali Linux 6.16.8+ validado)

### Software Obrigatório
- **Python**: 3.12.8 (obrigatório, outras versões podem causar problemas)
- **Ollama**: Instalado e rodando com modelo `phi:latest`
- **CUDA**: 12.4+ (se GPU disponível)
- **Qdrant**: Opcional para testes completos (rodando em `http://localhost:6333`)

### Verificação Rápida
```bash
# Verificar Python
python --version  # Deve ser 3.12.8

# Verificar Ollama e modelo phi:latest
ollama list | grep phi
# Deve mostrar: phi:latest

# Verificar CUDA (se GPU disponível)
python -c "import torch; print(torch.cuda.is_available())"
# Deve retornar: True

# Verificar Qdrant (opcional)
curl http://localhost:6333/health
# Deve retornar: {"status":"ok"}
```

---

## 🧪 Scripts de Teste Ativos

### ⚡ Execução Diária - `run_tests_fast.sh` (RECOMENDADO)

**Comando**:
```bash
./scripts/run_tests_fast.sh
```

**Características**:
- ⏱️ **Tempo**: ~10-15 minutos
- 📊 **Escopo**: ~3996 testes (suite rápida)
- 🚀 **GPU**: ✅ FORÇADA (CUDA_VISIBLE_DEVICES=0)
- 🔍 **Exclui**: Testes marcados com `@pytest.mark.slow` e `@pytest.mark.chaos`
- ✅ **Inclui**: Testes marcados com `@pytest.mark.real` (sem chaos)
- 📝 **Logs**: `data/test_reports/output_fast_*.log`
- 🎯 **Uso**: Validação diária rápida, desenvolvimento iterativo

**Marcadores de Teste**:
- `@pytest.mark.slow`: Testes longos (>30s timeout) - **EXCLUÍDOS**
- `@pytest.mark.real`: Testes com GPU+LLM+Network (não destrutivos) - **INCLUÍDOS**
- `@pytest.mark.chaos`: Testes de destruição de servidor - **EXCLUÍDOS**
- Sem marcadores: Testes unitários/integração mockados - **INCLUÍDOS**

---

### 🛡️ Validação Semanal - `run_tests_with_defense.sh`

**Comando**:
```bash
./scripts/run_tests_with_defense.sh
```

**Características**:
- ⏱️ **Tempo**: 1-2 horas (varia com crashes detectados)
- 📊 **Escopo**: ~4004 testes (suite completa + chaos engineering)
- 🚀 **GPU**: ✅ FORÇADA
- 🛡️ **Autodefesa**: ✅ Detecta testes perigosos (3+ crashes em 5min = label "dangerous")
- ⚠️ **ATENÇÃO**: Inclui testes de chaos engineering que **destroem servidor intencionalmente**
- 📈 **Gera**: Relatório de perigo e métricas em `data/test_reports/`
- 📝 **Logs**: `data/test_reports/output_*.log`
- 🎯 **Uso**: Validação semanal completa, certificação de resiliência

**Testes de Chaos Engineering**:
- Destroem servidor intencionalmente para validar resiliência de Φ
- Testam recuperação automática do sistema
- Validam integridade de métricas após crashes

---

### 🧪 Integração Completa - `quick_test.sh` (AVANÇADO)

**Pré-requisito (UMA VEZ)**:
```bash
bash scripts/configure_sudo_omnimind.sh  # Setup NOPASSWD sudo
```

**Comando**:
```bash
bash scripts/quick_test.sh
```

**Características**:
- ⏱️ **Tempo**: ~30-45 minutos
- 📊 **Escopo**: Suite completa + servidor backend
- 🚀 **GPU**: ✅ FORÇADA
- 🖥️ **Servidor**: ✅ Inicia em `localhost:8000`
- 💾 **Requer**: sudo configurado (para inicialização do servidor)
- 🔗 **Testa**: Contra servidor real (não isolado)
- 📝 **Logs**: `data/test_reports/output_*.log`
- 🎯 **Uso**: Validação de integração completa, testes end-to-end

---

## ⚠️ IBM Quantum Real Hardware (Fase Madura - Futuro)

**Status**: ✅ Implementado, ❌ **NÃO em ciclo ativo**

**Detalhes**:
- **Papers 2&3**: Validados em hardware real IBM Quantum (ibm_fez 27Q, ibm_torino 84Q)
- **Tempos de execução reais**: 30-120 segundos por job
- **Restrição**: Créditos gratuitos limitados
- **Plano**: Ativar em Phase 25+ para certificação regular

**Configuração Atual**:
```python
# tests/conftest.py
os.environ["OMNIMIND_DISABLE_IBM"] = "True"  # IBM auth falhando em sandbox
```

**Para Habilitar**:
```bash
# Definir token IBM no ambiente
export IBM_QUANTUM_TOKEN="your_token_here"
export OMNIMIND_DISABLE_IBM="False"

# Então executar testes
./scripts/run_tests_with_defense.sh
```

---

## 🔧 Correções Críticas Implementadas

### ✅ CRÍTICO 1: Timeout em Consensus Voting

**Arquivo**: `src/swarm/collective_learning.py`
**Status**: ✅ IMPLEMENTADO

**Mudanças**:
- [x] Adicionado `MAX_CONSENSUS_TIMEOUT = 30.0` segundos
- [x] Implementado `threading.Lock()` para thread-safety
- [x] Modificado `get_consensus_model()` com timeout protection
- [x] Fallback: retorna consensus parcial se timeout excedido
- [x] Logging detalhado de timeout e recuperação

**Validação**:
```python
from src.swarm.collective_learning import ConsensusLearning
cl = ConsensusLearning(5, consensus_timeout=30.0)
```

---

### ✅ CRÍTICO 2: Memory Cap com LRU Eviction

**Arquivo**: `src/memory/episodic_memory.py` (deprecated, usar `NarrativeHistory`)
**Status**: ✅ IMPLEMENTADO

**Mudanças**:
- [x] Limite de memória configurável
- [x] Eviction LRU automático quando limite excedido
- [x] Preservação de episódios mais importantes

**Nota**: `EpisodicMemory` está deprecated em favor de `NarrativeHistory` (Lacanian).

---

### ✅ CRÍTICO 3: Modelo LLM Padrão

**Arquivo**: Múltiplos (`src/neurosymbolic/neural_component.py`, etc.)
**Status**: ✅ CORRIGIDO (2025-12-05)

**Mudanças**:
- [x] Modelo padrão alterado de `qwen2:7b-instruct` para `phi:latest`
- [x] Configuração centralizada em `config/agent_config.yaml`
- [x] Fallback para `qwen2:7b-instruct` se `phi:latest` não disponível

**Arquivos Corrigidos**:
- `src/neurosymbolic/neural_component.py`: `ollama/phi:latest`
- `src/neurosymbolic/hybrid_reasoner.py`: `ollama/phi:latest`
- `src/integrations/orchestrator_llm.py`: `phi:latest`
- `src/orchestrator/task_executor.py`: `phi:latest`

---

## 📊 Configuração de Testes

### Timeout Global
- **Por teste**: 800 segundos (independente, não cumulativo)
- **Método**: Thread-based (interrupção segura)
- **Configuração**: `config/pytest.ini`

### Variáveis de Ambiente para Testes
```bash
CUDA_VISIBLE_DEVICES=0          # Força GPU device 0
OMNIMIND_GPU=true               # Habilita GPU
OMNIMIND_FORCE_GPU=true         # Força detecção GPU com fallback
OMNIMIND_DEV=true               # Modo desenvolvimento
OMNIMIND_DEBUG=true             # Logging debug
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512  # Otimização memória GPU
```

### Gerenciamento de Servidor
- **Centralizado**: Via `ServerStateManager` (previne race conditions)
- **Auto-limpeza**: Servidores são limpos automaticamente após testes
- **Isolamento**: Cada teste tem seu próprio contexto de servidor

---

## ✅ Checklist Pré-Execução

Antes de executar testes ou iniciar o sistema, verifique:

### Ambiente
- [ ] Python 3.12.8 instalado e ativo
- [ ] Ambiente virtual ativado (`.venv`)
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Ollama rodando (`ollama serve`)
- [ ] Modelo `phi:latest` disponível (`ollama list | grep phi`)

### GPU (Opcional)
- [ ] CUDA instalado e funcionando
- [ ] Driver NVIDIA atualizado
- [ ] PyTorch detecta GPU (`python -c "import torch; print(torch.cuda.is_available())"`)

### Serviços (Opcional para testes completos)
- [ ] Qdrant rodando (`curl http://localhost:6333/health`)
- [ ] Redis rodando (se necessário)
- [ ] Backend não está rodando (para testes isolados)

### Configuração
- [ ] Arquivo `.env` configurado (se necessário)
- [ ] `config/agent_config.yaml` com modelo `phi:latest`
- [ ] Diretórios de log existem (`logs/`, `data/test_reports/`)

---

## 🚨 Troubleshooting Comum

### Ollama não responde
```bash
# Verificar se Ollama está rodando
curl http://localhost:11434/api/tags

# Se não estiver, iniciar Ollama
ollama serve
```

### Modelo phi:latest não encontrado
```bash
# Baixar modelo phi:latest
ollama pull phi:latest

# Verificar modelos disponíveis
ollama list
```

### Erros de GPU/CUDA
```bash
# Verificar CUDA
python -c "import torch; print(torch.cuda.is_available())"

# Verificar variáveis de ambiente
echo $CUDA_VISIBLE_DEVICES
echo $CUDA_HOME
```

### Testes falhando com timeout
- Verificar se servidor não está rodando (conflito de porta)
- Verificar se GPU está disponível (alguns testes requerem GPU)
- Verificar logs em `data/test_reports/` para detalhes

---

## 📚 Referências

- **Quick Start**: `docs/canonical/QUICK_START.md`
- **System Initialization**: `docs/canonical/omnimind_system_initialization.md`
- **Safe Commands**: `docs/canonical/SAFE_COMMANDS.md`
- **Architecture**: `docs/canonical/omnimind_architecture_reference.md`

---

**Autor**: Fabrício da Silva + assistência de IA (Copilot GitHub/Cursor/Gemini/Perplexity)
