#!/bin/bash

##############################################################################
# Security Validation for Public Repository
#
# Ensures NO sensitive data leaks in public repo:
# - No API keys, passwords, tokens
# - No private configuration
# - No research/proprietary code
# - No large data files
#
# Usage: ./validate_public_repo.sh [directory]
##############################################################################

set -e

TARGET_DIR="${1:-.}"

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║         🔒 Public Repository Security Validation                          ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

ERRORS=0
WARNINGS=0

# Function to report error
error() {
    echo "❌ ERROR: $1"
    ((ERRORS++))
}

# Function to report warning
warning() {
    echo "⚠️  WARNING: $1"
    ((WARNINGS++))
}

# Function to report success
success() {
    echo "✅ $1"
}

cd "$TARGET_DIR"

echo "🔍 Scanning for sensitive data..."
echo ""

# Check for API keys
if grep -r "api_key\|API_KEY\|apiKey" . --include="*.py" --include="*.yaml" --include="*.json" 2>/dev/null | grep -v "# api_key" | grep -v "example"; then
    error "Found potential API keys"
else
    success "No API keys found"
fi

# Check for passwords
if grep -r "password\|PASSWORD\|pwd" . --include="*.py" --include="*.yaml" --include="*.json" 2>/dev/null | grep -v "example\|documentation\|#" | grep -v "\.md"; then
    warning "Found potential password references (verify manually)"
else
    success "No password references found"
fi

# Check for tokens
if grep -r "token\|TOKEN\|secret" . --include="*.py" --include="*.yaml" 2>/dev/null | grep -v "example\|Bearer" | grep -v "\.md" | head -5; then
    warning "Found potential token references (verify manually)"
else
    success "No token references found"
fi

echo ""
echo "📂 Checking file structure..."
echo ""

# Check for data directory
if [ -d "data" ]; then
    error "data/ directory exists (should be removed)"
else
    success "No data/ directory"
fi

# Check for models directory
if [ -d "models" ]; then
    error "models/ directory exists (should be removed)"
else
    success "No models/ directory"
fi

# Check for notebooks
if find . -name "*.ipynb" 2>/dev/null | head -1; then
    warning "Found Jupyter notebooks"
else
    success "No Jupyter notebooks"
fi

# Check for research files
if [ -d "docs/research" ]; then
    error "docs/research/ directory exists"
else
    success "No research documentation"
fi

# Check for large files
echo ""
echo "📦 Checking file sizes..."
LARGE_FILES=$(find . -type f -size +50M 2>/dev/null | grep -v "\.git" | head -10)
if [ -n "$LARGE_FILES" ]; then
    warning "Found large files:"
    echo "$LARGE_FILES" | while read f; do
        ls -lh "$f"
    done
else
    success "No large files (>50MB)"
fi

echo ""
echo "📋 File structure validation..."
echo ""

# Check required directories
REQUIRED_DIRS=("src" "tests" "scripts" "config" "requirements" "docs")
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        success "✓ $dir/"
    else
        warning "Missing directory: $dir/"
    fi
done

echo ""
echo "📊 Repository Statistics:"
echo ""
echo "   Python files: $(find . -name "*.py" -type f | wc -l)"
echo "   Test files: $(find ./tests -name "*.py" -type f 2>/dev/null | wc -l)"
echo "   Documentation: $(find . -name "*.md" -type f | wc -l)"
echo "   Total size: $(du -sh . | cut -f1)"
echo ""

# Check git status
if [ -d ".git" ]; then
    echo "🔗 Git Status:"
    echo "   Commits: $(git rev-list --count HEAD 2>/dev/null || echo '0')"
    if [ -n "$(git remote -v 2>/dev/null)" ]; then
        echo "   Remote: $(git remote get-url origin 2>/dev/null || echo 'Not set')"
    else
        echo "   Remote: Not configured"
    fi
    echo ""
fi

# Summary
echo "╔════════════════════════════════════════════════════════════════════════════╗"
if [ $ERRORS -eq 0 ] && [ $WARNINGS -le 2 ]; then
    echo "║                    ✅ VALIDATION PASSED                                ║"
    echo "║              Safe to push to public repository                        ║"
else
    echo "║                   ⚠️  REVIEW REQUIRED                                  ║"
    if [ $ERRORS -gt 0 ]; then
        echo "║   Fix $ERRORS error(s) before pushing to public                     ║"
    fi
fi
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

if [ $ERRORS -gt 0 ]; then
    exit 1
fi

exit 0
