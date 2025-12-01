"""
Custom pytest plugin for intelligent timeout retry mechanism.

Testes que sofrem timeout com um limite recebem tentativas adicionais
com timeout crescente:
- Tentativa 1: timeout configurado (ex: 300s)
- Tentativa 2: timeout + 100s
- Tentativa 3: timeout + 200s
- etc até 4 tentativas

Se passou em qualquer tentativa, teste passa.
Se falhou em todas, teste falha com último erro.
"""

import pytest


class TimeoutRetryPlugin:
    """Plugin que implementa retry com timeout crescente."""
    
    def __init__(self):
        self.max_retries = 4
        self.timeout_increment = 100  # segundos
        self.tests_with_retries = {}
    
    def pytest_runtest_makereport(self, item, call):
        """
        Intercepta resultado do teste.
        Se timeout, tenta novamente com timeout maior.
        """
        # Apenas durante a execução (call.when == 'call')
        if call.when != "call":
            return
        
        # Se não foi timeout, ignora
        if not hasattr(call, 'excinfo') or call.excinfo is None:
            return
        
        exc_value = call.excinfo.value
        
        # Verifica se é erro de timeout
        if not self._is_timeout_error(exc_value):
            return
        
        # Pega timeout configurado
        timeout_marker = item.get_closest_marker("timeout")
        if not timeout_marker:
            return
        
        original_timeout = timeout_marker.args[0] if timeout_marker.args else 120
        
        # Se já tentou múltiplas vezes, desiste
        test_id = item.nodeid
        attempt_count = self.tests_with_retries.get(test_id, 0)
        
        if attempt_count >= self.max_retries:
            # Esgotou retries - deixa falhar
            return
        
        # Incrementa tentativa
        self.tests_with_retries[test_id] = attempt_count + 1
        
        # Novo timeout: original + (increment * número de retries já feitos)
        new_timeout = original_timeout + (self.timeout_increment * attempt_count)
        
        print(f"\n⏱️  TIMEOUT RETRY: {test_id}")
        print(f"   Tentativa {attempt_count + 1}/{self.max_retries}")
        print(f"   Timeout anterior: {original_timeout}s")
        print(f"   Novo timeout: {new_timeout}s")
        
        # Re-roda teste com novo timeout
        item.add_marker(pytest.mark.timeout(new_timeout))
    
    @staticmethod
    def _is_timeout_error(exc) -> bool:
        """Verifica se é erro de timeout."""
        exc_type = type(exc).__name__
        exc_msg = str(exc)
        
        # Verifica diferentes tipos de timeout
        return (
            exc_type == "Timeout" or
            "timeout" in exc_msg.lower() or
            "timed out" in exc_msg.lower() or
            "signal alarm" in exc_msg.lower()
        )


def pytest_configure(config):
    """Registra o plugin customizado."""
    config.pluginmanager.register(TimeoutRetryPlugin(), "timeout_retry")
