# OmniMind Auto-Recovery Setup Guide

## Visão Geral

O sistema OmniMind inclui um mecanismo automático de detecção e recuperação de falhas. Para funcionamento completo, é necessário configurar o sudo para permitir execução sem senha de scripts críticos.

## Arquivos Envolvidos

### Scripts de Inicialização

- **`scripts/start_omnimind_system_wrapper_v2.sh`** (NOVO)
  - Wrapper inteligente que seleciona versão robusta automaticamente
  - Suporta auto-recovery com sudo
  - DEVE SER O SCRIPT PRINCIPAL

- **`scripts/canonical/system/start_omnimind_system_robust.sh`** (NOVO)
  - Versão robusta com melhorias de health check
  - Health check com estado persistente
  - CPU meter corrigido
  - Logging detalhado

- **`scripts/canonical/system/start_omnimind_system_sudo_auto.sh`** (NOVO)
  - Script de auto-recovery executado com sudo
  - Detecção automática de problemas
  - Recuperação não-interativa

- **`scripts/start_omnimind_system_sudo.sh`** (EXISTENTE)
  - Wrapper com elevação sudo
  - Chama script oficial

## Setup de Sudo para Auto-Recovery

### Opção 1: Setup Seguro (Recomendado)

```bash
# 1. Editar sudoers com visudo (OBRIGATÓRIO - nunca edite /etc/sudoers diretamente)
sudo visudo

# 2. Adicionar ao FINAL do arquivo (antes de qualquer outro include):
# Substitua $USER pelo seu usuário real (ex: fahbrain)
$USER ALL=(ALL) NOPASSWD: /home/fahbrain/projects/omnimind/scripts/canonical/system/start_omnimind_system_sudo_auto.sh

# 3. Salvar com Ctrl+X, confirmar com 'yes'

# 4. TESTAR (sem pedir senha):
sudo -n /home/fahbrain/projects/omnimind/scripts/canonical/system/start_omnimind_system_sudo_auto.sh --help
```

### Opção 2: Setup via Script Auxiliar

```bash
# Usar script de configuração fornecido
./scripts/configure_sudo_omnimind.sh

# Ou manual:
echo "$USER ALL=(ALL) NOPASSWD: $PWD/scripts/canonical/system/start_omnimind_system_sudo_auto.sh" | sudo tee /etc/sudoers.d/omnimind
sudo chmod 440 /etc/sudoers.d/omnimind
```

### Verificar Setup

```bash
# Verificar se sudo -n funciona
sudo -n true && echo "✅ Sudo sem senha OK" || echo "❌ Precisa de senha"

# Testar execução sem senha
sudo -n bash -c 'echo "✓ Script executado com sudo sem senha"'
```

## Melhorias na Versão Robusta

### 1. Health Check com Estado Persistente

```bash
# ANTES (v1.0):
# - Verifica rápido com timeout=3s
# - Se falha, reinicia TODOS os backends mesmo que alguns estejam OK
# - Race condition: confirma sucesso mas depois falha

# DEPOIS (v2.0 Robusta):
# - Estados persistem entre verificações (BACKEND_HEALTH_CACHE)
# - Lógica OR: se ANY backend ruim → reinicia
# - Não mais lógica AND com todas as portas
```

### 2. CPU Meter Corrigido

```bash
# ANTES:
# top -bn1 | awk '{sum+=$9}' → Soma percentual (pode > 100% em multi-core)
# Exemplo: 4 cores × 100% = 400% (confuso)

# DEPOIS:
# ps aux | grep python | awk '{sum+=$3}'
# Normalizar: /num_cores → % do sistema (0-100%)
# Exemplo: 400% / 4 = 100% do sistema
```

### 3. Timeout Unificado

```bash
# ANTES:
# Alguns checks usam timeout=3s, outros=5s
# Inconsistência leva a decisões erradas

# DEPOIS:
# Variável: HEALTH_CHECK_TIMEOUT=5
# Usada em todos os checks
# Configurável via variável de ambiente
```

### 4. Logging Detalhado

```bash
# Novo arquivo de log:
logs/startup_detailed.log

# Cada ação loggada com timestamp ISO:
# [2025-12-11T15:30:45.123Z] [INFO] Backend Primary inicializando...
# [2025-12-11T15:30:47.456Z] [SUCCESS] Backend Primary estável
# [2025-12-11T15:31:05.789Z] [ERROR] Backend Secondary não respondeu

# Debug mode:
export OMNIMIND_DEBUG=true
./scripts/start_omnimind_system_wrapper_v2.sh
```

## Fluxo de Auto-Recovery

### Detecção Automática

1. OmniMind monitora saúde dos serviços
2. Se detecta falha (backend down, frontend crashed):
   - Log: `data/long_term_logs/omnimind_metrics.jsonl`
   - Alert: systemd journal, syslog

3. OmniMind invoca auto-recovery:
   ```bash
   sudo -n /home/.../start_omnimind_system_sudo_auto.sh
   ```

### Processo de Recovery

```
PHASE 1: DIAGNÓSTICO
  ├─ Verificar Backend Primary (8000)
  ├─ Verificar Frontend
  └─ Verificar Ciclo Principal

PHASE 2: RECOVERY (Limpeza)
  ├─ Matar processos zumbis
  ├─ Limpar sockets dangling
  └─ Aguardar 3s

PHASE 3: REINICIALIZAÇÃO
  ├─ Executar startup robusto
  ├─ Health check com retry
  └─ Validar cada serviço

PHASE 4: VALIDAÇÃO
  ├─ Confirmar Backend respondendo
  ├─ Confirmar Frontend rodando
  └─ Gerar relatório de recovery
```

## Testando o Sistema

### Teste 1: Inicialização Normal

```bash
./scripts/start_omnimind_system_wrapper_v2.sh
```

Esperado: Inicializa com versão robusta

### Teste 2: Simular Falha de Backend

```bash
# Terminal 1: Inicializar
./scripts/start_omnimind_system_wrapper_v2.sh

# Terminal 2: Simular falha
pkill -9 -f 'uvicorn.*8000'

# Terminal 3: Verificar recovery automático (se monitorado)
# Ou executar manualmente:
sudo -n /path/to/start_omnimind_system_sudo_auto.sh
```

Esperado: Auto-recovery detecta e reinicia Backend Primary

### Teste 3: Debug Mode

```bash
export OMNIMIND_DEBUG=true
./scripts/start_omnimind_system_wrapper_v2.sh

# Vê logs detalhados de cada check:
tail -f logs/startup_detailed.log
```

## Troubleshooting

### "Sudo requer senha"

```bash
# Verificar permissões
sudo -l | grep start_omnimind

# Se não aparecer, configuração não foi salva
# Repetir setup com visudo
sudo visudo
```

### "Health check falhando mesmo com backend respondendo"

```bash
# Ver logs detalhados
cat logs/startup_detailed.log | grep -i "port 8000"

# Testar curl diretamente
curl -v http://localhost:8000/health/

# Verificar se porta está realmente aberta
ss -tlnp | grep 8000
# ou
netstat -tlnp | grep 8000
```

### "CPU meter não bate com realidade"

```bash
# Ver cálculo atual
ps aux | grep python | awk '{print $3, $11}' | sort -rn

# Num cores do sistema
nproc

# Cálculo esperado
# Total CPU / nproc = % do sistema
```

## Variáveis de Ambiente

```bash
# Debug mode (mais verbose)
export OMNIMIND_DEBUG=true

# Auto-recovery automático (usado internamente)
export OMNIMIND_AUTO_RECOVERY=true

# Custom timeout para health check (segundos)
export OMNIMIND_HEALTH_CHECK_TIMEOUT=10

# Custom retries para backends essenciais
export OMNIMIND_HEALTH_CHECK_RETRIES_ESSENTIAL=150

# Log file customizado
export OMNIMIND_STARTUP_LOG="/custom/path/startup.log"
```

## Performance

- **Overhead de health checks**: <5% de CPU
- **Timeout inicial**: ~5 minutos para carregamento de modelos
- **Recovery time**: ~2-3 minutos (limpeza + reinicialização)
- **Log rotation**: Automático em 5MB (arquivo anterior renomeado)

## Monitoramento Contínuo

Para monitoramento em produção:

```bash
# Terminal dedicado para logs
tail -f logs/startup_detailed.log

# Monitor de processos
watch -n 1 'ps aux | grep -E "[u]vivicorn|[n]pm.*dev|[p]ython.*src"'

# Monitor de saúde
while true; do
    curl -s http://localhost:8000/health/ && echo "✓ OK" || echo "✗ FAIL"
    sleep 5
done
```

## Próximas Melhorias

1. ✅ Health check com estado persistente
2. ✅ CPU meter corrigido
3. ⏳ Integração com systemd para auto-restart
4. ⏳ Alertas via webhook/Slack
5. ⏳ Dashboard de recovery metrics
6. ⏳ Análise preditiva de falhas

## Suporte

Para problemas ou sugestões:

1. Verificar logs: `logs/startup_detailed.log`
2. Testar manualmente: `sudo -n bash scripts/canonical/system/start_omnimind_system_sudo_auto.sh`
3. Reportar com: `tail -n 50 logs/startup_detailed.log`
