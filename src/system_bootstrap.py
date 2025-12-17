"""
src/system_bootstrap.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OmniMind Bootstrap - Ubuntu 22.04 Native

Garante que imports funcionem mesmo quando:
  - Rodado via cron/systemd (que não carregam .bashrc)
  - Rodado de IDEs (que às vezes ignoram PYTHONPATH)
  - Rodado com sudo (que limpa env vars)

Uso: Importar este módulo PRIMEIRO em cualquer entry point:
  from src.system_bootstrap import bootstrap_omnimind
  bootstrap_omnimind()
"""

import os
import sys
from pathlib import Path


def bootstrap_omnimind() -> Path:
    """
    Bootstrap OmniMind no ambiente.

    Retorna: projeto_root (Path)
    """
    # 1. Detectar raiz do projeto
    # Prioridade: env var > dedução do arquivo
    env_root = os.environ.get("OMNIMIND_ROOT")

    if env_root:
        project_root = Path(env_root).absolute()
    else:
        # Assumir estrutura: src/system_bootstrap.py → /omnimind/
        project_root = Path(__file__).parent.parent.absolute()

    # 2. Inserir no sys.path (se não estiver já)
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # 3. Validar ambiente
    if sys.platform != "linux":
        print(f"⚠️  AVISO: Sistema espera Linux nativo, detectado: {sys.platform}")

    # 4. Log (apenas em modo debug)
    if os.environ.get("OMNIMIND_DEBUG"):
        print(f"✅ OmniMind Bootstrap: {project_root}")
        print(f"   sys.path[0]: {sys.path[0]}")

    return project_root


# Auto-executar ao importar
_PROJECT_ROOT = bootstrap_omnimind()
