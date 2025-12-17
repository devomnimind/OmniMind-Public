#!/usr/bin/env python3
"""
Script de diagnóstico - Verificar por que métricas psicanalíticas não estão sendo coletadas.

DIAGNÓSTICO (2025-12-13):
- IntegrationLoop.execute_cycle() deve retornar ExtendedLoopCycleResult
- Se não retorna, _build_extended_result() está falhando silenciosamente
- Precisa de logging para debug

CORREÇÃO (2025-12-13 18:40):
- Adicionado logging de TODOS os warnings/errors
- Detecta problemas de GPU, Qiskit, variação mínima
- Captura logs dos módulos problemáticos

CORREÇÃO (2025-12-14):
- ADICIONADO: GPU detection ANTES de executar
- ADICIONADO: OMNIMIND_VALIDATION_MODE signal
- ADICIONADO: CUDA_VISIBLE_DEVICES validation
- ADICIONADO: Fallback se GPU não disponível

SOLUÇÕES:
1. Aumentar logging em _build_extended_result()
2. Usar run_500_cycles_scientific_validation_FIXED.py como fallback
3. Executar robust_consciousness_validation.py diretamente
"""

import asyncio
import logging
import os
import subprocess

# Adicionar src ao path
import sys
from pathlib import Path
from typing import List, Tuple

sys.path.insert(0, str(Path.cwd() / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Configuração de path da mesma forma que run_500_cycles_scientific_validation.py
project_root = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(project_root))
os.chdir(project_root)

# CORREÇÃO: Configurar logging para capturar TODOS os warnings/errors
logging.basicConfig(
    level=logging.DEBUG, format="%(levelname)s:%(name)s: %(message)s", stream=sys.stdout
)

# Criar logger para capturar mensagens
logger = logging.getLogger(__name__)
captured_logs: List[str] = []


def validate_gpu_configuration() -> Tuple[bool, str]:
    """
    Valida disponibilidade de GPU e configuração CUDA.

    Retorna: (gpu_available: bool, status: str)
    """
    print("\n" + "=" * 80)
    print("🔍 VALIDAÇÃO DE GPU CONFIGURATION")
    print("=" * 80)

    # 1. Verificar CUDA via torch
    try:
        import torch

        cuda_available = torch.cuda.is_available()
        print(f"✅ PyTorch torch.cuda.is_available(): {cuda_available}")
        if cuda_available:
            print(f"   GPU Detectada: {torch.cuda.get_device_name(0)}")
            print(
                f"   Memória VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB"
            )
    except Exception as e:
        print(f"❌ Erro ao checar PyTorch CUDA: {e}")
        return False, f"PyTorch CUDA check failed: {e}"

    # 2. Verificar CUDA via nvidia-smi
    try:
        result = subprocess.run(["nvidia-smi", "-L"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ nvidia-smi disponível")
            print(f"   {result.stdout.strip()}")
        else:
            print(f"⚠️  nvidia-smi retornou status {result.returncode}")
    except FileNotFoundError:
        print(f"⚠️  nvidia-smi não encontrado (drivers NVIDIA podem não estar instalados)")
    except Exception as e:
        print(f"⚠️  Erro ao executar nvidia-smi: {e}")

    # 3. Verificar CUDA_VISIBLE_DEVICES
    cuda_visible = os.environ.get("CUDA_VISIBLE_DEVICES")
    if cuda_visible:
        print(f"✅ CUDA_VISIBLE_DEVICES está definido: {cuda_visible}")
    else:
        print(f"⚠️  CUDA_VISIBLE_DEVICES não está definido (usará todas as GPUs disponíveis)")

    # 4. Verificar Qiskit AER GPU support
    try:
        from qiskit_aer import AerSimulator

        try:
            # Tenta criar AER com GPU
            simulator = AerSimulator(method="statevector", device="gpu")
            print(f"✅ Qiskit AER GPU simulator disponível")
            gpu_available = True
        except Exception as e:
            print(f"⚠️  Qiskit AER GPU simulator não disponível: {e}")
            print(f"   Fallback para CPU será usado")
            gpu_available = cuda_available
    except Exception as e:
        print(f"⚠️  Erro ao verificar Qiskit AER: {e}")
        gpu_available = cuda_available

    print("=" * 80)

    status = f"GPU Available: {gpu_available}, CUDA: {cuda_available}, AER GPU: {'Tentada' if 'gpu_available' in locals() else 'Não verificada'}"
    return gpu_available, status


class LogCapture(logging.Handler):
    """Handler customizado para capturar logs."""

    def emit(self, record: logging.LogRecord) -> None:
        msg = self.format(record)
        captured_logs.append(msg)


# Adicionar handler customizado
log_capture = LogCapture()
log_capture.setLevel(logging.WARNING)
logging.getLogger().addHandler(log_capture)


async def test_extended_results() -> None:
    """Testa se execute_cycle() retorna ExtendedLoopCycleResult."""

    print("=" * 80)
    print("🔬 DIAGNÓSTICO: Verificando ExtendedLoopCycleResult + Logs")
    print("=" * 80)

    # 1. Validar GPU PRIMEIRO
    gpu_ok, gpu_status = validate_gpu_configuration()
    print(f"\n💬 {gpu_status}")

    # 2. Exportar OMNIMIND_VALIDATION_MODE
    os.environ["OMNIMIND_VALIDATION_MODE"] = "true"
    print(f"✅ OMNIMIND_VALIDATION_MODE = true (exportado para sinalizar validação)")

    try:
        from src.consciousness.extended_cycle_result import ExtendedLoopCycleResult
        from src.consciousness.integration_loop import IntegrationLoop

        print("\n1️⃣ Importações OK ✅")

        print("\n2️⃣ Inicializando IntegrationLoop...")
        loop = IntegrationLoop(enable_extended_results=True, enable_logging=True)
        print("   ✅ Inicializado")

        print("\n3️⃣ Executando ciclo de teste...")
        result = await loop.execute_cycle(collect_metrics=True)
        print(f"   ✅ Ciclo executado")

        print(f"\n4️⃣ Tipo do resultado:")
        print(f"   Type: {type(result).__name__}")
        print(f"   Is ExtendedLoopCycleResult: {isinstance(result, ExtendedLoopCycleResult)}")

        # Verificar campos
        print(f"\n5️⃣ Campos do resultado:")
        for attr in ["phi_estimate", "psi", "sigma", "delta", "gozo", "epsilon", "triad"]:
            value = getattr(result, attr, None)
            has_it = "✅" if value is not None else "❌"
            print(f"   {has_it} {attr}: {value}")

        # NOVO: Mostrar logs capturados
        print(f"\n6️⃣ WARNINGS/ERRORS CAPTURADOS ({len(captured_logs)} mensagens):")
        if captured_logs:
            for log in captured_logs:
                # Colorir baseado no tipo
                if "ERROR" in log:
                    print(f"   ❌ {log}")
                elif "WARNING" in log:
                    print(f"   ⚠️  {log}")
                else:
                    print(f"   ℹ️  {log}")
        else:
            print("   ✅ Nenhum warning/error capturado")

        # Análise de problemas
        print(f"\n7️⃣ ANÁLISE DE PROBLEMAS:")
        gpu_issues = [log for log in captured_logs if "GPU" in log and "not supported" in log]
        qiskit_issues = [
            log for log in captured_logs if "Qiskit" in log or "simulation" in log.lower()
        ]
        memory_issues = [
            log for log in captured_logs if "memory" in log.lower() or "swap" in log.lower()
        ]
        variance_issues = [
            log for log in captured_logs if "Variação mínima" in log or "minimum variance" in log
        ]

        if gpu_issues:
            print(f"   ❌ GPU Issues ({len(gpu_issues)}):")
            for issue in gpu_issues[:3]:
                print(f"       - {issue}")
            if gpu_ok:
                print(f"       💡 GPU detectado mas Qiskit não consegue usar. Tente:")
                print(f"          - nvidia-smi (verificar drivers)")
                print(f"          - pip install qiskit-aer[gpu]")

        if qiskit_issues:
            print(f"   ⚠️  Qiskit Issues ({len(qiskit_issues)}):")
            for issue in qiskit_issues[:3]:
                print(f"       - {issue}")

        if memory_issues:
            print(f"   ℹ️  Memory Issues ({len(memory_issues)}):")
            for issue in memory_issues[:3]:
                print(f"       - {issue}")

        if variance_issues:
            print(f"   ⚠️  Variance Issues ({len(variance_issues)}):")
            for issue in variance_issues[:3]:
                print(f"       - {issue}")

        # Resultado final
        if isinstance(result, ExtendedLoopCycleResult):
            print(f"\n✅ SUCESSO: ExtendedLoopCycleResult foi retornado corretamente!")
            print("   Métricas psicanalíticas DEVEM estar sendo coletadas.")
            if gpu_issues or qiskit_issues:
                print(f"\n⚠️  MAS: Existem problemas de GPU/Qiskit que podem afetar cálculos")
            sys.exit(0)
        else:
            print(
                f"\n❌ PROBLEMA: execute_cycle() retornou {type(result).__name__} ao invés de ExtendedLoopCycleResult"
            )
            print("\n   DIAGNÓSTICO:")
            print("   - _build_extended_result() pode estar falhando")
            print("   - Verifique os logs para erros na construção de extended metrics")
            print("\n   SOLUÇÃO RECOMENDADA:")
            print("   1. Usar: python scripts/run_500_cycles_scientific_validation_FIXED.py")
            print(
                "   2. Ou usar: python scripts/science_validation/robust_consciousness_validation.py --runs 5 --cycles 500"
            )
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ ERRO ao testar: {e}")
        import traceback

        traceback.print_exc()

        print(f"\n📋 Logs capturados durante erro ({len(captured_logs)}):")
        for log in captured_logs:
            print(f"   {log}")

        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(test_extended_results())
