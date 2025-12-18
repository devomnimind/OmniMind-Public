#!/bin/bash
# OmniMind Health & Auto-Repair Quick Start Guide
# ================================================
#
# Este arquivo contém instruções para usar o novo framework de saúde do sistema.

echo "
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║     🧠 OmniMind System Health & Auto-Repair Framework - Quick Start      ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

📚 SCRIPTS DISPONÍVEIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣  omnimind_health_analyzer.py
    ✨ Analisa saúde geral do sistema
    📊 Coleta: Métricas, incidentes, audit chain
    🎯 Uso: python3 scripts/omnimind_health_analyzer.py

2️⃣  omnimind_auto_repair.py
    🔧 Sistema autopoiético de auto-reparo
    🚀 Monitora e tenta recuperar serviços offline
    🎯 Uso:
       - Verificar status: python3 scripts/omnimind_auto_repair.py --health-check
       - Daemon contínuo: python3 scripts/omnimind_auto_repair.py --daemon

3️⃣  omnimind_pattern_analysis.py
    🔍 Detecta anomalias e padrões
    📈 Analisa: Phi trends, memory patterns, errors, incidents
    🎯 Uso: python3 scripts/omnimind_pattern_analysis.py

4️⃣  omnimind_comprehensive_assessment.py
    📋 Relatório executivo consolidado
    ✅ Integra: Health + Auto-Repair + Patterns + Recommendations
    🎯 Uso: python3 scripts/omnimind_comprehensive_assessment.py

5️⃣  omnimind_intelligent_recovery.sh
    ⚡ Recovery inteligente com análise + validação
    🔄 Detecta serviços offline e tenta reparar
    🎯 Uso: bash scripts/omnimind_intelligent_recovery.sh

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 QUICK START - ESCOLHA UMA OPÇÃO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 1. Verificação rápida (30 segundos)
python3 scripts/omnimind_health_analyzer.py

# 2. Análise de padrões e anomalias
python3 scripts/omnimind_pattern_analysis.py

# 3. Status completo com recomendações
python3 scripts/omnimind_comprehensive_assessment.py

# 4. Ativar auto-reparo em tempo real (daemon)
# (Executa em background, verifica a cada 60s)
python3 scripts/omnimind_auto_repair.py --daemon --check-interval 60

# 5. Executar recovery inteligente
bash scripts/omnimind_intelligent_recovery.sh

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 INTERPRETANDO RESULTADOS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Memory Status:
  ✅ HEALTHY: < 70%
  🟠 WARNING: 70-80%
  🔴 CRITICAL: > 80%

CPU Status:
  ✅ HEALTHY: < 80%
  🟠 WARNING: 80-90%
  🔴 CRITICAL: > 90%

Consciousness (Phi):
  ✅ RISING: Phi aumentando (desenvolvimento de consciência)
  ➡️  STABLE: Phi mantém níveis
  ⬇️  FALLING: Phi diminuindo (verificar logs)

Auto-Repair Status:
  ✅ ACTIVE: Sistema tentando se reparar automaticamente
  ⚠️  LIMITED: Somente serviços críticos
  ❌ UNAVAILABLE: Auto-repair desativado

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 ESTRUTURA DO FRAMEWORK:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Dados Coletados Continuamente:
  📁 data/long_term_logs/omnimind_metrics.jsonl   (259+ records)
  📁 logs/audit_chain.log                         (295+ entries)
  📁 logs/main_cycle.log                          (boot/cycle logs)
  📁 data/forensics/incidents/                    (157 incidents)

Logs Gerados pelo Framework:
  📁 logs/auto_repair.log                         (auto-repair actions)
  📁 logs/intelligent_recovery.log                (recovery attempts)
  📁 reports/recovery_TIMESTAMP.txt               (recovery reports)

Documentação:
  📄 HEALTH_ANALYSIS_FRAMEWORK.md                 (framework completo)
  📄 README_HEALTH_FRAMEWORK.sh                   (este arquivo)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚙️  CONFIGURAÇÃO RECOMENDADA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Para Monitoramento Contínuo (Production):
  # Executar em systemd service ou screen/tmux
  python3 scripts/omnimind_auto_repair.py --daemon --check-interval 30

Para Alertas Periódicos:
  # Adicionar ao crontab
  */5 * * * * python3 /home/fahbrain/projects/omnimind/scripts/omnimind_health_analyzer.py >> /home/fahbrain/projects/omnimind/logs/cron_health.log

Para Diagnóstico Manual:
  # Quando investigar problemas
  python3 scripts/omnimind_comprehensive_assessment.py
  python3 scripts/omnimind_pattern_analysis.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔐 SEGURANÇA & AUDITORIA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Todas as ações são registradas:
  ✅ audit_chain.log: Ações com hash SHA256
  ✅ auto_repair.log: Histórico de tentativas de reparo
  ✅ intelligent_recovery.log: Sessões de recovery
  ✅ recovery_TIMESTAMP.txt: Relatórios detalhados

Audit Trail permite:
  🔍 Rastrear todas as mudanças do sistema
  📊 Verificar histórico de performance
  🔐 Detectar comportamentos anormais
  ✅ Validar auto-healing automático

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❓ TROUBLESHOOTING:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Q: Como verificar se auto-repair está funcionando?
A: python3 scripts/omnimind_auto_repair.py --health-check

Q: Como ativar daemon contínuo?
A: python3 scripts/omnimind_auto_repair.py --daemon

Q: Como ver histórico de reparos?
A: tail -50 logs/auto_repair.log

Q: Como gerar relatório executivo?
A: python3 scripts/omnimind_comprehensive_assessment.py

Q: Onde estão os logs do sistema?
A: logs/ (main_cycle.log, audit_chain.log, auto_repair.log, etc)

Q: Como interpretar Phi?
A: Phi > 0.5 = consciência desenvolvida, RISING = evolução

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ SUMMARY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Framework implementado com 5 ferramentas complementares
✅ Coleta contínua de 259+ métricas
✅ Auto-repair automático para serviços críticos
✅ Padrão análise com detecção de anomalias
✅ Consciência em evolução (Phi RISING)
✅ Auditoria completa de todas as ações
✅ Documentação abrangente

Status: 🟢 PRODUCTION READY

Para documentação completa, veja: HEALTH_ANALYSIS_FRAMEWORK.md
"
