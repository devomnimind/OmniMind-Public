# Imunidade P0 - Firecracker + DLP

## Objetivo
Garantir execução crítica em isolamento absoluto e bloquear qualquer dado sensível, mantendo trilhas de auditoria imutáveis e alertas automáticos.

## Arquitetura
- **FirecrackerSandbox** (`src/security/firecracker_sandbox.py`): encapsula a execução de planos críticos dentro de micro-VMs com kernel/rootfs dedicados. Registra eventos no `immutable_audit` e `AutonomyObservability` para rastreio completo.
- **DLPValidator** (`src/security/dlp.py` + `config/dlp_policies.yaml`): carrega políticas YAML rigorosas e verifica todas as strings antes que ferramentas externas as processem. Violações gravadas no `immutable_audit` e no painel de observabilidade.
- **SecurityAgent** reforçado (`src/security/security_agent.py`): antes mesmo de registrar um evento, valida com o DLP; respostas a incidentes são executadas dentro do sandbox Firecracker com fallback simulado.
- **Observabilidade**: o novo painel `/observability` expõe sanbox events e alertas DLP para o dashboard (backend `web/backend/main.py`, frontend `web/frontend/src/App.tsx`).

## Etapas de implementação
1. Criar o módulo de sandbox e validar a presença do kernel/rootfs; logar em `immutable_audit`.
2. Implementar o validador DLP com políticas configuráveis e mecanismo `enforce` para bloquear payloads perigosos.
3. Atualizar o `SecurityAgent` (e outros agentes críticos) para usar os novos módulos e registrar eventos nos novos buckets de observabilidade.
4. Expandir o dashboard para apresentar eventos Firecracker e alertas DLP, permitindo auditoria imediata.
5. Documentar variáveis de ambiente (`OMNIMIND_FIRECRACKER_KERNEL`, `OMNIMIND_FIRECRACKER_ROOTFS`, `OMNIMIND_DLP_POLICY_FILE`) e scripts de inicialização.

## Testes e validação
- `tests/test_firecracker_sandbox.py`: simula execução sandbox e garante log/audit.
- `tests/test_dlp_validator.py`: cobre cenários de bloqueio e alerta.
- `tests/test_security_agent_integration.py`: garante que o DLP bloqueia o payload antes de registrar eventos e que o sandbox é invocado durante respostas.
- `tests/test_dashboard_e2e.py`: atualiza o painel com as novas seções de segurança.
- `pytest` com `-W default` garante zero warnings.

## Governança e auditoria
- Todo evento de segurança alimenta o `immutable_audit` com hash encadeado e um alert trace no `AutonomyObservability`.
- Logs adicionais são criados em `~/.omnimind/security.log` e `logs/audit_chain.log`.
- Qualquer tentativa de bypass em payloads sensíveis gera alerta imediato por `DLPViolationError` e bloqueio do evento.
- Revisões formais (pull request com `pytest`, `mypy`, `black`) são obrigatórias antes de qualquer commit.

## Monitoramento contínuo
- Firecracker/DLP registram no painel `/observability`, acessível pelo dashboard autenticado.
- Alertas de DLP e falhas de sandbox disparam notificações no `AutonomyObservability.record_alert`.
- Monitoramento segue pipeline: coleta de métricas → auditoria hash → alertas → resposta sandbox.

## Scripts operacionais
- `scripts/setup_firecracker_env.sh [diretório]`: baixa ou valida `vmlinux.bin` e `rootfs.ext4`, escreve em `/opt/firecracker` por padrão e orienta as variáveis `OMNIMIND_FIRECRACKER_KERNEL` / `OMNIMIND_FIRECRACKER_ROOTFS`.
- `scripts/security_validation.sh`: invoca `scripts/validate_security.py` para checar integridade da cadeia, políticas DLP carregadas e existência dos artefatos de sandbox; pode ser agendado via cron (ex.: `*/15 * * * * /home/.../scripts/security_validation.sh`).
- `scripts/validate_security.py`: imprime JSON com resumo das validações (`audit`, `dlp`, `sandbox`) e sai com status 0; falhas em leitura de política ou auditoria serão logadas via `trustedlogger`.

## Preparação para produção
- Configure um job de monitoramento contínuo (`cron`, `systemd timer`) que executa `security_validation.sh`, coleta as saídas e as armazena em `logs/security_validation.jsonl` (com `tee`).
- Documente o comando no runbook: `OMNIMIND_FIRECRACKER_KERNEL=/opt/firecracker/vmlinux.bin OMNIMIND_FIRECRACKER_ROOTFS=/opt/firecracker/rootfs.ext4 /home/.../scripts/setup_firecracker_env.sh`.
- Estabeleça revisão SEMPRE antes de modificar `config/dlp_policies.yaml` ou colocar novos binários de kernel, com auditoria (`immutable_audit.log_action`) e sinalização no dashboard.
