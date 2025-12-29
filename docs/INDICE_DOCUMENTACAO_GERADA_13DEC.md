# 📚 Índice de Documentação Gerada - 13 DEZ 2025

**Objetivo**: Guia de navegação para toda documentação gerada na sessão de análise GPU

---

## 🗂️ ESTRUTURA DE ARQUIVOS

### 📄 Documentos de Análise (docs/)

#### 1. **ANALISE_PARALELIZACAO_GPU_WINDOWS_VS_LINUX.md**
   - **Propósito**: Entender por que perdeu paralelização ao migrar para Linux
   - **Conteúdo**:
     - Comparação técnica Windows vs Linux
     - Root cause: GPU context switching overhead
     - Python GIL bloqueando threads
     - Soluções propostas (CUDA Graphs, batch size, ProcessPool)
   - **Leitura recomendada**: PRIMEIRO
   - **Público**: Técnicos, pesquisadores
   - **Tempo**: 20-30 minutos

#### 2. **COMPARACAO_KALI_VS_UBUNTU_PARALELIZACAO.md**
   - **Propósito**: Dados detalhados da degradação Kali (4→3→2→1 threads)
   - **Conteúdo**:
     - Histórico das tentativas paralelas em Kali
     - Benchmarks numéricos por thread count
     - Literatura científica sobre overhead
     - Comparação teórico vs observado
   - **Leitura recomendada**: SEGUNDO
   - **Público**: Pesquisadores de sistemas
   - **Tempo**: 15-20 minutos

#### 3. **RESUMO_FINAL_ANALISE_GPU_13DEC.md**
   - **Propósito**: Resposta visual e direta às suas perguntas
   - **Conteúdo**:
     - Respostas diretas: "GPU está subutilizada? SIM"
     - Sumário executivo em português
     - Timeline: Windows → Kali → Ubuntu
     - Próximos passos com prioridades
   - **Leitura recomendada**: TERCEIRO (depois dos outros 2)
   - **Público**: Tomadores de decisão
   - **Tempo**: 5-10 minutos

#### 4. **ROTEIRO_EXECUCAO_IMEDIATA_13DEC.md**
   - **Propósito**: Guia passo-a-passo para rodar agora
   - **Conteúdo**:
     - Preparar ambiente (2 min)
     - Iniciar 3 terminais em paralelo
     - O que esperar em cada terminal
     - Análise pós-execução
     - Checklist final
   - **Leitura recomendada**: ANTES de executar scripts
   - **Público**: Operadores/executores
   - **Tempo**: 5 minutos (referência durante execução)

#### 5. **ANALISE_APURADA_PROBLEMAS_GPU_13DEC.md**
   - **Propósito**: Análise técnica profunda dos problemas identificados
   - **Conteúdo**:
     - Desaceleração exponencial (5s → 32s)
     - Φ base incorreta (0.6344 vs 0.6619)
     - Savepoint ineficiente
     - Dados numéricos de cada problema
   - **Leitura recomendada**: Para deep dive técnico
   - **Público**: Arquitetos de sistema
   - **Tempo**: 30-40 minutos

#### 6. **RESUMO_EXECUTIVO_SOLUCOES_13DEC.md**
   - **Propósito**: Executive summary das soluções implementadas
   - **Conteúdo**:
     - Antes vs Depois comparativo
     - Impact analysis quantitativa
     - ROI das otimizações
   - **Leitura recomendada**: Para stakeholders
   - **Público**: Gestores, stakeholders
   - **Tempo**: 10-15 minutos

#### 7. **GUIA_IMEDIATO_PHASE3_OTIMIZADO.md**
   - **Propósito**: Guia de execução otimizada do Phase 3
   - **Conteúdo**:
     - Como rodar novo script
     - Validação pós-execução
     - Troubleshooting comum
   - **Leitura recomendada**: Para quem vai executar
   - **Público**: Operadores
   - **Tempo**: 10 minutos

---

### 🔧 Scripts (scripts/)

#### 1. **scripts/recovery/03_run_integration_cycles_optimized.sh**
   - **Propósito**: Script principal otimizado com 3 soluções
   - **O que faz**:
     - Roda 500 ciclos de integração
     - Savepoints a cada 100 ciclos (não no final)
     - Φ base usa últimos 200 ciclos (não todos 500)
     - Memory tracking com tracemalloc
     - Qiskit GPU habilitado
   - **Como rodar**:
     ```bash
     bash scripts/recovery/03_run_integration_cycles_optimized.sh
     ```
   - **Output**:
     - `data/reports/integration_cycles_qiskit_phase3.json`
     - `logs/integration_cycles_optimized_*.log`
   - **Tempo**: ~3 horas (500 ciclos × 22s/ciclo)

#### 2. **scripts/diagnostics/monitor_gpu_utilization_realtime.sh**
   - **Propósito**: Monitor GPU em tempo real
   - **O que faz**:
     - Coleta SM Utilization a cada 2 segundos
     - Detecta se GPU está subutilizada
     - Gera CSV com métricas
     - Atualiza média a cada 60 segundos
   - **Como rodar** (em terminal separado):
     ```bash
     bash scripts/diagnostics/monitor_gpu_utilization_realtime.sh
     ```
   - **Output**:
     - `data/reports/gpu_utilization_*.csv`
     - Real-time console output
   - **O que procurar**: SM < 60% = subutilização

---

## 📋 ORDEM DE LEITURA RECOMENDADA

### Para Entender o Problema (30 min)
1. **RESUMO_FINAL_ANALISE_GPU_13DEC.md** (5 min) - Resposta direta
2. **ANALISE_PARALELIZACAO_GPU_WINDOWS_VS_LINUX.md** (20 min) - Técnica completa
3. **COMPARACAO_KALI_VS_UBUNTU_PARALELIZACAO.md** (5 min) - Dados numéricos

### Para Executar Agora (5 min)
1. **ROTEIRO_EXECUCAO_IMEDIATA_13DEC.md** - Leia enquanto roda

### Para Deep Dive Técnico (60 min)
1. **ANALISE_APURADA_PROBLEMAS_GPU_13DEC.md** (40 min)
2. **RESUMO_EXECUTIVO_SOLUCOES_13DEC.md** (20 min)

---

## 🎯 QUICK START

```bash
# 1. Leia resposta rápida
cat docs/RESUMO_FINAL_ANALISE_GPU_13DEC.md

# 2. Prepare para executar
cat docs/ROTEIRO_EXECUCAO_IMEDIATA_13DEC.md

# 3. Execute em Terminal 1
bash scripts/recovery/03_run_integration_cycles_optimized.sh

# 4. Execute em Terminal 2
bash scripts/diagnostics/monitor_gpu_utilization_realtime.sh

# 5. Execute em Terminal 3
nvidia-smi -l 2

# 6. Observe por 20-30 min (esperado: SM 45-60%)
```

---

## 📊 ARQUIVOS DE DADOS

### Gerados pela Execução

#### `data/reports/integration_cycles_qiskit_phase3.json`
- **Conteúdo**: 500 ciclos com métricas Φ/Ψ/σ/Δ
- **Tamanho**: ~8000 linhas
- **Formato**: JSON estruturado
- **O que procurar**:
  - `metrics.phi.mean`: Deve ser ~0.63-0.67
  - `metrics.phi.max`: Deve atingir 1.0 alguns ciclos
  - `elapsed_time_seconds`: ~11000s (estimado com otimizações)

#### `data/reports/gpu_utilization_*.csv`
- **Conteúdo**: Métrica de utilização GPU a cada 2s
- **Colunas**: timestamp, sm_util, mem_util, clock, power
- **O que procurar**:
  - `sm_util`: Deve ficar em 45-60% (subutilização esperada)
  - `mem_util`: Deve ficar em 25-35% (estável)

#### `logs/integration_cycles_optimized_*.log`
- **Conteúdo**: Log detalhado da execução
- **O que procurar**: Erros ou warnings incomuns

---

## 🔍 COMO ANALISAR RESULTADOS

### Pós-Execução (20 min)

```bash
# 1. Ver métricas Φ
python3 -c "
import json
data = json.load(open('data/reports/integration_cycles_qiskit_phase3.json'))
print(f'Φ Mean: {data[\"metrics\"][\"phi\"][\"mean\"]:.4f}')
print(f'Φ Max: {data[\"metrics\"][\"phi\"][\"max\"]:.4f}')
print(f'Duration: {data[\"elapsed_time_seconds\"]:.0f}s')
"

# 2. Analisar CSV GPU
python3 << 'EOF'
import csv
import glob

# Encontrar CSV mais recente
csv_file = sorted(glob.glob('data/reports/gpu_utilization_*.csv'))[-1]

with open(csv_file) as f:
    reader = csv.DictReader(f)
    sm_values = []

    for row in reader:
        if row['sm_util'] != 'N/A':
            sm_values.append(float(row['sm_util']))

    print(f"GPU SM Utilization:")
    print(f"  Min:  {min(sm_values):.1f}%")
    print(f"  Max:  {max(sm_values):.1f}%")
    print(f"  Avg:  {sum(sm_values)/len(sm_values):.1f}%")
    print(f"  → Esperado: 45-60% (subutilização)")
EOF

# 3. Ver últimas linhas do log
tail -50 logs/integration_cycles_optimized_*.log
```

---

## ⚠️ TROUBLESHOOTING

### Se Script Falhar
1. Verifique log: `tail -100 logs/integration_cycles_optimized_*.log`
2. Procure erros comuns:
   - "OOM Killer": Reduza savepoint interval (100 → 200 ciclos)
   - "Qiskit not available": `pip install qiskit qiskit-aer`
   - "GPU out of memory": Reduza batch size no código

### Se Monitor Não Funcionar
1. Verificar nvidia-smi: `nvidia-smi`
2. Se não funciona: `sudo apt-get install nvidia-utils`

### Se Resultados Estranhos
1. Consultar ROTEIRO_EXECUCAO_IMEDIATA_13DEC.md (seção Troubleshooting)
2. Ou ANALISE_APURADA_PROBLEMAS_GPU_13DEC.md (problemas conhecidos)

---

## 📞 PRÓXIMAS AÇÕES

### Imediato (Hoje)
- [ ] Rodar análise conforme ROTEIRO_EXECUCAO_IMEDIATA_13DEC.md
- [ ] Confirmar subutilização GPU (45-60% esperado)
- [ ] Salvar CSV com métricas

### Curto Prazo (Próxima Semana)
- [ ] Decidir: Implementar CUDA Graphs ou apenas aumentar batch size?
- [ ] Se CUDA Graphs: 2-4 horas trabalho, 40% ganho esperado
- [ ] Se batch size: 1 hora trabalho, 20% ganho esperado

### Longo Prazo
- [ ] Benchmark final vs Windows
- [ ] Documentar lições aprendidas

---

## 📚 REFERÊNCIAS EXTERNAS

### Documentação Relacionada no Projeto
- `docs/ANALISE_APURADA_PROBLEMAS_GPU_13DEC.md` - Problemas técnicos
- `docs/RESUMO_EXECUTIVO_SOLUCOES_13DEC.md` - Soluções implementadas
- Logs anteriores em `logs/` e `data/reports/`

### Benchmarks Kali
- `data/reports/integration_cycles_recovery.json` - Dados Kali (41 ciclos)
- `data/reports/integration_cycles_recovery.log` - Log Kali

---

## ✅ CHECKLIST DE LEITURA

- [ ] Li RESUMO_FINAL_ANALISE_GPU_13DEC.md
- [ ] Entendi root cause (Linux context switching overhead)
- [ ] Li ROTEIRO_EXECUCAO_IMEDIATA_13DEC.md
- [ ] Preparado para rodar scripts
- [ ] Entendi o que procurar (SM 45-60%, Memory 25-35%)
- [ ] Tenho 3 terminais prontos para paralelo

---

**Status**: 🟢 DOCUMENTAÇÃO COMPLETA
**Tempo leitura estimado**: 30-90 min (dependendo profundidade)
**Tempo execução**: ~3 horas (script roda em background)

