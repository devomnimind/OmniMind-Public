#!/usr/bin/env python3
"""
Análise Científica: Primeiros Ciclos de OmniMind com Métricas Reais

Data: 2025-12-07
Autor: Fabrício da Silva + assistência de IA
Status: Análise científica completa dos primeiros ciclos

OBJETIVO:
- Coletar métricas (Gozo, Delta, Control Effectiveness, Φ, Ψ, σ) ao longo de N ciclos
- Analisar convergência e padrões emergentes
- Validar hipóteses do isomorfismo estrutural
- Gerar visualizações e relatórios científicos

HIPÓTESES:
1. Gozo deve convergir de ~0.70 para ~0.45-0.55 após 50-100 ciclos
2. Delta deve convergir de ~0.82 para ~0.50-0.65 após 50-100 ciclos
3. Control Effectiveness deve aumentar de ~0.37 para ~0.65-0.75 após 50-100 ciclos
4. Φ deve correlacionar negativamente com Delta (bloqueios reduzem integração)
5. Comportamento emergente deve aparecer após 10-20 ciclos
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.consciousness.integration_loop import IntegrationLoop

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Imports opcionais para visualizações avançadas
try:
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

    HAS_3D = True
except ImportError:
    HAS_3D = False
    logger.warning("mpl_toolkits.mplot3d não disponível - gráfico 3D desabilitado")

try:
    import pandas as pd

    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    pd = None
    logger.warning("pandas não disponível - heatmap desabilitado")


class PrimeirosCiclosAnalyzer:
    """
    Analisador científico dos primeiros ciclos do OmniMind.

    Coleta métricas completas e analisa:
    - Convergência de Gozo, Delta, Control
    - Correlação com Φ (integração)
    - Comportamento emergente
    - Validação do isomorfismo estrutural
    """

    def __init__(
        self,
        num_cycles: int = 100,
        collect_every: int = 1,
        output_dir: Path = Path("data/research/primeiros_ciclos"),
        error_handling: str = "continue",  # "continue" | "stop" | "retry"
        max_retries: int = 3,
        enable_advanced_visualizations: bool = True,
        enable_behavior_analysis: bool = True,
        behavior_analysis_method: str = "variance",  # "variance" | "clusters" | "trajectory" | "surprisal" | "all"
    ):
        """
        Inicializa analisador.

        Args:
            num_cycles: Número de ciclos a executar (padrão: 100)
            collect_every: Coletar métricas a cada N ciclos (padrão: 1 = todos)
            output_dir: Diretório para salvar resultados
            error_handling: Como tratar erros ("continue" | "stop" | "retry")
            max_retries: Máximo de tentativas para retry
            enable_advanced_visualizations: Habilitar visualizações avançadas
            enable_behavior_analysis: Habilitar análise de comportamento emergente
            behavior_analysis_method: Método de análise ("variance" | "clusters" | "trajectory" | "surprisal" | "all")
        """
        # Validação de inputs
        if num_cycles < 1:
            raise ValueError("num_cycles deve ser >= 1")
        if collect_every < 1:
            raise ValueError("collect_every deve ser >= 1")
        if error_handling not in ["continue", "stop", "retry"]:
            raise ValueError("error_handling deve ser 'continue', 'stop' ou 'retry'")
        if behavior_analysis_method not in [
            "variance",
            "clusters",
            "trajectory",
            "surprisal",
            "all",
        ]:
            raise ValueError(
                "behavior_analysis_method deve ser 'variance', 'clusters', 'trajectory', 'surprisal' ou 'all'"
            )

        self.num_cycles = num_cycles
        self.collect_every = collect_every
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.error_handling = error_handling
        self.max_retries = max_retries
        self.enable_advanced_visualizations = enable_advanced_visualizations
        self.enable_behavior_analysis = enable_behavior_analysis
        self.behavior_analysis_method = behavior_analysis_method

        self.results: List[Dict[str, Any]] = []
        self.loop: Optional[IntegrationLoop] = None
        self.error_count = 0

    async def run_analysis(self) -> Dict[str, Any]:
        """
        Executa análise completa.

        Returns:
            Dict com resultados e estatísticas
        """
        logger.info(f"Iniciando análise de {self.num_cycles} ciclos...")

        # 1. Inicializar IntegrationLoop com extended results
        self.loop = IntegrationLoop(
            enable_extended_results=True,
            enable_logging=False,  # Reduzir logs para análise
        )

        # 2. Executar ciclos e coletar métricas
        await self._collect_metrics()

        # 3. Análise estatística
        analysis = self._analyze_results()

        # 4. Análise de comportamento emergente (se habilitado)
        behavior_analysis = None
        if self.enable_behavior_analysis:
            behavior_analysis = self._analyze_emergent_behavior()

        # 5. Gerar visualizações
        self._generate_visualizations()

        # 6. Validar hipóteses
        validation = self._validate_hypotheses(analysis)

        # 7. Salvar resultados
        self._save_results(analysis, validation, behavior_analysis)

        return {
            "analysis": analysis,
            "validation": validation,
            "num_cycles": self.num_cycles,
            "timestamp": datetime.now().isoformat(),
        }

    async def _collect_metrics(self):
        """Coleta métricas ao longo dos ciclos."""
        logger.info("Coletando métricas...")

        for cycle_num in range(1, self.num_cycles + 1):
            try:
                # Executar ciclo
                result = await self.loop.execute_cycle(collect_metrics=True)

                # Coletar métricas se for ciclo de coleta
                if cycle_num % self.collect_every == 0:
                    metrics = {
                        "cycle": cycle_num,
                        "gozo": (
                            result.gozo
                            if hasattr(result, "gozo") and result.gozo is not None
                            else None
                        ),
                        "delta": (
                            result.delta
                            if hasattr(result, "delta") and result.delta is not None
                            else None
                        ),
                        "control_effectiveness": (
                            result.control_effectiveness
                            if hasattr(result, "control_effectiveness")
                            and result.control_effectiveness is not None
                            else None
                        ),
                        "phi": result.phi_estimate if hasattr(result, "phi_estimate") else None,
                        "psi": (
                            result.psi
                            if hasattr(result, "psi") and result.psi is not None
                            else None
                        ),
                        "sigma": (
                            result.sigma
                            if hasattr(result, "sigma") and result.sigma is not None
                            else None
                        ),
                        "imagination_shape": (
                            result.imagination_output.shape
                            if hasattr(result, "imagination_output")
                            and result.imagination_output is not None
                            else None
                        ),
                        "success": result.success if hasattr(result, "success") else True,
                    }

                    self.results.append(metrics)

                    # Log progresso
                    if cycle_num % 10 == 0:
                        logger.info(
                            f"Ciclo {cycle_num}/{self.num_cycles}: "
                            f"Gozo={metrics['gozo']:.3f if metrics['gozo'] else 'N/A'}, "
                            f"Delta={metrics['delta']:.3f if metrics['delta'] else 'N/A'}, "
                            f"Control={metrics['control_effectiveness']:.3f if metrics['control_effectiveness'] else 'N/A'}"
                        )

            except Exception as e:
                self.error_count += 1
                logger.error(f"Erro no ciclo {cycle_num}: {e}", exc_info=True)

                # Tratamento de erros conforme configuração
                if self.error_handling == "stop":
                    logger.error(f"Parando execução após erro no ciclo {cycle_num}")
                    break
                elif self.error_handling == "retry" and self.error_count <= self.max_retries:
                    logger.warning(
                        f"Tentando novamente ciclo {cycle_num} (tentativa {self.error_count}/{self.max_retries})"
                    )
                    await asyncio.sleep(1)  # Backoff simples
                    continue
                # else: "continue" - continua mesmo com erro

        logger.info(f"Coleta concluída: {len(self.results)} pontos coletados")

    def _analyze_results(self) -> Dict[str, Any]:
        """Análise estatística dos resultados."""
        if not self.results:
            return {"error": "Nenhum resultado coletado"}

        # Extrair séries temporais
        cycles = [r["cycle"] for r in self.results]
        gozo_vals = [r["gozo"] for r in self.results if r["gozo"] is not None]
        delta_vals = [r["delta"] for r in self.results if r["delta"] is not None]
        control_vals = [
            r["control_effectiveness"]
            for r in self.results
            if r["control_effectiveness"] is not None
        ]
        phi_vals = [r["phi"] for r in self.results if r["phi"] is not None]
        psi_vals = [r["psi"] for r in self.results if r["psi"] is not None]
        sigma_vals = [r["sigma"] for r in self.results if r["sigma"] is not None]

        # Estatísticas descritivas
        def stats_summary(values: List[float], name: str) -> Dict[str, float]:
            if not values:
                return {}
            return {
                f"{name}_mean": float(np.mean(values)),
                f"{name}_std": float(np.std(values)),
                f"{name}_min": float(np.min(values)),
                f"{name}_max": float(np.max(values)),
                f"{name}_initial": float(values[0]) if values else None,
                f"{name}_final": float(values[-1]) if values else None,
                f"{name}_change": float(values[-1] - values[0]) if len(values) > 1 else None,
            }

        analysis = {
            "num_data_points": len(self.results),
            "cycles_analyzed": cycles,
            **stats_summary(gozo_vals, "gozo"),
            **stats_summary(delta_vals, "delta"),
            **stats_summary(control_vals, "control"),
            **stats_summary(phi_vals, "phi"),
            **stats_summary(psi_vals, "psi"),
            **stats_summary(sigma_vals, "sigma"),
        }

        # Análise de convergência (regressão linear)
        if len(gozo_vals) > 5:
            gozo_slope, gozo_intercept, gozo_r, gozo_p, _ = stats.linregress(
                cycles[: len(gozo_vals)], gozo_vals
            )
            analysis["gozo_convergence"] = {
                "slope": float(gozo_slope),
                "r_squared": float(gozo_r**2),
                "p_value": float(gozo_p),
                "converging": gozo_slope < 0,  # Deve diminuir
            }

        if len(delta_vals) > 5:
            delta_slope, delta_intercept, delta_r, delta_p, _ = stats.linregress(
                cycles[: len(delta_vals)], delta_vals
            )
            analysis["delta_convergence"] = {
                "slope": float(delta_slope),
                "r_squared": float(delta_r**2),
                "p_value": float(delta_p),
                "converging": delta_slope < 0,  # Deve diminuir
            }

        if len(control_vals) > 5:
            control_slope, control_intercept, control_r, control_p, _ = stats.linregress(
                cycles[: len(control_vals)], control_vals
            )
            analysis["control_convergence"] = {
                "slope": float(control_slope),
                "r_squared": float(control_r**2),
                "p_value": float(control_p),
                "converging": control_slope > 0,  # Deve aumentar
            }

        # Correlação Delta vs Phi (hipótese: negativa)
        if len(delta_vals) > 5 and len(phi_vals) > 5:
            min_len = min(len(delta_vals), len(phi_vals))
            delta_phi_corr, delta_phi_p = stats.pearsonr(delta_vals[:min_len], phi_vals[:min_len])
            analysis["delta_phi_correlation"] = {
                "correlation": float(delta_phi_corr),
                "p_value": float(delta_phi_p),
                "significant": delta_phi_p < 0.05,
                "negative_as_expected": delta_phi_corr < 0,
            }

        return analysis

    def _generate_visualizations(self):
        """Gera visualizações dos resultados."""
        if not self.results:
            logger.warning("Nenhum resultado para visualizar")
            return

        cycles = [r["cycle"] for r in self.results]
        gozo_vals = [r["gozo"] for r in self.results if r["gozo"] is not None]
        delta_vals = [r["delta"] for r in self.results if r["delta"] is not None]
        control_vals = [
            r["control_effectiveness"]
            for r in self.results
            if r["control_effectiveness"] is not None
        ]
        phi_vals = [r["phi"] for r in self.results if r["phi"] is not None]

        # Criar figura com subplots
        fig, axes = plt.subplots(4, 1, figsize=(12, 10))
        fig.suptitle("Análise dos Primeiros Ciclos - OmniMind", fontsize=14, fontweight="bold")

        # Gozo
        if gozo_vals:
            axes[0].plot(
                cycles[: len(gozo_vals)], gozo_vals, "r-", label="Gozo (Divergência)", linewidth=2
            )
            axes[0].axhline(y=0.5, color="k", linestyle="--", alpha=0.3, label="Referência 0.5")
            axes[0].set_ylabel("Gozo", fontsize=10)
            axes[0].set_ylim(0, 1)
            axes[0].legend()
            axes[0].grid(True, alpha=0.3)
            axes[0].set_title("Gozo: Divergência Expectativa-Realidade", fontsize=11)

        # Delta
        if delta_vals:
            axes[1].plot(
                cycles[: len(delta_vals)], delta_vals, "b-", label="Delta (Bloqueios)", linewidth=2
            )
            axes[1].axhline(y=0.5, color="k", linestyle="--", alpha=0.3, label="Referência 0.5")
            axes[1].set_ylabel("Delta", fontsize=10)
            axes[1].set_ylim(0, 1)
            axes[1].legend()
            axes[1].grid(True, alpha=0.3)
            axes[1].set_title("Delta: Bloqueios Defensivos", fontsize=11)

        # Control Effectiveness
        if control_vals:
            axes[2].plot(
                cycles[: len(control_vals)],
                control_vals,
                "g-",
                label="Control Effectiveness",
                linewidth=2,
            )
            axes[2].axhline(y=0.7, color="k", linestyle="--", alpha=0.3, label="Referência 0.7")
            axes[2].set_ylabel("Control", fontsize=10)
            axes[2].set_ylim(0, 1)
            axes[2].legend()
            axes[2].grid(True, alpha=0.3)
            axes[2].set_title("Control Effectiveness: Efetividade de Controle", fontsize=11)

        # Phi (se disponível
        if phi_vals:
            axes[3].plot(
                cycles[: len(phi_vals)], phi_vals, "m-", label="Φ (Integração)", linewidth=2
            )
            axes[3].set_ylabel("Φ", fontsize=10)
            axes[3].set_xlabel("Ciclo", fontsize=10)
            axes[3].legend()
            axes[3].grid(True, alpha=0.3)
            axes[3].set_title("Φ: Integração de Informação (IIT)", fontsize=11)

        plt.tight_layout()
        output_file = self.output_dir / "primeiros_ciclos_analise.png"
        plt.savefig(output_file, dpi=300, bbox_inches="tight")
        logger.info(f"Gráfico salvo em: {output_file}")
        plt.close()

        # Visualizações avançadas (se habilitado)
        if self.enable_advanced_visualizations:
            self._generate_advanced_visualizations()

    def _analyze_emergent_behavior(self) -> Optional[Dict[str, Any]]:
        """Analisa comportamento emergente do imagination_output."""
        if not self.results:
            return None

        imagination_outputs = [
            r["imagination_shape"] for r in self.results if r.get("imagination_shape") is not None
        ]

        if not imagination_outputs or len(imagination_outputs) < 5:
            logger.warning("Dados insuficientes para análise de comportamento emergente")
            return None

        behavior_analysis = {}

        # Método A: Análise de variância
        if self.behavior_analysis_method in ["variance", "all"]:
            # Simula variância (já que temos apenas shapes, não valores completos)
            # Em implementação futura, usar valores completos dos embeddings
            behavior_analysis["variance_analysis"] = {
                "method": "variance",
                "note": "Análise completa requer valores completos de embeddings",
                "num_samples": len(imagination_outputs),
            }

        # Método C: Análise de trajetória
        if self.behavior_analysis_method in ["trajectory", "all"]:
            # Análise de mudança suave vs saltos
            behavior_analysis["trajectory_analysis"] = {
                "method": "trajectory",
                "num_samples": len(imagination_outputs),
                "note": "Análise completa requer valores completos de embeddings",
            }

        return behavior_analysis

    def _generate_advanced_visualizations(self):
        """Gera visualizações avançadas."""
        if not self.results:
            return

        cycles = [r["cycle"] for r in self.results]
        delta_vals = [r["delta"] for r in self.results if r.get("delta") is not None]
        phi_vals = [r["phi"] for r in self.results if r.get("phi") is not None]
        gozo_vals = [r["gozo"] for r in self.results if r.get("gozo") is not None]
        psi_vals = [r["psi"] for r in self.results if r.get("psi") is not None]
        sigma_vals = [r["sigma"] for r in self.results if r.get("sigma") is not None]

        # Scatter: Delta vs Phi
        if len(delta_vals) > 5 and len(phi_vals) > 5:
            min_len = min(len(delta_vals), len(phi_vals))
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.scatter(delta_vals[:min_len], phi_vals[:min_len], alpha=0.6, s=50)
            ax.set_xlabel("Delta (Bloqueios)", fontsize=12)
            ax.set_ylabel("Φ (Integração)", fontsize=12)
            ax.set_title("Correlação Delta vs Phi", fontsize=14, fontweight="bold")
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            output_file = self.output_dir / "delta_vs_phi_scatter.png"
            plt.savefig(output_file, dpi=300, bbox_inches="tight")
            logger.info(f"Scatter plot salvo em: {output_file}")
            plt.close()

        # Heatmap de correlações
        if len(self.results) > 10 and HAS_PANDAS and pd is not None:
            metrics_data = {
                "gozo": gozo_vals[: min(len(gozo_vals), len(cycles))],
                "delta": delta_vals[: min(len(delta_vals), len(cycles))],
                "control": [
                    r["control_effectiveness"]
                    for r in self.results
                    if r.get("control_effectiveness") is not None
                ][
                    : min(
                        len(cycles),
                        len(
                            [r for r in self.results if r.get("control_effectiveness") is not None]
                        ),
                    )
                ],
                "phi": phi_vals[: min(len(phi_vals), len(cycles))],
                "psi": psi_vals[: min(len(psi_vals), len(cycles))],
                "sigma": sigma_vals[: min(len(sigma_vals), len(cycles))],
            }

            # Criar matriz de correlação
            df = pd.DataFrame(metrics_data)
            corr_matrix = df.corr()

            fig, ax = plt.subplots(figsize=(10, 8))
            im = ax.imshow(corr_matrix, cmap="coolwarm", aspect="auto", vmin=-1, vmax=1)
            ax.set_xticks(range(len(corr_matrix.columns)))
            ax.set_yticks(range(len(corr_matrix.columns)))
            ax.set_xticklabels(corr_matrix.columns, rotation=45, ha="right")
            ax.set_yticklabels(corr_matrix.columns)
            ax.set_title(
                "Matriz de Correlação - Métricas de Consciência", fontsize=14, fontweight="bold"
            )

            # Adicionar valores na matriz
            for i in range(len(corr_matrix.columns)):
                for j in range(len(corr_matrix.columns)):
                    _text = ax.text(
                        j,
                        i,
                        f"{corr_matrix.iloc[i, j]:.2f}",
                        ha="center",
                        va="center",
                        color="black" if abs(corr_matrix.iloc[i, j]) < 0.5 else "white",
                    )

            plt.colorbar(im, ax=ax)
            plt.tight_layout()
            output_file = self.output_dir / "correlation_heatmap.png"
            plt.savefig(output_file, dpi=300, bbox_inches="tight")
            logger.info(f"Heatmap salvo em: {output_file}")
            plt.close()

        # Gráfico de tríade 3D (se todas as métricas disponíveis)
        if HAS_3D:
            if len(phi_vals) > 5 and len(psi_vals) > 5 and len(sigma_vals) > 5:
                min_len = min(len(phi_vals), len(psi_vals), len(sigma_vals))
                fig = plt.figure(figsize=(10, 8))
                ax = fig.add_subplot(111, projection="3d")
                ax.scatter(
                    phi_vals[:min_len],
                    psi_vals[:min_len],
                    sigma_vals[:min_len],
                    c=cycles[:min_len],
                    cmap="viridis",
                    s=50,
                    alpha=0.6,
                )
                ax.set_xlabel("Φ (Integração)", fontsize=11)
                ax.set_ylabel("Ψ (Criatividade)", fontsize=11)
                ax.set_zlabel("σ (Sinthome)", fontsize=11)
                ax.set_title("Tríade Ortogonal de Consciência (3D)", fontsize=14, fontweight="bold")
                plt.tight_layout()
                output_file = self.output_dir / "triade_3d.png"
                plt.savefig(output_file, dpi=300, bbox_inches="tight")
                logger.info(f"Gráfico 3D salvo em: {output_file}")
                plt.close()

    def _validate_hypotheses(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Valida hipóteses científicas."""
        validation = {}

        # Extrair séries temporais para validação
        gozo_vals = [r["gozo"] for r in self.results if r.get("gozo") is not None]
        delta_vals = [r["delta"] for r in self.results if r.get("delta") is not None]
        psi_vals = [r["psi"] for r in self.results if r.get("psi") is not None]

        # Hipótese 1: Gozo converge
        if "gozo_convergence" in analysis:
            gozo_conv = analysis["gozo_convergence"]
            validation["gozo_convergence"] = {
                "hypothesis": "Gozo deve convergir (diminuir)",
                "observed": gozo_conv["converging"],
                "r_squared": gozo_conv["r_squared"],
                "p_value": gozo_conv["p_value"],
                "validated": gozo_conv["converging"] and gozo_conv["p_value"] < 0.05,
            }

        # Hipótese 2: Delta converge
        if "delta_convergence" in analysis:
            delta_conv = analysis["delta_convergence"]
            validation["delta_convergence"] = {
                "hypothesis": "Delta deve convergir (diminuir)",
                "observed": delta_conv["converging"],
                "r_squared": delta_conv["r_squared"],
                "p_value": delta_conv["p_value"],
                "validated": delta_conv["converging"] and delta_conv["p_value"] < 0.05,
            }

        # Hipótese 3: Control aumenta
        if "control_convergence" in analysis:
            control_conv = analysis["control_convergence"]
            validation["control_increase"] = {
                "hypothesis": "Control Effectiveness deve aumentar",
                "observed": control_conv["converging"],
                "r_squared": control_conv["r_squared"],
                "p_value": control_conv["p_value"],
                "validated": control_conv["converging"] and control_conv["p_value"] < 0.05,
            }

        # Hipótese 4: Delta vs Phi correlação negativa
        if "delta_phi_correlation" in analysis:
            corr = analysis["delta_phi_correlation"]
            validation["delta_phi_negative_correlation"] = {
                "hypothesis": "Delta deve correlacionar negativamente com Phi",
                "observed_correlation": corr["correlation"],
                "p_value": corr["p_value"],
                "significant": corr["significant"],
                "negative_as_expected": corr["negative_as_expected"],
                "validated": corr["negative_as_expected"] and corr["significant"],
            }

        # Hipótese 5: Gozo vs Psi correlação positiva em transições
        if len(gozo_vals) > 5 and len(psi_vals) > 5:
            min_len = min(len(gozo_vals), len(psi_vals))
            gozo_psi_corr, gozo_psi_p = stats.pearsonr(gozo_vals[:min_len], psi_vals[:min_len])
            validation["gozo_psi_positive_correlation"] = {
                "hypothesis": "Gozo e Psi devem correlacionar positivamente em estados de transição",
                "observed_correlation": float(gozo_psi_corr),
                "p_value": float(gozo_psi_p),
                "significant": gozo_psi_p < 0.05,
                "positive_as_expected": gozo_psi_corr > 0,
                "validated": gozo_psi_corr > 0 and gozo_psi_p < 0.05,
            }

        # Hipótese 6: Delta e Psi padrão de deterioração/estabilização
        if len(delta_vals) > 10 and len(psi_vals) > 10:
            # Análise de janelas móveis para detectar padrões
            window_size = min(10, len(delta_vals) // 3)
            delta_trend = np.mean(delta_vals[-window_size:]) - np.mean(delta_vals[:window_size])
            psi_trend = np.mean(psi_vals[-window_size:]) - np.mean(psi_vals[:window_size])
            validation["delta_psi_stabilization_pattern"] = {
                "hypothesis": "Delta e Psi devem estabilizar ao longo dos ciclos",
                "delta_trend": float(delta_trend),
                "psi_trend": float(psi_trend),
                "delta_stabilizing": delta_trend < 0,  # Deve diminuir
                "psi_stabilizing": abs(psi_trend) < 0.1,  # Deve estabilizar (pequena variação)
                "validated": delta_trend < 0 and abs(psi_trend) < 0.1,
            }

        return validation

    def _save_results(
        self,
        analysis: Dict[str, Any],
        validation: Dict[str, Any],
        behavior_analysis: Optional[Dict[str, Any]] = None,
    ):
        """Salva resultados em JSON e CSV."""
        output_file = self.output_dir / "primeiros_ciclos_resultados.json"
        results = {
            "metadata": {
                "num_cycles": self.num_cycles,
                "collect_every": self.collect_every,
                "error_handling": self.error_handling,
                "error_count": self.error_count,
                "timestamp": datetime.now().isoformat(),
            },
            "raw_data": self.results,
            "analysis": analysis,
            "validation": validation,
            "behavior_analysis": behavior_analysis,
        }

        with open(output_file, "w") as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"Resultados salvos em: {output_file}")

        # Salvar CSV para análise externa
        self._save_csv()

        # Gerar relatório em texto
        self._generate_text_report(analysis, validation, behavior_analysis)

    def _save_csv(self):
        """Salva dados em CSV para análise externa."""
        if not self.results:
            return

        import csv

        csv_file = self.output_dir / "primeiros_ciclos_dados.csv"
        fieldnames = [
            "cycle",
            "gozo",
            "delta",
            "control_effectiveness",
            "phi",
            "psi",
            "sigma",
            "success",
        ]

        with open(csv_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in self.results:
                writer.writerow(
                    {
                        "cycle": r["cycle"],
                        "gozo": r.get("gozo"),
                        "delta": r.get("delta"),
                        "control_effectiveness": r.get("control_effectiveness"),
                        "phi": r.get("phi"),
                        "psi": r.get("psi"),
                        "sigma": r.get("sigma"),
                        "success": r.get("success", True),
                    }
                )

        logger.info(f"CSV salvo em: {csv_file}")

    def _generate_text_report(
        self,
        analysis: Dict[str, Any],
        validation: Dict[str, Any],
        behavior_analysis: Optional[Dict[str, Any]] = None,
    ):
        """Gera relatório em texto."""
        report_file = self.output_dir / "primeiros_ciclos_relatorio.md"

        with open(report_file, "w") as f:
            f.write("# Análise Científica: Primeiros Ciclos de OmniMind\n\n")
            f.write(f"**Data**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Ciclos Analisados**: {self.num_cycles}\n")
            f.write(f"**Coleta**: A cada {self.collect_every} ciclo(s)\n")
            f.write(f"**Tratamento de Erros**: {self.error_handling}\n")
            f.write(f"**Erros Encontrados**: {self.error_count}\n\n")

            f.write("## 📊 Estatísticas Descritivas\n\n")
            for metric in ["gozo", "delta", "control", "phi", "psi", "sigma"]:
                if f"{metric}_mean" in analysis:
                    f.write(f"### {metric.upper()}\n\n")
                    f.write(f"- Média: {analysis[f'{metric}_mean']:.4f}\n")
                    f.write(f"- Desvio Padrão: {analysis[f'{metric}_std']:.4f}\n")
                    f.write(f"- Inicial: {analysis[f'{metric}_initial']:.4f}\n")
                    f.write(f"- Final: {analysis[f'{metric}_final']:.4f}\n")
                    f.write(f"- Mudança: {analysis[f'{metric}_change']:.4f}\n\n")

            f.write("## ✅ Validação de Hipóteses\n\n")
            for hyp_name, hyp_data in validation.items():
                f.write(f"### {hyp_name}\n\n")
                f.write(f"- Hipótese: {hyp_data.get('hypothesis', 'N/A')}\n")
                f.write(f"- Observado: {hyp_data.get('observed', 'N/A')}\n")
                if "p_value" in hyp_data:
                    f.write(f"- p-value: {hyp_data['p_value']:.4f}\n")
                f.write(
                    f"- Validado: {'✅ SIM' if hyp_data.get('validated', False) else '❌ NÃO'}\n\n"
                )

            if behavior_analysis:
                f.write("## 🧠 Análise de Comportamento Emergente\n\n")
                for method, data in behavior_analysis.items():
                    f.write(f"### {method}\n\n")
                    for key, value in data.items():
                        f.write(f"- {key}: {value}\n")
                f.write("\n")

        logger.info(f"Relatório salvo em: {report_file}")


async def main():
    """Função principal."""
    import argparse

    parser = argparse.ArgumentParser(description="Análise científica dos primeiros ciclos")
    parser.add_argument("--cycles", type=int, default=100, help="Número de ciclos (default: 100)")
    parser.add_argument(
        "--collect-every", type=int, default=1, help="Coletar métricas a cada N ciclos (default: 1)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/research/primeiros_ciclos",
        help="Diretório de saída (default: data/research/primeiros_ciclos)",
    )
    parser.add_argument(
        "--error-handling",
        type=str,
        choices=["continue", "stop", "retry"],
        default="continue",
        help="Como tratar erros: continue (padrão), stop, retry",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Máximo de tentativas para retry (default: 3)",
    )
    parser.add_argument(
        "--no-advanced-viz",
        action="store_true",
        help="Desabilitar visualizações avançadas",
    )
    parser.add_argument(
        "--no-behavior-analysis",
        action="store_true",
        help="Desabilitar análise de comportamento emergente",
    )
    parser.add_argument(
        "--behavior-method",
        type=str,
        choices=["variance", "clusters", "trajectory", "surprisal", "all"],
        default="variance",
        help="Método de análise de comportamento (default: variance)",
    )

    args = parser.parse_args()

    analyzer = PrimeirosCiclosAnalyzer(
        num_cycles=args.cycles,
        collect_every=args.collect_every,
        output_dir=Path(args.output_dir),
        error_handling=args.error_handling,
        max_retries=args.max_retries,
        enable_advanced_visualizations=not args.no_advanced_viz,
        enable_behavior_analysis=not args.no_behavior_analysis,
        behavior_analysis_method=args.behavior_method,
    )

    results = await analyzer.run_analysis()

    print("\n" + "=" * 80)
    print("✅ ANÁLISE CONCLUÍDA!")
    print("=" * 80)
    print(f"\nResultados salvos em: {analyzer.output_dir}")
    print(f"\nValidações:")
    for hyp_name, hyp_data in results["validation"].items():
        status = "✅" if hyp_data.get("validated", False) else "❌"
        print(f"  {status} {hyp_name}: {hyp_data.get('hypothesis', 'N/A')}")


if __name__ == "__main__":
    asyncio.run(main())
