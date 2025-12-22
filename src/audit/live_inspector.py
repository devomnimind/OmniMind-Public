"""
OMNIMIND LIVE INSPECTOR
Monitora quais módulos são carregados na memória durante a execução.
Identifica 'Código Morto' vs 'Tecido Vivo'.
"""

import sys
import psutil
import os
import importlib
from typing import Tuple


class ModuleInspector:
    def __init__(self, root_package="src"):
        self.root_package = root_package
        self.initial_modules = set(sys.modules.keys())
        self.process = psutil.Process(os.getpid())

    def scan_active_modules(self):
        """Retorna lista de módulos do projeto carregados na memória."""
        current_modules = set(sys.modules.keys())
        omnimind_modules = [m for m in current_modules if m.startswith(self.root_package)]
        return sorted(omnimind_modules)

    def get_memory_usage(self):
        """Retorna uso de memória em MB."""
        return self.process.memory_info().rss / 1024 / 1024

    def generate_report(self) -> Tuple[int, float]:
        active = self.scan_active_modules()
        mem = self.get_memory_usage()

        print(f"\n🔍 RELATÓRIO DE ENGRENAGENS VIVAS")
        print(f"-----------------------------------")
        print(f"Total de Módulos Ativos: {len(active)}")
        print(f"Consumo de Memória Atual: {mem:.2f} MB")
        print(f"Módulos Carregados (Top 20):")
        for m in active[:20]:
            print(f"  ✅ {m}")
        if len(active) > 20:
            print(f"  ... e mais {len(active)-20} módulos.")

        return len(active), mem
