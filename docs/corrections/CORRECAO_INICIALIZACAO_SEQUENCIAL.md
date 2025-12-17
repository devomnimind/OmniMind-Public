# Correção: Inicialização Sequencial de Serviços OmniMind

**Data**: 2025-12-09
**Autor**: Fabrício da Silva + assistência de IA
**Status**: ✅ Implementado

## Problema Original

O script `start_omnimind_system.sh` estava travando/bloqueando a máquina devido a:

1. **Inicialização paralela sem controle**: Múltiplos serviços iniciando simultaneamente
2. **Falta de verificação de saúde sequencial**: Serviços iniciando antes de dependências estarem prontas
3. **Timeouts inadequados**: Esperas fixas sem verificação real de saúde
4. **CPU alta durante inicialização**: Serviços pesados bloqueando o event loop

## Solução Implementada

### 1. Script Sequencial Dedicado
Criado `start_omnimind_sequential.sh` com:
- Health checks com retry para cada serviço
- Verificação de CPU antes de prosseguir
- Inicialização ordenada respeitando dependências
- Timeouts individuais por serviço

### 2. Atualização do Script Principal
`start_omnimind_system.sh` foi atualizado com:

#### Health Check Robusto para Backend
- Função `check_backend_health()` com retry (até 30 tentativas)
- Verificação de tempo de resposta (proxy para CPU)
- Contador de estabilidade (3 checks consecutivos)
- Timeout de 90s com diagnóstico em caso de falha

#### Verificação de CPU
- Função `check_cpu_stable()` que monitora CPU antes de prosseguir
- Aguarda CPU < 30% antes de iniciar serviços secundários
- Aborta se CPU > 80% por >30s (indica loop infinito)
- Logs detalhados de CPU durante espera

#### Inicialização Sequencial de Serviços Secundários
- **MCP Orchestrator**: Verifica Backend antes de iniciar
- **Ciclo Principal**: Verifica Backend antes de iniciar
- **Daemon**: Verifica Backend antes de iniciar
- Cada serviço verifica se processo iniciou corretamente
- Logs de sucesso/falha para cada serviço

## Estrutura de Inicialização

### TIER 1: CRÍTICOS (0-90s)
1. **Backend Cluster** (portas 8000, 8080, 3001)
   - Health check: `/health/` endpoint
   - Timeout: 90s com retry
   - Verificação de estabilidade: 3 checks consecutivos

### TIER 2: ESSENCIAIS (após Tier 1 estável)
2. **MCP Orchestrator**
   - Dependência: Backend Primary (8000)
   - Verificação: Processo rodando

3. **Ciclo Principal** (`src.main`)
   - Dependência: Backend Primary (8000)
   - Verificação: Processo rodando

4. **Daemon** (via API)
   - Dependência: Backend Primary (8000)
   - Verificação: `/daemon/status` endpoint

### TIER 3: SECUNDÁRIOS (após Tier 2)
5. **Observer Service**
6. **Frontend** (porta 3000)
7. **eBPF Monitor** (opcional)

## Melhorias Implementadas

### Health Checks
- ✅ Retry automático (até 30 tentativas para Backend)
- ✅ Verificação de tempo de resposta
- ✅ Contador de estabilidade
- ✅ Diagnóstico em caso de falha

### Controle de CPU
- ✅ Monitoramento antes de prosseguir
- ✅ Aguarda estabilização (< 30%)
- ✅ Aborta se crítica (> 80%)
- ✅ Logs detalhados

### Inicialização Sequencial
- ✅ Cada serviço só inicia após dependências prontas
- ✅ Verificação de processo após iniciar
- ✅ Logs de sucesso/falha
- ✅ Continua mesmo se serviço não-crítico falhar

## Arquivos Modificados

1. **`scripts/canonical/system/start_omnimind_sequential.sh`** (NOVO)
   - Script dedicado para inicialização sequencial
   - Health checks robustos
   - Verificação de CPU

2. **`scripts/canonical/system/start_omnimind_system.sh`** (ATUALIZADO)
   - Health check robusto para Backend
   - Verificação de CPU antes de prosseguir
   - Inicialização sequencial de serviços secundários
   - Verificações de saúde antes de cada serviço

3. **`docs/ANALISE_INICIALIZACAO_SERVICOS.md`** (NOVO)
   - Análise completa do problema
   - Identificação de serviços e dependências
   - Estratégia de correção

## Como Usar

### Script Principal (Recomendado)
```bash
cd /home/fahbrain/projects/omnimind
./scripts/canonical/system/start_omnimind_system.sh
```

### Script Sequencial Dedicado
```bash
cd /home/fahbrain/projects/omnimind
./scripts/canonical/system/start_omnimind_sequential.sh
```

## Validação

### Checklist de Testes
- [ ] Backend inicia e responde em < 90s
- [ ] CPU estabiliza antes de serviços secundários
- [ ] MCP Orchestrator inicia após Backend estável
- [ ] Ciclo Principal inicia após Backend estável
- [ ] Daemon inicia após Backend estável
- [ ] Sistema não bloqueia durante inicialização
- [ ] Logs mostram progresso sequencial

## Próximos Passos

1. ⏳ Testar inicialização completa em ambiente de desenvolvimento
2. ⏳ Validar que não bloqueia máquina
3. ⏳ Monitorar logs durante inicialização
4. ⏳ Ajustar timeouts se necessário

## Notas Técnicas

- Health checks usam `curl` com timeout de 3-5s
- CPU é verificada via `ps aux` somando processos Python
- Processos são verificados via `ps -p PID`
- Logs são salvos em `logs/` com timestamps

