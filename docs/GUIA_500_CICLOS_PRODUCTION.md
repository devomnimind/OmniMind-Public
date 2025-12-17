# 🚀 Execução 500-Ciclos - Guia Rápido

## Estrutura de Saída

O novo script cria organização limpa:

```
data/monitor/executions/
├── index.json                                    # Índice global de todas execuções
├── execution_001_20251212_202500/                # Pasta da execução 1
│   ├── 1.json                                    # Ciclo 1
│   ├── 2.json                                    # Ciclo 2
│   ├── ...
│   ├── 500.json                                  # Ciclo 500
│   └── summary.json                              # Resumo da execução
├── execution_002_20251212_220000/                # Próxima execução
│   ├── 1.json
│   ├── 2.json
│   ...
```

## Executar

```bash
cd /home/fahbrain/projects/omnimind

# Método 1: Direto (recomendado)
python3 scripts/run_500_cycles_production.py

# Método 2: Com venv ativado
source .venv/bin/activate
python3 scripts/run_500_cycles_production.py

# Método 3: Com monitoramento em tempo real
# Terminal 1 - Executar script
python3 scripts/run_500_cycles_production.py

# Terminal 2 - Monitorar (durante execução)
watch -n 5 'ls -la data/monitor/executions/*/$(ls -td data/monitor/executions/*/ | head -1 | xargs basename)/ | tail -20'
```

## Estimativa

- **Batch size**: 64KB (otimizado para GTX 1650)
- **Tempo por ciclo**: ~6 segundos
- **500 ciclos**: ~50 minutos (3000 segundos)

## Monitoramento

Durante execução, observe:

```bash
# Terminal 2 - Ver ciclos sendo criados
watch -n 3 'ls -1 data/monitor/executions/$(ls -d data/monitor/executions/*/ | tail -1 | xargs basename)/ | wc -l'

# Terminal 3 - Ver PHI valores dos últimos ciclos
ls -t data/monitor/executions/*/[0-9]*.json | head -5 | xargs tail -n 1

# Terminal 4 - Ver CPU/GPU (opcional)
nvidia-smi loop 2
```

## Após Conclusão

Analisar resultados:

```python
import json
from pathlib import Path

# Carregar última execução
executions = sorted(Path("data/monitor/executions").glob("execution_*"))
latest = executions[-1]
summary = json.load(open(latest / "summary.json"))

print(f"Ciclos: {summary['completed_cycles']}")
print(f"PHI Final: {summary['phi_final']:.6f}")
print(f"PHI Max: {summary['phi_max']:.6f}")
print(f"PHI Avg: {summary['phi_avg']:.6f}")
print(f"Tempo: {summary['duration_seconds']:.0f}s")
```

## Troubleshooting

**Erro: "cannot allocate memory for thread-local data"**
- ✅ FIXADO - env vars já configurados no script (linhas 1-60)
- Se persistir: `ulimit -u unlimited`

**Processo parece travar no ciclo 100-150**
- Likely: Fragmentação GPU
- Solução: Aguarde (limpeza de cache ocorre a cada 50 ciclos)
- Ou: Press Ctrl+C e execute novamente

**Memória muito alta**
- Reduzir PYTORCH_ALLOC_CONF: `max_split_size_mb:32` em run_500_cycles_production.py (linha 52)
- Vai ficar mais lento mas mais estável

## Próximos Passos Após 500 Ciclos

1. ✅ Analisar dados (script Python)
2. ✅ Gerar plots de convergência PHI
3. ✅ Publicar em papers
4. ✅ Validação científica IIT
