#!/bin/bash
cd /home/fahbrain/projects/omnimind/docs

ARCHIVE_DIR="/run/media/fahbrain/DEV_BRAIN_CLEAN/omnimind_archives/phase15_consolidation_20251123_144557"

echo "📦 Arquivando documentação..."
echo ""

# Pastas a arquivar
FOLDERS="advanced_features analysis_reports canonical deployment implementation_reports infrastructure ml phases planning policies pt-br reports status_reports studies security"

for folder in $FOLDERS; do
    if [ -d "$folder" ]; then
        echo "Moving: $folder"
        mv "$folder" "$ARCHIVE_DIR/"
        echo "  ✓ Done"
    fi
done

echo ""
echo "📄 Movendo arquivos raiz..."

# Arquivos a mover
FILES="IMPLEMENTATION_SUMMARY.md OPENTELEMETRY_IMPLEMENTATION_DETAILED.md ARCHITECTURE.md DEVELOPMENT.md ROADMAP.md SETUP.md CUDA_QUICK_REFERENCE.md"

for file in $FILES; do
    if [ -f "$file" ]; then
        echo "Moving: $file"
        mv "$file" "$ARCHIVE_DIR/"
        echo "  ✓ Done"
    fi
done

echo ""
echo "✅ Arquivamento completo!"
echo ""
echo "📊 Resultado final:"
du -sh "$ARCHIVE_DIR"
echo ""
echo "Pastas mantidas em docs/:"
ls -d */ 2>/dev/null | sed 's/$/  ✓/'
