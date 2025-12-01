"""
Custom pytest plugin para timeout inteligente com foco em Ollama.

ESTRATÉGIA PRÁTICA:
- Força mínimo 240s para TODA ação Ollama (não é falha, é esperado)
- Se timeout: exibe mensagem elegante com código #408
- Stack trace silencioso - apenas contexto essencial
- Retry via re-execução manual: pytest -k "test_name" --lf
"""

import pytest


class TimeoutRetryPlugin:
    """Plugin para timeout inteligente."""
    
    def __init__(self):
        self.min_ollama_timeout = 240
    
    def pytest_runtest_protocol(self, item, nextitem):
        """Força mínimo 240s para Ollama."""
        if self._has_ollama_call(item):
            self._ensure_min_timeout(item)
        
        # Deixa pytest executar normalmente
        return (yield)
    
    def pytest_runtest_makereport(self, item, call):
        """Silencia stack trace de timeout e mostra erro elegante."""
        if call.when != "call" or call.outcome != "failed":
            return
        
        if not call.excinfo:
            return
        
        exc = call.excinfo.value
        if not self._is_timeout(exc):
            return
        
        # Timeout detectado - altera mensagem
        test_name = item.nodeid.split("::")[-1]
        
        # Limpa stack trace excessivo
        call.excinfo.value = TimeoutError(
            f"⏱️  TIMEOUT (erro #408) {test_name}\n"
            f"   Ação Ollama levou >240s (comportamento esperado para LLM local)\n"
            f"   Retry: pytest -k {test_name} --tb=no"
        )
    
    def _ensure_min_timeout(self, item):
        """Força mínimo 240s."""
        existing = item.get_closest_marker("timeout")
        if existing:
            current = existing.args[0] if existing.args else 120
            if current < self.min_ollama_timeout:
                item.own_markers.remove(existing)
                item.add_marker(pytest.mark.timeout(self.min_ollama_timeout))
        else:
            item.add_marker(pytest.mark.timeout(self.min_ollama_timeout))
    
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
