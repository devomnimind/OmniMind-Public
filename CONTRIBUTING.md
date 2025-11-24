# Contributing to OmniMind

Obrigado por considerar contribuir com o OmniMind! Este documento fornece diretrizes e melhores práticas para contribuir com o projeto.

---

## 🤝 Código de Conduta

Esperamos que todos os contribuidores sigam nosso código de conduta:

- **Respeito Mútuo:** Trate todos os colaboradores com respeito e profissionalismo
- **Comunicação Clara:** Seja claro e objetivo em todas as comunicações
- **Foco em Qualidade:** Priorize código limpo, testado e bem documentado
- **Colaboração Construtiva:** Forneça feedback construtivo e esteja aberto a críticas
- **Inclusividade:** Seja acolhedor e inclusivo com novos contribuidores

---

## 🎯 Como Contribuir

### Reportar Bugs

Antes de reportar um bug, verifique se já existe uma issue relacionada.

**Para reportar um bug:**

1. Vá para [GitHub Issues](https://github.com/devomnimind/OmniMind/issues)
2. Clique em "New Issue"
3. Use o template de bug report
4. Inclua:
   - Descrição clara do problema
   - Passos para reproduzir
   - Comportamento esperado vs. atual
   - Logs relevantes (se aplicável)
   - Versão do Python, OS, e GPU (se relevante)

**Exemplo:**
```markdown
**Bug:** Neural component falha ao carregar modelo Ollama

**Passos para reproduzir:**
1. Executar `python -m src.neurosymbolic.neural_component`
2. Observar erro: "Connection refused to localhost:11434"

**Esperado:** Conexão bem-sucedida com Ollama
**Atual:** ConnectionError

**Logs:**
```
ERROR - Failed to connect to Ollama: [Errno 111] Connection refused
```

**Ambiente:**
- Python: 3.12.8
- OS: Ubuntu 22.04
- Ollama: Não instalado (causa raiz)
```

### Sugerir Features

Tem uma ideia para melhorar o OmniMind?

1. Abra uma [Discussion](https://github.com/devomnimind/OmniMind/discussions) no GitHub
2. Descreva o caso de uso detalhadamente
3. Explique por que essa feature seria valiosa
4. Aguarde feedback da equipe antes de implementar

**Nota:** Grandes features podem precisar de aprovação antes da implementação para garantir alinhamento com a visão do projeto.

---

## 🔧 Fazer Pull Requests

### Pré-requisitos

Antes de começar, certifique-se de ter:

1. **Python 3.12.8 instalado** (OBRIGATÓRIO - não use 3.13+)
   ```bash
   python --version  # Deve mostrar 3.12.8
   ```

2. **Lido as regras do projeto:**
   - [.agent/rules/antigravity-rules.md](.agent/rules/antigravity-rules.md)
   - [ARCHITECTURE.md](ARCHITECTURE.md)

3. **Ambiente configurado:**
   ```bash
   # Clone o repositório
   git clone https://github.com/devomnimind/OmniMind.git
   cd OmniMind
   
   # Crie e ative virtual environment
   python3.12 -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # .venv\Scripts\activate  # Windows
   
   # Instale dependências
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

### Workflow de Contribuição

#### 1. Fork e Branch

```bash
# Fork o repositório no GitHub, depois:
git clone https://github.com/SEU_USERNAME/OmniMind.git
cd OmniMind

# Adicione upstream
git remote add upstream https://github.com/devomnimind/OmniMind.git

# Crie uma branch para sua feature
git checkout -b feature/minha-feature

# Ou para bugfix
git checkout -b fix/correcao-bug
```

#### 2. Fazer Mudanças

- Faça suas modificações de código
- Siga os [Padrões de Código](#padrões-de-código) (abaixo)
- Escreva testes para suas mudanças

#### 3. Executar Validações OBRIGATÓRIAS

**Antes de commitar, execute TODAS as validações:**

```bash
# 1. Formatação de código (Black)
black src/ tests/
echo "✅ Black formatting: OK"

# 2. Linting (Flake8)
flake8 src/ tests/ --max-line-length=100
echo "✅ Flake8 linting: OK"

# 3. Type checking (MyPy)
mypy src/ --ignore-missing-imports
echo "✅ MyPy type checking: OK"

# 4. Testes (Pytest)
pytest tests/ --cov=src --cov-fail-under=90 -v
echo "✅ Pytest: OK"

# 5. Auditoria de segurança (se modificou código crítico)
python -m src.audit.immutable_audit verify_chain_integrity
echo "✅ Audit chain: OK"
```

**TODAS as validações devem passar antes de abrir um PR.**

#### 4. Commit

Use [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git add .
git commit -m "feat: adiciona suporte para novo backend neural"
# ou
git commit -m "fix: corrige memory leak em episodic memory"
# ou
git commit -m "docs: atualiza ARCHITECTURE.md com Phase 22"
```

**Tipos de commit:**
- `feat:` Nova feature
- `fix:` Correção de bug
- `docs:` Mudanças em documentação
- `refactor:` Refatoração de código (sem mudança de comportamento)
- `test:` Adicionar ou modificar testes
- `perf:` Melhorias de performance
- `chore:` Tarefas de manutenção (build, CI/CD, etc.)
- `style:` Mudanças de formatação (sem impacto funcional)

#### 5. Push e PR

```bash
# Push para seu fork
git push origin feature/minha-feature

# Abra PR no GitHub
# 1. Vá para https://github.com/devomnimind/OmniMind
# 2. Clique em "Compare & pull request"
# 3. Preencha o template de PR
# 4. Aguarde review
```

---

## 📝 Padrões de Código

### Type Hints (100% Obrigatório)

**Todos** os parâmetros e retornos de função devem ter type hints.

✅ **Correto:**
```python
def process_memory(
    text: str,
    embedding_model: str = "default",
    max_tokens: int = 512
) -> Dict[str, Any]:
    """Process text and store in memory."""
    result: Dict[str, Any] = {}
    return result
```

❌ **Incorreto:**
```python
def process_memory(text, embedding_model="default"):
    result = {}
    return result
```

### Docstrings (Google Style - Obrigatório)

**Todas** as funções e classes devem ter docstrings.

✅ **Correto:**
```python
def calculate_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors.
    
    Args:
        vec1: First vector as list of floats.
        vec2: Second vector as list of floats.
    
    Returns:
        Cosine similarity score between 0 and 1.
    
    Raises:
        ValueError: If vectors have different dimensions.
    
    Example:
        >>> calculate_similarity([1.0, 0.0], [0.0, 1.0])
        0.0
    """
    if len(vec1) != len(vec2):
        raise ValueError(f"Dimension mismatch: {len(vec1)} vs {len(vec2)}")
    # Implementation...
```

### Tratamento de Erros (Obrigatório)

**Sempre** use try/except com logging para operações que podem falhar.

✅ **Correto:**
```python
import logging

logger = logging.getLogger(__name__)

def load_model(model_path: str) -> Optional[Any]:
    """Load model from disk."""
    try:
        model = torch.load(model_path)
        logger.info(f"Model loaded successfully from {model_path}")
        return model
    except FileNotFoundError:
        logger.error(f"Model file not found: {model_path}")
        return None
    except Exception as e:
        logger.exception(f"Failed to load model: {e}")
        raise
```

❌ **Incorreto:**
```python
def load_model(model_path):
    model = torch.load(model_path)  # Pode falhar sem tratamento
    return model
```

### Testes (Cobertura Mínima: 90%)

**Todas** as novas features devem incluir testes.

✅ **Exemplo de teste:**
```python
import pytest
from src.memory.episodic_memory import EpisodicMemory

def test_episodic_memory_stores_event():
    """Test that episodic memory stores and retrieves events."""
    memory = EpisodicMemory()
    
    event = {"text": "Test event", "timestamp": "2025-11-24T10:00:00"}
    event_id = memory.store(event)
    
    assert event_id is not None
    retrieved = memory.retrieve(event_id)
    assert retrieved["text"] == "Test event"

def test_episodic_memory_handles_invalid_event():
    """Test that invalid events raise appropriate errors."""
    memory = EpisodicMemory()
    
    with pytest.raises(ValueError):
        memory.store({})  # Event vazio deve falhar
```

### Imports

Use imports absolutos:

✅ **Correto:**
```python
from src.neurosymbolic.neural_component import NeuralComponent
from src.memory.episodic_memory import EpisodicMemory
```

❌ **Incorreto:**
```python
from ..neurosymbolic.neural_component import NeuralComponent  # Import relativo
```

### Logging

Use logging estruturado:

```python
import logging

logger = logging.getLogger(__name__)

# Info para operações normais
logger.info("Processing request", extra={"user_id": user_id})

# Warning para situações anormais não-críticas
logger.warning("Cache miss, fetching from database")

# Error para erros recuperáveis
logger.error(f"Failed to connect to database: {error}")

# Exception para erros graves (com traceback)
logger.exception("Critical failure in neural component")
```

---

## 🚫 Proibido

### 1. Python 3.13+
❌ **NÃO USE Python 3.13 ou superior**
- Razão: Incompatibilidade com PyTorch CUDA
- Obrigatório: Python 3.12.8

### 2. Código Incompleto
❌ **NÃO submeta:**
- Stubs: `def func(): pass`
- Placeholders: `raise NotImplementedError`
- TODOs sem implementação: `# TODO: implement later`

✅ **Apenas código executável e completo**

### 3. Secrets Hardcoded
❌ **NUNCA coloque no código:**
```python
api_key = "sk-1234567890abcdef"  # ERRADO!
db_password = "senha123"  # ERRADO!
```

✅ **Use variáveis de ambiente:**
```python
api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("API_KEY environment variable not set")
```

### 4. Modificações Diretas Sem Testes
❌ **NÃO modifique código sem adicionar testes correspondentes**

### 5. Commits Sem Validação
❌ **NÃO faça commit sem executar as validações obrigatórias**

---

## 🌳 Estrutura de Branches

- `master` - Branch de produção (protegida)
- `copilot/*` - Features em desenvolvimento por copilot agents
- `pr-*` - Pull requests de contribuidores externos
- `feature/*` - Novas features
- `fix/*` - Correções de bugs

---

## 🪝 Pre-commit Hooks (Recomendado)

Configure hooks para validação automática:

```bash
# Instale pre-commit
pip install pre-commit

# Configure hooks
cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.0
    hooks:
      - id: black
        language_version: python3.12
  
  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=100]
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        args: [--ignore-missing-imports]
EOF

# Instale hooks
pre-commit install
```

Agora as validações rodarão automaticamente antes de cada commit!

---

## 🔍 Processo de Review

### Critérios de Aprovação

Para seu PR ser aprovado, ele deve:

1. ✅ Passar em **todas** as validações (Black, Flake8, MyPy, Pytest)
2. ✅ Ter **cobertura de testes ≥90%**
3. ✅ Seguir **padrões de código** documentados
4. ✅ Ter **pelo menos 1 aprovação** de mantenedor
5. ✅ Ter **CI/CD verde** (GitHub Actions)
6. ✅ Passar em **auditoria de segurança** (se aplicável)

### Tempo de Review

- **Small PRs** (<100 linhas): 1-2 dias
- **Medium PRs** (100-500 linhas): 3-5 dias
- **Large PRs** (>500 linhas): 1 semana+

**Dica:** Prefira PRs pequenos e focados para reviews mais rápidos.

### Feedback de Review

Se seu PR receber pedidos de mudança:

1. Faça as alterações solicitadas
2. Execute validações novamente
3. Push para a mesma branch (PR atualiza automaticamente)
4. Responda aos comentários explicando as mudanças

---

## 📚 Recursos Úteis

### Documentação Essencial
- [README.md](README.md) - Visão geral do projeto
- [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitetura detalhada
- [ROADMAP.md](ROADMAP.md) - Roadmap de evolução
- [.agent/rules/antigravity-rules.md](.agent/rules/antigravity-rules.md) - Regras críticas do projeto

### Guias Técnicos
- [docs/guides/VALIDATION_GUIDE.md](docs/guides/VALIDATION_GUIDE.md) - Como validar mudanças
- [docs/guides/TESTING_QA_QUICK_START.md](docs/guides/TESTING_QA_QUICK_START.md) - Testes e QA
- [docs/architecture/](docs/architecture/) - Documentação de arquitetura

### Status do Projeto
- [docs/.project/CURRENT_PHASE.md](docs/.project/CURRENT_PHASE.md) - Fase atual
- [docs/reports/](docs/reports/) - Relatórios de auditoria

---

## ❓ Dúvidas?

Se você tem dúvidas sobre como contribuir:

1. **Procure na documentação** (links acima)
2. **Verifique Issues existentes** no GitHub
3. **Abra uma Discussion** com label `question`
4. **Leia o código** - código é documentação também!

### Canais de Suporte

- **GitHub Issues:** Para bugs e problemas técnicos
- **GitHub Discussions:** Para perguntas gerais e ideias
- **Documentation:** Sempre consulte docs/ primeiro

---

## 🎓 Níveis de Contribuição

### Iniciante
- Corrigir typos em documentação
- Adicionar testes faltantes
- Melhorar docstrings
- Reportar bugs

### Intermediário
- Implementar features pequenas
- Refatorar código existente
- Melhorar performance
- Adicionar logging

### Avançado
- Implementar novas fases (Phase 22+)
- Arquitetura de novos módulos
- Otimizações de GPU/CUDA
- Integrações complexas

**Todos os níveis são bem-vindos!** Comece pequeno e evolua.

---

## 🙏 Agradecimentos

Obrigado por contribuir com o OmniMind! Cada contribuição, grande ou pequena, ajuda a tornar este projeto melhor.

**Happy Coding! 🚀**

---

*Este documento é atualizado regularmente. Última atualização: 24 de novembro de 2025*
