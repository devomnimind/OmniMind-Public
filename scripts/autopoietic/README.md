# Scripts de Monitoramento e Análise Autopoiética (Phase 22)

Este diretório contém ferramentas para monitorar, analisar e diagnosticar o ciclo autopoiético em produção.

## 📊 Ferramentas Disponíveis

### 1. `monitor_autopoietic.sh` - Monitoramento Rápido

Script bash interativo que fornece visão geral rápida do sistema.

**Uso:**
```bash
./scripts/autopoietic/monitor_autopoietic.sh
```

**Verifica:**
- ✅ Status do processo do ciclo principal (PID, uptime)
- 📝 Últimas linhas do log com detecção de erros
- 📈 Estatísticas do histórico de ciclos
- 📁 Componentes sintetizados (últimos 5)
- 📊 Gera relatório completo automaticamente

**Saída:**
- Status colorido no terminal
- Relatório completo em `data/autopoietic/production_report.txt`

### 2. `analyze_production_logs.py` - Análise Detalhada

Script Python que analisa o histórico completo e gera relatório estatístico.

**Uso:**
```bash
python3 scripts/autopoietic/analyze_production_logs.py
```

**Análises:**
- Total de ciclos executados
- Taxa de sucesso vs rejeições vs rollbacks
- Métricas de Φ (média antes/depois, delta médio)
- Distribuição de estratégias (STABILIZE, OPTIMIZE, EXPAND)
- Lista completa de componentes sintetizados

**Saída:**
- Relatório formatado no terminal
- Arquivo: `data/autopoietic/production_report.txt`

### 3. `check_phi_health.py` - Verificação de Saúde

Script Python para verificação rápida de saúde do sistema baseado em Φ.

**Uso:**
```bash
python3 scripts/autopoietic/check_phi_health.py
```

**Verifica:**
- Φ atual do sistema (de `data/monitor/real_metrics.json`)
- Alertas se Φ < threshold (0.3) ou < warning threshold (0.4)
- Análise dos últimos 10 ciclos
- Detecção de rollbacks e rejeições frequentes

**Exit Codes:**
- `0`: Sistema saudável ou warnings
- `1`: Crítico (Φ abaixo do threshold ou muitos rollbacks)

**Uso em monitoramento:**
```bash
# Integração com cron ou sistemas de monitoramento
if ! python3 scripts/autopoietic/check_phi_health.py; then
    # Enviar alerta
    echo "Sistema autopoiético em estado crítico!"
fi
```

## 📁 Estrutura de Dados

### Arquivos Analisados

- `data/autopoietic/cycle_history.jsonl`: Histórico de todos os ciclos
- `data/autopoietic/synthesized_code/*.py`: Componentes sintetizados
- `data/monitor/real_metrics.json`: Métricas atuais de consciência
- `logs/main_cycle.log`: Log do ciclo principal

### Arquivos Gerados

- `data/autopoietic/production_report.txt`: Relatório completo de análise

## 🔄 Integração com Produção

### Monitoramento Contínuo

Adicione ao crontab para verificação periódica:

```bash
# Verificar saúde a cada hora
0 * * * * cd /home/fahbrain/projects/omnimind && ./scripts/autopoietic/check_phi_health.py >> logs/phi_health.log 2>&1

# Gerar relatório diário
0 0 * * * cd /home/fahbrain/projects/omnimind && python3 scripts/autopoietic/analyze_production_logs.py
```

### Alertas

O script `check_phi_health.py` pode ser integrado a sistemas de alerta:

```bash
# Exemplo com sistema de notificação
if ! python3 scripts/autopoietic/check_phi_health.py; then
    # Enviar email, Slack, etc.
    send_alert "Sistema autopoiético em estado crítico"
fi
```

## 📊 Exemplo de Relatório

```
======================================================================
RELATÓRIO DE ANÁLISE - CICLO AUTOPOIÉTICO (PHASE 22)
======================================================================

📊 ESTATÍSTICAS GERAIS
   Total de ciclos: 150
   Sínteses bem-sucedidas: 120
   Rejeitadas antes (Φ baixo): 20
   Rollbacks (Φ colapsou): 10

📈 MÉTRICAS DE Φ (PHI)
   Φ médio antes: 0.6543
   Φ médio depois: 0.6721
   Delta médio (ΔΦ): +0.0178

🔧 ESTRATÉGIAS UTILIZADAS
   EXPAND: 80 (53.3%)
   STABILIZE: 45 (30.0%)
   OPTIMIZE: 25 (16.7%)

🧬 COMPONENTES SINTETIZADOS
   Total sintetizado: 180
   Componentes únicos: 45
```

## 🛠️ Manutenção

### Limpeza de Logs Antigos

```bash
# Manter apenas últimos 1000 ciclos
tail -n 1000 data/autopoietic/cycle_history.jsonl > /tmp/cycle_history.jsonl
mv /tmp/cycle_history.jsonl data/autopoietic/cycle_history.jsonl
```

### Backup de Componentes

```bash
# Backup dos componentes sintetizados
tar -czf backups/autopoietic_components_$(date +%Y%m%d).tar.gz \
    data/autopoietic/synthesized_code/
```

## 📝 Notas

- Os scripts assumem que o projeto está em `/home/fahbrain/projects/omnimind`
- Requer Python 3.12+ e venv ativado
- Logs são escritos em `logs/` e dados em `data/autopoietic/`

