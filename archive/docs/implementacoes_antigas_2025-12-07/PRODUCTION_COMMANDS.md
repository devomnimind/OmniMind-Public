# Comandos de Produção - Phase 22

## 🚀 Iniciar Sistema Completo

```bash
cd /home/fahbrain/projects/omnimind
./scripts/start_production_phase22.sh
```

**O que faz**:
1. Limpa processos antigos
2. Cria estrutura de diretórios
3. Inicia Backend (porta 8000)
4. Inicia Ciclo Principal com Autopoiese (Phase 22)
5. Inicia Frontend (porta 5173)

**Serviços iniciados**:
- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- Ciclo Principal: `python -m src.main` (background)

## 🛑 Parar Sistema

```bash
cd /home/fahbrain/projects/omnimind
./scripts/stop_production.sh
```

## 📊 Monitorar Sistema

### Logs em Tempo Real

```bash
# Ciclo Principal (Autopoiese)
tail -f logs/main_cycle.log

# Backend
tail -f logs/backend_8000.log

# Frontend
tail -f logs/frontend.log
```

### Verificar Status

```bash
# Verificar processos
ps aux | grep -E "python -m src.main|uvicorn|vite"

# Verificar PIDs
cat logs/main_cycle.pid
cat logs/frontend.pid

# Health Check Backend
curl http://localhost:8000/health/
```

### Métricas de Consciência

```bash
# API de métricas (com dados brutos)
curl -u admin:omnimind2025! \
  "http://localhost:8000/api/v1/autopoietic/consciousness/metrics?include_raw=true" \
  | jq .

# Status autopoiético
curl -u admin:omnimind2025! \
  "http://localhost:8000/api/v1/autopoietic/status" \
  | jq .
```

## 🔬 Treinamento Estendido

```bash
cd /home/fahbrain/projects/omnimind
./scripts/run_production_training.sh
```

**Duração**: ~8-10 minutos (500 ciclos)

## 📈 Análise de Resultados

```bash
# Análise de logs de produção
python3 scripts/autopoietic/analyze_production_logs.py

# Verificar saúde de Φ
python3 scripts/autopoietic/check_phi_health.py

# Validação de consistência
PYTHONPATH=src:$PYTHONPATH python3 scripts/validate_metrics_consistency.py
```

## 🔄 Reiniciar Sistema

```bash
./scripts/stop_production.sh
sleep 5
./scripts/start_production_phase22.sh
```

## 📁 Estrutura de Dados

```
data/
├── autopoietic/
│   ├── synthesized_code/    # Componentes sintetizados
│   └── cycle_history.jsonl  # Histórico de ciclos
├── monitor/
│   └── real_metrics.json    # Métricas reais de consciência
├── sessions/                 # Sessões de treinamento
└── validation/               # Relatórios de validação

logs/
├── main_cycle.log           # Log do ciclo principal
├── backend_8000.log        # Log do backend
└── frontend.log            # Log do frontend
```

## 🎯 Endpoints Importantes

- **Dashboard**: http://localhost:5173
- **API Health**: http://localhost:8000/health/
- **Métricas Consciência**: http://localhost:8000/api/v1/autopoietic/consciousness/metrics?include_raw=true
- **Status Autopoiético**: http://localhost:8000/api/v1/autopoietic/status
- **Ciclos Autopoiéticos**: http://localhost:8000/api/v1/autopoietic/cycles

## ⚠️ Troubleshooting

### Backend não inicia
```bash
# Verificar logs
tail -50 logs/backend_8000.log

# Verificar porta
netstat -tulpn | grep 8000
```

### Ciclo Principal não inicia
```bash
# Verificar logs
tail -50 logs/main_cycle.log

# Verificar PYTHONPATH
echo $PYTHONPATH
```

### Frontend não inicia
```bash
# Verificar logs
tail -50 logs/frontend.log

# Reinstalar dependências
cd web/frontend && npm install
```

---

**Última atualização**: 2025-12-04
**Phase 22**: ✅ Implementado e Funcional

