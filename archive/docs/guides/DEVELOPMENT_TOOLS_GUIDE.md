# OmniMind Development Tools & Automation

**Última Atualização**: 5 de Dezembro de 2025
**Versão**: Phase 24+ (Lacanian Memory + Autopoietic Evolution)
**Autor**: Fabrício da Silva + assistência de IA (Copilot GitHub/Cursor/Gemini/Perplexity)

---

Guia completo das ferramentas de desenvolvimento e automação do OmniMind.

## Table of Contents

1. [One-Click Installation](#one-click-installation)
2. [Environment Auto-Detection](#environment-auto-detection)
3. [Dependency Management](#dependency-management)
4. [Configuration Validation](#configuration-validation)
5. [Code Generation Tools](#code-generation-tools)
6. [Automated Code Review](#automated-code-review)
7. [Performance Benchmarking](#performance-benchmarking)

---

## One-Click Installation

### Overview
Fully automated installation script that sets up OmniMind with a single command.

### Features
- **OS Detection**: Automatic detection of Linux distribution (Ubuntu, Fedora, Arch, etc.)
- **Package Manager**: Auto-detection and use of system package manager (apt, dnf, yum, pacman)
- **Python Setup**: Automatic Python 3.12.8 installation via pyenv if needed
- **Docker Setup**: Docker and Docker Compose installation
- **GPU Detection**: NVIDIA GPU detection and CUDA configuration
- **Hardware Profiling**: Automatic hardware capability detection
- **Service Setup**: Docker image building and systemd service configuration
- **Validation**: Post-installation health checks

### Usage

```bash
# Clone repository
cd /home/fahbrain/projects
git clone <repository-url> omnimind
cd omnimind

# Run one-click installer
./scripts/canonical/install/install_omnimind.sh
```

**Nota**: O script de instalação está localizado em `scripts/canonical/install/install_omnimind.sh` e detecta automaticamente:
- Sistema operacional (Ubuntu, Fedora, Arch, Kali Linux)
- Gerenciador de pacotes (apt, dnf, yum, pacman)
- GPU NVIDIA e CUDA
- Python 3.12.8 (obrigatório)

### What It Does

1. **System Detection**
   - Detects OS and distribution
   - Identifies package manager
   - Detects GPU and hardware capabilities

2. **System Dependencies**
   - Installs build tools (gcc, make, etc.)
   - Installs Python development headers
   - Installs required libraries

3. **Python Environment**
   - Creates virtual environment
   - Installs Python packages from requirements.txt
   - Validates installation

4. **Configuration**
   - Creates .env file from template
   - Sets up configuration directories
   - Runs configuration validation

5. **Hardware Optimization**
   - Configures GPU support if available
   - Sets CPU-only mode if no GPU

6. **Services**
   - Builds Docker images
   - Prepares systemd service files

7. **Validation**
   - Runs diagnostic checks
   - Verifies module imports
   - Generates installation report

### Logs

Installation log saved to: `logs/install_YYYYMMDD_HHMMSS.log`

---

## Environment Auto-Detection

### Overview
Automatic hardware and environment detection with optimized configuration generation.

### Features
- **CPU Detection**: Core count, frequency, architecture
- **RAM Detection**: Total and available memory
- **GPU Detection**: NVIDIA GPU with VRAM and compute capability
- **Automatic Optimization**: Generates optimal batch sizes, worker counts, etc.

### Usage

A detecção automática de hardware é feita via variáveis de ambiente no script de inicialização:

```bash
# Configuração GPU (Kali Linux Native Paths)
export CUDA_HOME="/usr"
export CUDA_PATH="/usr"
export LD_LIBRARY_PATH="/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH}"
export CUDA_VISIBLE_DEVICES="0"
export OMNIMIND_GPU=true
export OMNIMIND_FORCE_GPU=true
```

**Nota**: O sistema OmniMind usa detecção de GPU via PyTorch (`torch.cuda.is_available()` e `torch.cuda.device_count()`). O script `start_omnimind_system.sh` força GPU via variáveis de ambiente.

### Verificação de GPU

```bash
# Verificar GPU status
python3 -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'Device count: {torch.cuda.device_count()}')"
```

### Sample Output

```json
{
  "device": "cuda",
  "use_gpu": true,
  "llm_batch_size": 8,
  "embedding_batch_size": 64,
  "max_tensor_size": 5000,
  "num_workers": 7,
  "vector_db": "chromadb",
  "cache_backend": "fakeredis"
}
```

---

## Dependency Management

### Overview
Gerenciamento de dependências com múltiplos arquivos de requirements por categoria.

### Estrutura de Requirements

O projeto OmniMind usa múltiplos arquivos de requirements:

- **`requirements/requirements-core.txt`**: Dependências principais do sistema
- **`requirements/requirements-dev.txt`**: Ferramentas de desenvolvimento
- **`requirements/requirements-gpu.txt`**: Dependências específicas de GPU (PyTorch com CUDA)
- **`requirements/requirements-cpu.txt`**: Dependências para CPU-only

### Instalação

```bash
# Instalar dependências principais
pip install -r requirements/requirements-core.txt

# Instalar ferramentas de desenvolvimento
pip install -r requirements/requirements-dev.txt

# Se GPU disponível
pip install -r requirements/requirements-gpu.txt

# Ou instalar tudo de uma vez (se requirements.txt existir)
pip install -r requirements.txt
```

### Ferramentas de Desenvolvimento

As ferramentas de desenvolvimento estão em `requirements/requirements-dev.txt`:

- **Black** (>=25.0.0): Formatação de código
- **Flake8** (>=7.0.0): Linting
- **MyPy** (>=1.15.0): Verificação de tipos
- **Isort** (>=7.0.0): Ordenação de imports
- **Pytest** e plugins: Testes
- **Pre-commit**: Hooks de pré-commit

### Lockfile Format

```json
{
  "generated_at": "2025-11-19T00:00:00",
  "python_version": "3.12",
  "platform": "Linux",
  "packages": {
    "pytest": {
      "version": "9.0.0",
      "hash": "abc123...",
      "dependencies": ["pluggy", "iniconfig"],
      "license": "MIT"
    }
  }
}
```

### Security Scanning

Scans dependencies against:
- **OSV Database**: Open Source Vulnerabilities (https://osv.dev)
- **Safety DB**: Python package vulnerability database

### Severity Levels
- **CRITICAL**: Immediate action required
- **HIGH**: Important security fix
- **MEDIUM**: Should be fixed soon
- **LOW**: Minor issue
- **INFO**: Informational only

---

## Configuration Validation

### Overview
Validação de código e configuração usando scripts canônicos.

### Scripts de Validação

#### 1. Validação de Código (`scripts/canonical/validate/validate_code.sh`)

Valida formatação, linting, tipagem e testes:

```bash
./scripts/canonical/validate/validate_code.sh
```

**Verificações realizadas:**
- ✅ Formatação (Black)
- ✅ Linting (Flake8) - erros críticos (E9, F63, F7, F82)
- ✅ Tipagem (MyPy) - máximo 25 erros aceitáveis
- ✅ Testes (Pytest)
- ✅ Integridade de arquivos
- ✅ Cadeia de auditoria

#### 2. Pre-Commit Hook (`scripts/dev/pre_commit_check.sh`)

Executado automaticamente antes de commits:

```bash
# Instalar hook
./scripts/dev/pre_commit_check.sh
```

**Verificações:**
- Formatação (Black) - corrige automaticamente
- Ordenação de imports (Isort) - corrige automaticamente
- Testes unitários essenciais (pytest -m "not integration")

### Health Checks

Pre-deployment checks include:
1. **Port Availability**: Checks if configured ports are free
2. **File Paths**: Validates file paths exist and are accessible
3. **Dependencies**: Verifies required Python packages
4. **Disk Space**: Ensures minimum disk space available
5. **Memory**: Checks available system memory

---

## IDE Setup e Configuração

### Overview
Configuração automática do ambiente de desenvolvimento (VS Code / Cursor).

### Script de Setup (`scripts/dev/setup_ide.sh`)

```bash
./scripts/dev/setup_ide.sh
```

**O que o script faz:**
1. Cria ambiente virtual (se não existir)
2. Instala ferramentas de desenvolvimento (Black, Isort, Pylint, Flake8, MyPy, Pytest)
3. Instala extensões recomendadas do VS Code/Cursor:
   - Python
   - Pylance
   - Black Formatter
   - Isort
   - Flake8
   - MyPy
   - Auto Docstring
   - Even Better TOML

### Configuração do VS Code/Cursor

O arquivo `.vscode/settings.json` já está configurado com:
- Python 3.12.8 obrigatório (venv local)
- Formatação automática (Black) ao salvar
- Organização de imports (Isort) ao salvar
- Linting habilitado (Flake8, MyPy)
- PYTHONPATH configurado para `src/`

**Importante**: Sempre abrir a pasta raiz do projeto (`/home/fahbrain/projects/omnimind`), não a pasta pai.

### Available Templates

1. **Agent Template**: Complete agent class with tools integration
2. **Tool Template**: Tool function with validation and error handling
3. **Test Template**: pytest test suite with fixtures
4. **API Endpoint Template**: FastAPI endpoint with Pydantic models
5. **Data Model Template**: Pydantic model with validators

---

## Ferramentas de Qualidade de Código

### Pipeline de Qualidade (Ordem Obrigatória)

Conforme `.cursor/rules/rules.mdc`, a ordem de validação é:

1. **Black** (formatação)
   ```bash
   black src tests
   ```

2. **Flake8** (linting)
   ```bash
   flake8 src tests --max-line-length=100
   ```

3. **MyPy** (tipagem)
   ```bash
   mypy src tests
   ```

4. **Testes** (via scripts oficiais)
   ```bash
   # Suite rápida (diária)
   ./scripts/run_tests_fast.sh

   # Suite completa (semanal)
   ./scripts/run_tests_with_defense.sh
   ```

### Ferramentas Disponíveis

- **Black** (>=25.0.0): Formatação automática
- **Flake8** (>=7.0.0): Linting (PEP 8)
- **MyPy** (>=1.15.0): Verificação de tipos estáticos
- **Isort** (>=7.0.0): Ordenação de imports
- **Pylint** (>=4.0.0): Análise estática adicional (opcional)

### Issue Categories

- **SECURITY**: Security vulnerabilities (eval, exec, SQL injection, hardcoded secrets)
- **PERFORMANCE**: Performance issues (string concatenation in loops)
- **STYLE**: Code style violations (line length, multiple statements)
- **COMPLEXITY**: High complexity functions
- **MAINTAINABILITY**: Maintainability issues (mutable defaults)
- **DOCUMENTATION**: Missing or poor documentation
- **TYPE_SAFETY**: Missing type hints
- **ERROR_HANDLING**: Poor error handling (bare except, pass in except)

### Severity Levels

- **CRITICAL**: Must fix before deployment
- **ERROR**: Should fix soon
- **WARNING**: Should be addressed
- **INFO**: Informational only

### Example Report

```markdown
# Code Review Report: src/agents/my_agent.py
Generated: 2025-11-19T00:00:00
Overall Score: 8.5/10.0
Status: ✅ PASSED

## Metrics
- Lines of Code: 150
- Complexity: 5
- Maintainability Index: 75.0/100
- Type Hint Coverage: 95.0%
- Docstring Coverage: 90.0%

## Issues Summary
- Total: 3
- Critical: 0
- Errors: 0
- Warnings: 2
- Info: 1
```

---

## Scripts de Teste e Validação

### Scripts Principais

#### 1. Suite Rápida (Diária) - `scripts/run_tests_fast.sh`

```bash
./scripts/run_tests_fast.sh
```

**Características:**
- Força GPU via variáveis de ambiente
- Exclui testes `@pytest.mark.slow` e `@pytest.mark.chaos`
- Inclui testes `@pytest.mark.real` (sem chaos)
- Duração: ~15-20 min
- Logs em `data/test_reports/`

#### 2. Suite Completa (Semanal) - `scripts/run_tests_with_defense.sh`

```bash
./scripts/run_tests_with_defense.sh
```

**Características:**
- Inclui todos os testes (incluindo chaos)
- Força GPU
- Duração: ~45-90 min
- Logs em `data/test_reports/`

### Scripts de Validação

- **`scripts/canonical/validate/validate_code.sh`**: Validação completa de código
- **`scripts/canonical/validate/validate_services.sh`**: Validação de serviços
- **`scripts/canonical/test/run_full_test_suite.sh`**: Suite completa de testes

### Advanced Usage

```python
# Establish baseline
benchmark = PerformanceBenchmark()
baseline = benchmark.establish_baseline(
    "my_algorithm_v1",
    my_algorithm_v1,
    iterations=100
)

# Compare optimized version
comparison = benchmark.compare_to_baseline(
    "my_algorithm_v1",
    "my_algorithm_v2",
    my_algorithm_v2,
    iterations=100
)

print(comparison.summary)
# Output: "Optimized version is 25.0% faster, 10.0% less memory"

# Regression detection
detector = RegressionDetector(regression_threshold=10.0)
regression = detector.detect_regressions("my_algorithm", result)

if regression["has_regression"]:
    print(f"⚠️ Regression detected: {regression['message']}")
```

### Regression Detection

Automatically detects performance regressions:
- Compares against recent N benchmarks (default: 5)
- Alerts if performance degrades beyond threshold (default: 10%)
- Tracks both time and memory regressions
- Generates trend reports

### Trend Reports

```markdown
# Performance Trend Report: my_workload
Total measurements: 10
Date range: 2025-11-01 to 2025-11-19

## Performance Over Time
| Timestamp | Time (ms) | Memory (MB) | CPU (%) |
| --- | --- | --- | --- |
| 2025-11-01 | 10.50 | 25.0 | 45.0 |
| 2025-11-10 | 10.25 | 24.5 | 44.0 |
| 2025-11-19 | 10.00 | 24.0 | 43.0 |

## Trends
- Time: -4.8% (from first to last)
- Memory: -4.0% (from first to last)
```

---

## Workflow de Desenvolvimento Completo

### 1. Setup Inicial

```bash
# Clone e configure ambiente
cd /home/fahbrain/projects
git clone <repository-url> omnimind
cd omnimind

# Criar venv e instalar dependências
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements-core.txt
pip install -r requirements/requirements-dev.txt

# Configurar IDE
./scripts/dev/setup_ide.sh
```

### 2. Desenvolvimento Diário

```bash
# Ativar ambiente
source .venv/bin/activate

# Desenvolver código...

# Validar antes de commitar
./scripts/canonical/validate/validate_code.sh

# Rodar testes rápidos
./scripts/run_tests_fast.sh
```

### 3. Pre-Commit

O hook `scripts/dev/pre_commit_check.sh` executa automaticamente:
- Formatação (Black)
- Ordenação de imports (Isort)
- Testes unitários essenciais

---

## Boas Práticas

### Instalação
1. Sempre usar Python 3.12.8 (obrigatório)
2. Usar script de instalação canônico: `scripts/canonical/install/install_omnimind.sh`
3. Verificar logs de instalação em `logs/install_*.log`
4. Validar GPU após instalação: `python3 -c "import torch; print(torch.cuda.is_available())"`

### Dependências
1. Usar arquivos de requirements por categoria (`requirements-core.txt`, `requirements-dev.txt`, etc.)
2. Não instalar dependências globalmente - sempre usar venv
3. Atualizar requirements quando adicionar novas dependências
4. Testar após atualizar dependências

### Qualidade de Código
1. Sempre rodar pipeline de qualidade antes de commitar:
   - `black src tests`
   - `flake8 src tests --max-line-length=100`
   - `mypy src tests`
2. Usar scripts oficiais de teste (não rodar `pytest tests` direto)
3. Manter tipagem completa em código novo
4. Adicionar logs informativos (sem TODO/FIXME)

### Testes
1. Suite rápida diária: `./scripts/run_tests_fast.sh`
2. Suite completa semanal: `./scripts/run_tests_with_defense.sh`
3. Testes críticos (phi, IIT, Lacanian, Freud) devem usar `@pytest.mark.real`
4. Testes que destroem servidor devem usar `@pytest.mark.chaos`

---

## Troubleshooting

### Problemas de Instalação

**Problema**: Python version incorreta
**Solução**: Python 3.12.8 é obrigatório. Instalar via pyenv ou usar sistema de pacotes.

**Problema**: GPU não detectada
**Solução**:
```bash
# Verificar drivers NVIDIA
nvidia-smi

# Verificar CUDA
python3 -c "import torch; print(torch.cuda.is_available())"

# Verificar variáveis de ambiente
echo $CUDA_HOME
echo $LD_LIBRARY_PATH
```

**Problema**: Permission denied
**Solução**: Não rodar como root. O script usa `sudo` quando necessário.

### Problemas de Dependências

**Problema**: D-Bus não encontrado
**Solução**: Instalar dependências do sistema primeiro:
```bash
sudo apt-get install -y libdbus-1-dev pkg-config
pip install -r requirements.txt
```

**Problema**: Erros de importação
**Solução**: Verificar que PYTHONPATH inclui `src/`:
```bash
export PYTHONPATH="${PWD}/src:${PYTHONPATH}"
```

### Problemas de Qualidade de Código

**Problema**: Black formatação falha
**Solução**: Rodar manualmente: `black src tests`

**Problema**: MyPy muitos erros
**Solução**: Máximo 25 erros aceitáveis. Verificar tipos gradualmente.

**Problema**: Testes falhando
**Solução**: Verificar se GPU está disponível e se Ollama está rodando com modelo `phi:latest`

---

## Referências

- **Scripts Canônicos**: `scripts/canonical/`
- **Configuração do Sistema**: `.cursor/rules/rules.mdc`
- **Guia de Ambiente**: `docs/guides/ENVIRONMENT_SETUP.md`
- **Guia de Uso**: `docs/guides/USAGE_GUIDE.md`
- **Guia de Modo Dev**: `docs/guides/DEV_MODE.md`

---

**Autor**: Fabrício da Silva + assistência de IA (Copilot GitHub/Cursor/Gemini/Perplexity)
**Última Atualização**: 5 de Dezembro de 2025
