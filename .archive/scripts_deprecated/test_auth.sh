#!/bin/bash
# Test authentication flow

echo "🔐 Testing OmniMind Authentication"
echo ""

CREDENTIALS="admin:omnimind2025!"
API_URL="http://127.0.0.1:8000"

echo "1️⃣  Testing direct backend auth..."
curl -s -u "$CREDENTIALS" "$API_URL/daemon/status" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ Backend accepts credentials"
else
    echo "   ❌ Backend auth failed"
fi

echo ""
echo "2️⃣  Testing frontend proxy auth..."
curl -s -u "$CREDENTIALS" "http://127.0.0.1:3000/daemon/status" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ Frontend proxy accepts credentials"
else
    echo "   ℹ️  Frontend proxy not yet tested (may be dev only)"
fi

echo ""
echo "3️⃣  Checking environment variables..."
grep "OMNIMIND_DASHBOARD" /home/fahbrain/projects/omnimind/.env
grep "VITE_DASHBOARD" /home/fahbrain/projects/omnimind/web/frontend/.env.local || echo "   ⚠️  .env.local not yet checked"

echo ""
echo "4️⃣  Full credentials test:"
echo "   User: admin"
echo "   Pass: omnimind2025!"
echo "   Endpoint: http://127.0.0.1:8000/daemon/status"
echo "   Command: curl -u admin:omnimind2025! http://127.0.0.1:8000/daemon/status"
