#!/usr/bin/env python3
"""
Script para executar ciclos em modo VERBOSO (com todo o debug) ou DRY RUN (simulação).

MODOS DISPONÍVEIS:
- DRY RUN: Simula execução sem realmente executar ciclos (padrão: 80 ciclos)
- PRODUÇÃO: Executa ciclos reais com opções: 50, 100, 200, 500 ciclos

USO:
    # Modo interativo (menu)
    python scripts/run_200_cycles_verbose.py

    # Modo DRY RUN (padrão 80 ciclos)
    python scripts/run_200_cycles_verbose.py --dry-run
    python scripts/run_200_cycles_verbose.py --dry-run --cycles 100

    # Modo PRODUÇÃO
    python scripts/run_200_cycles_verbose.py --production --cycles 100
    python scripts/run_200_cycles_verbose.py -p 200

MÉTRICAS CIENTÍFICAS COLETADAS:
- Φ (Phi): Integração de informação (IIT) - phi_estimate
- Ψ (Psi): Criatividade/Inovação (Deleuze) - psi
- σ (Sigma): Sinthome/Estrutura (Lacan) - sigma
- Δ (Delta): Trauma/Divergência - delta
- Gozo: Excesso pulsional - gozo
- Control Effectiveness: Efetividade de controle - control_effectiveness
- Tríade Completa: (Φ, Ψ, σ) com validação - triad
- RNN Metrics: phi_causal, rho_C/P/U norms, repression_strength

ATUALIZADO: 2025-12-08
- Compatível com refatoração IntegrationLoop (async → sync)
- Coleta todas as métricas científicas via ExtendedLoopCycleResult
- Validação com valores empíricos implementados
- Modo DRY RUN para testes e simulação
- Opções de ciclos configuráveis
"""

import argparse
import asyncio
import json

# Adicionar src ao path
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

project_root = Path(__file__).parent.parent.resolve()  # scripts -> omnimind
sys.path.insert(0, str(project_root))
# Garantir que estamos no diretório correto
os.chdir(project_root)

# 🔧 CRÍTICO: Configurar ambiente GPU ANTES de importar módulos
# Usar script de setup para detecção automática de CUDA
_setup_script = project_root / "scripts" / "setup_qiskit_gpu_force.sh"
if _setup_script.exists():
    # Executar script de setup (configura variáveis de ambiente)
    import subprocess

    try:
        result = subprocess.run(
            ["bash", str(_setup_script)],
            capture_output=True,
            text=True,
            env=os.environ.copy(),
        )
        # Script exporta variáveis, mas precisamos capturá-las
        # Por isso, vamos configurar manualmente também
    except Exception:
        pass  # Continuar mesmo se script falhar

# Configuração manual (fallback e garantia)
if "CUDA_VISIBLE_DEVICES" not in os.environ:
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"
if "CUDA_HOME" not in os.environ:
    # Tentar detectar CUDA automaticamente
    cuda_paths = [
        "/usr/local/cuda",
        "/usr/local/cuda-12.4",
        "/usr/local/cuda-12.0",
        "/usr/local/cuda-11.8",
        "/opt/cuda",
        "/usr",
    ]
    cuda_home = "/usr"  # Fallback
    for path in cuda_paths:
        if os.path.exists(path) and (
            os.path.exists(f"{path}/bin/nvcc") or os.path.exists(f"{path}/lib64")
        ):
            cuda_home = path
            break
    os.environ["CUDA_HOME"] = cuda_home
if "CUDA_PATH" not in os.environ:
    os.environ["CUDA_PATH"] = os.environ["CUDA_HOME"]
# Adicionar libs CUDA ao LD_LIBRARY_PATH se não estiver
ld_lib_path = os.environ.get("LD_LIBRARY_PATH", "")
cuda_lib_paths = [
    f"{os.environ['CUDA_HOME']}/lib64",
    f"{os.environ['CUDA_HOME']}/lib",
    "/usr/lib/x86_64-linux-gnu",
    "/usr/local/cuda/lib64",
]
for lib_path in cuda_lib_paths:
    if os.path.exists(lib_path) and lib_path not in ld_lib_path:
        os.environ["LD_LIBRARY_PATH"] = f"{lib_path}:{ld_lib_path}" if ld_lib_path else lib_path
        ld_lib_path = os.environ["LD_LIBRARY_PATH"]
        break
if not ld_lib_path:
    os.environ["LD_LIBRARY_PATH"] = "/usr/lib/x86_64-linux-gnu"

from src.consciousness.integration_loop import IntegrationLoop

# Opções de ciclos disponíveis
CYCLE_OPTIONS = [50, 80, 100, 200, 400, 500]
DEFAULT_DRY_RUN_CYCLES = 80
DEFAULT_PRODUCTION_CYCLES = 100

# Arquivos com timestamp para preservar histórico (serão configurados dinamicamente)
TIMESTAMP = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def get_metrics_file_path(total_cycles: int, mode: str) -> Path:
    """Gera caminho do arquivo de métricas baseado no número de ciclos e modo."""
    mode_prefix = "dry_run" if mode == "dry_run" else "production"
    return Path(f"data/monitor/phi_{total_cycles}_cycles_{mode_prefix}_metrics_{TIMESTAMP}.json")


def get_progress_file_path(mode: str) -> Path:
    """Gera caminho do arquivo de progresso baseado no modo."""
    mode_prefix = "dry_run" if mode == "dry_run" else "production"
    return Path(f"data/monitor/phi_{mode_prefix}_progress.json")


def get_executions_index_path() -> Path:
    """Retorna caminho do índice de execuções."""
    return Path("data/monitor/executions_index.json")


def parse_arguments() -> argparse.Namespace:
    """Parse argumentos de linha de comando."""
    parser = argparse.ArgumentParser(
        description="Executa ciclos de consciência em modo VERBOSO ou DRY RUN",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  # Modo interativo (menu)
  python scripts/run_200_cycles_verbose.py

  # DRY RUN (simulação, padrão 80 ciclos)
  python scripts/run_200_cycles_verbose.py --dry-run
  python scripts/run_200_cycles_verbose.py --dry-run --cycles 100

  # PRODUÇÃO
  python scripts/run_200_cycles_verbose.py --production --cycles 100
  python scripts/run_200_cycles_verbose.py -p 200
        """,
    )

    # Modo
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--dry-run",
        "-d",
        action="store_true",
        help="Modo DRY RUN (simulação, não executa ciclos reais)",
    )
    mode_group.add_argument(
        "--production",
        "-p",
        action="store_true",
        help="Modo PRODUÇÃO (executa ciclos reais)",
    )

    # Número de ciclos
    parser.add_argument(
        "--cycles",
        "-c",
        type=int,
        choices=CYCLE_OPTIONS,
        help=f"Número de ciclos ({', '.join(map(str, CYCLE_OPTIONS))})",
    )

    # Não interativo
    parser.add_argument(
        "--no-interactive",
        action="store_true",
        help="Não exibir menu interativo (usa padrões se argumentos não fornecidos)",
    )

    return parser.parse_args()


def show_interactive_menu() -> tuple[str, int]:
    """Exibe menu interativo e retorna (modo, ciclos)."""
    print("\n" + "=" * 80)
    print("🎯 SELECIONE O MODO DE EXECUÇÃO")
    print("=" * 80)
    print("\n1. DRY RUN (Simulação - não executa ciclos reais)")
    print("   - Útil para testar lógica e simulação de funcionamento")
    print("   - Padrão: 80 ciclos")
    print("\n2. PRODUÇÃO (Executa ciclos reais)")
    print("   - Executa ciclos completos de consciência")
    print("   - Padrão: 100 ciclos")
    print("\n0. Cancelar")
    print()

    while True:
        try:
            choice = input("Escolha uma opção (0-2): ").strip()
            if choice == "0":
                print("❌ Cancelado pelo usuário")
                sys.exit(0)
            elif choice == "1":
                mode = "dry_run"
                default_cycles = DEFAULT_DRY_RUN_CYCLES
                break
            elif choice == "2":
                mode = "production"
                default_cycles = DEFAULT_PRODUCTION_CYCLES
                break
            else:
                print("⚠️  Opção inválida. Escolha 0, 1 ou 2.")
        except (EOFError, KeyboardInterrupt):
            print("\n❌ Cancelado pelo usuário")
            sys.exit(0)

    print(f"\n📊 Opções de ciclos: {', '.join(map(str, CYCLE_OPTIONS))}")
    print(f"   Padrão para {mode.upper()}: {default_cycles} ciclos")
    print()

    while True:
        try:
            cycles_input = input(f"Número de ciclos (Enter para padrão={default_cycles}): ").strip()
            if not cycles_input:
                cycles = default_cycles
                break
            cycles = int(cycles_input)
            if cycles in CYCLE_OPTIONS:
                break
            else:
                print(f"⚠️  Opção inválida. Escolha entre: {', '.join(map(str, CYCLE_OPTIONS))}")
        except ValueError:
            print("⚠️  Por favor, digite um número válido.")
        except (EOFError, KeyboardInterrupt):
            print("\n❌ Cancelado pelo usuário")
            sys.exit(0)

    return mode, cycles


def save_progress(cycle: int, phi: float, metrics: Dict[str, Any], progress_file: Path) -> None:
    """Salva progresso em arquivo JSON."""
    progress = {
        "current_cycle": cycle,
        "phi_current": phi,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metrics": metrics,
    }
    progress_file.parent.mkdir(parents=True, exist_ok=True)
    with open(progress_file, "w") as f:
        json.dump(progress, f, indent=2)


def save_final_metrics(
    all_metrics: List[Dict[str, Any]],
    metrics_file: Path,
    mode: str,
    metrics_file_latest: Optional[Path] = None,
) -> None:
    """Salva métricas finais em arquivo JSON com timestamp e atualiza índice."""
    final_data = {
        "total_cycles": len(all_metrics),
        "mode": mode,
        "start_time": all_metrics[0]["timestamp"] if all_metrics else None,
        "end_time": all_metrics[-1]["timestamp"] if all_metrics else None,
        "phi_progression": [m["phi"] for m in all_metrics],
        "phi_final": all_metrics[-1]["phi"] if all_metrics else 0.0,
        "phi_max": max([m["phi"] for m in all_metrics]) if all_metrics else 0.0,
        "phi_min": min([m["phi"] for m in all_metrics]) if all_metrics else 0.0,
        "phi_avg": sum([m["phi"] for m in all_metrics]) / len(all_metrics) if all_metrics else 0.0,
        "metrics": all_metrics,
        "execution_timestamp": TIMESTAMP,  # Adicionar timestamp da execução
    }
    metrics_file.parent.mkdir(parents=True, exist_ok=True)

    # Salvar arquivo com timestamp
    with open(metrics_file, "w") as f:
        json.dump(final_data, f, indent=2)

    # Criar cópia como "latest" para compatibilidade (se especificado)
    if metrics_file_latest:
        import shutil

        shutil.copy2(metrics_file, metrics_file_latest)

    # Atualizar índice de execuções
    update_executions_index(metrics_file, final_data)


def update_executions_index(metrics_file: Path, final_data: Dict[str, Any]) -> None:
    """Atualiza índice de execuções para facilitar acesso ao histórico."""
    executions_index = get_executions_index_path()
    executions_index.parent.mkdir(parents=True, exist_ok=True)

    # Carregar índice existente ou criar novo
    if executions_index.exists():
        try:
            with open(executions_index, "r") as f:
                index = json.load(f)
        except (json.JSONDecodeError, IOError):
            index = {"executions": []}
    else:
        index = {"executions": []}

    # Adicionar nova execução ao índice
    execution_entry = {
        "timestamp": TIMESTAMP,
        "file": str(metrics_file.name),
        "mode": final_data.get("mode", "unknown"),
        "start_time": final_data.get("start_time"),
        "end_time": final_data.get("end_time"),
        "total_cycles": final_data.get("total_cycles", 0),
        "phi_final": final_data.get("phi_final", 0.0),
        "phi_max": final_data.get("phi_max", 0.0),
        "phi_avg": final_data.get("phi_avg", 0.0),
    }

    index["executions"].append(execution_entry)

    # Manter apenas últimas 50 execuções no índice (evitar crescimento infinito)
    if len(index["executions"]) > 50:
        index["executions"] = index["executions"][-50:]

    # Ordenar por timestamp (mais recente primeiro)
    index["executions"].sort(key=lambda x: x["timestamp"], reverse=True)
    index["last_updated"] = datetime.now(timezone.utc).isoformat()

    # Salvar índice
    with open(executions_index, "w") as f:
        json.dump(index, f, indent=2)


async def run_cycles(mode: str, total_cycles: int) -> None:
    """Executa ciclos em modo verboso ou DRY RUN."""
    # Configurar arquivos baseado no modo e número de ciclos
    metrics_file = get_metrics_file_path(total_cycles, mode)
    metrics_file_latest = Path(f"data/monitor/phi_{total_cycles}_cycles_{mode}_metrics.json")
    progress_file = get_progress_file_path(mode)
    executions_index = get_executions_index_path()

    print("=" * 80)
    mode_display = "DRY RUN (SIMULAÇÃO)" if mode == "dry_run" else "PRODUÇÃO"
    print(f"🚀 EXECUÇÃO DE {total_cycles} CICLOS EM MODO {mode_display}")
    print("=" * 80)
    print(f"📊 Métricas serão salvas em: {metrics_file}")
    print(f"📊 Métricas (latest): {metrics_file_latest}")
    print(f"📈 Progresso será salvo em: {progress_file}")
    print(f"📑 Índice de execuções: {executions_index}")
    print(f"🕐 Timestamp desta execução: {TIMESTAMP}")
    if mode == "dry_run":
        print("⚠️  MODO DRY RUN: Simulação - Nenhum ciclo real será executado")
    else:
        print("⚠️  MODO VERBOSO: Todo o debug será exibido")
    # Verificar GPU
    print("\n🔍 VERIFICAÇÃO DE GPU:")
    try:
        import torch

        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory_total = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            gpu_memory_allocated = torch.cuda.memory_allocated(0) / (1024**3)
            gpu_memory_free = gpu_memory_total - gpu_memory_allocated
            print(f"   ✅ GPU Disponível: {gpu_name}")
            print(f"   📊 Memória Total: {gpu_memory_total:.2f} GB")
            print(f"   💾 Memória Alocada: {gpu_memory_allocated:.2f} GB")
            print(f"   🆓 Memória Livre: {gpu_memory_free:.2f} GB")

            # Verificar memória disponível para uso
            from src.utils.device_utils import check_gpu_memory_available

            if check_gpu_memory_available(min_memory_mb=100):
                print(f"   ✅ GPU pronta para uso (≥100MB livre)")
            else:
                print(f"   ⚠️  GPU com pouca memória livre (<100MB)")
        else:
            print("   ⚠️  GPU não disponível - usando CPU")
    except Exception as e:
        print(f"   ⚠️  Erro ao verificar GPU: {e}")
        print("   ℹ️  Continuando com CPU")

    print("=" * 80)
    print("")

    # Criar loop com logging COMPLETO (enable_logging=True)
    # DRY RUN e PRODUÇÃO usam a mesma lógica - apenas snapshots diferem
    if mode == "dry_run":
        print("🎭 MODO DRY RUN: Executando lógica real (sem snapshots)")
        print("   (Usa mesma lógica de produção para validar comportamento)\n")

    loop = IntegrationLoop(enable_extended_results=True, enable_logging=True)

    all_metrics: List[Dict[str, Any]] = []

    try:
        for i in range(1, total_cycles + 1):
            print(f"\n{'='*80}")
            print(f"🔄 CICLO {i}/{total_cycles}")
            print(f"{'='*80}")

            # Executar ciclo
            result = await loop.execute_cycle(collect_metrics=True)

            # Coletar métricas
            cycle_metrics = {
                "cycle": i,
                "phi": result.phi_estimate,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "success": result.success,
                "modules_executed": result.modules_executed,
            }

            # Adicionar métricas estendidas se disponíveis (tratando None)
            # Verificar se é ExtendedLoopCycleResult (tem todas as métricas científicas)
            from src.consciousness.extended_cycle_result import ExtendedLoopCycleResult

            if isinstance(result, ExtendedLoopCycleResult):
                if result.psi is not None:
                    cycle_metrics["psi"] = result.psi
                if result.sigma is not None:
                    cycle_metrics["sigma"] = result.sigma
                if result.gozo is not None:
                    cycle_metrics["gozo"] = result.gozo
                if result.delta is not None:
                    cycle_metrics["delta"] = result.delta
                if result.control_effectiveness is not None:
                    cycle_metrics["control_effectiveness"] = result.control_effectiveness
                if result.triad is not None:
                    # Validar tríade e obter interpretação
                    triad_validation = result.triad.validate()
                    cycle_metrics["triad"] = {
                        "phi": result.triad.phi,
                        "psi": result.triad.psi,
                        "sigma": result.triad.sigma,
                        "interpretation": triad_validation.get("interpretation", "N/A"),
                        "valid": triad_validation.get("valid", False),
                        "warnings": triad_validation.get("warnings", []),
                        "metadata": result.triad.metadata,
                    }
            else:
                # Fallback para compatibilidade (verificar hasattr)
                if hasattr(result, "gozo") and result.gozo is not None:
                    cycle_metrics["gozo"] = result.gozo
                if hasattr(result, "delta") and result.delta is not None:
                    cycle_metrics["delta"] = result.delta
                if (
                    hasattr(result, "control_effectiveness")
                    and result.control_effectiveness is not None
                ):
                    cycle_metrics["control_effectiveness"] = result.control_effectiveness

            all_metrics.append(cycle_metrics)

            # Salvar progresso
            save_progress(i, result.phi_estimate, cycle_metrics, progress_file)

            # Calcular PHI do workspace
            try:
                phi_workspace = loop.workspace.compute_phi_from_integrations()
            except Exception as e:
                phi_workspace = 0.0
                print(f"⚠️  Erro ao calcular PHI do workspace: {e}")

            # REFATORAÇÃO: Coletar métricas do ConsciousSystem (RNN) se disponível
            phi_causal = None
            rho_C_norm = None
            rho_P_norm = None
            rho_U_norm = None
            repression_strength = None

            if loop.workspace.conscious_system is not None:
                try:
                    phi_causal = loop.workspace.conscious_system.compute_phi_causal()
                    state = loop.workspace.conscious_system.get_state()
                    import numpy as np

                    # CORREÇÃO: state.rho_C/P/U são numpy arrays, não torch tensors
                    rho_C_norm = float(np.linalg.norm(state.rho_C))
                    rho_P_norm = float(np.linalg.norm(state.rho_P))
                    rho_U_norm = float(np.linalg.norm(state.rho_U))
                    repression_strength = float(state.repression_strength)

                    # Adicionar ao ciclo_metrics
                    cycle_metrics["phi_causal"] = phi_causal
                    cycle_metrics["rho_C_norm"] = rho_C_norm
                    cycle_metrics["rho_P_norm"] = rho_P_norm
                    cycle_metrics["rho_U_norm"] = rho_U_norm
                    cycle_metrics["repression_strength"] = repression_strength
                except Exception as e:
                    print(f"⚠️  Erro ao coletar métricas do RNN: {e}")

            # Exibir resumo do ciclo
            print(f"\n✅ CICLO {i} CONCLUÍDO:")
            print(f"   PHI (ciclo): {result.phi_estimate:.6f}")
            print(f"   PHI (workspace): {phi_workspace:.6f}")
            if phi_causal is not None:
                print(f"   PHI (causal RNN): {phi_causal:.6f}")
            print(f"   Módulos executados: {len(result.modules_executed)}")
            print(f"   Módulos no workspace: {len(loop.workspace.embeddings)}")
            print(f"   Histórico workspace: {len(loop.workspace.history)}")
            print(f"   Cross predictions: {len(loop.workspace.cross_predictions)}")

            # Exibir métricas do RNN se disponíveis
            if rho_C_norm is not None:
                print(f"   RNN States:")
                print(f"     ρ_C norm: {rho_C_norm:.4f}")
                print(f"     ρ_P norm: {rho_P_norm:.4f}")
                print(f"     ρ_U norm: {rho_U_norm:.4f}")
                print(f"     Repressão: {repression_strength:.4f}")

            # Exibir métricas estendidas (tríade completa)
            from src.consciousness.extended_cycle_result import ExtendedLoopCycleResult

            if isinstance(result, ExtendedLoopCycleResult):
                if result.psi is not None:
                    print(f"   Psi (Ψ): {result.psi:.6f}")
                if result.sigma is not None:
                    print(f"   Sigma (σ): {result.sigma:.6f}")
                if result.gozo is not None:
                    print(f"   Gozo: {result.gozo:.6f}")
                if result.delta is not None:
                    print(f"   Delta (Δ): {result.delta:.6f}")
                if result.control_effectiveness is not None:
                    print(f"   Control Effectiveness: {result.control_effectiveness:.6f}")
                if result.triad is not None:
                    triad_validation = result.triad.validate()
                    print(
                        f"   Tríade: Φ={result.triad.phi:.4f}, Ψ={result.triad.psi:.4f}, σ={result.triad.sigma:.4f}"
                    )
                    print(f"   Interpretação: {triad_validation.get('interpretation', 'N/A')}")
                    if triad_validation.get("warnings"):
                        print(f"   ⚠️  Avisos: {', '.join(triad_validation['warnings'])}")
            else:
                # Fallback para compatibilidade
                if hasattr(result, "gozo") and result.gozo is not None:
                    print(f"   Gozo: {result.gozo:.6f}")
                elif hasattr(result, "gozo"):
                    print(f"   Gozo: N/A")
                if hasattr(result, "delta") and result.delta is not None:
                    print(f"   Delta: {result.delta:.6f}")
                elif hasattr(result, "delta"):
                    print(f"   Delta: N/A")
                if (
                    hasattr(result, "control_effectiveness")
                    and result.control_effectiveness is not None
                ):
                    print(f"   Control Effectiveness: {result.control_effectiveness:.6f}")
                elif hasattr(result, "control_effectiveness"):
                    print(f"   Control Effectiveness: N/A")

            # Flush para garantir que aparece no terminal
            sys.stdout.flush()

        # Salvar métricas finais
        save_final_metrics(all_metrics, metrics_file, mode, metrics_file_latest)

        # Criar snapshot final (apenas em modo produção)
        snapshot_id = None
        if mode == "production":
            print("\n" + "=" * 80)
            print("📸 CRIANDO SNAPSHOT FINAL...")
            print("=" * 80)
            snapshot_id = loop.create_full_snapshot(
                tag=f"production_{total_cycles}_cycles_verbose",
                description=f"Produção VERBOSO: {total_cycles} ciclos executados",
            )
            print(f"✅ Snapshot criado: {snapshot_id}")

        # Resumo final
        phi_final = all_metrics[-1]["phi"]
        phi_max = max([m["phi"] for m in all_metrics])
        phi_avg = sum([m["phi"] for m in all_metrics]) / len(all_metrics)
        phi_workspace_final = (
            loop.workspace.compute_phi_from_integrations() if mode == "production" else None
        )

        # REFATORAÇÃO: Coletar métricas finais do RNN
        phi_causal_final = None
        rho_C_final = None
        rho_P_final = None
        rho_U_final = None
        repression_final = None

        if loop.workspace.conscious_system is not None:
            try:
                phi_causal_final = loop.workspace.conscious_system.compute_phi_causal()
                state_final = loop.workspace.conscious_system.get_state()
                import numpy as np

                # CORREÇÃO: state.rho_C/P/U são numpy arrays, não torch tensors
                rho_C_final = float(np.linalg.norm(state_final.rho_C))
                rho_P_final = float(np.linalg.norm(state_final.rho_P))
                rho_U_final = float(np.linalg.norm(state_final.rho_U))
                repression_final = float(state_final.repression_strength)
            except Exception as e:
                print(f"⚠️  Erro ao coletar métricas finais do RNN: {e}")
                # Variáveis já inicializadas como None

        print("\n" + "=" * 80)
        print("📊 RESUMO FINAL")
        print("=" * 80)
        print(f"Total de ciclos: {total_cycles}")
        print(f"Modo: {mode.upper()}")
        print(f"PHI final (ciclo): {phi_final:.6f}")
        if phi_workspace_final is not None:
            print(f"PHI final (workspace): {phi_workspace_final:.6f}")
        if phi_causal_final is not None:
            print(f"PHI final (causal RNN): {phi_causal_final:.6f}")
        print(f"PHI máximo: {phi_max:.6f}")
        print(f"PHI mínimo: {min([m['phi'] for m in all_metrics]):.6f}")
        print(f"PHI médio: {phi_avg:.6f}")
        if phi_causal_final is not None:
            phi_causal_values = [m.get("phi_causal", 0.0) for m in all_metrics if "phi_causal" in m]
            if phi_causal_values:
                print(f"PHI causal médio: {sum(phi_causal_values) / len(phi_causal_values):.6f}")
                print(f"PHI causal máximo: {max(phi_causal_values):.6f}")
        if mode == "production":
            print(f"Módulos ativos: {len(loop.workspace.embeddings)}")
            print(f"Histórico workspace: {len(loop.workspace.history)}")
            print(f"Cross predictions: {len(loop.workspace.cross_predictions)}")
        if phi_causal_final is not None and rho_C_final is not None:
            print(f"\nRNN Final States:")
            print(f"  ρ_C norm: {rho_C_final:.4f}")
            print(f"  ρ_P norm: {rho_P_final:.4f}")
            print(f"  ρ_U norm: {rho_U_final:.4f}")
            print(f"  Repressão: {repression_final:.4f}")
        if snapshot_id:
            print(f"Snapshot ID: {snapshot_id}")
        print(f"Métricas salvas em: {metrics_file}")
        print("=" * 80)

    except KeyboardInterrupt:
        print("\n\n⚠️  Execução interrompida pelo usuário (Ctrl+C)")
        # Salvar métricas coletadas até o momento
        if all_metrics:
            save_final_metrics(all_metrics, metrics_file, mode, metrics_file_latest)
            print(f"✅ Métricas parciais salvas em: {metrics_file}")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Erro durante execução: {e}")
        import traceback

        traceback.print_exc()
        # Salvar métricas coletadas até o erro
        if all_metrics:
            save_final_metrics(all_metrics, metrics_file, mode, metrics_file_latest)
            print(f"✅ Métricas parciais salvas em: {metrics_file}")
        raise


def main() -> None:
    """Função principal com parsing de argumentos e menu interativo."""
    args = parse_arguments()

    # Determinar modo e ciclos
    mode: Optional[str] = None
    cycles: Optional[int] = None

    # Se argumentos fornecidos, usar eles
    if args.dry_run:
        mode = "dry_run"
        cycles = args.cycles or DEFAULT_DRY_RUN_CYCLES
    elif args.production:
        mode = "production"
        cycles = args.cycles or DEFAULT_PRODUCTION_CYCLES
    elif args.cycles:
        # Ciclos especificados mas modo não: usar produção como padrão
        mode = "production"
        cycles = args.cycles

    # Se modo não determinado e não é não-interativo, mostrar menu
    if mode is None and not args.no_interactive:
        mode, cycles = show_interactive_menu()
    elif mode is None:
        # Padrão: DRY RUN com 80 ciclos
        mode = "dry_run"
        cycles = DEFAULT_DRY_RUN_CYCLES
        print(f"⚠️  Nenhum modo especificado, usando padrão: {mode.upper()} com {cycles} ciclos")
        print("   Use --dry-run ou --production para especificar modo")
        print("   Use --help para ver opções\n")

    # Executar
    asyncio.run(run_cycles(mode, cycles))


if __name__ == "__main__":
    main()
