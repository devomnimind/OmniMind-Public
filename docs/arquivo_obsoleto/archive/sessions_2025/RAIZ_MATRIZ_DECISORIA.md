# 📊 MATRIZ DECISÓRIA: MOVER OU FICAR NA RAIZ

**Documento:** Decisões por arquivo com justificativa técnica  
**Data:** 2 de dezembro de 2025

---

## 🎯 LEGENDA

- 🔴 **CRÍTICO:** Quebra sistema se movido incorretamente
- 🟠 **IMPORTANTE:** Cuidado necessário, mas possível mover
- 🟡 **MODERADO:** Cuidado mínimo necessário
- 🟢 **SEGURO:** Pode mover sem risco

---

## 📋 MATRIZ COMPLETA

| # | Arquivo | Tamanho | Tipo | Risco | **DECISÃO** | Novo Caminho | Motivo | Condições |
|---|---------|---------|------|-------|-----------|--------------|--------|-----------|
| 1 | `conftest.py` | 135 L | Config | 🔴 CRÍTICO | ✅ **MOVER** | `tests/conftest.py` | Pytest procura aqui automaticamente; atual funciona na raiz | Verificar que `tests/` é onde estão 99% dos testes |
| 2 | `conftest_server.py` | 155 L | Config | 🟢 SEGURO | ✅ **MOVER** | `tests/fixtures/conftest_server.py` | Arquivo órfão - ninguém importa; não é usado | Ou deletar se funcionalidade foi integrada em conftest.py |
| 3 | `pytest_timeout_retry.py` | 71 L | Plugin | 🔴 CRÍTICO | ✅ **MOVER** | `tests/plugins/pytest_timeout_retry.py` | Importado por conftest.py; risco de path break | Atualizar import em `tests/conftest.py`: adicionar sys.path |
| 4 | `pytest_server_monitor.py` | 169 L | Plugin | 🔴 CRÍTICO | ✅ **MOVER** | `tests/plugins/pytest_server_monitor.py` | Importado por conftest.py; risco de path break | Atualizar import em `tests/conftest.py`: adicionar sys.path |
| 5 | `run_tests_gpu.py` | 185 L | Runner | 🟠 IMPORTANTE | ✅ **MOVER** | `scripts/run_tests_gpu.py` | Standalone; usa paths relativos | Converter paths relativos para PROJECT_ROOT absolutos |
| 6 | `run_consciousness_tests_gpu.sh` | 181 L | Shell | 🟠 IMPORTANTE | ✅ **MOVER** | `scripts/run_consciousness_tests_gpu.sh` | Standalone; mas com hardcoded `/home/fahbrain/` | Remover paths absolutos; usar `cd "$(dirname "$0")/.."` |
| 7 | `run_tests_with_server.sh` | 110 L | Shell | 🟠 IMPORTANTE | ✅ **MOVER** | `scripts/run_tests_with_server.sh` | Standalone; hardcoded paths | Remover paths absolutos; usar relativos |
| 8 | `monitor_suite.sh` | 45 L | Shell | 🟡 MODERADO | ✅ **MOVER** | `scripts/monitor_suite.sh` | Standalone; hardcoded PID/LOG | Tornar parametrizável (`$1`, `$2`) |
| 9 | `test_affective_extension.py` | 192 L | Demo | 🟢 SEGURO | ✅ **MOVER** | `scripts/demos/test_affective_extension.py` | Demo/Exploração; ninguém referencia | Se executável: python scripts/demos/test_affective_extension.py |
| 10 | `test_affective_simple.py` | 94 L | Demo | 🟢 SEGURO | ✅ **MOVER** | `scripts/demos/test_affective_simple.py` | Demo; ninguém referencia | Mesmo que acima |
| 11 | `test_rsi_simple.py` | 65 L | Demo | 🟢 SEGURO | ✅ **MOVER** | `scripts/demos/test_rsi_simple.py` | Demo; ninguém referencia | Mesmo que acima |
| 12 | `test_symbolic_register.py` | 85 L | Demo | 🟢 SEGURO | ✅ **MOVER** | `scripts/demos/test_symbolic_register.py` | Demo; ninguém referencia | Mesmo que acima |
| 13 | `lacanian_vs_cognitive_demo.py` | 71 L | Demo | 🟢 SEGURO | ✅ **MOVER** | `scripts/demos/lacanian_vs_cognitive_demo.py` | Demo educativo; ninguém referencia | Executável direto: python scripts/demos/... |
| 14 | `affective_extension_results.py` | 67 L | Demo | 🟢 SEGURO | ✅ **MOVER** | `scripts/demos/affective_extension_results.py` | Demo/Documentação; ninguém referencia | Mesmo que acima |
| 15 | `ablations_corrected_latest.json` | 4.5K | Data | 🟢 SEGURO | ✅ **MOVER** | `data/results/ablations_corrected_latest.json` | Output de testes; organizar com dados | Atualizar scripts que referenciam se houver |
| 16 | `integrated_suite_results.json` | 19K | Data | 🟢 SEGURO | ✅ **MOVER** | `data/results/integrated_suite_results.json` | Output de testes; organizar com dados | Mesmo que acima |
| 17 | `test_final.json` | 1.1K | Data | 🟢 SEGURO | ✅ **MOVER** | `data/results/test_final.json` | Output de testes; organizar com dados | Mesmo que acima |
| 18 | `pytest_dryrun.log` | 227K | Log | 🟢 SEGURO | ✅ **MOVER** | `data/test_reports/pytest_dryrun.log` | Log antigo; organizar com logs | Mover apenas se não mais necessário |
| 19 | `sha256_original.log` | 4.1M | Audit | 🟢 SEGURO | ✅ **MOVER** | `data/audit/sha256_original.log` | Auditoria histórica; organizar com audits | Mover apenas se não mais necessário |

---

## 🔍 ANÁLISE POR RISCO

### 🔴 CRÍTICOS (3 arquivos) - ATENÇÃO ESPECIAL

#### 1️⃣ `conftest.py`
**Status Atual:** Raiz  
**Por que crítico?** Pytest procura automaticamente em raiz e recursivamente  
**Se mover para `tests/conftest.py`:**
- ✅ Pytest ENCONTRA (procura recursivamente)
- ⚠️ MAS: Fixtures e markers só valem para `tests/`
- ✅ OK: Todos os testes estão em `tests/` mesmo assim

**Verificação:** Há testes em `omnimind/test_*.py` fora de `tests/`?
```bash
cd /home/fahbrain/projects/omnimind
find . -maxdepth 1 -name "test_*.py" -type f
```
Resultado esperado: Vazio (todos os testes estão em `tests/`)

✅ **SAFE TO MOVE** se resultado vazio

---

#### 2️⃣ `pytest_timeout_retry.py`
**Status Atual:** Raiz  
**Por que crítico?** Importado por conftest.py linha 26:
```python
from pytest_timeout_retry import TimeoutRetryPlugin  # ← Procura na raiz
```

**Se mover para `tests/plugins/pytest_timeout_retry.py`:**
- ❌ QUEBRA: ModuleNotFoundError se conftest.py ficar na raiz
- ✅ OK: Se conftest.py também se mover para `tests/`

**Condição:**
```python
# Em tests/conftest.py (NOVO):
import sys
import os
plugin_path = os.path.join(os.path.dirname(__file__), 'plugins')
sys.path.insert(0, plugin_path)
from pytest_timeout_retry import TimeoutRetryPlugin
```

✅ **SAFE TO MOVE** com atualização de conftest.py

---

#### 3️⃣ `pytest_server_monitor.py`
**Status Atual:** Raiz  
**Por que crítico?** Mesma situação que `pytest_timeout_retry.py`  
**Solução:** Mesma

✅ **SAFE TO MOVE** com atualização de conftest.py

---

### 🟠 IMPORTANTES (5 arquivos) - CUIDADO COM PATHS

#### 4️⃣ `run_tests_gpu.py`
**Status Atual:** Raiz  
**Problema:** Usa caminhos relativos tipo `tests/` e `data/`

**Se mover para `scripts/run_tests_gpu.py`:**
- ⚠️ RISKY: Se executado de outro diretório, paths quebram
- ✅ OK: Se adicionar PROJECT_ROOT detection

**Fix:**
```python
# Detectar PROJECT_ROOT
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_DIR = os.path.join(PROJECT_ROOT, 'tests')
```

✅ **SAFE TO MOVE** com projeto root detection

---

#### 5-8️⃣ Shell Scripts (4 arquivos)
**Status:** Todos com HARDCODED `/home/fahbrain/projects/omnimind`

**Exemplo problema:**
```bash
# Atual em run_consciousness_tests_gpu.sh:
cd /home/fahbrain/projects/omnimind  # ← HARDCODED, quebra se mudar máquina
```

**Fix:**
```bash
# Novo:
cd "$(dirname "$0")/.."  # ← Relativo ao script, portável
```

✅ **SAFE TO MOVE** com remoção de hardcoding

---

### 🟢 SEGUROS (11 arquivos) - SEM RISCO

- `conftest_server.py` - Órfão (não importado)
- 6 testes demo - Ninguém referencia
- 5 arquivos de dados - Apenas saída, não input

✅ **SAFE TO MOVE** sem verificação

---

## 🚀 ORDEM DE EXECUÇÃO RECOMENDADA

### FASE 1: BACKUP (Risco: 0%)
```bash
cd /home/fahbrain/projects/omnimind
git add -A
git commit -m "Backup: Estado antes de organização de raiz"
git branch refactor/organize-root
```

### FASE 2: MOVER SEGUROS (Risco: 0%)
```bash
# Testes demo
mkdir -p scripts/demos
mv test_affective_*.py lacanian_vs_cognitive_demo.py affective_extension_results.py scripts/demos/

# Dados
mkdir -p data/results data/audit
mv ablations_corrected_latest.json integrated_suite_results.json test_final.json data/results/
mv sha256_original.log data/audit/
mv pytest_dryrun.log data/test_reports/

git add -A && git commit -m "Refactor: Organize demos and data files"
```

### FASE 3: VALIDAR TESTES (Risco: 1%)
```bash
# Verificar que todos os testes rodam
python -m pytest tests/ --collect-only -q

# Se OK: continuar
# Se FALHA: rollback
```

### FASE 4: SCRIPTS SHELL (Risco: 5%)
```bash
# Editar para remover hardcoding
# Mover scripts
mkdir -p scripts
sed -i 's|cd /home/fahbrain/projects/omnimind|cd "$(dirname "$0")/.." |g' run_consciousness_tests_gpu.sh
mv run_consciousness_tests_gpu.sh run_tests_with_server.sh monitor_suite.sh scripts/

git add -A && git commit -m "Refactor: Move shell scripts with portable paths"
```

### FASE 5: RUNNER PYTHON (Risco: 10%)
```bash
# Editar para usar PROJECT_ROOT
# Mover
mkdir -p scripts
mv run_tests_gpu.py scripts/

# Testar execução
python scripts/run_tests_gpu.py --help

git add -A && git commit -m "Refactor: Move run_tests_gpu with root detection"
```

### FASE 6: PYTEST CONFIG (Risco: 25% - CRÍTICO)
```bash
# 6.1. Criar estrutura
mkdir -p tests/plugins

# 6.2. Atualizar conftest.py com sys.path setup
# (Ver script abaixo)

# 6.3. Mover plugins
cp pytest_timeout_retry.py tests/plugins/
cp pytest_server_monitor.py tests/plugins/

# 6.4. Mover conftest
mv conftest.py tests/

# 6.5. Remover órfão
rm conftest_server.py pytest_timeout_retry.py pytest_server_monitor.py

# 6.6. VALIDAR CRÍTICO
python -m pytest tests/ --collect-only -q

if [ $? -eq 0 ]; then
    git add -A && git commit -m "Refactor: Move pytest config to tests/"
else
    echo "FALHA! Revertendo..."
    git restore tests/conftest.py tests/plugins/ 
    git checkout pytest_timeout_retry.py pytest_server_monitor.py conftest.py
fi
```

### FASE 7: VALIDAÇÃO FINAL (Risco: 0%)
```bash
# Suite completa
python -m pytest tests/consciousness/ -v

# Se OK: merge
git checkout main
git merge refactor/organize-root
```

---

## 📝 SCRIPT: Novo `tests/conftest.py`

```python
"""Project-wide pytest configuration."""
import os
import sys
import time
import subprocess
import requests
import pytest
import warnings
import torch

# FORÇA GPU/CUDA SE DISPONÍVEL
if torch.cuda.is_available():
    os.environ["CUDA_VISIBLE_DEVICES"] = os.environ.get("CUDA_VISIBLE_DEVICES", "0")
    torch.set_default_device("cuda")
    print(f"✅ PyTorch CUDA forçado: {torch.cuda.get_device_name(0)}")
else:
    print("⚠️  CUDA não disponível - usando CPU")

# Add plugins directory to path
plugin_path = os.path.join(os.path.dirname(__file__), 'plugins')
if plugin_path not in sys.path:
    sys.path.insert(0, plugin_path)

# Add src to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Import custom plugins
from pytest_timeout_retry import TimeoutRetryPlugin
from pytest_server_monitor import ServerMonitorPlugin

# Servidor endpoints
DASHBOARD_URL = "http://localhost:5173"
API_URL = "http://localhost:8000"

# [RESTO DO ARQUIVO IGUAL AO ORIGINAL]
```

---

## 📝 SCRIPT: Atualizado `scripts/run_tests_gpu.py`

```python
#!/usr/bin/env python3
"""
Test runner inteligente com GPU dinâmico
- Saída em tempo real na tela com timestamps
- Salva log com timestamps
- GPU para testes quantum/ollama/mathematical
- CPU para testes padrão
"""
import os
import sys
import subprocess
import re
from datetime import datetime

# Detectar PROJECT_ROOT
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Verificar GPU disponível
CUDA_AVAILABLE = False
try:
    import torch
    CUDA_AVAILABLE = torch.cuda.is_available()
    device_name = torch.cuda.get_device_name(0) if CUDA_AVAILABLE else "CPU"
except Exception:
    device_name = "CPU"

# Padrões para detectar tipos de teste que precisam GPU
GPU_TEST_PATTERNS = [
    r"quantum",
    r"ollama",
    r"mathematical",
    r"quantics",
    r"q_bit",
    r"superposition",
]

LOG_FILE = None


def log_and_print(msg: str):
    """Printa com timestamp e salva em log"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_msg = f"[{timestamp}] {msg}"
    print(formatted_msg)
    if LOG_FILE:
        with open(LOG_FILE, "a") as f:
            f.write(formatted_msg + "\n")


def should_use_gpu(test_path: str) -> bool:
    """Determina se o teste deve rodar em GPU"""
    if not CUDA_AVAILABLE:
        return False
    test_lower = test_path.lower()
    
    # [RESTO DO ARQUIVO]
```

---

## ✅ CHECKLIST PRÉ-EXECUÇÃO

- [ ] Executar: `cd /home/fahbrain/projects/omnimind && find . -maxdepth 1 -name "test_*.py" -type f | wc -l` → resultado deve ser 0 (nenhum teste na raiz fora do tests/)
- [ ] Backup git criado: `git log -1 --oneline`
- [ ] Branch criada: `git branch -a | grep refactor/organize`
- [ ] Leitura de RAIZ_ANALISE_ORGANIZACAO.md completa ✅
- [ ] Compreensão dos riscos por arquivo ✅
- [ ] Preparação dos scripts de atualização ✅
- [ ] Teste de rollback funcionando: `git reset --hard HEAD~1` funciona

---

**PRÓXIMO PASSO:** Confirme se deseja prosseguir com a reorganização!
