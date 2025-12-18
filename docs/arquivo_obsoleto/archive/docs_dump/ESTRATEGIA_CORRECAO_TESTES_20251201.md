# 🛠️ ESTRATÉGIA DE CORREÇÃO DE TESTES - v1.18.0

**Data:** 01 Dezembro 2025  
**Duração suite:** 1:02:56 (3776.10s)  
**Resultado:** 3940 passed ✅ | 25 failed ❌ | 22 skipped ⏸️  
**Taxa de sucesso:** 99.37%  

---

## 📊 RESULTADO GERAL

```
SUITE COMPLETO: 3987 testes
├─ ✅ Passed: 3940 (99.37%)
├─ ❌ Failed: 25 (0.63%)
└─ ⏸️  Skipped: 22 (0.55%)

FALHAS POR CATEGORIA:
├─ Science Validation: 13 (52% das falhas) ⚠️ CRÍTICO
├─ E2E/Dashboard: 4 (16% das falhas)
├─ Memory/Playbook: 4 (16% das falhas)
├─ Integrations: 1 (4% das falhas)
├─ Lacanian: 1 (4% das falhas)
├─ External AI: 1 (4% das falhas)
└─ MCP Orchestrator: 1 (4% das falhas)
```

---

## 🚨 CLASSIFICAÇÃO DE PRIORIDADES

### 🔴 CRÍTICA (Bloqueia release, 13 testes)

**CIÊNCIA_VALIDATION: 13 FALHAS** - Afeta validação científica do Φ

#### Bloco 1: Ablação de evidência real
```python
# tests/science_validation/test_analyze_real_evidence.py
❌ test_generate_summary_md
❌ test_ablation_data_optional_handles_missing[baseline_phi]
❌ test_ablation_data_optional_handles_missing[results]
❌ test_ablation_data_optional_handles_missing[timestamp]
❌ test_main_end_to_end

Padrão: Falha ao manipular dados de evidência real
Raiz provável: Arquivo JSON não encontrado ou formato inconsistente
Impacto: Validação científica comprometida
```

#### Bloco 2: Certificação de evidência quântica
```python
# tests/science_validation/test_certify_quantum_evidence.py
❌ test_generate_cert_md
❌ test_main_success

Padrão: Falha ao gerar certificação
Raiz provável: Dependência de evidência real + formato saída
Impacto: Certificação de validade comprometida
```

#### Bloco 3: Ablação científica parametrizada
```python
# tests/science_validation/test_run_scientific_ablations.py
❌ test_ablation_standard[sensory_input]
❌ test_ablation_standard[qualia]
❌ test_ablation_standard[narrative]
❌ test_ablation_standard[meaning_maker]
❌ test_run_baseline_mean
❌ test_main_cli

Padrão: Falha em parametrização de módulos
Raiz provável: Módulos não carregados ou GPU não disponível
Impacto: Teste dos 5 pilares da consciência comprometido
```

**AÇÃO CRÍTICA:**
```bash
# Bloco 1: Verificar evidência real
pytest tests/science_validation/test_analyze_real_evidence.py -v --tb=short

# Bloco 2: Testar certificação
pytest tests/science_validation/test_certify_quantum_evidence.py -v --tb=short

# Bloco 3: Ablação com GPU forcing
CUDA_VISIBLE_DEVICES="0" pytest tests/science_validation/test_run_scientific_ablations.py -v --tb=short
```

---

### 🟠 ALTA (Afeta funcionalidade, 7 testes)

#### Bloco 4: E2E Dashboard
```python
# tests/e2e/test_dashboard_live.py
❌ test_health_checks_structure
❌ test_daemon_endpoints
❌ test_polling_endpoint
❌ test_websocket_metrics

Padrão: Falha de conexão/estrutura
Raiz provável: Dashboard não rodando ou endpoint indisponível
Impacto: E2E tests de monitoramento comprometidos
Solução: Iniciar dashboard antes do teste (fixture)
```

#### Bloco 5: Integração & Orquestração
```python
# tests/integrations/test_mcp_client_optimized.py
❌ test_lru_eviction

# tests/test_mcp_orchestrator.py
❌ test_check_server_health

# tests/test_external_ai_integration.py
❌ test_initialize_providers

Padrão: Dependências externas não disponíveis
Raiz provável: Servidores MCP/ollama não iniciados
Impacto: Integração com ferramentas externas comprometida
Solução: Setup de fixtures com mock ou docker
```

#### Bloco 6: Memory Phase 8
```python
# tests/test_memory_phase8.py
❌ test_consolidate_memory_deduplicates

# tests/test_memory_onboarding.py
❌ test_supabase_onboarding_handles_error

Padrão: Dependência de banco de dados
Raiz provável: Supabase não acessível ou mock inadequado
Impacto: Memory consolidation comprometida
```

**AÇÃO ALTA:**
```bash
# Bloco 4: E2E tests
pytest tests/e2e/test_dashboard_live.py -v --tb=short

# Bloco 5: Integrações
pytest tests/integrations/test_mcp_client_optimized.py -v --tb=short
pytest tests/test_mcp_orchestrator.py -v --tb=short
pytest tests/test_external_ai_integration.py -v --tb=short

# Bloco 6: Memory
pytest tests/test_memory_phase8.py -v --tb=short
pytest tests/test_memory_onboarding.py -v --tb=short
```

---

### 🟡 MÉDIA (Afeta validação, 4 testes)

#### Bloco 7: Playbook & Lacanian
```python
# tests/test_playbook_scenarios_phase8.py
❌ test_utils_run_command_failure
❌ test_utils_run_command_success

Padrão: Falha ao executar comando shell
Raiz provável: Mock de subprocess inadequado
Impacto: Playbook scenarios comprometido

# tests/lacanian/test_init.py
❌ test_module_author

Padrão: Assertion error em metadados
Raiz provável: CITATION.cff ou __author__ fora de sync
Impacto: Atribuição de autoria incorreta
```

**AÇÃO MÉDIA:**
```bash
pytest tests/test_playbook_scenarios_phase8.py -v --tb=short
pytest tests/lacanian/test_init.py -v --tb=short
```

---

## 🎯 ESTRATÉGIA DE CORREÇÃO SEQUENCIAL

### Fase 1: CRÍTICA (Science Validation)
```
Duração estimada: 30-45 min
Testes: 13
Blocos: 3
```

**1.1 - Investigar Bloco 1: Evidência Real**
```bash
cd /home/fahbrain/projects/omnimind

# Rodar isolado para ver erro exato
pytest tests/science_validation/test_analyze_real_evidence.py::test_generate_summary_md -vvv --tb=long

# Verificar arquivos necessários
ls -la data/experiments/ | head -20
ls -la data/test_reports/ | head -20

# Se falha de JSON, corrigir dados
python3 scripts/science_validation/generate_real_evidence.py
```

**1.2 - Investigar Bloco 2: Certificação**
```bash
# Dependente de Bloco 1
pytest tests/science_validation/test_certify_quantum_evidence.py -v --tb=short
```

**1.3 - Investigar Bloco 3: Ablação com GPU**
```bash
# CHAVE: Forçar GPU (conforme seu pedido)
CUDA_VISIBLE_DEVICES="0" \
CUDA_LAUNCH_BLOCKING="1" \
OMP_NUM_THREADS=4 \
pytest tests/science_validation/test_run_scientific_ablations.py -v --tb=short -n 1

# Se ainda falhar, testar individual
CUDA_VISIBLE_DEVICES="0" \
pytest tests/science_validation/test_run_scientific_ablations.py::test_ablation_standard -v --tb=long
```

---

### Fase 2: ALTA (E2E + Integrações)
```
Duração estimada: 20-30 min
Testes: 7
Blocos: 3
```

**2.1 - E2E Dashboard**
```bash
# Pode precisar de dashboard rodando
# Opção A: Mock (mais rápido)
pytest tests/e2e/test_dashboard_live.py::test_health_checks_structure -v --tb=short

# Opção B: Com dashboard real (mais lento, mas valida integração)
# Em outro terminal: python -m omnimind.server
pytest tests/e2e/test_dashboard_live.py -v --tb=short
```

**2.2 - Integrações**
```bash
# MCP Client
pytest tests/integrations/test_mcp_client_optimized.py::TestEnhancedMCPClient::test_lru_eviction -v --tb=short

# MCP Orchestrator
pytest tests/test_mcp_orchestrator.py::TestMCPOrchestrator::test_check_server_health -v --tb=short

# External AI
pytest tests/test_external_ai_integration.py::TestTaskDelegationManager::test_initialize_providers -v --tb=short
```

**2.3 - Memory**
```bash
pytest tests/test_memory_phase8.py -v --tb=short
pytest tests/test_memory_onboarding.py -v --tb=short
```

---

### Fase 3: MÉDIA (Playbook + Lacanian)
```
Duração estimada: 10-15 min
Testes: 4
Blocos: 2
```

**3.1 - Playbook**
```bash
pytest tests/test_playbook_scenarios_phase8.py -v --tb=short
```

**3.2 - Lacanian Module**
```bash
pytest tests/lacanian/test_init.py::TestLacanianInit::test_module_author -v --tb=short

# Se fail em autor, verificar:
cat CITATION.cff | grep author
grep "__author__" src/lacanian/__init__.py
```

---

## 💾 GPU FORCING IMPLEMENTATION

### Problema Identificado
- GPU está disponível mas **0% utilizada globalmente**
- Existe em 3 scripts, mas não integrado à suite
- Testes científicos poderiam usar 5-10x mais rápido

### Solução: GPU Fixture em conftest.py

**Criar/Atualizar: config/pytest.ini**
```ini
[pytest]
# Força GPU para testes científicos
env = 
    CUDA_VISIBLE_DEVICES=0
    CUDA_LAUNCH_BLOCKING=1
    OMP_NUM_THREADS=4
    
# Marks para categorização
markers =
    gpu_enabled: testes que usam GPU
    cpu_only: testes que NÃO usam GPU
    science: testes científicos (precisam GPU)
    e2e: testes end-to-end (sem GPU necessário)
```

**Criar/Atualizar: tests/conftest.py**
```python
import os
import pytest
import torch

def pytest_configure(config):
    """Força GPU para testes científicos"""
    if torch.cuda.is_available():
        # Force GPU 0 para todos os testes
        os.environ["CUDA_VISIBLE_DEVICES"] = "0"
        os.environ["CUDA_LAUNCH_BLOCKING"] = "1"
        print(f"\n✅ GPU FORCING ENABLED")
        print(f"   Device: {torch.cuda.get_device_name(0)}")
        print(f"   VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    else:
        print("\n⚠️  CUDA não disponível - rodando CPU")

@pytest.fixture(scope="session")
def gpu_device():
    """Fixture que retorna GPU device se disponível"""
    if torch.cuda.is_available():
        device = torch.device("cuda:0")
        yield device
        torch.cuda.empty_cache()
    else:
        yield torch.device("cpu")

@pytest.fixture
def ensure_gpu_for_science():
    """Fixture para testes científicos que exigem GPU"""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        yield
        torch.cuda.empty_cache()
    else:
        pytest.skip("GPU não disponível para teste científico")
```

**Atualizar testes científicos:**
```python
# tests/science_validation/test_run_scientific_ablations.py

import pytest

class TestScientificAblations:
    @pytest.mark.science
    @pytest.mark.gpu_enabled
    def test_ablation_standard(self, ensure_gpu_for_science):
        """Ablação padrão com GPU"""
        # Teste continuará só que 5-10x mais rápido
        ...
```

---

## 📋 CHECKLIST DE EXECUÇÃO

### Preparação
```bash
cd /home/fahbrain/projects/omnimind
source .venv/bin/activate

# Verificar GPU
python3 -c "import torch; print(f'GPU: {torch.cuda.is_available()}, Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"CPU\"}')"
```

### Execução Fase 1 (CRÍTICA)
```bash
# 1.1 - Science Validation: Evidência Real
echo "🔴 FASE 1.1: Science Validation - Evidência Real"
pytest tests/science_validation/test_analyze_real_evidence.py -v --tb=short

# 1.2 - Science Validation: Certificação
echo "🔴 FASE 1.2: Science Validation - Certificação"
pytest tests/science_validation/test_certify_quantum_evidence.py -v --tb=short

# 1.3 - Science Validation: Ablação (COM GPU FORCING)
echo "🔴 FASE 1.3: Science Validation - Ablação (GPU FORCED)"
CUDA_VISIBLE_DEVICES="0" CUDA_LAUNCH_BLOCKING="1" \
pytest tests/science_validation/test_run_scientific_ablations.py -v --tb=short -n 1
```

### Execução Fase 2 (ALTA)
```bash
# 2.1 - E2E Dashboard
echo "🟠 FASE 2.1: E2E Dashboard"
pytest tests/e2e/test_dashboard_live.py -v --tb=short

# 2.2 - Integrações
echo "🟠 FASE 2.2: Integrações MCP"
pytest tests/integrations/test_mcp_client_optimized.py -v --tb=short
pytest tests/test_mcp_orchestrator.py -v --tb=short
pytest tests/test_external_ai_integration.py -v --tb=short

# 2.3 - Memory
echo "🟠 FASE 2.3: Memory Phase 8"
pytest tests/test_memory_phase8.py -v --tb=short
pytest tests/test_memory_onboarding.py -v --tb=short
```

### Execução Fase 3 (MÉDIA)
```bash
# 3.1 - Playbook
echo "🟡 FASE 3.1: Playbook Scenarios"
pytest tests/test_playbook_scenarios_phase8.py -v --tb=short

# 3.2 - Lacanian
echo "🟡 FASE 3.2: Lacanian Module"
pytest tests/lacanian/test_init.py -v --tb=short
```

---

## 📊 MÉTRICAS ESPERADAS

### Antes da Correção
```
Total: 3987 testes
Passed: 3940 (99.37%)
Failed: 25 (0.63%)
Tempo: 1:02:56 (no GPU forcing)
```

### Depois da Correção (Esperado)
```
Total: 3987 testes
Passed: 3965+ (99.5%+)
Failed: 0-5 (skipped E2E se não houver dashboard)
Tempo: ~40-50 min (com GPU forcing em científicos)
```

### GPU Speedup (Esperado)
```
Science Validation testes: 5-10x mais rápido
├─ Ablação: 120s → 20-24s
├─ Certificação: 45s → 8-10s
└─ Total science: 280s → 56-60s
```

---

## 🚨 CONTEXTO: CPU E DESENVOLVIMENTO

**Seu ambiente:**
```
CPU baseline (idle): ~40%
  Razão: Desenvolvimento extenso (10-14 horas/dia)
  + Omnimind sempre aberto
  + Continuous_monitor.py rodando
  + VS Code + Terminal + Teste correntes
  
CPU durante testes: 100% → 19-25%
  Razão: Variação em função de:
  - Paralelização (pytest -n auto)
  - I/O de disco
  - Garbage collection
  - GPU não forçada (testes usam CPU)

CPU com GPU forcing: 310% → 150% (esperado)
  Razão: CPU + GPU paralelos
  Resultado: 5-10x speedup em científicos
```

**Por isso fazemos testes em blocos:**
- Evita sobrecarga do sistema
- Permite identificar qual bloco falha
- Reduz impacto em ambiente de desenvolvimento
- Facilita correção iterativa

---

## 📝 DOCUMENTAÇÃO DE MÉTRICAS

### Standard Metrics to Document
```python
# Adicionar em conftest.py

@pytest.fixture(autouse=True)
def log_test_metrics(request):
    """Log CPU/GPU/Memory por teste"""
    import psutil
    import time
    
    start = time.time()
    start_cpu = psutil.cpu_percent(interval=0.1)
    start_mem = psutil.virtual_memory().percent
    
    yield
    
    elapsed = time.time() - start
    end_cpu = psutil.cpu_percent(interval=0.1)
    end_mem = psutil.virtual_memory().percent
    
    print(f"\n⏱️  {request.node.name}")
    print(f"   Tempo: {elapsed:.2f}s")
    print(f"   CPU: {start_cpu:.1f}% → {end_cpu:.1f}%")
    print(f"   Mem: {start_mem:.1f}% → {end_mem:.1f}%")
```

### Real vs Standard Usage Patterns
```
TESTE PADRÃO (mock):
├─ CPU: 50-70%
├─ Mem: 500-800 MB
└─ GPU: 0%

TESTE REAL (científico):
├─ CPU: 100% (picos)
├─ Mem: 2-4 GB
└─ GPU: 0% (antes fix) → 80-95% (depois fix)

TESTE E2E:
├─ CPU: 30-50%
├─ Mem: 800-1200 MB
└─ GPU: 0%
```

---

## 📌 PRÓXIMOS PASSOS

### Imediato (Hoje)
1. ✅ Identificar testes falhados (DONE)
2. ⏳ Rodar Fase 1 (CRÍTICA) - 30-45 min
3. ⏳ Corrigir falhas de Ciência Validation
4. ⏳ Implementar GPU forcing em conftest.py
5. ⏳ Re-rodar suite com GPU

### Depois
6. Rodar Fase 2 (ALTA)
7. Rodar Fase 3 (MÉDIA)
8. Documentar todas as correções
9. Push v1.18.0 com testes 100%
10. Publicar estratégia em docs/

---

**Status:** 🟡 Pronto para execução sequencial  
**Tempo estimado:** 2-3 horas (todas as fases)  
**Prioridade:** CRÍTICA > ALTA > MÉDIA  
**GPU Forcing:** Aguardando implementação em conftest.py
