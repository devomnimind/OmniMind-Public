#!/usr/bin/env python3
"""
Script auxiliar para dividir data_core em sub-etapas menores.
Executa data_core em lotes menores para evitar timeouts.
"""

import argparse
import subprocess
import sys
from pathlib import Path

# Adicionar src ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))


def get_data_core_subdirs():
    """Retorna lista de subdiretórios em data/ para processamento em lotes."""
    data_dir = project_root / "data"

    # Subdiretórios prioritários (excluindo reports/modules que é massivo)
    priority_subdirs = [
        "alerts",
        "autopoietic",
        "backup",
        "benchmarks",
        "consciousness",
        "context",
        "datasets",
        "ethics",
        "experiments",
        "forensics",
        "integrity_baselines",
        "long_term_logs",
        "metrics",
        "ml",
        "monitor",
        "qdrant",
        "reports",
        "research",
        "sessions",
        "stimulation",
        "training",
        "validation",
    ]

    existing_subdirs = []
    for subdir in priority_subdirs:
        full_path = data_dir / subdir
        if full_path.exists() and full_path.is_dir():
            existing_subdirs.append(subdir)

    return existing_subdirs


def run_data_core_batch(batch_name: str, max_workers: int = 2, cycle_range: tuple = None):
    """Executa um lote específico de data_core."""
    print(f"\n🚀 Executando lote data_core: {batch_name}")
    if cycle_range:
        print(f"   Intervalo de ciclos: {cycle_range[0]} - {cycle_range[1]}")

    cmd = [
        sys.executable,
        "run_indexing.py",
        "--stages",
        f"data_core_{batch_name}",
        "--max-workers",
        str(max_workers),
        "--min-file-size",
        "50",
        "--gpu-memory-threshold",
        "1000",
        "--batch-size",
        "32",
    ]

    # Adicionar parâmetros de intervalo se especificado
    if cycle_range:
        cmd.extend(["--cycle-min", str(cycle_range[0]), "--cycle-max", str(cycle_range[1])])
        # Para reports_small com intervalos, não marcar como concluída automaticamente
        if batch_name == "reports_small":
            cmd.append("--no-mark-complete")

    try:
        result = subprocess.run(cmd, cwd=project_root, timeout=300)  # 5 minutos timeout
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout no lote {batch_name} (5 minutos)")
        return False
    except KeyboardInterrupt:
        print(f"\n⏹️ Lote {batch_name} interrompido pelo usuário")
        return False
    except Exception as e:
        print(f"❌ Erro no lote {batch_name}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Dividir data_core em sub-etapas")
    parser.add_argument("--batch", help="Executar um lote específico")
    parser.add_argument("--list", action="store_true", help="Listar lotes disponíveis")
    parser.add_argument("--max-workers", type=int, default=2, help="Workers por lote")
    parser.add_argument("--cycle-min", type=int, help="Número mínimo do ciclo para reports_small")
    parser.add_argument("--cycle-max", type=int, help="Número máximo do ciclo para reports_small")

    args = parser.parse_args()

    subdirs = get_data_core_subdirs()

    if args.list:
        print("📋 Lotes disponíveis para data_core:")
        for i, subdir in enumerate(subdirs):
            print(f"  {i+1}. data_core_{subdir}")
        print(f"  {len(subdirs)+1}. data_core_reports_small (exceto modules)")
        print("  Para reports_small, use --cycle-min e --cycle-max para intervalos")
        return

    if args.batch:
        if args.batch.startswith("data_core_"):
            batch_name = args.batch[10:]  # Remove prefixo
        else:
            batch_name = args.batch

        # Definir intervalo de ciclos se especificado
        cycle_range = None
        if args.cycle_min is not None and args.cycle_max is not None:
            cycle_range = (args.cycle_min, args.cycle_max)

        # Lotes especiais
        if batch_name == "reports_small":
            # Processa reports excluindo modules, com intervalo opcional
            success = run_data_core_batch("reports_small", args.max_workers, cycle_range)
        elif batch_name in subdirs:
            # Processa subdiretório específico
            success = run_data_core_batch(batch_name, args.max_workers)
        else:
            print(f"❌ Lote desconhecido: {batch_name}")
            return

        if success:
            print(f"✅ Lote {args.batch} concluído!")
        else:
            print(f"❌ Lote {args.batch} falhou!")
            sys.exit(1)

    else:
        # Executar todos os lotes
        print("🚀 Executando data_core em lotes menores...")
        print(f"📋 Lotes: {len(subdirs)} subdiretórios + reports_small")

        failed_batches = []

        # Primeiro os subdiretórios individuais
        for subdir in subdirs:
            if subdir == "reports":
                # Reports será feito separadamente como reports_small
                continue

            success = run_data_core_batch(subdir, args.max_workers)
            if not success:
                failed_batches.append(f"data_core_{subdir}")
                print(f"⚠️ Lote data_core_{subdir} falhou, continuando...")

        # Depois reports_small (excluindo modules)
        success = run_data_core_batch("reports_small", args.max_workers)
        if not success:
            failed_batches.append("data_core_reports_small")

        if failed_batches:
            print(f"\n❌ Lotes que falharam: {', '.join(failed_batches)}")
            sys.exit(1)
        else:
            print("\n🎉 Todos os lotes de data_core concluídos!")


if __name__ == "__main__":
    main()
