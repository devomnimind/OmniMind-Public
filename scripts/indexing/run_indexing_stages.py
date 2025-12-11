#!/usr/bin/env python3
"""
Script para indexação incremental por etapas do OmniMind.

Executa a indexação em etapas ordenadas por prioridade:
1. Arquivos principais (src/, tests/, config/, datasets/, deploy/, docs/, archive/)
2. Ruídos controlados (logs principais, node_modules limitados)
3. Dados do sistema (exceto módulos massivos)
4. Arquivos kernel e metadados
5. Dados massivos (última prioridade)

Uso:
    python run_indexing_stages.py                    # Executa todas as etapas pendentes
    python run_indexing_stages.py --stage core_code  # Executa apenas uma etapa específica
    python run_indexing_stages.py --reset            # Reseta e começa do início
    python run_indexing_stages.py --status           # Mostra status das etapas
"""

import argparse
import subprocess
import sys
from pathlib import Path

# Adicionar src ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))


def run_stage(stage_name: str, max_workers: int = 2, min_file_size: int = 50):
    """Executa uma etapa específica da indexação."""
    print(f"\n🚀 Executando etapa: {stage_name}")

    cmd = [
        sys.executable,
        "run_indexing.py",
        "--stages",
        stage_name,
        "--max-workers",
        str(max_workers),
        "--min-file-size",
        str(min_file_size),
        "--gpu-memory-threshold",
        "1000",
        "--batch-size",
        "32",
    ]

    # Configurações específicas por etapa
    if stage_name in ["data_modules"]:
        # Etapa massiva - configurações mais conservadoras
        cmd.extend(["--max-workers", "1", "--batch-size", "16"])
    elif stage_name in ["node_modules_main"]:
        # Node modules - pular patterns adicionais
        cmd.extend(["--skip-node-modules"])

    try:
        result = subprocess.run(cmd, cwd=project_root)
        return result.returncode == 0
    except KeyboardInterrupt:
        print(f"\n⏹️ Etapa {stage_name} interrompida pelo usuário")
        return False
    except Exception as e:
        print(f"❌ Erro na etapa {stage_name}: {e}")
        return False


def show_status():
    """Mostra status das etapas concluídas."""
    checkpoint_file = project_root / ".omnimind_embedding_checkpoint.json"

    if not checkpoint_file.exists():
        print("📋 Nenhuma etapa concluída ainda (checkpoint não encontrado)")
        return

    try:
        import json

        with open(checkpoint_file, "r") as f:
            data = json.load(f)

        completed = set(data.get("completed_stages", []))
        total_chunks = data.get("total_chunks", 0)
        timestamp = data.get("timestamp", "unknown")

        print(f"📊 Status da indexação (última atualização: {timestamp})")
        print(f"✅ Etapas concluídas: {len(completed)}")
        print(f"📈 Total de chunks: {total_chunks}")
        print("\nEtapas concluídas:")
        for stage in sorted(completed):
            chunks = data.get("results_summary", {}).get(stage, 0)
            print(f"  ✅ {stage}: {chunks} chunks")

    except Exception as e:
        print(f"❌ Erro ao ler checkpoint: {e}")


def main():
    parser = argparse.ArgumentParser(description="Indexação incremental por etapas")
    parser.add_argument("--stage", help="Executar apenas uma etapa específica")
    parser.add_argument(
        "--reset", action="store_true", help="Resetar checkpoint e começar do início"
    )
    parser.add_argument("--status", action="store_true", help="Mostrar status das etapas")
    parser.add_argument(
        "--max-workers", type=int, default=2, help="Número máximo de workers (padrão: 2)"
    )

    args = parser.parse_args()

    if args.status:
        show_status()
        return

    if args.reset:
        checkpoint_file = project_root / ".omnimind_embedding_checkpoint.json"
        if checkpoint_file.exists():
            checkpoint_file.unlink()
            print("🗑️ Checkpoint resetado!")
        else:
            print("ℹ️ Nenhum checkpoint encontrado")
        return

    # Ordem de prioridade das etapas
    stage_order = [
        # Etapa 1: Arquivos principais do projeto (sem ruídos)
        "core_code",  # Código fonte principal
        "tests",  # Testes
        "scripts",  # Scripts
        "configs",  # Configurações
        "datasets",  # Datasets
        "deploy",  # Deploy
        "docs",  # Documentação
        "archive",  # Arquivo
        # Etapa 2: Ruídos controlados
        "logs_main",  # Logs principais
        "node_modules_main",  # Node modules principais (limitado)
        # Etapa 3: Dados produzidos pelo sistema
        "data_core",  # Dados core (exceto módulos massivos)
        "data_reports",  # Relatórios
        # Etapa 4: Arquivos kernel e sistema
        "kernel_files",  # Arquivos kernel
        "system_metadata",  # Metadados do sistema
        # Etapa 5: Dados massivos (última prioridade)
        "data_modules",  # Módulos de dados (massivo)
        "exports",  # Exports
        "tmp",  # Temporários
    ]

    if args.stage:
        # Executar apenas uma etapa
        if args.stage not in stage_order:
            print(f"❌ Etapa desconhecida: {args.stage}")
            print(f"📋 Etapas disponíveis: {', '.join(stage_order)}")
            return

        success = run_stage(args.stage, args.max_workers)
        if success:
            print(f"✅ Etapa {args.stage} concluída com sucesso!")
        else:
            print(f"❌ Etapa {args.stage} falhou!")
            sys.exit(1)

    else:
        # Executar todas as etapas pendentes
        print("🚀 Iniciando indexação incremental por etapas...")
        print(f"📋 Ordem das etapas: {' -> '.join(stage_order)}")
        print(f"⚙️ Configuração: {args.max_workers} workers, min_file_size=50")

        failed_stages = []

        for stage in stage_order:
            success = run_stage(stage, args.max_workers)
            if not success:
                failed_stages.append(stage)
                print(f"⚠️ Etapa {stage} falhou, continuando com próximas...")

        if failed_stages:
            print(f"\n❌ Etapas que falharam: {', '.join(failed_stages)}")
            sys.exit(1)
        else:
            print("\n🎉 Todas as etapas concluídas com sucesso!")


if __name__ == "__main__":
    main()
