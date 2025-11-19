# OmniMind Development Tools & Automation

Complete guide to OmniMind's advanced development and setup automation features.

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

### Available Templates

1. **Agent Template**: Complete agent class with tools integration
2. **Tool Template**: Tool function with validation and error handling
3. **Test Template**: pytest test suite with fixtures
4. **API Endpoint Template**: FastAPI endpoint with Pydantic models
5. **Data Model Template**: Pydantic model with validators

---

## Automated Code Review

### Overview
AI-powered automated code review with comprehensive analysis.

### Features
- **Static Analysis**: AST parsing and code metrics
- **Security Scanning**: Vulnerability detection
- **Style Checking**: PEP 8 compliance
- **Complexity Analysis**: Cyclomatic complexity
- **Documentation Checks**: Docstring coverage
- **Type Safety**: Type hint validation
- **Performance Analysis**: Performance issue detection
- **Best Practices**: Python best practice validation

### Usage

```python
from src.workflows.automated_code_review import review_code

# Review a file
result = review_code(
    Path("src/agents/my_agent.py"),
    min_score=8.0,
    output_report=Path("logs/code_review.md")
)

print(f"Score: {result.overall_score:.1f}/10.0")
print(f"Issues: {len(result.issues)}")
print(f"Status: {'✅ PASSED' if result.passed else '❌ FAILED'}")

# View metrics
if result.metrics:
    print(f"Complexity: {result.metrics.complexity}")
    print(f"Type Hints: {result.metrics.type_hint_coverage:.1f}%")
    print(f"Docstrings: {result.metrics.docstring_coverage:.1f}%")
```

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
