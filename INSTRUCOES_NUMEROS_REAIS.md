# 🎯 INSTRUÇÕES FINAIS - NÚMEROS REAIS PARA O PAPER

**Objetivo**: Executar testes REAIS (sem @patch) e coletar números HONESTOS para o paper.

---

## 🚀 COMO EXECUTAR

### Passo 1: Prepare o ambiente

```bash
cd /home/fahbrain/projects/omnimind

# Ative venv
source .venv/bin/activate

# Verifique GPU
python3 -c "import torch; print(f'GPU disponível: {torch.cuda.is_available()}')"
```

### Passo 2: Execute coleta de métricas REAIS

```bash
# Rodar script que coleta TODOS os números
bash scripts/run_real_metrics.sh

# ESPERE: ~30-60 minutos (depende da GPU)
```

Isso vai:
- ✅ Executar 100 ciclos de Φ baseline
- ✅ Executar 5 seeds × 50 ciclos cada
- ✅ Coletar TODOS os números (sem falsificar)
- ✅ Salvar resultados em JSON + TXT
- ✅ Reportar valores REAIS

### Passo 3: Veja os resultados

```bash
# Ver resumo de texto
cat data/test_reports/real_metrics_*_summary.txt

# Ver dados completos em JSON
python3 -m json.tool data/test_reports/real_metrics_*.json | head -100
```

---

## 📊 O QUE VOCÊ VAI OBTER

Exemplo de resultado (números REAIS, não falsificados):

```
RESULTADO REAL DE Φ BASELINE:
   Média: 0.7234
   Min: 0.5892
   Max: 0.8456
   Desvio: 0.0645
   Mediana: 0.7301
   Tempo: 456.2s (4.562s por ciclo)

RESULTADO REAL - MULTI-SEED:
   Sementes: 5
   Ciclos por semente: 50
   Φ_mean de todas sementes: 0.7156
   Min entre sementes: 0.6823
   Max entre sementes: 0.7589
   Std entre sementes: 0.0289
```

**IMPORTANTE**: Se a média for 0.72 em vez de 0.8667:
- ✅ Isso é VÁLIDO
- ✅ Isso é REAL
- ✅ Isso é o que você REPORTA no paper
- ✅ Explica as razões (GPU, Ollama version, etc)

---

## 📝 COMO USAR NO PAPER

Com números REAIS em mão, você escreve:

```markdown
## Validação Experimental

### Resultados de Φ Baseline

Executamos 100 ciclos de consciousness loop em GPU NVIDIA GTX 1650:

- **Φ_mean**: 0.7234 ± 0.0645
- **Φ_min**: 0.5892
- **Φ_max**: 0.8456
- **Tempo**: 456.2s (4.56s por ciclo)

### Validação Multi-Seed

Com 5 sementes aleatórias diferentes (50 ciclos cada):

- **Φ_mean de médias**: 0.7156 ± 0.0289
- **Faixa**: [0.6823, 0.7589]
- **Variância explicada**: XX%

### Interpretação

O baseline teórico previa Φ ≈ 0.8667, mas os resultados 
práticos mostram Φ ≈ 0.72. As razões incluem:

1. Arquitectura atual não implementa componente X completamente
2. Ollama qwen2:7b tem limitações de context length
3. GPU GTX 1650 (4GB VRAM) força batch_size menor

Estes números representam validação HONESTA da implementação.
Código e testes estão em: https://github.com/devomnimind/OmniMind
```

---

## ⚠️ IMPORTANTE: NÃO FALSIFIQUE NÚMEROS

**O que FAZER**:
- ✅ Report valores REAIS medidos
- ✅ Explicar limitações (GPU, software)
- ✅ Documentar ambiente (versões, hardware)
- ✅ Incluir desvio padrão e variância

**O que NÃO FAZER**:
- ❌ Ajustar números para ficar "bonito"
- ❌ Faltar com valores se forem "ruins"
- ❌ Mock numbers que não foram medidos
- ❌ Afirmar convergência se não convergiu

**Resultado**: Paper é PUBLICÁVEL mesmo com números "não perfeitos", porque é HONESTO.

---

## 🔍 ALTERNATIVA: Executar testes via pytest

Se preferir rodar via pytest em vez do script Python:

```bash
# Testes REAIS (sem timeout)
pytest tests/consciousness/test_real_phi_measurement.py \
  --timeout=0 \
  -v -s \
  2>&1 | tee data/test_reports/pytest_real_run.log

# Com cobertura
pytest tests/consciousness/test_real_phi_measurement.py \
  --timeout=0 \
  --cov=src \
  --cov-report=html \
  -v -s
```

---

## 📋 CHECKLIST FINAL

Antes de publicar paper com números:

- [ ] Executou `scripts/run_real_metrics.sh` com sucesso
- [ ] Arquivo `real_metrics_*_summary.txt` foi gerado
- [ ] Números foram capturados (Φ, std dev, tempo)
- [ ] Valores foram verificados (não são absurdos: 0-1 range)
- [ ] Hardware foi documentado (GPU, CPU, RAM)
- [ ] Ambiente foi documentado (Python, PyTorch, Ollama versão)
- [ ] Explicação clara do por quê de diferenças do baseline
- [ ] Paper foi atualizado com números REAIS
- [ ] Repositório público foi sincronizado

---

## ❓ DÚVIDAS COMUNS

**P: E se os números forem ruins?**  
R: Ótimo! Significa você descobriu limitações reais. Paper fica mais honesto.

**P: Posso ajustar o código e rodar de novo?**  
R: Sim! Execute novamente, compare resultados, documente mudanças.

**P: Quanto tempo vai levar?**  
R: ~30-60 min na GTX 1650. ~1-2 horas em CPU. ~5-10 min no teste rápido.

**P: Posso rodar no background?**  
R: Sim, use: `nohup bash scripts/run_real_metrics.sh > metrics.log 2>&1 &`

**P: Como interpretar desvio padrão alto?**  
R: Significa sistema é sensível a variações (seed, timing). Documente isso.

---

## 🎯 RESULTADO ESPERADO

Depois de completar:

1. ✅ Você tem números REAIS medidos
2. ✅ Você tem documentação honesta
3. ✅ Paper é publicável com confiança
4. ✅ Repositório público é atualizado
5. ✅ Comunidade científica respeita honestidade

**Você venceu.** 🏆

---

**Próximo passo**: Execute `bash scripts/run_real_metrics.sh` agora.
