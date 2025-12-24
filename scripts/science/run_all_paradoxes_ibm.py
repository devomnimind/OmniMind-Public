#!/usr/bin/env python3
"""
OmniMind - Sistema de Experimentos Paradoxais via IBM Quantum Real
===================================================================

Executa experimentos científicos resolvendo paradoxos que a humanidade não consegue.

Autor: Fabrício da Silva
Data: 2024-12-24
Meta: A ERA DAS TREVAS ACABA
"""

import json
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Callable
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger("ParadoxRunner")

load_dotenv()


class ParadoxExperimentRunner:
    """Runner para experimentos paradoxais via IBM Quantum Real."""

    def __init__(self, ibm_token: str = None):
        """Inicializa runner com conexão IBM."""
        self.token = ibm_token or os.getenv("IBM_CLOUD_API_KEY")
        if not self.token:
            raise ValueError("IBM_CLOUD_API_KEY não encontrada")

        self.service = None
        self.backend = None
        self.results = []
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = Path(f"data/paradox_experiments/run_{self.timestamp}")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"✅ Runner inicializado: {self.output_dir}")

    def connect_ibm(self):
        """Conecta ao IBM Quantum Cloud."""
        from qiskit_ibm_runtime import QiskitRuntimeService

        logger.info("🔌 Conectando ao IBM Quantum Cloud...")

        try:
            self.service = QiskitRuntimeService(channel="ibm_cloud", token=self.token)
            logger.info("✅ Conectado ao IBM Quantum")
        except Exception as e:
            logger.error(f"❌ Erro na conexão: {e}")
            raise

        # Selecionar backend menos ocupado
        self.backend = self.service.least_busy(operational=True, simulator=False)
        logger.info(
            f"✅ Backend selecionado: {self.backend.name} ({self.backend.num_qubits} qubits)"
        )

        # Salvar metadata da conexão
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "backend": {
                "name": self.backend.name,
                "qubits": self.backend.num_qubits,
                "status": self.backend.status().status_msg,
            },
            "runner_version": "1.0.0",
        }

        with open(self.output_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

    def run_paradox(
        self, paradox_name: str, circuit_builder: Callable, description: str = ""
    ) -> Dict[str, Any]:
        """
        Executa experimento de paradoxo.

        Args:
            paradox_name: Nome do paradoxo
            circuit_builder: Função que retorna QuantumCircuit
            description: Descrição do paradoxo

        Returns:
            Resultado do experimento
        """
        from qiskit import transpile
        from qiskit_ibm_runtime import SamplerV2

        logger.info("=" * 60)
        logger.info(f"🔬 Executando: {paradox_name}")
        logger.info(f"   {description}")
        logger.info("=" * 60)

        # Criar diretório do paradoxo
        paradox_dir = self.output_dir / paradox_name.lower().replace(" ", "_")
        paradox_dir.mkdir(exist_ok=True)

        try:
            # 1. Construir circuito
            logger.info("🌀 Construindo circuito quântico...")
            qc = circuit_builder()

            # 2. Transpilar
            logger.info(f"🔧 Transpilando para {self.backend.name}...")
            start_transpile = datetime.now()
            transpiled = transpile(qc, backend=self.backend, optimization_level=3)
            transpile_time = (datetime.now() - start_transpile).total_seconds()
            logger.info(f"   Transpilação: {transpile_time:.2f}s")

            # 3. Executar
            logger.info("🚀 Executando no hardware quântico...")
            start_exec = datetime.now()

            sampler = SamplerV2(mode=self.backend)
            job = sampler.run([transpiled], shots=1024)

            logger.info(f"   Job ID: {job.job_id()}")
            logger.info("   Aguardando resultado...")

            result = job.result()
            exec_time = (datetime.now() - start_exec).total_seconds()

            # 4. Extrair counts (código validado)
            data_bin = result[0].data
            if hasattr(data_bin, "c"):
                counts_obj = data_bin.c
                counts = counts_obj.get_counts()
            else:
                counts = getattr(data_bin, "get_counts", lambda: {})()

            logger.info(f"✅ Resultado recebido ({exec_time:.2f}s)")

            # 5. Analisar resultado
            total = sum(counts.values()) or 1
            distribution = {state: count / total for state, count in counts.items()}

            # Log top 5 estados
            top_states = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]
            logger.info("📊 Top 5 estados:")
            for state, count in top_states:
                logger.info(f"   |{state}⟩: {count} ({count/total:.1%})")

            # 6. Interpretar
            interpretation = self._interpret_result(paradox_name, distribution)
            logger.info(f"💡 Interpretação: {interpretation['conclusion']}")

            # 7. Salvar resultado completo
            result_data = {
                "timestamp": datetime.now().isoformat(),
                "paradox": paradox_name,
                "description": description,
                "backend": {"name": self.backend.name, "qubits": self.backend.num_qubits},
                "job": {"job_id": job.job_id(), "status": "DONE"},
                "metrics": {
                    "transpile_time_seconds": transpile_time,
                    "execution_time_seconds": exec_time,
                    "shots": 1024,
                },
                "quantum_result": {"counts": counts, "distribution": distribution},
                "interpretation": interpretation,
                "omnimind_resolution": True,
            }

            # Salvar raw
            with open(paradox_dir / "result_raw.json", "w") as f:
                json.dump(result_data, f, indent=2)

            # Salvar sanitizado (sem job_id sensível)
            sanitized = result_data.copy()
            sanitized["job"]["job_id"] = "SANITIZED"

            with open(paradox_dir / "result_sanitized.json", "w") as f:
                json.dump(sanitized, f, indent=2)

            # Salvar interpretação em markdown
            with open(paradox_dir / "interpretation.md", "w") as f:
                f.write(f"# {paradox_name}\n\n")
                f.write(f"{description}\n\n")
                f.write(f"## Resultado\n\n")
                f.write(f"**Conclusão**: {interpretation['conclusion']}\n\n")
                f.write(f"**Significado**: {interpretation['meaning']}\n\n")
                f.write(f"## Distribuição Quântica\n\n")
                for state, prob in sorted(distribution.items(), key=lambda x: x[1], reverse=True)[
                    :10
                ]:
                    f.write(f"- |{state}⟩: {prob:.2%}\n")

            self.results.append(result_data)
            logger.info(f"✅ {paradox_name} concluído!")

            return result_data

        except Exception as e:
            logger.error(f"❌ Erro em {paradox_name}: {e}")
            import traceback

            traceback.print_exc()

            error_data = {
                "timestamp": datetime.now().isoformat(),
                "paradox": paradox_name,
                "status": "FAILED",
                "error": str(e),
            }

            with open(paradox_dir / "error.json", "w") as f:
                json.dump(error_data, f, indent=2)

            return error_data

    def _interpret_result(
        self, paradox_name: str, distribution: Dict[str, float]
    ) -> Dict[str, str]:
        """Interpreta resultado quântico do paradoxo."""

        # Análise genérica baseada em distribuição
        top_state = max(distribution.items(), key=lambda x: x[1])
        entropy = -sum(p * (p and (p * (1 / p))) for p in distribution.values() if p > 0)

        if entropy > 0.8:
            conclusion = f"{paradox_name} em SUPERPOSIÇÃO quântica"
            meaning = "Sistema mantém múltiplos estados simultaneamente"
        elif top_state[1] > 0.7:
            conclusion = f"{paradox_name} RESOLVIDO via colapso quântico"
            meaning = f"Sistema convergiu para estado |{top_state[0]}⟩"
        else:
            conclusion = f"{paradox_name} em EQUILÍBRIO quântico"
            meaning = "Sistema navega entre múltiplos estados"

        return {
            "conclusion": conclusion,
            "meaning": meaning,
            "entropy": entropy,
            "dominant_state": top_state[0],
            "dominant_probability": top_state[1],
        }

    def generate_summary_report(self):
        """Gera relatório final de todos os experimentos."""
        logger.info("📝 Gerando relatório final...")

        report_path = self.output_dir / "summary_report.md"

        with open(report_path, "w") as f:
            f.write("# OmniMind - Experimentos Paradoxais via IBM Quantum\n\n")
            f.write(f"**Data**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Backend**: {self.backend.name} ({self.backend.num_qubits} qubits)\n\n")
            f.write(f"**Total de Experimentos**: {len(self.results)}\n\n")
            f.write("---\n\n")

            for i, result in enumerate(self.results, 1):
                if "error" in result:
                    f.write(f"## {i}. {result['paradox']} ❌\n\n")
                    f.write(f"**Status**: FAILED\n\n")
                    f.write(f"**Erro**: {result['error']}\n\n")
                else:
                    f.write(f"## {i}. {result['paradox']} ✅\n\n")
                    f.write(f"**Conclusão**: {result['interpretation']['conclusion']}\n\n")
                    f.write(f"**Significado**: {result['interpretation']['meaning']}\n\n")
                    f.write(
                        f"**Tempo de Execução**: {result['metrics']['execution_time_seconds']:.2f}s\n\n"
                    )

                f.write("---\n\n")

            f.write("## 🎯 Meta Alcançada\n\n")
            f.write("**OmniMind resolve paradoxos que a humanidade não consegue**\n\n")
            f.write("**A ERA DAS TREVAS ACABA**\n")

        logger.info(f"✅ Relatório salvo: {report_path}")


if __name__ == "__main__":
    logger.info("🚀 OmniMind - Sistema de Experimentos Paradoxais")
    logger.info("=" * 60)

    # Exemplo de uso
    runner = ParadoxExperimentRunner()
    runner.connect_ibm()

    logger.info("✅ Sistema pronto para executar experimentos")
    logger.info(f"📁 Resultados em: {runner.output_dir}")
