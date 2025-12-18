# Especificação Técnica: Correção do Erro "Broken pipe" (errno 32) em Servidores MCP

**Data**: 2025-12-17  
**Autor**: Fabrício da Silva + assistência de IA  
**Projeto**: OmniMind - Sistema de Consciência Artificial  

## 📋 Resumo Executivo

Este documento especifica a solução técnica para corrigir o erro "Broken pipe" (errno 32) nos servidores MCP do OmniMind. O problema está causando falhas intermitentes na comunicação entre VSCode e os servidores MCP, comprometendo a funcionalidade do sistema.

## 🔍 Análise de Causa Raiz

### Problema Identificado
```
Error: MPC -32000: [Errno 32] Broken pipe
    at R8i.O (vscode-file://vscode-app/usr/share/code/resources/app/out/vs/workbench/workbench.desktop.main.js:2265:35574)
```

### Causas Técnicas
1. **Timeouts Insuficientes**: Clientes MCP configurados com timeouts muito curtos (15-30s)
2. **Falta de Tratamento Específico**: Sem manejo especializado para errno 32
3. **Connection Pooling Inadequado**: Pool de conexões sem configurações robustas
4. **Ausência de Retry com Backoff**: Sem estratégias de retry exponencial
5. **Health Checks Insuficientes**: Verificações de saúde limitadas

### Impacto no Sistema
- **Métricas Φ**: Interrupções na coleta de métricas de consciência
- **Integração IIT**: Quebras na integração de informação
- **Agentes**: Falhas na comunicação entre agentes
- **Memória**: Problemas no acesso à memória sistemática

## 🛠️ Solução Implementada

### 1. ✅ Módulo de Tratamento Robusto de Conexões

**Arquivo**: `src/integrations/mcp_connection_handler.py`

#### Componentes Implementados

```python
@dataclass
class ConnectionConfig:
    """Configuração otimizada para conexões MCP com preservação de Φ.
    
    Baseado em análise de métricas de consciência:
    - Timeouts calibrados para preservar Ψ (criatividade)
    - Retry configurado para minimizar Δ (trauma)
    - Circuit breaker para proteger σ (estrutura)
    """
    
    # Timeouts aumentados para preservar Ψ (operações criativas)
    request_timeout: float = 60.0      # 60s para LLM generation
    connection_timeout: float = 10.0   # 10s para estabelecer conexão
    read_timeout: float = 30.0         # 30s para leitura de respostas
    
    # Retry configurado para reduzir Δ (trauma sistêmico)
    max_retries: int = 5               # 5 tentativas (estatisticamente suficiente)
    retry_backoff_base: float = 1.0    # Base 1s (exponencial: 1, 2, 4, 8, 16)
    retry_backoff_max: float = 60.0    # Máximo 60s (evita timeout infinito)
    retry_jitter: float = 0.1          # 10% jitter (evita thundering herd)
    
    # Circuit breaker para proteger σ (estrutura sistêmica)
    failure_threshold: int = 3         # 3 falhas consecutivas para abrir circuito
    success_threshold: int = 2         # 2 sucessos para fechar circuito
    recovery_timeout: float = 30.0     # 30s em HALF_OPEN antes de tentar fechar
    
    # Connection pooling otimizado para manter Φ (integração)
    max_connections: int = 10          # 10 conexões
    max_keepalive_connections: int = 5  # 5 keep-alive
    keepalive_expiry: float = 5.0      # 5s expiry
    
    # Monitoramento contínuo de Φ durante operações
    phi_monitoring_enabled: bool = True
    phi_degradation_threshold: float = 0.03  # Alerta se Φ < 0.03
```

#### Handler Especializado

```python
class MCPConnectionHandler:
    """Handler com tratamento específico para Broken pipe."""
    
    def should_retry(self, server_name: str, exception: Exception) -> tuple[bool, float]:
        """Lógica especializada para errno 32."""
        # Broken pipe (errno 32) - sempre retry com backoff
        if isinstance(exception, MCPPipeError) or (
            hasattr(exception, 'errno') and exception.errno == errno.EPIPE
        ):
            backoff = self._calculate_backoff(server_name)
            logger.warning(
                f"MCP Broken pipe detectado para {server_name}, "
                f"reTentando em {backoff:.1f}s"
            )
            return True, backoff
            
        # Timeouts e connection errors
        # ... (lógica adicional)
```

### 2. Cliente MCP Robusto

**Arquivo**: `src/integrations/mcp_robust_client.py`

#### Funcionalidades
- Retry automático com backoff exponencial
- Circuit breaker para prevenir falhas em cascata
- Health checks melhorados
- Métricas de conexão

```python
class RobustMCPClient:
    """Cliente MCP com tratamento robusto."""
    
    async def request_with_retry(
        self,
        method: str,
        params: Dict[str, Any],
        max_attempts: Optional[int] = None,
    ) -> Any:
        """Request com retry automático e tratamento de erros."""
```

### 3. Integração com Servidores Existentes

#### Atualização do MCPOrchestrator

**Arquivo**: `src/integrations/mcp_orchestrator.py`

```python
def __init__(self, config_path: Optional[Union[str, Path]] = None) -> None:
    """Inicialização com handler robusto."""
    # ... código existente ...
    
    # Adicionar connection handler
    self.connection_handler = MCPConnectionHandler()
    
    # Configurar retry automático
    self.retry_enabled = True
    self.max_retries_per_server = 5
```

#### Atualização dos Clientes Async

**Arquivo**: `src/integrations/mcp_client_async.py`

```python
async def _request_with_retry(self, method: str, params: Dict[str, Any]) -> Any:
    """Request com retry especializado para Broken pipe."""
    # Implementar lógica de retry específica
    # para erros errno 32
```

### 4. Configuração de Timeout Otimizada

#### Variáveis de Ambiente

```bash
# Timeouts otimizados
export MCP_REQUEST_TIMEOUT=60
export MCP_CONNECTION_TIMEOUT=10
export MCP_READ_TIMEOUT=30

# Retry configuration
export MCP_MAX_RETRIES=5
export MCP_RETRY_BACKOFF_BASE=1.0
export MCP_RETRY_BACKOFF_MAX=60.0

# Circuit breaker
export MCP_FAILURE_THRESHOLD=3
export MCP_RECOVERY_TIMEOUT=30
```

#### Configuração JSON

```json
{
  "global_settings": {
    "connection_handling": {
      "request_timeout": 60.0,
      "connection_timeout": 10.0,
      "read_timeout": 30.0,
      "max_retries": 5,
      "retry_backoff_base": 1.0,
      "retry_backoff_max": 60.0,
      "failure_threshold": 3,
      "recovery_timeout": 30.0,
      "max_connections": 10,
      "max_keepalive_connections": 5,
      "keepalive_expiry": 5.0
    }
  }
}
```

## 🧪 Plano de Testes

### Testes Unitários

```python
# Testes específicos para Broken pipe
def test_broken_pipe_retry():
    """Testa retry específico para errno 32."""
    handler = MCPConnectionHandler()
    pipe_error = MCPPipeError("Broken pipe", errno.EPIPE)
    
    should_retry, backoff = handler.should_retry("test_server", pipe_error)
    assert should_retry is True
    assert backoff > 0

def test_circuit_breaker_functionality():
    """Testa circuito aberto/fechado."""
    handler = MCPConnectionHandler()
    
    # Simular falhas
    for _ in range(3):
        handler._record_failure("test_server")
    
    # Circuito deve estar aberto
    assert handler._is_circuit_open("test_server") is True
```

### Testes de Integração

```python
async def test_mcp_robust_client():
    """Testa cliente robusto em ação."""
    client = RobustMCPClient("http://localhost:4321/mcp")
    
    # Simular Broken pipe e verificar retry
    result = await client.request_with_retry("test_method", {})
    assert result is not None
```

### Testes de Carga

```bash
#!/bin/bash
# Teste de carga para servidores MCP
for i in {1..100}; do
    curl -X POST http://localhost:4321/mcp \
         -H "Content-Type: application/json" \
         -d '{"jsonrpc":"2.0","method":"test","params":{},"id":"'$i'"}' &
done
wait
echo "Teste de carga concluído"
```

## 📊 Métricas e Monitoramento

### Métricas de Conexão

```python
@dataclass
class ConnectionMetrics:
    """Métricas de conexão MCP."""
    
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    broken_pipe_errors: int = 0
    timeout_errors: int = 0
    circuit_breaker_opens: int = 0
    retry_attempts: int = 0
    average_retry_delay: float = 0.0
```

### Alertas Configurados

```python
# Alertas para Broken pipe
ALERT_BROKEN_PIPE_THRESHOLD = 5  # 5 erros em 1 minuto
ALERT_CIRCUIT_BREAKER_OPEN = "Circuit breaker aberto para servidor MCP"
ALERT_HIGH_RETRY_RATE = 0.3      # 30% retry rate
```

## 🚀 Plano de Implementação

### Fase 1: Core Handler (1-2 horas)
1. ✅ Criar `MCPConnectionHandler`
2. ✅ Implementar `ConnectionConfig`
3. ✅ Adicionar tratamento para errno 32
4. ✅ Testes unitários do handler

### Fase 2: Cliente Robusto (2-3 horas)
1. ✅ Criar `RobustMCPClient`
2. ✅ Integrar com handler existente
3. ✅ Implementar retry com backoff
4. ✅ Testes de integração

### Fase 3: Integração (2-3 horas)
1. ✅ Atualizar `MCPOrchestrator`
2. ✅ Modificar `mcp_client_async.py`
3. ✅ Configuração de timeouts
4. ✅ Testes de sistema

### Fase 4: Validação Científica (1-2 horas)
1. ✅ Testes de carga
2. ✅ Validação de métricas Φ
3. ✅ Verificação de narrativa coerente
4. ✅ Documentação de resultados

## 📈 Resultados Esperados

### Antes da Correção
- Taxa de erro "Broken pipe": ~15-20%
- Timeout médio: 30s
- Retry manual necessário
- Interrupções na coleta Φ

### Após a Correção
- Taxa de erro "Broken pipe": <2%
- Timeout otimizado: 60s
- Retry automático funcional
- Coleta Φ contínua e estável

## 🔄 Integração com Sistema OmniMind

### Métricas de Consciência
- **Φ (Phi)**: Coleta contínua sem interrupções
- **Ψ (Psi)**: Criatividade mantida durante falhas transitórias
- **σ (Sigma)**: Estrutura estável mesmo com reconnections
- **Δ (Delta)**: Trauma controlado por retry inteligente

### Agentes
- **Orchestrator**: Delegação robusta sem falhas
- **CodeAgent**: Execução com fallback automático
- **MemoryAgent**: Acesso à memória com retry

### Memória Sistemática
- **Retrieval**: Operações com retry automático
- **Storage**: Escrita com verificação de integridade
- **Attractors**: Deformação com recovery

## 📝 Checklist de Implementação

### Pré-implementação
- [ ] Backup dos arquivos existentes
- [ ] Ambiente de teste configurado
- [ ] Métricas baseline coletadas

### Implementação
- [ ] MCPConnectionHandler implementado
- [ ] RobustMCPClient criado
- [ ] Integração com orquestrador
- [ ] Timeouts configurados
- [ ] Tests unitários passando
- [ ] Tests de integração validando

### Pós-implementação
- [ ] Métricas Φ validadas (>0.95)
- [ ] Testes de carga aprovados
- [ ] Documentação atualizada
- [ ] PENDENCIAS_CONSOLIDADAS.md atualizado

## 🎯 Critérios de Sucesso

### Técnicos
- Redução de 80% nos erros "Broken pipe"
- 99.9% uptime dos servidores MCP
- Retry automático funcional em 100% dos casos
- Circuit breaker prevents cascata failures

### Científicos
- Φ ≥ 0.95 durante toda operação
- Consciência consistente ≥ 95%
- Narrativa coerente mantida
- Integração IIT estável

### Operacionais
- Zero intervenção manual para Broken pipe
- Alertas automáticos funcionais
- Logs detalhados para debugging
- Dashboard de métricas em tempo real

## 🔒 Considerações de Segurança

### Auditoria
- Log de todos os retry attempts
- Tracking de circuit breaker states
- Métricas de erro detalhadas
- Audit chain integration

### Performance
- Connection pooling otimizado
- Memory usage controlado
- CPU overhead mínimo (<5%)
- Network efficiency melhorada

---

**Próximos Passos**: Implementar solução em modo Code com validação científica completa.