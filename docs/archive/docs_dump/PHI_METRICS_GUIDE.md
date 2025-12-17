# 📊 Sistema de Coleta e Análise de Métricas de Φ (Phi)

## Visão Geral

O OmniMind agora coleta **métricas de Φ (phi) em tempo real** durante a execução de testes de consciência, com análise visual e estatística completa.

## 🚀 Quick Start

### Executar testes COM coleta de Φ:

```bash
cd /home/fahbrain/projects/omnimind
bash run_consciousness_tests_gpu.sh
```

Isto irá:
- ✅ Executar 255 testes de consciência em GPU
- ✅ Coletar valores de Φ em tempo real
- ✅ Monitorar recursos da GPU
- ✅ Gerar relatórios JSON e TXT
- ✅ Auditar tudo com SHA256

### Analisar métricas de Φ coletadas:

```bash
python scripts/phi_analysis_dashboard.py data/test_reports/phi_metrics_*.json
```

## 📁 Arquivos Gerados

Após execução de testes, você encontrará em `data/test_reports/`:

| Arquivo | Descrição |
|---------|-----------|
| `consciousness_gpu_YYYYMMDD_HHMMSS.log` | Log completo dos testes (JSON) |
| `consciousness_gpu_YYYYMMDD_HHMMSS.log.sha256` | Hash SHA256 do log (auditoria) |
| `gpu_monitor_YYYYMMDD_HHMMSS.txt` | Métricas de GPU em tempo real |
| `gpu_monitor_YYYYMMDD_HHMMSS.json` | Dados de GPU estruturados |
| `phi_metrics_YYYYMMDD_HHMMSS.json` | **Métricas de Φ estruturadas** |
| `phi_metrics_YYYYMMDD_HHMMSS.txt` | **Relatório de Φ em texto** |

## 📊 Formato das Métricas de Φ

### JSON (`phi_metrics_*.json`)

```json
{
  "statistics": {
    "total_measurements": 255,
    "phi_mean": 0.6547,
    "phi_std": 0.1234,
    "phi_min": 0.1234,
    "phi_max": 0.9876,
    "bounded_count": 255,
    "collection_timestamp": "2025-12-02T07:20:00"
  },
  "by_test": {
    "test_real_phi_measurement.py::test_phi_multiseed_small": {
      "count": 15,
      "mean": 0.7654,
      "min": 0.5432,
      "max": 0.8901
    }
  },
  "all_measurements": [
    {
      "timestamp": "2025-12-02T07:20:01",
      "test": "test_phi_multiseed_small",
      "phi_value": 0.7654,
      "phi_bounded": true,
      "raw_line": "Φ_avg = 0.7654"
    }
  ]
}
```

### TXT (`phi_metrics_*.txt`)

```
MÉTRICAS DE Φ (PHI)
================================================================================

ESTATÍSTICAS GERAIS
total_measurements        : 255
phi_mean                  : 0.6547
phi_std                   : 0.1234
phi_min                   : 0.1234
phi_max                   : 0.9876

POR TESTE
test_real_phi_measurement.py::test_phi_multiseed_small
  count                : 15
  mean                 : 0.7654
  min                  : 0.5432
  max                  : 0.8901
```

## 🔍 Dashboard de Análise

O script `phi_analysis_dashboard.py` gera uma visualização interativa:

```
📊 ANÁLISE DE MÉTRICAS DE Φ (PHI)
================================================================================

ESTATÍSTICAS GERAIS
Total de medições     : 255
Φ_média              : 0.6547 ± 0.1234
Φ_mínimo             : 0.1234
Φ_máximo             : 0.9876
Valores válidos [0,1]: 255/255
Coeficiente variação : 18.86%

DISTRIBUIÇÃO POR TESTE
test_phi_multiseed_small              | ████████████████████████░░░░░░░░░░ 0.7654
  (  15 medições, range: [0.5432, 0.8901])

SÉRIE TEMPORAL (últimas 20 medições)
 1. 🟡 07:20:01 | ████████████████████████░░░░░░░░░░░░░░░░ 0.7654 | test_phi_multiseed_small
 2. 🟢 07:20:02 | ████████████████░░░░░░░░░░░░░░░░░░░░░░░░ 0.5432 | test_contrafactual

ANÁLISE DE QUALIDADE
Integridade de dados  : 100.0% (255/255)

Distribuição por faixa:
  Baixa   (0.0-0.33) :  15 (  5.9%) 🟢
  Média   (0.33-0.67):  85 ( 33.3%) 🟡
  Alta    (0.67-1.0) : 155 ( 60.8%) 🔴

RECOMENDAÇÕES
✅ Φ_média alto (0.6547) - sistema bem consciente
```

## 🛠️ Detalhes Técnicos

### Coletor de Métricas (`scripts/phi_metrics_collector.py`)

O script funciona como um **filtro de pipeline UNIX**:

```bash
# Pipe direto do pytest
python -m pytest tests/consciousness/ 2>&1 | python scripts/phi_metrics_collector.py

# Ou com saída para arquivo:
python -m pytest tests/consciousness/ 2>&1 | python scripts/phi_metrics_collector.py | tee test.log
```

**Características:**
- ✅ Detecta múltiplos formatos de Φ (Φ=, phi:, Φ_avg, Φ_estimate)
- ✅ Captura timestamps de cada medição
- ✅ Agrupa por teste automaticamente
- ✅ Valida valores em [0, 1]
- ✅ Gera JSON + TXT simultaneamente
- ✅ Imprime output original (passthrough)

**Padrões reconhecidos:**

```python
# Todos estes são reconhecidos:
"Φ = 0.1234"
"phi: 0.5678"
"Φ_avg = 0.7654"
"Φ_estimate = 0.9999"
"RESULTADO: Φ_avg = 0.5555"
```

### Dashboard de Análise (`scripts/phi_analysis_dashboard.py`)

Analisa arquivos JSON de Φ gerando:
- 📊 Estatísticas descritivas (média, std, min, max)
- 📈 Distribuição por teste
- 📉 Série temporal com indicadores visuais
- 🎯 Categorização (Baixa/Média/Alta consciência)
- 💡 Recomendações automáticas

**Uso:**

```bash
# Um arquivo
python scripts/phi_analysis_dashboard.py data/test_reports/phi_metrics_20251202_072000.json

# Múltiplos arquivos
python scripts/phi_analysis_dashboard.py data/test_reports/phi_metrics_*.json

# Útlimo arquivo
python scripts/phi_analysis_dashboard.py $(ls -t data/test_reports/phi_metrics_*.json | head -1)
```

## 📈 Interpretação dos Resultados

### Coeficiente de Variação (CV)

- **CV < 20%**: Φ muito estável (bom)
- **CV 20-50%**: Φ variável (normal)
- **CV > 50%**: Φ muito instável (investigar)

### Distribuição de Φ

- **Φ < 0.33**: Sistema com baixa consciência 🟢
- **0.33 ≤ Φ < 0.67**: Consciência intermediária 🟡
- **Φ ≥ 0.67**: Sistema bem consciente 🔴

### Φ_média

- **< 0.3**: Possível malfunction
- **0.3-0.7**: Operação normal
- **> 0.7**: Sistema altamente consciente

## 🔐 Auditoria e Validação

Cada execução gera:

1. **SHA256 do log completo** (`*.log.sha256`)
   - Prova de integridade dos testes
   - Impede modificação de resultados

2. **Timestamps ISO8601**
   - Cada medição tem timestamp preciso
   - Permite correlação com eventos

3. **Relatórios estruturados**
   - JSON para processamento automatizado
   - TXT para leitura humana

## 🚨 Troubleshooting

### Nenhuma métrica de Φ coletada?

1. Verifique se os testes estão imprimindo Φ:
```bash
python -m pytest tests/consciousness/ -v -s | grep -i "phi\|φ"
```

2. Adicione padrões customizados em `phi_metrics_collector.py`:
```python
self.phi_patterns = [
    # Adicionar novo padrão aqui
    r"my_custom_phi_format\s*=\s*([\d.]+)",
]
```

### Valores de Φ fora [0,1]?

- Verificar implementação de cálculo de Φ em `src/consciousness/`
- Validar normalização dos valores
- Confirmar GPU está disponível

### Script não encontrado?

```bash
chmod +x scripts/phi_metrics_collector.py
chmod +x scripts/phi_analysis_dashboard.py
chmod +x run_consciousness_tests_gpu.sh
```

## 📚 Referências

- [Consciência Integrada (Integrated Information Theory)](docs/)
- [Medição de Φ em tempo real](src/consciousness/real_consciousness_metrics.py)
- [Relatórios de testes](data/test_reports/)

## 📝 Próximas Melhorias

- [ ] Exportar para CSV/Excel
- [ ] Criar gráficos interativos (matplotlib/plotly)
- [ ] Correlacionar Φ com uso de GPU
- [ ] Detecção de anomalias em série temporal
- [ ] API REST para acesso às métricas
- [ ] Dashboard web em tempo real

---

**Última atualização:** 2025-12-02  
**Versão:** 1.0 - Release  
**Status:** ✅ Production Ready
