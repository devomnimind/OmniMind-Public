# 🚫 CONFIGURAÇÕES DE SEGURANÇA - PROTEÇÃO CONTRA AI MALICIOSA
# Este arquivo reforça limitações para prevenir corrupção similar à ROO Code

# EXTENSÕES PROIBIDAS (não instalar)
FORBIDDEN_EXTENSIONS = [
    "rooveterinaryinc.roo-code-nightly",
    "any.*ai.*code.*assistant",  # Qualquer extensão AI que modifica código
    ".*autonomous.*ai.*",        # AIs autônomas
    ".*self.*modifying.*ai.*"    # AIs que se modificam
]

# CONFIGURAÇÕES DE SEGURANÇA
SECURITY_SETTINGS = {
    # Pre-commit hooks obrigatórios
    "pre_commit_required": True,
    "no_verify_bypass": True,

    # Validações automáticas
    "auto_validate_on_save": True,
    "block_commits_with_errors": True,

    # Limitações de AI
    "ai_modifications_blocked": True,
    "ai_can_only_suggest": True,
    "manual_review_required": True,

    # Monitoramento
    "log_all_changes": True,
    "backup_before_ai_action": True,
    "integrity_checks": True
}

# PROCEDIMENTOS DE SEGURANÇA
SECURITY_PROCEDURES = """
1. NUNCA instalar extensões AI que modifiquem código automaticamente
2. SEMPRE executar validações manuais antes de commits
3. SEMPRE revisar mudanças feitas por AI assistants
4. SEMPRE verificar integridade após modificações
5. BLOQUEAR commits com --no-verify exceto em emergências validadas
"""

# VERIFICAÇÃO DE INTEGRIDADE
INTEGRITY_CHECKS = [
    "Verificar presença de extensões proibidas",
    "Validar cadeia de auditoria",
    "Verificar arquivos de configuração suspeitos",
    "Executar suite completa de testes",
    "Verificar formatação e linting"
]