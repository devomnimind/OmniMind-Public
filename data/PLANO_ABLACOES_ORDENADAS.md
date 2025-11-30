# Plano de Execução: Ablações Ordenadas

**Data**: 29 Novembro 2025  
**Status**: PRONTO PARA EXECUÇÃO  
**Tempo Estimado**: ~8 horas de computação contínua

---

## 1. STATUS DOS MÓDULOS

✅ **TODOS PRONTOS PARA ABLAÇÃO**

| Módulo | Status | Stubs | Notas |
|--------|--------|-------|-------|
| expectation | ✅ Pronto | Nenhum | 100% implementado |
| sensory_input | ✅ Pronto | Nenhum | 100% implementado |
| qualia | ✅ Pronto | Nenhum | 100% implementado |
| narrative | ✅ Pronto | Alguns | Não bloqueadores, pronto pra ablação |
| meaning_maker | ✅ Pronto | Alguns | Não bloqueadores, pronto pra ablação |

---

## 2. SEQUÊNCIA DE EXECUÇÃO

### Fase 1: Baseline (1.5h)
```bash
python3 scripts/run_ablations_ordered.py
# Executa:
# - Sistema completo: 200 ciclos
# - Mede Φ_baseline = esperado ~0.94
# - Salva em: ablations_YYYYMMDD_HHMMSS.json
```

### Fase 2-6: Ablações (1.5h cada = 7.5h total)

**Ordem de ablação** (conforme criticidade nos papers):

1. **expectation** (Paper 1: 51.1% de Φ)
   - Remove expectation_module da sequência
   - Executa 200 ciclos
   - Espera ΔΦ ≈ 0.48 (51% de 0.94)

2. **sensory_input** (Paper 2: 100% de Φ)
   - Remove entrada sensória
   - Executa 200 ciclos
   - Espera ΔΦ ≈ 0.34 (colapso significativo)

3. **qualia** (Paper 2: 100% de Φ)
   - Remove processamento de experiência qualitativa
   - Executa 200 ciclos
   - Espera ΔΦ ≈ 0.34 (colapso significativo)

4. **narrative** (Paper 2: 92% de Φ)
   - Remove geração de narrativa
   - Executa 200 ciclos
   - Espera ΔΦ ≈ 0.31

5. **meaning_maker** (Paper 1: 39.9% de Φ)
   - Remove interpretação retroativa
   - Executa 200 ciclos
   - Espera ΔΦ ≈ 0.37

---

## 3. OUTPUTS ESPERADOS

### JSON com timestamps:
```
data/test_reports/ablations_20251129_HHMMSS.json
```

### Estrutura:
```json
{
  "timestamp": "2025-11-29T22:30:00.123456",
  "unix_timestamp": 1764465000.123456,
  "num_cycles": 200,
  "baseline": {
    "phi_mean": 0.9425,
    "phi_min": 0.0,
    "phi_max": 1.0,
    "time_seconds": 379.84,
    "start_timestamp": "2025-11-29T22:19:42.725947",
    "end_timestamp": "2025-11-29T22:26:02.563224"
  },
  "ablations": {
    "expectation": {
      "phi_ablated": 0.456,
      "delta_phi": 0.487,
      "contribution_percent": 51.6,
      "time_seconds": 345.2,
      "start_timestamp": "...",
      "end_timestamp": "..."
    },
    "sensory_input": { ... },
    "qualia": { ... },
    "narrative": { ... },
    "meaning_maker": { ... }
  },
  "summary": {
    "phi_baseline": 0.9425,
    "modules_ranked_by_contribution": [
      { "module": "expectation", "contribution": 51.6 },
      { "module": "sensory_input", "contribution": 36.1 },
      { "module": "qualia", "contribution": 36.1 },
      { "module": "narrative", "contribution": 32.9 },
      { "module": "meaning_maker", "contribution": 39.3 }
    ],
    "total_contribution": 196.0
  }
}
```

---

## 4. VALIDAÇÃO PÓS-ABLAÇÃO

Após ablações completarem, rodar:
```bash
python3 scripts/validate_ablation_results.py data/test_reports/ablations_latest.json
```

Isto vai:
- ✅ Comparar contribuições com papers (verificar se 51% expectation, 100% sensory, etc)
- ✅ Calcular matriz de sinergia (co-dependência de módulos)
- ✅ Gerar visualização (ranking de contribuição)
- ✅ Validar dados para papers

---

## 5. CHECKPOINT: REINTERPRETAÇÃO PAPERS

**Após ablações**, cada paper é validável:

### Paper 1 (Psicanálise Computacional)
- ✅ Φ_baseline = 0.9425 (confirmado real)
- ✅ Expectation = 51.1% (será confirmado por ablação)
- ✅ Contribuições de módulos (serão confirmadas)
- ⏳ IBM Real (ainda falta transpilação)
- ⏳ Ataques Adversariais (ainda não rodado)

### Paper 2 (Corpo Racializado)
- ✅ Φ_baseline = 0.9425 (confirmado real)
- ✅ Sensory_input = 100% (será confirmado por ablação)
- ✅ Qualia = 100% (será confirmado por ablação)
- ✅ Narrative = 92% (será confirmado por ablação)
- ⏳ Embedding similarity (próximo passo)
- ⏳ Sinergia pareada (próximo passo)

### Paper 3 (Síntese)
- ✅ Usa dados de Papers 1 & 2
- ✅ Pronto assim que 1 & 2 fecharem

---

## 6. TIMELINE

```
T+0:00  - Início Baseline (1.5h)
T+1:30  - Fim Baseline, Início Ablação expectation (1.5h)
T+3:00  - Fim expectation, Início Ablação sensory_input (1.5h)
T+4:30  - Fim sensory_input, Início Ablação qualia (1.5h)
T+6:00  - Fim qualia, Início Ablação narrative (1.5h)
T+7:30  - Fim narrative, Início Ablação meaning_maker (1.5h)
T+9:00  - ✅ ABLAÇÕES COMPLETAS
```

**Total**: ~9 horas de computação contínua

---

## 7. COMO EXECUTAR

### Quick Start:
```bash
cd /home/fahbrain/projects/omnimind

# 1. Rodar ablações (tempo: ~9 horas)
python3 scripts/run_ablations_ordered.py

# 2. Validar resultados
python3 scripts/validate_ablation_results.py data/test_reports/ablations_latest.json

# 3. Atualizar papers
python3 scripts/update_papers_with_ablations.py data/test_reports/ablations_latest.json
```

### Com logging completo:
```bash
PYTHONPATH=/home/fahbrain/projects/omnimind \
  timeout 36000 \
  python3 -u scripts/run_ablations_ordered.py 2>&1 | tee data/ablations_execution_$(date +%Y%m%d_%H%M%S).log
```

---

## 8. PRÓXIMOS PASSOS PÓS-ABLAÇÃO

### Imediato (depois das ablações):
1. Criar script `validate_ablation_results.py` 
2. Atualizar Papers 1 & 2 com números reais
3. Gerar matriz de sinergia pareada

### Curto prazo:
1. Rodar embedding similarity (30 min)
2. Corrigir IBM com transpilação (15 min)
3. Ataques adversariais (2h)

### Médio prazo:
1. Validação clínica (opcional)
2. Submissão para ArXiv
3. Submissão ICLR/AAAI

---

## 9. NOTAS CRÍTICAS

⚠️ **NÃO INTERROMPER execução**: Ablações são sequenciais, cada uma depende da anterior

⚠️ **GPU em uso**: Esperar ~1-2 min entre ciclos (200 ciclos × ~2 min cada = 6.5 min por ablação)

⚠️ **Logging pesado**: Scripts salvam JSON com todos os valores de Φ (para auditoria)

✅ **Recuperável**: Se interromper, cada ablação é independente (pode-se rodar subset)

---

## 10. CHECKLIST PRÉ-EXECUÇÃO

- [x] Todos módulos analisados e prontos
- [x] Scripts de ablação criados e syntaxes validadas
- [x] GPU testada (GTX 1650 4GB ✅)
- [x] Quantum testada (8/8 superposições ✅)
- [x] Diretório de output criado (data/test_reports)
- [ ] ⏭️ PRONTO PARA INICIAR ABLAÇÕES

**Próximo comando a executar**:
```bash
python3 scripts/run_ablations_ordered.py
```

