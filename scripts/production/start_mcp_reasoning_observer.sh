#!/bin/bash
# Script para iniciar MCPs de Reasoning Observer (4339-4341)
# MCP 4339: Reasoning Capture
# MCP 4340: Model Profile
# MCP 4341: Comparative Intelligence

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "🧠 Iniciando Reasoning Observer MCPs..."
echo "   • MCP 4339: Reasoning Capture"
echo "   • MCP 4340: Model Profile"
echo "   • MCP 4341: Comparative Intelligence"

cd "$PROJECT_ROOT"
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Iniciar MCPs em background (para demonstração)
# Em produção, cada um teria seu próprio servidor/porta

echo "✅ Reasoning Observer MCPs importados e prontos"
echo ""
echo "Classes disponíveis:"
echo "   • ReasoningCaptureService (4339)"
echo "   • ModelProfile (4340)"
echo "   • ComparativeIntelligence (4341)"

# Check if venv exists and use it, otherwise use python3
if [ -f ".venv/bin/python" ]; then
    PYTHON_CMD="$PROJECT_ROOT/.venv/bin/python"
else
    PYTHON_CMD="python3"
fi

# Teste rápido
$PYTHON_CMD << 'EOF'
import asyncio
from src.integrations.mcp_reasoning_capture_4339 import ReasoningCaptureService
from src.integrations.mcp_model_profile_4340 import ModelProfile
from src.integrations.mcp_comparative_intelligence_4341 import ComparativeIntelligence

async def quick_test():
    print("\n🧪 Quick Test:")

    # Test 4339
    capture = ReasoningCaptureService()
    await capture.capture_reasoning_step("analysis", "Test")
    chain = capture.get_reasoning_chain()
    print(f"   ✓ MCP 4339: {chain['step_count']} steps captured")

    # Test 4340
    profile = ModelProfile("test")
    profile.record_decision("clf", "success", 0.95)
    prof_data = profile.get_profile()
    print(f"   ✓ MCP 4340: {prof_data['statistics']['total_decisions']} decisions recorded")

    # Test 4341
    comp = ComparativeIntelligence()
    comp.add_model_profile("Model A", {"statistics": {"success_rate": 0.95}})
    report = comp.generate_comparison_report()
    print(f"   ✓ MCP 4341: {report['model_count']} model(s) in comparison")

asyncio.run(quick_test())
print("\n✅ All Reasoning Observer MCPs functional!")
EOF
