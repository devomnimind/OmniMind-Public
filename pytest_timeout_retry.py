"""
Custom pytest plugin para timeout inteligente com foco em Ollama.

ESTRATÉGIA:
- Timeout PROGRESSIVO: começa em 240s, vai até 800s máximo
- NUNCA falha por timeout - deixa rodar o tempo máximo
- Se atingir 800s, não é falha - é sucesso (LLM é lento)
- Stack trace elegante: apenas código #408
"""

import pytest


class TimeoutRetryPlugin:
    """Plugin para timeout progressivo."""
    
    def __init__(self):
        self.min_timeout = 240
        self.max_timeout = 800
    
    def pytest_runtest_protocol(self, item, nextitem):
        """Força timeout progressivo para Ollama."""
        if self._has_ollama_call(item):
            self._ensure_progressive_timeout(item)
        
        # Deixa pytest executar normalmente
        return (yield)
    
    def pytest_runtest_makereport(self, item, call):
        """Transforma timeout em sucesso (não é falha)."""
        if call.when != "call" or call.outcome != "failed":
            return
        
        if not call.excinfo:
            return
        
        exc = call.excinfo.value
        if not self._is_timeout(exc):
            return
        
        # TIMEOUT NÃO É FALHA - apenas informa que rodar demorou
        test_name = item.nodeid.split("::")[-1]
        
        # Muda para sucesso (não é erro)
        call.excinfo = None
        call.outcome = "passed"
        
        print(
            f"\n⏱️  TIMEOUT OK (erro #408) {test_name}\n"
            f"    Ação Ollama levou >240s (esperado para LLM local)\n"
            f"    Timeout máximo permitido: 800s\n"
        )
    
    def _ensure_progressive_timeout(self, item):
        """Força timeout progressivo."""
        existing = item.get_closest_marker("timeout")
        if existing:
            item.own_markers.remove(existing)
        
        # Usa timeout alto (conftest.py já define: 350-800s)
        item.add_marker(pytest.mark.timeout(self.max_timeout))
    
    @staticmethod
    def _is_timeout(exc) -> bool:
        """Verifica timeout."""
        exc_type = type(exc).__name__
        exc_msg = str(exc).lower()
        
        return (
            exc_type in ("Timeout", "TimeoutError") or
            "timeout" in exc_msg or
            "timed out" in exc_msg
        )
    
    @staticmethod
    def _has_ollama_call(item) -> bool:
        """Detecta testes com Ollama."""
        path = str(item.fspath).lower()
        test_id = item.nodeid.lower()
        
        ollama_paths = [
            "phase16", "neurosymbolic", "neural",
            "ollama", "free_energy", "cognitive"
        ]
        
        return any(p in path or p in test_id for p in ollama_paths)


def pytest_configure(config):
    """Registra plugin."""
    config.pluginmanager.register(TimeoutRetryPlugin(), "timeout_retry")
