#!/bin/bash
# Script de Renomeação de Serviços OmniMind
# omnimind-*.service → mind-*.service
# Criado: 2025-12-18
# Aprovado: LGTM

set -euo pipefail

BACKUP_DIR="/tmp/omnimind_services_backup"
PROJECT_ROOT="/home/fahbrain/projects/omnimind"

echo "🔄 OmniMind Service Renaming Script"
echo "===================================="
echo ""

# 1. Backup já criado, validar
if [ ! -d "$BACKUP_DIR" ]; then
    echo "❌ Backup não encontrado em $BACKUP_DIR"
    exit 1
fi

BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/*.service 2>/dev/null | wc -l)
echo "✅ Backup validado: $BACKUP_COUNT arquivos em $BACKUP_DIR"
echo ""

# 2. Função de renomeação
rename_service() {
    local file=$1
    local dir=$(dirname "$file")
    local base=$(basename "$file")
    local new_base="${base/omnimind/mind}"
    local new_file="$dir/$new_base"

    if [ "$base" != "$new_base" ]; then
        echo "  📝 $base → $new_base"
        mv "$file" "$new_file"
        return 0
    fi
    return 1
}

# 3. Renomear em config/systemd/
echo "📂 Renomeando em config/systemd/"
cd "$PROJECT_ROOT/config/systemd"
renamed_count=0
for file in omnimind*.service; do
    if [ -f "$file" ]; then
        if rename_service "$file"; then
            ((renamed_count++))
        fi
    fi
done
echo "   ✅ Renomeados: $renamed_count arquivos"
echo ""

# 4. Renomear em scripts/production/deploy/
echo "📂 Renomeando em scripts/production/deploy/"
cd "$PROJECT_ROOT/scripts/production/deploy"
renamed_count=0
for file in omnimind*.service; do
    if [ -f "$file" ]; then
        if rename_service "$file"; then
            ((renamed_count++))
        fi
    fi
done
echo "   ✅ Renomeados: $renamed_count arquivos"
echo ""

# 5. Atualizar conteúdo dos arquivos (referências internas)
echo "🔍 Atualizando referências internas..."
cd "$PROJECT_ROOT"

# Substituir em arquivos .service
find config/systemd scripts/production/deploy -name "mind*.service" -type f | while read file; do
    sed -i 's/omnimind-/mind-/g' "$file"
    sed -i 's/omnimind\./mind./g' "$file"
done

# Substituir em scripts shell
find scripts -name "*.sh" -type f | while read file; do
    sed -i 's/omnimind-\([a-z-]*\)\.service/mind-\1.service/g' "$file"
    sed -i 's/omnimind\.service/mind.service/g' "$file"
done

echo "   ✅ Referências atualizadas"
echo ""

# 6. Relatório final
echo "📊 Relatório de Renomeação"
echo "========================="
echo "Arquivos em config/systemd/:"
ls -1 config/systemd/*.service 2>/dev/null | wc -l
echo ""
echo "Arquivos em scripts/production/deploy/:"
ls -1 scripts/production/deploy/*.service 2>/dev/null | wc -l
echo ""
echo "Backup preservado em: $BACKUP_DIR"
echo ""
echo "✅ Renomeação concluída com sucesso!"
echo ""
echo "⚠️  PRÓXIMOS PASSOS:"
echo "1. Revisar mudanças: git diff"
echo "2. Se OK, commitar: git add . && git commit -m 'refactor: Rename services omnimind→mind'"
echo "3. Reload systemd: sudo systemctl daemon-reload"
echo "4. Restart serviços: sudo systemctl restart mind-backend mind-mcp"
