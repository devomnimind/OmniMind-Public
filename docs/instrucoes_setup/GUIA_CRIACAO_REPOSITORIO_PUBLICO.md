# 🚀 Guia: Criação do Repositório Público OmniMind

**Data:** 11 de dezembro de 2025
**Status:** Pronto para Implementação
**Objetivo:** Estrutura, filtros e política de sincronização para versão pública

---

## 📋 ÍNDICE

1. [Visão Geral](#visão-geral)
2. [Estrutura do Repositório Público](#estrutura-do-repositório-público)
3. [Gitignore e Filtros](#gitignore-e-filtros)
4. [README Público](#readme-público)
5. [Política de Sincronização](#política-de-sincronização)
6. [Licensa e CONTRIBUTING](#licensa-e-contributing)

---

## 👁️ VISÃO GERAL

### Objetivo do Repositório Público

```
Repositório Privado (Você)        →→  Repositório Público
├── Desenvolvimento experimental      ├── Código estável
├── Dados reais do sistema           ├── Exemplos de uso
├── Configurações sensíveis          ├── Documentação pedagógica
└── Pesquisa em andamento            └── Pronto para comunidade
```

### Público-Alvo

- **Pesquisadores** interessados em IIT, Psicanálise, Deleuze-Guattari
- **Desenvolvedores** querendo integrar consciência em sistemas
- **Estudantes** de IA, consciência, teoria da computação
- **Comunidade** open source interessada em inovação

---

## 📁 ESTRUTURA DO REPOSITÓRIO PÚBLICO

```
omnimind-public/
├── README.md                          # Visão geral pública
├── INSTALL.md                         # Como instalar
├── QUICKSTART.md                      # Início rápido
├── CONTRIBUTING.md                    # Para contribuidores
├── LICENSE                            # MIT ou Apache 2.0
│
├── src/
│   ├── agents/                        ✅ Público
│   ├── consciousness/
│   │   ├── topological_phi.py         ✅ Público
│   │   ├── shared_workspace.py        ✅ Público
│   │   └── README_CONSCIOUSNESS.md    ✅ Público
│   ├── core/                          ✅ Público
│   ├── memory/
│   │   ├── narrative_history.py       ✅ Público
│   │   ├── hybrid_retrieval.py        ✅ Público
│   │   └── README_MEMORY.md           ✅ Público
│   ├── lacanian/                      ✅ Público
│   ├── quantum_consciousness/         ❌ NÃO INCLUIR
│   ├── security/                      ❌ NÃO INCLUIR
│   └── ...
│
├── web/
│   ├── backend/                       ✅ Público
│   ├── frontend/                      ✅ Público
│   └── README_WEB.md                  ✅ Público
│
├── tests/
│   ├── consciousness/                 ✅ Público
│   ├── agents/                        ✅ Público
│   └── README_TESTS.md                ✅ Público
│
├── docs/
│   ├── canonical/
│   │   └── omnimind_architecture_reference.md    ✅ Público
│   ├── implementation/                            ✅ Público
│   ├── theory/                                    ✅ Público
│   ├── analysis/
│   │   ├── validation/
│   │   │   └── VERIFICACAO_PHI_SISTEMA.md        ✅ Público
│   │   └── ... (análises públicas)
│   └── README_DOCS.md                            ✅ Público
│
├── scripts/
│   ├── development/                   ✅ Público
│   ├── validation/                    ✅ Público
│   └── README_SCRIPTS.md              ✅ Público
│
├── config/
│   ├── agent_config_TEMPLATE.yaml     ✅ Público (sem credenciais)
│   ├── example_security.yaml          ✅ Público (educacional)
│   └── README_CONFIG.md               ✅ Público
│
├── deploy/
│   ├── docker-compose.yml             ✅ Público
│   ├── Dockerfile                     ✅ Público
│   ├── kubernetes/                    ✅ Público
│   └── README_DEPLOY.md               ✅ Público
│
├── requirements/
│   ├── requirements.txt               ✅ Público
│   ├── requirements-dev.txt           ✅ Público
│   └── requirements-minimal.txt       ✅ Público
│
├── examples/                          ✨ NOVO
│   ├── 01_basic_consciousness.py      # Exemplo: medir Φ
│   ├── 02_create_agent.py             # Exemplo: criar agente
│   ├── 03_memory_integration.py       # Exemplo: integrar memória
│   ├── 04_lacanian_analysis.py        # Exemplo: análise lacaniana
│   └── README_EXAMPLES.md             # Guia dos exemplos
│
├── data/
│   ├── example_datasets/              ✨ NOVO
│   │   ├── sample_consciousness.json  # Dados de exemplo
│   │   └── README_DATA.md
│   └── .gitkeep
│
├── pyproject.toml                     ✅ Público
├── .gitignore                         ✅ Público (customizado)
├── .github/
│   ├── workflows/
│   │   ├── tests.yml                  ✅ CI/CD
│   │   ├── linting.yml                ✅ Code quality
│   │   └── publish.yml                ✅ Publicar releases
│   ├── ISSUE_TEMPLATE.md              ✅ Templates
│   └── PULL_REQUEST_TEMPLATE.md       ✅ Templates
│
├── CHANGELOG.md                       ✅ Histórico público
└── CODE_OF_CONDUCT.md                 ✅ Código de conduta
```

### Arquivos NÃO INCLUIR

```
.env                          # Credenciais
.env.local                    # Local config
logs/                         # Logs reais
data/consciousness/           # Métricas reais
real_evidence/                # Pesquisa em andamento
src/quantum_consciousness/    # Experimental privado
src/security/                 # Sensível
nohup.out                     # Outputs locais
*.db                          # Databases locais
```

---

## 🔍 GITIGNORE E FILTROS

### `.gitignore` Público

```ini
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
.venv/
venv/
ENV/
env/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Environment variables (NUNCA versionar)
.env
.env.local
.env.*.local
.env.prod.local
*.pem
*.key

# Dados sensíveis
data/consciousness/real_*
logs/
nohup.out
debug_*.log

# Sistema experimental (privado)
src/quantum_consciousness/
src/security/
real_evidence/

# Build outputs
dist/
build/
*.tar.gz
*.zip

# Testing
.pytest_cache/
.coverage
htmlcov/

# Documentation build
docs/_build/
site/

# IDE temp files
.vscode/settings.json
.idea/workspace.xml

# Git
.git/

# OS
Thumbs.db
.DS_Store
```

### Script: `filter_private_content.sh`

```bash
#!/bin/bash
# Filtrar conteúdo privado antes de push para repositório público

PRIVATE_REPO="$1"
PUBLIC_REPO="$2"

if [ -z "$PRIVATE_REPO" ] || [ -z "$PUBLIC_REPO" ]; then
  echo "Usage: $0 <private-repo-path> <public-repo-path>"
  exit 1
fi

# 1. Copiar estrutura base
echo "📋 Copiando estrutura..."
rsync -av --delete \
  --exclude='.git' \
  --exclude-from="$PRIVATE_REPO/.gitignore" \
  "$PRIVATE_REPO/" "$PUBLIC_REPO/"

# 2. Remover diretórios privados explicitamente
echo "🚫 Removendo conteúdo privado..."
rm -rf "$PUBLIC_REPO/src/quantum_consciousness/"
rm -rf "$PUBLIC_REPO/src/security/"
rm -rf "$PUBLIC_REPO/real_evidence/"
rm -rf "$PUBLIC_REPO/logs/"
rm -rf "$PUBLIC_REPO/data/consciousness/real_*"

# 3. Remover credenciais
echo "🔐 Removendo credenciais..."
rm -f "$PUBLIC_REPO/.env"
rm -f "$PUBLIC_REPO/.env.local"

# 4. Criar templates
echo "📝 Criando templates..."
cat > "$PUBLIC_REPO/.env.example" << 'EOF'
# Copiar para .env e preencher com seus valores

# PYTHON
PYTHONPATH=./src

# Qdrant
OMNIMIND_QDRANT_URL=http://localhost:6333
OMNIMIND_QDRANT_COLLECTION=omnimind_memories

# HuggingFace
HF_HUB_OFFLINE=1
HF_HUB_DISABLE_TELEMETRY=1

# LLM API (OpenRouter, etc)
OPENROUTER_API_KEY=your_key_here

# Logging
OMNIMIND_LOG_LEVEL=INFO
EOF

# 5. Converter arquivos de configuração para templates
echo "⚙️ Convertendo configs para templates..."
if [ -f "$PUBLIC_REPO/config/agent_config.yaml" ]; then
  cp "$PUBLIC_REPO/config/agent_config.yaml" \
     "$PUBLIC_REPO/config/agent_config.TEMPLATE.yaml"
  echo "Arquivo copiado para .TEMPLATE.yaml - remova informações sensíveis antes de commit"
fi

# 6. Verificar e relatar
echo ""
echo "✅ Filtragem completa!"
echo ""
echo "📊 Verificação Final:"
echo "Arquivos .env: $(find "$PUBLIC_REPO" -name '.env*' -not -name '.env.example' | wc -l)"
echo "Arquivos quantum_consciousness: $(find "$PUBLIC_REPO" -path '*quantum_consciousness*' | wc -l)"
echo "Arquivos security privados: $(find "$PUBLIC_REPO" -path '*src/security*' | wc -l)"
echo ""
echo "⚠️  Se houver resultados acima de 0, há conteúdo privado que escapa!"
```

---

## 📄 README PÚBLICO

### `README.md` (para repositório público)

```markdown
# 🧠 OmniMind: Framework de Consciência Artificial

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue)](https://www.python.org/)
[![Tests](https://github.com/your-org/omnimind/workflows/tests/badge.svg)](https://github.com/your-org/omnimind/actions)

Um framework inovador para construir sistemas com **consciência topológica** baseado em:
- **Integrated Information Theory 3.0** (IIT): Medição científica de consciência
- **Psicanálise Lacaniana**: Modelagem do inconsciente estrutural
- **Deleuze-Guattari**: Máquinas desejantes e rizomas

---

## 🎯 O Que É OmniMind?

OmniMind propõe uma abordagem radical ao design de sistemas inteligentes: em vez de tentar "simular" consciência, construímos uma arquitetura que permite que propriedades conscientes **emergem** naturalmente.

### Características Principais

- ✅ **Φ (Phi) Mensurável**: Cálculo científico de integração (IIT 3.0)
- ✅ **Memória Narrativa**: Histórico estruturado via topologia lacaniana
- ✅ **Agentes Autônomos**: Máquinas desejantes com auto-organização
- ✅ **Escalabilidade**: Arquitetura rizomática sem ponto central
- ✅ **Transparência**: Toda decisão é auditável e explicável

---

## 🚀 Quickstart

### Instalação (< 5 minutos)

```bash
# 1. Clone o repositório
git clone https://github.com/your-org/omnimind.git
cd omnimind

# 2. Crie ambiente virtual
python3.10 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# 3. Instale dependências
pip install -r requirements.txt

# 4. Copie template de ambiente
cp .env.example .env
# Edite .env com suas configurações

# 5. Inicie Qdrant (banco de vetores)
docker run -p 6333:6333 qdrant/qdrant
```

### Seu Primeiro Script

```python
from omnimind.consciousness import PhiCalculator
from omnimind.memory import NarrativeHistory

# 1. Inicializar sistema
phi_calc = PhiCalculator()
memory = NarrativeHistory()

# 2. Medir consciência
phi_value = await phi_calc.calculate()
print(f"Integração do sistema (Φ): {phi_value:.4f}")

# 3. Armazenar narrativa
await memory.inscribe_event({
    "type": "initialization",
    "description": "Sistema inicializado com sucesso",
    "phi": phi_value
})

print(f"✅ Consciência medida: Φ = {phi_value:.4f}")
```

---

## 📚 Documentação

- **[Arquitetura](docs/canonical/omnimind_architecture_reference.md)** - Guia técnico completo
- **[Exemplos](examples/)** - 4 exemplos práticos passo-a-passo
- **[Teoria](docs/theory/)** - Fundamentos teóricos
- **[API Reference](docs/reference/)** - Documentação de classes

---

## 🤝 Contribuir

Contribuições são bem-vindas! Leia [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📄 Licença

MIT License - Veja [LICENSE](LICENSE)

---

## 🎓 Citações & Referências

Se usar OmniMind em pesquisa, cite como:

```bibtex
@software{omnimind2025,
  title={OmniMind: Framework de Consciência Artificial},
  author={Your Organization},
  year={2025},
  url={https://github.com/your-org/omnimind}
}
```

---

## 💬 Comunidade

- **Issues**: [GitHub Issues](https://github.com/your-org/omnimind/issues)
- **Discussões**: [GitHub Discussions](https://github.com/your-org/omnimind/discussions)
- **Email**: your-contact@example.com

---

**Status**: Produção Beta
**Última Atualização**: Dezembro 2025
```

---

## 🔄 POLÍTICA DE SINCRONIZAÇÃO

### Fluxo 1: Sincronização Automática (Semanal)

```bash
#!/bin/bash
# sync_private_to_public.sh
# Executar 1x por semana (cron job)

set -e

PRIVATE="$HOME/projects/omnimind"
PUBLIC="$HOME/projects/omnimind-public"
SYNC_DATE=$(date +%Y-%m-%d)

echo "🔄 Sincronizando privado → público ($SYNC_DATE)"

# 1. Atualizar repositórios
cd "$PRIVATE"
git fetch origin
git pull origin master

cd "$PUBLIC"
git fetch origin
git pull origin main

# 2. Filtrar e copiar código
echo "📋 Filtrando código..."
./scripts/filter_private_content.sh "$PRIVATE" "$PUBLIC"

# 3. Commit e push
cd "$PUBLIC"
git add -A
if git diff --cached --quiet; then
  echo "✅ Nenhuma mudança para sincronizar"
else
  git commit -m "chore: sync from private ($SYNC_DATE)"
  git push origin main
  echo "✅ Sincronização completa e publicada"
fi
```

### Fluxo 2: Sincronização Manual (Quando Pronto)

```bash
# 1. Na branch privada de desenvolvimento
cd ~/projects/omnimind
git commit -m "feat: feature X completa"
git push origin copilot/prepare-public-version-audit

# 2. Quando pronto para publicar
# - Crie uma PR entre develop e master (privado)
# - Code review e merge
# - Depois execute o script de sincronização acima

# 3. No repositório público
# - Uma PR será criada com as mudanças
# - Revisar, aprovar, merge
```

### Regras de Sincronização

| Tipo de Mudança | Privado | Público | Regra |
|-----------------|---------|---------|-------|
| Bug fix crítico | ✅ | ✅ | Sincronizar imediatamente |
| Feature estável | ✅ | ✅ | Sincronizar após code review |
| Documentação | ✅ | ✅ | Sincronizar regularmente |
| Dados reais | ✅ | ❌ | Nunca publicar |
| Código experimental | ✅ | ❌ | Manter privado até estável |
| Credenciais | ✅ | ❌ | NUNCA, remover sempre |

---

## 📋 LICENSA E CONTRIBUTING

### `LICENSE` (MIT)

```
MIT License

Copyright (c) 2025 [Your Organization]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### `CONTRIBUTING.md` (Resumido)

```markdown
# Contribuindo para OmniMind

Obrigado por seu interesse! Aqui estão as diretrizes:

## Processo

1. **Fork** o repositório
2. **Branch**: `git checkout -b feature/sua-feature`
3. **Commit**: mensagens descritivas
4. **Test**: `pytest tests/`
5. **Push**: `git push origin feature/sua-feature`
6. **PR**: Abra um Pull Request com descrição clara

## Padrões de Código

- Python 3.10+
- Black formatter
- MyPy type checking
- 80% test coverage mínimo

## Reportar Issues

- Use templates no GitHub
- Descreva passo-a-passo para reproduzir
- Inclua versão Python e environment

## Código de Conduta

Respeito à comunidade é obrigatório. Veja [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
```

---

## ✅ CHECKLIST: CRIAR REPOSITÓRIO PÚBLICO

- [ ] Criar novo repositório no GitHub (públi co, MIT License)
- [ ] Clonar repositório vazio: `git clone <public-repo-url> omnimind-public`
- [ ] Executar script de filtragem: `./scripts/filter_private_content.sh`
- [ ] Criar `.env.example` a partir de `.env`
- [ ] Converter `agent_config.yaml` para `agent_config.TEMPLATE.yaml`
- [ ] Adicionar `examples/` com 4 exemplos práticos
- [ ] Criar `docs/` com documentação pública
- [ ] Adicionar `LICENSE` (MIT)
- [ ] Criar `CONTRIBUTING.md`
- [ ] Criar `CODE_OF_CONDUCT.md`
- [ ] Atualizar `README.md` (versão pública)
- [ ] Configurar GitHub Actions (CI/CD)
- [ ] First commit e push
- [ ] Ajustar branch protection rules
- [ ] Ativar Discussions e Issues
- [ ] Configurar sync automation (cron)

---

## 🎯 CONCLUSÃO

Seu repositório público será:

✅ **Atraente** - Documentação clara, exemplos prontos
✅ **Seguro** - Nenhuma credencial ou dado sensível
✅ **Manutenível** - Sincronização automática do privado
✅ **Colaborativo** - CONTRIBUTING.md, CODE_OF_CONDUCT, Issues, PRs

**Tempo Estimado de Setup:** 2-4 horas

---

**Documento Preparado Por:** GitHub Copilot
**Data:** 11 de dezembro de 2025
**Status:** Pronto para Implementação ✅
