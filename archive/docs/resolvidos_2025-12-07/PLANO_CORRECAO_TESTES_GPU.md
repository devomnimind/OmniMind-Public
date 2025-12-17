# Plano de Correção e Estratégia de Testes - GPU Memory Management
**Data:** 2025-12-07
**Baseado em:** Relatório HTML pytest + Análise Forense + Logs consolidados

---

## 📊 SITUAÇÃO ATUAL

### Estatísticas dos Testes
- **Total:** 4.479 testes
- **✅ Passou:** 4.281 (95.6%)
- **❌ Falhou:** 87 (1.9%)
- **⚠️ Erros:** 116 (2.6%) - **CRÍTICO**
- **⏭️ Pulados:** 87 (1.9%)
- **CUDA OOM:** 188 ocorrências
- **Duração:** 1h 31min (5490s)

### Problemas Identificados

#### 1. CUDA Out of Memory (188 ocorrências) - 🔴 CRÍTICO
**Padrão:**
```
CUDA out of memory. Tried to allocate 46.00 MiB.
GPU 0 has a total capacity of 3.81 GiB of which 16.19 MiB is free.
Process 2126427 has 384.00 MiB memory in use.
Process 2126425 has 384.00 MiB memory in use.
Process 2126426 has 384.00 MiB memory in use.
Of the allocated memory 1.69 GiB is allocated by PyTorch,
and 130.07 MiB is reserved by PyTorch but unallocated.
```

**Causa Raiz:**
- **Múltiplos processos PyTorch** compartilhando GPU (3-4 processos simultâneos)
- **Fragmentação de memória** (130-162 MiB reservados mas não alocados)
- **Modelos não liberados** após uso (SentenceTransformer, embeddings)
- **GPU pequena** (3.81 GiB) para testes paralelos

#### 2. Agentes sem `_embedding_model` (136 erros) - 🟡 MÉDIO
**Padrão:**
```
'OrchestratorAgent' object has no attribute '_embedding_model'
'EnhancedCodeAgent' object has no attribute '_embedding_model'
'CodeAgent' object has no attribute '_embedding_model'
```

**Impacto:** Agentes não conseguem se registrar no SharedWorkspace

#### 3. Referência Incorreta a "gpt-4" (6 ocorrências) - 🟡 BAIXO
**Padrão:**
```
Neural component initialized: gpt-4 (provider=ollama, temp=0.7)
```

**Status:** Já corrigido em testes, mas ainda aparece em logs

---

## 🎯 PLANO DE CORREÇÃO

### Fase 1: Consolidação de Memória GPU (PRIORIDADE MÁXIMA)

**⚠️ CORREÇÃO CONCEITUAL:** Não deletar memórias, mas **consolidar** (comprimir e reprimir para inconsciente criptografado).

#### 1.1 Adicionar Fixture de Consolidação em `tests/conftest.py`

```python
import pytest
import torch
from src.memory.gpu_memory_consolidator import get_gpu_consolidator

@pytest.fixture(autouse=True)
def consolidate_gpu_memory():
    """Consolida memória GPU ao invés de deletar."""
    consolidator = get_gpu_consolidator()

    yield

    # Após teste, verificar se precisa consolidar
    if consolidator.should_consolidate():
        # Coletar memórias ativas
        memory_items = _collect_active_memories()

        # Consolidar (comprimir e reprimir para inconsciente)
        stats = consolidator.consolidate_gpu_memory(
            memory_items,
            process_context=f"test_{pytest.current_test_name()}",
        )

        logger.info(f"🧠 Consolidação: {stats}")
```

**Arquivo:** `tests/conftest.py`
**Estimativa:** 1h (inclui coleta de memórias)

#### 1.2 Consolidação em Modelos de Embedding

**Arquivo:** `src/memory/episodic_memory.py` (linha 92)

```python
# ANTES:
self.embedding_model = SentenceTransformer(model_name, device=device)

# DEPOIS:
from src.memory.gpu_memory_consolidator import get_gpu_consolidator

try:
    self.embedding_model = SentenceTransformer(model_name, device=device)
except torch.cuda.OutOfMemoryError:
    logger.warning(f"CUDA OOM ao carregar {model_name}. Consolidando memórias...")

    # Consolidar memórias existentes antes de fallback
    consolidator = get_gpu_consolidator()
    if consolidator.should_consolidate():
        memory_items = _collect_embedding_memories()
        consolidator.consolidate_gpu_memory(memory_items, process_context="episodic_memory")

    # Fallback para CPU
    self.embedding_model = SentenceTransformer(model_name, device='cpu')
    logger.info("Usando CPU para embeddings (fallback após consolidação)")
```

**Estimativa:** 1h

#### 1.3 Consolidação em Fixtures de Teste

**Arquivo:** `tests/conftest.py` - Fixtures que usam GPU

```python
from src.memory.gpu_memory_consolidator import get_gpu_consolidator

@pytest.fixture
def embedding_model():
    """Fixture com consolidação automática."""
    model = SentenceTransformer('all-MiniLM-L6-v2')
    yield model

    # Consolidar ao invés de deletar
    consolidator = get_gpu_consolidator()
    if consolidator.should_consolidate():
        memory_items = [{
            'data': model.state_dict() if hasattr(model, 'state_dict') else None,
            'type': 'sentence_transformer',
            'metadata': {'model_name': 'all-MiniLM-L6-v2'},
        }]
        consolidator.consolidate_gpu_memory(memory_items, process_context="embedding_model_fixture")

    # Limpeza apenas após consolidação
    del model
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
```

**Estimativa:** 2h (encontrar todas as fixtures)

---

### Fase 2: Correção de Agentes (PRIORIDADE MÉDIA)

#### 2.1 Adicionar `_embedding_model` aos Agentes

**Arquivo:** `src/agents/react_agent.py` (linha 203)

```python
def _init_workspace_integration(self):
    """Inicializa integração com SharedWorkspace."""
    try:
        if self.workspace is None:
            self.workspace = get_shared_workspace()

        # CRÍTICO: Inicializar embedding model antes de registrar
        if not hasattr(self, '_embedding_model'):
            from sentence_transformers import SentenceTransformer
            self._embedding_model = SentenceTransformer(
                'sentence-transformers/all-MiniLM-L6-v2',
                device='cpu'  # Usar CPU por padrão para evitar OOM
            )

        # Registrar agente no workspace
        self.workspace.register_agent(
            agent_id=self.agent_id,
            embedding_model=self._embedding_model
        )
    except Exception as e:
        logger.warning(f"Erro ao registrar agente no workspace: {e}")
```

**Arquivos Afetados:**
- `src/agents/react_agent.py`
- `src/agents/orchestrator_agent.py` (herda de ReactAgent)
- `src/agents/code_agent.py` (herda de ReactAgent)
- `src/agents/enhanced_code_agent.py` (herda de CodeAgent)

**Estimativa:** 2h

---

### Fase 3: Fallback Inteligente GPU → CPU

#### 3.1 Melhorar `HybridResourceManager`

**Arquivo:** `src/monitor/resource_manager.py` (linha 83)

```python
def allocate_task(self, task_type: str, estimated_size_mb: float) -> Literal["cuda", "cpu"]:
    """Decide onde alocar tarefa baseado em carga atual."""
    if not self.gpu_available:
        return "cpu"

    stats = self.get_system_status()

    # CRÍTICO: Se VRAM > 85%, forçar CPU imediatamente
    if stats["vram"] > 85.0:
        logger.warning(
            f"VRAM Critical ({stats['vram']:.1f}%), "
            f"forcing CPU fallback for {task_type}"
        )
        # Limpar cache antes de fallback
        torch.cuda.empty_cache()
        return "cpu"

    # Se tentando alocar > 200MB e VRAM > 70%, usar CPU
    if estimated_size_mb > 200 and stats["vram"] > 70.0:
        logger.info(
            f"Large allocation ({estimated_size_mb:.1f}MB) com VRAM alta "
            f"({stats['vram']:.1f}%), usando CPU"
        )
        return "cpu"

    # Resto da lógica existente...
    return "cuda" if task_type in ["math", "quantum", "tensor"] else "cpu"
```

**Estimativa:** 1h

#### 3.2 Fallback Automático em SentenceTransformer

**Arquivo:** `src/utils/device_utils.py`

```python
def get_sentence_transformer_device() -> str:
    """Retorna device para SentenceTransformer com fallback inteligente."""
    if not torch.cuda.is_available():
        return "cpu"

    # Verificar memória disponível
    try:
        stats = torch.cuda.memory_stats(0)
        allocated = stats.get("allocated_bytes.all.current", 0) / 1024**3  # GB
        reserved = stats.get("reserved_bytes.all.current", 0) / 1024**3  # GB

        # Se > 80% da GPU está em uso, usar CPU
        total_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
        usage_percent = (reserved / total_memory) * 100

        if usage_percent > 80:
            logger.warning(
                f"GPU memory usage {usage_percent:.1f}% > 80%, "
                "using CPU for SentenceTransformer"
            )
            return "cpu"
    except Exception as e:
        logger.warning(f"Erro ao verificar memória GPU: {e}, usando CPU")
        return "cpu"

    return "cuda"
```

**Estimativa:** 1h

---

## 🧪 ESTRATÉGIA DE TESTES EM GRUPOS

### Objetivo
Entender **quando, onde e por quê** a GPU falha por memória, e quando o sistema faz fallback para CPU.

### Metodologia

#### Grupo 1: Testes de Embedding (Isolados)
**Objetivo:** Entender consumo de memória por modelo de embedding

```bash
# Executar apenas testes que usam SentenceTransformer
pytest tests/memory/test_hybrid_retrieval.py \
    tests/memory/test_semantic_cache.py \
    tests/memory/test_phase_24_basic.py \
    -v --tb=short \
    --log-cli-level=INFO \
    2>&1 | tee logs/test_group_embeddings.log
```

**Métricas a coletar:**
- Memória GPU antes/depois de cada teste
- Quando ocorre OOM
- Se fallback para CPU funciona
- Tempo de execução

**Script de monitoramento:**
```python
# scripts/monitor_gpu_tests.py
import torch
import time
import subprocess

def monitor_gpu_during_test(test_path: str):
    """Monitora uso de GPU durante teste."""
    if not torch.cuda.is_available():
        print("GPU não disponível")
        return

    print(f"Monitorando: {test_path}")
    print("Tempo | Alocada (GB) | Reservada (GB) | Livre (GB)")
    print("-" * 60)

    start = time.time()
    while True:
        stats = torch.cuda.memory_stats(0)
        allocated = stats["allocated_bytes.all.current"] / 1024**3
        reserved = stats["reserved_bytes.all.current"] / 1024**3
        free = torch.cuda.get_device_properties(0).total_memory / 1024**3 - reserved

        elapsed = time.time() - start
        print(f"{elapsed:6.1f}s | {allocated:8.3f} | {reserved:10.3f} | {free:8.3f}")
        time.sleep(0.5)
```

#### Grupo 2: Testes de Agentes (Sequenciais)
**Objetivo:** Entender acúmulo de memória entre testes

```bash
# Executar testes de agentes em sequência (sem paralelismo)
pytest tests/agents/test_enhanced_code_agent_integration.py \
    tests/agents/test_orchestrator_agent.py \
    tests/agents/test_orchestrator_workflow.py \
    -v --tb=short \
    -x \  # Parar no primeiro erro
    --log-cli-level=INFO \
    2>&1 | tee logs/test_group_agents_sequential.log
```

**Análise:**
- Memória acumula entre testes?
- Limpeza automática funciona?
- Qual teste causa OOM?

#### Grupo 3: Testes de Consciência (GPU Intensivos)
**Objetivo:** Entender uso de GPU em cálculos de Φ

```bash
# Executar testes que calculam Phi
pytest tests/consciousness/ \
    -v --tb=short \
    -m "not slow" \
    --log-cli-level=INFO \
    2>&1 | tee logs/test_group_consciousness.log
```

**Métricas:**
- Uso de GPU durante cálculo de Φ
- Quando ocorre OOM
- Se cálculos vão para CPU quando GPU cheia

#### Grupo 4: Testes MCP (Integração)
**Objetivo:** Entender impacto de múltiplos processos

```bash
# Executar testes MCP (que podem criar múltiplos processos)
pytest tests/integrations/test_mcp_*.py \
    -v --tb=short \
    --log-cli-level=INFO \
    2>&1 | tee logs/test_group_mcp.log
```

**Análise:**
- Quantos processos PyTorch simultâneos?
- Memória compartilhada vs isolada
- Quando processos competem por GPU

---

## 📈 ANÁLISE DE SEQUÊNCIA DE EXECUÇÃO

### Script de Análise de Sequência

```python
# scripts/analyze_test_sequence.py
"""
Analisa sequência de execução de testes para identificar padrões de OOM.
"""

import re
from collections import defaultdict
from pathlib import Path

def analyze_oom_sequence(log_path: str):
    """Analisa quando OOM ocorre na sequência de testes."""

    oom_tests = []
    test_sequence = []
    current_test = None

    with open(log_path, 'r') as f:
        for line in f:
            # Detectar início de teste
            test_match = re.search(r'tests/[^:]+::[^:]+::([^\s]+)', line)
            if test_match:
                current_test = test_match.group(0)
                test_sequence.append(current_test)

            # Detectar OOM
            if 'CUDA out of memory' in line or 'torch.OutOfMemoryError' in line:
                if current_test:
                    oom_tests.append({
                        'test': current_test,
                        'position': len(test_sequence),
                        'line': line.strip()[:200]
                    })

    # Análise
    print("=" * 70)
    print("ANÁLISE DE SEQUÊNCIA DE OOM")
    print("=" * 70)
    print(f"\nTotal de testes executados: {len(test_sequence)}")
    print(f"Total de OOM: {len(oom_tests)}")
    print(f"\nPrimeiros 10 OOM:")
    for i, oom in enumerate(oom_tests[:10], 1):
        print(f"  {i}. Teste #{oom['position']}: {oom['test']}")

    # Agrupar por tipo de teste
    by_type = defaultdict(list)
    for oom in oom_tests:
        test_type = oom['test'].split('::')[0]  # tests/agents/...
        by_type[test_type].append(oom)

    print(f"\nOOM por tipo de teste:")
    for test_type, ooms in sorted(by_type.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {test_type}: {len(ooms)} ocorrências")

    return oom_tests, test_sequence
```

---

## ✅ CHECKLIST DE EXECUÇÃO

### Pré-Correção
- [ ] Backup do código atual
- [ ] Documentar estado atual (relatórios forenses)
- [ ] Criar branch: `fix/gpu-memory-management`

### Correções
- [ ] Fase 1.1: Adicionar fixture `cleanup_gpu_memory` em `conftest.py`
- [ ] Fase 1.2: Limpeza explícita em `episodic_memory.py`
- [ ] Fase 1.3: Limpeza em fixtures de teste
- [ ] Fase 2.1: Adicionar `_embedding_model` aos agentes
- [ ] Fase 3.1: Melhorar `HybridResourceManager`
- [ ] Fase 3.2: Fallback automático em `device_utils.py`

### Testes em Grupos
- [ ] Grupo 1: Testes de Embedding (isolados)
- [ ] Grupo 2: Testes de Agentes (sequenciais)
- [ ] Grupo 3: Testes de Consciência (GPU intensivos)
- [ ] Grupo 4: Testes MCP (integração)

### Análise
- [ ] Executar `analyze_test_sequence.py` em cada grupo
- [ ] Comparar memória GPU antes/depois
- [ ] Verificar se fallback CPU funciona
- [ ] Documentar padrões encontrados

### Validação Final
- [ ] Executar suite completa: `./scripts/run_tests_fast.sh`
- [ ] Comparar com relatório anterior:
  - Redução de OOM?
  - Redução de erros?
  - Taxa de sucesso melhorou?
- [ ] Gerar novo relatório forense
- [ ] Comparar relatórios: `python scripts/omnimind_log_forensics.py --compare`

---

## 📝 NOTAS TÉCNICAS

### Quando Teste Vai para CPU

**Cenários:**
1. **GPU não disponível:** `torch.cuda.is_available() == False`
2. **VRAM > 85%:** `HybridResourceManager` força CPU
3. **Alocação > 200MB com VRAM > 70%:** Fallback preventivo
4. **OOM capturado:** Try/except força CPU
5. **Modelo pequeno:** SentenceTransformer pode usar CPU por padrão

### Quando Teste NÃO Vai para CPU

**Cenários:**
1. **VRAM < 70%:** GPU é preferida
2. **Tarefa GPU-intensiva:** Cálculos de Φ, tensores grandes
3. **Sem fallback implementado:** Código antigo sem try/except

### Impacto de Múltiplos Processos

**Problema:**
- 3-4 processos PyTorch compartilhando GPU
- Cada processo aloca ~384 MiB
- Total: ~1.5 GiB apenas em processos
- Sobra ~2.3 GiB para modelos/tensores

**Solução:**
- Limpeza entre testes (fixture)
- Fallback preventivo (VRAM > 85%)
- Serialização de testes GPU-intensivos

---

## 🎯 MÉTRICAS DE SUCESSO

### Antes (Estado Atual)
- CUDA OOM: 188 ocorrências
- Erros: 116
- Taxa de sucesso: 95.6%

### Meta (Após Correções)
- CUDA OOM: < 20 ocorrências (redução de 90%)
- Erros: < 50 (redução de 57%)
- Taxa de sucesso: > 98%

### Indicadores
- ✅ Fallback CPU funciona em 100% dos casos de OOM
- ✅ Limpeza de memória reduz fragmentação
- ✅ Agentes se registram no workspace sem erros
- ✅ Testes GPU-intensivos completam sem OOM

---

**Próximos Passos:**
1. Executar Fase 1 (Limpeza de Memória)
2. Testar Grupo 1 (Embeddings)
3. Analisar resultados
4. Iterar com Fase 2 e 3

**Status:** 📋 Plano criado, aguardando execução

