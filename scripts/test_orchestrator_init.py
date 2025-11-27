import sys
import os
from pathlib import Path

# Adicionar raiz ao path
sys.path.insert(0, str(Path.cwd()))

print("Importing OrchestratorAgent...")
from src.agents.orchestrator_agent import OrchestratorAgent

print("Initializing OrchestratorAgent...")
try:
    orch = OrchestratorAgent("config/agent_config.yaml")
    print("OrchestratorAgent initialized successfully!")
except Exception as e:
    print(f"Failed to initialize: {e}")
    import traceback

    traceback.print_exc()
