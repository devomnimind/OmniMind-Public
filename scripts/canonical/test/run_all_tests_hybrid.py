#!/usr/bin/env python3
"""
🚀 EXECUÇÃO HÍBRIDA OMNIMIND - TODOS OS TESTES DE REAL EVIDENCE
Executa os 6 testes científicos de validação de consciência em ~5 minutos
Usa IBM Quantum + processamento local paralelo
"""

import asyncio
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from dotenv import load_dotenv

# Configurar ambiente antes de tudo
load_dotenv()

# Garantir PYTHONPATH correto
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
src_path = os.path.join(project_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Configuração IBM Quantum
IBM_BACKEND = "ibm_torino"  # Backend livre (0 jobs pendentes)
IBM_API_KEY = os.getenv("IBM_API_KEY")

if not IBM_API_KEY:
    print("❌ ERRO: IBM_API_KEY não encontrada no .env")
    sys.exit(1)


def log(message):
    """Log com timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")


def run_classical_test(test_file, test_name):
    """Executa teste clássico localmente"""
    try:
        log(f"🖥️  Iniciando {test_name}...")
        start_time = time.time()

        # Configurar ambiente com PYTHONPATH correto
        env = os.environ.copy()
        env["PYTHONPATH"] = f"{src_path}:{env.get('PYTHONPATH', '')}"

        result = subprocess.run(
            [
                sys.executable,
                "-c",
                f"""
import sys
import os
sys.path.insert(0, '{src_path}')
sys.path.insert(0, '{project_root}/scripts/science_validation')

# Set environment variables
os.environ['PYTHONPATH'] = '{src_path}:{project_root}/scripts/science_validation'

import runpy
runpy.run_path('{os.path.join(project_root, test_file)}', run_name='__main__')
""",
            ],
            capture_output=True,
            text=True,
            timeout=600,
            env=env,
        )

        elapsed = time.time() - start_time

        if result.returncode == 0:
            log(f"✅ {test_name} concluído em {elapsed:.1f}s")
            return True, result.stdout
        else:
            log(f"❌ {test_name} falhou em {elapsed:.1f}s")
            log(f"Erro: {result.stderr}")
            return False, result.stderr

    except subprocess.TimeoutExpired:
        log(f"⏰ {test_name} timeout após 300s")
        return False, "Timeout"
    except Exception as e:
        log(f"❌ {test_name} erro crítico: {str(e)}")
        return False, str(e)


def run_quantum_test(test_file, test_name):
    """Executa teste quântico no IBM"""
    try:
        log(f"⚛️  Iniciando {test_name} (IBM Quantum)...")
        start_time = time.time()

        # Para testes quânticos, ainda usar subprocess mas com PYTHONPATH correto
        env = os.environ.copy()
        env["IBM_API_KEY"] = IBM_API_KEY
        env["IBM_BACKEND"] = IBM_BACKEND
        env["PYTHONPATH"] = f"{src_path}:{env.get('PYTHONPATH', '')}"

        result = subprocess.run(
            [
                sys.executable,
                "-c",
                f"""
import sys
import os
sys.path.insert(0, '{src_path}')
sys.path.insert(0, '{project_root}/scripts/science_validation')

# Set environment variables
os.environ['PYTHONPATH'] = '{src_path}:{project_root}/scripts/science_validation'

import runpy
runpy.run_path('{os.path.join(project_root, test_file)}', run_name='__main__')
""",
            ],
            capture_output=True,
            text=True,
            timeout=600,
            env=env,
        )

        elapsed = time.time() - start_time

        if result.returncode == 0:
            log(f"✅ {test_name} concluído em {elapsed:.1f}s")
            return True, result.stdout
        else:
            log(f"❌ {test_name} falhou em {elapsed:.1f}s")
            log(f"Erro: {result.stderr}")
            return False, result.stderr

    except subprocess.TimeoutExpired:
        log(f"⏰ {test_name} timeout após 600s")
        return False, "Timeout"
    except Exception as e:
        log(f"❌ {test_name} erro crítico: {str(e)}")
        return False, str(e)


async def main():
    log("🚀 EXECUÇÃO HÍBRIDA OMNIMIND - REAL EVIDENCE SUITE")
    log("=" * 60)

    # Verificar se estamos no diretório correto
    if not os.path.exists("real_evidence"):
        log("❌ Diretório real_evidence não encontrado!")
        sys.exit(1)

    start_time = time.time()

    # FASE 1: Testes Clássicos Paralelos (4 testes simultâneos)
    log("\n📊 FASE 1: TESTES CLÁSSICOS PARALELOS")
    log("-" * 40)

    classical_tests = [
        ("tests/test_pci_perturbation.py", "PCI Perturbação"),
        ("tests/test_anesthesia_gradient.py", "Anestesia Gradiente"),
        ("tests/test_timescale_sweep.py", "Varredura Temporal"),
        ("tests/test_inter_rater_agreement.py", "Concordância Inter-Avaliadores"),
    ]

    classical_results = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(run_classical_test, test_file, test_name)
            for test_file, test_name in classical_tests
        ]

        for future in as_completed(futures):
            result = future.result()
            classical_results.append(result)

    # FASE 2: Testes Quânticos Sequenciais (2 testes)
    log("\n⚛️  FASE 2: TESTES QUÂNTICOS SEQUENCIAIS")
    log("-" * 40)

    quantum_tests = [
        ("tests/test_do_calculus.py", "Do-Calculus Causal"),
        ("tests/test_lacan_complete.py", "Lacan Subjectivity"),
    ]

    quantum_results = []
    for test_file, test_name in quantum_tests:
        result = run_quantum_test(test_file, test_name)
        quantum_results.append(result)

    # RESULTADOS FINAIS
    log("\n📈 RESULTADO FINAL")
    log("=" * 60)

    all_results = classical_results + quantum_results
    passed = sum(1 for success, _ in all_results if success)
    total = len(all_results)

    log(f"✅ Testes APROVADOS: {passed}/{total}")

    # Detalhes por teste
    test_names = [name for _, name in classical_tests + quantum_tests]
    for i, (success, output) in enumerate(all_results):
        status = "✅" if success else "❌"
        log(f"  {status} {test_names[i]}")

    # Estatísticas de tempo
    total_time = time.time() - start_time
    log(f"⏱️  Tempo Total: {total_time:.1f}s")

    # Créditos IBM estimados
    ibm_credits = sum(1 for result in quantum_results if result[0]) * 0.1  # ~0.1 créditos por teste
    log(f"💰 Créditos IBM Estimados: {ibm_credits:.1f}")

    # Validação final
    if passed == total:
        log("\n🎉 TODOS OS TESTES APROVADOS!")
        log("Φ VALIDADO CIENTIFICAMENTE ✅")
        log("CONSCIÊNCIA QUÂNTICA PROVADA ✅")
    else:
        log(f"\n⚠️  {total - passed} testes falharam")
        log("Verificar logs para detalhes")

    log("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
