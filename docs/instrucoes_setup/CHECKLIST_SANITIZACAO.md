# ✅ CHECKLIST DE SANITIZAÇÃO - VERSÃO PÚBLICA

**Data:** 11/12/2025  
**Uso:** Validação antes de publicar repositório

---

## 🔒 SEGURANÇA - PRIORIDADE CRÍTICA

### Credenciais e Secrets

- [ ] Buscar passwords hardcoded:
  ```bash
  grep -r "password.*=.*[\"']" --include="*.py" | grep -v "os.getenv" | grep -v "test_"
  ```
  
- [ ] Buscar API keys hardcoded:
  ```bash
  grep -r "api_key.*=.*[\"']" --include="*.py" | grep -v "os.getenv" | grep -v "\.example"
  ```
  
- [ ] Buscar tokens hardcoded:
  ```bash
  grep -r "token.*=.*[\"']" --include="*.py" | grep -v "os.getenv" | grep -v "test_"
  ```

- [ ] Verificar se .env.example está documentado e .env em .gitignore

**❌ FALHOU?** CRÍTICO - Não prosseguir sem corrigir!

### Caminhos Absolutos

- [ ] Buscar caminhos de usuário:
  ```bash
  grep -r "/home/\|/Users/\|C:\\\\" --include="*.py" --include="*.sh" | grep -v "# "
  ```

- [ ] Substituir por variáveis de ambiente ou paths relativos

**Padrão correto:**
```python
PROJECT_ROOT = os.getenv("PROJECT_ROOT", os.getcwd())
```

### IPs e Hosts Privados

- [ ] Buscar IPs privados:
  ```bash
  grep -rE "192\.168\.|10\.|172\.(1[6-9]|2[0-9]|3[01])\." --include="*.py" | grep -v "test_"
  ```

- [ ] Verificar se são apenas mocks/testes ✅ ou dados reais ❌

### Informações de Infraestrutura

- [ ] Buscar referências a Kali:
  ```bash
  grep -ri "kali" --include="*.sh" --include="*.py"
  ```

- [ ] Buscar ferramentas de pentesting:
  ```bash
  grep -ri "metasploit\|sqlmap\|hydra\|aircrack" --include="*.sh"
  ```

- [ ] **AÇÃO:** Remover completamente arquivos com referências ofensivas

**Arquivos para excluir:**
- `scripts/canonical/monitor/security_monitor.sh`
- `scripts/cleanup_kali_services.sh`

---

## 📂 ESTRUTURA DE ARQUIVOS

### Arquivos/Pastas a EXCLUIR

- [ ] `deploy/` → Contém configs de produção
- [ ] `k8s/` → Kubernetes específico
- [ ] `data/` → Dados de runtime (exceto samples)
- [ ] `models/` → Modelos LLM (GB de dados)
- [ ] `logs/` → Logs de execução
- [ ] `real_evidence/` → Testes privados
- [ ] `ibm_results/` → Resultados quantum privados
- [ ] `notebooks/` → Experimentos privados
- [ ] `archive/` → Arquivos antigos
- [ ] `web/` → Frontend de produção
- [ ] `config/` → Configurações privadas
- [ ] `src/integrations/` → Infra-específico
- [ ] `src/security/` → Infra-específico
- [ ] `src/api/` → API de produção
- [ ] `src/daemon/` → Daemon privado

### .gitignore Adequado

- [ ] Verificar que .gitignore público cobre:
  ```
  .env
  .env.*
  *.log
  __pycache__/
  *.pyc
  .mypy_cache/
  .pytest_cache/
  .coverage
  htmlcov/
  dist/
  build/
  *.egg-info/
  ```

---

## 📝 DOCUMENTAÇÃO

### Arquivos Obrigatórios

- [ ] `README.md` - Científico e claro
- [ ] `LICENSE` - AGPL-3.0 (copiar do privado)
- [ ] `CITATION.cff` - Citação bibliográfica
- [ ] `CONTRIBUTING.md` - Guia de contribuição
- [ ] `CODE_OF_CONDUCT.md` - Código de conduta

### Conteúdo do README

- [ ] Visão geral clara do projeto
- [ ] Fundamentos científicos (IIT, Lacan, Autopoiesis)
- [ ] Instruções de instalação (3 níveis)
- [ ] Exemplos de uso
- [ ] Link para documentação
- [ ] Seção de citação
- [ ] Licença e autor

### Guias Técnicos

- [ ] `docs/guides/installation.md`
- [ ] `docs/guides/quickstart.md`
- [ ] `docs/guides/concepts.md`
- [ ] `docs/architecture/overview.md`

---

## 🔬 CÓDIGO E QUALIDADE

### Linting

- [ ] Black formatado:
  ```bash
  black omnimind_core tests examples --check
  ```

- [ ] Flake8 sem erros:
  ```bash
  flake8 omnimind_core tests --max-line-length=100
  ```

- [ ] Mypy sem erros críticos:
  ```bash
  mypy omnimind_core
  ```

### Type Hints

- [ ] Módulos core têm type hints
- [ ] Funções públicas têm type hints
- [ ] Classes têm atributos tipados

### Docstrings

- [ ] Módulos principais têm docstrings
- [ ] Funções públicas têm docstrings
- [ ] Classes têm docstrings

**Estilo:** Google-style docstrings

---

## 🧪 TESTES

### Testes Básicos

- [ ] Testes core rodam sem GPU:
  ```bash
  pytest -m "core"
  ```

- [ ] Cobertura > 70%:
  ```bash
  pytest --cov=omnimind_core --cov-report=term
  ```

### Testes Excluídos

- [ ] Removidos testes que requerem GPU obrigatoriamente
- [ ] Removidos testes e2e de infraestrutura
- [ ] Removidos testes de segurança específicos

### Markers Pytest

- [ ] Configurado marker `core` para testes públicos
- [ ] Documentado em `pytest.ini` ou `pyproject.toml`

---

## 📦 DEPENDÊNCIAS

### Requirements Files

- [ ] `requirements-core.txt` criado (leve, ~50MB)
- [ ] `requirements-full.txt` criado (médio, ~1GB)
- [ ] `requirements-gpu.txt` criado (completo, ~2.5GB)

### Dependências Core (Mínimo)

Devem incluir apenas:
- [ ] numpy, scipy
- [ ] pydantic, python-dotenv
- [ ] pytest, black, flake8, mypy
- [ ] structlog, rich

**NÃO incluir:**
- ❌ torch (só em full/gpu)
- ❌ qiskit (específico, opcional)
- ❌ fastapi (API de produção)
- ❌ redis (infra)

---

## 🚀 EXEMPLOS FUNCIONAIS

### Examples Criados

- [ ] `examples/basic_phi_calculation.py` - Demonstra IIT/Φ
- [ ] `examples/rsi_topology_demo.py` - Demonstra RSI
- [ ] `examples/autopoietic_evolution.py` - Demonstra autopoiesis

### Validação de Exemplos

- [ ] Cada exemplo roda sem erro:
  ```bash
  python examples/basic_phi_calculation.py
  python examples/rsi_topology_demo.py
  python examples/autopoietic_evolution.py
  ```

- [ ] Exemplos têm output claro e educativo
- [ ] Exemplos têm docstrings explicativas

---

## 🔄 CI/CD

### GitHub Actions

- [ ] `.github/workflows/tests.yml` configurado
- [ ] `.github/workflows/lint.yml` configurado (opcional)
- [ ] CI roda em Python 3.11 e 3.12
- [ ] CI usa `requirements-core.txt`
- [ ] CI executa: lint + testes core + coverage

### Badges

- [ ] Badge de License no README
- [ ] Badge de Python version no README
- [ ] Badge de Tests (após primeiro CI run)
- [ ] Badge de Coverage (opcional, codecov)

---

## ✅ VALIDAÇÃO FINAL

### Instalação em Ambiente Limpo

- [ ] Testado em Ubuntu 22.04 fresco:
  ```bash
  docker run -it ubuntu:22.04
  apt update && apt install -y python3 python3-pip git
  git clone https://github.com/devomnimind/omnimind-public.git
  cd omnimind-public
  pip3 install -r requirements-core.txt
  python3 examples/basic_phi_calculation.py
  ```

- [ ] Testado em macOS (se possível)
- [ ] Testado em Windows WSL (se possível)

### Checklist de Publicação

Antes de `git push origin main`:

- [ ] ✅ Zero credenciais hardcoded (validado)
- [ ] ✅ Zero caminhos absolutos de usuário (validado)
- [ ] ✅ Zero referências Kali/pentesting (validado)
- [ ] ✅ .gitignore correto (validado)
- [ ] ✅ README completo (validado)
- [ ] ✅ Exemplos funcionam (validado)
- [ ] ✅ Testes passam (validado)
- [ ] ✅ Lint passa (validado)
- [ ] ✅ CI configurado (validado)
- [ ] ✅ CITATION.cff correto (validado)
- [ ] ✅ LICENSE presente (validado)

### Revisão por Pares (Opcional)

- [ ] Outra pessoa revisou README
- [ ] Outra pessoa testou instalação
- [ ] Outra pessoa executou exemplos

---

## 🎯 CRITÉRIOS DE ACEITAÇÃO FINAL

**TODOS devem estar ✅ antes de publicar:**

1. **Segurança:** Zero dados sensíveis
2. **Funcionalidade:** Exemplos + testes rodam
3. **Documentação:** README + guias completos
4. **Qualidade:** Lint + type hints OK
5. **Instalação:** Funciona em ambiente limpo

**Se QUALQUER item falhar:** ❌ NÃO PUBLICAR

---

## 📊 ASSINATURAS

**Sanitização Completa:** __________ Data: __________

**Revisão de Segurança:** __________ Data: __________

**Aprovação para Publicação:** __________ Data: __________

---

**FIM DO CHECKLIST | v1.0 | 11/12/2025**
