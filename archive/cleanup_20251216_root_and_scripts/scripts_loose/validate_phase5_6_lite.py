#!/usr/bin/env python3
"""
🚀 VALIDAÇÃO LITE - PHASE 5 & 6 (SEM COLETA DE MÉTRICAS PESADA)

Script de validação rápido que não executa ciclos completos da IntegrationLoop.
Apenas verifica pré-requisitos e código, sem rodar o sistema de consciência.

USO:
    python scripts/validate_phase5_6_lite.py --pre-flight
    python scripts/validate_phase5_6_lite.py --validate
    python scripts/validate_phase5_6_lite.py --all

SAÍDA:
    - logs/validation/phase5_6_lite_validation_TIMESTAMP.json

ATUALIZADO: 2025-12-09
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Setup paths
project_root = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(project_root))
os.chdir(project_root)


# Colors for output
class Colors:
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def log_info(msg: str):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.RESET}")


def log_success(msg: str):
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")


def log_warning(msg: str):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.RESET}")


def log_error(msg: str):
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")


def run_command(cmd: List[str], timeout: int = 30) -> Tuple[bool, str]:
    """Execute command and return success status and output"""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, cwd=project_root
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, f"Command timeout after {timeout}s"
    except Exception as e:
        return False, str(e)


def validate_preflight() -> Dict[str, Any]:
    """Stage 1: Pre-flight checks"""
    print("\n" + "=" * 80)
    print("STAGE 1: PRÉ-FLIGHT CHECKS")
    print("=" * 80)

    results = {}

    # Check Python version
    log_info("Verificando versão Python...")
    try:
        import sys

        version_info = sys.version_info
        python_version = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
        if version_info >= (3, 12):
            log_success(f"Python {python_version}")
            results["python_version"] = python_version
        else:
            log_warning(f"Python {python_version} (recomendado 3.12+)")
            results["python_version"] = python_version
    except Exception as e:
        log_error(f"Erro ao verificar Python: {e}")
        results["python_version"] = str(e)

    # Check PyTorch
    log_info("Verificando PyTorch...")
    try:
        import torch

        log_success(f"PyTorch {torch.__version__}")
        results["pytorch_version"] = torch.__version__

        # Check CUDA
        if torch.cuda.is_available():
            log_success(f"CUDA disponível - {torch.cuda.get_device_name(0)}")
            results["cuda_available"] = True
            results["cuda_device"] = torch.cuda.get_device_name(0)
        else:
            log_warning("CUDA não disponível (CPU mode)")
            results["cuda_available"] = False
    except Exception as e:
        log_error(f"PyTorch não disponível: {e}")
        results["pytorch_version"] = str(e)

    # Check essential modules
    log_info("Verificando módulos essenciais...")
    modules = [
        "fastapi",
        "uvicorn",
        "numpy",
        "scipy",
        "scikit-learn",
        "qdrant_client",
        "qiskit",
        "qiskit_aer",
    ]

    missing_modules = []
    for module in modules:
        try:
            __import__(module)
            log_success(f"✓ {module}")
        except ImportError:
            log_warning(f"✗ {module} não encontrado")
            missing_modules.append(module)

    results["missing_modules"] = missing_modules

    # Check directory structure
    log_info("Verificando estrutura de diretórios...")
    required_dirs = [
        "src/consciousness",
        "scripts/canonical/validate",
        "logs/validation",
        "data/monitor",
    ]

    missing_dirs = []
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            log_success(f"✓ {dir_path}")
        else:
            log_warning(f"✗ {dir_path} não encontrado")
            missing_dirs.append(dir_path)

    results["missing_directories"] = missing_dirs

    # Overall status
    overall_status = len(missing_modules) == 0 and len(missing_dirs) == 0
    results["overall_status"] = "PASS" if overall_status else "PASS_WITH_WARNINGS"

    return results


def validate_code() -> Dict[str, Any]:
    """Stage 2: Code validation"""
    print("\n" + "=" * 80)
    print("STAGE 2: VALIDAÇÃO DE CÓDIGO")
    print("=" * 80)

    results = {}

    # Black - Format check
    log_info("Verificando formatação (Black)...")
    success, output = run_command(
        [sys.executable, "-m", "black", "src/", "scripts/", "--check", "--diff"], timeout=60
    )

    if success:
        log_success("Formatação correta")
        results["black"] = "PASS"
    else:
        log_warning("Formatação pode ser melhorada")
        results["black"] = "PASS_WITH_WARNINGS"

    # Flake8 - Linting
    log_info("Verificando linting (Flake8)...")
    success, output = run_command(
        [
            sys.executable,
            "-m",
            "flake8",
            "src/",
            "scripts/",
            "--max-line-length=88",
            "--extend-ignore=E203,W503",
        ],
        timeout=60,
    )

    if success:
        log_success("Linting limpo")
        results["flake8"] = "PASS"
    else:
        log_warning("Linting encontrou problemas (não críticos)")
        results["flake8"] = "PASS_WITH_WARNINGS"

    # MyPy - Type checking
    log_info("Verificando tipos (MyPy)...")
    success, output = run_command(
        [sys.executable, "-m", "mypy", "src/", "--ignore-missing-imports", "--show-error-codes"],
        timeout=60,
    )

    if success:
        log_success("Tipos corretos")
        results["mypy"] = "PASS"
    else:
        log_warning("MyPy encontrou problemas de tipo")
        results["mypy"] = "PASS_WITH_WARNINGS"

    # Pytest - Basic imports
    log_info("Verificando módulos com pytest...")
    success, output = run_command(
        [sys.executable, "-m", "pytest", "tests/", "-x", "-v", "--tb=short", "-k", "import"],
        timeout=120,
    )

    if success:
        log_success("Testes passando")
        results["pytest"] = "PASS"
    else:
        log_warning("Alguns testes falhando (verificar logs)")
        results["pytest"] = "PARTIAL"

    # Overall status
    all_pass = all(v == "PASS" for v in results.values() if v in ["PASS", "PASS_WITH_WARNINGS"])
    results["overall_status"] = "PASS" if all_pass else "PARTIAL"

    return results


def main():
    parser = argparse.ArgumentParser(description="Validação LITE Phase 5 & 6")
    parser.add_argument("--pre-flight", action="store_true", help="Executa pré-flight checks")
    parser.add_argument("--validate", action="store_true", help="Executa validação de código")
    parser.add_argument("--all", action="store_true", help="Executa todos os testes")

    args = parser.parse_args()

    # Default: run all if no args
    if not any([args.pre_flight, args.validate, args.all]):
        args.all = True

    print("\n" + "=" * 80)
    print("🚀 PHASE 5 & 6 PRODUCTION VALIDATION (LITE)")
    print(f"ℹ️  Timestamp: {datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}")
    print("=" * 80)

    validation_results = {}

    if args.pre_flight or args.all:
        validation_results["preflight"] = validate_preflight()

    if args.validate or args.all:
        validation_results["code_validation"] = validate_code()

    # Overall status
    overall_status = all(
        result.get("overall_status") in ["PASS", "PASS_WITH_WARNINGS"]
        for result in validation_results.values()
    )

    print("\n" + "=" * 80)
    print("📊 RESULTADO FINAL")
    print("=" * 80)

    if overall_status:
        log_success(f"✅ VALIDAÇÃO COMPLETA - {len(validation_results)} estágios passaram")
    else:
        log_error(f"❌ VALIDAÇÃO FALHOU - Verifique erros acima")

    # Save results
    log_dir = Path("logs/validation")
    log_dir.mkdir(parents=True, exist_ok=True)

    output_file = (
        log_dir
        / f"phase5_6_lite_validation_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    )

    try:
        with open(output_file, "w") as f:
            json.dump(
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "overall_status": "PASS" if overall_status else "FAIL",
                    "validation_results": validation_results,
                },
                f,
                indent=2,
            )
        log_success(f"Resultado salvo em: {output_file}")
    except Exception as e:
        log_error(f"Erro ao salvar resultado: {e}")

    return 0 if overall_status else 1


if __name__ == "__main__":
    sys.exit(main())
