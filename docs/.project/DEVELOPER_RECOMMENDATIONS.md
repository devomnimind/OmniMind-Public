# 👨‍💻 RECOMENDAÇÕES PARA DESENVOLVEDORES

**Última Atualização:** 23 de novembro de 2025  
**Versão:** 1.0 - Phase 15 Stable

---

## 🎯 Antes de Começar a Trabalhar

### 1. Setup Inicial

```bash
# Clone o repositório
git clone https://github.com/devomnimind/OmniMind.git
cd OmniMind

# Ative o ambiente (auto-ativação via .zshrc)
cd omnimind  # ou entrando na pasta
# ✅ Ambiente deve ativar automaticamente com Python 3.12.8

# Verifique Python
python --version  # Deve ser 3.12.8

# Instale dependências
pip install -r requirements.txt

# Valide GPU (se disponível)
python -c "import torch; print(torch.cuda.is_available())"  # Deve ser True
```

### 2. Estrutura de Pastas Esperada

```
omnimind/
├── src/
│   ├── agents/                 # Multi-agent system
│   ├── tools/                  # Agent tools
│   ├── memory/                 # Episodic + Semantic
│   ├── audit/                  # Immutable audit chain
│   ├── security/               # Security layers
│   ├── integrations/           # MCP, D-Bus, etc
│   └── omnimind_core.py        # Main orchestrator
├── tests/
│   ├── agents/
│   ├── tools/
│   ├── audit/
│   └── ...                     # 1 pasta por módulo
├── docs/
│   ├── .project/               # Canonical docs
│   │   ├── CURRENT_PHASE.md   # Fase atual
│   │   ├── PROBLEMS.md        # Histórico de problemas
│   │   ├── CHANGELOG.md       # Mudanças
│   │   └── KNOWN_ISSUES.md    # Issues ativas
│   ├── README.md              # Documentação geral
│   └── ...                    # Outros arquivos
├── scripts/
│   ├── validate_code.sh       # Validação completa
│   ├── protect_project_structure.sh
│   └── ...
├── .venv/                      # Virtual environment LOCAL
├── .env                        # Variáveis de ambiente
├── .python-version             # Lock: 3.12.8
├── pytest.ini                  # Config pytest
├── .coveragerc                 # Config cobertura
└── README.md                   # Início
```

### 3. Padrões de Código Obrigatórios

```python
# ✅ OBRIGATÓRIO: Type hints 100%
def calculate_attention(query: Tensor, keys: Tensor) -> Tensor:
    """Calculate multi-head attention.
    
    Args:
        query: Query tensor of shape (batch, seq_len, dim)
        keys: Keys tensor of shape (batch, seq_len, dim)
    
    Returns:
        Attention output tensor
    """
    pass

# ✅ OBRIGATÓRIO: Google-style docstrings
def train_model(
    model: NeuralNetwork,
    data: DataLoader,
    epochs: int = 10,
    lr: float = 1e-3
) -> Dict[str, float]:
    """Train neural network model.
    
    Args:
        model: Model to train
        data: Training data loader
        epochs: Number of training epochs (default: 10)
        lr: Learning rate (default: 1e-3)
    
    Returns:
        Dictionary with loss history
    
    Raises:
        ValueError: If epochs < 1
        RuntimeError: If GPU not available
    """
    pass

# ✅ OBRIGATÓRIO: Error handling com logging
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    raise
except Exception as e:
    logger.critical(f"Unexpected error: {e}", exc_info=True)
    raise

# ❌ PROIBIDO: Código incompleto
def feature_not_implemented():
    pass  # ❌ Não permitido

def another_feature():
    NotImplementedError()  # ❌ Não permitido

def broken_feature():
    TODO: implementar  # ❌ Não permitido
```

---

## 🧪 Testes (Obrigatórios)

### Estrutura de Testes

```python
# tests/agents/test_react_agent.py
import pytest
from typing import Generator
from src.agents.react_agent import ReactAgent

class TestReactAgent:
    """Test suite for ReactAgent."""
    
    @pytest.fixture
    def agent(self) -> Generator[ReactAgent, None, None]:
        """Create a test agent."""
        agent = ReactAgent(config={})
        yield agent
        agent.cleanup()
    
    def test_initialization(self, agent: ReactAgent) -> None:
        """Test agent initializes correctly."""
        assert agent.state == "ready"
        assert agent.memory is not None
    
    @pytest.mark.asyncio
    async def test_decision_making(self, agent: ReactAgent) -> None:
        """Test agent makes decisions."""
        decision = await agent.decide(context="test")
        assert decision is not None
```

### Executar Testes

```bash
# Suite completa
pytest tests/ -v

# Com cobertura
pytest tests/ --cov=src --cov-fail-under=90

# Teste específico
pytest tests/agents/test_react_agent.py::TestReactAgent::test_initialization -v

# Skip tests que falham (temporário)
pytest tests/ -k "not test_security"  # Pula testes de segurança
```

### Padrões de Nomes

```python
# ✅ BOM
def test_authentication_with_valid_credentials() -> None:
def test_error_handling_when_database_unavailable() -> None:
def test_gpu_acceleration_returns_correct_result() -> None:

# ❌ RUIM
def test_auth() -> None:
def test_db() -> None:
def test_gpu() -> None:
```

---

## 📋 Checklist Antes de Commit

### 1. Formatação e Linting
```bash
black src/ tests/
flake8 src/ tests/ --max-line-length=100
mypy src/ --ignore-missing-imports
```

### 2. Testes
```bash
# Testes do módulo que mudou
pytest tests/seu_modulo/ -v

# Testes de cobertura
pytest tests/seu_modulo/ --cov=src.seu_modulo --cov-fail-under=90
```

### 3. Validação de Segurança
```bash
# Auditoria de segurança
python -m src.audit.immutable_audit verify_chain_integrity

# Check de dependências
pip check
```

### 4. Status Git
```bash
git status  # Deve estar limpo
git diff    # Review mudanças antes de commit
```

### 5. Commit Message
```
# ✅ BOM - Siga este padrão:
feat: Implement multi-head attention mechanism
fix: Resolve GPU memory leak in training loop
docs: Update CURRENT_PHASE.md with Phase 15 results
test: Add comprehensive tests for SecurityAgent

# ❌ RUIM
Fixed stuff
wip
test

# Formato:
<type>: <subject (max 50 chars)>
<blank line>
<body (optional, max 72 chars)>
```

---

## 🚫 CÓDIGO PROIBIDO (Zero Tolerance)

```python
# ❌ PROIBIDO: Código stub/incompleto
def critical_function():
    pass

# ❌ PROIBIDO: Hardcoded secrets
DATABASE_URL = "postgresql://user:password123@localhost"

# ❌ PROIBIDO: Dados falsificados em produção
def get_metrics():
    return {"cpu": 50.0}  # ❌ Não é real

# ❌ PROIBIDO: Imports não usados
import numpy as np
import os  # Não usado!
from torch import nn  # Não usado!

# ❌ PROIBIDO: Python 3.13+
# Use APENAS Python 3.12.8
import sys
if sys.version_info < (3, 12):
    raise RuntimeError("Must use Python 3.12+")

# ❌ PROIBIDO: Comentários em código
# for i in range(10):
#     print(i)

# ❌ PROIBIDO: Variáveis não usadas
result = expensive_operation()  # Não usada depois
```

---

## 🔄 Git Workflow

### Branches
```bash
# Feature
git checkout -b feature/my-feature
git push -u origin feature/my-feature

# Bugfix
git checkout -b fix/critical-bug
git push -u origin fix/critical-bug

# Copilot
git checkout -b copilot/task-description
git push -u origin copilot/task-description
```

### Pull Request

1. Criar branch com padrão `feature/`, `fix/`, ou `copilot/`
2. Fazer commit com mensagem descritiva
3. Abrir PR com checklist preenchido
4. Aguardar CI/CD (testes, linting, tipos)
5. Code review
6. Merge quando aprovado

### Rebase Antes de Merge
```bash
git fetch origin
git rebase origin/master
git push -f origin feature/my-feature
```

---

## 📊 Métricas de Qualidade

Todas as mudanças devem manter ou melhorar:

| Métrica | Limite | Status |
|---------|--------|--------|
| Test Pass Rate | ≥95% | ✅ 98.94% |
| Code Coverage | ≥90% | ⚠️ 85% |
| MyPy Errors | 0 | ✅ 0 |
| Type Hints | 100% | ✅ 100% |
| Audit Chain | Válido | ✅ Válido |
| GPU Speedup | >4x | ✅ 5.15x |

**Se alguma métrica piorar, o commit será rejeitado.**

---

## 🆘 Troubleshooting

### "CUDA not available"
```bash
# Verificar
python -c "import torch; print(torch.cuda.is_available())"

# Se False:
sudo modprobe nvidia_uvm
python -c "import torch; print(torch.cuda.is_available())"

# Se ainda False, reinicie e tente novamente
```

### "Python version wrong"
```bash
# Verificar
python --version  # Deve ser 3.12.8

# Se wrong:
# Edite ~/.zshrc e remova conflitos
# Ou: pyenv local 3.12.8
```

### "Tests failing"
```bash
# Executar teste específico com verbose
pytest tests/path/test_file.py::TestClass::test_method -vv

# Ver traceback completo
pytest tests/ -vv --tb=long

# Rodar com debugger
pytest tests/ --pdb
```

### "Git merge conflict"
```bash
# Ver conflitos
git diff

# Resolver manualmente, depois:
git add arquivo_resolvido.py
git commit -m "Resolve merge conflict in..."
```

---

## 📝 Documentação de Código

### Quando Documentar

- ✅ **SEMPRE:** Funções públicas (docstring obrigatória)
- ✅ **SEMPRE:** Parâmetros com tipos complexos
- ✅ **SEMPRE:** Classes e interfaces principais
- ⚠️ **SOMETIMES:** Lógica complexa em comentários
- ❌ **NUNCA:** Código óbvio com comentários

### Exemplo Completo

```python
def process_tensor(
    input_tensor: torch.Tensor,
    operation: Literal["mean", "sum", "max"] = "mean",
    device: Optional[torch.device] = None
) -> torch.Tensor:
    """Process a tensor with specified aggregation operation.
    
    This function applies GPU acceleration if available and applies
    the specified reduction operation along all dimensions.
    
    Args:
        input_tensor: Input tensor to process
        operation: Reduction operation to apply (default: 'mean')
        device: Device to use for computation. If None, auto-detect
    
    Returns:
        Scalar tensor containing the aggregated result
    
    Raises:
        ValueError: If operation not in ('mean', 'sum', 'max')
        RuntimeError: If GPU requested but not available
    
    Example:
        >>> tensor = torch.randn(10, 20, 30)
        >>> result = process_tensor(tensor, operation='sum')
        >>> print(result.shape)
        torch.Size([])
    """
    if operation not in ("mean", "sum", "max"):
        raise ValueError(f"Unknown operation: {operation}")
    
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    tensor_on_device = input_tensor.to(device)
    
    operations = {
        "mean": torch.mean,
        "sum": torch.sum,
        "max": lambda x: torch.max(x)
    }
    
    return operations[operation](tensor_on_device)
```

---

## ✨ Dicas Finais

1. **Leia o código existente** antes de escrever novo código
2. **Teste incrementalmente** - não espere até o final
3. **Commits frequentes** - um feature = um commit
4. **Comunique mudanças** - atualize CURRENT_PHASE.md se relevante
5. **Respeite deadlines** - fale cedo se vai atrasar

---

**Bem-vindo ao OmniMind! 🚀**

