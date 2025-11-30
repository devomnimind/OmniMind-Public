# 📋 COMANDOS RÁPIDOS PARA TESTAR O NOVO REPO

Copie e cole estes comandos para verificar que tudo está funcionando:

## ✅ Teste 1: Verificar Repo no GitHub

```bash
gh repo view devomnimind/omnimind-consciousness-study
```

Deve mostrar: nome, descrição, URL, data.

## ✅ Teste 2: Clone Fresh (Simular novo usuário)

```bash
cd /tmp
rm -rf test-omnimind-consciousness
git clone https://github.com/devomnimind/omnimind-consciousness-study.git test-omnimind-consciousness
cd test-omnimind-consciousness

# Verificar estrutura
echo "=== ESTRUTURA ===" && tree -L 2

# Verificar arquivos essenciais
echo "=== ESSENCIAIS ===" && ls -la | grep -E '(README|LICENSE|requirements|CITATION|pyproject)'

# Verificar real_evidence
echo "=== DADOS ===" && ls real_evidence/ablations/

# Verificar src/consciousness
echo "=== SRC ===" && ls src/consciousness/ | head -10
```

## ✅ Teste 3: Imports

```bash
cd /tmp/test-omnimind-consciousness
python3 -c "
from src.consciousness.integration_loop import IntegrationLoop
from src.consciousness.shared_workspace import SharedWorkspace
print('✅ Imports OK')
print('✅ Framework is ready')
"
```

## ✅ Teste 4: Setup & Run (Optional - takes 60 min on GPU)

```bash
cd /tmp/test-omnimind-consciousness

# Setup
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Quick import test
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')
from src.consciousness.integration_loop import IntegrationLoop
print("✅ Framework ready to run ablations")
PYEOF

# Run mini-ablation (change num_cycles=10 for 2-min test)
python3 scripts/run_ablations_corrected.py
```

## 📊 Resultado esperado

Se tudo funcionar:
- ✅ Nenhum erro de importação
- ✅ Estrutura de pastas clara
- ✅ Dados presentes em real_evidence/
- ✅ Script pronto para rodar

---

## 🔍 Verificação Rápida (Sem Clone)

Se só quiser confirmar que o repo existe:

```bash
# Via GitHub CLI
gh repo view devomnimind/omnimind-consciousness-study --json name,description,url

# Via curl (sem autenticação)
curl -s https://api.github.com/repos/devomnimind/omnimind-consciousness-study | jq '{name: .name, description: .description, url: .html_url}'
```

---

## ✅ CHECKLIST FINAL

Faça isso antes de publicar papers:

- [ ] `gh repo view devomnimind/omnimind-consciousness-study` retorna info correta
- [ ] `git clone` funciona sem erro
- [ ] `README.md` aparece claro no navegador
- [ ] `src/consciousness/` tem 16 arquivos
- [ ] `real_evidence/ablations/` tem dados JSON
- [ ] `requirements.txt` pode ser instalado com pip
- [ ] Python imports funcionam
- [ ] Nenhum __pycache__ ou .pyc visível

Se tudo passar ✅, está pronto para anunciar!

---

## 🚀 Quando Estiver Pronto

Coloque isso nos papers no arXiv:

```
Reproducible code and data available at:
https://github.com/devomnimind/omnimind-consciousness-study

To reproduce:
git clone https://github.com/devomnimind/omnimind-consciousness-study.git
cd omnimind-consciousness-study
pip install -r requirements.txt
python3 scripts/run_ablations_corrected.py
```

---

**Data:** 30 Nov 2025  
**Status:** Repo está live e pronto para testes
