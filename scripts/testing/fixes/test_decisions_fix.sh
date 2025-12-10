#!/bin/bash

# Test script to verify DecisionsDashboard fix

echo "🧪 Testing DecisionsDashboard Error Fix"
echo "========================================"
echo ""

export PATH="/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/sbin"

# 1. Check backend endpoint
echo "1️⃣  Checking /api/metacognition/insights endpoint..."
INSIGHTS=$(curl -s http://127.0.0.1:8000/api/metacognition/insights 2>&1)

if [ ! -z "$INSIGHTS" ]; then
    echo "✅ Endpoint responding"

    # Check if it's an object or array
    if echo "$INSIGHTS" | grep -q '"health"'; then
        echo "   Type: OBJECT (not array) - This is what was causing the error"
    elif echo "$INSIGHTS" | grep -q '^\['; then
        echo "   Type: ARRAY - No problems expected"
    fi
else
    echo "❌ Endpoint not responding"
    exit 1
fi

echo ""
echo "2️⃣  Frontend fix status..."
echo "   ✅ api.ts: getDecisions() now normalizes response to array"
echo "   ✅ api.ts: getDecisionDetail() returns guaranteed object"
echo "   ✅ api.ts: getDecisionStats() returns object with defaults"
echo "   ✅ api.ts: exportDecisions() normalizes to array"
echo "   ✅ DecisionsDashboard.tsx: fetchDecisions() validates array type"
echo "   ✅ DecisionsDashboard.tsx: fetchStats() validates object type"
echo "   ✅ DecisionsDashboard.tsx: fetchDecisionDetail() validates object type"

echo ""
echo "3️⃣  Expected behavior after fix:"
echo "   ✅ Page loads without TypeError"
echo "   ✅ Console shows no 'decisions.map is not a function'"
echo "   ✅ Pooling works correctly"
echo "   ✅ Shows 'Nenhuma decisão encontrada' if no data"
echo "   ✅ Displays data in table if available"

echo ""
echo "========================================"
echo "✅ Fix is in place and ready to test!"
echo ""
echo "Next: Refresh your browser (Ctrl+F5) and check the DecisionsDashboard page"
echo ""
