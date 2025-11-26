# Bug Fix Log - Session 2025-11-26

## Bug #1: Backend Startup Loop (CRÍTICO - RESOLVIDO)

### Sintoma
- Backend cluster travava em "Waiting for application startup"
- Consumo alto de CPU (5-6%) sem progresso
- Logs mostravam tentativas de executar comandos `sudo` que requeriam senha interativa

### Causa Raiz
**Violação de Contexto Assíncrono**: O `OrchestratorAgent.__init__()` (contexto síncrono) chamava `_init_security_agent()`, que por sua vez tentava fazer `asyncio.create_task()` sem um event loop ativo.

```python
# ANTES (ERRADO) - src/agents/orchestrator_agent.py:179
def _init_security_agent(self) -> Optional[SecurityAgent]:
    agent = SecurityAgent(config_path=config_path, llm=self.llm)
    if agent.config.get("security_agent", {}).get("enabled", False):
        import asyncio
        asyncio.create_task(agent.start_continuous_monitoring())  # ❌ No event loop!
```

**Resultado**: RuntimeWarning "no running event loop" + bloqueio do `lifespan` do Fast API.

### Solução
Remover a tentativa de iniciar monitoramento contínuo no `__init__`. O SecurityAgent agora é apenas **instanciado** no init, e o monitoramento contínuo deve ser iniciado explicitamente em um contexto assíncrono (se necessário).

```python
# DEPOIS (CORRETO) - src/agents/orchestrator_agent.py:168-179
def _init_security_agent(self) -> Optional[SecurityAgent]:
    """Initializes the security agent (monitoring must be started separately via async context)."""
    try:
        security_config = self.config.get("security", {})
        config_path = security_config.get("config_path", "config/security.yaml")
        agent = SecurityAgent(config_path=config_path, llm=self.llm)
        logger.info("SecurityAgent initialized (monitoring NOT auto-started to avoid event loop issues)")
        return agent
    except Exception as exc:
        logger.error("Failed to initialize SecurityAgent: %s", exc)
        return None
```

### Solução Completa (2-parte)

**Parte 1: Corrigir Event Loop** (orchestrator_agent.py)
- Remover `asyncio.create_task()` do `__init__` (contexto síncrono)
- SecurityAgent é apenas instanciado, não ativado

**Parte 2: Ativar no Contexto Assíncrono** (main.py lifespan)
- Iniciar `security_agent.start_continuous_monitoring()` no `lifespan` do FastAPI
- Agora o event loop está ativo e a task pode ser criada corretamente

**Parte 3: Configurar Privilégios Sudo**
- Criar `/etc/sudoers.d/omnimind` com comandos específicos (NOPASSWD)
- Instalação via `sudo ./scripts/setup_security_privileges.sh`
- Ver `docs/SECURITY_PRIVILEGES.md` para detalhes

### Decisão de Design: SecurityAgent é Essencial

O SecurityAgent **não é opcional**. Ele implementa as **4 Defensive Blindages** do Sinthome Distribuído:

1. **Ressonância Estocástica Panárquica** → Monitoramento de latência (`tc`, `ss`)
2. **Strange Attractor** → Detecção de anomalias (`ps`, `pgrep`)
3. **Real Inaccessível** → Eventos de auditoria (`auditctl`, `ausearch`)
4. **Scar Integration** → Análise de logs históricos (`journalctl`)

**Modelo de Privilégios**:
- **SecurityAgent**: Monitoramento diário (NOPASSWD para comandos read-only)
- **Orchestrator**: Gerenciamento de serviços omnimind-* (NOPASSWD)
- **User**: Comandos críticos de sistema (reboot, shutdown) → popup de senha padrão

### Arquivos Criados/Modificados
- `src/agents/orchestrator_agent.py` (linhas 168-179) - Remover auto-start
- `web/backend/main.py` (linhas 167-192) - Adicionar start no lifespan
- `config/sudoers.d/omnimind` - Configuração sudoers
- `scripts/setup_security_privileges.sh` - Script de instalação
- `docs/SECURITY_PRIVILEGES.md` - Documentação completa

---

## Próximos Passos
1. ✅ Backend cluster funcional
2. ✅ SecurityAgent corrigido e re-habilitado
3. ⏳ **Instalar privilégios**: `sudo ./scripts/setup_security_privileges.sh`
4. ⏳ Testar conexões WebSocket do frontend com cluster
5. ⏳ Analisar logs de benchmarks/testes de longa duração
