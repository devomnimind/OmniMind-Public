#!/bin/bash
# Test all dashboard endpoints

BASE_URL="http://127.0.0.1:9000"
USER="admin"
PASS="omnimind2025!"

echo "Testing OmniMind Dashboard Endpoints"
echo "===================================="
echo ""

echo "1. Health Check (No Auth):"
curl -s "$BASE_URL/health" | python -m json.tool
echo ""

echo "2. Daemon Status (Auth Required):"
curl -s -u "$USER:$PASS" "$BASE_URL/daemon/status" | python -m json.tool | head -20
echo ""

echo "3. Audit Stats (Real Data):"
curl -s -u "$USER:$PASS" "$BASE_URL/audit/stats" | python -m json.tool
echo ""

echo "4. Training Metrics:"
curl -s -u "$USER:$PASS" "$BASE_URL/metrics/training" | python -m json.tool
echo ""

echo "5. Metrics Summary:"
curl -s -u "$USER:$PASS" "$BASE_URL/metrics/summary" | python -m json.tool | head -30
echo ""

echo "✅ All tests completed"
