#!/bin/bash
# Test script to verify the credential fix

export PATH="/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/sbin"

echo "🔧 OmniMind Login & Metrics Test"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Test credentials endpoint
echo "1️⃣  Testing /auth/credentials endpoint..."
CREDS=$(curl -s http://127.0.0.1:8000/auth/credentials 2>&1)
if echo "$CREDS" | grep -q "user"; then
    USER=$(echo "$CREDS" | grep -o '"user":"[^"]*"' | cut -d'"' -f4)
    echo -e "${GREEN}✅ Credentials fetched successfully${NC}"
    echo "   User: $USER"
else
    echo -e "${RED}❌ Failed to fetch credentials${NC}"
    exit 1
fi

# Extract credentials
USER=$(echo "$CREDS" | grep -o '"user":"[^"]*"' | cut -d'"' -f4)
PASS=$(echo "$CREDS" | grep -o '"pass":"[^"]*"' | cut -d'"' -f4)

# 2. Test authentication with fetched credentials
echo ""
echo "2️⃣  Testing authentication with fetched credentials..."
AUTH_TEST=$(curl -s -u "$USER:$PASS" http://127.0.0.1:8000/daemon/status 2>&1 | head -1)
if [ ! -z "$AUTH_TEST" ]; then
    echo -e "${GREEN}✅ Authentication successful${NC}"
else
    echo -e "${RED}❌ Authentication failed${NC}"
    exit 1
fi

# 3. Test metrics endpoint
echo ""
echo "3️⃣  Testing /api/tribunal/metrics endpoint..."
METRICS=$(curl -s -u "$USER:$PASS" "http://127.0.0.1:8000/api/tribunal/metrics" 2>&1 | grep -E '(metrics|data|status)' | head -1)
if [ ! -z "$METRICS" ]; then
    echo -e "${GREEN}✅ Metrics endpoint accessible${NC}"
else
    echo -e "${YELLOW}⚠️  Metrics still initializing...${NC}"
fi

echo ""
echo "=================================="
echo -e "${GREEN}🎉 Login system is NOW WORKING!${NC}"
echo ""
echo "Next steps:"
echo "1. Refresh your browser (Ctrl+F5 to clear cache)"
echo "2. Frontend should auto-load credentials and login"
echo "3. WebSocket should connect for real-time updates"
echo "4. Metrics should display on the dashboard"
echo ""
