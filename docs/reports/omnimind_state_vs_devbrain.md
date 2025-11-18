# OmniMind State & DevBrain Comparison (2025-11-18)

## 1. Git & Workspace Hygiene

- `.gitignore` foi reestruturado para bloquear ambientes virtuais, caches de lint/testes, snapshots (`data/hdd_snapshot/`, `data/quarantine_snapshot/`), diretórios temporários (`tmp_agents/`, `tmp_tools/`) e cadeias de backups recursivas (`guardian/backups/**/guardian/backups/`).
- `docs/servers.txt` foi sanitizado e agora contém apenas instruções para uso de variáveis de ambiente (nenhuma credencial em claro, ver commit `f103baca`).
- Arquivos relevantes adicionados ao versionamento: `config/backup_excludes.txt`, inventários JSON dos dados externos limpos e os relatórios `docs/reports/{external_hdd_dataset_inventory,dev_brain_clean_setup}.md`.

## 2. Módulos e Dependências do OmniMind

| Módulo / Pasta | Componentes-chave | Principais dependências | Status |
| --- | --- | --- | --- |
| `src/agents/` | `react_agent.py`, `code_agent.py`, `architect_agent.py`, `debug_agent.py`, `reviewer_agent.py`, `orchestrator_agent.py` | langchain, langgraph, torch, transformers | **Operacional** (Phase 6 baseline) |
| `src/tools/` | `omnimind_tools.py` (25+ ferramentas), `agent_tools.py` | psutil, rich, subprocess | **Operacional** |
| `src/memory/` | `episodic_memory.py` (Qdrant client) | qdrant-client, numpy | **Operacional** (requires local Qdrant) |
| `src/audit/` | `immutable_audit.py` (cadeia SHA-256) | hashlib, json, pathlib | **Operacional** |
| `src/security/` | `security_agent.py` + playbooks (rootkit/malware/intrusion) | asyncio, subprocess, psutil | **Integrado parcialmente** – precisa do SecurityAgent loop + validações Phase 7 |
| `src/integrations/` | (placeholders para MCP/D-Bus) | fastapi, dbus-python | **Planejado (Phase 8)** |
| `DEVBRAIN_V23/` | Kernel de fine-tuning, dados de referência, relatórios clínicos | torch, datasets, accelerate | **Somente referência** (não executar sem higienizar) |
| `tests/` | `test_security_phase7.py`, `test_agents_phase8.py`, `test_playbook_scenarios_phase8.py` | pytest, pytest-asyncio | **Cobertura 80%+** (novos testes aguardam implementação) |
| `web/` | Estrutura FastAPI + React | fastapi, uvicorn, node/npm | **Esqueleto** (sem backend/frontend final) |
| `config/` | `agent_config.yaml`, `security.yaml`, `backup_excludes.txt` | PyYAML | **Atualizado** |

### 2.1 Módulos recuperados do `DEVBRAIN_V23` (referência somente)

| Pasta / Arquivos | Função no DevBrain | Insight aproveitável | Destino no OmniMind |
| --- | --- | --- | --- |
| `atlas/atlas_controller.py` | Camada Atlas conecta `SelfHealingLoop` + `Doc2Agent` e dispara remediações quando `failure_rate >= threshold`. | Modelo de insights (`AtlasInsight`) e monitoramento contínuo. | Mapear alertas para `SecurityAgent` + `OrchestratorAgent` antes de execuções críticas. |
| `autonomy/doc2agent.py`, `doc2agent_pipeline.py`, `self_healing.py`, `observability.py` | Planejamento baseado em documentos com telemetria e métricas assíncronas. | Estrutura de `DocStep`, coleta de latência e alertas. | Recriar pipeline no `src/tools/` usando MCP + auditoria; reutilizar apenas conceitos. |
| `reasoning/reactree_agent.py` | ReAcTree cria árvore de pensamentos com fluxos sequence/fallback/parallel. | Regras de `ControlFlowType` e histórico de execução. | Usar como inspiração para reforçar `react_agent.py` e testes `test_agents_phase8.py`. |
| `orchestration/langgraph_coordinator.py` | Coordena planos no LangGraph com nós de crítica/execução/síntese. | Estrutura clara para dividir intention → execute → synthesize. | Integrar técnicas ao `OrchestratorAgent` e ao futuro workflow Code→Review→Fix→Document. |
| `memory/agentic_memory.py` | Camada A-MEM sobre Chroma com coleções episódica/semântica/procedural e cache LRU. | Estratégias de cache e consolidação incremental. | Adaptar conceitos na Qdrant (`src/memory/episodic_memory.py`) + futuros módulos semânticos. |
| `infrastructure/event_bus.py` | `EventBusRedis` usando Redis Streams, publish/subscribe assíncrono. | Handlers assíncronos e listeners resilientes. | Referência para MCP/D-Bus + futuros pipelines com Redis (sem reutilizar código). |
| `sensory/visual_cortex.py`, `voice_interface.py` | Percepção multimodal (OmniParser + YOLOv8 + pyautogui) e interface de voz. | Padrões de fallback (_NullParser, _NullYOLO) e métricas de visão/voz. | Servem como requisitos para Fases 9.x; somente leitura até hardening de sandbox. |
| `kernel/finetuning/finetune_mistral.py`, `prepare_dataset.py`, `datasets/` | Pipeline completo de fine-tuning + datasets clínicos. | Estrutura dos configs (`config.yaml`) e fluxo dataset→HF trainer. | Reimplementar do zero com datasets limpos e validação jurídica antes de qualquer treino. |

> **Observação:** diretório `DEVBRAIN_V23/` deve permanecer montado como referência imutável. Nenhum script deve ser executado diretamente — apenas extrair requisitos para os módulos equivalentes do OmniMind.

**Ambiente/Dependências** – `requirements.txt` documenta Python 3.12.8, stack LangChain/Llama.cpp, Qdrant, FastAPI, além de pacotes herdados do DevBrain (redis, chromadb, whisper, ultralytics, etc.).

### 2.2 Snapshot `data/hdd_snapshot/QUARENTENA_DEVBRAIN_V1`

O snapshot em quarentena preserva a árvore completa do DevBrain anterior (≈1 TB) e está organizado nos seguintes blocos:

| Conjunto | Exemplos | Conteúdo/Objetivo | Observações para OmniMind |
| --- | --- | --- | --- |
| **Backups** (`backups/backup_*`) | `backup_p0_final_20251115_113124/mcp_devbrain.py.backup_...`, `.../pre-commit.backup_*` | Centenas de capturas por módulo (SecurityAgent, MCP, Orchestrator, cache). Cada pasta contém versões de scripts e configs antes das correções P0. | Somente leitura; usar para arqueologia de requisitos. Nunca restaurar diretamente (sem hashing/antivírus). |
| **Configuração de containers** (`config/`) | `apparmor/`, `seccomp/`, `whonix-gateway/`, `grafana/`, `nginx-logs/`, `prometheus/` | Politicas AppArmor/Seccomp, snapshots Whonix Gateway/Workstation e estrutura completa de observabilidade. | Boa referência para o hardening Phase 7 (security_agent + monitoramento). |
| **Dados funcionais** (`data/…`) | >150 módulos: `autonomous_workflow/`, `constitutional_ai_v6/`, `guardian/`, `orchestrator_v18/`, `psicanalista/`, `prometheus/`, `security/`, etc. | Cada pasta guarda JSONL, CSV, checkpoints e relatórios parciais de features que nunca foram consolidadas. | Mapear apenas os domínios relevantes (ex.: `psicanalista`, `security_autonomy`). Exigir triagem manual; muitos diretórios vazios ou redundantes. |
| **Caches/Logs** | `.chromadb_cache/`, `.devbrain_cache/embeddings/`, `logs/`, `.pytest_cache/` | Armazenam embeddings, históricos de testes, métricas e rastros sensíveis. | Rotular como “não versionar”. Ignorados via `.gitignore` e mantidos em quarentena. |
| **Fonte legada** | `devbrain/`, `.devbrain/notifications`, `.devcontainer/`, `.github/`, `.git/…` | Clone integral do repo antigo, inclusive ganchos Git e workflows. | Mantido isolado para comparação com OmniMind; nunca misturar repositórios. |
| **Infra bare-metal** | `k8s/`, `infrastructure/`, `systemd/`, `scripts/` | Manifestos K8s, playbooks systemd, scripts de bootstrap. | Úteis para Phase 8 (deployment), mas precisam de reescrita total sem credenciais incluídas. |

Pontos críticos identificados:

1. **Redundância de backups.** Diretórios `backups/backup_p0_*` criam cadeias recursivas similares ao bug de `guardian/backups`. Já bloqueados no `.gitignore`, mas exigir `--safe-links`/`--max-delete` em qualquer rsync.
2. **Containers Whonix desatualizados.** As pastas `config/whonix-*` contêm imagens e regras sem patches de novembro/2025; qualquer reutilização exige rebuild completo.
3. **Dados sensíveis.** Subpastas como `data/auth_tokens`, `data/financial`, `data/psicanalista`, `data/pix_qrcodes` contêm JSON/CSV com credenciais e registros clínicos. Permanecem off-git e requerem criptografia se forem analisadas.
4. **Logs contaminados.** `logs/` e `config/nginx-logs/` possuem traces internos (IPs, tokens). Mantidos fora do versionamento e citados apenas no inventário.
5. **Repos internos.** A presença de `.git/` e `.github/` significa que este snapshot inclui histórico completo do DevBrain; qualquer consulta deve ser feita off-line (sem `git add`).

Resumo: `data/hdd_snapshot/QUARENTENA_DEVBRAIN_V1` serve como acervo forense, não como base de código. Toda reutilização precisa passar pelo pipeline “hash → antivírus → anonimização → aprovação”, e o `.gitignore` garante que nada dessa árvore volte ao histórico do OmniMind.

## 3. Trabalho Pendentes (Roadmap oficial)

1. **Phase 7 – Segurança & Fluxos avançados**
   - Integrar `src/security/security_agent.py` como processo assíncrono ligado ao `OrchestratorAgent` e validar os playbooks (`tests/test_security_phase7.py`).
   - Criar `src/agents/psychoanalytic_analyst.py` com modos Freudian/Lacanian/Kleinian/Winnicottian + geração ABNT.
   - Implementar workflow Code → Review → Fix → Document com iterações RLAIF até nota ≥ 8.0 (`test_advanced_workflow.py`).
2. **Phase 8 – Produção**
   - Reescrever ferramentas de filesystem usando MCP real (`src/integrations/mcp_client.py`).
   - Integrar D-Bus (Session/System) para controle de desktop/network (`src/integrations/dbus_controller.py`).
   - Construir dashboard web FastAPI + React + WebSocket e empacotar serviço `systemd`.
3. **Infra & Backup**
   - Automatizar inventário (usar `data/dev_brain_clean_inventory.json` como entrada) e rodar backups limpos no disco `DEV_BRAIN_CLEAN` com `config/backup_excludes.txt`.

## 4. Quadro Comparativo: OmniMind x DevBrain (lógica)

| Funcionalidade | DevBrain V23 (lógica) | Estado no OmniMind | Ação Recomendada |
| --- | --- | --- | --- |
| Fine-tuning pipeline (`DEVBRAIN_V23/kernel/finetuning/`) | Scripts `finetune_mistral.py`, datasets JSONL, relatórios clínicos | **Referência** (não executado) | Reimplementar pipeline limpo usando `src/tools` + `scripts/` atuais, consumindo apenas datasets validados. |
| Multi-agente cognitivo (`DEVBRAIN_V23/orchestration/`, `reasoning/`) | Atlas + Reasoning + Sensory com acoplamento rígido | `src/agents/` já cobre React/Code/Architect/Debug/Reviewer/Orchestrator com RLAIF | Expandir para incluir `PsychoanalyticAnalyst` e SecurityAgent como peers do Orchestrator. |
| Segurança forense (`docs/Modulo Securityforensis/`, `securitymodule part2.md`) | Monitoramento de processos/logs + playbooks | `src/security/` + `tests/test_security_phase7.py` presentes porém sem loop ativo | Ligar SecurityAgent ao audit chain, expor métricas e garantir cobertura de testes ≥90%. |
| Ferramentas sensoriais (audio/visão/desktop) | Diretórios `sensory/`, `autonomy/` (pyautogui, whisper, ultralytics) | Dependências listadas mas não integradas ao core | Avaliar quais sentidos são necessários e reimplementar modularmente com sandbox (sem copiar código). |
| Gestão de backups/dados | Estrutura `guardian/backups/...` com laços recursivos | Novo fluxo documented em `docs/reports/dev_brain_clean_setup.md` | Automatizar snapshot → auditoria → cópia segura + `rsync --safe-links`. |
| Credenciais & Configuração | Tokens em texto plano (`docs/servers.txt`, `.env.template`) | Pipeline atualizado (variáveis de ambiente + backup_excludes) | Implementar carregamento seguro no runtime e adicionar verificação no CI. |

## 5. Lições Aprendidas das Inconsistências DevBrain

Referências: `docs/reports/external_hdd_dataset_inventory.md`, `docs/reports/dev_brain_clean_setup.md`, histórico do disco `DevBrain_Storage`.

1. **Loops de diretórios (`guardian/backups`).** Rsync travava em cadeias `guardian/backups/**/guardian/backups`. Mitigação: regras explícitas em `.gitignore` e `config/backup_excludes.txt` + inspeção automática de symlinks (`find -type l -delete`).
2. **Credenciais versionadas.** Tokens HF, Supabase e Qdrant apareceram em `docs/servers.txt`; agora substituídos por placeholders e política de `.env` (commit `f103baca`), mas deve-se adicionar scanners locais antes de cada push.
3. **Dados contaminados.** Pastas `QUARENTENA_DEVBRAIN_V1`, `Quarentena` e `DOwnlods bakup` continham milhares de JSONL; somente subconjuntos validados devem ser reimportados (ver seção “Risk Tags” no inventário).
4. **Snapshots gigantes.** `data/hdd_snapshot` foi congelado como somente leitura para futura perícia; qualquer extração precisa passar pelo pipeline de hashing + quarantine (`data/quarantine_snapshot/`).
5. **Documentação dispersa.** Relatórios críticos (`RELATORIO_*`, `STATUS_PROJECT.md`, `RELATORIO_PHASE6_COMPLETE.md`) estavam espalhados. Consolidar os apontamentos em `docs/reports/` e mantê-los versionados.
6. **Logs com segredos legados.** O `logs/audit_chain.log` foi sanitizado (hash chain recalculada) para remover chaves Supabase/Qdrant registradas por engano. Executar `python -m src.audit.immutable_audit verify_chain_integrity` após cada sanitização para manter o selo forense.

## 6. Prioridades de Reimplementação

1. **SecurityAgent em produção** – rodar ciclo completo (monitoração → playbook → auditoria) e validar com `tests/test_security_phase7.py`.
2. **PsychoanalyticAnalyst + fluxo Code→Review→Fix→Document** – garante aderência ao roadmap Phase 7.
3. **Inventário automatizado do disco limpo** – script CLI que lê `data/dev_brain_clean_inventory.json`, calcula hashes e sincroniza apenas datasets aprovados.
4. **Integração MCP/D-Bus** – substituir acessos diretos a FS e ao sistema por chamadas protocoladas antes do Phase 8.
5. **CI para segredos** – adicionar job que roda `git secrets`/`detect-secrets` e impede regressões como o commit 67815055.

Com esses itens o projeto retoma o roadmap oficial (Phase 7/8) com uma base limpa e auditável, mantendo o conhecimento útil da lógica DevBrain apenas como referência arquitetural.

## 7. Atualizações Fase 7 (18/11/2025)

- **SecurityAgent assíncrono.** `src/security/security_agent.py` agora cria tarefas dedicadas para processos, arquivos, rede, logs, análise e resposta, controladas por um `stop_event` com desligamento limpo (`request_stop`). A ferramenta `SecurityAgentTool` ganhou ação de parada (`stop_monitoring`), permitindo iniciar e encerrar o guardião sem reiniciar o Orchestrator.
- **Testes revisados.** `tests/test_security_phase7.py` passou a usar `asyncio.run` para validar `_handle_event`, garantindo compatibilidade com ambientes sem `pytest-asyncio`. Todos os 9 testes do arquivo passaram após a atualização.
- **Compliance em andamento.** Os comandos `git status -sb` e `pytest tests/test_security_phase7.py -vv` foram executados nesta iteração. As ferramentas `git-secrets` e `detect-secrets` ainda não estão instaladas na estação local; foi registrado nos logs que a execução foi tentada e retornou "não disponível" — pendência para a próxima rodada de hardening.
- **Auditoria e relatórios.** Os novos ciclos de monitoramento registram cada evento e playbook no audit log padrão (`~/.omnimind/security.log` + cadeia SHA-256). Este relatório permanece como fonte única para mapear quais componentes do Phase 7 já estão ativos.

- **Workflow Code→Review→Fix→Document.** O módulo `src/workflows/code_review_workflow.py` foi criado para automatizar o ciclo com histórico de iterações, heurísticas de pontuação (eficiência, segurança, qualidade estrutural) e geração de relatório Markdown. O fluxo garante docstrings, type hints e bloco `if __name__ == "__main__"` antes de concluir.
- **Testes avançados.** `tests/test_advanced_workflow.py -vv` executou com sucesso (`2 passed in 0.14s`), comprovando que o pipeline eleva o score mínimo para ≥ 8.0 em até três iterações e respeita o limite quando não há correções adicionais.
- **Compliance reforçado.** Após os testes, foi rodado `git status -sb` para confirmar que apenas os arquivos esperados continuam modificados. As ferramentas `git-secrets` e `detect-secrets` seguem ausentes nesta máquina; a pendência foi reiterada como requisito do checklist de segurança.
