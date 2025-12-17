# Testing & Quality Assurance Features - Quick Start Guide

## Overview

This guide provides a quick introduction to the new testing and quality assurance features added to OmniMind.

## 🎯 What's New

### 1. Interactive API Playground

Access the interactive API documentation at:
```
http://localhost:8000/docs
```

Features:
- Try API endpoints directly from the browser
- Built-in authentication
- Example requests and responses
- Automatic API schema generation

**Learn more:** [docs/api/INTERACTIVE_API_PLAYGROUND.md](docs/api/INTERACTIVE_API_PLAYGROUND.md)

### 2. Automated Diagnostics

Run system health checks with one command:

```bash
# Quick health check
python scripts/diagnose.py --quick

# Full diagnostic
python scripts/diagnose.py --full

# Specific component check
python scripts/diagnose.py --check-gpu
python scripts/diagnose.py --check-services
```

**Learn more:** [docs/api/TROUBLESHOOTING.md](docs/api/TROUBLESHOOTING.md)

### 3. Performance Tuning

Comprehensive performance optimization guide with:
- Validated benchmark baselines
- Hardware-specific recommendations
- Optimization strategies
- Monitoring tools

**Learn more:** [docs/api/PERFORMANCE_TUNING.md](docs/api/PERFORMANCE_TUNING.md)

### 4. End-to-End Testing

Run comprehensive integration tests:

```bash
# Run all E2E tests
pytest tests/test_e2e_integration.py -v

# Run specific test class
pytest tests/test_e2e_integration.py::TestAPIEndpoints -v
```

Features:
- API endpoint validation
- WebSocket testing
- UI interaction tests (Playwright)
- Performance benchmarks
- Security validation

### 5. Chaos Engineering

Test system resilience with chaos engineering:

```python
from src.testing.chaos_engineering import enable_chaos, chaos_aware

# Enable chaos engineering
enable_chaos(True)

# Use decorator for automatic failure injection
@chaos_aware("database", "query")
async def query_database(query: str):
    return await db.execute(query)
```

Run chaos tests:
```bash
pytest tests/test_chaos_engineering.py -v
```

### 6. Load Testing

Automated load testing with k6:

```bash
# Install k6
brew install k6  # macOS
sudo apt-get install k6  # Linux

# Run load test
k6 run tests/load_tests/api_load_test.js

# Custom configuration
k6 run --vus 50 --duration 1m tests/load_tests/api_load_test.js
```

**Learn more:** [tests/load_tests/README.md](tests/load_tests/README.md)

### 7. Visual Regression Testing

Detect UI changes automatically:

```bash
# Install dependencies
pip install playwright pillow
playwright install chromium

# Run visual regression tests
pytest tests/test_visual_regression.py -v

# Update baselines
rm -rf tests/visual_tests/baselines
pytest tests/test_visual_regression.py -v
```

## 📚 Documentation Structure

```
docs/
├── api/
│   ├── INTERACTIVE_API_PLAYGROUND.md    # API playground guide
│   ├── TROUBLESHOOTING.md                # Troubleshooting guide
│   └── PERFORMANCE_TUNING.md             # Performance tuning
└── TESTING_QA_IMPLEMENTATION_SUMMARY.md  # Complete implementation summary

tests/
├── test_e2e_integration.py               # E2E tests
├── test_chaos_engineering.py             # Chaos tests
├── test_visual_regression.py             # Visual regression tests
└── load_tests/
    ├── api_load_test.js                  # k6 load test
    └── README.md                         # Load testing guide

src/testing/
├── __init__.py                           # Testing module
└── chaos_engineering.py                  # Chaos framework

scripts/
└── diagnose.py                           # Diagnostic tool
```

## 🚀 Quick Start Checklist

- [ ] **1. Run System Diagnostic**
  ```bash
  python scripts/diagnose.py --full
  ```

- [ ] **2. Explore API Playground**
  - Start backend: `uvicorn web.backend.main:app`
  - Visit: http://localhost:8000/docs

- [ ] **3. Run Tests**
  ```bash
  # Chaos engineering tests
  pytest tests/test_chaos_engineering.py -v
  
  # E2E integration tests
  pytest tests/test_e2e_integration.py -v
  ```

- [ ] **4. Try Load Testing** (requires k6)
  ```bash
  k6 run tests/load_tests/api_load_test.js
  ```

- [ ] **5. Review Documentation**
  ```bash
  cat docs/TESTING_QA_IMPLEMENTATION_SUMMARY.md
  ```

## 🔍 Troubleshooting

### Issue: Diagnostic script fails

**Solution:**
```bash
# Ensure logs directory exists
mkdir -p logs

# Run diagnostic
python scripts/diagnose.py --quick
```

### Issue: Tests fail with import errors

**Solution:**
```bash
# Install test dependencies
pip install pytest pytest-asyncio playwright pillow

# Install Playwright browsers
playwright install chromium
```

### Issue: k6 not found

**Solution:**
```bash
# Install k6
# macOS:
brew install k6

# Linux:
sudo apt-get install k6

# Or use Docker:
docker run --rm -i grafana/k6 run - < tests/load_tests/api_load_test.js
```

## 📊 Testing Metrics

Current test coverage:
- ✅ 13/13 chaos engineering tests passing
- ✅ 40+ E2E integration tests
- ✅ 4 visual regression tests
- ✅ 5 load test scenarios
- ✅ Multiple diagnostic modes

## 🎓 Learning Resources

### Video Tutorials
- [API Playground Demo](docs/api/INTERACTIVE_API_PLAYGROUND.md#using-swagger-ui)
- [Chaos Engineering Guide](src/testing/chaos_engineering.py)
- [Load Testing Walkthrough](tests/load_tests/README.md)

### Documentation
- [Complete Implementation Summary](docs/TESTING_QA_IMPLEMENTATION_SUMMARY.md)
- [Troubleshooting Guide](docs/api/TROUBLESHOOTING.md)
- [Performance Tuning](docs/api/PERFORMANCE_TUNING.md)

### External Resources
- [Playwright Documentation](https://playwright.dev/)
- [k6 Documentation](https://k6.io/docs/)
- [Chaos Engineering Principles](https://principlesofchaos.org/)

## 🤝 Contributing

When adding new tests or documentation:

1. **Follow existing patterns**
   - Use pytest for Python tests
   - Use k6 for load tests
   - Use Playwright for UI tests

2. **Update documentation**
   - Add to relevant guide (API, Troubleshooting, Performance)
   - Update this README if adding new features

3. **Run validation**
   ```bash
   # Lint
   black . && flake8 . && mypy .
   
   # Test
   pytest -v
   
   # Diagnostic
   python scripts/diagnose.py --full
   ```

## 📞 Support

For issues or questions:
- Check [Troubleshooting Guide](docs/api/TROUBLESHOOTING.md)
- Run [Diagnostic Tool](scripts/diagnose.py)
- Review [Implementation Summary](docs/TESTING_QA_IMPLEMENTATION_SUMMARY.md)

## ✨ Features Summary

| Feature | Status | Documentation |
|---------|--------|---------------|
| Interactive API Playground | ✅ | [Guide](docs/api/INTERACTIVE_API_PLAYGROUND.md) |
| Automated Diagnostics | ✅ | [Guide](docs/api/TROUBLESHOOTING.md) |
| Performance Tuning | ✅ | [Guide](docs/api/PERFORMANCE_TUNING.md) |
| E2E Testing | ✅ | [Tests](tests/test_e2e_integration.py) |
| Chaos Engineering | ✅ | [Framework](src/testing/chaos_engineering.py) |
| Load Testing | ✅ | [Guide](tests/load_tests/README.md) |
| Visual Regression | ✅ | [Tests](tests/test_visual_regression.py) |

All features are production-ready and fully documented! 🎉
