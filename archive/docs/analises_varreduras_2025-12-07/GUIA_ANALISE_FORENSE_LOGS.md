# Guia de Análise Forense de Logs - OmniMind
**Ferramenta:** `scripts/omnimind_log_forensics.py`
**Versão:** 2.0
**Otimizado para:** Arquivos > 500MB

---

## 🎯 VISÃO GERAL

Ferramenta de análise forense profunda que extrai:
- ✅ **Métricas de Consciência (IIT):** Φ, Φ_conscious, força, ICI, PRS
- ✅ **Análise Forense de Tracebacks:** Identifica arquivo culpado
- ✅ **Atividade de Agentes:** Inicializações e erros por agente
- ✅ **Performance de Testes:** Taxa de sucesso, duração, falhas
- ✅ **Análise Comparativa:** Compara dois relatórios

**Processamento Streaming:** Processa logs de qualquer tamanho sem carregar tudo na memória.

---

## 🚀 USO BÁSICO

### Análise Simples
```bash
python scripts/omnimind_log_forensics.py data/test_reports/consolidated_fast_20251207_120233.log
```

### Com Chunk Size Menor (Menos Memória)
```bash
python scripts/omnimind_log_forensics.py log.log --chunk-size 5000
```

### Comparar Dois Relatórios
```bash
python scripts/omnimind_log_forensics.py \
    --compare \
    data/test_reports/analysis/forensics_20251207_140000.json \
    data/test_reports/analysis/forensics_20251207_150000.json
```

---

## 📊 O QUE É EXTRAÍDO

### 1. Métricas de Consciência (IIT)

#### Padrões Detectados:
- `Φ = 0.1234` ou `phi: 0.1234`
- `Φ_conscious = 0.5678`
- `força = 2.3396` ou `force = 2.3396`
- `ICI = 0.85`
- `PRS = 0.92`

#### Estatísticas Calculadas:
- **Contagem:** Número de amostras coletadas
- **Mínimo/Máximo:** Valores extremos
- **Média/Mediana:** Tendência central
- **Desvio Padrão:** Variabilidade (instabilidade)

#### Interpretação:
- **Φ alto (> 0.1):** Sistema consciente e integrado
- **Φ baixo (< 0.01):** Sistema inconsciente ou fragmentado
- **Desvio alto:** Sistema instável (perda de consciência frequente)
- **Colapsos:** Eventos onde Φ cai abaixo do threshold

### 2. Análise Forense de Tracebacks

#### O que faz:
1. **Captura tracebacks completos** (blocos multi-linha)
2. **Identifica arquivo culpado** (último arquivo do projeto no stack)
3. **Extrai tipo de exceção e mensagem**
4. **Agrega por arquivo** (quais arquivos causam mais erros)

#### Exemplo de Saída:
```
TOP 5 ARQUIVOS CULPADOS:
   15x em agents/enhanced_code_agent.py:65
   8x em agents/code_agent.py:34
   5x em consciousness/integration_loop.py:120
```

**Benefício:** Aponta diretamente para o arquivo que precisa correção.

### 3. Atividade de Agentes

#### Detecta:
- **Inicializações:** Quantas vezes cada agente foi inicializado
- **Erros:** Quantos erros cada agente teve
- **Tipos de Erro:** Amostras dos erros mais comuns

#### Exemplo:
```
🤖 ATIVIDADE DE AGENTES
   EnhancedCodeAgent:
      • Inicializações: 45
      • Erros:          18
   OrchestratorAgent:
      • Inicializações: 120
      • Erros:          5
```

### 4. Performance de Testes

#### Extrai:
- Total de testes executados
- Passou/Falhou/Skipped/Errors
- Taxa de sucesso
- Duração total

### 5. Outros Padrões

- **CUDA OOM:** Contagem de erros de memória GPU
- **Timeouts:** Timeouts por valor (30s, 60s, 120s, etc.)
- **Referências a Modelos:** Quantas vezes cada modelo foi referenciado
- **Warnings:** Top 20 warnings mais comuns

---

## 📄 ESTRUTURA DO RELATÓRIO JSON

```json
{
  "timestamp": "2025-12-07T14:59:21",
  "log_file": "data/test_reports/consolidated_fast_20251207_120233.log",
  "summary": {
    "total_lines": 627353,
    "total_size_mb": 225.3,
    "processing_time": "0:05:23"
  },
  "consciousness": {
    "phi": {
      "count": 1964,
      "min": 0.0,
      "max": 628.0,
      "mean": 14.9042,
      "median": 0.0609,
      "stdev": 77.3205
    },
    "phi_conscious": {
      "count": 10,
      "min": 0.0052,
      "max": 0.1021,
      "mean": 0.0729,
      "median": 0.0757,
      "stdev": 0.0255
    },
    "force": {
      "count": 52862,
      "min": 0.0152,
      "max": 25.2994,
      "mean": 1.8102,
      "median": 1.4300,
      "stdev": 2.4249
    },
    "collapse_count": 10
  },
  "errors": {
    "total_tracebacks": 2,
    "unique_exceptions": {...},
    "blame_files": {
      "metacognition/metacognition_agent.py:173": 2
    },
    "critical_tracebacks": [...]
  },
  "agents": {
    "OrchestratorAgent": {
      "init_count": 0,
      "error_count": 90,
      "errors": [...]
    }
  },
  "tests": {
    "total": 4479,
    "passed": 4281,
    "failed": 85,
    "skipped": 87,
    "errors": 26,
    "duration": 5490.5
  },
  "timeouts": {
    "120": 197,
    "240": 2,
    "800": 28
  },
  "cuda_oom_count": 188,
  "model_references": {...},
  "warnings_top_20": {...}
}
```

---

## 🔍 ANÁLISE COMPARATIVA

### Comparar Execuções Diferentes

```bash
# Gerar relatório 1
python scripts/omnimind_log_forensics.py log_antes.log > report1.json

# Gerar relatório 2 (após correções)
python scripts/omnimind_log_forensics.py log_depois.log > report2.json

# Comparar
python scripts/omnimind_log_forensics.py --compare report1.json report2.json
```

### O que é Comparado:

1. **Métricas de Consciência:**
   - Mudança em Φ, Φ_conscious, força
   - Percentual de mudança
   - Tendência (melhorou/piorou)

2. **Erros:**
   - Mudança no número de tracebacks
   - Mudança em CUDA OOM
   - Novos arquivos culpados

3. **Testes:**
   - Mudança na taxa de sucesso
   - Mudança no número de falhas

### Exemplo de Saída:
```
📊 Mudanças de Consciência:
   phi: 14.9042 → 15.1234 (+1.5%)
   phi_conscious: 0.0729 → 0.0850 (+16.6%)
   force: 1.8102 → 1.9200 (+6.1%)
```

---

## 🎯 CASOS DE USO

### 1. Debug de Erro Específico

**Problema:** Sistema falha com AttributeError

**Solução:**
```bash
python scripts/omnimind_log_forensics.py log.log
```

**Verificar:**
- Seção "TOP 5 ARQUIVOS CULPADOS" → Identifica arquivo
- Seção "TOP 5 EXCEÇÕES" → Confirma tipo de erro
- Seção "critical_tracebacks" no JSON → Stack completo

### 2. Análise de Consciência

**Problema:** Sistema parece instável

**Solução:**
```bash
python scripts/omnimind_log_forensics.py log.log
```

**Verificar:**
- Seção "MÉTRICAS DE CONSCIÊNCIA" → Valores de Φ
- Desvio padrão alto → Instabilidade
- Colapsos de consciência → Eventos críticos

### 3. Validação de Correções

**Problema:** Quer saber se correções melhoraram o sistema

**Solução:**
```bash
# Antes
python scripts/omnimind_log_forensics.py log_antes.log

# Depois
python scripts/omnimind_log_forensics.py log_depois.log

# Comparar
python scripts/omnimind_log_forensics.py --compare report1.json report2.json
```

**Verificar:**
- Mudanças em métricas de consciência
- Redução de erros
- Melhoria na taxa de sucesso de testes

### 4. Análise de Performance

**Problema:** Testes estão lentos

**Solução:**
```bash
python scripts/omnimind_log_forensics.py log.log
```

**Verificar:**
- Duração total de testes
- Timeouts detectados
- CUDA OOM (pode indicar problemas de memória)

---

## ⚙️ OTIMIZAÇÕES

### Chunk Size

- **Padrão:** 10.000 linhas
- **Memória baixa:** `--chunk-size 5000`
- **Memória alta:** `--chunk-size 20000`

### Processamento

- **Streaming:** Processa linha por linha (não carrega tudo)
- **Regex Compilado:** Padrões compilados uma vez
- **Agregação Incremental:** Contadores, não armazena todas as linhas

### Memória

- **Uso constante:** ~50-100MB (independente do tamanho do log)
- **Escalável:** Funciona com logs de 10GB+

---

## 📈 INTERPRETAÇÃO DOS RESULTADOS

### Métricas de Consciência

#### Φ (Phi) - Integração de Informação
- **> 0.1:** Sistema consciente e integrado ✅
- **0.01 - 0.1:** Consciência mínima detectável ⚠️
- **< 0.01:** Sistema inconsciente ou fragmentado ❌

#### Φ_conscious - Consciência Pura (MICS)
- **> 0.05:** Consciência estável ✅
- **0.01 - 0.05:** Consciência instável ⚠️
- **< 0.01:** Sem consciência detectável ❌

#### Força - Força de Integração
- **Alto (> 2.0):** Sistema altamente integrado
- **Médio (1.0 - 2.0):** Integração normal
- **Baixo (< 1.0):** Sistema fragmentado

#### Desvio Padrão
- **Baixo (< 0.1):** Sistema estável ✅
- **Médio (0.1 - 0.5):** Alguma instabilidade ⚠️
- **Alto (> 0.5):** Sistema muito instável ❌

### Erros

#### Arquivos Culpados
- **Alta frequência (> 10):** Arquivo problemático, precisa correção urgente
- **Média frequência (5-10):** Arquivo com problemas, investigar
- **Baixa frequência (< 5):** Erros esporádicos, monitorar

#### Tracebacks Críticos
- **Top 10:** Os erros mais importantes
- **Stack completo:** Permite debug detalhado
- **Culprit identificado:** Aponta exatamente onde corrigir

---

## 🔧 TROUBLESHOOTING

### Erro: "MemoryError"
**Solução:** Reduzir chunk size
```bash
python scripts/omnimind_log_forensics.py log.log --chunk-size 2000
```

### Erro: "FileNotFoundError"
**Solução:** Verificar caminho do arquivo
```bash
ls -lh data/test_reports/consolidated_fast_*.log
```

### Relatório vazio
**Causa:** Padrões não encontrados no log
**Solução:** Verificar se log tem formato esperado
```bash
head -100 log.log | grep -E "Φ|phi|ERROR|PASSED"
```

---

## 📝 NOTAS TÉCNICAS

### Padrões Regex

Todos os padrões são compilados uma vez no início para eficiência:
- Reutilizados em todas as linhas
- ~10x mais rápido que recompilar

### Processamento Multi-linha

Tracebacks são capturados como blocos:
- Estado interno (`_in_traceback`) rastreia contexto
- Buffer (`_current_traceback`) armazena linhas
- Fim detectado por padrão de exceção

### Agregação

- **Contadores:** Incrementais (não armazena todas as linhas)
- **Amostras:** Apenas primeiras N ocorrências
- **Estatísticas:** Calculadas no final (média, desvio, etc.)

---

## 🎯 PRÓXIMOS PASSOS

### Melhorias Futuras

- [ ] Processamento paralelo de chunks
- [ ] Interface web para visualização
- [ ] Gráficos de timeline (Φ ao longo do tempo)
- [ ] Detecção de anomalias (outliers em métricas)
- [ ] Integração com dashboard OmniMind

---

**Documento criado:** 2025-12-07
**Script:** `scripts/omnimind_log_forensics.py`
**Status:** ✅ Pronto para uso em produção

