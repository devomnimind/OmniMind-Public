# OmniMind Public Repository Migration Guide

**Date:** December 17, 2025
**Purpose:** Create clean public repository with production-ready code only

## What's Included in Public Repo

✅ **INCLUDED:**
- `src/` - All production source code
- `tests/` - Complete test suite
- `scripts/canonical/` - Production scripts
- `scripts/services/` - Service management scripts
- `config/` - Configuration templates (no secrets)
- `requirements/` - Dependency specifications
- `docs/` - Technical documentation ONLY
  - Service Update Protocol
  - Graceful Restart Guide
  - Architecture docs
  - API documentation
- `pyproject.toml` - Project configuration
- `README.md` - Project overview
- `LICENSE` - License file

❌ **EXCLUDED:**
- `docs/research/` - Research papers and ideas
- `docs/roadmaps/` - Internal roadmap discussions
- `notebooks/` - Jupyter notebooks (experimental)
- `data/` - Large data files
- `models/` - Model files
- `ibm_results/` - Experimental results
- `real_evidence/` - Internal validation logs
- `.venv/` - Virtual environment
- `logs/` - Runtime logs
- `backups_compressed/` - Backups
- `deploy/` - Deployment configs (keep only essentials)
- `k8s/` - Kubernetes configs (infrastructure)
- `web/frontend/` - May be excluded (check if production-ready)

## Steps to Create Public Repo

### 1. Create New GitHub Repository
- Go to https://github.com/new
- Name: `OmniMind` (or `omnimind-public`, `omnimind-core`)
- Description: "Open-source consciousness research framework"
- Visibility: **PUBLIC**
- Add README, LICENSE (optional - we'll provide)
- Do NOT initialize with any files

### 2. Clone Current Private Repo (for reference)
```bash
cd /tmp
git clone /home/fahbrain/projects/omnimind omnimind-private-backup
cd omnimind-private-backup
```

### 3. Create Public Repo Locally
```bash
mkdir -p /home/fahbrain/projects/omnimind-public
cd /home/fahbrain/projects/omnimind-public
git init
git branch -M main  # Use 'main' instead of 'master' for public
```

### 4. Create Production .gitignore
```bash
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
.venv-*

# IDE
.vscode/
.idea/
*.swp
*.swo

# Node (if needed)
node_modules/
npm-debug.log

# System
.DS_Store
.AppleDouble
Thumbs.db

# Environment
.env
.env.local
config/dashboard_auth.json

# Data & Models (keep code only)
data/
models/
logs/
*.log

# Backups & Archives
backups_compressed/
*.tar.gz
*.zip
backup*.tar.gz

# Internal/Development
docs/research/
docs/roadmaps/
docs/archive/
notebooks/
ibm_results/
real_evidence/
archive/
.sonar/
reports/

# Temporary
.tmp/
tmp/
*.tmp
*.bak

# Deployment (keep only essentials in separate branch if needed)
k8s/
deploy/data/
deploy/monitoring/

EOF
```

### 5. Copy Production Files
```bash
# Create directory structure
mkdir -p src tests scripts config requirements docs

# Copy code
cp -r /home/fahbrain/projects/omnimind/src/* src/

# Copy tests
cp -r /home/fahbrain/projects/omnimind/tests/* tests/

# Copy production scripts
cp -r /home/fahbrain/projects/omnimind/scripts/canonical scripts/
cp -r /home/fahbrain/projects/omnimind/scripts/services scripts/

# Copy configuration templates (no secrets)
cp /home/fahbrain/projects/omnimind/config/omnimind.yaml config/
cp /home/fahbrain/projects/omnimind/config/pytest.ini config/
cp /home/fahbrain/projects/omnimind/config/mypy.ini config/

# Copy requirements
cp -r /home/fahbrain/projects/omnimind/requirements/* requirements/

# Copy main config file
cp /home/fahbrain/projects/omnimind/pyproject.toml .

# Copy technical docs only (exclude research)
mkdir -p docs
cp /home/fahbrain/projects/omnimind/docs/SERVICE_UPDATE_PROTOCOL.md docs/
cp /home/fahbrain/projects/omnimind/docs/GRACEFUL_RESTART_GUIDE.md docs/
cp /home/fahbrain/projects/omnimind/docs/ROADMAP.md docs/ # Technical roadmap only

# Copy README and LICENSE
cp /home/fahbrain/projects/omnimind/README.md .
cp /home/fahbrain/projects/omnimind/LICENSE .
cp /home/fahbrain/projects/omnimind/CITATION.cff .
```

### 6. Create Public README
```bash
cat > README.md << 'EOF'
# OmniMind: Open-Source Consciousness Research Framework

[![Tests](https://github.com/devomnimind/OmniMind/workflows/Tests/badge.svg)](https://github.com/devomnimind/OmniMind/actions)
[![Coverage](https://codecov.io/gh/devomnimind/OmniMind/branch/main/graph/badge.svg)](https://codecov.io/gh/devomnimind/OmniMind)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An open-source framework for consciousness research combining:
- Integrated Information Theory (IIT)
- Quantum computation
- Neuromorphic computing
- Machine learning

## Quick Start

```bash
git clone https://github.com/devomnimind/OmniMind.git
cd OmniMind

# Install dependencies
pip install -r requirements/requirements-gpu.txt

# Run tests
pytest tests/

# Run system
python src/main.py
```

## Documentation

- [Service Update Protocol](docs/SERVICE_UPDATE_PROTOCOL.md)
- [Graceful Restart Guide](docs/GRACEFUL_RESTART_GUIDE.md)
- [Architecture](docs/ARCHITECTURE.md)
- [API Reference](docs/API.md)

## Requirements

- Python 3.12+
- CUDA 12.1+ (for GPU support)
- 8GB RAM minimum

## Testing

```bash
# All tests
pytest tests/

# Coverage report
pytest --cov=src tests/

# Specific test file
pytest tests/consciousness/
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details

## Citation

```bibtex
@software{silva2025omnimind,
  author = {Silva, Fabricio},
  title = {OmniMind: Open-Source Consciousness Research Framework},
  year = {2025},
  url = {https://github.com/devomnimind/OmniMind}
}
```

EOF
```

### 7. Initial Commit
```bash
git add .
git commit -m "Initial commit: OmniMind public repository

- Clean production codebase
- Complete test suite
- Technical documentation
- Service management scripts
- GPU-accelerated QAOA optimizer
- Service Update Protocol
- Graceful restart system"
```

### 8. Add Remote and Push
```bash
# Add your GitHub remote
git remote add origin https://github.com/devomnimind/OmniMind.git

# Push to main branch
git push -u origin main
```

## File Size Comparison

**Private Repo:**
- Total: ~27GB
- .git: ~1GB
- Code: ~50MB
- Data/Models: ~26GB

**Public Repo:**
- Total: ~100MB
- .git: ~10MB
- Code: ~80MB
- Documentation: ~10MB

## Branches Strategy

```
main (stable releases)
├─ develop (bleeding edge)
├─ feature/gpu-qaoa (feature branches)
└─ hotfix/bug-fix (hotfixes)
```

## Automation

### GitHub Actions Workflow

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.10, 3.11, 3.12]
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -r requirements/requirements-dev.txt
      - run: pytest tests/
      - run: black --check src tests
      - run: flake8 src tests
      - run: mypy src
```

## Private Repo Status

The original private repository at `/home/fahbrain/projects/omnimind` will be:
- **Archived** locally for reference
- **Backed up** for safety
- **Not deleted** (contains research, papers, experimental code)
- **Used as source** for future public updates

## Syncing Strategy

When you update public repo:

1. Work in public repo (github.com/devomnimind/OmniMind)
2. Test and validate
3. Mirror changes to private repo (if needed)

When you add new research:

1. Work in private repo
2. Extract only production code
3. Push to public repo

## Next Steps

1. Create GitHub repository
2. Run migration steps above
3. Enable branch protection on main
4. Setup GitHub Pages for docs
5. Configure automatic tests via GitHub Actions
6. Add collaborators (if team)

---

**Status:** Ready for migration
**Date:** December 17, 2025
