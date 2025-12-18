#!/usr/bin/env python3
"""
MCP Runtime Validation - Inicia MCPs e valida health checks
Fase 6 do ciclo: Teste de instâncias reais em execução
"""

import subprocess
import sys
import time
from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class MCPHealthValidator:
    """Valida health de MCPs em execução."""

    def __init__(self):
        self.mcps = {
            "memory": {"port": 4321, "module": "src.integrations.mcp_memory_server"},
            "thinking": {
                "port": 4322,
                "module": "src.integrations.mcp_thinking_server",
            },
            "context": {"port": 4323, "module": "src.integrations.mcp_context_server"},
        }
        self.processes = {}

    def start_mcp(self, name: str) -> bool:
        """Inicia um MCP servidor."""
        print(f"\n   🚀 Iniciando {name}...")

        mcp_info = self.mcps[name]
        try:
            # Inicia processo em background
            proc = subprocess.Popen(
                [sys.executable, "-m", mcp_info["module"]],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(PROJECT_ROOT),
            )
            self.processes[name] = proc
            time.sleep(2)  # Aguarda startup

            # Verifica se processo ainda está rodando
            if proc.poll() is not None:
                _, stderr = proc.communicate()
                print(f"      ❌ Falha ao iniciar: {stderr.decode()[:100]}")
                return False

            print(f"      ✅ Processo iniciado (PID: {proc.pid})")
            return True

        except Exception as e:
            print(f"      ❌ Erro: {e}")
            return False

    def health_check(self, name: str) -> bool:
        """Testa health endpoint do MCP."""
        port = self.mcps[name]["port"]
        url = f"http://localhost:{port}/health"

        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"      ✅ Health check passed (status: {response.status_code})")
                return True
            else:
                print(f"      ⚠️  Unexpected status: {response.status_code}")
                return False
        except requests.ConnectionError:
            print(f"      ⚠️  Connection refused (port {port} not listening yet)")
            return False
        except requests.Timeout:
            print("      ⚠️  Health check timeout")
            return False
        except Exception as e:
            print(f"      ⚠️  Error: {str(e)[:50]}")
            return False

    def stop_mcp(self, name: str):
        """Para um MCP servidor."""
        if name in self.processes:
            proc = self.processes[name]
            print(f"\n   🛑 Parando {name}...")
            try:
                proc.terminate()
                proc.wait(timeout=5)
                print("      ✅ Processo encerrado")
            except subprocess.TimeoutExpired:
                proc.kill()
                print("      ✅ Processo forçadamente encerrado")
            except Exception as e:
                print(f"      ⚠️  Error: {e}")

    def validate_all(self) -> dict:
        """Valida todos os MCPs."""
        print("\n" + "=" * 70)
        print("🏥 FASE 6: RUNTIME VALIDATION (Health Checks)")
        print("=" * 70)

        results = {}

        for mcp_name in ["memory", "thinking", "context"]:
            print(f"\n🔍 Validando {mcp_name.upper()}:")

            # Start
            started = self.start_mcp(mcp_name)
            if not started:
                results[mcp_name] = {"started": False, "healthy": False}
                continue

            # Health check
            healthy = self.health_check(mcp_name)
            results[mcp_name] = {"started": True, "healthy": healthy}

            # Stop
            self.stop_mcp(mcp_name)

        return results

    def summary(self, results: dict):
        """Mostra summary dos resultados."""
        print("\n" + "=" * 70)
        print("📊 RESUMO DE VALIDAÇÃO (Runtime)")
        print("=" * 70)

        all_ok = True
        for name, result in results.items():
            started = result.get("started", False)
            healthy = result.get("healthy", False)

            if started and healthy:
                print(f"✅ {name:15} | Started: ✅ | Healthy: ✅")
            elif started:
                print(f"⚠️  {name:15} | Started: ✅ | Healthy: ❌")
                all_ok = False
            else:
                print(f"❌ {name:15} | Started: ❌ | Healthy: ❌")
                all_ok = False

        print("\n" + "=" * 70)
        if all_ok:
            print("✅ Todos os MCPs estão funcionando normalmente")
            print("   Próximo passo: Implementar testes de integração")
        else:
            print("⚠️  Alguns MCPs falharam na validação")
            print("   Verifique os logs e ajuste configurações")
        print("=" * 70 + "\n")

        return all_ok


def main():
    """Main function."""
    print("\n" + "🎯 " * 25)
    print("OmniMind MCP Runtime Validation")
    print("🎯 " * 25)

    validator = MCPHealthValidator()
    results = validator.validate_all()
    all_ok = validator.summary(results)

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
