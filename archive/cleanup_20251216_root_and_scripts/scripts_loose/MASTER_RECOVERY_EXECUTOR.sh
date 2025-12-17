#!/bin/bash

# 🔧 MASTER RECOVERY EXECUTOR - OmniMind System Stabilization
# ============================================================================
# Este script fornece um menu para executar todos os passos de recuperação
# em ordem correta. Está PRONTO para você executar.
#
# Uso: bash scripts/MASTER_RECOVERY_EXECUTOR.sh
# ============================================================================

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Paths
PROJECT_ROOT="/home/fahbrain/projects/omnimind"
SCRIPTS_DIR="$PROJECT_ROOT/scripts"
DATA_DIR="$PROJECT_ROOT/data"

echo -e "${MAGENTA}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║  🔧 OMNIMIND MASTER RECOVERY EXECUTOR                         ║${NC}"
echo -e "${MAGENTA}║  Recovery Phase: Stabilization + Training                     ║${NC}"
echo -e "${MAGENTA}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Status check
echo -e "${CYAN}📊 PRE-EXECUTION STATUS CHECK${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check Python
echo -n "🐍 Python version: "
python3 --version 2>/dev/null || echo -e "${RED}NOT FOUND${NC}"

# Check CUDA
echo -n "🎮 CUDA status: "
python3 -c "import torch; print(f'✅ CUDA {torch.version.cuda}' if torch.cuda.is_available() else '❌ NO CUDA')" 2>/dev/null || echo "❌ PyTorch not available"

# Check services
echo -n "🗄️  Qdrant: "
curl -s --max-time 2 http://localhost:6333/healthz > /dev/null && echo "✅ Running" || echo -e "${RED}❌ NOT RUNNING${NC}"

echo -n "📢 Redis: "
redis-cli ping 2>/dev/null | grep -q PONG && echo "✅ Running" || echo -e "${YELLOW}⚠️  Check status${NC}"

echo ""

# Check system metrics
echo -e "${CYAN}💻 SYSTEM METRICS${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
nvidia-smi --query-gpu=name,driver_version,memory.total,memory.used,utilization.gpu --format=csv,noheader 2>/dev/null | while IFS=, read -r name driver mem_total mem_used util; do
    echo "GPU: $name (Driver: $driver)"
    echo "   VRAM: ${mem_used}MB / ${mem_total}MB allocated"
    echo "   Utilization: $util"
done

echo ""
echo "Integration loop cycles:"
CYCLE_COUNT=$(find "$DATA_DIR/reports/modules" -name "*integration_loop_cycle*" 2>/dev/null | wc -l)
echo "   📊 Existing: $CYCLE_COUNT cycles"

echo ""
echo "Qdrant vectors:"
python3 << 'EOF'
try:
    from qdrant_client import QdrantClient
    client = QdrantClient(url="http://localhost:6333")
    collections = client.get_collections()
    for coll in collections.collections:
        try:
            info = client.get_collection(coll.name)
            print(f"   • {coll.name}: {info.points_count} vectors")
        except:
            pass
except Exception as e:
    print(f"   ⚠️  Unable to check: {e}")
EOF

echo ""
echo -e "${CYAN}📋 EXECUTION MENU${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Choose recovery steps to execute (in order):"
echo ""
echo "  ${CYAN}1)${NC} Initialize Qdrant Collections (MUST RUN FIRST)"
echo "  ${CYAN}2)${NC} Index System Code (44k vectors training)"
echo "  ${CYAN}3)${NC} Run Integration Cycles + Stimulation (500 cycles)"
echo "  ${CYAN}4)${NC} Initialize Persistent State (from cycle data)"
echo "  ${CYAN}5)${NC} Fix GPU Memory Allocation"
echo "  ${CYAN}6)${NC} Increase Daemon Logging Verbosity"
echo ""
echo "  ${CYAN}A)${NC} Execute ALL steps (automated recovery)"
echo "  ${CYAN}Q)${NC} Exit without executing"
echo ""
read -p "Select option [1-6, A, Q]: " choice

case "$choice" in
    1)
        echo -e "${GREEN}🟢 Step 1: Initialize Qdrant Collections${NC}"
        bash "$SCRIPTS_DIR/recovery/01_init_qdrant_collections.sh"
        ;;
    2)
        echo -e "${GREEN}🟢 Step 2: Index System Code (44k vectors)${NC}"
        bash "$SCRIPTS_DIR/recovery/02_train_embeddings.sh"
        ;;
    3)
        echo -e "${GREEN}🟢 Step 3: Run Integration Cycles + Stimulation${NC}"
        bash "$SCRIPTS_DIR/recovery/03_run_integration_cycles.sh"
        ;;
    4)
        echo -e "${GREEN}🟢 Step 4: Initialize Persistent State${NC}"
        bash "$SCRIPTS_DIR/recovery/04_init_persistent_state.sh"
        ;;
    5)
        echo -e "${GREEN}🟢 Step 5: Fix GPU Memory Allocation${NC}"
        bash "$SCRIPTS_DIR/recovery/05_fix_gpu_allocation.sh"
        ;;
    6)
        echo -e "${GREEN}🟢 Step 6: Increase Daemon Logging${NC}"
        bash "$SCRIPTS_DIR/recovery/06_increase_daemon_logging.sh"
        ;;
    A|a)
        echo -e "${MAGENTA}🚀 EXECUTING FULL AUTOMATED RECOVERY${NC}"
        echo ""

        echo -e "${GREEN}Step 1/6: Initialize Qdrant Collections${NC}"
        bash "$SCRIPTS_DIR/recovery/01_init_qdrant_collections.sh" || exit 1
        sleep 5

        echo ""
        echo -e "${GREEN}Step 2/6: Index System Code (44k vectors)${NC}"
        bash "$SCRIPTS_DIR/recovery/02_train_embeddings.sh" || exit 1
        sleep 5

        echo ""
        echo -e "${GREEN}Step 3/6: Run Integration Cycles + Stimulation${NC}"
        bash "$SCRIPTS_DIR/recovery/03_run_integration_cycles.sh" || exit 1
        sleep 5

        echo ""
        echo -e "${GREEN}Step 4/6: Initialize Persistent State${NC}"
        bash "$SCRIPTS_DIR/recovery/04_init_persistent_state.sh" || exit 1
        sleep 5

        echo ""
        echo -e "${GREEN}Step 5/6: Fix GPU Memory Allocation${NC}"
        bash "$SCRIPTS_DIR/recovery/05_fix_gpu_allocation.sh" || exit 1
        sleep 5

        echo ""
        echo -e "${GREEN}Step 6/6: Increase Daemon Logging${NC}"
        bash "$SCRIPTS_DIR/recovery/06_increase_daemon_logging.sh" || exit 1

        echo ""
        echo -e "${MAGENTA}╔════════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${MAGENTA}║  ✅ AUTOMATED RECOVERY COMPLETED SUCCESSFULLY!                ║${NC}"
        echo -e "${MAGENTA}║  System should now be INTEGRATED and COMPUTING Φ correctly    ║${NC}"
        echo -e "${MAGENTA}╚════════════════════════════════════════════════════════════════╝${NC}"
        ;;
    Q|q)
        echo -e "${YELLOW}Exiting without execution${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid option${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✅ Step completed!${NC}"
echo ""
echo "📊 POST-EXECUTION STATUS:"
echo "Run: bash $SCRIPTS_DIR/MASTER_RECOVERY_EXECUTOR.sh  (to check status)"
echo ""
