# Correção de Portas MCP - Resumo
**Data:** 2025-11-25
**Status:** ✅ CORRIGIDO

## 🔍 Problema Identificado

Todos os servidores MCP estavam tentando usar a mesma porta 4321 (padrão do `mcp.json`), causando:
- Conflitos de porta (Address already in use)
- Servidores caindo e reiniciando constantemente
- Processos zombie (defunct)
- Instabilidade geral do sistema MCP

## ✅ Correções Implementadas

### 1. Configuração de Portas Individuais
Adicionadas portas únicas para cada servidor MCP em `config/mcp_servers.json`:

| Servidor | Porta | Prioridade | Tier |
|----------|-------|------------|------|
| memory | 4321 | critical | 1 |
| sequential_thinking | 4322 | critical | 1 |
| context | 4323 | high | 2 |
| python | 4324 | high | 2 |
| system_info | 4325 | medium | 3 |
| logging | 4326 | medium | 3 |
| filesystem | 4327 | critical | 1 |
| git | 4328 | high | 2 |
| sqlite | 4329 | medium | 3 |

### 2. Modificações no Código

#### `src/integrations/mcp_orchestrator.py`
- ✅ Adicionado campo `port: Optional[int]` em `MCPServerConfig`
- ✅ Carregamento de porta do JSON de configuração
- ✅ Passagem de porta via variável de ambiente `MCP_PORT` ao iniciar servidores
- ✅ Forçamento de `MCP_HOST=127.0.0.1` para segurança (localhost apenas)
- ✅ Adicionado `import os` para manipulação de variáveis de ambiente

#### `src/integrations/mcp_server.py`
- ✅ Modificado `MCPConfig.load()` para ler porta de variável de ambiente `MCP_PORT`
- ✅ Prioridade: variável de ambiente > arquivo de configuração
- ✅ Validação de segurança: host sempre `127.0.0.1` (nunca `0.0.0.0`)
- ✅ Adicionado `import os`

### 3. Segurança das Portas

**Garantias implementadas:**
- ✅ Todas as portas escutam apenas em `127.0.0.1` (localhost)
- ✅ Nunca expostas em `0.0.0.0` (não acessíveis externamente)
- ✅ Portas em range seguro (4321-4329)
- ✅ Validação automática no código

## 📋 Arquivos Modificados

1. `config/mcp_servers.json` - Adicionadas portas individuais
2. `src/integrations/mcp_orchestrator.py` - Suporte a portas individuais
3. `src/integrations/mcp_server.py` - Leitura de porta via env

## 🔄 Como Funciona Agora

1. **Orquestrador lê configuração:**
   - Carrega `mcp_servers.json`
   - Extrai porta de cada servidor (ou usa 4321 como padrão)

2. **Ao iniciar servidor:**
   - Define `MCP_PORT=<porta_individual>` no ambiente
   - Define `MCP_HOST=127.0.0.1` (forçado para segurança)
   - Inicia processo com variáveis de ambiente

3. **Servidor MCP lê configuração:**
   - `MCPConfig.load()` verifica `MCP_PORT` primeiro
   - Se não encontrado, usa porta do arquivo `mcp.json`
   - Sempre força host para `127.0.0.1`

## ✅ Validação

```bash
# Verificar portas configuradas
python -c "import json; config = json.load(open('config/mcp_servers.json')); ..."

# Verificar orquestrador
python -c "from src.integrations.mcp_orchestrator import MCPOrchestrator; ..."
```

**Resultado:** Todas as 9 portas configuradas corretamente ✅

## 🎯 Próximos Passos

1. **Reiniciar serviço MCP** para aplicar correções:
   ```bash
   sudo systemctl restart omnimind-mcp.service
   ```

2. **Monitorar logs** para verificar se servidores param de reiniciar:
   ```bash
   journalctl -u omnimind-mcp.service -f
   ```

3. **Verificar status** dos servidores:
   ```bash
   python -c "from src.integrations.mcp_orchestrator import MCPOrchestrator; ..."
   ```

## 🔒 Conformidade com Padrões do Projeto

- ✅ Segurança: Portas apenas em localhost (127.0.0.1)
- ✅ Configuração centralizada: `mcp_servers.json`
- ✅ Variáveis de ambiente: Padrão do projeto
- ✅ Type hints: Mantidos em todas modificações
- ✅ Documentação: Este resumo

## 📝 Notas Técnicas

- Portas 4321-4329 são seguras para uso local
- Range evita conflitos com portas comuns (8000, 3000, etc.)
- Sistema suporta até 9 servidores MCP simultâneos
- Expansível: fácil adicionar mais servidores com novas portas

