#!/usr/bin/env python3
"""
GPU + Thread Resource Diagnostic
Identifica exatamente onde threads/memory faltam
"""

import os
import resource
import subprocess
import sys
import threading
from datetime import datetime


def check_system_limits():
    """Verifica limites de recursos do sistema"""
    print("\n" + "=" * 80)
    print("📊 SYSTEM RESOURCE LIMITS")
    print("=" * 80)

    # Soft vs Hard limits
    limits_to_check = [
        ("RLIMIT_NPROC", "Max processes per user"),
        ("RLIMIT_NOFILE", "Max open file descriptors"),
        ("RLIMIT_STACK", "Max stack size"),
        ("RLIMIT_MEMLOCK", "Max locked memory"),
        ("RLIMIT_AS", "Max virtual memory"),
    ]

    for limit_name, description in limits_to_check:
        if hasattr(resource, limit_name):
            limit = getattr(resource, limit_name)
            soft, hard = resource.getrlimit(limit)

            soft_str = f"{soft//1024}KB" if soft != resource.RLIM_INFINITY else "UNLIMITED"
            hard_str = f"{hard//1024}KB" if hard != resource.RLIM_INFINITY else "UNLIMITED"

            print(f"\n{limit_name}:")
            print(f"  Soft: {soft_str}")
            print(f"  Hard: {hard_str}")
            print(f"  Current: {soft}")

            # Alerta se baixo
            if soft < 1000 and limit != resource.RLIMIT_MEMLOCK:
                print("  ⚠️  ALERTA: Limite baixo!")


def check_ulimit():
    """Verifica ulimit via bash"""
    print("\n" + "=" * 80)
    print("🔧 ULIMIT (bash system limits)")
    print("=" * 80)

    try:
        result = subprocess.run(
            ["bash", "-c", "ulimit -a"], capture_output=True, text=True, timeout=5
        )
        print(result.stdout)
    except Exception as e:
        print(f"Error: {e}")


def check_omp_config():
    """Verifica configuração OpenMP"""
    print("\n" + "=" * 80)
    print("🧵 OPENMP CONFIGURATION")
    print("=" * 80)

    omp_vars = [
        "OMP_NUM_THREADS",
        "OMP_THREAD_LIMIT",
        "OMP_MAX_ACTIVE_LEVELS",
        "OMP_STACKSIZE",
        "OMP_NESTED",
        "OMP_DYNAMIC",
        "GOMP_STACKSIZE",
        "LIBGOMP_DEBUG",
    ]

    for var in omp_vars:
        value = os.environ.get(var, "NOT SET")
        print(f"{var:30s}: {value}")


def check_pytorch_config():
    """Verifica configuração PyTorch CUDA"""
    print("\n" + "=" * 80)
    print("🎮 PYTORCH CUDA CONFIGURATION")
    print("=" * 80)

    pytorch_vars = [
        "PYTORCH_ALLOC_CONF",
        "PYTORCH_CUDA_ALLOC_CONF",
        "CUDA_LAUNCH_BLOCKING",
        "CUDA_DEVICE_ORDER",
        "CUDA_VISIBLE_DEVICES",
        "CUDA_SYNCHRONIZE",
        "CUDNN_BENCHMARK",
        "CUDNN_DETERMINISTIC",
        "TORCH_ALLOW_TF32",
    ]

    for var in pytorch_vars:
        value = os.environ.get(var, "NOT SET")
        print(f"{var:30s}: {value}")


def check_pthread_config():
    """Verifica pthread limits"""
    print("\n" + "=" * 80)
    print("🔒 PTHREAD LIMITS")
    print("=" * 80)

    # Tenta criar threads até falhar
    test_threads = []
    max_threads_test = 0

    try:
        for i in range(100):  # Teste até 100 threads
            t = threading.Thread(target=lambda: None)
            t.daemon = True
            t.start()
            test_threads.append(t)
            max_threads_test = i + 1
    except RuntimeError as e:
        print(f"❌ Thread creation failed at #{max_threads_test}: {e}")

    print(f"\n✅ Successfully created {max_threads_test} test threads")
    print("   (This is a lower bound; system may allow more)")


def check_gpu_memory():
    """Verifica GPU memory e limits"""
    print("\n" + "=" * 80)
    print("💾 GPU MEMORY")
    print("=" * 80)

    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=index,name,memory.total,memory.used,memory.free",
                "--format=csv,noheader",
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        print(result.stdout)
    except Exception as e:
        print(f"Error querying GPU: {e}")

    # PyTorch CUDA memory info
    try:
        import torch

        print("\n🔥 PyTorch CUDA Status:")
        print(f"  CUDA Available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"  Device: {torch.cuda.get_device_name(0)}")
            print(f"  Memory Allocated: {torch.cuda.memory_allocated(0) / 1e6:.1f} MB")
            print(f"  Memory Cached: {torch.cuda.memory_reserved(0) / 1e6:.1f} MB")
    except Exception as e:
        print(f"Error checking PyTorch CUDA: {e}")


def check_limits_conf():
    """Verifica /etc/security/limits.conf"""
    print("\n" + "=" * 80)
    print("📄 /etc/security/limits.conf")
    print("=" * 80)

    try:
        result = subprocess.run(
            ["cat", "/etc/security/limits.conf"], capture_output=True, text=True, timeout=5
        )
        # Show only non-comment lines
        lines = [
            line
            for line in result.stdout.split("\n")
            if line.strip() and not line.strip().startswith("#")
        ]
        if lines:
            print("Active limits:")
            for line in lines[:20]:
                print(f"  {line}")
        else:
            print("  (No active limits configured)")
    except Exception as e:
        print(f"Error: {e}")


def check_pam_limits():
    """Verifica PAM limits"""
    print("\n" + "=" * 80)
    print("🔐 PAM LIMITS (per-user/session)")
    print("=" * 80)

    try:
        result = subprocess.run(
            ["cat", "/etc/security/limits.d/*"], capture_output=True, text=True, timeout=5
        )
        lines = [
            line
            for line in result.stdout.split("\n")
            if line.strip() and not line.strip().startswith("#")
        ]
        if lines:
            for line in lines[:20]:
                print(f"  {line}")
        else:
            print("  (No PAM limits configured)")
    except Exception as e:
        print(f"Info: {e}")


def diagnose_thread_issue():
    """Diagnóstico específico de thread starvation"""
    print("\n" + "=" * 80)
    print("🔍 THREAD STARVATION ROOT CAUSE")
    print("=" * 80)

    print(
        """
POSSIBILIDADES:

1. RLIMIT_NPROC muito baixo
   └─ Cada thread OpenMP conta como processo
   └─ padrão Ubuntu: 63356 (ok)
   └─ padrão Kali: ~1024 (PROBLEMA!)
   └─ Solução: ulimit -u unlimited

2. PTHREAD_STACK_SIZE padrão (8-10MB)
   └─ Com OMP_NUM_THREADS=2+: 16-20MB já
   └─ Com múltiplas threads: rápido excede memória
   └─ Solução: export GOMP_STACKSIZE=512k

3. RLIMIT_STACK muito baixo
   └─ Threads precisam de pilha de função
   └─ Padrão: 8MB (pode ser insuficiente)
   └─ Solução: ulimit -s unlimited

4. Fragmentação de memória CUDA
   └─ Chunks não se consolidam
   └─ PYTORCH_ALLOC_CONF=max_split_size_mb:32 ajuda
   └─ Mas 32MB ainda pode não ser o ideal
   └─ Solução: profile com torch.cuda.memory._dump_snapshot()

5. PyTorch Eager Mode vs Graph Mode
   └─ Eager: cria tensor a cada operação (muita memória)
   └─ Solução: torchscript ou torch.compile() para otimizar
"""
    )


def generate_recommendations():
    """Gera recomendações específicas"""
    print("\n" + "=" * 80)
    print("✅ RECOMENDAÇÕES POR CENÁRIO")
    print("=" * 80)

    print(
        """
CENÁRIO A: Vindo de Kali (ulimit baixo)
────────────────────────────────────
1. Verificar limite atual:
   $ ulimit -u

2. Se < 10000:
   $ ulimit -u unlimited
   $ export GOMP_STACKSIZE=512k

3. Testar ciclos novamente

CENÁRIO B: CUDA memory fragmentation
─────────────────────────────────────
1. Current: PYTORCH_ALLOC_CONF=max_split_size_mb:32
2. Try: max_split_size_mb=16 (mais agressivo)
3. Or enable CachedAllocator profiling:

   torch.cuda.memory._record_memory_history()
   # ... run cycles ...
   torch.cuda.memory._dump_snapshot('snapshot.pickle')

CENÁRIO C: Thread stack exhaustion
──────────────────────────────────
1. Check: ulimit -s (default 8MB)
2. Set: ulimit -s unlimited
3. Or: export GOMP_STACKSIZE=256k (reduz por thread)

CENÁRIO D: OMP nesting conflict
───────────────────────────────
1. Disable nesting:
   export OMP_NESTED=FALSE

2. Force flat team:
   export OMP_MAX_ACTIVE_LEVELS=1
"""
    )


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🔧 OMNIMIND SYSTEM RESOURCE DIAGNOSTIC")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"System: {sys.platform}")

    # Run all checks
    check_ulimit()
    check_system_limits()
    check_omp_config()
    check_pytorch_config()
    check_pthread_config()
    check_gpu_memory()
    check_limits_conf()
    check_pam_limits()
    diagnose_thread_issue()
    generate_recommendations()

    print("\n" + "=" * 80)
    print("📋 NEXT STEPS:")
    print("=" * 80)
    print(
        """
1. Run this diagnostic:
   python3 diagnose_threads.py > diagnostic_$(date +%Y%m%d_%H%M%S).log

2. Review output for ⚠️ ALERTA markers

3. Apply recommended fixes in scripts/run_500_cycles_scientific_validation.py:
   - Add before ANY imports

4. Re-test with 80 cycles first

5. If still fails, share diagnostic log for detailed analysis
"""
    )
