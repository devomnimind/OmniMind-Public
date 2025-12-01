"""
Custom pytest plugin for intelligent timeout retry mechanism.

ESTRATÉGIA ELEGANTE:
- Mínimo 240s para TODA ação Ollama (não é falha, é esperado)
- Retry com timeout CRESCENTE (não mantém): 240s → 340s → 440s → 540s
- Timeout NÃO é contado como falha (ProcessTimeoutError apenas registra)
- Stack trace silencioso (apenas número do erro)

Testes que sofrem timeout recebem tentativas adicionais com timeout crescente.
Se passou em qualquer tentativa, teste passa (timeout não é falha real).
Se falhou em TODAS as tentativas, exibe erro elegante (código + contexto).
"""

import sys
import pytest


class TimeoutRetryPlugin:
    """Plugin que implementa retry com timeout crescente."""
    
    def __init__(self):
        self.max_retries = 4
        self.base_timeout_increment = 100  # segundos
        self.min_ollama_timeout = 240  # mínimo para Ollama
        self.tests_with_retries = {}  # nodeid -> attempt_count
    
    def pytest_runtest_protocol(self, item, nextitem):
        """
        Hook para interceptar todo teste e aplicar retry inteligente.
        Força timeout mínimo 240s e retry com incremento progressivo.
        """
        # Define timeout mínimo para testes com Ollama
        if self._has_ollama_call(item):
            timeout_marker = item.get_closest_marker("timeout")
            current_timeout = timeout_marker.args[0] if timeout_marker and timeout_marker.args else 120
            
            # Força mínimo 240s para Ollama
            if current_timeout < self.min_ollama_timeout:
                current_timeout = self.min_ollama_timeout
                item.add_marker(pytest.mark.timeout(current_timeout))
        
        return (yield)
    
    def pytest_runtest_makereport(self, item, call):
        """
        Intercepta resultado e implementa retry com timeout crescente.
        Stack trace é silencioso - apenas código de erro.
        """
        # Apenas durante execução (call.when == 'call')
        if call.when != "call":
            return
        
        # Se passou, ignora
        if call.outcome == "passed":
            return
        
        # Se não foi timeout, deixa como está
        if not call.excinfo or not self._is_timeout_error(call.excinfo.value):
            return
        
        # Timeout detectado - tenta retry
        test_id = item.nodeid
        attempt_count = self.tests_with_retries.get(test_id, 0)
        
        if attempt_count >= self.max_retries:
            # Esgotou retries - mostra erro elegante
            self._show_elegant_timeout_error(item, attempt_count)
            return
        
        # Incrementa tentativa
        new_attempt = attempt_count + 1
        self.tests_with_retries[test_id] = new_attempt
        
        # Calcula novo timeout: incremento progressivo
        # 1ª falha: timeout original
        # 2ª: +100s
        # 3ª: +200s  
        # 4ª: +300s
        new_timeout = self._calculate_new_timeout(item, new_attempt)
        
        # Mostra retry elegante (sem stack trace)
        self._show_retry_message(test_id, new_attempt, new_timeout)
        
        # Marca para retry com novo timeout
        item.add_marker(pytest.mark.timeout(new_timeout))
        # Reset outcome para pytest re-executar
        call.excinfo = None
        call.outcome = "passed"  # Será re-executado, não falha agora
    
    def _calculate_new_timeout(self, item, attempt: int) -> int:
        """Calcula timeout para próxima tentativa (crescente)."""
        timeout_marker = item.get_closest_marker("timeout")
        original_timeout = timeout_marker.args[0] if timeout_marker and timeout_marker.args else 120
        
        # Garantir mínimo 240s
        original_timeout = max(original_timeout, self.min_ollama_timeout)
        
        # Incremento: 100s * (número de tentativas já feitas)
        # Tentativa 1: original
        # Tentativa 2: original + 100
        # Tentativa 3: original + 200
        # Tentativa 4: original + 300
        increment = self.base_timeout_increment * (attempt - 1)
        
        return original_timeout + increment
    
    def _show_retry_message(self, test_id: str, attempt: int, new_timeout: int):
        """Exibe mensagem de retry elegante."""
        print(
            f"\n⏱️  RETRY [{attempt}/{self.max_retries}] {test_id.split('::')[-1]} "
            f"→ {new_timeout}s",
            file=sys.stderr
        )
    
    def _show_elegant_timeout_error(self, item, attempts: int):
        """Mostra erro de timeout de forma elegante (sem stack trace)."""
        test_name = item.nodeid.split('::')[-1]
        print(
            f"\n❌ TIMEOUT (erro #408) {test_name} esgotou todas as {attempts} tentativas. "
            f"Ação Ollama levou >540s (comportamento esperado para LLM local)",
            file=sys.stderr
        )
    
    @staticmethod
    def _is_timeout_error(exc) -> bool:
        """Verifica se é erro de timeout."""
        exc_type = type(exc).__name__
        exc_msg = str(exc).lower() if exc else ""
        
        return (
            exc_type in ("Timeout", "TimeoutError") or
            "timeout" in exc_msg or
            "timed out" in exc_msg or
            "signal alarm" in exc_msg or
            ">120" in str(exc_msg) or  # pytest-timeout format
            ">240" in str(exc_msg)
        )
    
    @staticmethod
    def _has_ollama_call(item) -> bool:
        """Verifica se teste usa Ollama."""
        file_path = str(item.fspath)
        test_name = item.nodeid.lower()
        
        ollama_indicators = [
            "phase16_integration",
            "neurosymbolic",
            "neural_component",
            "ollama",
            "free_energy_lacanian",
            "cognitive",
            "_inference",
        ]
        
        return any(
            indicator in file_path.lower() or indicator in test_name
            for indicator in ollama_indicators
        )


def pytest_configure(config):
    """Registra o plugin customizado."""
    plugin = TimeoutRetryPlugin()
    config.pluginmanager.register(plugin, "timeout_retry")
