# OmniMind Sync Protocol: PRIVATE ↔ PUBLIC

**Documento de referência rápida para sincronizar mudanças entre repositórios**

---

## 📋 Resumo Executivo

| Aspecto | PRIVATE (OmniMind) | PUBLIC (OmniMind-Core-Papers) |
|--------|-------------------|------------------------------|
| **Visibilidade** | PRIVATE | PUBLIC (MIT + CC BY 4.0) |
| **Conteúdo** | Tudo | Apenas research-core + documentação |
| **Fluxo** | Base (sempre sincroniza daqui) | Subset (apenas mudanças aprovadas) |
| **Dashboard/UI** | ✅ Incluso | ❌ Proprietary (não vai) |
| **Quantum algoritmos avançados** | ✅ Incluso | ❌ Proprietary (não vai) |
| **Métricas e consciência** | ✅ Incluso | ✅ Research-core (vai) |
| **Daemon/MCP** | ✅ Incluso | ❌ Proprietary (não vai) |
| **Testes** | ✅ Todos | ✅ Research tests (vai) |

---

## 🔄 Workflow de Sincronização

### Passo 1: Fazer Mudanças no PRIVATE
```bash
cd ~/projects/omnimind
# ... edite código ...
git add .
git commit -m "descrição"
git push origin master
```

### Passo 2: Validar Políticas

**Pergunte-se:**
- ✅ Afeta módulos de consciousness/metacognition?
- ✅ Afeta testes research?
- ✅ Afeta documentação técnica?
- ❌ É código de dashboard?
- ❌ É quantum proprietary?
- ❌ É daemon/MCP?

**Se SIM para alguma pergunta com ✅** → Proceda com sincronização

### Passo 3: Preparar Mudanças para PUBLIC

#### Opção A: Copiar Arquivos Específicos
```bash
# Copiar módulo inteiro
cp -r ~/projects/omnimind/src/metrics ~/projects/OmniMind-Core-Papers/src/

# Ou copiar arquivo específico
cp ~/projects/omnimind/src/consciousness/production_consciousness.py \
   ~/projects/OmniMind-Core-Papers/src/consciousness/
```

#### Opção B: Cherry-pick via Git
```bash
cd ~/projects/OmniMind-Core-Papers
git remote add private ~/projects/omnimind
git fetch private master

# Cherry-pick commits específicos
git cherry-pick <commit-hash>
```

### Passo 4: Validar Localmente

**Usar o script de validação do Papers:**

```bash
cd ~/projects/OmniMind-Core-Papers

# Validação rápida (2 testes críticos)
bash validate_sync.sh quick

# Validação completa (todas as suites)
bash validate_sync.sh

# Validação de módulo específico
bash validate_sync.sh consciousness
bash validate_sync.sh ethics
```

**Esperado:**
```
✅ SYNC VALIDATION: PASSED

Next steps:
  1. Review changes: git diff --cached
  2. Commit: git commit -m 'Message'
  3. Push: git push origin master
```

### Passo 5: Revisar Mudanças

```bash
# Ver exatamente o que vai subir
git diff HEAD~1

# Verificar se não há credenciais/proprietary
grep -r "OMNIMIND_\|quantum\|dashboard\|mcp\|daemon" src/
```

### Passo 6: Commit com Mensagem Clara

```bash
git commit -m "Fix: Add/Update module X for paper reproducibility

Description of what changed and why.

- Item 1
- Item 2

Related to paper: [Paper name if applicable]"
```

### Passo 7: Push para PUBLIC

```bash
git push origin master
```

**GitHub Actions rodará automaticamente:**
- ✅ Testes (300+ tests)
- ✅ Coverage report
- ✅ Linting

---

## 🚫 Checklist: O que NÃO sincroniza

- ❌ `web/frontend/` → Dashboard é proprietary
- ❌ `src/quantum_consciousness/` (versão avançada) → Proprietary
- ❌ `src/api/routes/daemon.py` → Daemon é proprietary
- ❌ `VSCODE_ENV_SETUP.md`, `DASHBOARD_REPAIR_COMPLETE.md` → Dev docs
- ❌ `requirements-ci.txt` → CI-specific
- ❌ `.env`, credentials, tokens → NUNCA
- ❌ `simple_backend.py` se tiver quantum/proprietary

**Regra de Ouro:** Se está em `src/consciousness/` ou `src/metacognition/` → **PODE IR**

---

## ✅ Checklist: O que SIM sincroniza

- ✅ `src/consciousness/` → Research-core (MIT)
- ✅ `src/metacognition/` → Research-core (MIT)
- ✅ `src/metrics/` → Metrics para papers (MIT)
- ✅ `tests/` → Tests de reproducibility
- ✅ `scripts/` → Scripts para reproduzir papers
- ✅ `docs/` → Documentação técnica
- ✅ `README.md`, `CHANGELOG.md` → Docs técnicas
- ✅ Fixes em code de consciousness (bugs, optimizações)

---

## 📊 Histórico de Syncs Recentes

| Data | Mudança | Status | Notas |
|------|---------|--------|-------|
| 29-Nov-2025 | Adicionado `src/metrics/` | ✅ SYNCED | Corrigiu 2 testes falhados no Papers |
| 29-Nov-2025 | Criado `validate_sync.sh` | ✅ SYNCED | Protocolo de validação pré-push |

---

## 🔍 Troubleshooting

### Testes falhando no Papers após sync

```bash
# 1. Validar localmente primeiro
cd ~/projects/OmniMind-Core-Papers
bash validate_sync.sh

# 2. Se falhar, ver erro específico
bash validate_sync.sh consciousness --verbose

# 3. Copiar módulo faltante do PRIVATE
cp -r ~/projects/omnimind/src/metrics ~/projects/OmniMind-Core-Papers/src/
```

### Arquivo foi sincronizado mas não deveria

```bash
# Remover do git (mas manter localmente)
git rm --cached <arquivo>
git commit -m "Remove: <arquivo> (proprietary, não deveria estar no PUBLIC)"

# Adicionar ao .gitignore do Papers
echo "<arquivo>" >> .gitignore
```

### Conflict entre PRIVATE e PUBLIC

```bash
# NUNCA fazer force-push em PUBLIC
# Em vez disso:

# 1. Rebase local em cima do PUBLIC
git fetch origin
git rebase origin/master

# 2. Se houver conflitos, resolver manualmente
git mergetool

# 3. Push normalmente
git push origin master
```

---

## 📞 Contato & Dúvidas

- **Repositório PRIVATE:** `https://github.com/devomnimind/OmniMind.git`
- **Repositório PUBLIC:** `https://github.com/devomnimind/OmniMind-Core-Papers.git`
- **Script de validação:** `~/projects/OmniMind-Core-Papers/validate_sync.sh`

---

**Última atualização:** 29-Nov-2025  
**Próxima revisão:** Quando adicionar novos módulos ao PUBLIC
