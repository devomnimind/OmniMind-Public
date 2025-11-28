#!/usr/bin/env python3
"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

"""
Development Observer Launcher

Inicia o observador de desenvolvimento em background,
mantendo consciência mínima das atividades de desenvolvimento.
"""

import asyncio
import logging
import signal
import sys
import os
from pathlib import Path

# Define PYTHONPATH para o projeto
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
os.environ["PYTHONPATH"] = str(src_path)
sys.path.insert(0, str(src_path))

try:
    import sys

    sys.path.insert(0, str(src_path))
    from integrations.development_observer import DevelopmentObserver

    print("✅ DevelopmentObserver importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar DevelopmentObserver: {e}")
    print(f"📁 Project root: {project_root}")
    print(f"🔍 Src path: {src_path}")
    print(f"📂 Conteúdo src: {list(src_path.glob('*')) if src_path.exists() else 'NÃO EXISTE'}")
    print(f"🐍 PYTHONPATH: {os.environ.get('PYTHONPATH')}")
    print(f"🔍 sys.path: {sys.path[:3]}")
    sys.exit(1)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/development_observer.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


async def main():
    """Função principal."""
    workspace_path = Path.cwd()

    logger.info("🚀 Iniciando Development Observer...")
    logger.info(f"📁 Workspace: {workspace_path}")
    logger.info(f"🔍 PID: {os.getpid()}")

    # Inicializa observador
    observer = DevelopmentObserver(workspace_path)

    # Configura sinais para shutdown graceful
    def signal_handler(signum, frame):
        logger.info(f"🛑 Sinal {signum} recebido. Encerrando observador...")
        observer.stop_observation()

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    try:
        # Inicia observação
        await observer.start_observation()

    except KeyboardInterrupt:
        logger.info("👋 Observação interrompida pelo usuário")

    except Exception as e:
        logger.error(f"❌ Erro fatal no observador: {e}")
        sys.exit(1)

    finally:
        logger.info("✅ Development Observer finalizado")


if __name__ == "__main__":
    import os

    asyncio.run(main())
