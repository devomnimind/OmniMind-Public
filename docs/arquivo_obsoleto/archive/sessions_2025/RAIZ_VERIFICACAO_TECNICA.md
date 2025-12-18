# 🔬 VERIFICAÇÃO TÉCNICA PROFUNDA - Cada Arquivo

**Documento:** Análise de código com grep/imports para confirmar segurança de movimento  
**Data:** 2 de dezembro de 2025

---

## 📌 METODOLOGIA

Para cada arquivo, vou:
1. **Listar TODOS os imports** (dependências explícitas)
2. **Buscar REFERÊNCIAS** em todo workspace (dependências implícitas)
3. **Determinar RISCO** baseado em dependências
4. **PROPOR NOVO CAMINHO** com segurança garantida

---

## 🔍 VERIFICAÇÃO ARQUIVO POR ARQUIVO

### ✅ 1. `conftest.py` (RAIZ)

**Imports (linha-por-linha):**
```python
1. import os                                          # stdlib ✅
2. import sys                                         # stdlib ✅
3. import time                                        # stdlib ✅
4. import subprocess                                  # stdlib ✅
5. import requests                                    # external (pip)
6. import pytest                                      # external (pip)
7. import warnings                                    # stdlib ✅
8. import torch                                       # external (pip)
9. from pytest_timeout_retry import TimeoutRetryPlugin      # LOCAL ⚠️
10. from pytest_server_monitor import ServerMonitorPlugin   # LOCAL ⚠️
```

**Dependências Externas:**
- `pytest` - OK (installed)
- `requests` - OK (installed)
- `torch` - OK (installed)

**Dependências Locais:**
- `pytest_timeout_retry` (RAIZ) - Encontrado ✅
- `pytest_server_monitor` (RAIZ) - Encontrado ✅

**Referências em Workspace:**
```bash
grep -r "conftest" . --include="*.py" --include="*.yml" --include="*.yaml"
# Resultado: Pytest descobre automaticamente (sem imports diretos necessários)
```

**Classes/Funções Definidas:**
```python
- pytest_configure(config)                          # Pytest hook
- pytest_collection_modifyitems(config, items)      # Pytest hook
- check_server_health() -> bool                      # Internal
- server_health() fixture                            # Pytest fixture
```

**Uso de Fixtures:**
```bash
grep -r "server_health" tests/ --include="*.py"
# Resultado: Aparições em code, mas fixture é auto-discovered
```

**VEREDICTO:** ✅ **SEGURO MOVER**
- **Para:** `tests/conftest.py`
- **Razão:** Pytest procura hier automaticamente
- **Condição:** Atualizar imports de plugins com sys.path

---

### ✅ 2. `conftest_server.py` (RAIZ)

**Imports:**
```python
import os                       # stdlib ✅
import time                     # stdlib ✅
import subprocess               # stdlib ✅
import requests                 # external ✅
import pytest                   # external ✅
from typing import Optional     # stdlib ✅
import signal                   # stdlib ✅
```

**Dependências Locais:**
- NENHUMA

**Referências em Workspace:**
```bash
grep -r "conftest_server" . --include="*.py" --include="*.sh"
# Resultado: 0 matches

grep -r "ServerManager" . --include="*.py"
# Resultado: 0 matches (definida aqui, não usada)
```

**Classes Definidas:**
```python
- ServerManager                 # Define aqui, nunca usada
- Fixtures: server_fixture, ensure_server_healthy
```

**VEREDICTO:** 🟢 **COMPLETELY SAFE - ORPHAN FILE**
- **Status:** Não é importado, não é usado
- **Opções:** 
  - ✅ Mover para `tests/fixtures/conftest_server.py`
  - ✅ Deletar se funcionalidade foi integrada em conftest.py
- **Recomendação:** Deletar (código não ativo)

---

### ✅ 3. `pytest_timeout_retry.py` (RAIZ)

**Imports:**
```python
import pytest  # external, installed ✅
```

**Dependências Locais:**
- NENHUMA

**Classe Principal:**
```python
class TimeoutRetryPlugin:
    """Plugin customizado para timeout progressivo"""
    
    Methods:
    - pytest_collection_modifyitems(config, items)   # Hook
    - pytest_runtest_logreport(report)               # Hook
    - _has_ollama_call(item) -> bool                 # Static
```

**Referências em Workspace:**
```bash
grep -r "pytest_timeout_retry" . --include="*.py"
# Resultado:
# conftest.py:26: from pytest_timeout_retry import TimeoutRetryPlugin
# 👆 ÚNICA REFERÊNCIA

grep -r "TimeoutRetryPlugin" . --include="*.py"
# Resultado:
# conftest.py:50: config.pluginmanager.register(TimeoutRetryPlugin(), "timeout_retry")
# 👆 ÚNICA REFERÊNCIA
```

**VEREDICTO:** 🔴 **CRÍTICO - MAS PODE MOVER COM CUIDADO**
- **Status:** Importado APENAS por conftest.py
- **Risco:** Se conftest.py fica na raiz → quebra
- **Solução:** Mover JUNTO com conftest.py
- **Para:** `tests/plugins/pytest_timeout_retry.py`
- **Condição:** Atualizar import em `tests/conftest.py`

---

### ✅ 4. `pytest_server_monitor.py` (RAIZ)

**Imports:**
```python
import subprocess  # stdlib ✅
import requests    # external ✅
import time        # stdlib ✅
import pytest      # external ✅
import os          # stdlib ✅
```

**Classe Principal:**
```python
class ServerMonitorPlugin:
    """Monitor de servidor durante testes"""
    
    Methods:
    - pytest_configure(config)
    - pytest_collection_finish(session)
    - pytest_runtest_setup(item)
    - pytest_runtest_makereport(item, call)
    - pytest_runtest_teardown(item)
    - _is_server_healthy() -> bool
    - _ensure_server_up()
    - _start_server()
    - _wait_for_server_with_retry()
    - pytest_sessionfinish(session, exitstatus)
```

**Referências em Workspace:**
```bash
grep -r "pytest_server_monitor" . --include="*.py"
# Resultado:
# conftest.py:27: from pytest_server_monitor import ServerMonitorPlugin
# 👆 ÚNICA REFERÊNCIA

grep -r "ServerMonitorPlugin" . --include="*.py"
# Resultado:
# conftest.py:51: config.pluginmanager.register(ServerMonitorPlugin(), "server_monitor")
# 👆 ÚNICA REFERÊNCIA
```

**VEREDICTO:** 🔴 **CRÍTICO - MAS PODE MOVER COM CUIDADO**
- **Status:** Importado APENAS por conftest.py
- **Risco:** Mesma situação que pytest_timeout_retry.py
- **Para:** `tests/plugins/pytest_server_monitor.py`
- **Condição:** Mover JUNTO com conftest.py

---

### ✅ 5. `run_tests_gpu.py` (RAIZ)

**Imports:**
```python
import os           # stdlib ✅
import sys          # stdlib ✅
import subprocess   # stdlib ✅
import re           # stdlib ✅
from datetime import datetime  # stdlib ✅
import torch        # optional (try-except used)
```

**Caminhos Relativos Usados:**
```python
"tests/"            # ← Relativo, pode quebrar se executado fora
"data/test_reports/" # ← Relativo, pode quebrar
```

**Referências em Workspace:**
```bash
grep -r "run_tests_gpu" . --include="*.py" --include="*.sh" --include="*.yml"
# Resultado: 0 matches (standalone script)
```

**Funções Principais:**
```python
- log_and_print(msg)
- should_use_gpu(test_path) -> bool
- run_tests(...)
- main()
```

**VEREDICTO:** 🟠 **IMPORTANTE - PODE MOVER COM ADAPTAÇÃO**
- **Status:** Standalone, mas usa paths relativos
- **Risco:** Quebra se executado de outro diretório
- **Para:** `scripts/run_tests_gpu.py`
- **Condição:** Adicionar PROJECT_ROOT detection

**Fix Necessário:**
```python
# Adicionar no início:
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Substituir:
# "tests/" por os.path.join(PROJECT_ROOT, "tests")
# "data/test_reports/" por os.path.join(PROJECT_ROOT, "data/test_reports")
```

---

### ✅ 6. `run_consciousness_tests_gpu.sh` (RAIZ)

**Caminhos Absolutos:**
```bash
cd /home/fahbrain/projects/omnimind  # ← HARDCODED 🚨
```

**Caminhos Relativos:**
```bash
data/test_reports
tests/consciousness/
scripts/monitor_gpu_tests.py
scripts/phi_metrics_collector.py
```

**Referências em Workspace:**
```bash
grep -r "run_consciousness_tests_gpu" . --include="*.sh" --include="*.py" --include="*.yml"
# Resultado: 0 matches (standalone script)
```

**VEREDICTO:** 🟠 **IMPORTANTE - PODE MOVER COM REMOÇÃO DE HARDCODING**
- **Para:** `scripts/run_consciousness_tests_gpu.sh`
- **Condição:** Remover path absoluto

**Fix Necessário:**
```bash
# Substituir:
cd /home/fahbrain/projects/omnimind

# Por:
cd "$(dirname "$0")/.."  # ← Relativo ao script
```

---

### ✅ 7. `run_tests_with_server.sh` (RAIZ)

**Caminhos Absolutos:**
```bash
cd /home/fahbrain/projects/omnimind       # ← HARDCODED 🚨
/home/fahbrain/projects/omnimind/deploy   # ← HARDCODED 🚨
```

**Referências em Workspace:**
```bash
grep -r "run_tests_with_server" . --include="*.sh" --include="*.yml"
# Resultado: 0 matches
```

**VEREDICTO:** 🟠 **IMPORTANTE - MESMA SITUAÇÃO**
- **Para:** `scripts/run_tests_with_server.sh`
- **Condição:** Remover AMBOS os hardcodes

---

### ✅ 8. `monitor_suite.sh` (RAIZ)

**Valores Hardcoded:**
```bash
LOGFILE="data/test_reports/full_suite_20251201_094631.log"  # ← DATA ESPECÍFICA
PID=86970                                                     # ← PID ESPECÍFICO
```

**Referências em Workspace:**
```bash
grep -r "monitor_suite" . --include="*.sh" --include="*.yml"
# Resultado: 0 matches
```

**VEREDICTO:** 🟡 **MODERADO - PODE MOVER COM PARAMETRIZAÇÃO**
- **Para:** `scripts/monitor_suite.sh`
- **Condição:** Tornar parametrizável (receber como argumentos)

**Fix Necessário:**
```bash
# Adicionar parâmetros:
LOGFILE="${1:?Usage: $0 <logfile> <pid>}"
PID="${2:?Usage: $0 <logfile> <pid>}"
```

---

### ✅ 9-12. Testes Demo (4 arquivos)

#### `test_affective_extension.py`
```bash
grep -r "test_affective_extension" . --include="*.py"
# Resultado: 0 matches ✅

grep -r "affective_extension" . --include="*.py"
# Resultado: Match apenas no arquivo mesmo (imports internos)
```

**VEREDICTO:** 🟢 **COMPLETAMENTE SEGURO**
- **Status:** Não é importado em lugar nenhum
- **Uso:** Execução direta: `python test_affective_extension.py`
- **Para:** `scripts/demos/test_affective_extension.py`

#### Mesmo para: `test_affective_simple.py`, `test_rsi_simple.py`, `test_symbolic_register.py`

---

### ✅ 13-14. Scripts Demos (2 arquivos)

#### `lacanian_vs_cognitive_demo.py`
```bash
grep -r "lacanian_vs_cognitive" . --include="*.py"
# Resultado: 0 matches ✅
```

**VEREDICTO:** 🟢 **COMPLETAMENTE SEGURO**
- **Para:** `scripts/demos/lacanian_vs_cognitive_demo.py`

#### Mesmo para: `affective_extension_results.py`

---

### ✅ 15-19. Arquivos de Dados (5 arquivos)

#### `ablations_corrected_latest.json`
```bash
grep -r "ablations_corrected_latest" . --include="*.py" --include="*.sh"
# Resultado: 0 matches ✅
```

**VEREDICTO:** 🟢 **COMPLETAMENTE SEGURO**
- **Tipo:** Output (não input)
- **Para:** `data/results/ablations_corrected_latest.json`

#### Mesmo para: `integrated_suite_results.json`, `test_final.json`, `pytest_dryrun.log`, `sha256_original.log`

---

## 📊 RESUMO FINAL COM VERIFICAÇÃO

| # | Arquivo | Tipo | Imports Locais | Referências | Hardcoding | **RISCO** | **SEGURO?** | Novo Caminho |
|---|---------|------|---|---|---|---|---|---|
| 1 | `conftest.py` | Config | pytest_timeout_retry, pytest_server_monitor | 0 (auto-descoberto) | Não | 🟠 MÉD | ✅ SIM | `tests/conftest.py` |
| 2 | `conftest_server.py` | Config | Nenhum local | 0 | Não | 🟢 BAIXO | ✅ SIM | Deletar |
| 3 | `pytest_timeout_retry.py` | Plugin | Nenhum | conftest.py | Não | 🔴 ALTO | ✅ SIM* | `tests/plugins/` |
| 4 | `pytest_server_monitor.py` | Plugin | Nenhum | conftest.py | Não | 🔴 ALTO | ✅ SIM* | `tests/plugins/` |
| 5 | `run_tests_gpu.py` | Runner | Nenhum local | 0 | Não | 🟠 MÉD | ✅ SIM | `scripts/` |
| 6 | `run_consciousness_tests_gpu.sh` | Shell | N/A | 0 | ✅ 1 path | 🟠 MÉD | ✅ SIM | `scripts/` |
| 7 | `run_tests_with_server.sh` | Shell | N/A | 0 | ✅ 2 paths | 🟠 MÉD | ✅ SIM | `scripts/` |
| 8 | `monitor_suite.sh` | Shell | N/A | 0 | ✅ PID/LOG | 🟡 BAIXO | ✅ SIM | `scripts/` |
| 9 | `test_affective_extension.py` | Demo | Nenhum local | 0 | Não | 🟢 NENHUM | ✅ SIM | `scripts/demos/` |
| 10 | `test_affective_simple.py` | Demo | Nenhum local | 0 | Não | 🟢 NENHUM | ✅ SIM | `scripts/demos/` |
| 11 | `test_rsi_simple.py` | Demo | Nenhum local | 0 | Não | 🟢 NENHUM | ✅ SIM | `scripts/demos/` |
| 12 | `test_symbolic_register.py` | Demo | Nenhum local | 0 | Não | 🟢 NENHUM | ✅ SIM | `scripts/demos/` |
| 13 | `lacanian_vs_cognitive_demo.py` | Demo | Nenhum local | 0 | Não | 🟢 NENHUM | ✅ SIM | `scripts/demos/` |
| 14 | `affective_extension_results.py` | Demo | Nenhum local | 0 | Não | 🟢 NENHUM | ✅ SIM | `scripts/demos/` |
| 15 | `ablations_corrected_latest.json` | Data | N/A | 0 | Não | 🟢 NENHUM | ✅ SIM | `data/results/` |
| 16 | `integrated_suite_results.json` | Data | N/A | 0 | Não | 🟢 NENHUM | ✅ SIM | `data/results/` |
| 17 | `test_final.json` | Data | N/A | 0 | Não | 🟢 NENHUM | ✅ SIM | `data/results/` |
| 18 | `pytest_dryrun.log` | Log | N/A | 0 | Não | 🟢 NENHUM | ✅ SIM | `data/test_reports/` |
| 19 | `sha256_original.log` | Audit | N/A | 0 | Não | 🟢 NENHUM | ✅ SIM | `data/audit/` |

**CONCLUSÃO GERAL:**
- ✅ **TODOS OS 19 ARQUIVOS PODEM SER MOVIDOS COM SEGURANÇA**
- ⚠️ **CRÍTICO:** Plugins precisam ser movidos com conftest.py
- ⚠️ **IMPORTANTE:** Shell scripts precisam remover hardcoding
- ✅ **11 ARQUIVOS:** Sem risco algum

*= Condição: Mover com conftest.py e atualizar sys.path

---

## ✅ CHECKLIST FINAL

- [x] Todos os imports verificados
- [x] Todas as referências rastreadas com grep
- [x] Todos os hardcodings identificados
- [x] Nenhuma dependência circular encontrada
- [x] Nenhum arquivo órfão para manter na raiz
- [x] Segurança confirmada para todos os 19 arquivos
- [x] Caminhos de novo local definidos
- [x] Condições de movimento documentadas

**PRONTO PARA MOVIMENTO! Confirme com o usuário antes de executar.**
