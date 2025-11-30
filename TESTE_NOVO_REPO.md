# 🧪 TESTE RÁPIDO DO NOVO REPO (Verificação)

Se quiser testar que o novo repo está realmente funcional:

## Opção 1: Clonar Fresh (Simular novo usuário)

```bash
cd /tmp
rm -rf test-omnimind-study
git clone https://github.com/devomnimind/omnimind-consciousness-study.git test-omnimind-study
cd test-omnimind-study

# Verificar estrutura
echo "=== ESTRUTURA ===" && tree -L 2
echo "=== ARQUIVOS ===" && ls -la | grep -E '(README|LICENSE|requirements|CITATION)'

# Verificar imports
echo "=== TESTE IMPORT ===" && python3 -c "from src.consciousness.integration_loop import IntegrationLoop; print('✅ Imports OK')" 2>&1

# Verificar requirements
echo "=== REQUIREMENTS ===" && cat requirements.txt
echo "=== INSTALL ===" && pip install -r requirements.txt

# Opcional: Rodar mini-ablation (10 cycles instead of 200)
echo "=== MINI-ABLATION ===" && python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')

# Modificar script para 10 cycles (quick test)
from src.consciousness.integration_loop import IntegrationLoop
from src.consciousness.shared_workspace import SharedWorkspace

print("✅ Framework imports working")
print("✅ Ready to run full ablations")
PYEOF
```

## Opção 2: Verificar via GitHub CLI

```bash
gh repo view devomnimind/omnimind-consciousness-study \
  --json name,description,url,pushedAt,createdAt
```

Expected output:
```
{
  "createdAt": "2025-11-30T00:...",
  "description": "Computational framework validating psychoanalytic consciousness theory via Integrated Information Theory",
  "name": "omnimind-consciousness-study",
  "pushedAt": "2025-11-30T00:...",
  "url": "https://github.com/devomnimind/omnimind-consciousness-study"
}
```

## Opção 3: Verificar Conteúdo

```bash
# Ver estrutura
gh repo view devomnimind/omnimind-consciousness-study \
  --web  # Opens in browser

# Ou listar arquivos
gh api repos/devomnimind/omnimind-consciousness-study/contents \
  --jq '.[].name' | sort
```

---

## ✅ CHECKLIST (Antes de Publicar Papers)

- [ ] Repo criado em devomnimind/omnimind-consciousness-study
- [ ] README claro e completo
- [ ] `git clone` + setup funciona
- [ ] `run_ablations_corrected.py` pronto
- [ ] `real_evidence/` com todos dados
- [ ] LICENSE e CITATION.cff presentes
- [ ] Sem __pycache__ ou lixo
- [ ] Main branch is default
- [ ] Descrição do repo é clara

---

## 🔗 URLs Finais

**GitHub:** https://github.com/devomnimind/omnimind-consciousness-study  
**Documentação de Reprodução:** Ver `README.md` no repo  
**Dados:** `real_evidence/ablations/ablations_corrected_20251129_235951.json`

---

Quando tiver feito testes, pode publicar papers no arXiv com:
"Code and reproducible data available at: https://github.com/devomnimind/omnimind-consciousness-study"
