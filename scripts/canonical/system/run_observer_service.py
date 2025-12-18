#!/usr/bin/env python3
"""
Wrapper para ObserverService - Métricas de Longo Prazo
"""
import asyncio
import sys
from pathlib import Path

# Adicionar raiz do projeto ao path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.services.observer_service import ObserverService


def main():
    service = ObserverService()
    try:
        asyncio.run(service.run())
    except KeyboardInterrupt:
        print("Observer Service Stopped.")
    except Exception as e:
        print(f"Observer Service Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
