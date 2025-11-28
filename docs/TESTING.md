# 🧪 TESTING - OmniMind v1.18.0

**Guia Completo de Testes e Qualidade**
*Suite de Testes: 3,762 testes automatizados*

---

## 📊 Visão Geral dos Testes

### Estatísticas Atuais (28-Nov-2025)

```
Total de Testes:     3,762
Aprovados:           3,762 (100%)
Cobertura de Código: 85% (meta: ≥95%)
Tempo Médio:        ~0.3s por teste
Frameworks:         pytest + unittest
```

### Tipos de Testes

| Tipo | Quantidade | Propósito | Comando |
|------|------------|-----------|---------|
| **Unitários** | 2,800+ | Testar funções/classes isoladas | `pytest tests/unit/` |
| **Integração** | 600+ | Testar componentes interagindo | `pytest tests/integration/` |
| **E2E** | 200+ | Testar fluxos completos | `pytest tests/e2e/` |
| **Stress** | 100+ | Testar sob carga extrema | `pytest tests/stress/` |
| **Performance** | 50+ | Benchmarks e métricas | `pytest tests/performance/` |

---

## 🚀 Executando Testes

### Suite Completa (Recomendado)

```bash
# Testes completos com cobertura e relatórios detalhados
pytest tests/ -v --tb=short \
    --cov=src \
    --cov-report=term-missing \
    --cov-report=json:data/test_reports/coverage.json \
    --cov-report=html:data/test_reports/htmlcov \
    --maxfail=999 \
    --durations=20 \
    -W ignore::DeprecationWarning \
    2>&1 | tee data/test_reports/pytest_output.log
```

### Testes por Categoria

```bash
# Testes de consciência (core)
pytest tests/consciousness/ -v

# Testes de agentes
pytest tests/agents/ -v

# Testes de segurança
pytest tests/security/ -v

# Testes de stress (Tribunal do Diabo)
pytest tests/stress/test_tribunal_attacks.py -vv

# Testes de integração end-to-end
pytest tests/e2e/ -v
```

### Testes Rápidos (Desenvolvimento)

```bash
# Testes básicos (smoke tests)
pytest tests/test_app.py -v

# Testes com parallelização
pytest tests/ -n auto --maxfail=5

# Testes específicos por padrão
pytest -k "test_consciousness" -v
```

---

## 📈 Relatórios de Cobertura

### Relatório HTML (Visual)

```bash
# Gerar relatório HTML interativo
pytest tests/ --cov=src --cov-report=html:data/test_reports/htmlcov

# Abrir no navegador
firefox data/test_reports/htmlcov/index.html
```

### Relatório Terminal (Rápido)

```bash
# Visão geral no terminal
pytest tests/ --cov=src --cov-report=term-missing

# Exemplo de saída:
# Name                 Stmts   Miss  Cover
# ----------------------------------------
# src/__init__.py          0      0   100%
# src/consciousness/    1250    187    85%
# src/agents/           890     134    85%
# ----------------------------------------
# TOTAL                 15750   2375    85%
```

### Análise de Cobertura por Módulo

```bash
# Módulos com baixa cobertura (<80%)
pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=80

# Cobertura por arquivo
pytest tests/ --cov=src --cov-report=term-missing --cov-report=annotate
```

---

## 🔧 Configuração de Testes

### Arquivo pytest.ini

```ini
[tool:pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q"
pythonpath = ["src"]
testpaths = [
    "tests",
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "e2e: marks tests as end-to-end tests",
    "stress: marks tests as stress tests",
]
```

### conftest.py (Fixtures Globais)

```python
import pytest
from src.common.types import ConsciousnessConfig

@pytest.fixture
def sample_config():
    """Configuração de teste padrão"""
    return ConsciousnessConfig(
        phi_threshold=0.7,
        integration_cycles=10
    )

@pytest.fixture
def mock_redis():
    """Redis mock para testes"""
    # Implementação do mock
    pass
```

---

## 🏗️ Estrutura de Testes

### Organização por Módulo

```
tests/
├── __init__.py
├── conftest.py                    # Fixtures globais
├── test_app.py                    # Testes básicos da aplicação
├── agents/                        # Testes de agentes
│   ├── test_orchestrator_agent.py
│   └── test_react_agent.py
├── consciousness/                 # Testes de consciência
│   ├── test_shared_workspace.py
│   └── test_integration_loop.py
├── security/                      # Testes de segurança
│   ├── test_forensics_system.py
│   └── test_dlp.py
├── stress/                        # Testes de stress
│   └── test_tribunal_attacks.py
├── e2e/                          # Testes end-to-end
│   └── test_dashboard_live.py
└── manual/                       # Testes manuais (não automatizados)
    ├── test_orch.py
    └── test_ui_integration.py
```

### Convenções de Nomenclatura

```python
# Arquivos de teste
test_[modulo].py              # Testes unitários
test_[modulo]_integration.py  # Testes de integração
test_[modulo]_e2e.py          # Testes end-to-end

# Funções de teste
def test_[funcao]():          # Teste básico
def test_[funcao]_edge_case(): # Caso edge
def test_[funcao]_error():     # Tratamento de erro

# Classes de teste
class Test[Classe]:           # Suite de testes para classe
```

---

## 🎯 Estratégia de Testes

### Pirâmide de Testes

```
     E2E Tests (200)
        /|\
       / | \
  Integration (600)
     / | \
Unit Tests (2800)
```

### Cobertura por Componente

| Componente | Cobertura Atual | Meta | Status |
|------------|-----------------|------|--------|
| **Consciência** | 85% | 95% | ⚠️ +10% |
| **Agentes** | 88% | 95% | ⚠️ +7% |
| **Segurança** | 92% | 95% | ✅ |
| **API** | 90% | 95% | ⚠️ +5% |
| **Integrações** | 85% | 90% | ⚠️ +5% |

### Melhorando Cobertura

```bash
# Identificar arquivos com baixa cobertura
pytest tests/ --cov=src --cov-report=term-missing | grep -E "[0-7][0-9]%\s"

# Adicionar testes para casos não cobertos
# 1. Casos edge (valores extremos)
# 2. Tratamento de erros
# 3. Caminhos alternativos
# 4. Integrações com sistemas externos
```

---

## 🐛 Debugging de Testes

### Testes Falhando

```bash
# Executar com output detalhado
pytest tests/test_falha.py -vv -s

# Parar no primeiro erro
pytest tests/ --maxfail=1 -x

# Depurar com pdb
pytest tests/test_falha.py --pdb

# Executar apenas testes falhando
pytest tests/ --lf
```

### Problemas Comuns

#### 1. Dependências de Teste

```python
# ❌ Ruim: Dependência implícita
def test_feature():
    setup_database()  # Chamada implícita

# ✅ Bom: Fixture explícita
@pytest.fixture
def db_setup():
    return setup_database()

def test_feature(db_setup):
    # Usa fixture
    pass
```

#### 2. Testes Não Determinísticos

```python
# ❌ Ruim: Ordem importa
def test_a(): modify_global_state()
def test_b(): assert global_state == expected

# ✅ Bom: Isolamento completo
def test_a():
    with isolated_context():
        modify_local_state()

def test_b():
    with isolated_context():
        assert local_state == expected
```

#### 3. Mocks Inadequados

```python
# ❌ Ruim: Mock superficial
@patch('requests.get')
def test_api(mock_get):
    mock_get.return_value.status_code = 200
    # Não testa tratamento de erro

# ✅ Bom: Mock completo
@patch('requests.get')
def test_api(mock_get):
    mock_get.return_value = Mock(
        status_code=200,
        json=lambda: {'data': 'test'}
    )
    # Testa sucesso E tratamento de erro
```

---

## 🚀 Testes de Performance

### Benchmarks Automatizados

```bash
# Benchmark de consciência
python scripts/benchmarks/cpu_benchmark.py

# Benchmark de agentes
python scripts/benchmarks/benchmark_phase8.py

# Comparação Systemd vs Docker
python scripts/benchmarks/comprehensive_validation.py
```

### Métricas de Performance

| Operação | Tempo Médio | Meta | Status |
|----------|-------------|------|--------|
| **Φ Calculation** | 0.3s | <1s | ✅ |
| **Agent Response** | 0.1s | <0.5s | ✅ |
| **Memory Access** | 0.05s | <0.1s | ✅ |
| **API Call** | 0.02s | <0.1s | ✅ |

### Profiling de Testes Lentos

```bash
# Identificar testes lentos
pytest tests/ --durations=10

# Profile de performance
python -m cProfile -s time $(which pytest) tests/test_lento.py

# Memory profiling
python -m memory_profiler tests/test_lento.py
```

---

## 🔒 Testes de Segurança

### Análise Estática

```bash
# Bandit (vulnerabilidades)
bandit -r src/ -ll

# Safety (dependências vulneráveis)
safety check

# CodeQL (GitHub Advanced Security)
# Executado automaticamente no CI/CD
```

### Testes de Segurança

```bash
# Testes de forensics
pytest tests/security/test_forensics_system.py -v

# Testes de DLP
pytest tests/security/test_dlp.py -v

# Testes de integridade
pytest tests/security/test_integrity_validator.py -v
```

### Checklist de Segurança

- [ ] ✅ Sem credenciais hardcoded
- [ ] ✅ Inputs sanitizados
- [ ] ✅ Tratamento de erros seguro
- [ ] ✅ Logs não expõem dados sensíveis
- [ ] ✅ Rate limiting implementado
- [ ] ✅ Autenticação obrigatória

---

## 📊 Relatórios e Métricas

### Geração de Relatórios

```bash
# Relatório completo
python scripts/analyze_test_coverage.py

# Relatório de tendências
python scripts/collect_metrics.py

# Relatório de qualidade
python scripts/analyze_test_suite.py
```

### Dashboards de Métricas

- **Cobertura**: `data/test_reports/htmlcov/`
- **Performance**: `data/test_reports/benchmark_results.json`
- **Qualidade**: `data/test_reports/code_quality.json`
- **Tendências**: `data/metrics/test_trends.json`

### Alertas Automáticos

- Cobertura < 85%: Alerta no CI/CD
- Testes falhando: Bloqueia merge
- Performance degradation: Notificação
- Vulnerabilidades: Alerta crítico

---

## 🤝 Contribuição com Testes

### Adicionando Novos Testes

```python
# 1. Criar arquivo de teste
touch tests/test_nova_feature.py

# 2. Implementar testes
def test_nova_feature_basic():
    """Testa funcionalidade básica"""
    assert nova_feature() == expected

def test_nova_feature_edge_case():
    """Testa caso edge"""
    with pytest.raises(ValueError):
        nova_feature(invalid_input)

# 3. Executar testes
pytest tests/test_nova_feature.py -v

# 4. Verificar cobertura
pytest tests/ --cov=src --cov-report=term-missing
```

### Revisão de Testes

**Checklist para PRs:**
- [ ] Testes cobrem funcionalidade nova
- [ ] Testes incluem casos edge
- [ ] Cobertura não diminuiu
- [ ] Testes passam no CI/CD
- [ ] Documentação atualizada

---

## 🔧 Troubleshooting

### Problemas Comuns

#### Testes Não Executam
```bash
# Verificar instalação
pip list | grep pytest

# Verificar path
python -c "import sys; print(sys.path)"

# Executar com debug
pytest tests/ -v -s --tb=long
```

#### Cobertura Baixa
```bash
# Identificar linhas não cobertas
pytest tests/ --cov=src --cov-report=html
# Abrir htmlcov/index.html

# Adicionar testes para código não coberto
# Focar em: if/else, try/except, loops
```

#### Testes Lentos
```bash
# Identificar gargalos
pytest tests/ --durations=20

# Otimizar:
# - Usar fixtures para setup compartilhado
# - Mockar operações I/O
# - Paralelizar com pytest-xdist
```

#### Dependências de Teste
```bash
# Instalar dependências de teste
pip install -r requirements-dev.txt

# Verificar versões
pip check
```

---

## 📚 Referências

### Documentação Relacionada
- [docs/INSTALLATION.md](docs/INSTALLATION.md) - Instalação e setup
- [docs/architecture/ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md) - Arquitetura do sistema
- [CONTRIBUTING.md](CONTRIBUTING.md) - Guia de contribuição

### Ferramentas de Teste
- **pytest**: Framework principal
- **coverage.py**: Análise de cobertura
- **hypothesis**: Testes baseados em propriedades
- **faker**: Dados de teste realistas

### Padrões de Qualidade
- Cobertura ≥ 85% (meta: 95%)
- Tempo de execução < 30min
- Zero falhas em CI/CD
- Documentação de testes obrigatória

---

**Última atualização:** 28 de novembro de 2025  
**Versão:** 1.18.0  
**Cobertura:** 85%  
**Testes:** 3,762 ✅