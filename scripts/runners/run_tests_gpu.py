#!/usr/bin/env python3
"""
Test runner inteligente com GPU dinâmico
- Saída em tempo real na tela com timestamps
- Salva log com timestamps
- GPU para testes quantum/ollama/mathematical
- CPU para testes padrão
"""
import os
import re
import subprocess
import sys
from datetime import datetime

# Verificar GPU disponível
CUDA_AVAILABLE = False
try:
    import torch

    CUDA_AVAILABLE = torch.cuda.is_available()
    device_name = torch.cuda.get_device_name(0) if CUDA_AVAILABLE else "CPU"
except Exception:
    device_name = "CPU"

# Padrões para detectar tipos de teste que precisam GPU
GPU_TEST_PATTERNS = [
    r"quantum",
    r"ollama",
    r"mathematical",
    r"quantics",
    r"q_bit",
    r"superposition",
]

LOG_FILE = None


def log_and_print(msg: str):
    """Printa com timestamp e salva em log"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_msg = f"[{timestamp}] {msg}"
    print(formatted_msg)
    if LOG_FILE:
        with open(LOG_FILE, "a") as f:
            f.write(formatted_msg + "\n")


def should_use_gpu(test_path: str) -> bool:
    """Determina se o teste deve rodar em GPU"""
    if not CUDA_AVAILABLE:
        return False
    test_lower = test_path.lower()
    for pattern in GPU_TEST_PATTERNS:
        if re.search(pattern, test_lower):
            return True
    return False


def run_tests(test_path: str = "tests/", device: str = "cpu"):
    """Roda testes com o dispositivo especificado"""
    if device == "gpu":
        os.environ["CUDA_VISIBLE_DEVICES"] = "0"
        os.environ["TORCH_HOME"] = "/home/fahbrain/.cache/torch"
        os.environ["TF_FORCE_GPU_MEMORY_GROWTH"] = "true"
        device_display = "GPU (NVIDIA GTX 1650)"
    else:
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
        device_display = "CPU"

    log_and_print("=" * 80)
    log_and_print(f"Running with {device_display}")
    log_and_print(f"Path: {test_path}")
    log_and_print("=" * 80)

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        test_path,
        "-v",
        "--tb=short",
        "-x",
        "--maxfail=1",
        "-p",
        "no:warnings",
    ]

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    failed_test = None
    failure_lines = []
    in_failure = False

    if process.stdout:
        for line in process.stdout:
            line = line.rstrip()

            # Detectar falhas
            if "FAILED" in line or "ERROR" in line:
                in_failure = True
                failed_test = re.search(r"test_\w+", line)
                if failed_test:
                    failed_test = failed_test.group(0)
                log_and_print("\n" + "=" * 80)
                log_and_print("FAILURE DETECTED!")
                log_and_print("=" * 80)

            # Capturar linhas de falha
            if in_failure:
                failure_lines.append(line)
                log_and_print(line)
                if line.startswith("=") and ("passed" in line.lower() or "failed" in line.lower()):
                    in_failure = False
            elif "passed" in line.lower() and "%" in line:
                log_and_print(line)
            elif line and not line.startswith(" "):
                log_and_print(line)

    process.wait()

    log_and_print("\n" + "=" * 80)
    log_and_print("SUMMARY")
    log_and_print(f"Device: {device_display}")
    if failed_test:
        log_and_print(f"Failed: {failed_test}")
    else:
        log_and_print("All tests passed!")
    log_and_print(f"Exit Code: {process.returncode}")
    log_and_print("=" * 80)

    return process.returncode, failed_test, failure_lines


def main():
    global LOG_FILE

    # Criar log file
    os.makedirs("data/test_reports", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    LOG_FILE = f"data/test_reports/tests_{timestamp}.log"

    log_and_print("=" * 80)
    log_and_print("OMNIMIND TEST RUNNER - INTELLIGENT GPU ALLOCATION")
    log_and_print("=" * 80)
    log_and_print(f"GPU Available: {CUDA_AVAILABLE}")
    log_and_print(f"Log File: {LOG_FILE}")
    log_and_print("")

    # Determine default device
    default_device = "gpu" if CUDA_AVAILABLE else "cpu"

    # Rodar testes
    exit_code, failed_test, _ = run_tests("tests/", default_device)

    if exit_code != 0:
        log_and_print("\n" + "=" * 80)
        log_and_print("TESTS FAILED")
        log_and_print("=" * 80)
        if failed_test:
            log_and_print(f"Failed test: {failed_test}")

        # Não reiniciar em CPU automaticamente
        log_and_print("Skipping CPU retry as requested.")

    log_and_print("\n" + "=" * 80)
    log_and_print(f"Full log saved: {LOG_FILE}")
    log_and_print("=" * 80)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
