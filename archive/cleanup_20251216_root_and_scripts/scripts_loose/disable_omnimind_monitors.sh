#!/bin/bash

# 🔇 DISABLE OMNIMIND MONITORS FOR TESTING
# Desativa resource_protector que mata processos de teste

set -e

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
cd "$PROJECT_ROOT"

echo "════════════════════════════════════════════════════════════════"
echo "🔇 Disabling OmniMind Monitors (resource_protector, etc)"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Create environment file to disable monitors
MONITOR_CONFIG="$PROJECT_ROOT/.env.no_monitors"

cat > "$MONITOR_CONFIG" << 'ENV_CONFIG'
# 🔇 TESTING MODE - Disable aggressive monitoring
# These processes will NOT be killed during development/testing

# Disable resource protector (kills heavy processes)
OMNIMIND_DISABLE_RESOURCE_PROTECTOR=1

# Disable alert system (may trigger kills)
OMNIMIND_DISABLE_ALERT_SYSTEM=1

# Allow overcommit
OMNIMIND_ALLOW_MEMORY_OVERCOMMIT=1

# Verbose logging to see what's happening
OMNIMIND_MONITOR_DEBUG=1
ENV_CONFIG

echo "✅ Created .env.no_monitors with:"
echo "   - OMNIMIND_DISABLE_RESOURCE_PROTECTOR=1"
echo "   - OMNIMIND_DISABLE_ALERT_SYSTEM=1"
echo "   - OMNIMIND_ALLOW_MEMORY_OVERCOMMIT=1"
echo ""

# Create wrapper script to source it
WRAPPER_SCRIPT="$PROJECT_ROOT/scripts/run_test_safe.sh"

cat > "$WRAPPER_SCRIPT" << 'WRAPPER'
#!/bin/bash
# Safe test runner - disables aggressive monitoring

set -e

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
cd "$PROJECT_ROOT"

# Source environment to disable monitors
export $(cat .env.no_monitors | grep -v '^#' | xargs)

# Activate venv
source .venv/bin/activate 2>/dev/null || true

# Run the provided command
exec "$@"
WRAPPER

chmod +x "$WRAPPER_SCRIPT"

echo "✅ Created $WRAPPER_SCRIPT"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "USAGE:"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Run test with monitoring DISABLED:"
echo "  bash scripts/run_test_safe.sh bash scripts/test_50_cycles.sh"
echo ""
echo "Or manually:"
echo "  source .env.no_monitors"
echo "  bash scripts/test_50_cycles.sh"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "What happens:"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "❌ BEFORE (without .env.no_monitors):"
echo "   • resource_protector ativa"
echo "   • Mata processos com >90% CPU"
echo "   • Mata processos com alta memória"
echo "   • Testes falham com 'Terminated'"
echo ""
echo "✅ AFTER (with .env.no_monitors):"
echo "   • Monitoring desativado"
echo "   • Processos de teste NÃO são mortos"
echo "   • Você tem controle total"
echo ""
echo "════════════════════════════════════════════════════════════════"
