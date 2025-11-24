# OmniMind - Relatório de Pendências e Plano de Ataque

## Executive Summary
- **Total de pendências:** 5
- **Críticas:** 0 | **Altas:** 1 | **Médias:** 3 | **Baixas:** 1
- **Tempo estimado total:** 1 Sprint (2 semanas)

## Pendências por Categoria

### 🏗️ Arquitetura
#### [ARCH-001] Duplicação de Módulos de Swarm Intelligence
- **Prioridade:** 🟡 Alta
- **Contexto:** Existem dois diretórios para inteligência coletiva: `src/collective_intelligence` e `src/swarm` (Phase 19).
- **Impacto:** Confusão sobre qual é a implementação canônica e potencial código morto.
- **Estimativa:** M (2-3 dias)
- **Dependências:** Nenhuma

### 📝 Documentação
#### [DOC-001] Relatórios de Status Faltantes
- **Prioridade:** 🟢 Média
- **Contexto:** Faltam os relatórios formais `docs/reports/PHASE19_STATUS.md`, `docs/reports/PHASE20_STATUS.md` e `docs/reports/PHASE21_STATUS.md`.
- **Impacto:** Falta de registro histórico consolidado das fases recentes.
- **Estimativa:** S (1 dia)
- **Dependências:** Nenhuma

#### [DOC-002] Regras de Projeto e Copilot Instructions
- **Prioridade:** 🟢 Média
- **Contexto:** Arquivos explícitos de regras (`.cursorrules` ou similar) e instruções para Copilot precisam ser formalizados/atualizados na raiz ou `.github`.
- **Impacto:** Inconsistência no comportamento de agentes auxiliares.
- **Estimativa:** S (1 dia)
- **Dependências:** Nenhuma

### 🧪 Testes
#### [TEST-001] Testes Quânticos Pulados
- **Prioridade:** ⚪ Baixa
- **Contexto:** 11 testes no módulo `quantum_consciousness` estão sendo pulados (provavelmente por falta de hardware ou dependências opcionais).
- **Impacto:** Cobertura incompleta da fase experimental.
- **Estimativa:** M (Ongoing)
- **Dependências:** Hardware QPU ou simuladores avançados.

## Plano de Ataque

### Sprint 1 (Consolidação e Limpeza)
1.  **[DOC-001]** Criar relatórios de status para Phases 19, 20 e 21.
2.  **[ARCH-001]** Analisar e unificar `src/swarm` e `src/collective_intelligence`.
3.  **[DOC-002]** Criar/Atualizar `.github/copilot-instructions.md` e `.cursorrules`.

### Sprint 2 (Otimização)
1.  **[TEST-001]** Investigar testes pulados e configurar CI para simulação quântica se possível.
