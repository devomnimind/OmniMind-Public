# 🕵️ Relatório de Auditoria Forense e Plano de Organização Documental

**Data:** 02 de Dezembro de 2025
**Auditor:** GitHub Copilot (Agent)
**Status:** Planejamento (Pré-Execução)

---

## 1. Resumo Executivo

A auditoria identificou um grande volume de arquivos na raiz do projeto, muitos dos quais são artefatos de sessões anteriores, relatórios de progresso ou documentação transitória. O documento `NEURAL_SYSTEMS_COMPARISON_2016-2025.md` foi identificado como a "Fonte da Verdade" atual para a implementação científica.

A estrutura atual apresenta riscos de confusão para novos desenvolvedores e para a manutenção contínua, misturando código, configuração e múltiplos "pontos de entrada" (START_HERE, COMECE_AQUI, QUICK_START, etc.).

## 2. Inventário e Classificação

### 2.1. Fonte da Verdade (Manter e Priorizar)
*   `NEURAL_SYSTEMS_COMPARISON_2016-2025.md`: Roteiro científico e técnico atualizado (Modificado em 02/12/2025).
*   `README.md`: Ponto de entrada principal (Necessita atualização para apontar para a nova fonte da verdade).

### 2.2. Candidatos a Arquivamento (Mover para `docs/archive/sessions/`)
Estes arquivos representam estados passados ou relatórios específicos de sessões que não devem poluir a raiz do projeto.

*   `00_COMECE_AQUI.md`
*   `ANALYSIS_COMPARISON_LACANIAN_VS_IIT.md`
*   `API_INTEGRATION_STATUS.md`
*   `BEHAVIORAL_STRUCTURE_PHI_IMPACT.md`
*   `CHAOS_IMPLEMENTATION_COMPLETE.md`
*   `CHAOS_IMPLEMENTATION_SUMMARY.md`
*   `CHAOS_INSTALLATION_CHECKLIST.md`
*   `CHAOS_NAVIGATION_MAP.md`
*   `CHAOS_QUICK_START.md`
*   `CLOSURE_SESSION_COMPLETE.md`
*   `DECISION_FLOWCHART_PHI_STRATEGY.md`
*   `DELIVERY_MANIFEST.md`
*   `EXECUTIVE_SUMMARY_PHI_DECISION.md`
*   `FINAL_DELIVERY_STATUS.md`
*   `LACANIAN_REFACTORING_DOCUMENTATION.md`
*   `PHI_METRICS_ANSWER.md`
*   `QUICK_START_PHI_INCONSCIENTE.md`
*   `QUICK_START_PHI.md`
*   `RAIZ_ANALISE_ORGANIZACAO.md`
*   `RAIZ_MATRIZ_DECISORIA.md`
*   `RAIZ_SUMARIO_EXECUTIVO.md`
*   `RAIZ_VERIFICACAO_TECNICA.md`
*   `README_CHAOS_INDEX.md`
*   `RESUMO_EXECUTIVO_FINAL_PT.md`
*   `START_HERE.md`
*   `STRUCTURAL_CHANGE_PHI_ANALYSIS.md`
*   `SUMARIO_EXECUTIVO_LAYERED_INTEGRATION.md`
*   `SYNTHESIS_FINAL_COMPARISON_RECOMMENDATION.md`
*   `TECHNICAL_ANALYSIS_THREE_PHIS.md`
*   `VISUAL_SUMMARY_TABLES.md`

### 2.3. Candidatos a Exclusão (Lixo/Temporário)
*   Arquivos em `tmp/tools/` (Notas temporárias de ferramentas).
*   Arquivos vazios ou irrelevantes em `node_modules` ou `.venv` (Ignorados, mas notados).

### 2.4. Arquivos com Pendências (TODO/FIXME)
Foram identificados marcadores de "TODO" ou "FIXME" em arquivos críticos que precisam ser revisados:
*   `DELIVERY_MANIFEST.md`
*   `real_evidence/CONSCIOUSNESS_VALIDATION_SUMMARY.md`
*   `docs/ESTRATEGIA_RELEASE_PUBLICO_V1_18_0.md`
*   `docs/architecture/MCP_IMPLEMENTATION_SUMMARY.md`

### 2.5. Problemas de Formatação (HTML em Markdown)
Arquivos contendo tags HTML (`<div>`, `<br>`, etc.) que dificultam a leitura em visualizadores puramente textuais:
*   `docs/architecture/ENHANCED_AGENT_SYSTEM.md`
*   `web/frontend/README.md`

## 3. Plano de Execução

### Fase 1: Limpeza e Organização (Imediata)
1.  Criar diretório `docs/archive/sessions_2025/`.
2.  Mover todos os arquivos listados em **2.2** para este diretório.
3.  Excluir arquivos em `tmp/tools/`.

### Fase 2: Consolidação da Documentação
1.  Atualizar `README.md` na raiz:
    *   Remover referências a arquivos movidos.
    *   Adicionar link proeminente para `NEURAL_SYSTEMS_COMPARISON_2016-2025.md`.
    *   Simplificar instruções de início.
2.  Atualizar `INDEX_ALL_ARTIFACTS.md` (se mantido) para refletir a nova estrutura ou movê-lo para o arquivo.

### Fase 3: Padronização e Correção
1.  Converter HTML para Markdown puro nos arquivos identificados em **2.5**.
2.  Criar issues ou tarefas para os TODOs críticos identificados em **2.4**.

## 4. Verificação Forense
*   **Integridade:** O arquivo `NEURAL_SYSTEMS_COMPARISON_2016-2025.md` foi verificado via Git (Commit `189fa4b` de 02/12/2025) e confirmado como autêntico e recente.
*   **Rastreabilidade:** A movimentação de arquivos preservará o histórico Git (usando `git mv`).

---

**Aprovação:** Aguardando confirmação do usuário para executar a Fase 1.
