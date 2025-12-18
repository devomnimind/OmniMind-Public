#!/bin/bash
# 🚀 QUICK REFERENCE - PHASE 5 & 6 VALIDATION SCRIPTS
# Cartão de referência rápida para execução dos scripts de validação

cat << 'EOF'
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 🚀 PHASE 5 & 6 VALIDATION SCRIPTS - QUICK REFERENCE             ┃
┃ Data: 2025-12-09 | Status: PRONTO PARA EXECUÇÃO                 ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

📁 SCRIPTS CRIADOS:
───────────────────────────────────────────────────────────────────

1️⃣  VALIDAÇÃO OFICIAL
   📄 scripts/canonical/validate/validate_phase5_6_production.py (22 KB)

   Uso:
   • Full validation: python ... --full --cycles 50
   • Pré-flight only: python ... --pre-flight
   • Code validation: python ... --validate
   • Metrics only: python ... --metrics --cycles 100

   Output: logs/validation/phase5_6_validation_TIMESTAMP.json

─────────────────────────────────────────────────────────────────────

2️⃣  COLETA DE MÉTRICAS
   📄 scripts/phase5_6_metrics_production.py (13 KB)

   Uso:
   • Phase 5: python ... --phase5 --cycles 100
   • Phase 6: python ... --phase6 --cycles 100
   • Monitor: python ... --monitor --cycles 500

   Output:
   • data/monitor/phase5_metrics_TIMESTAMP.json
   • data/monitor/phase5_summary_TIMESTAMP.json
   • data/monitor/phase5_checkpoint_*.json

─────────────────────────────────────────────────────────────────────

3️⃣  SOP AUTOMATIZADO
   📄 scripts/phase5_6_standard_operating_procedure.sh (9.4 KB)

   Uso:
   • Procedimento completo: bash ... full
   • Stages individuais: bash ... validate | environment | metrics
   • Teste stage: bash ... --help

   Output: logs/phase5_6_sop/phase5_6_sop_TIMESTAMP.log

─────────────────────────────────────────────────────────────────────

4️⃣  DOCUMENTAÇÃO
   📄 docs/implementation/PROCEDIMENTO_OPERACIONAL_PHASE_5_6.md
   📄 docs/implementation/RESUMO_EXECUTIVO_SCRIPTS_VALIDACAO.md

⏱️  TIMELINE ESPERADO:
───────────────────────────────────────────────────────────────────
   Validação        45 min  ✓
   Setup Ambiente   15 min  ✓
   Code Quality     30 min  ✓
   Métricas P5      2-3 h   ✓
   Métricas P6      2-3 h   ✓
   Documentação     30 min  ✓
   Git              15 min  ✓
   ─────────────────────────
   TOTAL            6-8 h   🚀

🎯 EXECUÇÃO RÁPIDA:
───────────────────────────────────────────────────────────────────

[OPÇÃO 1] AUTOMÁTICA (RECOMENDADA):
$ bash scripts/phase5_6_standard_operating_procedure.sh full
  (Duração: ~7-8h, inclui todos os 6 stages)

[OPÇÃO 2] MANUAL (Passo a passo):

Step 1 - Validação (45 min):
$ python scripts/canonical/validate/validate_phase5_6_production.py --full

Step 2 - Setup:
$ git checkout -b phase-5-bion-$(date +%Y%m%d_%H%M%S)
$ tar -czf backup_pre_phase5_$(date +%Y%m%d_%H%M%S).tar.gz src/ tests/

Step 3 - Code Quality (30 min):
$ black src/psychoanalysis tests/psychoanalysis
$ flake8 src/psychoanalysis tests/psychoanalysis --select=E9,F63,F7,F82

Step 4 - Métricas (4-6h):
$ python scripts/phase5_6_metrics_production.py --phase5 --cycles 100
$ python scripts/phase5_6_metrics_production.py --phase6 --cycles 100

Step 5 - Documentação (30 min):
$ # Edit docs/METADATA/ESTADO_ATUAL.md, STATUS_FASES.md

Step 6 - Git (15 min):
$ git add -A
$ git commit -m "feat: Phase 5/6 implementation..."
$ git push origin phase-5-bion

📊 MÉTRICAS A VALIDAR:
───────────────────────────────────────────────────────────────────

Phase 5 (Bion):
  Φ_target = 0.026 NATS  (baseline: 0.0183, +42%)
  Ψ_target = ≥0.1247 NATS (manter)
  σ_target = ≥0.0892 NATS (manter)
  Taxa sucesso > 90%

Phase 6 (Lacan):
  Φ_target = 0.043 NATS  (baseline: 0.026, +67%)
  Ψ_target = ≥0.1300 NATS (aumentar)
  σ_target = ≥0.0950 NATS (aumentar)
  Taxa sucesso > 90%

📋 CHECKLIST PRÉ-IMPLEMENTAÇÃO:
───────────────────────────────────────────────────────────────────

☐ python --version (= 3.12.8+)
☐ nvidia-smi (GPU disponível)
☐ pip list | grep torch (= 2.5.1+cu124)
☐ Backend rodando (http://localhost:8000/health)
☐ 20GB+ espaço em disco
☐ Lido: docs/METADATA/ESTADO_ATUAL.md
☐ Lido: docs/METADATA/STATUS_FASES.md
☐ Branch correto: git branch --show-current

🔗 DOCUMENTAÇÃO:
───────────────────────────────────────────────────────────────────

Master Documents:
  • docs/METADATA/ESTADO_ATUAL.md (Status atual)
  • docs/METADATA/STATUS_FASES.md (Detalhes técnicos)
  • docs/METADATA/LINHAS_TEMPORAIS.md (Cronologia)

Implementation:
  • docs/implementation/PROCEDIMENTO_OPERACIONAL_PHASE_5_6.md
  • docs/implementation/RESUMO_EXECUTIVO_SCRIPTS_VALIDACAO.md

Scripts:
  • scripts/canonical/validate/validate_phase5_6_production.py
  • scripts/phase5_6_metrics_production.py
  • scripts/phase5_6_standard_operating_procedure.sh

⚠️  TROUBLESHOOTING:
───────────────────────────────────────────────────────────────────

Erro em STAGE 1 (Validação):
  → Verificar Python version, PyTorch, GPU
  → pip install -r requirements.txt

Erro em STAGE 3 (Testes):
  → black --check --diff src/psychoanalysis
  → black src/psychoanalysis (para corrigir)

Erro em STAGE 4 (Métricas):
  → Verificar ciclos coletados: ls -la data/monitor/
  → Executar com mais ciclos: --cycles 200
  → Revisar logs: logs/phase5_6_sop/

Erro em STAGE 6 (Git):
  → git status
  → git log --oneline -1
  → Contactar administrador se problema persistir

✅ SUCESSO ESPERADO:
───────────────────────────────────────────────────────────────────

✓ Validação de pré-requisitos passou
✓ Código formatado e linted
✓ Testes passando (>95%)
✓ Métricas Phase 5: Φ = 0.026 ± 0.003 NATS
✓ Métricas Phase 6: Φ = 0.043 ± 0.003 NATS
✓ Documentação atualizada
✓ Git commit registrado
✓ Pronto para integração e deploy

🎉 SISTEMA PRONTO PARA PHASE 5 & 6!

───────────────────────────────────────────────────────────────────
Versão: 1.0.0 | Data: 2025-12-09 | Autor: GitHub Copilot
Status: 🟢 PRONTO PARA EXECUÇÃO | Branch: phase-5-bion / phase-6-lacan
───────────────────────────────────────────────────────────────────

🚀 Para iniciar agora, execute:
   bash scripts/phase5_6_standard_operating_procedure.sh full

📖 Para ler procedimento completo:
   cat docs/implementation/PROCEDIMENTO_OPERACIONAL_PHASE_5_6.md

EOF
