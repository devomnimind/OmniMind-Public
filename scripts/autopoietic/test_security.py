#!/usr/bin/env python3
"""
Teste de Segurança do Sistema Autopoiético

Valida que o sistema gera componentes com:
1. Assinatura de segurança obrigatória
2. Sandboxing para validação
3. Isolamento de execução
"""

import sys
from pathlib import Path

# Adicionar src ao path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from autopoietic.manager import AutopoieticManager
from autopoietic.meta_architect import ComponentSpec
from autopoietic.sandbox import create_secure_sandbox


def test_security_signature():
    """Testa se componentes têm assinatura de segurança."""
    print("🧪 Testando assinatura de segurança...")

    try:
        manager = AutopoieticManager()

        # Registrar componente base
        base_spec = ComponentSpec(
            name="test_kernel", type="process", config={"priority": "high", "generation": "0"}
        )
        manager.register_spec(base_spec)

        # Executar ciclo com métricas que forçam síntese
        metrics = {
            "error_rate": 0.15,
            "cpu_usage": 80.0,
            "latency_ms": 150.0,
        }  # Valores altos para forçar evolução
        print(f"Executando ciclo com métricas: {metrics}")
        log = manager.run_cycle(metrics)
        print(f"Ciclo executado. Componentes sintetizados: {log.synthesized_components}")

        # Verificar se arquivo foi criado com assinatura
        if log.synthesized_components:
            component_name = log.synthesized_components[0]
            expected_file = (
                Path("data/autopoietic/synthesized_code_secure") / f"{component_name}.py"
            )
            print(f"Verificando arquivo: {expected_file}")

            if expected_file.exists():
                content = expected_file.read_text()
                print("Arquivo existe. Verificando assinatura...")
                has_signature = "modulo_autopoiesis_data_" in content
                has_sandbox_marker = "_generated_in_sandbox = True" in content
                print(f"Assinatura presente: {has_signature}")
                print(f"Marker sandbox presente: {has_sandbox_marker}")

                if has_signature and has_sandbox_marker:
                    print("✅ Assinatura de segurança presente")
                    return True
                else:
                    print("❌ Assinatura de segurança ausente")
                    print(f"Conteúdo do arquivo: {content[:500]}...")
                    return False
            else:
                print("❌ Arquivo não foi criado")
                return False
        else:
            print("❌ Nenhum componente foi sintetizado")
            return False
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_sandbox_validation():
    """Testa validação no sandbox."""
    print("🧪 Testando validação no sandbox...")

    # Código seguro
    safe_code = '''
# 🔒 SEGURANÇA AUTOPOIÉTICA - COMPONENTE GERADO EM SANDBOX
import logging

class ModuloAutopoiesisDataTestComponent:
    """Auto‑generated component of type 'process' (Strategy: EXPAND).
    🔒 Security Signature: modulo_autopoiesis_data_test_component
    🧪 Generated in Sandbox Environment
    """
    def __init__(self):
        self._security_signature = "modulo_autopoiesis_data_test_component"
        self._generated_in_sandbox = True
        self._logger = logging.getLogger(__name__)

    def run(self) -> None:
        self._logger.info(f"Running {self.__class__.__name__} component (EXPANDED)")
'''

    # Código perigoso
    dangerous_code = """
import os
os.system("rm -rf /")
"""

    with create_secure_sandbox() as sandbox:
        # Testar código seguro
        safe_result = sandbox.execute_component(safe_code, "modulo_autopoiesis_data_test_component")
        if safe_result["success"]:
            print("✅ Código seguro passou na validação")
        else:
            print(f"❌ Código seguro falhou: {safe_result.get('error')}")
            return False

        # Testar código perigoso
        dangerous_result = sandbox.validate_component(dangerous_code)
        if not dangerous_result:
            print("✅ Código perigoso foi rejeitado")
        else:
            print("❌ Código perigoso passou na validação (ERRO DE SEGURANÇA!)")
            return False

    return True


def test_file_isolation():
    """Testa isolamento de arquivos."""
    print("🧪 Testando isolamento de arquivos...")

    # Verificar se arquivos são criados no diretório seguro
    secure_dir = Path("data/autopoietic/synthesized_code_secure")

    if secure_dir.exists():
        files_in_secure = list(secure_dir.glob("*.py"))
        if files_in_secure:
            print(f"✅ Arquivos criados no diretório seguro: {len(files_in_secure)} arquivos")
            # Verificar assinatura nos nomes
            signed_files = [f for f in files_in_secure if "modulo_autopoiesis_data_" in f.name]
            if len(signed_files) == len(files_in_secure):
                print("✅ Todos os arquivos têm assinatura no nome")
                return True
            else:
                print(f"❌ {len(files_in_secure) - len(signed_files)} arquivos sem assinatura")
                return False
        else:
            print("⚠️ Nenhum arquivo encontrado no diretório seguro")
            return False
    else:
        print("❌ Diretório seguro não existe")
        return False


def main():
    """Executa todos os testes de segurança."""
    print("🔒 INICIANDO TESTES DE SEGURANÇA AUTOPOIÉTICA")
    print("=" * 50)

    tests = [
        ("Assinatura de Segurança", test_security_signature),
        ("Validação no Sandbox", test_sandbox_validation),
        ("Isolamento de Arquivos", test_file_isolation),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            print()
        except Exception as e:
            print(f"❌ Erro no teste {test_name}: {e}")
            results.append((test_name, False))
            print()

    print("=" * 50)
    print("📊 RESULTADOS FINAIS:")

    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False

    print()
    if all_passed:
        print("🎉 TODOS OS TESTES DE SEGURANÇA PASSARAM!")
        print("🛡️ Sistema autopoiético está seguro para uso.")
    else:
        print("🚨 FALHAS DE SEGURANÇA DETECTADAS!")
        print("🛡️ NÃO use o sistema até corrigir as vulnerabilidades.")

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
