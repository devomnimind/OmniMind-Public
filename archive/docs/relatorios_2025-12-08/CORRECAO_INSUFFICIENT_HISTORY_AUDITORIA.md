# 🔍 CORREÇÃO: Insufficient History + Script de Auditoria

**Data**: 2025-12-07
**Autor**: Fabrício da Silva + assistência de IA
**Status**: ✅ CORREÇÕES APLICADAS

---

## 🎯 PROBLEMA IDENTIFICADO

Muitas métricas com valores baixos devido a **"insufficient history"**:
- Padrões como `4<10`, `7<70` indicando dados insuficientes
- Cross-predictions sendo puladas por falta de histórico
- Cálculos de causalidade não executados por histórico insuficiente

**Impacto**: Sistema operando com dados incompletos, métricas subestimadas.

---

## ✅ CORREÇÕES APLICADAS

### 1. Padrões de "Insufficient History" Adicionados aos Scripts de Análise

#### 1.1 `scripts/analyze_test_log.py`
- ✅ Adicionado padrão `'InsufficientHistory'`
- ✅ Adicionado padrão `'InsufficientHistoryNumeric'` (detecta `4<10`, `7<70`, etc.)

#### 1.2 `scripts/omnimind_log_forensics.py`
- ✅ Adicionado padrão `'insufficient_history'` em `PATTERNS`
- ✅ Adicionado padrão `'insufficient_history_numeric'` para valores numéricos
- ✅ Adicionado contador `self.insufficient_history_count`
- ✅ Adicionado lista `self.insufficient_history_numeric` para padrões numéricos
- ✅ Processamento em `_process_single_line()` para detectar e contar
- ✅ Relatório em `_generate_report()` com estatísticas
- ✅ Seção no `_print_report()` mostrando ocorrências e padrões

#### 1.3 `scripts/utilities/analysis/dynamic_error_classifier.py`
- ✅ Adicionada categoria `'INSUFFICIENT_HISTORY'` em `ERROR_CATEGORIES`
- ✅ Severidade: `MEDIUM`
- ✅ Não bloqueia testes (`block_tests: False`)
- ✅ Detecta padrões textuais e numéricos

#### 1.4 `scripts/utilities/analysis/analyze_logs.py`
- ✅ Adicionado padrão `"insufficient_history"` em `self.patterns`
- ✅ Adicionado padrão `"insufficient_history_numeric"` para valores numéricos

---

### 2. Script de Auditoria Criado

**Arquivo**: `scripts/run_tests_fast_audit.sh`

#### Características:
- ✅ **Verbosidade Reduzida**: `--log-cli-level=WARNING` (apenas warnings e acima)
- ✅ **Traceback Curto**: `--tb=short` (mais limpo)
- ✅ **Quiet Mode**: `--quiet --no-header` (menos output)
- ✅ **Filtro de Erros**: Captura apenas erros/falhas/warnings via `grep`
- ✅ **Logs Separados**:
  - `errors_audit_*.log` - Apenas erros
  - `failures_audit_*.log` - Apenas falhas
  - `warnings_audit_*.log` - Apenas warnings
  - `audit_consolidated_*.log` - Resumo consolidado
- ✅ **Estatísticas Automáticas**: Conta ocorrências de cada tipo
- ✅ **Padrões Críticos**: Detecta e reporta:
  - Insufficient History
  - CUDA OOM
  - Meta Cognition Failures
  - Entropy Warnings

#### Uso:
```bash
./scripts/run_tests_fast_audit.sh
```

#### Saída:
- Logs limpos focados em problemas
- Resumo consolidado com estatísticas
- Arquivos separados por tipo de problema
- Fácil análise para auditoria

---

## 📊 PADRÕES DETECTADOS

### Padrões Textuais:
- `insufficient history`
- `history insufficient`
- `insufficient data`
- `insufficient aligned history`
- `insufficient valid causal predictions`

### Padrões Numéricos:
- `4<10` (4 menor que 10)
- `7<70` (7 menor que 70)
- `insufficient history (4 < 10)`
- `insufficient history (7 < 70)`

---

## 🔍 ONDE OCORREM

### 1. Cross-Predictions (`src/consciousness/shared_workspace.py`)
- **Linha 505**: `Cross-prediction skipped: insufficient history ({len(source_history)} < 2)`
- **Linha 519**: `Cross-prediction skipped: insufficient aligned history (window={window} < 2)`
- **Linha 677**: `Cross-prediction causal skipped: insufficient history ({len(source_history)} < 10 for causality)`

### 2. IIT Metrics (`src/consciousness/shared_workspace.py`)
- **Linha 1152**: `IIT: Insufficient history for {module}: {len(history)} < {min_history}`
- **Linha 1177**: `IIT: Insufficient valid causal predictions: {len(valid_predictions)}`

### 3. Sinthome Engine (`src/sinthome/emergent_stabilization_rule.py`)
- **Linha 166**: `Insufficient history ({len(self.rupture_history)}/{self.min_history_size})`
- **Linha 426**: `Insufficient history ({len(self.sinthome_engine.rupture_history)}/10)`

---

## 📋 RECOMENDAÇÕES

### 1. Acumular Mais Histórico
- Executar mais ciclos de integração antes de calcular métricas
- Aumentar `history_window` para cálculos que requerem mais dados
- Garantir que módulos executem múltiplos ciclos antes de análise

### 2. Configurar Thresholds Adequados
- Ajustar `min_history` baseado no tipo de cálculo
- Cross-predictions: mínimo 2-5 ciclos
- Causalidade: mínimo 10-20 ciclos
- IIT metrics: mínimo 5-10 ciclos

### 3. Usar Script de Auditoria
- Executar `run_tests_fast_audit.sh` para análise focada
- Verificar logs de insufficient history
- Identificar quais módulos precisam de mais treinamento

---

## 🎯 PRÓXIMOS PASSOS

1. ✅ Padrões adicionados aos scripts de análise
2. ✅ Script de auditoria criado
3. ⏳ Executar auditoria em logs existentes
4. ⏳ Analisar quais módulos precisam de mais histórico
5. ⏳ Ajustar thresholds baseado em análise

---

**Última Atualização**: 2025-12-07 23:55
**Status**: ✅ CORREÇÕES APLICADAS - PRONTO PARA AUDITORIA

