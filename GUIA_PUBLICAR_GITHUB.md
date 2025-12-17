# 🚀 Guia: Publicar OmniMind na Organização devomnimind

**Data:** 17 de Dezembro de 2025
**Organização:** https://github.com/devomnimind/
**Repositório Público:** OmniMind-Public
**Repositório Privado:** OmniMind (mantido como arquivo)

---

## 📋 Resumo Executivo

Este guia orienta sobre como publicar o OmniMind como repositório público limpo na organização `devomnimind`, excluindo:
- ❌ Dados grandes (data/, models/, logs/)
- ❌ Documentação de pesquisa (ideias, artigos científicos)
- ❌ Experimentos e notebooks
- ❌ Backups e artefatos temporários

**Incluindo apenas:**
- ✅ Código-fonte (`src/`)
- ✅ Suite de testes (`tests/`)
- ✅ Scripts canônicos (`scripts/canonical/`, `scripts/services/`)
- ✅ Documentação técnica (SERVICE_UPDATE_PROTOCOL, GRACEFUL_RESTART_GUIDE)
- ✅ Configurações essenciais (`config/`, `requirements/`)
- ✅ Arquivo de licença e citação

---

## 🎯 Passo a Passo Rápido

### 1. Gerar Repositório Público Limpo

```bash
cd /home/fahbrain/projects/omnimind

# Criar repositório público em /tmp
./scripts/setup_public_repo.sh

# Ou especificar outro caminho
./scripts/setup_public_repo.sh /tmp/omnimind-public
```

**Resultado:** Um diretório limpo com apenas código essencial

### 2. Validar o Repositório

```bash
# Entrar no diretório gerado
cd /tmp/omnimind-public-* # (use a data gerada)

# Verificar tamanho
du -sh .

# Listar arquivos principais
ls -la

# Testar imports
python3 -c "from src.consciousness.topological_phi import PhiCalculator; print('✅ Imports OK')"
```

### 3. Criar Repositório no GitHub

**Na organização devomnimind:**

1. Abrir: https://github.com/devomnimind
2. Novo repositório (+)
3. Nome: `OmniMind-Public`
4. Descrição: "OmniMind Public Repository - Consciousness Framework"
5. **Public** ✅
6. Sem README inicial (usaremos o nosso)
7. Criar repositório

### 4. Fazer Push para GitHub

```bash
cd /tmp/omnimind-public-* # (entrar no diretório gerado)

# Configurar origem remota
git remote add origin https://github.com/devomnimind/OmniMind-Public.git

# Fazer push da branch main
git push -u origin main
```

**Resultado:** Repositório público em https://github.com/devomnimind/OmniMind-Public

---

## 📊 Comparação Repositórios

| Aspecto | Privado (omnimind) | Público (OmniMind-Public) |
|--------|-------------------|--------------------------|
| **Localização** | /home/fahbrain/projects/omnimind | github.com/devomnimind/OmniMind-Public |
| **Acesso** | Privado (você) | Público (todos) |
| **Tamanho** | ~35GB (com data/, models/, logs/) | ~500MB (só código + testes) |
| **Propósito** | Desenvolvimento + pesquisa | Produção limpa |
| **Documentação** | Tudo (ideias, artigos, etc) | Só técnica (SERVICE_UPDATE_PROTOCOL, etc) |
| **Atualizações** | Frequente | Após validação |

---

## 🔄 Workflow Recomendado

```
Desenvolvimento (Privado)
    ↓
    ├─ Fazer mudanças em /home/fahbrain/projects/omnimind
    ├─ Testar localmente
    ├─ Validar (black, flake8, mypy, pytest)
    ├─ Commit & Push (repositório privado)
    │
    └─ QUANDO PRONTO PARA PRODUÇÃO:
        ↓
        ├─ ./scripts/setup_public_repo.sh
        ├─ Validar qualidade
        ├─ git push para github.com/devomnimind/OmniMind-Public
        │
        └─ Repositório Público Atualizado ✅
```

---

## 🛡️ Checklist de Segurança

Antes de fazer push para público, verificar:

- [ ] **Sem credenciais?** (`grep -r "pass\|token\|key" .`)
- [ ] **Sem dados privados?** (`grep -r "fahbrain\|/home/" .`)
- [ ] **Sem arquivo grande?** (`du -sh .` < 1GB)
- [ ] **Testes passando?** (`python3 -m pytest tests/`)
- [ ] **Código limpo?** (`black --check src tests`)
- [ ] **Sem imports quebrados?** (`python3 -c "from src import *"`)
- [ ] **LICENSE presente?** (`cat LICENSE`)

---

## 📁 Estrutura do Repositório Público

```
OmniMind-Public/
├── src/                          # ✅ Código principal
│   ├── consciousness/
│   ├── quantum_consciousness/
│   ├── services/
│   └── ...
├── tests/                        # ✅ Suite de testes
├── scripts/                      # ✅ Scripts canônicos
│   ├── canonical/
│   ├── services/
│   └── testing/
├── docs/                         # ✅ Documentação técnica
│   └── technical/
│       ├── SERVICE_UPDATE_PROTOCOL.md
│       └── GRACEFUL_RESTART_GUIDE.md
├── config/                       # ✅ Configurações
├── requirements/                 # ✅ Dependências
├── README.md                     # ✅ Documentação principal
├── LICENSE                       # ✅ Licença
├── CITATION.cff                  # ✅ Metadados de citação
├── pyproject.toml               # ✅ Configuração Python
├── .gitignore                    # ✅ Production-ready
└── .git/                         # ✅ Histórico git limpo
```

---

## 🔗 URLs Importantes

- **Organização:** https://github.com/devomnimind/
- **Repositório Público (novo):** https://github.com/devomnimind/OmniMind-Public
- **Repositório Privado (arquivo):** /home/fahbrain/projects/omnimind
- **Documentação Técnica:** docs/technical/SERVICE_UPDATE_PROTOCOL.md

---

## 📞 Próximas Ações

1. ✅ Executar `./scripts/setup_public_repo.sh`
2. ✅ Validar qualidade (testes, imports)
3. ✅ Criar repositório em https://github.com/devomnimind/OmniMind-Public
4. ✅ Fazer push inicial (`git push -u origin main`)
5. ✅ Configurar branch protection (main)
6. ✅ Adicionar tópicos GitHub (consciousness, ai, framework)
7. ✅ Publicar releases do repositório privado
8. ✅ Configurar CI/CD (GitHub Actions)

---

**Status:** ✅ Pronto para publicação
**Última Atualização:** 17 de Dezembro de 2025
**Responsável:** Fabrício da Silva
