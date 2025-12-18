"""
Pytest plugin para mostrar detalhes de CADA TESTE em tempo real.

Mostra:
- Início/fim de cada teste
- Cálculos sendo feitos
- Conexões HTTP
- Operações async
- Logs em tempo real
"""

import logging
import sys
from datetime import datetime


class VerboseTestViewer:
    """Mostra execução detalhada de cada teste."""

    def __init__(self):
        self.current_test = None
        self.test_start_time = None
        self.indent_level = 0
        self._setup_logging()

    def _setup_logging(self):
        """Configurar logging para capturar tudo."""
        # Handler para console
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)

        # Formatter detalhado
        formatter = logging.Formatter(
            "%(asctime)s | %(name)s | %(levelname)s | %(message)s", datefmt="%H:%M:%S"
        )
        handler.setFormatter(formatter)

        # Registrar handler em logger raiz
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.DEBUG)

    def _indent(self, text: str, level: int | None = None) -> str:
        """Indentar texto."""
        if level is None:
            level = self.indent_level
        return "  " * level + text

    def pytest_runtest_setup(self, item):
        """Antes de cada teste."""
        self.current_test = item.name
        self.test_start_time = datetime.now()
        self.indent_level = 0

        print("\n" + "=" * 80)
        print(f"🧪 INICIANDO TESTE: {item.name}")
        print(f"   📍 Arquivo: {item.fspath}::{item.name}")
        print(f"   ⏰ Horário: {self.test_start_time.strftime('%H:%M:%S')}")
        print("=" * 80)

        self.indent_level = 1

    def pytest_runtest_call(self, item):
        """Durante execução do teste."""
        # Neste ponto, o teste está rodando
        # Logs do teste aparecem com indentação

    def pytest_runtest_teardown(self, item):
        """Após cada teste."""
        if self.test_start_time:
            elapsed = (datetime.now() - self.test_start_time).total_seconds()
            status_emoji = "✅" if item.passed else "❌" if item.failed else "⏭️"

            print("\n" + "-" * 80)
            print(f"{status_emoji} TESTE FINALIZADO: {item.name}")
            print(f"   ⏱️  Duração: {elapsed:.2f}s")
            print(
                f"   📊 Status: {'PASSOU' if item.passed else 'FALHOU' if item.failed else 'PULADO'}"
            )
            print("-" * 80)

        self.indent_level = 0

    def pytest_runtest_makereport(self, item, call):
        """Chamado quando teste termina."""
        if call.when == "call":
            if call.excinfo:
                print(f"\n   🔴 ERRO: {call.excinfo.typename}")
                print(f"   📝 Detalhes: {call.excinfo.value}")


# Registrar o plugin
pytest_plugins = [VerboseTestViewer()]


def pytest_configure(config):
    """Registrar plugin customizado."""
    config.addinivalue_line("markers", "verbose_test: marcar teste para verbose output detalhado")
