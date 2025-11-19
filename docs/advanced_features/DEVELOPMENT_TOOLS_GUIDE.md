# Ferramentas de Desenvolvimento e Automação OmniMind

Guia completo dos recursos avançados de desenvolvimento e automação de configuração do OmniMind.

## Sumário

1. [Instalação com Um Clique](#one-click-installation)
2. [Auto-Detecção de Ambiente](#environment-auto-detection)
3. [Gerenciamento de Dependências](#dependency-management)
4. [Validação de Configuração](#configuration-validation)
5. [Ferramentas de Geração de Código](#code-generation-tools)
6. [Revisão de Código Automatizada](#automated-code-review)
7. [Benchmarking de Performance](#performance-benchmarking)

---

## Instalação com Um Clique

### Visão Geral
Script de instalação totalmente automatizado que configura o OmniMind com um único comando.

### Recursos
- **Detecção de SO**: Detecção automática de distribuição Linux (Ubuntu, Fedora, Arch, etc.)
- **Gerenciador de Pacotes**: Auto-detecção e uso do gerenciador de pacotes do sistema (apt, dnf, yum, pacman)
- **Configuração Python**: Instalação automática do Python 3.12.8 via pyenv se necessário
- **Configuração Docker**: Instalação do Docker e Docker Compose
- **Detecção GPU**: Detecção de GPU NVIDIA e configuração CUDA
- **Perfil de Hardware**: Detecção automática de capacidades de hardware
- **Configuração de Serviço**: Construção de imagem Docker e configuração de serviço systemd
- **Validação**: Verificações de saúde pós-instalação

### Usage

```bash
# Clone repository
git clone https://github.com/fabs-devbrain/OmniMind.git
cd OmniMind

# Run one-click installer
./scripts/install_omnimind.sh
```

### What It Does

1. **System Detection**
   - Detects OS and distribution
   - Identifies package manager
   - Detects GPU and hardware capabilities

2. **Dependências do Sistema**
   - Instala ferramentas de compilação (gcc, make, etc.)
   - Instala headers de desenvolvimento Python
   - Instala bibliotecas necessárias

3. **Ambiente Python**
   - Cria ambiente virtual
   - Instala pacotes Python de requirements.txt
   - Valida instalação

4. **Configuração**
   - Cria arquivo .env do template
   - Configura diretórios de configuração
   - Executa validação de configuração

5. **Otimização de Hardware**
   - Configura suporte GPU se disponível
   - Define modo apenas CPU se não houver GPU

6. **Serviços**
   - Constrói imagens Docker
   - Prepara arquivos de serviço systemd

7. **Validação**
   - Executa verificações de diagnóstico
   - Verifica importações de módulos
   - Gera relatório de instalação

### Logs

Installation log saved to: `logs/install_YYYYMMDD_HHMMSS.log`

---

## Auto-Detecção de Ambiente

### Visão Geral
Detecção automática de hardware e ambiente com geração de configuração otimizada.

### Recursos
- **Detecção CPU**: Contagem de núcleos, frequência, arquitetura
- **Detecção RAM**: Memória total e disponível
- **Detecção GPU**: GPU NVIDIA com VRAM e capacidade de computação
- **Otimização Automática**: Gera tamanhos de batch ideais, contagens de workers, etc.

### Uso

```python
from src.optimization.hardware_detector import auto_configure

# Auto-detect and configure
profile, config = auto_configure(save=True, prefer_local=True)

print(f"Device: {config.device}")
print(f"GPU: {profile.gpu_name}")
print(f"Batch Size: {config.llm_batch_size}")
```

### Configuration Files

After detection, configuration is saved to:
- `config/hardware_profile.json` - Hardware capabilities
- `config/optimization_config.json` - Optimized settings

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
Advanced dependency management with security scanning and version locking.

### Features
- **Dependency Locking**: SHA-256 hash verification
- **Security Scanning**: OSV API and Safety DB integration
- **Conflict Detection**: Automatic dependency conflict resolution
- **Update Suggestions**: Compatible version updates
- **Security Reports**: Detailed vulnerability reports

### Usage

```python
from src.tools.dependency_manager import DependencyManager

# Initialize manager
manager = DependencyManager()

# Generate lockfile
lockfile = manager.generate_lockfile()
print(f"Locked {len(lockfile.packages)} packages")

# Scan for vulnerabilities
vulnerabilities = manager.scan_vulnerabilities()
print(f"Found {len(vulnerabilities)} vulnerabilities")

# Generate security report
report = manager.generate_security_report(
    Path("logs/security_report.md")
)
```

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
Pre-deployment configuration validation with health checks.

### Features
- **Schema Validation**: JSON schema validation
- **Dependency Checking**: Required dependency verification
- **Environment Validation**: Environment-specific checks
- **Health Checks**: Pre-deployment validation
- **Auto-fixes**: Automatic configuration corrections

### Usage

```python
from src.security.config_validator import (
    ConfigurationValidator,
    ConfigEnvironment
)

# Initialize validator
validator = ConfigurationValidator(
    environment=ConfigEnvironment.PRODUCTION
)

# Validate configuration
with open("config/omnimind.yaml") as f:
    config = yaml.safe_load(f)

result = validator.validate_config(config)

if result.valid:
    print("✅ Configuration valid")
else:
    print(f"❌ {len(result.issues)} issues found")
    for issue in result.issues:
        print(f"  - {issue.message}")

# Run health checks
health = validator.run_health_checks(config)
print(f"Overall: {health['overall_status']}")
```

### Health Checks

Pre-deployment checks include:
1. **Port Availability**: Checks if configured ports are free
2. **File Paths**: Validates file paths exist and are accessible
3. **Dependencies**: Verifies required Python packages
4. **Disk Space**: Ensures minimum disk space available
5. **Memory**: Checks available system memory

---

## Code Generation Tools

### Overview
AI-assisted code generation with intelligent templates.

### Features
- **Template Types**: Agent, Tool, Test, API Endpoint, Data Model
- **Smart Generation**: Context-aware code generation
- **Boilerplate Reduction**: Reduces repetitive coding
- **Test Generation**: Automatic test case generation
- **Type Hints**: Automatic type hint addition
- **Docstrings**: Google-style docstring generation

### Usage

```python
from src.tools.code_generator import CodeGenerator

generator = CodeGenerator()

# Generate an agent
agent_code = generator.generate_agent(
    agent_name="DataProcessorAgent",
    description="Agent for processing data",
    purpose="Process and analyze data",
    capabilities=[
        "- Data validation",
        "- Data transformation"
    ],
    output_file=Path("src/agents/data_processor.py")
)

# Generate tests
test_code = generator.generate_test(
    module_name="data_processor",
    module_path="src.agents.data_processor",
    class_name="DataProcessorAgent",
    methods=["execute", "validate"],
    output_file=Path("tests/test_data_processor.py")
)

# Generate API endpoint
api_code = generator.generate_api_endpoint(
    endpoint_name="process_data",
    description="Process data endpoint",
    prefix="/api/v1",
    tag="Data",
    path="/process",
    method="post",
    output_file=Path("web/backend/api/data.py")
)
```

### Templates Disponíveis

1. **Template de Agente**: Classe completa de agente com integração de ferramentas
2. **Template de Ferramenta**: Função de ferramenta com validação e tratamento de erros
3. **Template de Teste**: Suite de testes pytest com fixtures
4. **Template de Endpoint API**: Endpoint FastAPI com modelos Pydantic
5. **Template de Modelo de Dados**: Modelo Pydantic com validadores

---

## Revisão Automática de Código

### Visão Geral
Revisão automática de código alimentada por IA com análise abrangente.

### Recursos
- **Análise Estática**: Parsing AST e métricas de código
- **Verificação de Segurança**: Detecção de vulnerabilidades
- **Verificação de Estilo**: Conformidade PEP 8
- **Análise de Complexidade**: Complexidade ciclomática
- **Verificações de Documentação**: Cobertura de docstring
- **Segurança de Tipos**: Validação de type hints
- **Análise de Performance**: Detecção de problemas de performance
- **Melhores Práticas**: Validação de melhores práticas Python

### Usage

```python
from src.workflows.automated_code_review import review_code

# Revisar um arquivo
result = review_code(
    Path("src/agents/my_agent.py"),
    min_score=8.0,
    output_report=Path("logs/code_review.md")
)

print(f"Pontuação: {result.overall_score:.1f}/10.0")
print(f"Problemas: {len(result.issues)}")
print(f"Status: {'✅ APROVADO' if result.passed else '❌ REPROVADO'}")

# Ver métricas
if result.metrics:
    print(f"Complexidade: {result.metrics.complexity}")
    print(f"Type Hints: {result.metrics.type_hint_coverage:.1f}%")
    print(f"Docstrings: {result.metrics.docstring_coverage:.1f}%")
```

### Categorias de Problemas

- **SEGURANÇA**: Vulnerabilidades de segurança (eval, exec, SQL injection, secrets hardcoded)
- **PERFORMANCE**: Problemas de performance (concatenação de strings em loops)
- **ESTILO**: Violações de estilo de código (comprimento de linha, múltiplas declarações)
- **COMPLEXIDADE**: Funções de alta complexidade
- **MANUTENÇÃO**: Problemas de manutenção (padrões mutáveis)
- **DOCUMENTAÇÃO**: Documentação ausente ou inadequada
- **SEGURANÇA_DE_TIPOS**: Type hints ausentes
- **TRATAMENTO_DE_ERROS**: Tratamento inadequado de erros (except vazio, pass em except)

### Níveis de Severidade

- **CRÍTICO**: Deve corrigir antes do deployment
- **ERRO**: Deve corrigir em breve
- **AVISO**: Deve ser abordado
- **INFO**: Apenas informativo

### Relatório de Exemplo

```markdown
# Relatório de Revisão de Código: src/agents/my_agent.py
Gerado: 2025-11-19T00:00:00
Pontuação Geral: 8.5/10.0
Status: ✅ APROVADO

## Métricas
- Linhas de Código: 150
- Complexidade: 5
- Índice de Manutenibilidade: 75.0/100
- Cobertura de Type Hints: 95.0%
- Cobertura de Docstrings: 90.0%

## Resumo de Problemas
- Total: 3
- Críticos: 0
- Erros: 0
- Avisos: 2
- Info: 1
```

---

## Performance Benchmarking

### Overview
Comprehensive performance benchmarking with regression detection.

### Features
- **Benchmark Execution**: Multiple iterations with warmup
- **Metrics Collection**: Time, memory, CPU utilization
- **Baseline Comparison**: Compare against baseline
- **Regression Detection**: Automatic regression alerts
- **Historical Tracking**: Performance trends over time
- **Report Generation**: Detailed benchmark reports

### Usage

```python
from src.optimization.benchmarking import (
    PerformanceBenchmark,
    RegressionDetector,
    benchmark_with_regression_detection
)

# Simple benchmark
def my_workload():
    result = sum(range(1000000))
    return result

# Run benchmark with regression detection
result = benchmark_with_regression_detection(
    name="my_workload",
    workload=my_workload,
    iterations=100,
    regression_threshold=10.0
)

print(result["benchmark"]["mean_time_ms"])
print(result["regression"]["message"])
```

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

## Integration Examples

### Full Development Workflow

```python
from pathlib import Path
from src.tools.code_generator import CodeGenerator
from src.workflows.automated_code_review import review_code
from src.optimization.benchmarking import benchmark_with_regression_detection

# 1. Generate code
generator = CodeGenerator()
generator.generate_agent(
    agent_name="MyAgent",
    description="My custom agent",
    purpose="Custom tasks",
    output_file=Path("src/agents/my_agent.py")
)

# 2. Review code
review_result = review_code(
    Path("src/agents/my_agent.py"),
    min_score=8.0,
    output_report=Path("logs/review.md")
)

if not review_result.passed:
    print("Code review failed - fix issues first")
    exit(1)

# 3. Benchmark performance
def agent_workload():
    from src.agents.my_agent import MyAgent
    agent = MyAgent()
    return agent.execute("test task")

benchmark_result = benchmark_with_regression_detection(
    name="my_agent_performance",
    workload=agent_workload,
    iterations=100
)

print(f"Performance: {benchmark_result['benchmark']['mean_time_ms']:.2f}ms")
```

---

## Best Practices

### Installation
1. Always use one-click installer for new setups
2. Review installation log for any warnings
3. Run validation after installation
4. Keep hardware profile updated

### Dependencies
1. Generate lockfile after any dependency changes
2. Run security scan regularly (weekly recommended)
3. Keep dependencies updated (but test first)
4. Review security reports before deployment

### Code Quality
1. Generate tests for all new code
2. Run code review before committing
3. Maintain 8.0+ code quality score
4. Fix all critical and error-level issues

### Performance
1. Establish baselines for critical operations
2. Run benchmarks before optimization
3. Set appropriate regression thresholds
4. Monitor trends over time

---

## Troubleshooting

### Installation Issues

**Problem**: Python version too old  
**Solution**: Installer will automatically install Python 3.12.8 via pyenv

**Problem**: GPU not detected  
**Solution**: Check NVIDIA drivers with `nvidia-smi`, run `verify_gpu_setup.py`

**Problem**: Permission denied  
**Solution**: Don't run installer as root - it will use sudo when needed

### Dependency Issues

**Problem**: Lockfile verification fails  
**Solution**: Regenerate lockfile with `manager.generate_lockfile()`

**Problem**: Vulnerability scan timeout  
**Solution**: Disable OSV scanning temporarily: `scan_vulnerabilities(use_osv=False)`

### Code Review Issues

**Problem**: Score too low  
**Solution**: Check specific issues and fix highest severity first

**Problem**: False positives  
**Solution**: Review suggestions - not all are required to fix

### Benchmark Issues

**Problem**: High variance in results  
**Solution**: Increase warmup iterations or iterations count

**Problem**: Regression false positive  
**Solution**: Adjust regression threshold or check system load

---

## Contributing

When adding new features:
1. Use code generator for boilerplate
2. Run automated code review
3. Add comprehensive tests
4. Run benchmarks for performance-critical code
5. Update this documentation

---

## License

MIT License - See LICENSE file for details

---

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/fabs-devbrain/OmniMind/issues
- Documentation: https://github.com/fabs-devbrain/OmniMind/docs
