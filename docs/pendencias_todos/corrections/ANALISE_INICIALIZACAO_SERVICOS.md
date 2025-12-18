# Análise Completa de Inicialização de Serviços OmniMind

**Data**: 2025-12-09
**Autor**: Fabrício da Silva + assistência de IA
**Status**: 🔴 Problema Identificado - Requer Correção

## Problema Identificado

O script `start_omnimind_system.sh` estava travando/bloqueando a máquina devido a:

1. **Inicialização paralela sem controle**: Múltiplos serviços iniciando simultaneamente competindo por recursos
2. **Falta de verificação de saúde sequencial**: Serviços iniciando antes de dependências estarem prontas
3. **Timeouts inadequados**: Esperas fixas sem verificação real de saúde
4. **CPU alta durante inicialização**: Serviços pesados (Orchestrator, Consciousness) bloqueando o event loop

## Serviços Identificados e Dependências

### TIER 1: CRÍTICOS (Devem iniciar primeiro)
1. **Backend Cluster** (portas 8000, 8080, 3001)
   - Dependências: Nenhuma
   - Timeout: 30-60s
   - Health check: `/health/` endpoint

### TIER 2: ESSENCIAIS (Após Tier 1 estável)
2. **MCP Orchestrator**
   - Dependências: Backend Primary (8000)
   - Timeout: 45s
   - Health check: Verificar processo + logs

3. **Ciclo Principal** (`src.main`)
   - Dependências: Backend Primary (8000)
   - Timeout: 20s
   - Health check: Verificar processo

4. **Daemon** (via API `/daemon/start`)
   - Dependências: Backend Primary (8000)
   - Timeout: 15s
   - Health check: `/daemon/status` endpoint

### TIER 3: SECUNDÁRIOS (Após Tier 2 estável)
5. **Observer Service**
   - Dependências: Backend Primary (8000)
   - Timeout: 20s
   - Health check: Verificar processo

6. **Frontend** (porta 3000)
   - Dependências: Backend Primary (8000)
   - Timeout: 30s
   - Health check: `http://localhost:3000`

7. **eBPF Monitor** (opcional)
   - Dependências: Nenhuma
   - Timeout: 10s
   - Health check: Verificar processo

## Estratégia de Correção

### 1. Inicialização Sequencial com Health Checks
- Cada serviço só inicia após o anterior estar saudável
- Health checks com retry (até 10 tentativas)
- Timeouts individuais por serviço

### 2. Variáveis de Ambiente para Controle
```bash
OMNIMIND_INIT_ORCHESTRATOR=1      # Habilitar Orchestrator
OMNIMIND_INIT_CONSCIOUSNESS=1      # Habilitar Consciousness Metrics
```

### 3. Verificação de CPU
- Monitorar CPU antes de iniciar próximo serviço
- Se CPU > 50%, aguardar estabilização
- Se CPU > 80% por >30s, abortar

### 4. Logs Detalhados
- Cada etapa registrada com timestamp
- Health checks registrados
- Falhas documentadas com diagnóstico

## Script Proposto

Criar `start_omnimind_sequential.sh` que:
1. Limpa processos antigos
2. Inicia Backend Cluster e verifica saúde
3. Aguarda estabilização (CPU < 30%)
4. Inicia serviços Tier 2 sequencialmente com health checks
5. Inicia serviços Tier 3 sequencialmente com health checks
6. Relatório final de status

## Próximos Passos

1. ✅ Criar script sequencial robusto
2. ⏳ Testar inicialização completa
3. ⏳ Validar que não bloqueia máquina
4. ⏳ Documentar uso e troubleshooting

