#!/bin/bash
# Setup Validation Hooks Script
# Configura os hooks de git para validação automática

set -e

echo "🔧 Configurando hooks de validação OmniMind..."

# Verificar se estamos na raiz do projeto
if [[ ! -f "scripts/validation_lock.sh" ]]; then
    echo "❌ Execute este script da raiz do projeto OmniMind"
    exit 1
fi

# Verificar se .git existe
if [[ ! -d ".git" ]]; then
    echo "❌ Diretório .git não encontrado. Este não é um repositório git?"
    exit 1
fi

# Criar diretório de hooks se não existir
mkdir -p .git/hooks

# Copiar hooks
echo "📋 Instalando hooks..."

# Hook pre-commit
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# OmniMind Pre-Commit Hook
# Bloqueia commits que não passem nas validações obrigatórias

echo "🔒 Executando validações OmniMind antes do commit..."

# Caminho para o script de validação
VALIDATION_SCRIPT="scripts/validation_lock.sh"

# Verificar se o script existe
if [[ ! -f "$VALIDATION_SCRIPT" ]]; then
    echo "❌ Script de validação não encontrado: $VALIDATION_SCRIPT"
    echo "Execute: ./scripts/setup_validation_hooks.sh"
    exit 1
fi

# Executar validações
if ! bash "$VALIDATION_SCRIPT"; then
    echo ""
    echo "❌ Validações falharam! Commit bloqueado."
    echo "Corrija os erros acima antes de tentar commitar novamente."
    echo ""
    echo "Para pular validações (APENAS EM CASOS EXTREMOS):"
    echo "git commit --no-verify"
    echo ""
    exit 1
fi

echo "✅ Todas as validações passaram. Commit autorizado."
exit 0
EOF

# Hook pre-push
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash
# OmniMind Pre-Push Hook
# Bloqueia pushes que não passem nas validações obrigatórias

echo "🔒 Executando validações OmniMind antes do push..."

# Caminho para o script de validação
VALIDATION_SCRIPT="scripts/validation_lock.sh"

# Verificar se o script existe
if [[ ! -f "$VALIDATION_SCRIPT" ]]; then
    echo "❌ Script de validação não encontrado: $VALIDATION_SCRIPT"
    echo "Execute: ./scripts/setup_validation_hooks.sh"
    exit 1
fi

# Executar validações completas (incluindo testes pesados)
if ! bash "$VALIDATION_SCRIPT" --full; then
    echo ""
    echo "❌ Validações falharam! Push bloqueado."
    echo "Corrija os erros acima antes de tentar fazer push novamente."
    echo ""
    echo "Para pular validações (APENAS EM CASOS EXTREMOS):"
    echo "git push --no-verify"
    echo ""
    exit 1
fi

echo "✅ Todas as validações passaram. Push autorizado."
exit 0
EOF

# Tornar executáveis
chmod +x .git/hooks/pre-commit .git/hooks/pre-push

echo "✅ Hooks instalados com sucesso!"
echo ""
echo "🎯 Funcionalidades:"
echo "  • pre-commit: Bloqueia commits com validações falhadas"
echo "  • pre-push: Bloqueia pushes com validações completas falhadas"
echo ""
echo "💡 Para pular validações (apenas em emergências):"
echo "  git commit --no-verify"
echo "  git push --no-verify"
echo ""
echo "🧪 Teste os hooks:"
echo "  git add . && git commit -m 'test'"
echo "  git push origin main"