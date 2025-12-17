# 🚀 Criando Repositório Público do OmniMind

## Resumo Executivo

Este guia cria um **repositório público limpo** com:
- ✅ Código de produção (`src/`)
- ✅ Suite de testes (`tests/`)
- ✅ Scripts canônicos (`scripts/canonical/`, `scripts/services/`)
- ✅ Documentação técnica (`docs/SERVICE_UPDATE_PROTOCOL.md`, etc)
- ✅ Configurações essenciais (`config/`, `requirements/`)

**EXCLUI:**
- ❌ Data, modelos, logs
- ❌ Documentação de pesquisa, artigos, ideias
- ❌ Notebooks Jupyter, resultados IBM
- ❌ Arquivos temporários, backups

## Como Usar

### Opção 1: Script Automático (Recomendado)

```bash
cd /home/fahbrain/projects/omnimind

# Criar repositório público em /tmp/omnimind-public
./scripts/create_public_repo.sh /tmp/omnimind-public

# Ou com URL do GitHub (opcional)
./scripts/create_public_repo.sh /tmp/omnimind-public https://github.com/seu-usuario/OmniMind.git
```

**O que o script faz:**
1. ✅ Cria diretório limpo
2. ✅ Inicializa git
3. ✅ Copia `src/`, `tests/`, `scripts/`
4. ✅ Copia documentação técnica
5. ✅ Cria `.gitignore` production
6. ✅ Faz commit inicial
7. ✅ Configura remote GitHub (opcional)

### Opção 2: Passo a Passo Manual

```bash
# 1. Criar diretório
mkdir -p /tmp/omnimind-public
cd /tmp/omnimind-public

# 2. Inicializar git
git init
git branch -M main

# 3. Copiar produção
cp -r /home/fahbrain/projects/omnimind/src .
cp -r /home/fahbrain/projects/omnimind/tests .
cp -r /home/fahbrain/projects/omnimind/scripts/canonical scripts/canonical
cp -r /home/fahbrain/projects/omnimind/scripts/services scripts/services
cp -r /home/fahbrain/projects/omnimind/config .
cp -r /home/fahbrain/projects/omnimind/requirements .
cp -r /home/fahbrain/projects/omnimind/docs .

# 4. Copiar arquivos raiz
cp /home/fahbrain/projects/omnimind/pyproject.toml .
cp /home/fahbrain/projects/omnimind/README.md .
cp /home/fahbrain/projects/omnimind/LICENSE .
cp /home/fahbrain/projects/omnimind/CITATION.cff .

# 5. Criar .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*.pyo
.pytest_cache/
.mypy_cache/
.coverage
*.egg-info/
dist/
build/

# Virtual environments
.venv/
venv/
env/

# IDE
.vscode/
.idea/
*.swp

# System
.DS_Store
Thumbs.db

# Environment
.env
config/dashboard_auth.json

# Data & Models (NUNCA)
data/
models/
logs/
*.log

# Development (NUNCA)
docs/research/
notebooks/
ibm_results/
real_evidence/
archive/
backups_compressed/
EOF

# 6. Fazer commit
git add .
git commit -m "Initial commit: OmniMind public repository"
```

## Validação de Segurança

**Antes de fazer push, validar:**

```bash
# Usar script de validação
./scripts/validate_public_repo.sh /tmp/omnimind-public

# Ou manual:
cd /tmp/omnimind-public

# Procurar por dados sensíveis
grep -r "api_key\|password\|token" . --include="*.py" --include="*.yaml"

# Verificar tamanho dos arquivos
find . -type f -size +50M

# Verificar git antes de push
git status
git log --oneline -5
```

## Publicar no GitHub

### Primeira vez:

```bash
# Criar repositório em https://github.com/novo (deixar vazio, sem README)
# Copiar URL do HTTPS

cd /tmp/omnimind-public

# Adicionar remote
git remote add origin https://github.com/seu-usuario/OmniMind.git

# Fazer push
git push -u origin main

# Verificar
git remote -v
```

### Atualizações futuras:

```bash
cd /tmp/omnimind-public

# Ou se clonou:
git pull origin main

# Fazer mudanças, testar, depois:
git add .
git commit -m "Descrição clara"
git push origin main
```

## Manter em Sincronia

Para manter repo público atualizado com mudanças de código:

```bash
# No repo PRIVADO (/home/fahbrain/projects/omnimind)
# Depois de mudanças importantes:

cd /home/fahbrain/projects/omnimind
git add .
git commit -m "Change description"

# Sincronizar com PUBLIC
cd /tmp/omnimind-public
git pull ../../../home/fahbrain/projects/omnimind.git main
# Ou se tem remote configurado:
git push origin main
```

## Arquitetura Final

```
REPOSITÓRIO PRIVADO (arquivo + desenvolvimento)
/home/fahbrain/projects/omnimind
├── src/                      ← Copiado para público
├── tests/                    ← Copiado para público
├── scripts/canonical/        ← Copiado para público
├── scripts/services/         ← Copiado para público
├── docs/                     ← Parcial (técnica apenas)
├── config/                   ← Copiado para público
├── requirements/             ← Copiado para público
├── data/                     ← PRIVADO
├── models/                   ← PRIVADO
├── notebooks/                ← PRIVADO
├── ibm_results/              ← PRIVADO
├── real_evidence/            ← PRIVADO
├── docs/research/            ← PRIVADO
└── archive/                  ← PRIVADO

REPOSITÓRIO PÚBLICO (limpo + produção)
GitHub: https://github.com/seu-usuario/OmniMind
├── src/                      ✅
├── tests/                    ✅
├── scripts/                  ✅
├── docs/                     ✅ (técnica)
├── config/                   ✅
├── requirements/             ✅
├── README.md                 ✅
├── LICENSE                   ✅
└── CITATION.cff             ✅
```

## Checklist Antes de Push

- [ ] `.gitignore` contém `data/`, `models/`, `notebooks/`, `ibm_results/`
- [ ] Nenhum arquivo `.env` com credenciais
- [ ] Nenhuma API key / password / token
- [ ] Todos os arquivos Python compilam (`python -m py_compile src/**/*.py`)
- [ ] Tests passam localmente
- [ ] Tamanho total < 500MB
- [ ] `git status` está limpo
- [ ] Commit message é descritiva

## Troubleshooting

### "Erro: arquivo muito grande"
```bash
# Remover antes de commit
git rm --cached arquivo_grande.bin
echo "arquivo_grande.bin" >> .gitignore
git commit -m "Remove large file"
```

### "Erro: credenciais no histórico"
```bash
# Se credencial foi committed:
git log -p arquivo.py  # encontrar commit
git revert <commit-hash>
git push origin main
```

### "Sincronização com privado"
```bash
# Se mudanças em privado não estão em público:
cd /tmp/omnimind-public
git pull /home/fahbrain/projects/omnimind main
# Ou adicionar como remote:
git remote add private /home/fahbrain/projects/omnimind
git fetch private && git merge private/main
```

## Próximos Passos

1. ✅ Criar repositório público com script
2. ✅ Validar com `validate_public_repo.sh`
3. ✅ Testar localmente (build, testes)
4. ✅ Criar no GitHub
5. ✅ Fazer push: `git push -u origin main`
6. ✅ Configurar CI/CD (GitHub Actions)
7. ✅ Documentar setup local (README.md)

## Perguntas Frequentes

**P: Posso atualizar o repo público depois?**
R: Sim! Adicione como remoto e use `git push`.

**P: E se esquecer de remover algo sensível?**
R: Use `git rm --cached` e `git commit --amend` (se não fez push).

**P: Vou perder o histórico privado?**
R: Não! O repo privado continua em `/home/fahbrain/projects/omnimind`.

**P: Como sincronizar mudanças?**
R: Faça em privado, depois copie arquivos ou use `git fetch` do remoto privado.

---

**Autor:** Fabrício da Silva
**Data:** 16 de Dezembro de 2025
**Status:** ✅ Pronto para execução
