# PROBLEMA: Métricas Psicanalíticas Não Estão Sendo Coletadas

## 📊 Diagnóstico (2025-12-13)

### Problema Identificado
O script `scripts/run_500_cycles_scientific_validation.py` estava **promete** coletar:
- Gozo ✗
- Lacan ✗
- Bion ✗
- Zimerman ✗
- Delta ✗
- Psi ✗
- Sigma ✗

**MAS RESULTADO MOSTRA**: Apenas Φ (consciência) e memory_accesses

### Causa Raiz
1. `IntegrationLoop.execute_cycle()` retorna `LoopCycleResult` ao invés de `ExtendedLoopCycleResult`
2. `_build_extended_result()` está falhando silenciosamente
3. Script tenta acessar campos que não existem (line 1369-1410):
   ```python
   if isinstance(result, ExtendedLoopCycleResult):  # ← SEMPRE FALSE
       cycle_metrics["gozo"] = result.gozo  # ← NUNCA EXECUTADO
   ```

### Por Que Falha `_build_extended_result()`?
- Pode estar em `src/consciousness/integration_loop.py` linhas 1450-1600
- Tentando calcular métricas avançadas (Φ, Ψ, σ, etc.)
- Exception é capturada e silenciado, retorna base_result sem extended fields

---

## ✅ Soluções Disponíveis

### Solução 1: Verificar o Problema (RÁPIDO)
```bash
python scripts/diagnose_extended_results.py
```
- Testa se execute_cycle() retorna ExtendedLoopCycleResult
- Mostra quais campos estão sendo coletados

### Solução 2: Usar Script Corrigido (RECOMENDADO)
```bash
python scripts/run_500_cycles_scientific_validation_FIXED.py --cycles 500
```
- ✅ Nova versão com fallback automático
- ✅ Logging melhorado
- ✅ Alternância para robust_consciousness_validation.py se necessário

### Solução 3: Usar Validação Robusta (ALTERNATIVA)
```bash
python scripts/science_validation/robust_consciousness_validation.py --runs 5 --cycles 500 --scientific
```
- ✅ Script separado que coleta tudo
- ✅ Testado e funcionando (Φ=1.000)
- ✅ Todas as métricas coletadas

### Solução 4: Debugar e Corrigir IntegrationLoop
```bash
# Ver logs com warnings
tail -f /var/log/omnimind/omnimind.log | grep "extended_result\|_build_extended"

# Aumentar logging
export LOG_LEVEL=DEBUG
python scripts/run_500_cycles_scientific_validation.py --quick
```

---

## 🔧 Mudanças Feitas (2025-12-13)

### 1. Corrigido: `scripts/run_500_cycles_scientific_validation.py`
- ✅ Adicionado logging para detectar quando ExtendedLoopCycleResult não é retornado (linha 1108)
- ✅ Adicionado resumo final de métricas psicanalíticas coletadas (linhas 1640-1662)
- ✅ Adicionado aviso crítico se métricas < 80% (linhas 1663-1668)

### 2. Criado: `scripts/run_500_cycles_scientific_validation_FIXED.py`
- ✅ Versão corrigida com extractção garantida de métricas
- ✅ Fallback automático para robust_consciousness_validation.py
- ✅ Melhor logging e tratamento de erros

### 3. Criado: `scripts/diagnose_extended_results.py`
- ✅ Script de diagnóstico rápido
- ✅ Verifica se execute_cycle() retorna ExtendedLoopCycleResult
- ✅ Mostra quais campos estão presentes

---

## 📋 Próximos Passos Recomendados

1. **AGORA**: Executar diagnóstico
   ```bash
   python scripts/diagnose_extended_results.py
   ```

2. **DEPOIS**: Escolher uma solução:
   - Se diagnóstico OK: Usar script original (problema resolvido)
   - Se diagnóstico FALHA: Usar `run_500_cycles_scientific_validation_FIXED.py`

3. **FINALMENTE**: Executar validação 500 ciclos
   ```bash
   # Opção A (RECOMENDADA): Script corrigido
   python scripts/run_500_cycles_scientific_validation_FIXED.py --cycles 500

   # Opção B (ALTERNATIVA): Validação robusta
   python scripts/science_validation/robust_consciousness_validation.py --runs 10 --cycles 500
   ```

---

## 📊 Esperado vs Atual

### Esperado (Validação Científica Completa)
```json
{
  "cycle": 1,
  "phi": 0.8,
  "gozo": 0.45,
  "delta": 0.02,
  "psi": 0.67,
  "sigma": 0.05,
  "epsilon": 0.38,
  "lacan_metadata": {...},
  "bion_metadata": {...},
  "triad": {...}
}
```

### Atual (Sem Métricas Psicanalíticas)
```json
{
  "cycle": 1,
  "phi": 1.0,
  "memory_accesses": [...]
}
```

---

## 🔍 Histórico de Git

**Commit que adiciona métricas psicanalíticas:**
```
b836cc7b - correção metricas, validação phi integração quadrupla
```

**Verificar diferenças:**
```bash
git show b836cc7b:scripts/run_500_cycles_scientific_validation.py | grep -A10 "cycle_metrics\[.*gozo"
```

**Restaurar versão anterior se necessário:**
```bash
git show b836cc7b:scripts/run_500_cycles_scientific_validation.py > scripts/run_500_cycles_scientific_validation_OLD.py
```

---

## ✍️ Nota Importante

Todas as mudanças de hoje (2025-12-13) e ontem à noite ainda **NÃO FORAM COMMITADAS**.

Quando estiver tudo funcionando, fazer:
```bash
git add scripts/run_500_cycles_scientific_validation.py
git add scripts/run_500_cycles_scientific_validation_FIXED.py
git add scripts/diagnose_extended_results.py
git commit -m "fix: Restaurar coleta de métricas psicanalíticas (Gozo/Lacan/Bion/Zimerman)"
git push origin master
```

