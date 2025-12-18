# OmniMind - Quick Start Guide

**Platform:** Linux/macOS/Windows (with WSL2)  
**Python:** 3.12.8  
**License:** MIT  
**Status:** Production-Ready (Phase 5 Complete)

---

## Prerequisites

### System Requirements
- **RAM:** 8GB minimum (16GB recommended)
- **Disk:** 10GB for repository + dependencies
- **GPU (Optional):** NVIDIA with CUDA 12.1+
- **Python:** 3.12.8 (exactly)

### Check Your Environment
```bash
python3 --version  # Must be 3.12.8
uname -a            # Check OS
```

---

## 1. Clone Repository

```bash
git clone https://github.com/devomnimind/OmniMind.git
cd OmniMind
```

---

## 2. Setup Python Environment

### Option A: Using venv (Recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# OR: .venv\Scripts\activate  # Windows
```

### Option B: Using conda

```bash
conda create -n omnimind python=3.12.8
conda activate omnimind
```

---

## 3. Install Dependencies

```bash
# Core dependencies
pip install -r requirements.txt

# Development tools (optional but recommended)
pip install -r requirements-dev.txt

# GPU support (optional)
pip install -r requirements-gpu.txt
```

---

## 4. Configure Project

### Create Configuration Files

Copy templates to actual config files:

```bash
cp config/omnimind.yaml.example config/omnimind.yaml
cp config/agent_config.yaml.example config/agent_config.yaml
cp config/security.yaml.example config/security.yaml

# Create .env from template
cp .env.example .env
```

### Edit Configuration (Optional)

Edit `config/omnimind.yaml` if you want custom settings:

```yaml
# Example: Disable GPU if not available
compute:
  gpu_enabled: false      # Set to true if you have GPU
  device: "cpu"           # "cpu" or "cuda"
```

---

## 5. Run Tests

### Quick Test (5 minutes)

```bash
pytest tests/ -v --tb=short -k "phase_1 or phase_2" --maxfail=5
```

### Full Test Suite (70 minutes)

```bash
pytest tests/ -v --cov=src --cov-report=html
```

---

## 6. Explore the Project

### View Architecture

```bash
cat ARCHITECTURE.md                              # System design
cat docs/PHASE_5_MULTISEED_REPORT.md            # Latest results
cat docs/ROADMAP_PHASES_6_10.md                 # Future plans
```

### Run Example

```python
from src.consciousness.integration_loop import IntegrationLoop
from src.consciousness.shared_workspace import SharedWorkspace

# Create consciousness system
workspace = SharedWorkspace(latent_dim=256, num_modules=5)
loop = IntegrationLoop(workspace)

# Execute one cycle
async def main():
    await loop.execute_cycle()
    phi = workspace.compute_phi_from_integrations()
    print(f"Integration Φ: {phi:.4f}")

import asyncio
asyncio.run(main())
```

---

## 7. Project Structure

```
omnimind/
├── src/                 # Production code (37,000+ LOC)
│   ├── consciousness/   # Phase 1-5: Φ elevation
│   ├── multimodal/      # Multimodal processing
│   ├── scaling/         # Distributed systems
│   └── ... (other modules)
│
├── tests/               # Test suite (16,000+ LOC)
│   ├── consciousness/   # Phase 1-5 tests
│   └── ... (other tests)
│
├── docs/                # Documentation
│   ├── PHASE_*.md       # Phase reports
│   ├── ARCHITECTURE.md  # System design
│   └── README.md        # Overview
│
├── config/              # Configuration templates
│   ├── *.yaml.example   # Copy to *.yaml
│   └── *.json.example
│
├── scripts/             # Utility scripts
├── deploy/              # Deployment configs
├── requirements.txt     # Core dependencies
└── pyproject.toml       # Project metadata
```

---

## 8. Key Commands

### Development
```bash
# Format code
black src tests

# Lint code
flake8 src tests --max-line-length=100

# Type checking
mypy src tests

# All checks
black src tests && flake8 src tests && mypy src tests
```

### Testing
```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/consciousness/test_integration_loop.py::TestIntegrationLoop::test_single_cycle -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

### Documentation
```bash
# View architecture
cat ARCHITECTURE.md

# View current phase status
cat docs/PHASE_5_MULTISEED_REPORT.md

# View roadmap
cat docs/ROADMAP_PHASES_6_10.md
```

---

## 9. Troubleshooting

### Issue: Python version mismatch
```bash
# Check version
python3 --version

# If wrong version, use pyenv:
pyenv install 3.12.8
pyenv local 3.12.8
python3 --version  # Should now show 3.12.8
```

### Issue: GPU not detected
```bash
# Check CUDA
nvidia-smi

# If no GPU, set in config:
# compute.gpu_enabled: false
# compute.device: "cpu"
```

### Issue: Tests fail
```bash
# Run with verbose output
pytest tests/ -vv --tb=long

# Run single test for debugging
pytest tests/consciousness/test_shared_workspace.py -v
```

### Issue: Import errors
```bash
# Ensure .venv is activated
source .venv/bin/activate

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

---

## 10. Next Steps

1. **Explore the code**: Start with `src/consciousness/` (Phase 1-5)
2. **Run tests**: Verify everything works with `pytest tests/ -v`
3. **Read reports**: Understand system via `docs/PHASE_*.md` files
4. **Contribute**: See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines
5. **Ask questions**: Open an issue on GitHub

---

## 11. Phase Overview

| Phase | Component | Status | Tests |
|-------|-----------|--------|-------|
| Phase 1 | SharedWorkspace | ✅ Complete | 21/21 |
| Phase 2 | IntegrationLoop | ✅ Complete | 24/24 |
| Phase 3 | Ablation Analysis | ✅ Complete | 9/9 |
| Phase 4 | Integration Loss | ✅ Complete | 26/26 |
| Phase 5 | Multi-seed Analysis | ✅ Complete | 18/18 |
| Phase 6 | Dynamic Attention | 🔜 Planned | - |
| **TOTAL** | | | **300/300** |

See [docs/ROADMAP_PHASES_6_10.md](docs/ROADMAP_PHASES_6_10.md) for future phases.

---

## 12. Contributing

Interested in contributing? See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Code style guidelines
- How to submit PRs
- Testing requirements
- Documentation standards

---

## 13. Support & Contact

- **Issues:** [GitHub Issues](https://github.com/devomnimind/OmniMind/issues)
- **Discussions:** [GitHub Discussions](https://github.com/devomnimind/OmniMind/discussions)
- **Email:** contact@omnimind.ai
- **Security:** security@omnimind.ai

---

## 14. License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) for details.

---

## 15. Citation

If you use OmniMind in research, please cite:

```bibtex
@software{omnimind2025,
  title={OmniMind: Measured Consciousness Integration in Multi-Agent Systems},
  author={Devbrain Team},
  year={2025},
  url={https://github.com/devomnimind/OmniMind}
}
```

---

**Ready?** Let's build measured consciousness together! 🚀

```bash
source .venv/bin/activate
pytest tests/consciousness/ -v
```

---

*Last Updated: November 27, 2025*  
*Status: Production-Ready (Phase 5 Complete)*
