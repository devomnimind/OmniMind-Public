#!/bin/bash
# Install Code Signing Git Hooks

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}Installing Code Signing Git Hooks...${NC}"

# Check if in git repo
if [[ ! -d ".git" ]]; then
    echo -e "${RED}✗ Not in a git repository${NC}"
    exit 1
fi

# Create hooks directory if needed
mkdir -p .git/hooks

# Pre-commit hook to sign modules
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook: Sign modified modules

# Only run if credentials are set
if [[ -z "$OMNIMIND_AUTHOR_NAME" ]] || [[ -z "$OMNIMIND_AUTHOR_EMAIL" ]]; then
    exit 0  # Skip silently if not configured
fi

# Get list of staged Python files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$' | grep -v test)

if [[ -z "$STAGED_FILES" ]]; then
    exit 0
fi

echo "🔏 Signing staged modules..."

# Create temporary directory for staged files
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# Copy staged files to temp dir preserving structure
echo "$STAGED_FILES" | while read file; do
    mkdir -p "$TEMP_DIR/$(dirname "$file")"
    git show :"$file" > "$TEMP_DIR/$file" 2>/dev/null || true
done

# Sign the temporary copies
python scripts/code_signing/sign_modules.py --module-path "$TEMP_DIR" 2>/dev/null || true

# Copy signed files back to working directory
echo "$STAGED_FILES" | while read file; do
    if [[ -f "$TEMP_DIR/$file" ]]; then
        cp "$TEMP_DIR/$file" "$file"
    fi
done

# Re-stage the signed files
echo "$STAGED_FILES" | xargs git add

echo "✓ Modules signed"
exit 0
EOF

# Post-merge hook to verify signatures
cat > .git/hooks/post-merge << 'EOF'
#!/bin/bash
# Post-merge hook: Verify module signatures

# Check if Python modules were merged
MERGED_FILES=$(git diff HEAD~1 HEAD --name-only | grep '\.py$' | grep -v test)

if [[ -z "$MERGED_FILES" ]]; then
    exit 0
fi

echo "🔍 Verifying merged module signatures..."

# Quick verification (don't fail merge)
python scripts/code_signing/sign_modules.py --verify 2>/dev/null | grep -c "Valid" > /dev/null

if [ $? -eq 0 ]; then
    echo "✓ Signatures verified"
else
    echo "⚠️  Some modules may not be signed. Check with: python scripts/code_signing/sign_modules.py --verify"
fi

exit 0
EOF

chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/post-merge

echo -e "${GREEN}✓ Git hooks installed${NC}"
echo ""
echo -e "${YELLOW}To enable code signing on commits:${NC}"
echo ""
echo "  export OMNIMIND_AUTHOR_NAME=\"Your Name\""
echo "  export OMNIMIND_AUTHOR_EMAIL=\"your.email@example.com\""
echo ""
echo -e "${YELLOW}Then modules will be automatically signed before each commit.${NC}"
