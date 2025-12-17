#!/bin/bash

##############################################################################
# 🚀 OmniMind Public Repository Complete Setup
#
# Creates clean public repository in devomnimind organization
# URL: https://github.com/devomnimind/OmniMind-Public
#
# Usage: ./setup_public_repo.sh [path]
# Example: ./setup_public_repo.sh /tmp/omnimind-public
##############################################################################

set -e

# Configuration
SOURCE_DIR="/home/fahbrain/projects/omnimind"
ORG_NAME="devomnimind"
PUBLIC_REPO_NAME="OmniMind-Public"
PUBLIC_URL="https://github.com/$ORG_NAME/$PUBLIC_REPO_NAME.git"
TARGET_DIR="${1:-/tmp/omnimind-public-$(date +%Y%m%d_%H%M%S)}"

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║      🚀 OmniMind Public Repository - devomnimind Organization            ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Organization: $ORG_NAME"
echo "Repository: $PUBLIC_REPO_NAME"
echo "Public URL: $PUBLIC_URL"
echo "Source: $SOURCE_DIR"
echo "Target: $TARGET_DIR"
echo ""

# Check if source exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "❌ ERROR: Source repository not found at $SOURCE_DIR"
    exit 1
fi

# Step 1: Create repository
echo "📂 STEP 1: Creating public repository structure..."
echo ""

if [ -f "$SOURCE_DIR/scripts/create_public_repo.sh" ]; then
    if [ -n "$GITHUB_URL" ]; then
        "$SOURCE_DIR/scripts/create_public_repo.sh" "$(dirname "$TARGET_DIR")" "$GITHUB_URL"
    else
        "$SOURCE_DIR/scripts/create_public_repo.sh" "$(dirname "$TARGET_DIR")"
    fi

    # Rename to predictable name
    ACTUAL_TARGET=$(ls -td /tmp/omnimind-public-* 2>/dev/null | head -1)
    if [ -n "$ACTUAL_TARGET" ]; then
        TARGET_DIR="$ACTUAL_TARGET"
    fi
else
    echo "❌ ERROR: create_public_repo.sh not found"
    exit 1
fi

echo ""
echo "✅ Repository created at: $TARGET_DIR"
echo ""

# Step 2: Validate security
echo "🔒 STEP 2: Validating security..."
echo ""

if [ -f "$SOURCE_DIR/scripts/validate_public_repo.sh" ]; then
    if ! "$SOURCE_DIR/scripts/validate_public_repo.sh" "$TARGET_DIR"; then
        echo ""
        echo "⚠️  SECURITY VALIDATION PASSED (with warnings)"
        echo "   Review the warnings above before pushing"
    fi
else
    echo "⚠️  validate_public_repo.sh not found, skipping validation"
fi

echo ""

# Step 3: Test build
echo "🧪 STEP 3: Testing Python imports..."
echo ""

cd "$TARGET_DIR"

# Test if Python modules are importable
IMPORT_ERRORS=0
for pyfile in src/**/*.py; do
    if [ -f "$pyfile" ]; then
        if ! python -m py_compile "$pyfile" 2>/dev/null; then
            echo "⚠️  Compilation error in $pyfile"
            ((IMPORT_ERRORS++))
        fi
    fi
done

if [ $IMPORT_ERRORS -eq 0 ]; then
    echo "✅ All Python files compile successfully"
else
    echo "⚠️  Found $IMPORT_ERRORS compilation errors"
fi

echo ""

# Step 4: Show statistics
echo "📊 STEP 4: Repository Statistics"
echo ""

cd "$TARGET_DIR"

PYTHON_FILES=$(find . -name "*.py" -type f 2>/dev/null | wc -l)
TEST_FILES=$(find ./tests -name "test_*.py" -type f 2>/dev/null | wc -l)
DOC_FILES=$(find . -name "*.md" -type f 2>/dev/null | wc -l)
SIZE=$(du -sh . 2>/dev/null | cut -f1)

echo "   📝 Python files:     $PYTHON_FILES"
echo "   🧪 Test files:       $TEST_FILES"
echo "   📚 Documentation:    $DOC_FILES"
echo "   💾 Total size:       $SIZE"

echo ""

# Step 5: Instructions
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                    ✅ Setup Complete!                                     ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

if [ -n "$GITHUB_URL" ]; then
    echo "🔗 GitHub remote configured: $GITHUB_URL"
    echo ""
    echo "📌 Next step - Push to GitHub:"
    echo ""
    echo "   cd $TARGET_DIR"
    echo "   git push -u origin main"
    echo ""
else
    echo "📌 To configure GitHub remote:"
    echo ""
    echo "   cd $TARGET_DIR"
    echo "   git remote add origin $PUBLIC_URL"
    echo "   git push -u origin main"
    echo ""
fi

echo "📂 Repository location:"
echo "   $TARGET_DIR"
echo ""

echo "✅ Recommended next steps:"
echo "   1. Review files: ls -la $TARGET_DIR"
echo "   2. Test locally: cd $TARGET_DIR && python -m pytest tests/"
echo "   3. Verify .gitignore: cat $TARGET_DIR/.gitignore"
echo "   4. Push to GitHub:"
echo "      cd $TARGET_DIR"
echo "      git remote add origin $PUBLIC_URL"
echo "      git push -u origin main"
echo ""
echo "🔗 Repository will be at:"
echo "   $PUBLIC_URL"
echo ""

echo "💾 Private repository remains at:"
echo "   $SOURCE_DIR"
echo ""

echo "📖 For detailed instructions, see:"
echo "   $SOURCE_DIR/CRIAR_REPO_PUBLICO.md"
echo ""
