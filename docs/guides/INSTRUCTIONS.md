# OmniMind - Instruções de Correção e Otimização

## 1. Correção de Privilégios de Segurança (CONCLUÍDO)

As regras de privilégios foram instaladas com sucesso em `/etc/sudoers.d/omnimind`.
O sistema agora tem autonomia para executar monitoramento e resposta a incidentes sem solicitar senha.

Além disso, as prioridades dos processos (Backend e Frontend) foram ajustadas para **Alta Prioridade (Nice -5)** para mitigar a lentidão e disputa de recursos.

### Fallback Interativo (Novo)

Se uma operação crítica não estiver autorizada no `sudoers`, o sistema agora tentará usar `pkexec` para abrir uma janela gráfica solicitando sua senha, garantindo que você possa autorizar exceções manualmente ("Senha Sudo-Além"). Isso está habilitado via `OMNIMIND_INTERACTIVE=true` no `.env`.

## 2. Verificação de Operacionalidade

O sistema foi reiniciado e configurado para inicialização robusta via **Systemd**.

- **Backend**: `sudo systemctl status omnimind-backend`
- **Frontend**: `sudo systemctl status omnimind-frontend`
- **Logs**: `journalctl -u omnimind-backend -f`

Os serviços iniciam automaticamente no boot e reiniciam em caso de falha.

## 3. Escalabilidade e Assincronismo (100 Agentes)

## 3. Escalabilidade e Assincronismo (100 Agentes)

Para suportar a escala de 100 agentes e evitar lentidão:

1.  **Inicialização Assíncrona**: O `OrchestratorAgent` agora carrega em segundo plano, liberando o servidor HTTP imediatamente.
2.  **Async MCP**: Foi criado `src/integrations/async_mcp_client.py` para permitir comunicação não-bloqueante com o MCP Server.
3.  **Próximos Passos**: Refatorar o `OrchestratorAgent` para usar `AsyncMCPClient` e `asyncio.gather` para execução paralela de tarefas.

## 4. Análise de Lentidão (Antigravity)

A lentidão observada pode ser devido a:

- **Disputa de Recursos**: O OmniMind é intensivo em CPU/Memória. Em ambiente compartilhado/experimental, isso causa contenção.
- **Bloqueio de I/O**: Corrigimos vários comandos `sudo` que poderiam estar esperando senha silenciosamente.
- **Recomendação**: Mantenha apenas os serviços essenciais rodando. O script `scripts/start_omnimind_system.sh` ajuda a limpar processos antigos.

## 5. Auditoria

O relatório de auditoria de privilégios e métricas pode ser encontrado em:
- `docs/SECURITY_PRIVILEGES.md`
- `docs/METRICS_AUDIT.md`
