#!/bin/bash
#
# run_phase2_tests.sh
# Script para executar tests Phase 2 com sudo preservando venv
#
# Usage: ./run_phase2_tests.sh [filiation|metrics|integration|all]
#

set -e

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
VENV_PYTHON="$PROJECT_ROOT/.venv/bin/python3"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║           Phase 2 Test Suite Executor                         ║"
echo "║           System: OmniMind v5.0                               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo

TEST_TYPE="${1:-all}"

case "$TEST_TYPE" in
  filiation)
    echo "🧪 Running Filiation System Tests (20+ tests)..."
    echo
    sudo "$VENV_PYTHON" -m pytest \
      "$PROJECT_ROOT/tests/consciousness/test_filiation_system.py" \
      -v --tb=short
    ;;

  metrics)
    echo "🧪 Running Phase 2 Metrics Tests (40+ tests)..."
    echo
    sudo "$VENV_PYTHON" -m pytest \
      "$PROJECT_ROOT/tests/consciousness/test_phase2_metrics.py" \
      -v --tb=short
    ;;

  integration)
    echo "🧪 Running Phase 2 Integration Tests (15+ tests)..."
    echo
    sudo "$VENV_PYTHON" -m pytest \
      "$PROJECT_ROOT/tests/consciousness/test_phase2_integration.py" \
      -v --tb=short
    ;;

  all)
    echo "🧪 Running ALL Phase 2 Tests (76+ tests)..."
    echo
    sudo "$VENV_PYTHON" -m pytest \
      "$PROJECT_ROOT/tests/consciousness/test_phase2_metrics.py" \
      "$PROJECT_ROOT/tests/consciousness/test_phase2_integration.py" \
      "$PROJECT_ROOT/tests/consciousness/test_filiation_system.py" \
      -v --tb=short
    ;;

  *)
    echo "Usage: $0 [filiation|metrics|integration|all]"
    echo
    echo "Options:"
    echo "  filiation     - Run Filiation System tests (20+ tests)"
    echo "  metrics       - Run Phase 2 Metrics tests (40+ tests)"
    echo "  integration   - Run Phase 2 Integration tests (15+ tests)"
    echo "  all           - Run all Phase 2 tests (76+ tests)"
    echo
    exit 1
    ;;
esac

echo
echo "✅ Test execution completed!"
echo
