# Warnings ativos (Pytest & mypy)

- **ResourceWarning (asyncio.event_loop)** – Ao rodar `pytest -vv -W default` ainda aparece `ResourceWarning: unclosed event loop <_UnixSelectorEventLoop ...>` de fixtures `pytest-asyncio`. O warning permanece documentado e será resolvido com revisão do fluxo async mais adiante.
- **Mypy backlog (100+ erros)** – Após os ciclos de DBus/GraphQL/Supabase/memória, `mypy src tests` ainda reporta erros críticos nos módulos de auditoria (`tests/test_audit.py`), integrações (DBus, MCP, GraphQL), agentes React/Code e testes de dashboard/agents. Esses erros bloqueiam o ambiente e precisam ser atacados módulo a módulo conforme prioridade de estabilidade.
- **ReactAgent/CodeAgent/backend typing** – O ciclo atual levantou erros adicionais em `src/agents/react_agent.py` (tipagem de grafos e chamadas `invoke`), `src/agents/code_agent.py` (categorias de ferramentas) e `web/backend/main.py` (vários `type: ignore` obsoletos). Esses blocos são a causa imediata da falha no `mypy tests/test_dashboard_e2e.py` e devem ser o foco do próximo ciclo de correção.

> Atualize esse arquivo assim que qualquer warning for adicionado ou eliminado. Mantenha o histórico para onboarding futuros e referencie-o nos commits que lidam com os bloqueios listados.

