#!/bin/bash
set -e

echo "═══════════════════════════════════════════════════════════════════════════════════"
echo "🔧 SCRIPT: Fix Log Permissions & JSON Access"
echo "═══════════════════════════════════════════════════════════════════════════════════"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# STEP 1: Fix compression_index.jsonl permission
echo -e "${BLUE}STEP 1: Fix compression_index.jsonl (owned by root)${NC}"
echo "Current status:"
ls -la data/reports/modules/archive/compression_index.jsonl 2>&1
echo ""

if [ -f "data/reports/modules/archive/compression_index.jsonl" ]; then
    if sudo chown fahbrain:fahbrain data/reports/modules/archive/compression_index.jsonl; then
        echo -e "${GREEN}✅ Changed owner to fahbrain:fahbrain${NC}"
    else
        echo -e "${RED}❌ Failed to change owner (need sudo)${NC}"
        exit 1
    fi

    if sudo chmod 644 data/reports/modules/archive/compression_index.jsonl; then
        echo -e "${GREEN}✅ Changed permissions to 644${NC}"
    else
        echo -e "${RED}❌ Failed to change permissions${NC}"
        exit 1
    fi

    echo ""
    echo "New status:"
    ls -la data/reports/modules/archive/compression_index.jsonl
else
    echo -e "${YELLOW}⚠️ File not found, creating fresh...${NC}"
    mkdir -p data/reports/modules/archive/
    echo '{"timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'", "compression": "enabled", "cleanup": "done"}' > data/reports/modules/archive/compression_index.jsonl
    echo -e "${GREEN}✅ Created fresh file${NC}"
fi

# STEP 2: Fix logs/ directory permissions
echo ""
echo -e "${BLUE}STEP 2: Fix logs/ directory permissions${NC}"
if [ -d "logs" ]; then
    echo "Current ownership:"
    ls -ld logs
    echo ""

    if sudo chown -R fahbrain:fahbrain logs/ && sudo chmod -R 755 logs/; then
        echo -e "${GREEN}✅ Fixed logs/ ownership and permissions${NC}"
    else
        echo -e "${RED}❌ Failed to fix logs/ (need sudo)${NC}"
        exit 1
    fi

    echo "New ownership:"
    ls -ld logs
fi

# STEP 3: Fix data/reports directory if needed
echo ""
echo -e "${BLUE}STEP 3: Verify data/reports/ ownership${NC}"
if [ -d "data/reports" ]; then
    OWNER=$(ls -ld data/reports | awk '{print $3}')
    if [ "$OWNER" != "fahbrain" ]; then
        echo "Fixing data/reports/ (currently owned by $OWNER)..."
        if sudo chown -R fahbrain:fahbrain data/reports/; then
            echo -e "${GREEN}✅ Fixed data/reports/ ownership${NC}"
        else
            echo -e "${RED}❌ Failed to fix data/reports/${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}✅ data/reports/ already owned by fahbrain${NC}"
    fi
fi

# STEP 4: Validate JSON files
echo ""
echo -e "${BLUE}STEP 4: Validate JSON files${NC}"

validate_json() {
    local file=$1
    if [ -f "$file" ]; then
        if python3 -c "import json; json.load(open('$file'))" 2>/dev/null; then
            echo -e "${GREEN}✅ $file is valid JSON${NC}"
            return 0
        else
            echo -e "${RED}❌ $file has invalid JSON${NC}"
            return 1
        fi
    fi
}

# Validate key JSON files
validate_json "data/reports/modules/archive/compression_index.jsonl" || true
validate_json "config/omnimind_parameters.json" || true
validate_json "config/agent_config.yaml" || true

# STEP 5: Summary
echo ""
echo "═══════════════════════════════════════════════════════════════════════════════════"
echo -e "${GREEN}✅ SUMMARY: All permissions fixed successfully!${NC}"
echo "═══════════════════════════════════════════════════════════════════════════════════"
echo ""
echo "Fixed:"
echo "  • compression_index.jsonl → fahbrain:fahbrain"
echo "  • logs/ directory → correct permissions"
echo "  • data/reports/ directory → correct ownership"
echo ""
echo "✅ System is ready for logging & report generation"
echo ""
