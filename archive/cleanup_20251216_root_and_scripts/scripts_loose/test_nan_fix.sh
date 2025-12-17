#!/bin/bash
# Quick test: Check if NaN issue in test_trainer_step is fixed

cd /home/fahbrain/projects/omnimind

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 Testing NaN Fix: test_trainer_step"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Activate venv
source .venv/bin/activate

# Run just the failing test
python -m pytest tests/consciousness/test_integration_loss.py::TestIntegrationTrainer::test_trainer_step -xvs 2>&1 | tee /tmp/test_nan_fix.log

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check result
if grep -q "PASSED" /tmp/test_nan_fix.log; then
    echo "✅ TEST PASSED - NaN issue FIXED!"
elif grep -q "FAILED" /tmp/test_nan_fix.log; then
    echo "❌ TEST FAILED - NaN still present"
    echo ""
    echo "Error details:"
    grep -A 5 "assert nan" /tmp/test_nan_fix.log || grep -A 5 "AssertionError" /tmp/test_nan_fix.log
else
    echo "⚠️  Unable to determine test result"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
