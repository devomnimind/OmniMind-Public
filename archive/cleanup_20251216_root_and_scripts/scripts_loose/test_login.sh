#!/bin/bash
# Quick login test script

echo "🧪 Testing OmniMind Login Flow"
echo ""

# Check if backend is running
if ! pgrep -f "uvicorn.*main:app" > /dev/null; then
    echo "❌ Backend not running. Start it with:"
    echo "   cd /home/fahbrain/projects/omnimind"
    echo "   python -m uvicorn web.backend.main:app --host 0.0.0.0 --port 8000 &"
    exit 1
fi

echo "✅ Backend is running"
echo ""

# Step 1: Get credentials
echo "Step 1: Fetching credentials from /auth/credentials"
RESPONSE=$(curl -s -m 5 http://localhost:8000/auth/credentials)
USER=$(echo "$RESPONSE" | python -c "import sys,json; print(json.load(sys.stdin).get('user', ''))" 2>/dev/null)
PASS=$(echo "$RESPONSE" | python -c "import sys,json; print(json.load(sys.stdin).get('pass', ''))" 2>/dev/null)

if [ -z "$USER" ] || [ -z "$PASS" ]; then
    echo "❌ Failed to fetch credentials"
    echo "Response: $RESPONSE"
    exit 1
fi

echo "✅ Credentials fetched: $USER / ***"
echo ""

# Step 2: Test /daemon/status
echo "Step 2: Testing /daemon/status with credentials"
STATUS_RESPONSE=$(curl -s -m 5 -u "$USER:$PASS" http://localhost:8000/daemon/status)

if echo "$STATUS_RESPONSE" | grep -q "Invalid credentials"; then
    echo "❌ Credentials rejected by /daemon/status"
    echo "Response: $STATUS_RESPONSE"
    exit 1
elif echo "$STATUS_RESPONSE" | grep -q "error"; then
    echo "⚠️  Got error response:"
    echo "$STATUS_RESPONSE" | python -m json.tool
    exit 1
else
    echo "✅ /daemon/status responded successfully"
    echo "Response (first 10 lines):"
    echo "$STATUS_RESPONSE" | python -m json.tool | head -10
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Login test PASSED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 Frontend should now be able to login with these credentials"
echo "   or auto-load them from the /auth/credentials endpoint"
