#!/bin/bash
# Test script to validate Φ (Phi) correction
# Run: bash test_phi_correction.sh

set -e

echo "═══════════════════════════════════════════════════════"
echo "🧪 Testing Φ (Phi) Calculation Correction"
echo "═══════════════════════════════════════════════════════"
echo ""

cd /home/fahbrain/projects/omnimind

# Activate environment
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

echo "📋 Running test: test_phi_elevates_to_target"
echo "─────────────────────────────────────────────"
python -m pytest \
    tests/consciousness/test_integration_loss.py::TestPhiElevationResults::test_phi_elevates_to_target \
    -v \
    --tb=short \
    --capture=no \
    2>&1 | tee test_phi_correction.log

echo ""
echo "═══════════════════════════════════════════════════════"
echo "📊 Result Summary"
echo "═══════════════════════════════════════════════════════"

if grep -q "PASSED" test_phi_correction.log; then
    echo "✅ TEST PASSED - Φ correction is working!"
    echo ""
    echo "📈 Φ values are now calculated using:"
    echo "   1. Harmonic mean (not arithmetic)"
    echo "   2. Single penalty (not double)"
    echo "   3. Normalized causal strengths [0-1]"
    exit 0
else
    echo "❌ TEST FAILED - Need further investigation"
    echo ""
    echo "🔍 Check output above for details"
    exit 1
fi
