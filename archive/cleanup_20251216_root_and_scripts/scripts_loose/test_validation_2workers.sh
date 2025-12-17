#!/bin/bash

# 🧪 Test Validation with 2 Workers Configuration (FASE 1 - VALIDAÇÃO)
# ====================================================================
# Objetivo: Testar se validação completa RÁPIDO com 2 workers por backend
# Baseline esperado: 90-150 minutos (vs 4-5 horas anterior)
#
# Uso: bash scripts/test_validation_2workers.sh [--quick|--full]
#   --quick (padrão): 2 runs × 100 cycles = ~10 minutos (teste rápido)
#   --full: 5 runs × 1000 cycles = ~90-150 minutos (validação completa)

set -e

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
TEST_MODE="${1:---quick}"  # --quick ou --full
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
TEST_LOG="$PROJECT_ROOT/logs/test_validation_2workers_${TIMESTAMP}.log"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}🧪 Test Validation with 2 Workers Configuration${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}📋 Configuration:${NC}"
echo "   Project: $PROJECT_ROOT"
echo "   Test mode: $TEST_MODE"
echo "   Log file: $TEST_LOG"
echo "   Timestamp: $TIMESTAMP"
echo ""

# Create logs directory
mkdir -p "$PROJECT_ROOT/logs"
mkdir -p "$PROJECT_ROOT/data/test_reports"

# Activate venv
cd "$PROJECT_ROOT"
source .venv/bin/activate 2>/dev/null || true

# Configure environment
export PYTHONPATH="$PROJECT_ROOT/src:$PROJECT_ROOT:$PYTHONPATH"

# 🎯 PHASE 1: Start Backend with 2 Workers
echo -e "${YELLOW}📦 PHASE 1: Starting Backend with 2 Workers...${NC}"
echo "" | tee -a "$TEST_LOG"

# Export worker configuration
export OMNIMIND_WORKERS=2
export OMNIMIND_BACKENDS=3
export OMNIMIND_WORKERS_VALIDATION=2

echo "   OMNIMIND_WORKERS=2" | tee -a "$TEST_LOG"
echo "   OMNIMIND_BACKENDS=3" | tee -a "$TEST_LOG"
echo "   OMNIMIND_WORKERS_VALIDATION=2" | tee -a "$TEST_LOG"
echo "" | tee -a "$TEST_LOG"

# Kill existing backends gracefully
echo -e "${YELLOW}🛑 Stopping existing backends...${NC}"
pkill -f "uvicorn.*main:app" 2>/dev/null || true
sleep 2

# Start cluster
echo -e "${YELLOW}🚀 Starting cluster...${NC}"
bash scripts/canonical/system/run_cluster.sh >> "$TEST_LOG" 2>&1 &
CLUSTER_PID=$!
echo "   Cluster PID: $CLUSTER_PID" | tee -a "$TEST_LOG"

# Wait for backends to be ready
echo -e "${YELLOW}⏳ Waiting for backends to be ready...${NC}"
sleep 5

# Check if backends are responding
echo -e "${YELLOW}🔍 Checking backend health...${NC}"
for port in 8000 8080 3001; do
    if curl -s http://localhost:$port/health > /dev/null 2>&1; then
        echo "   ✅ Port $port: OK" | tee -a "$TEST_LOG"
    else
        echo -e "   ${RED}❌ Port $port: FAILED${NC}" | tee -a "$TEST_LOG"
    fi
done
echo "" | tee -a "$TEST_LOG"

# 🎯 PHASE 2: Run Validation Test
echo -e "${YELLOW}📊 PHASE 2: Running Validation Test...${NC}"
echo "" | tee -a "$TEST_LOG"

# Set validation mode
export OMNIMIND_VALIDATION_MODE=true
sleep 2

# Determine test parameters
if [ "$TEST_MODE" = "--full" ]; then
    RUNS=5
    CYCLES=1000
    TEST_NAME="FULL VALIDATION (5 runs × 1000 cycles)"
    EXPECTED_TIME="90-150 minutes"
else
    RUNS=2
    CYCLES=100
    TEST_NAME="QUICK TEST (2 runs × 100 cycles)"
    EXPECTED_TIME="~10 minutes"
fi

echo -e "${YELLOW}🎯 Test Configuration:${NC}"
echo "   Mode: $TEST_NAME" | tee -a "$TEST_LOG"
echo "   Expected time: $EXPECTED_TIME" | tee -a "$TEST_LOG"
echo "   Workers: 2 per backend" | tee -a "$TEST_LOG"
echo "   Backends: 3 (1 primary + 1 secondary + 1 fallback)" | tee -a "$TEST_LOG"
echo "" | tee -a "$TEST_LOG"

# Start validation timing
START_TIME=$(date +%s)
echo -e "${BLUE}⏱️  Starting at $(date)${NC}" | tee -a "$TEST_LOG"
echo "" | tee -a "$TEST_LOG"

# Run validation
python scripts/science_validation/robust_consciousness_validation.py \
    --runs "$RUNS" \
    --cycles "$CYCLES" \
    2>&1 | tee -a "$TEST_LOG"

VALIDATION_EXIT_CODE=$?

# End timing
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
DURATION_MIN=$((DURATION / 60))
DURATION_SEC=$((DURATION % 60))

echo "" | tee -a "$TEST_LOG"
echo -e "${BLUE}⏱️  Completed at $(date)${NC}" | tee -a "$TEST_LOG"
echo -e "${BLUE}⏱️  Duration: ${DURATION_MIN}m ${DURATION_SEC}s${NC}" | tee -a "$TEST_LOG"
echo "" | tee -a "$TEST_LOG"

# 🎯 PHASE 3: Analysis
echo -e "${YELLOW}📈 PHASE 3: Test Analysis...${NC}"
echo "" | tee -a "$TEST_LOG"

if [ $VALIDATION_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ Validation test PASSED${NC}" | tee -a "$TEST_LOG"
else
    echo -e "${RED}❌ Validation test FAILED${NC}" | tee -a "$TEST_LOG"
fi

echo "" | tee -a "$TEST_LOG"

# Cleanup: Exit validation mode
unset OMNIMIND_VALIDATION_MODE
sleep 1

# Stop cluster
echo -e "${YELLOW}🛑 Stopping cluster...${NC}"
pkill -f "uvicorn.*main:app" 2>/dev/null || true

# 🎯 PHASE 4: Results Summary
echo -e "${YELLOW}📋 PHASE 4: Results Summary${NC}"
echo "" | tee -a "$TEST_LOG"

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo "Test Summary:"
echo "   Configuration: 2 workers × 3 backends (OMNIMIND_WORKERS=2)"
echo "   Duration: ${DURATION_MIN}m ${DURATION_SEC}s"
echo "   Status: $([ $VALIDATION_EXIT_CODE -eq 0 ] && echo -e "${GREEN}PASSED${NC}" || echo -e "${RED}FAILED${NC}")"
echo "   Log: $TEST_LOG"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# 📊 Performance Analysis
echo -e "${YELLOW}📊 Performance Analysis:${NC}"
echo ""

if [ "$DURATION_MIN" -lt 150 ]; then
    echo -e "${GREEN}✅ EXCELLENT: Validation completed in ${DURATION_MIN}m (< 150 min target)${NC}" | tee -a "$TEST_LOG"
elif [ "$DURATION_MIN" -lt 300 ]; then
    echo -e "${YELLOW}⚠️  ACCEPTABLE: Validation took ${DURATION_MIN}m (< 5 hours baseline)${NC}" | tee -a "$TEST_LOG"
else
    echo -e "${RED}❌ SLOW: Validation took ${DURATION_MIN}m (> 5 hours) - needs investigation${NC}" | tee -a "$TEST_LOG"
fi

echo ""

# 🎯 Next Steps
echo -e "${YELLOW}📝 Next Steps:${NC}"
echo ""
if [ $VALIDATION_EXIT_CODE -eq 0 ] && [ "$DURATION_MIN" -lt 150 ]; then
    echo "✅ RECOMMEND: Mark 2 workers as official stable configuration"
    echo "   Action: Run './scripts/canonical/system/run_cluster.sh' normally"
    echo "   Effect: 2 workers becomes default production configuration"
    echo ""
    echo "🚀 Performance: Validation reduced from 4-5 hours to ~${DURATION_MIN} minutes"
    echo "   Improvement: ~$(echo "scale=1; (300-$DURATION_MIN)/300*100" | bc)% faster"
elif [ $VALIDATION_EXIT_CODE -eq 0 ]; then
    echo "⚠️  CONDITIONAL: 2 workers works but slower than expected"
    echo "   Action: Investigate GPU utilization and CPU contention"
    echo "   Option 1: Try with 1 worker for validation (return to baseline)"
    echo "   Option 2: Reduce backends to 2 during validation (test dynamic mode)"
else
    echo "❌ FAILED: 2 workers configuration needs debugging"
    echo "   Action: Check logs for errors: tail -f $TEST_LOG"
    echo "   Option 1: Revert to 1 worker (stable fallback)"
    echo "   Option 2: Investigate resource contention issues"
fi

echo ""
echo "📚 Documentation:"
echo "   Log: tail -f $TEST_LOG"
echo "   Logs dir: ls -la $PROJECT_ROOT/logs/"
echo ""

exit $VALIDATION_EXIT_CODE
