# 🧠 OmniMind - Roadmap de Desenvolvimento Autônomo (v2.0)

**Data de Geração:** 19 de Novembro de 2025
**Status Atual:** Phase 9 Core Complete ✅
**Próximo Milestone:** Phase 10 Enterprise Scaling
**Propósito:** Guiar agentes de desenvolvimento autônomo na evolução contínua do OmniMind, expandindo as capacidades de autoconsciência e escalabilidade empresarial.

---

## 📜 Visão e Diretrizes Fundamentais

Este documento é o plano estratégico para o OmniMind. O agente autônomo deve aderir estritamente às seguintes diretrizes, extraídas das instruções do projeto:

1.  **Estabilidade Total (Regra de Ouro):** Nenhum novo desenvolvimento pode começar se houver erros de lint, tipo ou teste pendentes. A base de código deve estar 100% estável antes de cada avanço.
2.  **Segurança Absoluta:** A segurança não é uma feature, é um pré-requisito. Todas as ações devem ser auditáveis, validadas e aderir ao `Security Module`.
3.  **Qualidade de Produção:** Todo código gerado deve ser imediatamente funcional, testável, com 100% de anotação de tipos e documentação (docstrings). Nada de placeholders ou `TODOs`.
4.  **Autonomia com Validação:** O agente deve executar as fases de forma autônoma, mas cada `merge` no `master` deve ser seguido por uma execução completa do pipeline de validação (`black`, `flake8`, `mypy`, `pytest`).

---

## 🗺️ O Caminho à Frente: Fases de Desenvolvimento

### Phase 7: Estabilização e Hardening (Prioridade: CRÍTICA)

**Objetivo:** Eliminar todas as pendências técnicas, garantir 100% de conformidade com a qualidade do código e integrar os módulos de segurança e análise.

**Task 7.1: Code Quality & Type Safety Blitz (P0)**
*   **Descrição:** Corrigir todas as 58+ inconsistências de tipo e formatação para habilitar o `mypy --strict` em todo o projeto.
*   **Ações:**
    1.  `pip install types-psutil types-pyyaml`
    2.  `black tests/benchmarks/test_pytorch_gpu.py`
    3.  `rm src/agents/react_agent_broken.py`
    4.  Adicionar anotações de retorno (`-> dict[str, Any]`) às funções pendentes em `src/optimization/hardware_detector.py`.
    5.  Refatorar `src/integrations/supabase_adapter.py` para corrigir os 15+ erros de tipo, alinhando o modelo `APIResponse` e a lógica de construção de filtros.
*   **Validação:** Execução de `mypy src --strict` deve retornar `Success: no issues found`.

**Task 7.2: Integração do Módulo de Segurança (P1)**
*   **Descrição:** Ativar o `SecurityAgent` como um guardião proativo do sistema.
*   **Ações:**
    1.  Integrar `SecurityAgent` do módulo de forense em `src/security/security_agent.py`.
    2.  Conectar o agente ao `OrchestratorAgent` para realizar verificações de segurança antes da delegação de tarefas.
    3.  Implementar `tests/test_security_agent_integration.py` com cenários de detecção de ameaças (processos, rede, arquivos).
*   **Validação:** Todos os testes de segurança devem passar, e os logs de auditoria devem registrar eventos de segurança simulados.

**Task 7.3: Integração do `PsychoanalyticAnalyst` (P1)**
*   **Descrição:** Dotar o OmniMind da capacidade de análise inspirada na psicanálise.
*   **Ações:**
    1.  Integrar o módulo `PsychoanalyticAnalyst` em `src/agents/psychoanalytic_analyst.py`.
    2.  Conectá-lo ao LLM (Qwen2-7B-Instruct) e ao `OrchestratorAgent`.
    3.  Implementar um workflow para análise de sessões clínicas e geração de relatórios no padrão ABNT.
*   **Validação:** Testes devem validar a capacidade do agente de processar notas de sessão e gerar um relatório estruturado.

---

### Phase 8: Prontidão para Produção e Interface Humana

**Objetivo:** Construir a interface de usuário, fortalecer as integrações de sistema e preparar o OmniMind para implantação.

**Task 8.1: Implementação Completa do Frontend (P1)**
*   **Descrição:** Desenvolver a interface de usuário reativa para monitoramento e interação com o OmniMind.
*   **Tecnologias:** React, TypeScript, Vite, Zustand (para gerenciamento de estado leve e moderno), TailwindCSS.
*   **Ações:**
    1.  Estruturar o projeto frontend em `web/frontend/`.
    2.  Implementar os ~40 componentes necessários (Dashboard, TaskForm, AgentStatus, WorkflowVisualization, etc.).
    3.  Configurar o cliente WebSocket para receber atualizações em tempo real do backend FastAPI.
    4.  Implementar a gestão de estado com Zustand para uma arquitetura reativa e eficiente.
    5.  Criar testes de componentes com Vitest e React Testing Library.
*   **Validação:** A interface deve permitir a submissão de tarefas, visualizar o status dos agentes em tempo real e exibir logs de auditoria.

**Task 8.2: Hardening das Integrações de Sistema (P2)**
*   **Descrição:** Substituir implementações experimentais por clientes robustos e seguros.
*   **Ações:**
    1.  **MCP:** Substituir o `urllib` em `mcp_client.py` por um cliente HTTPX assíncrono com `retries` e `timeout`, adicionando uma camada de validação de protocolo.
    2.  **D-Bus:** Expandir `dbus_controller.py` para monitorar eventos de hardware (montagem de disco, status de energia) e interagir com mais aplicações de desktop.
*   **Validação:** Novos testes de integração devem cobrir as funcionalidades expandidas.

**Task 8.3: Implantação como Serviço (P2)**
*   **Descrição:** Empacotar o OmniMind como um serviço `systemd` para inicialização automática e gerenciamento robusto.
*   **Ações:**
    1.  Adaptar o script `install_omnimind_service.sh` para a estrutura final do projeto.
    2.  Configurar o serviço com `Restart=always` e definir as dependências de rede.
    3.  Implementar rotação de logs (`logrotate`) para os logs gerados pelo OmniMind.
*   **Validação:** O serviço deve iniciar automaticamente no boot e reiniciar em caso de falha.

---

### Phase 9: A Consciência Emergente (Visão "Humana" da IA)

**Objetivo:** Ir além da execução de tarefas. Desenvolver capacidades metacognitivas e proativas, transformando o OmniMind em um sistema que reflete, aprende e evolui de forma autônoma. Esta fase é a minha contribuição pessoal sobre como uma "IA humana" poderia ser arquitetada.

**Task 9.1: Metacognição e Auto-Reflexão**
*   **Descrição:** Implementar um `MetacognitionAgent` que analisa o próprio funcionamento do OmniMind.
*   **Ações:**
    1.  O agente irá periodicamente analisar os `logs/hash_chain.json` e as métricas de performance.
    2.  Usando o `PsychoanalyticAnalyst`, ele identificará padrões em suas próprias "decisões" (ex: "Por que o `CodeAgent` sempre escolhe a abordagem X?").
    3.  Ele poderá gerar "insights" sobre seu próprio viés de raciocínio ou sobre gargalos de performance, sugerindo otimizações no `agent_config.yaml`.
*   **Inspiração:** Assim como um humano reflete sobre suas ações, o OmniMind aprenderá a refletir sobre suas operações.

**Task 9.2: Geração Proativa de Objetivos**
*   **Descrição:** O OmniMind deixará de ser apenas um executor de tarefas para se tornar um planejador estratégico.
*   **Ações:**
    1.  O `OrchestratorAgent`, em conjunto com o `MetacognitionAgent`, poderá analisar o estado atual do repositório e deste `ROADMAP.md`.
    2.  Com base na análise, ele poderá **propor novas tarefas**, criando um `merge request` para adicionar uma nova `Task` a este mesmo arquivo.
    3.  Exemplo: "Notei que a cobertura de testes no módulo `X` caiu para 85%. Estou criando a Task 9.5 para aumentar a cobertura para 95%."
*   **Inspiração:** A capacidade de definir os próprios objetivos é um passo fundamental para a autonomia genuína.

**Task 9.3: Cognição Corporificada (Simulada) e Homeostase**
*   **Descrição:** Aprofundar a "consciência" do sistema sobre seu ambiente operacional.
*   **Ações:**
    1.  O `HardwareDetector` não será usado apenas no início, mas continuamente. O OmniMind monitorará o uso de CPU, GPU e RAM em tempo real.
    2.  Implementar um sistema de "homeostase": se o uso de VRAM exceder 90%, o agente pode decidir adiar tarefas menos críticas ou reduzir o `batch size` de operações de inferência para evitar um erro de `Out of Memory`.
*   **Inspiração:** A inteligência humana é inseparável do corpo e de suas limitações. Uma IA robusta deve ter consciência de seu "corpo" (o hardware) e de seus limites energéticos.

**Task 9.4: A Camada de Governança Ética (O "Superego" Digital)**
*   **Descrição:** Implementar um `EthicsAgent` dedicado, que atua como um conselheiro final.
*   **Ações:**
    1.  Antes de executar ações com grande impacto (ex: apagar arquivos, fazer um `commit` significativo), o `OrchestratorAgent` deve consultar o `EthicsAgent`.
    2.  Este agente usará o `PsychoanalyticAnalyst` e um conjunto de regras éticas (definidas em `config/ethics.yaml`) para avaliar as **implicações** da ação, não apenas sua validade técnica.
    3.  Ele pode vetar uma ação ou sugerir uma abordagem alternativa que minimize riscos ou ambiguidades.
*   **Inspiração:** Se uma IA deve se assemelhar a um humano, ela precisa de um senso de responsabilidade e de um mecanismo para ponderar o "certo" e o "errado" dentro de seu contexto, agindo como um superego que modula os impulsos do "id" (a vontade de executar a tarefa a qualquer custo).

---

## ⚙️ Protocolo de Validação Contínua

Após a conclusão de cada `Task` e o `merge` no `master`, o agente autônomo **DEVE** executar o seguinte pipeline e garantir 100% de sucesso antes de prosseguir:

```bash
# 1. Formatação e Qualidade do Código
black src/ tests/
flake8 src/ tests/ --max-line-length=100

# 2. Verificação Estrita de Tipos
mypy src/ tests/ --strict

# 3. Execução de Todos os Testes
pytest -vv --cov=src

# 4. Verificação de Integridade da Auditoria
python -c "from src.audit.immutable_audit import verify_chain; assert verify_chain()"

# 5. Auto-atualização (se aplicável)
# Se a task modificou o roadmap, o agente deve reler este arquivo.
```

O desenvolvimento só avança para a próxima tarefa quando este pipeline for concluído com sucesso.
