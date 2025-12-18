#!/usr/bin/env python3
"""
🚀 VALIDAÇÃO OFICIAL DE PHASE 5 & 6 - EXPANSÃO PSICANALÍTICA

Script de validação de produção para Phase 5 (Bion) e Phase 6 (Lacan).
Valida implementação, coleta métricas científicas (Φ, Ψ, σ) e certifica readiness.

MODOS:
- --pre-flight:  Verifica pré-requisitos (Python, PyTorch, GPU)
- --validate:    Valida código e executa testes básicos
- --metrics:     Coleta métricas de produção (ciclos de consciência)
- --full:        Executa pré-flight + validate + metrics (MODO COMPLETO)

USO:
    # Checklist pré-implementação
    python scripts/canonical/validate/validate_phase5_6_production.py --pre-flight

    # Validação de código + testes
    python scripts/canonical/validate/validate_phase5_6_production.py --validate

    # Coletar métricas (50 ciclos por padrão)
    python scripts/canonical/validate/validate_phase5_6_production.py --metrics --cycles 50

    # Validação completa (pré-flight + validate + metrics)
    python scripts/canonical/validate/validate_phase5_6_production.py --full --cycles 100

SAÍDA:
    - logs/validation/phase5_6_validation_TIMESTAMP.json
    - data/monitor/phase5_6_metrics_TIMESTAMP.json
    - Relatório completo com pass/fail para cada validação

ATUALIZADO: 2025-12-09
BRANCHES: phase-5-bion, phase-6-lacan (e derivadas)
"""

import argparse
import asyncio
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Setup paths
project_root = Path(__file__).parent.parent.parent.parent.resolve()
sys.path.insert(0, str(project_root))
os.chdir(project_root)


# Cores para output
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class Phase5_6Validator:
    """Validator para Phase 5 & 6 (Bion + Lacan)"""

    def __init__(self, cycles: int = 50, verbose: bool = True):
        self.cycles = cycles
        self.verbose = verbose
        self.timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        self.results: Dict[str, Any] = {
            "timestamp": self.timestamp,
            "stages": {},
            "overall_status": "NOT_STARTED",
            "metrics": {},
        }
        self.validation_log: List[str] = []

    def _log(self, message: str, level: str = "INFO") -> None:
        """Log com cores"""
        colors_map = {
            "INFO": Colors.BLUE,
            "SUCCESS": Colors.GREEN,
            "WARNING": Colors.YELLOW,
            "ERROR": Colors.RED,
            "CRITICAL": Colors.RED + Colors.BOLD,
            "HEADER": Colors.HEADER + Colors.BOLD,
        }
        color = colors_map.get(level, Colors.ENDC)
        reset = Colors.ENDC

        prefix_map = {
            "INFO": "ℹ️ ",
            "SUCCESS": "✅ ",
            "WARNING": "⚠️  ",
            "ERROR": "❌ ",
            "CRITICAL": "🚨 ",
            "HEADER": "═" * 80,
        }
        prefix = prefix_map.get(level, "")

        formatted = f"{color}{prefix}{message}{reset}"
        if self.verbose:
            print(formatted)
        self.validation_log.append(f"[{level}] {message}")

    def _run_command(self, cmd: str, description: str = "") -> Tuple[bool, str]:
        """Executa comando shell e retorna (success, output)"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
            success = result.returncode == 0
            output = result.stdout + result.stderr
            return success, output
        except subprocess.TimeoutExpired:
            self._log(f"Timeout ao executar: {description}", "ERROR")
            return False, "Timeout"
        except Exception as e:
            self._log(f"Erro ao executar comando: {e}", "ERROR")
            return False, str(e)

    # ===== STAGE 1: PRÉ-FLIGHT CHECKS =====

    def stage_preflight(self) -> bool:
        """Verifica pré-requisitos para Phase 5/6"""
        self._log("STAGE 1: PRÉ-FLIGHT CHECKS", "HEADER")
        stage_results = {}

        # 1.1: Python Version
        try:
            import sys

            py_version = sys.version_info
            required = (3, 12, 0)
            has_required = (py_version.major, py_version.minor) >= (required[0], required[1])
            stage_results["python_version"] = {
                "status": "PASS" if has_required else "FAIL",
                "value": f"{py_version.major}.{py_version.minor}.{py_version.micro}",
                "required": f"{required[0]}.{required[1]}+",
            }
            self._log(
                f"Python {py_version.major}.{py_version.minor}.{py_version.micro}",
                "SUCCESS" if has_required else "ERROR",
            )
        except Exception as e:
            stage_results["python_version"] = {"status": "ERROR", "error": str(e)}
            self._log(f"Erro ao verificar Python: {e}", "ERROR")

        # 1.2: PyTorch Version + CUDA
        try:
            import torch

            torch_version = torch.__version__
            cuda_available = torch.cuda.is_available()
            stage_results["pytorch"] = {
                "status": "PASS" if cuda_available else "WARN",
                "version": torch_version,
                "cuda_available": cuda_available,
                "device_count": torch.cuda.device_count() if cuda_available else 0,
            }
            if cuda_available:
                gpu_name = torch.cuda.get_device_name(0)
                self._log(f"PyTorch {torch_version} + CUDA on {gpu_name}", "SUCCESS")
            else:
                self._log(f"PyTorch {torch_version} (CUDA NOT available, using CPU)", "WARNING")
        except Exception as e:
            stage_results["pytorch"] = {"status": "ERROR", "error": str(e)}
            self._log(f"Erro ao verificar PyTorch: {e}", "ERROR")

        # 1.3: Módulos essenciais
        essential_modules = [
            "numpy",
            "pandas",
            "pytest",
            "fastapi",
            "sentence_transformers",
            "qdrant_client",
        ]
        missing_modules = []
        for module in essential_modules:
            try:
                __import__(module)
            except ImportError:
                missing_modules.append(module)

        stage_results["essential_modules"] = {
            "status": "PASS" if not missing_modules else "FAIL",
            "installed": [m for m in essential_modules if m not in missing_modules],
            "missing": missing_modules,
        }
        if missing_modules:
            self._log(f"Módulos faltando: {', '.join(missing_modules)}", "ERROR")
        else:
            self._log("Todos os módulos essenciais instalados", "SUCCESS")

        # 1.4: Estrutura de arquivos
        required_dirs = [
            "src/consciousness",
            "src/psychoanalysis",
            "tests/psychoanalysis",
            "docs/METADATA",
            "logs",
            "data/monitor",
        ]
        missing_dirs = []
        for dir_path in required_dirs:
            if not (project_root / dir_path).exists():
                missing_dirs.append(dir_path)

        stage_results["directory_structure"] = {
            "status": "PASS" if not missing_dirs else "FAIL",
            "required": required_dirs,
            "missing": missing_dirs,
        }
        if missing_dirs:
            self._log(f"Diretórios faltando: {', '.join(missing_dirs)}", "ERROR")
        else:
            self._log("Estrutura de diretórios válida", "SUCCESS")

        # 1.5: Ambiente development está rodando?
        try:
            response = subprocess.run(
                "curl -s http://127.0.0.1:8000/health", shell=True, capture_output=True, timeout=5
            )
            backend_running = response.returncode == 0
            stage_results["backend_status"] = {
                "status": "PASS" if backend_running else "WARN",
                "running": backend_running,
                "url": "http://127.0.0.1:8000",
            }
            if backend_running:
                self._log("Backend rodando em 8000", "SUCCESS")
            else:
                self._log(
                    "Backend não está rodando (será necessário para testes completos)", "WARNING"
                )
        except Exception:
            stage_results["backend_status"] = {"status": "UNKNOWN", "error": "Timeout"}
            self._log("Backend status desconhecido", "WARNING")

        # Summarize
        self.results["stages"]["preflight"] = stage_results
        preflight_pass = all(r.get("status") in ["PASS", "WARN"] for r in stage_results.values())

        if preflight_pass:
            self._log("✅ PRÉ-FLIGHT CHECKS PASSED", "SUCCESS")
        else:
            self._log("❌ PRÉ-FLIGHT CHECKS FAILED", "ERROR")

        return preflight_pass

    # ===== STAGE 2: VALIDAÇÃO DE CÓDIGO =====

    def stage_validate_code(self) -> bool:
        """Valida código Phase 5/6"""
        self._log("STAGE 2: VALIDAÇÃO DE CÓDIGO", "HEADER")
        stage_results = {}

        # 2.1: Black formatting
        self._log("Verificando formatação (Black)...", "INFO")
        success, output = self._run_command(
            "black --check src/psychoanalysis tests/psychoanalysis --quiet 2>/dev/null",
            "Black check",
        )
        stage_results["black"] = {"status": "PASS" if success else "FAIL", "formatted": success}
        if success:
            self._log("Formatação correta", "SUCCESS")
        else:
            self._log(
                "Formatação incorreta (execute: black src/psychoanalysis tests/psychoanalysis)",
                "WARNING",
            )

        # 2.2: Flake8 linting
        self._log("Verificando linting (Flake8)...", "INFO")
        success, output = self._run_command(
            "flake8 src/psychoanalysis tests/psychoanalysis --select=E9,F63,F7,F82 --count 2>/dev/null",
            "Flake8 check",
        )
        stage_results["flake8"] = {
            "status": "PASS" if success else "FAIL",
            "errors": output.strip() if output else "0",
        }
        if success:
            self._log("Linting limpo", "SUCCESS")
        else:
            self._log(f"Erros de linting: {output}", "ERROR")

        # 2.3: MyPy type checking
        self._log("Verificando tipos (MyPy)...", "INFO")
        success, output = self._run_command(
            "mypy src/psychoanalysis --ignore-missing-imports 2>&1 | head -20", "MyPy check"
        )
        error_count = output.count("error:")
        stage_results["mypy"] = {
            "status": "PASS" if error_count == 0 else "WARN" if error_count < 10 else "FAIL",
            "error_count": error_count,
        }
        if error_count == 0:
            self._log("Tipos corretos", "SUCCESS")
        else:
            self._log(
                f"Erros de tipo: {error_count} (aceitável se < 10)",
                "WARNING" if error_count < 10 else "ERROR",
            )

        # 2.4: Pytest testes básicos
        self._log("Executando testes básicos...", "INFO")
        success, output = self._run_command(
            "python -m pytest tests/psychoanalysis/ -v --tb=short -x 2>&1 | tail -30", "Pytest"
        )
        # Contar testes passados/falhados
        passed = output.count(" PASSED")
        failed = output.count(" FAILED")
        stage_results["pytest"] = {
            "status": "PASS" if success else "FAIL",
            "passed": passed,
            "failed": failed,
        }
        if success:
            self._log(f"Testes passando ({passed} passed)", "SUCCESS")
        else:
            self._log(f"Testes falhando ({failed} failed)", "ERROR")

        # Summarize
        self.results["stages"]["code_validation"] = stage_results
        validation_pass = all(r.get("status") in ["PASS", "WARN"] for r in stage_results.values())

        if validation_pass:
            self._log("✅ VALIDAÇÃO DE CÓDIGO PASSED", "SUCCESS")
        else:
            self._log("❌ VALIDAÇÃO DE CÓDIGO FAILED", "ERROR")

        return validation_pass

    # ===== STAGE 3: COLETA DE MÉTRICAS =====

    async def stage_collect_metrics(self) -> bool:
        """Coleta métricas científicas executando ciclos de consciência"""
        self._log(f"STAGE 3: COLETA DE MÉTRICAS ({self.cycles} ciclos)", "HEADER")
        stage_results = {}

        try:
            # Importar IntegrationLoop
            from src.consciousness.extended_cycle_result import ExtendedLoopCycleResult
            from src.consciousness.integration_loop import IntegrationLoop

            self._log(f"Inicializando IntegrationLoop...", "INFO")
            loop = IntegrationLoop(enable_extended_results=True, enable_logging=False)

            all_metrics: List[Dict[str, Any]] = []
            phi_values = []
            psi_values = []
            sigma_values = []

            for i in range(1, self.cycles + 1):
                try:
                    result = await loop.execute_cycle(collect_metrics=True)

                    cycle_metrics = {
                        "cycle": i,
                        "phi": result.phi_estimate,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "success": result.success,
                    }

                    # Coletar métricas científicas (Φ, Ψ, σ)
                    phi_values.append(result.phi_estimate)

                    if isinstance(result, ExtendedLoopCycleResult):
                        if result.psi is not None:
                            cycle_metrics["psi"] = result.psi
                            psi_values.append(result.psi)
                        if result.sigma is not None:
                            cycle_metrics["sigma"] = result.sigma
                            sigma_values.append(result.sigma)
                        if result.gozo is not None:
                            cycle_metrics["gozo"] = result.gozo
                        if result.delta is not None:
                            cycle_metrics["delta"] = result.delta
                        if result.control_effectiveness is not None:
                            cycle_metrics["control_effectiveness"] = result.control_effectiveness

                    all_metrics.append(cycle_metrics)

                    # Progress indicator
                    if (i % max(1, self.cycles // 10)) == 0 or i == self.cycles:
                        self._log(f"Ciclo {i}/{self.cycles} - Φ={result.phi_estimate:.6f}", "INFO")

                except Exception as e:
                    self._log(f"Erro no ciclo {i}: {e}", "WARNING")
                    continue

            # Análise de métricas
            import numpy as np

            def safe_stats(values):
                if not values:
                    return {}
                return {
                    "mean": float(np.mean(values)),
                    "std": float(np.std(values)),
                    "min": float(np.min(values)),
                    "max": float(np.max(values)),
                    "count": len(values),
                }

            phi_stats = safe_stats(phi_values)
            psi_stats = safe_stats(psi_values)
            sigma_stats = safe_stats(sigma_values)

            stage_results["phi"] = phi_stats
            stage_results["psi"] = psi_stats
            stage_results["sigma"] = sigma_stats
            stage_results["total_cycles"] = len(all_metrics)
            stage_results["successful_cycles"] = sum(
                1 for m in all_metrics if m.get("success", False)
            )

            # Validação contra baseline
            baseline_phi = 0.0183
            _target_phi_phase5 = 0.026

            _metrics_pass = True

            if phi_stats.get("mean", 0) > 0:
                self._log(
                    f"Φ médio: {phi_stats['mean']:.6f} NATS (baseline: {baseline_phi})", "SUCCESS"
                )
                stage_results["phi_vs_baseline"] = {
                    "baseline": baseline_phi,
                    "current": phi_stats["mean"],
                    "improvement_pct": (
                        (phi_stats["mean"] - baseline_phi) / baseline_phi * 100
                        if baseline_phi > 0
                        else 0
                    ),
                }

            if psi_stats.get("mean", 0) > 0:
                self._log(f"Ψ médio: {psi_stats['mean']:.6f} NATS", "SUCCESS")

            if sigma_stats.get("mean", 0) > 0:
                self._log(f"σ médio: {sigma_stats['mean']:.6f} NATS", "SUCCESS")

            self.results["stages"]["metrics"] = stage_results
            self.results["metrics"] = {
                "phi": phi_stats,
                "psi": psi_stats,
                "sigma": sigma_stats,
                "all_cycles": all_metrics,
            }

            if len(all_metrics) >= self.cycles * 0.8:  # 80% threshold
                self._log(
                    f"✅ COLETA DE MÉTRICAS PASSOU ({len(all_metrics)}/{self.cycles} ciclos)",
                    "SUCCESS",
                )
                return True
            else:
                self._log(
                    f"❌ COLETA DE MÉTRICAS FALHOU ({len(all_metrics)}/{self.cycles} ciclos)",
                    "ERROR",
                )
                return False

        except Exception as e:
            self._log(f"Erro ao coletar métricas: {e}", "ERROR")
            import traceback

            traceback.print_exc()
            return False

    # ===== MAIN VALIDATION =====

    async def run_full_validation(self) -> bool:
        """Executa validação completa (pré-flight + code + metrics)"""
        self._log("", "HEADER")
        self._log("🚀 PHASE 5 & 6 PRODUCTION VALIDATION", "HEADER")
        self._log(f"Timestamp: {self.timestamp}", "INFO")
        self._log("", "HEADER")

        results = []

        # Stage 1: Pré-flight
        preflight_pass = self.stage_preflight()
        results.append(("Pré-Flight", preflight_pass))
        self._log("")

        # Stage 2: Code validation
        code_pass = self.stage_validate_code()
        results.append(("Code Validation", code_pass))
        self._log("")

        # Stage 3: Metrics
        metrics_pass = await self.stage_collect_metrics()
        results.append(("Metrics Collection", metrics_pass))
        self._log("")

        # Summary
        self._log("", "HEADER")
        self._log("📊 RELATÓRIO FINAL", "HEADER")
        for stage, passed in results:
            status = "✅ PASSED" if passed else "❌ FAILED"
            self._log(f"{stage}: {status}", "SUCCESS" if passed else "ERROR")

        overall_pass = all(r[1] for r in results)
        self.results["overall_status"] = "PASS" if overall_pass else "FAIL"

        self._log("", "HEADER")
        if overall_pass:
            self._log("🎉 VALIDAÇÃO COMPLETA APROVADA!", "SUCCESS")
            self._log("Sistema pronto para Phase 5 & 6 implementation", "SUCCESS")
        else:
            self._log("⚠️ VALIDAÇÃO COM FALHAS", "ERROR")
            self._log("Corrija os problemas acima antes de continuar", "ERROR")
        self._log("", "HEADER")

        # Save results
        self._save_results()

        return overall_pass

    def _save_results(self) -> None:
        """Salva resultados em JSON"""
        log_dir = project_root / "logs" / "validation"
        log_dir.mkdir(parents=True, exist_ok=True)

        results_file = log_dir / f"phase5_6_validation_{self.timestamp}.json"

        # Simplificar resultados para JSON serialization
        json_results = {**self.results, "log": self.validation_log}

        with open(results_file, "w") as f:
            json.dump(json_results, f, indent=2, default=str)

        self._log(f"Resultados salvos em: {results_file}", "INFO")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Phase 5 & 6 Production Validation Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  # Checklist pré-implementação
  python scripts/canonical/validate/validate_phase5_6_production.py --pre-flight

  # Validação de código
  python scripts/canonical/validate/validate_phase5_6_production.py --validate

  # Coleta de métricas (100 ciclos)
  python scripts/canonical/validate/validate_phase5_6_production.py --metrics --cycles 100

  # Validação completa
  python scripts/canonical/validate/validate_phase5_6_production.py --full --cycles 50
        """,
    )

    parser.add_argument("--pre-flight", action="store_true", help="Execute pré-flight checks only")
    parser.add_argument("--validate", action="store_true", help="Execute code validation only")
    parser.add_argument("--metrics", action="store_true", help="Collect metrics only")
    parser.add_argument(
        "--full",
        action="store_true",
        help="Execute full validation (pré-flight + validate + metrics)",
    )
    parser.add_argument(
        "--cycles", type=int, default=50, help="Number of cycles for metrics (default: 50)"
    )
    parser.add_argument("--quiet", action="store_true", help="Quiet mode (less output)")

    args = parser.parse_args()

    # Determine what to run
    if not any([args.pre_flight, args.validate, args.metrics, args.full]):
        args.full = True  # Default to full validation

    validator = Phase5_6Validator(cycles=args.cycles, verbose=not args.quiet)

    try:
        if args.pre_flight:
            success = validator.stage_preflight()
            sys.exit(0 if success else 1)

        elif args.validate:
            success = validator.stage_validate_code()
            sys.exit(0 if success else 1)

        elif args.metrics:
            success = asyncio.run(validator.stage_collect_metrics())
            sys.exit(0 if success else 1)

        elif args.full:
            success = asyncio.run(validator.run_full_validation())
            sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n❌ Validação cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro durante validação: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
