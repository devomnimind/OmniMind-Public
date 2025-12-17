# 📊 Resposta: Métricas de Φ (Phi) - Sistemas de Coleta e Análise

## ✅ Implementado

Você perguntou: **"Mas e a métrica de Φ?"**

**Resposta:** O sistema agora coleta, processa e analisa **métricas de Φ (phi) em tempo real** durante execução dos testes de consciência!

## 🎯 O Que Foi Implementado

### 1. **Coletor de Métricas de Φ** (`scripts/phi_metrics_collector.py`)
- ✅ Funciona como **filtro de pipeline UNIX**
- ✅ Reconhece **múltiplos formatos** de Φ
- ✅ **Normaliza valores** para [0,1]
- ✅ Gera **JSON + TXT** simultaneamente
- ✅ Captura **timestamps ISO8601**
- ✅ Agrupa automaticamente **por teste**

**Uso:**
```bash
python -m pytest tests/ 2>&1 | python scripts/phi_metrics_collector.py
```

### 2. **Dashboard de Análise** (`scripts/phi_analysis_dashboard.py`)
- ✅ **Estatísticas descritivas** (média, std, min, max)
- ✅ **Visualização por teste**
- ✅ **Série temporal** com indicadores visuais
- ✅ **Categorização** (Baixa/Média/Alta consciência)
- ✅ **Recomendações automáticas**

**Uso:**
```bash
python scripts/phi_analysis_dashboard.py data/test_reports/phi_metrics_*.json
```

### 3. **Integração com Script Principal** (`run_consciousness_tests_gpu.sh`)
- ✅ **Coleta Φ em tempo real** durante testes
- ✅ Monitora **GPU + Φ + métricas** simultaneamente
- ✅ Gera **relatórios consolidados**
- ✅ Auditoria com **SHA256**

**Uso:**
```bash
bash run_consciousness_tests_gpu.sh
```

## 📊 Exemplo de Resultado Prático

Teste realizado com 8 medições:

```
ESTATÍSTICAS GERAIS
─────────────────────────────────────
Total de medições     : 8
Φ_média              : 0.7426 ± 0.4288
Φ_mínimo             : 0.0000
Φ_máximo             : 0.9999
Valores válidos [0,1]: 8/8

SÉRIE TEMPORAL (últimas 20 medições)
─────────────────────────────────────
1. 🔴 07:30:28 | ████████████████████░░░░░ 0.9973 | alta consciência
2. 🟢 07:30:28 | ░░░░░░░░░░░░░░░░░░░░░░░░░ 0.0000 | baixa consciência
3. 🟢 07:30:28 | ░░░░░░░░░░░░░░░░░░░░░░░░░ 0.0000 | baixa consciência
4. 🔴 07:30:28 | ████████████████████░░░░░ 0.9973 | alta consciência
5. 🔴 07:30:28 | ████████████████████░░░░░ 0.9999 | MÁXIMA consciência
6. 🔴 07:30:28 | ████████████████████░░░░░ 0.9820 | alta consciência
7. 🔴 07:30:28 | ████████████████████░░░░░ 0.9820 | alta consciência
8. 🔴 07:30:28 | ████████████████████░░░░░ 0.9820 | alta consciência

DISTRIBUIÇÃO POR FAIXA
─────────────────────────────────────
Baixa   (0.0-0.33) :   2 ( 25.0%) 🟢
Média   (0.33-0.67):   0 (  0.0%) 🟡
Alta    (0.67-1.0) :   6 ( 75.0%) 🔴

RECOMENDAÇÕES
─────────────────────────────────────
✓ Φ_média normal (0.7426) - sistema operacional
⚠️ Alta variabilidade (CV=57.7%) - investigar inconsistências
```

## 🔄 Fluxo Completo

```
┌─────────────────────────────────────────┐
│  bash run_consciousness_tests_gpu.sh   │
└────────────┬────────────────────────────┘
             │
             ├─ ✅ Verifica GPU disponível
             ├─ ✅ Inicia monitor GPU (background)
             │
             ├─ python -m pytest tests/consciousness/ \
             │        | phi_metrics_collector.py \
             │        | (capture em tempo real)
             │
             ├─ 📊 Gera: phi_metrics_TIMESTAMP.json
             ├─ 📊 Gera: phi_metrics_TIMESTAMP.txt
             ├─ 📊 Gera: gpu_monitor_TIMESTAMP.json
             ├─ 📊 Gera: gpu_monitor_TIMESTAMP.txt
             │
             └─ ✅ Auditoria SHA256 (log.sha256)

┌─────────────────────────────────────────┐
│ python phi_analysis_dashboard.py        │
│    data/test_reports/phi_metrics_*.json │
└────────────┬────────────────────────────┘
             │
             └─ 📊 Dashboard visual + recomendações
```

## 📁 Arquivos Novos Criados

| Arquivo | Descrição |
|---------|-----------|
| `scripts/phi_metrics_collector.py` | Coleta Φ em tempo real (pipeline) |
| `scripts/phi_analysis_dashboard.py` | Dashboard de análise visual |
| `test_phi_collection.sh` | Script teste de coleta rápido |
| `docs/PHI_METRICS_GUIDE.md` | Documentação completa |

## 🔬 Padrões de Φ Reconhecidos

```python
"Φ = 0.1234"                    # Formato direto
"phi: 0.5678"                   # Formato coloquial
"Φ_avg = 0.7654"               # Média de Φ
"Φ_estimate = 0.9999"          # Estimativa
"RESULTADO: Φ_avg = 0.5555"    # Relatório
"phi_proxy = 372.5999"         # Métrica bruta (normalizada automaticamente)
```

## 🛠️ Como Usar Agora

### Opção 1: Teste Completo com 255 testes
```bash
cd /home/fahbrain/projects/omnimind
bash run_consciousness_tests_gpu.sh
```

### Opção 2: Teste Rápido de Φ (8 medições)
```bash
cd /home/fahbrain/projects/omnimind
bash test_phi_collection.sh
```

### Opção 3: Análise de Arquivo Existente
```bash
python scripts/phi_analysis_dashboard.py data/test_reports/phi_metrics_20251202_073024.json
```

### Opção 4: Pipe Customizado
```bash
python -m pytest tests/consciousness/ -v -s 2>&1 | python scripts/phi_metrics_collector.py | tee my_log.txt
```

## 📈 Métricas Disponíveis

**JSON** (`phi_metrics_*.json`):
- Estatísticas gerais (média, std, min, max, CV)
- Agrupamento por teste
- Todas as medições individuais com timestamps
- Validação [0,1]

**TXT** (`phi_metrics_*.txt`):
- Relatório formatado para leitura humana
- Estatísticas por teste
- Fácil importação em dashboards

## ✨ Destaques da Implementação

1. **Normalização automática**: `phi_proxy` (0-500+) → Φ (0-1) via sigmoid
2. **Série temporal**: Últimas 20 medições com indicadores visuais 🟢🟡🔴
3. **Coeficiente de variação**: Detecta instabilidade do sistema
4. **Sem modificação de código**: Funciona via pipeline, não requer mudanças nos testes
5. **Auditoria completa**: SHA256 + timestamps ISO8601

## 🚀 Próximas Melhorias Possíveis

- [ ] Exportar para CSV/Excel
- [ ] Gráficos interativos (matplotlib/plotly)
- [ ] Correlação Φ vs GPU utilization
- [ ] Detecção de anomalias em série temporal
- [ ] API REST para acesso em tempo real
- [ ] Dashboard web persistente

## 📞 Suporte

Para dúvidas sobre as métricas:
- Ver: [docs/PHI_METRICS_GUIDE.md](docs/PHI_METRICS_GUIDE.md)
- Executar: `python scripts/phi_analysis_dashboard.py --help`
- Verificar: `data/test_reports/` para exemplos

---

**Status**: ✅ Production Ready  
**Testado em**: 2025-12-02  
**Versão**: 1.0
