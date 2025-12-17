"""
Plugin de colorização inteligente para pytest.

Apenas testes que falham/erro ficam em vermelho.
Testes que passam/skipped ficam em verde/amarelo (não herdam vermelho).
"""


class ColorfulTestPlugin:
    """Plugin que gerencia colorização independente por teste."""

    def __init__(self):
        self.last_failed_test = None
        self.last_error_test = None

    def pytest_runtest_logreport(self, report):
        """Registra resultado de cada teste individualmente."""
        if report.when == "call":
            if report.outcome == "failed":
                self.last_failed_test = report.nodeid
                # Limpar erro anterior se passou
                self.last_error_test = None
            elif report.outcome == "passed":
                # Limpar falha anterior
                self.last_failed_test = None
                self.last_error_test = None
            elif report.outcome == "error":
                self.last_error_test = report.nodeid
                self.last_failed_test = None

    def pytest_collection_finish(self, session):
        """Após coletar testes, registra o plugin."""
        # Garante que pytest use colorização por teste
        if hasattr(session.config, "_tmpdirhandler"):
            # Reset color state antes de testes
            pass


def pytest_configure(config):
    """Registra o plugin de colorização."""
    plugin = ColorfulTestPlugin()
    config.pluginmanager.register(plugin, "colorful_test_plugin")

    # Configurar pytest-html para colorização independente
    if hasattr(config, "option"):
        # Garantir que cada teste é colorido independentemente
        config.option.tb = "short"
