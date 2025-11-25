# Análise dos Servidores MCP Reiniciando
**Data:** 2025-11-25 03:46
**Status:** 🔴 PROBLEMA CRÍTICO IDENTIFICADO

## 🔍 Problema Identificado

Os servidores MCP estão entrando em um ciclo de restart constante. Análise dos logs mostra:

### Sintomas
1. **Servidores iniciam com sucesso** (logs mostram "iniciado com sucesso (PID=XXXXX)")
2. **Após ~60 segundos**, o health check detecta que não estão mais rodando
3. **Processos se tornam "zombie" (defunct)** - visível em `ps aux`
4. **Ciclo se repete indefinidamente**

### Servidores Afetados
- ❌ sequential_thinking - Reiniciando a cada ~60s
- ❌ context - Reiniciando a cada ~60s  
- ❌ python - Reiniciando a cada ~60s
- ❌ system_info - Reiniciando a cada ~60s
- ❌ logging - Reiniciando a cada ~60s
- ✅ memory - **ÚNICO ESTÁVEL** (rodando desde 02:01)

### Processos Zombie Detectados
```
root     3329711  1.5  0.0      0     0 ?        Z    03:45   0:00 [python] <defunct>
root     3329844  1.4  0.0      0     0 ?        Z    03:45   0:00 [python] <defunct>
root     3329928  1.4  0.0      0     0 ?        Z    03:45   0:00 [python] <defunct>
root     3330036  1.7  0.0      0     0 ?        Z    03:45   0:01 [python] <defunct>
root     3330087  1.5  0.0      0     0 ?        Z    03:45   0:00 [python] <defunct>
```

## 🔬 Causa Raiz

### Análise do Código

Os servidores MCP stub têm o seguinte padrão em `__main__`:

```python
if __name__ == "__main__":
    server = ThinkingMCPServer()
    try:
        server.start()
        logger.info("Thinking MCPServer running...")
        if server._thread:
            server._thread.join()
    except KeyboardInterrupt:
        server.stop()
```

### Problema Identificado

1. **Thread daemon**: O `MCPServer.start()` cria uma thread com `daemon=True` por padrão
2. **Thread.join() bloqueante**: O código chama `server._thread.join()` que deveria manter o processo vivo
3. **Processo termina**: Mas o processo Python está terminando mesmo assim, criando processos zombie

### Possíveis Causas

1. **Erro silencioso**: Os servidores podem estar crashando silenciosamente
2. **Porta em uso**: Tentativa de bind em porta já ocupada (erro visto: "Address already in use")
3. **Falta de tratamento de exceções**: Erros não capturados podem estar matando o processo
4. **Configuração incorreta**: Os servidores podem estar tentando usar a mesma porta

## 📊 Evidências dos Logs

### Padrão de Restart Observado
```
03:45:30 - WARNING: Servidor sequential_thinking não está mais rodando
03:45:30 - INFO: Reiniciando servidor MCP sequential_thinking
03:45:31 - INFO: Servidor MCP sequential_thinking iniciado com sucesso (PID=3329711)
... (60 segundos depois) ...
03:46:30 - WARNING: Servidor sequential_thinking não está mais rodando
```

### Erro de Porta
Ao testar manualmente:
```
OSError: [Errno 98] Address already in use
```

## ✅ Soluções Propostas

### 1. Imediato: Verificar Portas
- Verificar se múltiplos servidores estão tentando usar a mesma porta
- Cada servidor MCP precisa de uma porta única

### 2. Curto Prazo: Melhorar Tratamento de Erros
- Adicionar try/except mais robusto nos servidores
- Capturar e logar stderr dos processos
- Adicionar timeout no health check

### 3. Médio Prazo: Corrigir Implementação
- Verificar se os servidores stub precisam de loop de espera adicional
- Implementar signal handlers para graceful shutdown
- Adicionar validação de porta antes de iniciar

### 4. Longo Prazo: Monitoramento
- Adicionar métricas de uptime
- Alertas quando servidores caem repetidamente
- Dashboard de status dos servidores MCP

## 🎯 Próximos Passos

1. **Verificar configuração de portas** em `config/mcp_servers.json`
2. **Capturar stderr dos processos** para ver erros reais
3. **Adicionar logging mais detalhado** nos servidores stub
4. **Testar servidores individualmente** para isolar o problema

## 📝 Notas Técnicas

- O servidor `memory` está estável, sugerindo que a implementação base funciona
- O problema parece específico dos servidores que estão reiniciando
- Processos zombie indicam que o processo pai não está fazendo wait() corretamente
- O orquestrador pode precisar melhorar o gerenciamento de processos filhos

