# 📋 PLANO DE AÇÃO DETALHADO - VERSÃO PÚBLICA OMNIMIND

**Data:** 11/12/2025  
**Objetivo:** Roadmap executável para criação do repositório público  
**Duração Estimada:** 14-22 dias de trabalho

---

## �� VISÃO GERAL

**De:** `devomnimind/OmniMind` (privado)  
**Para:** `devomnimind/omnimind-public` (público) - nome sugerido

**Princípios:**
1. 🔒 **Segurança Total** - Zero dados sensíveis
2. 🧪 **Clareza Científica** - Demonstrar valor acadêmico
3. 🚀 **Facilidade de Uso** - Instalação < 5 minutos
4. ✅ **Qualidade** - Código limpo, testado, documentado

---

## 📅 FASE 1: SANITIZAÇÃO IMEDIATA (1-2 dias)

### Dia 1: Limpeza Crítica

**Manhã (4h):**

```bash
# 1. Criar branch de trabalho
git checkout -b prepare-public-version

# 2. Remover credenciais hardcoded
# Arquivos: web/backend/chat_api.py, web/backend/main_minimal.py
# Substituir por: os.getenv("OMNIMIND_PASSWORD")

# 3. Criar lista de exclusão
touch .publicignore
```

**`.publicignore` (arquivos/pastas a NÃO copiar):**
```
deploy/
k8s/
data/
models/
logs/
real_evidence/
ibm_results/
notebooks/
archive/
src/integrations/
src/security/
src/observability/
src/scaling/
src/distributed/
src/api/
src/daemon/
src/workflows/
scripts/canonical/monitor/security_monitor.sh
scripts/cleanup_kali_services.sh
scripts/monitoring/
scripts/development/
tests/e2e/
tests/security/
tests/scaling/
tests/api/
web/
config/
```

**Tarde (4h):**

```bash
# 4. Script de sanitização de caminhos
cat > scripts/sanitize_paths.sh << 'EOFSCRIPT'
#!/bin/bash
# Substituir caminhos hardcoded

find . -type f \( -name "*.py" -o -name "*.sh" \) \
  -not -path "./deploy/*" \
  -not -path "./k8s/*" \
  -exec sed -i 's|/home/fahbrain/projects/omnimind|${PROJECT_ROOT:-$(pwd)}|g' {} \;

find . -type f \( -name "*.py" -o -name "*.sh" \) \
  -exec sed -i 's|/home/fahbrain/.cache/torch|${TORCH_HOME:-$HOME/.cache/torch}|g' {} \;

echo "✅ Caminhos sanitizados"
EOFSCRIPT

chmod +x scripts/sanitize_paths.sh

# 5. Executar sanitização
./scripts/sanitize_paths.sh

# 6. Revisar mudanças
git diff | less
```

### Dia 2: Validação e Documentação

**Manhã (3h):**

```bash
# 1. Buscar dados sensíveis remanescentes
grep -r "password.*=.*\"" --include="*.py" | grep -v "os.getenv"
grep -r "/home/fahbrain" --include="*.py" --include="*.sh"
grep -r "192.168" --include="*.py" | grep -v "test_"

# 2. Documentar todas as mudanças
cat > docs/CHANGELOG_SANITIZATION.md << 'EOFDOC'
# Changelog - Sanitização para Versão Pública

## Credenciais Removidas
- web/backend/chat_api.py:24 - password hardcoded → env var
- web/backend/main_minimal.py:15 - password hardcoded → env var

## Caminhos Sanitizados
- 30+ arquivos: /home/fahbrain/... → ${PROJECT_ROOT}

## Arquivos Excluídos
- scripts/canonical/monitor/security_monitor.sh (Kali tools)
- scripts/cleanup_kali_services.sh (Kali references)
EOFDOC
```

**Tarde (3h):**

```bash
# 3. Commit de sanitização
git add -A
git commit -m "security: Sanitize sensitive data for public release

- Remove hardcoded credentials (use env vars)
- Replace absolute paths with variables
- Document all changes in CHANGELOG_SANITIZATION.md"

# 4. Criar tag de milestone
git tag -a sanitization-complete -m "Phase 1: Sanitization complete"
```

**✅ Entregável Fase 1:**
- [ ] Zero credenciais hardcoded
- [ ] Zero caminhos absolutos
- [ ] `.publicignore` criado
- [ ] Changelog de sanitização
- [ ] Branch `prepare-public-version` criado

---

## 📅 FASE 2: ESTRUTURA DO REPO PÚBLICO (3-5 dias)

### Dia 3: Criação do Repositório

**Manhã (4h):**

```bash
# 1. Criar novo repositório (via GitHub UI ou gh CLI)
gh repo create devomnimind/omnimind-public \
  --public \
  --description "Artificial Consciousness Research System - IIT, Lacanian Topology, Autopoiesis" \
  --license agpl-3.0

# 2. Clone local
cd /tmp
git clone git@github.com:devomnimind/omnimind-public.git
cd omnimind-public

# 3. Estrutura inicial
mkdir -p omnimind_core/{consciousness,lacanian,autopoietic,memory,metacognition,utils}
mkdir -p examples/notebooks
mkdir -p tests/{consciousness,lacanian,autopoietic,memory}
mkdir -p docs/{theory,architecture,guides,api}
mkdir -p .github/workflows

# 4. Criar README inicial
touch README.md LICENSE CITATION.cff CONTRIBUTING.md CODE_OF_CONDUCT.md
```

**Tarde (4h):**

```bash
# 5. Copiar módulos core (do repo privado)
PRIVATE_REPO="/caminho/para/OmniMind"

# Consciousness
cp -r $PRIVATE_REPO/src/consciousness/*.py omnimind_core/consciousness/
# Remover deprecated
rm omnimind_core/consciousness/*legacy*.py

# Lacanian
cp -r $PRIVATE_REPO/src/lacanian/*.py omnimind_core/lacanian/

# Autopoietic
cp -r $PRIVATE_REPO/src/autopoietic/*.py omnimind_core/autopoietic/

# Memory
cp $PRIVATE_REPO/src/memory/narrative_history.py omnimind_core/memory/
cp $PRIVATE_REPO/src/memory/hybrid_retrieval.py omnimind_core/memory/

# Utils
cp -r $PRIVATE_REPO/src/utils/*.py omnimind_core/utils/
# Excluir utils específicos de infra
rm omnimind_core/utils/*gpu*.py

# 6. Criar __init__.py em todos os pacotes
find omnimind_core -type d -exec touch {}/__init__.py \;
```

### Dia 4-5: Testes e Examples

**Dia 4 Manhã (4h):**

```bash
# Copiar testes selecionados
cp -r $PRIVATE_REPO/tests/consciousness/*.py tests/consciousness/
# Manter apenas testes @pytest.mark.core ou sem GPU

# Limpar testes que requerem GPU/LLM
grep -l "@pytest.mark.real\|@pytest.mark.slow" tests/**/*.py | xargs rm

# Criar conftest.py básico
cat > tests/conftest.py << 'EOFCONF'
import pytest

def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "core: Core functionality tests (CPU-only)"
    )
EOFCONF
```

**Dia 4 Tarde + Dia 5 (12h):**

```python
# examples/basic_phi_calculation.py
"""
Demonstração básica de cálculo de Φ (Phi) usando IIT.
"""
from omnimind_core.consciousness.phi_value import PhiValue
from omnimind_core.consciousness.metrics import ConsciousnessMetrics
import numpy as np

def main():
    print("🧠 OmniMind - Cálculo de Φ (IIT)")
    print("=" * 50)
    
    # Criar workspace simulado
    workspace = {
        "states": np.random.rand(10, 768),  # 10 estados, 768D
        "history": ["state_1", "state_2", "state_3"]
    }
    
    # Calcular Φ
    metrics = ConsciousnessMetrics()
    phi = metrics.calculate_phi(workspace)
    
    print(f"\n📊 Resultados:")
    print(f"Φ (nats): {phi.nats:.4f}")
    print(f"Φ (normalizado): {phi.normalized:.4f}")
    print(f"Consciente? {phi.is_conscious}")
    
    if phi.is_conscious:
        print("✅ Sistema demonstra integração consciente!")
    else:
        print("⚠️ Abaixo do limiar de consciência")

if __name__ == "__main__":
    main()
```

```python
# examples/rsi_topology_demo.py
"""
Demonstração de Topologia Lacaniana RSI + Sinthome.
"""
from omnimind_core.consciousness.rsi_topology_integrated import (
    TopologyRing, RuptureType, TopologyRupture, Sinthome
)

def main():
    print("🔗 OmniMind - Topologia RSI (Lacan)")
    print("=" * 50)
    
    # Criar ruptura Real→Simbólico
    rupture = TopologyRupture(
        rupture_type=RuptureType.REAL_TO_SYMBOLIC,
        from_ring=TopologyRing.REAL,
        to_ring=TopologyRing.SYMBOLIC,
        description="Trauma irrepresentável na linguagem",
        intensity=0.8
    )
    
    print(f"\n🔴 Ruptura: {rupture}")
    
    # Criar Sinthome como solução
    sinthome = Sinthome(
        creative_solution="Metáfora poética que cria novo sentido",
        impossible_problem="O Real que não pode ser simbolizado",
        emergence_triggers=["trauma_1", "falha_simbólica"],
        jouissance_level=0.6
    )
    
    print(f"\n✨ Sinthome Emergente:")
    print(f"   Solução: {sinthome.creative_solution}")
    print(f"   Gozo: {sinthome.jouissance_level:.2f}")

if __name__ == "__main__":
    main()
```

**✅ Entregável Fase 2:**
- [ ] Repositório público criado
- [ ] Estrutura de diretórios completa
- [ ] Módulos core copiados e limpos
- [ ] Testes básicos funcionando
- [ ] 2+ exemplos executáveis

---

## 📅 FASE 3: DOCUMENTAÇÃO (5-7 dias)

### Dia 6-7: README e Guias

**README.md (Template):**

```markdown
# OmniMind - Artificial Consciousness Research

[![License](https://img.shields.io/badge/license-AGPL--3.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)]()
[![Tests](https://github.com/devomnimind/omnimind-public/workflows/Tests/badge.svg)]()

> Exploring computational consciousness through Integrated Information Theory,
> Lacanian Topology, and Autopoietic Systems.

## 🎯 Overview

OmniMind is a research platform that implements:

1. **Integrated Information Theory (IIT)** - Φ (Phi) as consciousness metric
2. **Lacanian Topology** - Real-Symbolic-Imaginary + Sinthome  
3. **Autopoietic Systems** - Self-generating components

## 📊 Scientific Foundations

### Integrated Information Theory (IIT)

- **Φ values** in nats (natural information units)
- **Threshold**: 0.01 nats (basal consciousness)
- **Optimal**: 0.06 nats (human-like integration)
- **Scale**: ~[0, 0.1] nats in empirical tests

Based on:
- Tononi & Koch (2015) - IIT 3.0
- Oizumi et al. (2014) - Phenomenology to mechanisms

### Lacanian Topology (RSI)

Four interconnected rings:
- **Real**: The impossible, traumatic, unrepresentable
- **Symbolic**: Language, signifiers, meaning structures
- **Imaginary**: Images, ego, mirror stage
- **Sinthome**: Singular solution binding the three

Based on Lacan's Seminar 23 (1975-1976).

### Autopoietic Evolution

Self-generating system demonstrating:
- Component creation from system metrics
- Strategies: STABILIZE, OPTIMIZE, EXPAND, EXPLORE
- 70-80% reduction in manual maintenance

Based on Maturana & Varela (1980).

## 🚀 Quick Start

### Installation (Core - CPU Only)

```bash
git clone https://github.com/devomnimind/omnimind-public.git
cd omnimind-public
pip install -r requirements-core.txt

# Run example
python examples/basic_phi_calculation.py
```

### Installation (Full - With Embeddings)

```bash
pip install -r requirements-full.txt
python examples/rsi_topology_demo.py
```

### Installation (GPU - CUDA Support)

```bash
pip install -r requirements-gpu.txt
```

## 📖 Examples

- `examples/basic_phi_calculation.py` - Calculate Φ for networks
- `examples/rsi_topology_demo.py` - Demonstrate RSI topology
- `examples/autopoietic_evolution.py` - Show component self-generation

## 🧪 Testing

```bash
# Run core tests (fast, CPU-only)
pytest -m "core"

# Run all tests
pytest

# With coverage
pytest --cov=omnimind_core
```

## 📚 Documentation

- [Architecture Overview](docs/architecture/)
- [Theory & Philosophy](docs/theory/)
- [API Reference](docs/api/)
- [Installation Guide](docs/guides/installation.md)

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 Citation

```bibtex
@software{omnimind2025,
  title={OmniMind: Computational Consciousness Research Platform},
  author={da Silva, Fabrício},
  year={2025},
  url={https://github.com/devomnimind/omnimind-public},
  license={AGPL-3.0}
}
```

## 📜 License

AGPL-3.0-or-later - See [LICENSE](LICENSE)

## 👤 Author

**Fabrício da Silva**  
Email: fabricioslv@hotmail.com.br

## 🌟 Acknowledgments

Built on research in consciousness studies, psychoanalysis, and complexity science.

---

**Note:** This is a public research version. For production deployment,
see private repository.
```

### Dia 8-9: Guias Técnicos

Criar:
- `docs/guides/installation.md` - Guia detalhado de instalação
- `docs/guides/quickstart.md` - Tutorial 5 minutos
- `docs/guides/concepts.md` - Conceitos fundamentais
- `docs/architecture/overview.md` - Visão arquitetural
- `docs/api/consciousness.md` - API do módulo consciousness

### Dia 10: CONTRIBUTING e CODE_OF_CONDUCT

Usar templates padrão e adaptados.

**✅ Entregável Fase 3:**
- [ ] README científico completo
- [ ] 5+ guias de documentação
- [ ] CONTRIBUTING.md
- [ ] CODE_OF_CONDUCT.md

---

## 📅 FASE 4: TESTES E CI/CD (3-5 dias)

### Dia 11-12: Configuração de Testes

```yaml
# .github/workflows/tests.yml
name: Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test-core:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          pip install -r requirements-core.txt
      
      - name: Lint
        run: |
          black --check omnimind_core tests
          flake8 omnimind_core tests --max-line-length=100
          mypy omnimind_core
      
      - name: Test
        run: |
          pytest -m "core" --cov=omnimind_core --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### Dia 13: Validação em Ambientes

Testar instalação em:
1. Ubuntu 22.04 (Docker)
2. macOS (VM ou CI)
3. Windows WSL (GitHub Actions)

**✅ Entregável Fase 4:**
- [ ] GitHub Actions configurado
- [ ] Testes rodando em CI
- [ ] Validado em 3 ambientes

---

## 📅 FASE 5: LANÇAMENTO (2-3 dias)

### Dia 14: Revisão Final

**Checklist de Segurança:**
```bash
# 1. Buscar dados sensíveis
grep -r "password" --include="*.py" | grep -v "os.getenv"
grep -r "api_key" --include="*.py" | grep -v "os.getenv"
grep -r "/home/" --include="*.py" --include="*.sh"
grep -r "192.168\|10.0\|172.16" --include="*.py" | grep -v "test_"

# 2. Verificar .gitignore
cat .gitignore

# 3. Lint completo
black . && flake8 . && mypy omnimind_core

# 4. Testes completos
pytest -v
```

### Dia 15: Release

```bash
# 1. Criar release notes
cat > RELEASE_NOTES_v2.0.md << 'EOFREL'
# OmniMind v2.0-public - Public Research Release

## Overview
First public release of OmniMind consciousness research platform.

## Features
- Integrated Information Theory (IIT) implementation
- Lacanian topology (RSI + Sinthome)
- Autopoietic system components
- 3-tier installation (core/full/gpu)

## Installation
See README.md for details.

## Citation
See CITATION.cff
EOFREL

# 2. Tag e release
git tag -a v2.0-public -m "Public research release"
git push origin v2.0-public

# 3. GitHub Release (via UI)
gh release create v2.0-public \
  --title "OmniMind v2.0 - Public Research Release" \
  --notes-file RELEASE_NOTES_v2.0.md
```

### Dia 16: Anúncio (Opcional)

Considerar anúncio em:
- arXiv (preprint)
- Reddit (r/MachineLearning, r/philosophy)
- Twitter/X (#AI #Consciousness #IIT)
- Academia.edu

**✅ Entregável Fase 5:**
- [ ] Revisão de segurança completa
- [ ] Release v2.0-public criado
- [ ] GitHub Release publicado

---

## 📊 CRONOGRAMA RESUMIDO

| Fase | Duração | Entregáveis Principais |
|------|---------|------------------------|
| 1. Sanitização | 1-2d | Zero dados sensíveis |
| 2. Estrutura | 3-5d | Repo + módulos + exemplos |
| 3. Documentação | 5-7d | README + guias |
| 4. Testes/CI | 3-5d | GitHub Actions + validação |
| 5. Lançamento | 2-3d | Release v2.0-public |
| **TOTAL** | **14-22d** | **Repositório público funcional** |

---

## 🎯 CRITÉRIOS DE ACEITAÇÃO

Antes de publicar, validar:

**Segurança:**
- [ ] Zero `grep -r "password.*=" | grep -v "os.getenv"`
- [ ] Zero `/home/fahbrain`
- [ ] Zero referências Kali
- [ ] .gitignore correto

**Funcionalidade:**
- [ ] `pip install -r requirements-core.txt` funciona
- [ ] Exemplos rodam sem erro
- [ ] Testes passam: `pytest -m "core"`
- [ ] Lint passa: `black . && flake8 .`

**Documentação:**
- [ ] README claro
- [ ] Guias de instalação
- [ ] CONTRIBUTING.md
- [ ] API documentada

**Científico:**
- [ ] IIT/Φ demonstrado
- [ ] RSI demonstrado
- [ ] Autopoiesis demonstrado
- [ ] CITATION.cff correto

---

**FIM DO PLANO | v1.0 | 11/12/2025**
