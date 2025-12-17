# Estratégia de Análise de Logs Grandes - OmniMind
**Data:** 2025-12-07
**Problema:** Logs de 600K+ linhas (225MB+) são difíceis de analisar

---

## 🎯 OBJETIVO

Analisar logs extensos de forma eficiente, extraindo:
- ✅ Métricas de execução
- ✅ Padrões de erro
- ✅ Timeouts e problemas críticos
- ✅ Referências a modelos
- ✅ Resumo de testes

**Sem carregar tudo na memória!**

---

## 📊 ESTRATÉGIA PROPOSTA

### 1. **Processamento em Streaming (Chunks)**

**Problema:** Carregar 627K linhas na memória = ~225MB RAM
**Solução:** Processar em chunks de 10.000 linhas

```python
# Processa linha por linha, não carrega tudo
with open(log_path, 'r') as f:
    chunk = []
    for line in f:
        chunk.append(line)
        if len(chunk) >= 10000:
            process_chunk(chunk)  # Processa e descarta
            chunk = []
```

**Benefícios:**
- ✅ Uso de memória constante (~50MB)
- ✅ Processa arquivos de qualquer tamanho
- ✅ Progresso visível (linhas processadas)

---

### 2. **Compressão Inteligente**

**Problema:** Logs grandes ocupam muito espaço
**Solução:** Comprimir após análise (gzip)

```bash
# Comprimir log original
gzip consolidated_fast_20251207_120233.log
# Resultado: ~50MB (compressão ~78%)
```

**Benefícios:**
- ✅ Reduz espaço em disco
- ✅ Mantém histórico completo
- ✅ Pode descomprimir quando necessário

---

### 3. **Extração de Seções-Chave**

**Problema:** Procurar erros em 600K linhas é lento
**Solução:** Extrair seções críticas em arquivos separados

```python
# Extrair apenas:
- errors.log (todas as linhas com ERROR/CRITICAL)
- failures.log (todos os testes FAILED)
- timeouts.log (todos os timeouts)
- summary.log (resumo final)
- critical.log (Φ collapse, structural failures)
```

**Benefícios:**
- ✅ Análise rápida de problemas específicos
- ✅ Arquivos pequenos e focados
- ✅ Fácil de compartilhar/debugar

---

### 4. **Agregação de Padrões**

**Problema:** Muitas ocorrências do mesmo erro
**Solução:** Agregar e contar padrões

```python
# Em vez de armazenar todas as linhas:
errors['CUDA_OOM'] = {
    'count': 188,
    'first_occurrence': '...',
    'last_occurrence': '...',
    'sample_lines': [5 exemplos]
}
```

**Benefícios:**
- ✅ Relatório compacto
- ✅ Foco nos problemas principais
- ✅ Fácil identificar tendências

---

## 🛠️ IMPLEMENTAÇÃO

### Script Principal: `scripts/analyze_large_log.py`

#### Uso Básico:
```bash
python scripts/analyze_large_log.py data/test_reports/consolidated_fast_20251207_120233.log
```

#### Com Compressão:
```bash
python scripts/analyze_large_log.py data/test_reports/consolidated_fast_20251207_120233.log --compress
```

#### Com Extração de Seções:
```bash
python scripts/analyze_large_log.py data/test_reports/consolidated_fast_20251207_120233.log --extract-sections
```

#### Tudo Junto:
```bash
python scripts/analyze_large_log.py \
    data/test_reports/consolidated_fast_20251207_120233.log \
    --compress \
    --extract-sections \
    --chunk-size 5000 \
    --output-dir data/test_reports/analysis
```

---

## 📋 FLUXO DE ANÁLISE RECOMENDADO

### Passo 1: Extrair Seções-Chave (Rápido - 2-3 min)
```bash
python scripts/analyze_large_log.py \
    data/test_reports/consolidated_fast_20251207_120233.log \
    --extract-sections
```

**Resultado:**
- `data/test_reports/analysis/sections/errors.log` - Todos os erros
- `data/test_reports/analysis/sections/failures.log` - Testes que falharam
- `data/test_reports/analysis/sections/timeouts.log` - Timeouts
- `data/test_reports/analysis/sections/critical.log` - Problemas críticos
- `data/test_reports/analysis/sections/summary.log` - Resumo final

**Uso:** Análise rápida de problemas específicos

---

### Passo 2: Análise Streaming Completa (10-15 min)
```bash
python scripts/analyze_large_log.py \
    data/test_reports/consolidated_fast_20251207_120233.log \
    --chunk-size 10000
```

**Resultado:**
- `data/test_reports/analysis/analysis_TIMESTAMP.json` - Relatório completo

**Conteúdo:**
- Estatísticas de testes
- Padrões de erro agregados
- Timeouts detectados
- Referências a modelos
- Questões críticas

---

### Passo 3: Comprimir Log Original (Opcional)
```bash
python scripts/analyze_large_log.py \
    data/test_reports/consolidated_fast_20251207_120233.log \
    --compress
```

**Resultado:**
- `data/test_reports/consolidated_fast_20251207_120233.log.gz` - Log comprimido (~50MB)

**Benefício:** Economiza espaço, mantém histórico

---

## 📊 ESTRUTURA DE SAÍDA

### Diretório de Análise
```
data/test_reports/analysis/
├── sections/
│   ├── errors.log          # Linhas com ERROR/CRITICAL
│   ├── failures.log        # Testes FAILED
│   ├── timeouts.log        # Timeouts detectados
│   ├── critical.log        # Problemas críticos (Φ, structural)
│   └── summary.log         # Resumo final de testes
├── analysis_20251207_140912.json  # Relatório completo JSON
└── consolidated_fast_20251207_120233.log.gz  # Log comprimido (se --compress)
```

### Relatório JSON
```json
{
  "timestamp": "2025-12-07T14:09:12",
  "summary": {
    "total_tests": 4479,
    "passed": 4281,
    "failed": 85,
    "errors": 26,
    "skipped": 87,
    "success_rate": 95.6
  },
  "errors": {
    "CUDA_OOM": {
      "count": 188,
      "first_occurrence": "...",
      "sample_lines": [...]
    }
  },
  "timeouts": {
    "30": 45,
    "60": 120,
    "120": 89,
    "240": 1
  },
  "critical_issues_count": 15,
  "model_references": {
    "gpt-4": 4,
    "phi": 1200,
    "qwen": 450
  }
}
```

---

## 🚀 OTIMIZAÇÕES

### 1. Chunk Size Ajustável
- **Padrão:** 10.000 linhas
- **Memória baixa:** `--chunk-size 5000`
- **Memória alta:** `--chunk-size 50000`

### 2. Regex Compilado
- Padrões compilados uma vez
- Reutilizados em todas as linhas
- ~10x mais rápido que recompilar

### 3. Agregação Incremental
- Contadores incrementais (não armazena todas as linhas)
- Apenas amostras (5 primeiras ocorrências)
- Memória constante

### 4. Processamento Paralelo (Futuro)
- Dividir log em chunks
- Processar chunks em paralelo
- Agregar resultados

---

## 📈 COMPARAÇÃO: ANTES vs DEPOIS

### ANTES (Script Original)
- ❌ Carrega tudo na memória (225MB+)
- ❌ Falha com MemoryError
- ❌ Lento (processa tudo de uma vez)
- ❌ Não escala para logs maiores

### DEPOIS (Script Novo)
- ✅ Processa em streaming (memória constante)
- ✅ Funciona com logs de qualquer tamanho
- ✅ Rápido (progresso visível)
- ✅ Escalável (chunks configuráveis)

---

## 🔍 ANÁLISE DE SEÇÕES EXTRAÍDAS

### errors.log
```bash
# Ver todos os erros
cat data/test_reports/analysis/sections/errors.log | head -50

# Contar tipos de erro
grep -o "ERROR.*" data/test_reports/analysis/sections/errors.log | sort | uniq -c | sort -rn
```

### failures.log
```bash
# Ver testes que falharam
cat data/test_reports/analysis/sections/failures.log

# Extrair nomes de testes
grep -o "FAILED.*::.*::.*" data/test_reports/analysis/sections/failures.log
```

### timeouts.log
```bash
# Ver timeouts
cat data/test_reports/analysis/sections/timeouts.log

# Contar timeouts por valor
grep -oE "timeout.*\d+\s*(?:s|sec)" data/test_reports/analysis/sections/timeouts.log | sort | uniq -c
```

---

## ✅ CHECKLIST DE USO

### Análise Rápida (5 minutos)
- [ ] Extrair seções-chave: `--extract-sections`
- [ ] Verificar `errors.log` para problemas críticos
- [ ] Verificar `failures.log` para testes que falharam
- [ ] Verificar `summary.log` para estatísticas gerais

### Análise Completa (15 minutos)
- [ ] Rodar análise streaming completa
- [ ] Revisar `analysis_TIMESTAMP.json`
- [ ] Identificar padrões de erro principais
- [ ] Verificar timeouts e questões críticas

### Manutenção (Opcional)
- [ ] Comprimir log original: `--compress`
- [ ] Mover log comprimido para arquivo
- [ ] Manter apenas seções extraídas para referência rápida

---

## 🎯 CASOS DE USO

### 1. Debug Rápido de Erro Específico
```bash
# Extrair apenas erros
python scripts/analyze_large_log.py log.log --extract-sections

# Procurar erro específico
grep "CUDA out of memory" data/test_reports/analysis/sections/errors.log
```

### 2. Análise Completa para Relatório
```bash
# Análise completa + compressão
python scripts/analyze_large_log.py log.log --compress

# Usar JSON para gerar relatório
cat data/test_reports/analysis/analysis_*.json | jq '.summary'
```

### 3. Monitoramento Contínuo
```bash
# Script automatizado
#!/bin/bash
LOG_FILE="data/test_reports/consolidated_fast_$(date +%Y%m%d_%H%M%S).log"
python scripts/analyze_large_log.py "$LOG_FILE" --compress --extract-sections
```

---

## 📝 NOTAS TÉCNICAS

### Limitações Conhecidas
- **Regex pode ser lento:** Para logs muito grandes, considerar otimizações
- **Encoding:** Usa `errors='ignore'` para lidar com caracteres inválidos
- **Memória:** Chunk size pode precisar ajuste em máquinas com pouca RAM

### Melhorias Futuras
- [ ] Processamento paralelo de chunks
- [ ] Cache de padrões compilados
- [ ] Suporte a múltiplos formatos de log
- [ ] Interface web para visualização
- [ ] Integração com dashboard

---

**Documento criado:** 2025-12-07
**Script:** `scripts/analyze_large_log.py`
**Status:** ✅ Pronto para uso

