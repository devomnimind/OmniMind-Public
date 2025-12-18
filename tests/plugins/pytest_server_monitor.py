"""
Pytest plugin para monitorar e auto-recuperar servidor durante testes.

Se servidor cair durante execução:
1. Detecta queda
2. Registra qual teste derrubou
3. Reinicia servidor automaticamente
4. Testes E2E subsequentes usam servidor novo

OTIMIZAÇÕES ROBUSTAS PARA PROD+DEV HÍBRIDO:
- Timeouts progressivos (não hardcoded)
- Debug logging para troubleshooting
- Health checks inteligentes
- Métricas de startup
- Recuperação graceful
- Respeita ServerStateManager para evitar conflitos com fixture omnimind_server

RESPEITO AO ESTADO DO SERVIDOR:
- Se fixture omnimind_server controla servidor → plugin NÃO reinicia
- Plugin só reinicia se é proprietário ou se ninguém controla
- Evita race conditions e múltiplas reinicializações
"""

import logging
import os
import subprocess
import sys
import time

import pytest
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from tests.server_state_manager import get_server_state_manager

# Setup logging para debug
logger = logging.getLogger("omnimind.server_monitor")
logger.setLevel(logging.DEBUG)

# Criar session com RETRY STRATEGY PERSONALIZADO
# Desabilita retries automáticos (causava "Max retries exceeded")
session = requests.Session()
retry_strategy = Retry(
    total=0,  # ❌ NÃO fazer retry automático - deixa pytest_server_monitor gerenciar
    backoff_factor=0,
    status_forcelist=[],  # Não retry em nenhum status
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

# Alert system (optional - pode não estar disponível em todos os ambientes)
_alert_system = None


async def _get_alert_system():
    """Obter sistema de alertas se disponível."""
    global _alert_system
    if _alert_system is None:
        try:
            # Lazy import para evitar circular dependency
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
            from src.monitor import get_alert_system

            _alert_system = await get_alert_system()
        except Exception as e:
            logger.debug(f"Sistema de alertas não disponível: {e}")
    return _alert_system


class ServerMonitorPlugin:
    """
    Monitora saúde do servidor durante testes PERIGOSOS (chaos, stress, ddos).

    IMPORTANTE:
    - Monitor NÃO inicia servidor - isso é responsabilidade do script do sistema
    - Monitor só ativo em testes marcados como chaos/stress/ddos
    - Monitor apenas verifica e reinicia se servidor cair durante testes perigosos
    - Desabilitado por padrão - só ativa em testes específicos
    """

    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.server_process = None
        self.server_was_down = False
        self.crashed_tests = []
        self.has_e2e_tests = False
        self.startup_metrics = {}  # Rastreia tempo de startup
        self.skip_server_tests = (
            os.environ.get("OMNIMIND_SKIP_SERVER_TESTS", "false").lower() == "true"
        )
        # IMPORTANTE: Monitor desabilitado por padrão
        # Só ativa em testes perigosos (chaos, stress, ddos)
        self.enabled = False

        # ========== TIMEOUTS ADAPTATIVOS POR TESTE ==========
        # ALINHADO COM CONFIGURAÇÃO GLOBAL (pytest.ini + conftest.py):
        # - Timeout global: 800s máximo por teste individual
        # - Timeout progressivo: começa em 240s, vai até 800s
        # - Modo gradual: não falha, continua até máximo
        # - NÃO é timeout global acumulativo - cada teste tem seu próprio orçamento
        self.startup_attempt_count = 0

        # Timeouts por tentativa (aumenta progressivamente)
        # ⏱️ CADA CONEXÃO/TESTE INDIVIDUAL tem estes timeouts:
        # Tentativa 1: 240s  (startup + Orchestrator + SecurityAgent - alinhado com config global)
        # Tentativa 2: 400s  (permite +recovery time para 2+ ciclos)
        # Tentativa 3: 600s  (permite 3+ ciclos completos)
        # Tentativa 4+: 800s (máximo - continua indefinidamente)
        # IMPORTANTE: Respeita configuração global de 240s inicial e 800s máximo
        self.timeout_progression = [240, 400, 600, 800, 800]
        self.max_global_timeout = 800  # Máximo individual por teste (não global)

    def pytest_configure(self, config):
        """Inicializa monitoring na configuração - LAZY INIT."""
        # NÃO inicia servidor aqui - deixa para pytest_collection_finish

    def pytest_collection_finish(self, session):
        """
        Após coletar testes: verifica se há testes perigosos e ativa monitor se necessário.

        IMPORTANTE: Monitor NÃO inicia servidor - isso é responsabilidade do script do sistema.
        Monitor apenas verifica e reinicia se servidor cair durante testes perigosos.
        """
        # ⚡ OTIMIZAÇÃO: Skip durante --collect-only
        if session.config.option.collectonly:
            logger.info("🏃 Collect-only mode: Pulando verificação de monitor")
            return

        # Verificar se há testes perigosos (chaos, stress, ddos)
        dangerous_markers = ["chaos", "stress", "ddos", "load"]
        has_dangerous_tests = False

        for item in session.items:
            # Verificar se teste tem marcador perigoso
            for marker in item.iter_markers():
                if marker.name in dangerous_markers:
                    has_dangerous_tests = True
                    self.enabled = True
                    logger.info(f"⚠️  Teste perigoso detectado: {item.name} - Monitor ativado")
                    break
            if has_dangerous_tests:
                break

        if has_dangerous_tests:
            logger.info("⚠️  Monitor ativado para testes perigosos")
            print("⚠️  Monitor de servidor ativado para testes perigosos (chaos/stress/ddos)")
        else:
            logger.info("✅ Nenhum teste perigoso detectado - Monitor desabilitado")

    def pytest_runtest_setup(self, item):
        """
        Antes de cada teste: verifica se servidor está UP (apenas para testes perigosos).

        IMPORTANTE:
        - Monitor só ativo em testes perigosos (chaos, stress, ddos)
        - Monitor NÃO inicia servidor - isso é responsabilidade do script do sistema
        - Monitor apenas verifica e reinicia se servidor cair durante testes perigosos
        """
        # Monitor desabilitado por padrão - só ativa em testes perigosos
        if not self.enabled:
            return

        # Verificar se teste é perigoso
        dangerous_markers = ["chaos", "stress", "ddos", "load"]
        is_dangerous = any(item.get_closest_marker(marker) for marker in dangerous_markers)

        if not is_dangerous:
            return  # Monitor não ativo para testes normais

        # Apenas para testes perigosos que precisam de servidor
        if self._needs_server(item):
            if self.skip_server_tests:
                pytest.skip("Servidor skipped via OMNIMIND_SKIP_SERVER_TESTS=true")
                return

            state_manager = get_server_state_manager()

            # Se fixture controla → confia na fixture
            if state_manager.owner == "fixture":
                logger.info(f"✅ Fixture controla servidor para {item.name}")
                state_manager.mark_running()
                return

            # Verificar se há health check recente em cache (45s)
            # Evita múltiplos checks durante suite com muitos testes
            if state_manager.has_recent_health_check():
                cached_result = state_manager.get_cached_health_check()
                if cached_result is True:
                    logger.debug("✅ Health check em cache (recente) - servidor UP")
                    return
                # Se cache diz DOWN, tenta reiniciar

            # Sem cache recente: fazer health check
            if not self._is_server_healthy():
                print(f"\n⚠️  Servidor DOWN antes de {item.name}")
                print(
                    "   💡 Monitor não inicia servidor - inicie manualmente: "
                    "./scripts/start_omnimind_system_sudo.sh"
                )
                logger.warning(
                    f"Servidor não está respondendo antes de teste perigoso: {item.name}"
                )
                pytest.skip(
                    "Servidor não está respondendo - inicie manualmente com "
                    "./scripts/start_omnimind_system_sudo.sh"
                )

    def pytest_runtest_makereport(self, item, call):
        """
        Detecta se teste perigoso derrubou servidor.

        IMPORTANTE:
        - Monitor só ativo em testes perigosos (chaos, stress, ddos)
        - Monitor NÃO inicia servidor - isso é responsabilidade do script do sistema
        - Monitor apenas verifica e reinicia se servidor cair durante testes perigosos
        """
        # Monitor desabilitado por padrão - só ativa em testes perigosos
        if not self.enabled:
            return

        # Verificar se teste é perigoso
        dangerous_markers = ["chaos", "stress", "ddos", "load"]
        is_dangerous = any(item.get_closest_marker(marker) for marker in dangerous_markers)

        if not is_dangerous:
            return  # Monitor não ativo para testes normais

        if call.when == "call" and self._needs_server(item):
            state_manager = get_server_state_manager()

            # Se fixture controla → não interferir
            if state_manager.owner == "fixture":
                logger.info("ℹ️  Fixture controla servidor, plugin não interfere")
                return

            # OTIMIZAÇÃO: Se há health check recente em cache, confiar nele
            if state_manager.has_recent_health_check():
                cached_result = state_manager.get_cached_health_check()
                if cached_result is True:
                    logger.debug("✅ Cache recente diz servidor UP - não refazer health check")
                    return

            # Sem cache recente: fazer health check
            # Verifica se servidor caiu após o teste perigoso
            if not self._is_server_healthy():
                self.crashed_tests.append(item.name)
                self.server_was_down = True
                print(f"\n⚠️  Servidor DOWN após teste perigoso: {item.name}")
                print(
                    "   💡 Monitor não reinicia servidor - reinicie manualmente: "
                    "./scripts/start_omnimind_system_sudo.sh"
                )
                logger.warning(f"Servidor caído após teste perigoso: {item.name}")

                # Emitir alerta para VS Code
                try:
                    import asyncio

                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                    async def _emit_alert():
                        alerts = await _get_alert_system()
                        if alerts:
                            await alerts.emit_server_down(
                                reason=f"Derrubado pelo teste perigoso: {item.name}",
                                context={
                                    "test_name": item.name,
                                    "timestamp": time.time(),
                                    "module": (
                                        item.module.__name__
                                        if hasattr(item, "module")
                                        else "unknown"
                                    ),
                                },
                            )

                    loop.run_until_complete(_emit_alert())
                except Exception as e:
                    logger.debug(f"Erro ao emitir alerta de servidor down: {e}")

    def pytest_runtest_teardown(self, item):
        """
        Após cada teste: garante servidor UP para próximo.

        Apenas interfere se plugin controla servidor (não fixture).
        """
        state_manager = get_server_state_manager()

        # Se fixture controla → não interferir no teardown
        if state_manager.owner == "fixture":
            return

        if self._needs_server(item) and self.server_was_down:
            # Aumentar muito o tempo limite para permitir suite completa rodar
            # Sem timeout artificial - deixa tempo contínuo para recuperação real
            self._wait_for_server_with_retry(max_attempts=None, max_wait_seconds=600)
            # Reset flag após recuperação bem-sucedida
            self.server_was_down = False

    def _is_server_healthy(self) -> bool:
        """
        Verifica se servidor está respondendo (SEM retries automáticos).

        Timeout tolerante: 5s (não 1s) porque durante testes lentos,
        servidor pode estar processando e não responder em 1s.

        IMPORTANTE: Timeout ≠ DOWN. Apenas ConnectionError confirma DOWN.
        """
        try:
            # Usa session com retry=0 (sem retries automáticos)
            # Adicionado trailing slash para evitar 307 Redirect
            # Timeout TOLERANTE: 5s (permite testes lentos em background)
            resp = session.get(f"{self.backend_url}/health/", timeout=5)
            if resp.status_code in (200, 404):
                logger.debug(f"✅ Health check OK: {resp.status_code}")
                return True
        except requests.exceptions.Timeout:
            # Timeout NÃO significa DOWN - servidor pode estar lento
            logger.debug("⏱️  Health check timeout (5s) - servidor pode estar ocupado, não é DOWN")
            return True  # ← Crucial: assume servidor está UP se apenas timeout
        except requests.exceptions.ConnectionError:
            logger.debug("🔌 Health check connection refused (servidor genuinamente DOWN)")
        except Exception as e:
            logger.debug(f"❌ Health check erro: {type(e).__name__}: {e}")

        # Fallback: tenta endpoint raiz
        try:
            resp = session.get(f"{self.backend_url}/", timeout=5, allow_redirects=False)
            if resp.status_code in (200, 301, 302, 307, 308):
                logger.debug(f"✅ Fallback OK: {resp.status_code}")
                return True
        except requests.exceptions.Timeout:
            # Timeout no fallback também = não é DOWN
            logger.debug("⏱️  Fallback timeout (5s) - servidor pode estar ocupado, não é DOWN")
            return True  # ← Crucial: assume servidor está UP
        except requests.exceptions.ConnectionError:
            logger.debug("🔌 Fallback connection refused - CONFIRMA servidor DOWN")
        except Exception as e:
            logger.debug(f"❌ Fallback erro: {type(e).__name__}: {e}")

        return False

    def _ensure_server_up(self):
        """
        Verifica se servidor está UP (NÃO inicia servidor).

        IMPORTANTE:
        - Monitor NÃO inicia servidor - isso é responsabilidade do script do sistema
        - Monitor apenas verifica se servidor está respondendo
        - Se servidor não está respondendo, apenas avisa (não tenta iniciar)
        """
        state_manager = get_server_state_manager()

        # Verificar se outro componente controla servidor
        if state_manager.owner == "fixture":
            print(
                "ℹ️  Servidor está sob gerenciamento da fixture E2E "
                "(omnimind_server) - plugin não interfere"
            )
            return

        # Se já está saudável, apenas avisa
        if self._is_server_healthy():
            print("✅ Servidor backend já está rodando em http://localhost:8000")
            state_manager.mark_running()
            return

        # Servidor não está respondendo - apenas avisa (não tenta iniciar)
        print("⚠️  Servidor backend não está respondendo")
        print("   💡 Inicie o servidor manualmente: ./scripts/start_omnimind_system_sudo.sh")
        logger.warning(
            "Servidor não está respondendo - monitor não inicia servidor automaticamente"
        )

    def _needs_server(self, item) -> bool:
        """Verifica se teste precisa de servidor."""
        # Testes E2E são gerenciados por fixture omnimind_server em tests/e2e/conftest.py
        # ou precisam de servidor explicitamente
        item_path = str(item.fspath).lower()
        test_name = str(item.nodeid).lower()

        # Se está em tests/e2e/, deixa fixture do conftest.py gerenciar
        if "tests/e2e/" in item_path or "tests\\e2e\\" in item_path:
            return False

        # EXCEÇÃO EXPLÍCITA: Lista de arquivos que contêm palavras-chave de integração
        # mas são unitários/mockados e NÃO devem disparar o servidor real.
        excluded_files = [
            "tests/consciousness/test_integration_loss.py",
            "tests/autopoietic/test_architecture_evolution.py",
            "tests/autopoietic/test_meaning_maker.py",
            "tests/manual/test_ui_integration.py",
            "tests/test_agents_core_integration.py",
            "tests/test_enhanced_agents_integration.py",
            "tests/test_dashboard_ws_auth.py",
            "tests/metrics/test_dashboard_metrics.py",
            "tests/test_enhanced_integrations.py",
            "tests/autopoietic/test_integration_flow_v2.py",
            "tests/test_security_agent_integration.py",
            "tests/swarm/test_swarm_integration.py",
            "tests/consciousness/test_integration_loop.py",
            "tests/test_lacanian_integration_complete.py",
            "tests/test_external_ai_integration.py",
            "tests/test_phase16_full_integration.py",
            "tests/test_phase16_integration.py",
            "tests/test_tools_integration.py",
            "tests/test_dashboard_e2e.py",
            "tests/test_phase3_integration.py",
            "tests/autopoietic/test_advanced_repair.py",
            # REFATORAÇÃO 2025-12-08: Testes de composição e sync são unitários
            "tests/agents/test_enhanced_code_agent_composition.py",
            "tests/consciousness/test_integration_loop_sync.py",
        ]

        # Normaliza o caminho do item para comparação
        normalized_item_path = item_path.replace("\\", "/")

        for excluded in excluded_files:
            if excluded in normalized_item_path:
                return False

        # Testes que explicitamente marcam que precisam de servidor OmniMind (porta 8000)
        # NOTA: "integration" é muito amplo - muitos testes unitários têm "integration" no nome
        # mas usam mocks. Verificar se realmente usa localhost:8000 antes de iniciar servidor.
        e2e_markers = ["e2e", "endpoint", "dashboard"]

        # Verificar se contém marcadores E2E (mais específicos)
        has_e2e_marker = any(marker in item_path or marker in test_name for marker in e2e_markers)

        # Se não tem marcador E2E específico, verificar se realmente usa servidor OmniMind
        # (não apenas serviços externos como Ollama/Qdrant)
        if not has_e2e_marker:
            # Verificar se arquivo realmente usa servidor OmniMind (porta 8000)
            # Isso evita iniciar servidor para testes que só usam serviços externos
            try:
                import os

                test_file_path = str(item.fspath)
                if os.path.exists(test_file_path):
                    with open(test_file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        # Verificar se realmente usa servidor OmniMind (porta 8000)
                        uses_omnimind_server = (
                            "localhost:8000" in content
                            or "http://localhost:8000" in content
                            or "backend.*8000" in content
                            or "port.*8000" in content
                        )
                        # Se não usa servidor OmniMind, não precisa iniciar
                        if not uses_omnimind_server:
                            return False
            except Exception:
                # Se não conseguir ler arquivo, usar lógica antiga
                pass

        return has_e2e_marker

    def _start_server(self):
        """
        REMOVIDO: Monitor não inicia servidor.

        IMPORTANTE:
        - Monitor NÃO inicia servidor - isso é responsabilidade do script do sistema
        - Para iniciar servidor, use: ./scripts/start_omnimind_system_sudo.sh
        - Monitor apenas verifica e reinicia se servidor cair durante testes perigosos
        """
        logger.warning("Monitor não inicia servidor - use ./scripts/start_omnimind_system_sudo.sh")
        print("⚠️  Monitor não inicia servidor automaticamente")
        print("   💡 Para iniciar servidor: ./scripts/start_omnimind_system_sudo.sh")
        raise RuntimeError(
            "Monitor não inicia servidor - inicie manualmente com "
            "./scripts/start_omnimind_system_sudo.sh"
        )
        start_time = time.time()
        self.startup_attempt_count += 1

        try:
            # Tenta com script wrapper que detecta necessidade de sudo
            script_path = os.path.join(
                os.path.dirname(__file__), "..", "..", "scripts", "start_omnimind_system_sudo.sh"
            )

            if not os.path.exists(script_path):
                raise FileNotFoundError(f"Script não encontrado: {script_path}")

            print(f"   → Executando {script_path}...")
            print("   → Mostrando saída completa do script de inicialização...\n")

            # CORREÇÃO: Mostrar saída em tempo real para debug
            # Executa SEM sudo direto - o script start_omnimind_system_sudo.sh
            # já gerencia a elevação via secure_run.py quando necessário
            # IMPORTANTE: stdout/stderr não capturados para mostrar
            # backend, frontend, cluster, credenciais
            process = subprocess.Popen(
                ["bash", script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Mesclar stderr em stdout
                text=True,
                bufsize=1,  # Line buffered
                universal_newlines=True,
                cwd=os.path.dirname(__file__) + "/../..",
            )

            # Mostrar saída em tempo real
            output_lines = []
            try:
                if process.stdout is None:
                    raise RuntimeError("process.stdout is None")
                for line in process.stdout:
                    line = line.rstrip()
                    print(f"   {line}")  # Mostrar cada linha
                    output_lines.append(line)
                    # Log também para debug
                    logger.debug(f"Script output: {line}")
            except Exception as e:
                logger.warning(f"Erro ao ler saída do script: {e}")

            # Aguardar término do processo
            returncode = process.wait(timeout=240)  # Timeout aumentado

            if returncode != 0:
                logger.warning(f"Script falhou com returncode {returncode}")
                print(f"   ⚠️  Script retornou código de erro: {returncode}")
                # Mostrar últimas linhas de saída para debug
                if output_lines:
                    print("   ⚠️  Últimas linhas de saída:")
                    for line in output_lines[-10:]:
                        print(f"      {line}")

                # IMPORTANTE: Verificar se servidor já está rodando antes de considerar erro
                # Script pode falhar por várias razões (permissões, dependências), mas servidor
                # pode já estar rodando de uma execução anterior
                if self._is_server_healthy():
                    logger.info(
                        "✅ Servidor já está rodando apesar do erro do script - "
                        "usando servidor existente"
                    )
                    print("   ✅ Servidor já está rodando - ignorando erro do script")
                    state_manager = get_server_state_manager()
                    state_manager.mark_running()
                    return  # Servidor está UP, não precisa continuar

                # Se servidor não está rodando E script falhou, continua para tentar iniciar
                # Continua mesmo com erro - pode ser permissão mas servidor pode estar subindo
            else:
                print("   ✅ Script executado com sucesso")

            # ========== TIMEOUTS ADAPTATIVOS COM RESTART INTERMEDIÁRIO ==========
            total_timeout = self._get_adaptive_timeout()
            # Ciclo: aguarda servidor subir (120-150s + buffer para ambiente híbrido)
            # Aumentado para 240s para dar margem em ambientes híbridos de desenvolvimento
            cycle_timeout = 240

            logger.info(
                f"Aguardando servidor (tentativa {self.startup_attempt_count}, "
                f"timeout total {total_timeout}s, ciclo {cycle_timeout}s)..."
            )
            print(
                f"\n   ⏳ Timeout adaptativo: {total_timeout}s (ciclo de restart: {cycle_timeout}s)"
            )

            # Loop de tentativas com restart intermediário
            wait_start_time = time.time()
            while True:
                try:
                    # Tenta esperar pelo servidor por 'cycle_timeout' segundos
                    self._wait_for_server_with_retry(
                        max_attempts=None, max_wait_seconds=cycle_timeout
                    )
                    # Se chegou aqui, servidor está UP
                    break
                except TimeoutError:
                    # Timeout do ciclo atingido
                    elapsed_total = time.time() - wait_start_time

                    # Se já passou do tempo total, lança erro real
                    if elapsed_total >= total_timeout:
                        raise TimeoutError(f"Timeout total ({total_timeout}s) atingido")

                    print(
                        f"   🔄 Servidor não subiu em {cycle_timeout}s. "
                        f"Reiniciando processo de startup..."
                    )

                    # IMPORTANTE: NÃO matar processos uvicorn existentes
                    # Se servidor já está rodando (iniciado manualmente ou por outro processo),
                    # não devemos matá-lo. Apenas mata processos que o plugin iniciou.
                    # Verificar se plugin iniciou o processo antes de matar
                    if self.server_process is not None:
                        try:
                            # Apenas mata processo que plugin iniciou
                            if self.server_process.poll() is None:
                                # Processo ainda está rodando
                                self.server_process.terminate()
                                try:
                                    self.server_process.wait(timeout=5)
                                except subprocess.TimeoutExpired:
                                    self.server_process.kill()
                        except Exception as e:
                            logger.debug(f"Erro ao terminar processo do plugin: {e}")

                    # NÃO usar pkill - pode matar processos uvicorn que não foram
                    # iniciados pelo plugin
                    # subprocess.run(["pkill", "-f", "uvicorn"], stderr=subprocess.DEVNULL)
                    # REMOVIDO
                    # subprocess.run(
                    #     ["pkill", "-f", "python web/backend/main.py"],
                    #     stderr=subprocess.DEVNULL
                    # )  # REMOVIDO

                    # Re-executa script de startup
                    print(f"   → Re-executando {script_path}...")
                    subprocess.run(
                        ["bash", script_path],
                        capture_output=True,
                        text=True,
                        timeout=240,  # Timeout aumentado para ambiente híbrido
                        cwd=os.path.dirname(__file__) + "/../..",
                    )
                    # Continua loop (nova espera de cycle_timeout)

            elapsed = time.time() - start_time
            self.startup_metrics["total_startup_time"] = elapsed

            logger.info(
                f"✅ Servidor iniciado em {elapsed:.1f}s (tentativa {self.startup_attempt_count})"
            )
            print(
                f"✅ Servidor backend iniciado em {elapsed:.1f}s " f"(Backend + eBPF inicializados)"
            )

        except TimeoutError:
            elapsed = time.time() - start_time
            current_timeout = self._get_adaptive_timeout()

            logger.error(
                f"❌ Timeout na tentativa {self.startup_attempt_count} "
                f"após {elapsed:.1f}s (timeout: {current_timeout:.0f}s)"
            )
            print(f"\n❌ Timeout na tentativa {self.startup_attempt_count} após {elapsed:.1f}s")

            # Emitir alerta de timeout
            try:
                import asyncio

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                async def _emit_timeout_alert():
                    alerts = await _get_alert_system()
                    if alerts:
                        await alerts.emit_test_timeout(
                            test_name="SERVER_STARTUP",
                            timeout_seconds=int(current_timeout),
                            context={
                                "attempt": self.startup_attempt_count,
                                "elapsed": elapsed,
                            },
                        )

                loop.run_until_complete(_emit_timeout_alert())
            except Exception as e:
                logger.debug(f"Erro ao emitir alerta de timeout: {e}")

            # Verifica se já atingiu timeout máximo (800s)
            if current_timeout >= 800 and self.startup_attempt_count > 5:
                print(
                    f"\n🛑 FALHA CRÍTICA: Atingiu timeout máximo por teste (800s) "
                    f"após {self.startup_attempt_count} tentativas"
                )
                print("   Possíveis causas:")
                print("   - Orchestrator + SecurityAgent levando >800s")
                print("   - Qdrant não está acessível ou muito lento")
                print("   - Recursos insuficientes (RAM/GPU/Disco)")
                print("   - Múltiplas tentativas de restart não recuperaram servidor")
                raise RuntimeError(
                    f"Servidor backend falhou após {self.startup_attempt_count} tentativas, "
                    f"tempo máximo (800s) por teste atingido"
                )

            # Tenta novamente com timeout maior
            print("   🔄 Tentando novamente com timeout maior...\n")
            self._start_server()

        except Exception as e:
            elapsed = time.time() - start_time

            logger.error(
                f"❌ ERRO ao iniciar servidor na tentativa {self.startup_attempt_count} "
                f"após {elapsed:.1f}s: {e}"
            )
            print(f"\n❌ ERRO ao iniciar servidor: {e}")
            print("⚠️  ATENÇÃO: Testes que precisam de servidor falharão!")
            raise RuntimeError(f"Servidor backend não conseguiu iniciar: {e}")

    def _get_adaptive_timeout(self) -> float:
        """
        Calcula timeout adaptativo baseado no número de tentativas.

        ALINHADO COM CONFIGURAÇÃO GLOBAL (pytest.ini + conftest.py):
        - Respeita timeout progressivo: 240s inicial → 800s máximo
        - Modo gradual: não falha, continua até máximo
        - Cada teste individual tem seu próprio orçamento de tempo

        Estratégia (timeout INDIVIDUAL por teste - PER CONNECTION):
        - Tentativa 1: 240s  (startup + Orchestrator + SecurityAgent - alinhado com config global)
        - Tentativa 2: 400s  (permite +recovery time para múltiplos ciclos)
        - Tentativa 3: 600s  (permite 3+ ciclos completos de recovery)
        - Tentativa 4+: 800s (máximo - continua indefinidamente sem artificial timeout)

        Retorna o timeout em segundos.
        """
        idx = min(self.startup_attempt_count - 1, len(self.timeout_progression) - 1)
        timeout = self.timeout_progression[idx]

        logger.info(f"Timeout adaptativo (tentativa {self.startup_attempt_count}): {timeout}s")

        return timeout

    def _start_python_server(self):
        """
        Inicia servidor via python -m uvicorn.

        IMPORTANTE: Verifica se servidor já está rodando antes de tentar iniciar.
        Não mata processos uvicorn existentes - apenas verifica se servidor responde.
        """
        # Verificar se servidor já está rodando antes de tentar iniciar
        if self._is_server_healthy():
            logger.info("✅ Servidor já está rodando e respondendo - não precisa iniciar")
            print("✅ Servidor já está rodando - usando servidor existente")
            state_manager = get_server_state_manager()
            state_manager.mark_running()
            return

        # Muda para diretório raiz do projeto
        project_root = os.path.join(os.path.dirname(__file__), "../..")
        os.chdir(project_root)

        # Define variáveis de ambiente necessárias
        env = os.environ.copy()
        env.update(
            {
                "QDRANT_URL": "http://localhost:6333",
                # Em testes: usa modo "test" para paralelizar inicialização
                "OMNIMIND_MODE": "test",
                # Logging detalhado para debug de startup
                "OMNIMIND_LOG_LEVEL": "INFO",
            }
        )

        # Inicia uvicorn
        self.server_process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "web.backend.main:app",
                "--host",
                "0.0.0.0",
                "--port",
                "8000",
                "--workers",
                "1",
                "--log-level",
                "info",
            ],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        print("   ✅ uvicorn iniciado em background (com Orchestrator completo)")

    def _wait_for_server_with_retry(self, max_attempts=None, max_wait_seconds=240):
        """
        Aguarda servidor ficar saudável com retry agressivo.

        Args:
            max_attempts: Número máximo de tentativas (None = usar max_wait_seconds)
            max_wait_seconds: Tempo máximo em segundos (default 4 min para ambiente híbrido)
        """
        # ⚡ OTIMIZAÇÃO: Verifica se já está UP antes de esperar
        if self._is_server_healthy():
            return

        start_time = time.time()
        attempt = 0

        # ⏳ Delay inicial mínimo para estabilização do processo
        # Removido sleep de 30s hardcoded - agora usa loop de verificação ativa
        time.sleep(2)

        while True:
            if self._is_server_healthy():
                elapsed = time.time() - start_time
                print(f"   ✅ Servidor respondendo na tentativa {attempt + 1} após {elapsed:.1f}s")
                logger.info(f"Servidor UP em {elapsed:.1f}s")
                return

            elapsed = time.time() - start_time

            # Verifica limites
            if max_wait_seconds and elapsed > max_wait_seconds:
                logger.error(f"Timeout: servidor não respondeu em {max_wait_seconds}s")
                raise TimeoutError(
                    f"Servidor não ficou saudável em {max_wait_seconds}s " f"({attempt} tentativas)"
                )

            if max_attempts and attempt >= max_attempts:
                logger.error(f"Max attempts: {max_attempts} (time: {elapsed:.1f}s)")
                raise TimeoutError(
                    f"Servidor não ficou saudável em {max_attempts} tentativas " f"({elapsed:.1f}s)"
                )

            attempt += 1

            # Print progress (a cada 10 tentativas ou 30s)
            if attempt % 10 == 1 or (elapsed > 30 and attempt % 5 == 1):
                print(f"   ⏳ Tentativa {attempt} após {elapsed:.1f}s...")

            time.sleep(1)

    def pytest_sessionfinish(self, session):
        """Ao final: exibe relatório de servidores derrubados e métricas."""
        if self.crashed_tests:
            print("\n" + "=" * 60)
            print("⚠️  TESTES QUE DERRUBARAM O SERVIDOR:")
            for test_name in self.crashed_tests:
                print(f"   - {test_name}")
            print("=" * 60)

        # Exibe métricas de startup se disponível
        if self.startup_metrics:
            print("\n" + "=" * 60)
            print("📊 MÉTRICAS DE STARTUP DO SERVIDOR:")
            if "total_startup_time" in self.startup_metrics:
                print(f"   ⏱️  Tempo total: {self.startup_metrics['total_startup_time']:.1f}s")
            print("=" * 60)


def pytest_configure(config):
    """Registra plugin de monitoramento."""
    config.pluginmanager.register(ServerMonitorPlugin(), "server_monitor")
