"""
Pytest plugin para monitorar e auto-recuperar servidor durante testes.

Se servidor cair durante execução:
1. Detecta queda
2. Registra qual teste derrubou
3. Reinicia servidor automaticamente
4. Testes E2E subsequentes usam servidor novo
"""

import subprocess
import requests
import time
import pytest
import os


class ServerMonitorPlugin:
    """Monitora saúde do servidor durante testes - ESSENCIAL para segurança."""
    
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.server_process = None
        self.server_was_down = False
        self.crashed_tests = []
        self.has_e2e_tests = False
    
    def pytest_configure(self, config):
        """Inicializa monitoring na configuração - LAZY INIT."""
        # NÃO inicia servidor aqui - deixa para pytest_collection_finish
        pass
    
    def pytest_collection_finish(self, session):
        """Após coletar testes: verifica E INICIA servidor se necessário."""
        # Verifica se há testes E2E
        for item in session.items:
            if self._needs_server(item):
                self.has_e2e_tests = True
                break
        
        # Se há E2E tests, GARANTE servidor UP
        if self.has_e2e_tests:
            self._ensure_server_up()
    
    def pytest_runtest_setup(self, item):
        """Antes de cada teste: verifica se servidor está UP."""
        # Apenas para testes que precisam de servidor
        if self._needs_server(item):
            if not self._is_server_healthy():
                print(f"\n⚠️  Servidor DOWN antes de {item.name} - reiniciando...")
                self._start_server()
    
    def pytest_runtest_makereport(self, item, call):
        """Detecta se teste derrubou servidor - SÓ PARA E2E."""
        if call.when == "call" and self._needs_server(item):
            # Verifica se servidor caiu após o teste
            if not self._is_server_healthy():
                self.crashed_tests.append(item.name)
                self.server_was_down = True
                print(f"\n⚠️  Servidor DOWN após {item.name} - reiniciando...")
                self._start_server()
    
    def pytest_runtest_teardown(self, item):
        """Após cada teste: garante servidor UP para próximo."""
        if self._needs_server(item) and self.server_was_down:
            self._wait_for_server_with_retry(max_attempts=15)
    
    def _is_server_healthy(self) -> bool:
        """Verifica se servidor está respondendo."""
        try:
            resp = requests.get(f"{self.backend_url}/health", timeout=2)
            return resp.status_code in (200, 404)
        except Exception:
            return False
    
    def _ensure_server_up(self):
        """Garante servidor UP - verifica antes de iniciar."""
        # Se já está saudável, apenas avisa
        if self._is_server_healthy():
            print("✅ Servidor backend já está rodando em http://localhost:8000")
            return
        
        # Servidor DOWN - inicia
        print("⚠️  Servidor backend DOWN - iniciando...")
        self._start_server()
    
    def _needs_server(self, item) -> bool:
        """Verifica se teste precisa de servidor."""
        # Testes E2E são gerenciados por fixture omnimind_server em tests/e2e/conftest.py
        # ou precisam de servidor explicitamente
        item_path = str(item.fspath).lower()
        test_name = str(item.nodeid).lower()
        
        # Se está em tests/e2e/, deixa fixture do conftest.py gerenciar
        if "tests/e2e/" in item_path or "tests\\e2e\\" in item_path:
            return False
        
        # Testes que explicitamente marcam que precisam de servidor
        e2e_markers = ["e2e", "endpoint", "dashboard", "integration"]
        
        return any(marker in item_path or marker in test_name for marker in e2e_markers)
    
    def _start_server(self):
        """Inicia servidor via docker-compose ou python."""
        print("🚀 Iniciando servidor backend...")
        
        try:
            # Tenta docker-compose primeiro
            deploy_dir = os.path.join(
                os.path.dirname(__file__), "deploy"
            )
            
            if os.path.exists(deploy_dir):
                print(f"   → Tentando docker-compose em {deploy_dir}...")
                subprocess.Popen(
                    ["docker-compose", "up", "-d"],
                    cwd=deploy_dir,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            else:
                # Fallback: python direto
                print("   → Tentando python -m uvicorn...")
                subprocess.Popen(
                    [
                        "python", "-m", "uvicorn",
                        "src.api.main:app",
                        "--host", "0.0.0.0",
                        "--port", "8000"
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            
            # Aguarda servidor ficar saudável com retry agressivo
            self._wait_for_server_with_retry(max_attempts=30)
            print("✅ Servidor backend iniciado com sucesso")
        
        except Exception as e:
            print(f"❌ ERRO ao iniciar servidor: {e}")
            print("⚠️  ATENÇÃO: Testes E2E falharão sem servidor!")
            raise RuntimeError("Servidor backend não conseguiu iniciar")
    
    def _wait_for_server_with_retry(self, max_attempts=30):
        """Aguarda servidor ficar saudável com retry agressivo."""
        for attempt in range(1, max_attempts + 1):
            if self._is_server_healthy():
                print(f"   ✅ Servidor respondendo na tentativa {attempt}")
                return
            
            print(f"   ⏳ Tentativa {attempt}/{max_attempts} para conectar ao servidor...")
            time.sleep(1)
        
        raise RuntimeError(f"Servidor não ficou saudável em {max_attempts} tentativas")
    
    def pytest_sessionfinish(self, session):
        """Ao final: exibe relatório de servidores derrubados."""
        if self.crashed_tests:
            print("\n" + "="*60)
            print("⚠️  TESTES QUE DERRUBARAM O SERVIDOR:")
            for test_name in self.crashed_tests:
                print(f"   - {test_name}")
            print("="*60)


def pytest_configure(config):
    """Registra plugin de monitoramento."""
    config.pluginmanager.register(ServerMonitorPlugin(), "server_monitor")
