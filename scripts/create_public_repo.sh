#!/bin/bash

##############################################################################
# OmniMind Public Repository Migration Script
#
# Creates a clean public repository with:
# - Production code only
# - Test suite
# - Technical documentation
# - No research, papers, ideas, or internal docs
#
# Usage: ./create_public_repo.sh [target_directory] [github_url]
# Example: ./create_public_repo.sh /tmp/omnimind-public https://github.com/devomnimind/OmniMind.git
##############################################################################

set -e

TARGET_DIR="${1:-.}/omnimind-public"
GITHUB_URL="${2:-}"
SOURCE_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║         🚀 OmniMind Public Repository Migration                           ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Source: $SOURCE_DIR"
echo "Target: $TARGET_DIR"
echo ""

# Step 1: Create target directory
echo "📁 Creating target directory..."
mkdir -p "$TARGET_DIR"
cd "$TARGET_DIR"
echo "✅ Directory created: $TARGET_DIR"
echo ""

# Step 2: Initialize git repo
echo "🔧 Initializing git repository..."
git init
git branch -M main
echo "✅ Git initialized (main branch)"
echo ""

# Step 3: Create production .gitignore
echo "📝 Creating .gitignore (production)..."
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*.pyo
.pytest_cache/
.mypy_cache/
.coverage
*.egg-info/
dist/
build/

# Virtual environments
.venv/
venv/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Node
node_modules/
npm-debug.log

# System
.DS_Store
Thumbs.db

# Environment
.env
config/dashboard_auth.json

# Data & Models
data/
models/
logs/
*.log

# Development only
docs/research/
docs/roadmaps/
docs/archive/
notebooks/
ibm_results/
real_evidence/
archive/
backups_compressed/
.sonar/
EOF
echo "✅ .gitignore created"
echo ""

# Step 4: Copy production code
echo "📂 Copying production code..."
mkdir -p src tests scripts config requirements docs

# Copy main source
cp -r "$SOURCE_DIR/src"/* src/ 2>/dev/null || echo "   ⚠️  src/ directory not found"

# Copy tests
cp -r "$SOURCE_DIR/tests"/* tests/ 2>/dev/null || echo "   ⚠️  tests/ directory not found"

# Copy production scripts
mkdir -p scripts/canonical scripts/services
cp -r "$SOURCE_DIR/scripts/canonical"/* scripts/canonical/ 2>/dev/null || echo "   ⚠️  scripts/canonical/ not found"
cp -r "$SOURCE_DIR/scripts/services"/* scripts/services/ 2>/dev/null || echo "   ⚠️  scripts/services/ not found"

# Copy configs
cp "$SOURCE_DIR/config/omnimind.yaml" config/ 2>/dev/null || echo "   ⚠️  omnimind.yaml not found"
cp "$SOURCE_DIR/config/pytest.ini" config/ 2>/dev/null || echo "   ⚠️  pytest.ini not found"
cp "$SOURCE_DIR/config/mypy.ini" config/ 2>/dev/null || echo "   ⚠️  mypy.ini not found"

# Copy requirements
cp -r "$SOURCE_DIR/requirements"/* requirements/ 2>/dev/null || echo "   ⚠️  requirements/ not found"

# Copy project config
cp "$SOURCE_DIR/pyproject.toml" . 2>/dev/null || echo "   ⚠️  pyproject.toml not found"

echo "✅ Code copied"
echo ""

# Step 5: Copy documentation (technical only)
echo "📚 Copying technical documentation..."
cp "$SOURCE_DIR/docs/SERVICE_UPDATE_PROTOCOL.md" docs/ 2>/dev/null || echo "   ⚠️  SERVICE_UPDATE_PROTOCOL.md not found"
cp "$SOURCE_DIR/docs/GRACEFUL_RESTART_GUIDE.md" docs/ 2>/dev/null || echo "   ⚠️  GRACEFUL_RESTART_GUIDE.md not found"
cp "$SOURCE_DIR/README.md" . 2>/dev/null || echo "   ⚠️  README.md not found"
cp "$SOURCE_DIR/LICENSE" . 2>/dev/null || echo "   ⚠️  LICENSE not found"
cp "$SOURCE_DIR/CITATION.cff" . 2>/dev/null || echo "   ⚠️  CITATION.cff not found"

echo "✅ Documentation copied"
echo ""

# Step 6: Create .gitkeep files for empty directories
echo "🔑 Creating directory markers..."
touch src/.gitkeep
touch tests/.gitkeep
echo "✅ Directory markers created"
echo ""

# Step 7: Initial commit
echo "💾 Creating initial commit..."
git add .
git commit -m "Initial commit: OmniMind public repository

- Clean production codebase
- Complete test suite
- Technical documentation
- Service management scripts
- GPU-accelerated QAOA optimizer
- Service Update Protocol
- Graceful restart system"

echo "✅ Initial commit created"
echo ""

# Step 8: Add remote if provided
if [ -n "$GITHUB_URL" ]; then
    echo "🔗 Adding GitHub remote..."
    git remote add origin "$GITHUB_URL"
    echo "✅ Remote added: $GITHUB_URL"
    echo ""
    echo "📌 To push to GitHub, run:"
    echo "   cd $TARGET_DIR"
    echo "   git push -u origin main"
else
    echo "⏳ No GitHub URL provided"
    echo "   To add later, run:"
    echo "   git remote add origin https://github.com/YOUR_USER/omnimind-public.git"
    echo "   git push -u origin main"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║              ✅ Public Repository Created Successfully                    ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Repository Statistics:"
du -sh "$TARGET_DIR" 2>/dev/null || echo "   (Size will show after full clone)"
echo ""
echo "📂 Contents:"
find "$TARGET_DIR" -type f -name '*.py' | wc -l | xargs echo "   Python files:"
find "$TARGET_DIR" -type f -name '*.md' | wc -l | xargs echo "   Markdown files:"
echo ""
echo "🚀 Next Steps:"
echo "   1. Review the repository at: $TARGET_DIR"
echo "   2. Make sure all sensitive data is removed"
echo "   3. Test building and running locally"
echo "   4. Push to GitHub with: git push -u origin main"
echo ""
