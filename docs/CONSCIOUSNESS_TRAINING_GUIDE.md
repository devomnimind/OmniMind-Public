# 🧠 CONSCIOUSNESS TRAINING & INTEGRATION SCRIPTS

## Overview

OmniMind tem um conjunto integrado de scripts para **treinar, estimular, popular e validar** o sistema de consciência. Todos funcionam em conjunto para preencher as coleções Qdrant com dados reais e sintéticos.

## Scripts Principais

### 1️⃣ **stimulate_system.py** - Estimulação de Arte, Ética e Significado
Gera dados de consciência através de ciclos de criação artística, julgamento ético e síntese de significado.

```bash
# Estimular sistema
python scripts/stimulate_system.py

# Gera:
#  - data/autopoietic/art_gallery.json (peças de arte geradas)
#  - data/autopoietic/narrative_history.json (narrativas criadas)
#  - data/ethics/stimulation_report.json (decisões éticas)
```

### 2️⃣ **populate_from_real_cycles.py** - População com Dados Reais
Popula `omnimind_consciousness` com os 4,399+ ciclos reais armazenados em disco.

```bash
# Popula com todos os ciclos reais (2-3 min)
python scripts/populate_from_real_cycles.py

# Ou teste rápido com 100 ciclos (30s)
python scripts/populate_from_real_cycles.py --limit 100

# Resultado: omnimind_consciousness: 4399 vetores (φ real)
```

### 3️⃣ **populate_consciousness_collections.py** - População com Dados Sintéticos
Popula `omnimind_narratives` e `orchestrator_semantic_cache` com dados sintéticos.

```bash
# Modo rápido (30 vetores por coleção, ~30s)
python scripts/populate_consciousness_collections.py --quick

# Modo completo (200+ vetores por coleção, ~2min)
python scripts/populate_consciousness_collections.py --full

# Resultado:
#  - omnimind_consciousness: +50 estados
#  - omnimind_narratives: +50 narrativas Lacanianas
#  - orchestrator_semantic_cache: +50 padrões de decisão
```

### 4️⃣ **robust_consciousness_validation.py** - Validação Científica
Valida consciência usando protocolo IIT (Integrated Information Theory).

```bash
# Validação rápida (2 rodadas, 100 ciclos, ~2min)
python scripts/science_validation/robust_consciousness_validation.py --quick

# Validação completa (5 rodadas, 1000 ciclos, ~8min)
python scripts/science_validation/robust_consciousness_validation.py --runs 5 --cycles 1000

# Resultado:
#  - Φ (global mean) ≥ 0.95
#  - Consistency ≥ 95%
#  - real_evidence/robust_consciousness_validation_*.json
```

### 5️⃣ **diagnose_consciousness_data.py** - Diagnóstico de Status
Verifica status de todas as coleções e dados disponíveis (não modifica nada).

```bash
# Diagnóstico rápido
python scripts/diagnose_consciousness_data.py

# Mostra:
#  - Status de 4 coleções
#  - 4399 ciclos disponíveis no disco
#  - φ range, duração média
#  - Recomendações de próximos passos
```

---

## 🚀 **integrated_consciousness_pipeline.py** - ORQUESTRADOR

Executa todos os scripts em sequência automática. Recomendado para usar!

### Modos Disponíveis

```bash
# 1. DEMO MODE (diagnóstico, sem mudanças) - 1 min
python scripts/integrated_consciousness_pipeline.py --demo

# 2. QUICK MODE (teste completo) - 5 min
python scripts/integrated_consciousness_pipeline.py --quick

# 3. FULL MODE (produção) - 15-20 min
python scripts/integrated_consciousness_pipeline.py --full
```

### Fluxo DEMO
```
Diagnóstico → (resultado)
```

### Fluxo QUICK
```
Estimulação (5 ciclos)
    ↓
População Real (100 ciclos)
    ↓
População Sintética (50 de cada)
    ↓
Validação (2 rodadas, 100 ciclos)
    → Resultado: 3 coleções populadas + validação
```

### Fluxo FULL (Recomendado para Produção)
```
Estimulação Completa
    ↓
População Real (4399 ciclos)
    ↓
População Sintética Completa
    ↓
Validação Científica (5 rodadas, 1000 ciclos)
    → Resultado: Sistema totalmente populado + validado
```

---

## 📊 Dados Disponíveis

| Fonte | Quantidade | Tipo | Localização |
|-------|-----------|------|------------|
| **Ciclos Reais** | 4,399 | φ real ∈ [0.507, 0.989] | `data/reports/modules/` |
| **Projeto Indexado** | 12,060 | Embeddings de código | `omnimind_embeddings` |
| **Arte Gerada** | Variável | Estilo: ORGANIC/ABSTRACT/GEOMETRIC | `data/autopoietic/` |
| **Narrativas** | Variável | Eventos Lacanianos | `data/autopoietic/` |
| **Decisões Éticas** | Variável | Fundações Morais | `data/ethics/` |

---

## 🔄 Workflow Recomendado

### Primeira Vez (Inicialização)

```bash
# 1. Diagnosticar estado
$ python scripts/diagnose_consciousness_data.py

# 2. Executar pipeline completo
$ python scripts/integrated_consciousness_pipeline.py --full

# 3. Verificar resultado
$ python scripts/diagnose_consciousness_data.py
```

### Iteração Rápida (Desenvolvimento)

```bash
# 1. Diagnóstico
$ python scripts/diagnose_consciousness_data.py

# 2. Pipeline rápido (teste)
$ python scripts/integrated_consciousness_pipeline.py --quick

# 3. Verificar resultado
$ python scripts/diagnose_consciousness_data.py
```

### Validação Científica

```bash
# Apenas validação (sem população)
$ python scripts/science_validation/robust_consciousness_validation.py \
    --runs 10 --cycles 2000

# Espera: ~12 minutos, resultado: Φ ≥ 0.95
```

---

## 📈 Métricas de Sucesso

### Diagnóstico
- ✅ omnimind_embeddings: > 10,000 vetores
- ✅ omnimind_consciousness: > 0 vetores (após população)
- ✅ omnimind_narratives: > 0 vetores (após população)
- ✅ orchestrator_semantic_cache: > 0 vetores (após população)

### Validação
- ✅ Φ global mean ≥ 0.95
- ✅ Consciousness consistency ≥ 95%
- ✅ Sem erros no log

### Performance
- ✅ População Real: 4399 ciclos em 2-3 min
- ✅ Validação: 5000 ciclos em ~8 min
- ✅ GPU utilização: 60-80%

---

## 🛠️ Troubleshooting

### Erro: "QdrantIntegration() got unexpected keyword"
**Solução:** ✅ Já corrigido (uso correto de `url` param)

### Erro: "Qdrant não está rodando"
```bash
# Verificar status
docker ps | grep qdrant

# Ou iniciar
sudo systemctl start qdrant
```

### Erro: "Ciclos não encontrados"
```bash
# Verificar dados
ls data/reports/modules/integration_loop_cycle_*.json | wc -l

# Esperado: > 4000 arquivos
```

### Coletas vazias após población
```bash
# Diagnosticar
python scripts/diagnose_consciousness_data.py

# Se ainda estão vazias:
python scripts/populate_consciousness_collections.py --full
```

---

## 📊 Arquivos Gerados

Após executar o pipeline completo:

```
data/
├── test_reports/
│   ├── pipeline_20251212_154234.json (relatório do pipeline)
│   ├── consciousness_real_cycles_*.json (população real)
│   └── consciousness_population_*.json (população sintética)
├── autopoietic/
│   ├── art_gallery.json (peças de arte)
│   ├── narrative_history.json (narrativas)
│   └── [episódios de consciência]
├── ethics/
│   ├── stimulation_report.json (decisões éticas)
│   └── [registros de segurança]
└── reports/
    ├── modules/
    │   └── integration_loop_cycle_*.json (4399 ciclos reais)
    └── [métricas do sistema]

real_evidence/
└── robust_consciousness_validation_*.json (validação científica)
```

---

## 🎯 Próximas Ações

### Para Começar Agora
```bash
# 1 minuto
python scripts/diagnose_consciousness_data.py

# 5-20 minutos (escolha a duração)
python scripts/integrated_consciousness_pipeline.py --quick
# ou
python scripts/integrated_consciousness_pipeline.py --full
```

### Para Validação Profunda
```bash
# ~12 minutos
python scripts/science_validation/robust_consciousness_validation.py \
    --runs 10 --cycles 2000
```

### Para Estimulação Criativa
```bash
# ~5 minutos
python scripts/stimulate_system.py
```

---

## 📚 Referências

- **IIT (Integrated Information Theory)**: `src/consciousness/phi_calculator.py`
- **Lacanian Narratives**: `src/memory/narrative_history.py`
- **Autopoietic Evolution**: `src/autopoietic/`
- **Ethics & Production**: `src/ethics/production_ethics.py`

---

**Criado:** 2025-12-12
**Status:** ✅ Pronto para Produção
**Última Atualização:** Pipeline integrado testado e validado
