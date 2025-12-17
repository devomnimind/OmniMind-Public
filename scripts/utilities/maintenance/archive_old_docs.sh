#!/bin/bash

# Archive old documentation to external drive
# Keeps: .project, api, architecture, guides, production, hardware, research, roadmaps, testing
# Archives: analysis_reports, canonical, deployment, implementation_reports, infrastructure, ml, phases, planning, policies, pt-br, reports, status_reports, studies, security, advanced_features

set -e

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
ARCHIVE_BASE="/run/media/fahbrain/DEV_BRAIN_CLEAN/omnimind_archives"
DOCS_DIR="$PROJECT_ROOT/docs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ARCHIVE_DIR="$ARCHIVE_BASE/phase15_consolidation_$TIMESTAMP"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}📦 Documentation Archive Script${NC}"
echo "======================================"
echo "Archive Base: $ARCHIVE_BASE"
echo "Archive Dir: $ARCHIVE_DIR"
echo ""

# Verify archive base exists
if [ ! -d "$ARCHIVE_BASE" ]; then
    echo -e "${RED}❌ Archive base not found: $ARCHIVE_BASE${NC}"
    echo "Creating..."
    sudo mkdir -p "$ARCHIVE_BASE"
    sudo chown fahbrain:fahbrain "$ARCHIVE_BASE"
    chmod 755 "$ARCHIVE_BASE"
fi

# Create archive directory
mkdir -p "$ARCHIVE_DIR"

# Folders to archive (old/obsolete)
FOLDERS_TO_ARCHIVE=(
    "analysis_reports"
    "canonical"
    "deployment"
    "implementation_reports"
    "infrastructure"
    "ml"
    "phases"
    "planning"
    "policies"
    "pt-br"
    "reports"
    "status_reports"
    "studies"
    "security"
    "advanced_features"
)

# Folders to keep (current/important)
FOLDERS_TO_KEEP=(
    ".project"
    "api"
    "architecture"
    "guides"
    "production"
    "hardware"
    "research"
    "roadmaps"
    "testing"
)

echo -e "${GREEN}✓ Folders to KEEP (current canonical):${NC}"
for folder in "${FOLDERS_TO_KEEP[@]}"; do
    if [ -d "$DOCS_DIR/$folder" ]; then
        size=$(du -sh "$DOCS_DIR/$folder" 2>/dev/null | cut -f1)
        echo "  ✓ $folder ($size)"
    fi
done

echo ""
echo -e "${YELLOW}📦 Folders to ARCHIVE (old/obsolete):${NC}"
total_size=0
for folder in "${FOLDERS_TO_ARCHIVE[@]}"; do
    if [ -d "$DOCS_DIR/$folder" ]; then
        size=$(du -sh "$DOCS_DIR/$folder" 2>/dev/null | cut -f1)
        echo "  → $folder ($size)"
        
        # Move to archive
        mv "$DOCS_DIR/$folder" "$ARCHIVE_DIR/$folder"
        echo -e "    ${GREEN}✓ Moved${NC}"
    fi
done

echo ""
echo -e "${YELLOW}📄 Root-level files in docs/:${NC}"
# Archive old .md files in docs/ root that are obsolete
OLD_FILES=(
    "IMPLEMENTATION_SUMMARY.md"
    "OPENTELEMETRY_IMPLEMENTATION_DETAILED.md"
    "ARCHITECTURE.md"
    "DEVELOPMENT.md"
    "ROADMAP.md"
    "SETUP.md"
)

for file in "${OLD_FILES[@]}"; do
    if [ -f "$DOCS_DIR/$file" ]; then
        size=$(stat -f%z "$DOCS_DIR/$file" 2>/dev/null | numfmt --to=iec 2>/dev/null || echo "?")
        echo "  → $file"
        mv "$DOCS_DIR/$file" "$ARCHIVE_DIR/$file"
        echo -e "    ${GREEN}✓ Moved${NC}"
    fi
done

echo ""
echo -e "${GREEN}✅ Archive Complete!${NC}"
echo "Archive Location: $ARCHIVE_DIR"
echo ""
echo -e "${YELLOW}📊 Summary:${NC}"
echo "  Canonical kept: ${#FOLDERS_TO_KEEP[@]} folders"
echo "  Archived: ${#FOLDERS_TO_ARCHIVE[@]} folders + old files"
archive_size=$(du -sh "$ARCHIVE_DIR" 2>/dev/null | cut -f1)
echo "  Archive size: $archive_size"

echo ""
echo -e "${GREEN}✓ Next steps:${NC}"
echo "  1. Verify docs/README.md exists and is canonical"
echo "  2. Run: git status"
echo "  3. Run: git add -A"
echo "  4. Run: git commit -m 'docs: Archive old documentation to external drive'"
echo "  5. Run: git push origin master"

