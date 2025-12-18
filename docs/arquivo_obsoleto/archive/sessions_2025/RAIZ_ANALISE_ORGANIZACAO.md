# 📋 ANÁLISE COMPLETA DE ARQUIVOS NA RAIZ - Organização e Segurança

**Data:** 2 de dezembro de 2025  
**Status:** PRONTO PARA REORGANIZAÇÃO COM SEGURANÇA  
**Análise:** Arquivo por arquivo, com verificação explícita de dependências

---

## 📊 SUMÁRIO EXECUTIVO

| Categoria | Arquivos | Estado | Risco de Movimento |
|-----------|----------|--------|-------------------|
| **Pytest Config** | 2 | CRÍTICOS | 🔴 MUITO ALTO |
| **Plugins Pytest** | 2 | CRÍTICOS | 🔴 MUITO ALTO |
| **Runners de Teste** | 1 | IMPORTANTE | 🟠 MÉDIO |
| **Scripts Shell** | 3 | IMPORTANTE | 🟠 MÉDIO |
| **Testes Demonstrativos** | 4 | OPCIONAL | 🟢 BAIXO |
| **Scripts Demonstrativos** | 2 | OPCIONAL | 🟢 BAIXO |
| **Dados Resultados** | 5 | SUPORTE | 🟡 BAIXO |

**Total Arquivos Analisados:** 19 arquivos principais

---

## 🔴 CATEGORIA 1: PYTEST CONFIG (CRÍTICOS - NÃO MOVER)

### 1. `conftest.py` (RAIZ)
- **Linhas:** 135 linhas
- **Criação:** Sessão anterior
- **Propósito:** Configuração GLOBAL de pytest para TODA suite
- **Importâncias:**
  ```python
  from pytest_timeout_retry import TimeoutRetryPlugin
  from pytest_server_monitor import ServerMonitorPlugin
  ```

**Análise de Dependências:**
```
conftest.py (RAIZ)
├── Importa: pytest_timeout_retry.TimeoutRetryPlugin ✅ (arquivo na raiz)
├── Importa: pytest_server_monitor.ServerMonitorPlugin ✅ (arquivo na raiz)
├── Define: pytest_configure() - registra MARKERS globais
│   ├── @computational, @gpu, @quantum, @consciousness, @e2e, @real
│   └── Todos usados em: tests/**/*.py (implícito via markers)
├── Define: pytest_collection_modifyitems() - AUTO-MARCA TESTES
│   └── Mapeia caminhos de teste → timeouts progressivos
│       ├── "test_integration_loss.py" → 600s
│       ├── "consciousness" → 300s
│       ├── "test_e2e_integration" → 400s
│       └── Padrões usados em: tests/**/*.py (pathnames)
└── Fixture: server_health() - verifica API health
    └── Usado por: Qualquer teste com marker @e2e
```

**⚠️ RISCO: CRÍTICO**
- **POR QUÊ:** pytest procura `conftest.py` automaticamente na RAIZ
- **Se mover para `tests/conftest.py`:**
  - ✅ SIM é possível (pytest recursa até achar)
  - ⚠️ MAS: Fixtures e markers podem não ativarem para testes na raiz
  - ❌ Qualquer teste manual fora de `tests/` perde config

**DECISÃO RECOMENDADA:** ✅ **PODE MOVER para `tests/conftest.py`**
- **Condição:** Se TODOS os testes estão em `tests/`
- **Verificar:** Há testes executáveis na raiz? (ver abaixo)

---

### 2. `conftest_server.py` (RAIZ)
- **Linhas:** 155 linhas  
- **Criação:** Sessão anterior
- **Propósito:** Gerenciador de servidor para testes E2E
- **Diferença:** NÃO é usado automaticamente por pytest

**Análise de Dependências:**
```
conftest_server.py
├── Define: ServerManager class
├── Define: Fixtures
│   ├── server_fixture() - @pytest.fixture(scope="session", autouse=True)
│   └── ensure_server_healthy() - @pytest.fixture(autouse=True)
└── Uso: NINGUÉM IMPORTA ESTE ARQUIVO

Buscas no workspace:
├── grep "from conftest_server" → 0 matches ✅
├── grep "import conftest_server" → 0 matches ✅
└── pytest descobre automaticamente? NÃO (não está em conftest.py)
```

**⚠️ RISCO: NENHUM**
- **POR QUÊ:** Não é importado, não é usado
- **Status:** Arquivo ÓRFÃO - provavelmente código anterior não ativado

**DECISÃO RECOMENDADA:** ✅ **PODE MOVER para `tests/fixtures/conftest_server.py`**
- **Alternativa:** Deletar se não está sendo usado
- **Nota:** Verificar se funcionalidade foi integrada em `conftest.py`

---

## 🔴 CATEGORIA 2: PLUGINS PYTEST (CRÍTICOS - NÃO MOVER)

### 3. `pytest_timeout_retry.py` (RAIZ)
- **Linhas:** 71 linhas
- **Criação:** Sessão anterior
- **Propósito:** Plugin customizado pytest para timeout progressivo

**Análise de Dependências:**
```
pytest_timeout_retry.py
├── Define: class TimeoutRetryPlugin
└── Uso em: conftest.py linha 26
    └── config.pluginmanager.register(TimeoutRetryPlugin(), "timeout_retry")

Fluxo de Execução:
1. pytest carrega conftest.py (raiz)
2. conftest.py linha 26: from pytest_timeout_retry import TimeoutRetryPlugin
3. conftest.py linha 26 registra o plugin
4. pytest executa métodos do plugin durante teste:
   ├── pytest_collection_modifyitems() 
   ├── pytest_runtest_logreport()
   └── _has_ollama_call()
```

**🔴 RISCO: CRÍTICO - PATH ABSOLUTO**
- **POR QUÊ:** conftest.py faz `from pytest_timeout_retry import ...`
- **Se mover para `tests/pytest_timeout_retry.py`:**
  - ❌ FALHA: conftest.py não encontra mais o módulo
  - ❌ Error: `ModuleNotFoundError: No module named 'pytest_timeout_retry'`
- **Se mover para `src/pytest_timeout_retry.py`:**
  - ⚠️ FUNCIONA: se sys.path incluir src (que inclui)
  - 📝 MAS: Mistura código de produção com plugins de teste

**DECISÃO RECOMENDADA:** ✅ **PODE MOVER para `tests/plugins/pytest_timeout_retry.py`**
- **Condição 1:** Atualizar import em conftest.py:
  ```python
  # Antes:
  from pytest_timeout_retry import TimeoutRetryPlugin
  
  # Depois:
  import sys
  sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'plugins'))
  from pytest_timeout_retry import TimeoutRetryPlugin
  ```
- **Condição 2:** Mover conftest.py para raiz `tests/conftest.py`

---

### 4. `pytest_server_monitor.py` (RAIZ)
- **Linhas:** 169 linhas
- **Criação:** Sessão anterior
- **Propósito:** Plugin customizado pytest para monitorar servidor

**Análise de Dependências:**
```
pytest_server_monitor.py
├── Define: class ServerMonitorPlugin
└── Uso em: conftest.py linha 27
    └── config.pluginmanager.register(ServerMonitorPlugin(), "server_monitor")

Fluxo:
1. conftest.py linha 27: from pytest_server_monitor import ServerMonitorPlugin
2. Registra o plugin
3. Plugin monitora durante testes E2E:
   ├── pytest_configure()
   ├── pytest_collection_finish() - inicia servidor
   ├── pytest_runtest_setup()
   ├── pytest_runtest_makereport()
   └── pytest_runtest_teardown()
```

**🔴 RISCO: CRÍTICO - PATH ABSOLUTO**
- **Mesma situação do pytest_timeout_retry.py**
- **Se mover sem atualizar conftest.py:** ❌ FALHA

**DECISÃO RECOMENDADA:** ✅ **PODE MOVER para `tests/plugins/pytest_server_monitor.py`**
- **Mesma condição:** Atualizar imports em conftest.py

---

## 🟠 CATEGORIA 3: RUNNERS DE TESTE (IMPORTANTES - CUIDADO)

### 5. `run_tests_gpu.py` (RAIZ)
- **Linhas:** 185 linhas
- **Criação:** Sessão anterior
- **Propósito:** Runner inteligente com detecção GPU dinâmica

**Análise de Dependências:**
```
run_tests_gpu.py
├── Função: should_use_gpu(test_path: str) → bool
├── Função: log_and_print(msg: str)
├── Executa: subprocess.run(['python', '-m', 'pytest', ...])
└── Referências de Caminhos:
    ├── "tests/" (caminho relativo)
    ├── LOG_FILE = "data/test_reports/..." (caminho relativo)
    └── Uso: Executado manualmente: python run_tests_gpu.py

Buscas no workspace:
├── grep "run_tests_gpu" → 0 matches na source
├── Usado em: run_consciousness_tests_gpu.sh? → NÃO
└── Script é INDEPENDENTE
```

**🟡 RISCO: BAIXO (caminhos relativos funcionam)**
- **POR QUÊ:** Usa caminhos relativos, não imports
- **Se mover para `scripts/run_tests_gpu.py`:**
  - ⚠️ CUIDADO: Caminhos tipo `tests/` podem quebrar se executado de fora
  - ✅ SOLUÇÃO: Usar `os.path.join(PROJECT_ROOT, 'tests')`

**DECISÃO RECOMENDADA:** ✅ **PODE MOVER para `scripts/run_tests_gpu.py`**
- **Condição:** Atualizar caminhos para caminhos absolutos baseados em PROJECT_ROOT

---

## 🟠 CATEGORIA 4: SCRIPTS SHELL (IMPORTANTES - CUIDADO)

### 6. `run_consciousness_tests_gpu.sh` (RAIZ)
- **Tamanho:** 181 linhas
- **Criação:** Sessão anterior
- **Propósito:** Script principal de testes GPU com monitoramento

**Análise de Dependências:**
```
run_consciousness_tests_gpu.sh
├── Variáveis de Ambiente:
│   ├── CUDA_VISIBLE_DEVICES=0
│   ├── TORCH_HOME=/home/fahbrain/.cache/torch
│   └── PYTHONUNBUFFERED=1
├── Executa:
│   ├── cd /home/fahbrain/projects/omnimind (CAMINHO ABSOLUTO)
│   ├── mkdir -p data/test_reports (relativo)
│   ├── python3 scripts/monitor_gpu_tests.py (CAMINHO RELATIVO)
│   ├── pytest tests/consciousness/ (CAMINHO RELATIVO)
│   └── python scripts/phi_metrics_collector.py (CAMINHO RELATIVO)
└── Dependências de Arquivos:
    ├── scripts/monitor_gpu_tests.py ✅ (existe)
    ├── scripts/phi_metrics_collector.py ✅ (existe)
    └── tests/consciousness/ ✅ (existe)

Buscas no workspace:
├── grep "run_consciousness_tests_gpu.sh" → 0 matches
├── grep "run_consciousness_tests_gpu" → 0 matches
├── Usado por: Execução manual ou CI/CD
└── Status: Independente
```

**🟠 RISCO: MÉDIO (caminhos mistos)**
- **POR QUÊ:** Mix de caminhos absolutos e relativos
- **Crítico:** cd /home/fahbrain... é HARDCODED (não portável)
- **Se mover para `scripts/`:**
  - ✅ Funciona se executado de `omnimind/` (cd omnimind && bash scripts/run_consciousness_tests_gpu.sh)
  - ⚠️ MAS: path absoluto `cd /home/fahbrain...` deve ser relativo

**DECISÃO RECOMENDADA:** ✅ **PODE MOVER para `scripts/run_consciousness_tests_gpu.sh`**
- **Condição 1:** Remover path absoluto `cd /home/fahbrain/...`
- **Condição 2:** Começar com: `cd "$(dirname "$0")/.."` (vai para raiz omnimind)
- **Benefício:** Portável entre máquinas

---

### 7. `run_tests_with_server.sh` (RAIZ)
- **Tamanho:** 110 linhas
- **Criação:** Sessão anterior
- **Propósito:** Runner de testes com auto-restart servidor

**Análise de Dependências:**
```
run_tests_with_server.sh
├── Caminhos Absolutos:
│   ├── cd /home/fahbrain/projects/omnimind (HARDCODED)
│   └── /home/fahbrain/projects/omnimind/deploy (HARDCODED)
├── Caminhos Relativos:
│   ├── data/test_reports
│   ├── tests/
│   └── docker-compose (em deploy/)
└── Referências Externas:
    ├── curl http://localhost:8000/health/ (servidor)
    └── docker-compose (ferramenta)

Status: Mesmo problema - caminhos hardcoded
```

**🟠 RISCO: MÉDIO (caminhos absolutos)**

**DECISÃO RECOMENDADA:** ✅ **PODE MOVER para `scripts/run_tests_with_server.sh`**
- **Mesma condição:** Remover hardcoding de caminhos

---

### 8. `monitor_suite.sh` (RAIZ)
- **Tamanho:** 45 linhas
- **Criação:** Sessão anterior
- **Propósito:** Monitor de progresso durante execução de suite

**Análise de Dependências:**
```
monitor_suite.sh
├── Hardcoded:
│   ├── LOGFILE="data/test_reports/full_suite_20251201_094631.log"
│   └── PID=86970
├── Comandos:
│   ├── wc, grep, ps, awk
│   └── Nenhuma dependência interna
└── Status: Completamente Standalone, mas com valores hardcoded
```

**🟢 RISCO: BAIXO (mas hardcoded)**

**DECISÃO RECOMENDADA:** ✅ **PODE MOVER para `scripts/monitor_suite.sh`**
- **Condição:** Tornar parametrizável (receber PID e LOGFILE como argumentos)

---

## 🟢 CATEGORIA 5: TESTES DEMONSTRATIVOS (OPCIONAIS - MOVER)

### 9-12. Testes Demonstrativos (4 arquivos)

#### `test_affective_extension.py` (RAIZ)
- **Linhas:** 192 linhas
- **Propósito:** Teste demo da extensão lacaniana (afetiva)
- **Tipo:** Demo/Experimental (NÃO pytest automático - sem @pytest.mark)

```python
if __name__ == "__main__":  # ← Executável direto
    test_behaviorist_model()
    test_lacanian_model()
```

**Análise:**
```
test_affective_extension.py
├── Imports:
│   ├── sys.path.insert(0, 'src') ✅
│   ├── from consciousness.emotional_intelligence import EmotionalIntelligence
│   └── import structlog
├── Pode executar: python test_affective_extension.py
├── Pytest encontraria? SIM (nome começa com test_)
├── MAS: Sem fixtures pytest, não é teste formalmente
└── Status: Demo standalone

Buscas:
├── grep "test_affective_extension" → 0 matches (não importado)
├── grep "affective_extension" → 0 matches
└── Referências: NENHUMA
```

**🟢 RISCO: NENHUM**

**DECISÃO RECOMENDADA:** ✅ **MOVER para `notebooks/` ou `scripts/demos/`**
- **Tipo:** Demo/Prototipagem
- **Razão:** Não é teste formal, é exploração
- **Novo Caminho:** `scripts/demos/test_affective_extension.py`

---

#### `test_affective_simple.py` (RAIZ)
- **Linhas:** 94 linhas
- **Propósito:** Teste simples das classes lacanianas

**Status:** Mesma situação que `test_affective_extension.py`

**DECISÃO RECOMENDADA:** ✅ **MOVER para `scripts/demos/test_affective_simple.py`**

---

#### `test_rsi_simple.py` (RAIZ)
- **Linhas:** 65 linhas
- **Propósito:** Teste simples da topologia RSI

**Status:** Mesma situação (demo)

**DECISÃO RECOMENDADA:** ✅ **MOVER para `scripts/demos/test_rsi_simple.py`**

---

#### `test_symbolic_register.py` (RAIZ)
- **Linhas:** 85 linhas
- **Propósito:** Teste básico do Shared Symbolic Register

**Status:** Mesma situação (demo)

**DECISÃO RECOMENDADA:** ✅ **MOVER para `scripts/demos/test_symbolic_register.py`**

---

## 🟢 CATEGORIA 6: SCRIPTS DEMONSTRATIVOS (OPCIONAIS - MOVER)

### 13-14. Scripts Demonstrativos (2 arquivos)

#### `lacanian_vs_cognitive_demo.py` (RAIZ)
- **Linhas:** 71 linhas
- **Propósito:** Demo comparativa de Theory of Mind

```python
if __name__ == "__main__":
    demonstrate_cognitive_vs_lacanian()
```

**Análise:**
```
lacanian_vs_cognitive_demo.py
├── Imports:
│   ├── from src.consciousness.theory_of_mind import TheoryOfMind, LacanianTheoryOfMind
│   └── Nenhuma dependência de pytest
├── Tipo: Demo/Exemplo educativo
├── Pytest o encontraria? Não (if __name__ garante)
└── Referências: NENHUMA

Uso:
└── python lacanian_vs_cognitive_demo.py (execução direta)
```

**🟢 RISCO: NENHUM**

**DECISÃO RECOMENDADA:** ✅ **MOVER para `scripts/demos/lacanian_vs_cognitive_demo.py`**
- **Tipo:** Demo/Educativo
- **Razão:** Clareza de propósito

---

#### `affective_extension_results.py` (RAIZ)
- **Linhas:** 67 linhas
- **Propósito:** Resultado/Documentação da extensão lacaniana

**Status:** Mesma situação (demo/documentação)

**DECISÃO RECOMENDADA:** ✅ **MOVER para `scripts/demos/affective_extension_results.py`**

---

## 🟡 CATEGORIA 7: DADOS E RESULTADOS (SUPORTE - NÃO MOVER)

### 15-19. Arquivos de Dados (5 arquivos)

#### `ablations_corrected_latest.json` (RAIZ)
- **Tamanho:** 4.5K
- **Propósito:** Dados de ablations (experimentos corrigidos)
- **Tipo:** OUTPUT de testes anteriores

**Análise:**
```
Referências em código:
├── grep "ablations_corrected_latest.json" → 0 matches
├── Arquivo gerado por: run_consciousness_tests_gpu.sh (provavelmente)
└── Usado por: Análise manual / Comparações
```

**DECISÃO RECOMENDADA:** ✅ **MOVER para `data/results/ablations_corrected_latest.json`**
- **Tipo:** Dados de saída de testes
- **Razão:** Organização (`data/` é para dados)

---

#### `integrated_suite_results.json` (RAIZ)
- **Tamanho:** 19K
- **Propósito:** Resultados da suite integrada

**DECISÃO RECOMENDADA:** ✅ **MOVER para `data/results/integrated_suite_results.json`**

---

#### `test_final.json` (RAIZ)
- **Tamanho:** 1.1K
- **Propósito:** Resultado final de testes

**DECISÃO RECOMENDADA:** ✅ **MOVER para `data/results/test_final.json`**

---

#### `pytest_dryrun.log` (RAIZ)
- **Tamanho:** 227K
- **Propósito:** Log da execução de dry-run do pytest

**DECISÃO RECOMENDADA:** ✅ **MOVER para `data/test_reports/pytest_dryrun.log`**

---

#### `sha256_original.log` (RAIZ)
- **Tamanho:** 4.1M
- **Propósito:** Assinatura SHA256 original (auditoria)

**DECISÃO RECOMENDADA:** ✅ **MOVER para `data/audit/sha256_original.log`**

---

## 📋 PLANO DE REORGANIZAÇÃO (PASSO A PASSO)

### FASE 1: ANÁLISE E BACKUP (Risco: NENHUM)

```bash
# 1. Criar backup completo
cd /home/fahbrain/projects/omnimind
git add -A
git commit -m "Backup: Estado anterior à reorganização de raiz"

# 2. Criar branches de organização
git checkout -b refactor/organize-root-files
```

---

### FASE 2: MOVER TESTES DEMO (Risco: BAIXO)

```bash
# Criar diretório
mkdir -p scripts/demos

# Mover demos (seguros - ninguém referencia)
mv test_affective_extension.py scripts/demos/
mv test_affective_simple.py scripts/demos/
mv test_rsi_simple.py scripts/demos/
mv test_symbolic_register.py scripts/demos/
mv lacanian_vs_cognitive_demo.py scripts/demos/
mv affective_extension_results.py scripts/demos/

git add -A
git commit -m "Refactor: Move demos para scripts/demos"
```

---

### FASE 3: ORGANIZAR DADOS (Risco: NENHUM)

```bash
# Criar diretórios
mkdir -p data/results
mkdir -p data/audit

# Mover dados
mv ablations_corrected_latest.json data/results/
mv integrated_suite_results.json data/results/
mv test_final.json data/results/
mv pytest_dryrun.log data/test_reports/
mv sha256_original.log data/audit/

git add -A
git commit -m "Refactor: Organize data files into data/ subdirs"
```

---

### FASE 4: MOVER SCRIPTS SHELL (Risco: BAIXO)

```bash
# Criar diretório se não existir
mkdir -p scripts

# Editar scripts para remover hardcoding:

# 4.1. run_consciousness_tests_gpu.sh
# Substituir: cd /home/fahbrain/projects/omnimind
# Por: cd "$(dirname "$0")/.."
sed -i 's|cd /home/fahbrain/projects/omnimind|cd "$(dirname "$0")/.." |g' run_consciousness_tests_gpu.sh

# Mover
mv run_consciousness_tests_gpu.sh scripts/

# 4.2. run_tests_with_server.sh (mesma edição)
sed -i 's|cd /home/fahbrain/projects/omnimind|cd "$(dirname "$0")/.." |g' run_tests_with_server.sh
sed -i 's|/home/fahbrain/projects/omnimind/deploy|../../deploy|g' run_tests_with_server.sh
mv run_tests_with_server.sh scripts/

# 4.3. monitor_suite.sh (adicionar parâmetros)
# Fazer manualmente (ver abaixo)
mv monitor_suite.sh scripts/

git add -A
git commit -m "Refactor: Move shell scripts to scripts/ with portable paths"
```

---

### FASE 5: REORGANIZAR PYTEST CONFIG (Risco: ALTO - REVERTER SE FALHAR)

```bash
# 5.1. Criar estrutura
mkdir -p tests/plugins

# 5.2. Mover plugins
cp pytest_timeout_retry.py tests/plugins/
cp pytest_server_monitor.py tests/plugins/

# 5.3. Criar conftest.py em tests/
# (com imports atualizados - ver abaixo)

# 5.4. Mover conftest.py para tests/
mv conftest.py tests/

# 5.5. REMOVER conftest_server.py (órfão, não usado)
rm conftest_server.py

# 5.6. Testar (CRÍTICO)
cd /home/fahbrain/projects/omnimind
python -m pytest tests/ -v --collect-only

# Se falhar: git restore tests/conftest.py
# Se OK: continuar

# 5.7. Cleanup na raiz
rm pytest_timeout_retry.py pytest_server_monitor.py

git add -A
git commit -m "Refactor: Move pytest config and plugins to tests/"
```

---

### FASE 6: MOVER RUNNER PYTHON (Risco: MÉDIO)

```bash
# Editar run_tests_gpu.py para usar PROJECT_ROOT
# Ver script abaixo

# Mover
mv run_tests_gpu.py scripts/
mv run_tests_gpu.py scripts/run_tests_gpu.py

git add -A
git commit -m "Refactor: Move run_tests_gpu to scripts/ with absolute paths"
```

---

### FASE 7: ATUALIZAR REFERÊNCIAS (Risco: MÉDIO)

```bash
# Verificar se há scripts ou CI/CD que referenciam os arquivos movidos
grep -r "run_consciousness_tests_gpu.sh" . --include="*.md" --include="*.yml" --include="*.yaml"
grep -r "run_tests_gpu.py" . --include="*.md" --include="*.yml" --include="*.yaml"

# Atualizar descobertas conforme necessário
# Exemplo: .github/workflows/*.yml, README.md, etc.
```

---

### FASE 8: VALIDAÇÃO FINAL (Risco: NENHUM)

```bash
# Executar suite completa para validar
python -m pytest tests/consciousness/ -v --tb=short

# Se OK: merge branch
git checkout main
git merge refactor/organize-root-files

# Se não OK: git revert
```

---

## 📝 SCRIPTS DE ATUALIZAÇÃO

### Script 1: Atualizar `tests/conftest.py` (novo)

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

# Importar plugins customizados
plugin_path = os.path.join(os.path.dirname(__file__), 'plugins')
if plugin_path not in sys.path:
    sys.path.insert(0, plugin_path)

from pytest_timeout_retry import TimeoutRetryPlugin
from pytest_server_monitor import ServerMonitorPlugin

# [RESTO DO ARQUIVO IGUAL AO ORIGINAL conftest.py]
```

---

### Script 2: Atualizar `run_consciousness_tests_gpu.sh`

```bash
#!/bin/bash
# Testes de Consciência com GPU obrigatória

set -e

# Obter diretório do script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

# [RESTO DO ARQUIVO, MAS COM PATHS RELATIVOS]
```

---

### Script 3: Atualizar `run_tests_gpu.py`

```python
#!/usr/bin/env python3
import os

# Detectar PROJECT_ROOT
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Usar em caminhos
LOG_DIR = os.path.join(PROJECT_ROOT, "data", "test_reports")
TEST_DIR = os.path.join(PROJECT_ROOT, "tests")

# [RESTO DO ARQUIVO]
```

---

### Script 4: Tornar `monitor_suite.sh` parametrizável

```bash
#!/bin/bash
# Monitorar conclusão de suite com PID e LOG parametrizáveis

# Parâmetros
LOGFILE="${1:?Usar: monitor_suite.sh <logfile> <pid>}"
PID="${2:?Usar: monitor_suite.sh <logfile> <pid>}"

# [RESTO DO ARQUIVO]
```

---

## ✅ CHECKLIST PRÉ-REORGANIZAÇÃO

- [ ] Fazer commit inicial de backup
- [ ] Testar suite completa ANTES de mover
- [ ] Criar branch `refactor/organize-root-files`
- [ ] Mover demos (baixo risco)
- [ ] Validar: `pytest tests/ --collect-only` OK?
- [ ] Mover dados
- [ ] Validar: Arquivos de dados ainda acessíveis
- [ ] Mover scripts shell (com paths revisados)
- [ ] Validar: Scripts shell executáveis
- [ ] Mover pytest config (REVERTER se falhar)
- [ ] Validar: `pytest tests/ -v` OK?
- [ ] Mover runner python
- [ ] Atualizar documentação (README, etc)
- [ ] Executar suite completa: `pytest tests/` 
- [ ] Merge branch se tudo OK

---

## 🚨 ROLLBACK (SE NECESSÁRIO)

Se algo quebrar:

```bash
# Volta ao último commit
git reset --hard HEAD~1

# Ou volta branch inteira
git checkout main
git branch -D refactor/organize-root-files
```

---

## 📊 RESULTADO ESPERADO

**ANTES:**
```
omnimind/
├── conftest.py
├── conftest_server.py
├── pytest_timeout_retry.py
├── pytest_server_monitor.py
├── run_tests_gpu.py
├── run_consciousness_tests_gpu.sh
├── run_tests_with_server.sh
├── monitor_suite.sh
├── test_affective_extension.py
├── test_affective_simple.py
├── test_rsi_simple.py
├── test_symbolic_register.py
├── lacanian_vs_cognitive_demo.py
├── affective_extension_results.py
├── ablations_corrected_latest.json
├── integrated_suite_results.json
├── test_final.json
├── pytest_dryrun.log
└── sha256_original.log
```

**DEPOIS:**
```
omnimind/
├── tests/
│   ├── conftest.py ✅ (movido)
│   ├── plugins/
│   │   ├── pytest_timeout_retry.py ✅
│   │   └── pytest_server_monitor.py ✅
│   └── [testes existentes]
├── scripts/
│   ├── run_consciousness_tests_gpu.sh ✅
│   ├── run_tests_with_server.sh ✅
│   ├── run_tests_gpu.py ✅
│   ├── monitor_suite.sh ✅
│   ├── [scripts existentes]
│   └── demos/ ✅
│       ├── test_affective_extension.py
│       ├── test_affective_simple.py
│       ├── test_rsi_simple.py
│       ├── test_symbolic_register.py
│       ├── lacanian_vs_cognitive_demo.py
│       └── affective_extension_results.py
├── data/
│   ├── results/ ✅
│   │   ├── ablations_corrected_latest.json
│   │   ├── integrated_suite_results.json
│   │   └── test_final.json
│   ├── audit/ ✅
│   │   └── sha256_original.log
│   ├── test_reports/ ✅
│   │   └── pytest_dryrun.log
│   └── [dados existentes]
└── [resto da estrutura]
```

**RAIZ LIMPA:** 19 arquivos → 0 arquivos (todos organizados)

---

## 📈 BENEFÍCIOS

1. **Clareza:** Cada tipo de arquivo tem seu lugar
2. **Portabilidade:** Scripts com caminhos relativos funcionam em qualquer máquina
3. **Manutenibilidade:** Fácil encontrar e atualizar
4. **Segurança:** Sem risco de quebrar conf global (testes isolados)
5. **CI/CD:** Integração mais fácil

---

**Próximos Passos:** Confirmar com você qual abordagem deseja seguir antes de fazer qualquer movimento!
