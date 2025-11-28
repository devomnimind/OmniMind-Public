# Guia de Validação Manual de Warnings e Timing

**⚠️ NÃO USE SCRIPTS AUTOMÁTICOS PARA CORREÇÃO**

Este documento descreve como **investigar manualmente** quaisquer problemas em warnings e timing.

---

## 🔍 Checklist de Validação

### 1. Antes de Executar Testes

```bash
# Verificar se logs antigos existem
ls -lh data/test_reports/pytest*.log

# AÇÃO MANUAL: Se quiser começar "limpo", você pode fazer:
# (Não é obrigatório, mas recomendado)
# DECIDA SE VAI DELETAR - não faça automaticamente!
# rm data/test_reports/pytest_full.log
```

### 2. Executar Testes COM RASTREAMENTO DE TEMPO

```bash
# Registrar hora de início
echo "Início: $(date -u +%Y-%m-%dT%H:%M:%SZ)" > /tmp/test_timing.log

# Executar testes (usar o comando padrão)
pytest tests/ -v --tb=short --cov=src --cov-report=term-missing \
  --cov-report=json:data/test_reports/coverage.json \
  --cov-report=html:data/test_reports/htmlcov \
  --maxfail=999 --durations=20 -W ignore::DeprecationWarning \
  2>&1 | tee data/test_reports/pytest_full.log

# Registrar hora de fim
echo "Fim: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> /tmp/test_timing.log
```

### 3. Analisar Warnings Manualmente

```bash
# Contar warnings reais (não nomes de testes)
grep '"level": "warning"' data/test_reports/pytest_full.log | wc -l

# Ver tipos de warnings
grep '"level": "warning"' data/test_reports/pytest_full.log | \
  grep -o '"event": "[^"]*"' | sort | uniq -c | sort -rn

# Verificar se são esperados
grep '"level": "warning"' data/test_reports/pytest_full.log | head -20
```

### 4. Validar Timing

```bash
# Ver timestamp do primeiro warning
grep '"timestamp"' data/test_reports/pytest_full.log | head -1

# Ver timestamp do último warning
grep '"timestamp"' data/test_reports/pytest_full.log | tail -1

# Ver tempo reportado pelo pytest
tail -5 data/test_reports/pytest_full.log | grep "passed"

# DECISÃO MANUAL: Compare os tempos
# - Se `pytest` diz 1h26m mas timestamps mostram 12min
#   → Há múltiplas sessões de teste no arquivo
#   → Decida se quer limpar ou manter ambas
```

### 5. Problemas Conhecidos e Soluções Seguras

#### Problema: Muitos Warnings (> 50)
```
❌ ERRADO: Usar script automático para "corrigir" warnings
✅ CERTO: 
   1. Investigar qual teste está causando
   2. Ler o código do teste
   3. Verificar se é comportamento esperado
   4. Decidir manualmente se é problema
   5. Fazer alteração manual e testar
```

#### Problema: Logging Não Limpo Entre Execuções
```
❌ ERRADO: rm data/test_reports/pytest_full.log (automático)
✅ CERTO:
   1. Verificar data de modificação: ls -l data/test_reports/pytest_full.log
   2. Se logs têm > 24h, pode ser seguro deletar
   3. Decidir SE QUER deletar
   4. Se deletar, fazer backup antes:
      cp data/test_reports/pytest_full.log /tmp/pytest_full.log.bak
   5. Depois deletar ou renomear
```

#### Problema: Discrepância de Tempo
```
✅ CERTO:
   1. Extrair primeiro timestamp de eventos: grep '"timestamp"' ... | head -1
   2. Extrair último timestamp: grep '"timestamp"' ... | tail -1
   3. Calcular diferença manualmente
   4. Comparar com pytest.ini configuration
   5. Registrar em DIAGNOSIS_WARNINGS_AND_TIMING.md
```

---

## 📋 Processo de Investigação Segura

### Para Cada Warning Encontrado:

1. **Identificar o tipo**
   ```bash
   grep '"event": "seu_evento"' data/test_reports/pytest_full.log
   ```

2. **Encontrar contexto do teste**
   ```bash
   grep -B5 'seu_evento' data/test_reports/pytest_full.log
   ```

3. **Localizar teste no código**
   ```bash
   find tests/ -name "*.py" -exec grep -l "seu_evento" {} \;
   ```

4. **Ler o teste completo**
   ```bash
   # Abrir arquivo no editor
   code tests/seu_teste.py
   ```

5. **Decidir se é esperado**
   - Procure comentários como `# Expected warning:`
   - Procure por `try/except` que captura o warning
   - Procure por `pytest.warns()`
   - Procure por configuração `@pytest.mark.xfail`

6. **Registrar decisão**
   - Atualizar `DIAGNOSIS_WARNINGS_AND_TIMING.md`
   - Adicionar categoria do warning
   - Marcar como ✅ Esperado ou 🚨 Problema

---

## 🛡️ Proteções Contra Erros

### O QUE NUNCA FAZER

```bash
# ❌ NUNCA
for file in *.py; do sed -i 's/warning/ok/g' "$file"; done

# ❌ NUNCA
find . -name "conftest.py" | xargs rm

# ❌ NUNCA
python -c "import os; os.system('pytest --fixes')"

# ❌ NUNCA
grep -r "warning" src/ | cut -d: -f1 | xargs rm

# ❌ NUNCA
chmod -x tests/
```

### O QUE FAZER ANTES DE QUALQUER MUDANÇA

```bash
# 1. Fazer backup
cp -r src src.backup.$(date +%s)
cp -r tests tests.backup.$(date +%s)

# 2. Registrar estado
git status > /tmp/git_status_before.txt

# 3. Criar checkpoint
git add .
git commit -m "chkpt: pre-investigation state - DO NOT PUSH"

# 4. DEPOIS SIM, investigar
# ... suas investigações ...

# 5. Se algo der errado
git reset --hard HEAD~1
```

---

## ✅ Checklist de Conclusão

Depois de investigar warnings/timing:

- [ ] Todos os warnings foram categorizados
- [ ] Cada categoria tem justificativa escrita
- [ ] Nenhuma alteração automática foi feita
- [ ] Todas as alterações estão em git
- [ ] `DIAGNOSIS_WARNINGS_AND_TIMING.md` foi atualizado
- [ ] Estado foi commitado como checkpoint
- [ ] Testes passam ainda: `pytest tests/ -x`

---

## 📚 Referência de Warnings Esperados

Veja `DIAGNOSIS_WARNINGS_AND_TIMING.md` para lista atualizada de:
- ✅ Warnings que SÃO esperados
- 🟡 Warnings que PRECISAM investigação
- ❌ Warnings que SÃO erros

---

## 🆘 Se Algo Der Muito Errado

```bash
# 1. Voltar a commit seguro
git log --oneline data/test_reports/pytest_full.log | head -3

# 2. Ver qual commit é seguro
git show <commit_hash>:data/test_reports/pytest_full.log > /tmp/test_log.bak

# 3. Restaurar se necessário
git checkout <commit_seguro>
```

---

**Lembre**: A segurança é mais importante que velocidade. Sempre investigue manualmente.
