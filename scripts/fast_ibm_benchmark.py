#!/usr/bin/env python3
"""
🚀 Fast IBM Quantum Benchmark (9 minutes max)
Testa backends disponíveis com API corrigida do Qiskit Runtime
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path

import structlog

logger = structlog.get_logger(__name__)


def benchmark_ibm_quantum():
    """Execute benchmark rápido em backends IBM."""
    try:
        from qiskit import QuantumCircuit
        from qiskit_ibm_runtime import QiskitRuntimeService, Sampler

        # Backends disponíveis (plan 'open' não suporta Session)
        backends_to_test = [
            "ibm_fez",  # 0 fila (Omnimind)
            "ibm_torino",  # 0 fila (Omnimind)
            "ibm_marrakesh",  # 13k fila (skip)
        ]

        # Configurar token
        token = os.getenv("IBM_API_KEY")
        if not token:
            logger.error("ibm_token_missing", msg="IBM_API_KEY not set")
            return

        logger.info("initializing_qiskit_runtime", token_preview=token[:10] + "...")

        # Inicializar service
        try:
            service = QiskitRuntimeService(channel="ibm_cloud", token=token)
        except ValueError:
            service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token)

        logger.info("connected_to_ibm_quantum")

        # Dados de benchmark
        benchmark_data = {
            "timestamp": datetime.now().isoformat(),
            "backends": {},
            "metadata": {
                "total_backends_tested": 0,
                "successful_runs": 0,
                "failed_runs": 0,
                "total_time_seconds": 0,
            },
        }

        start_time = time.time()
        max_time = 540  # 9 minutos em segundos

        # Testar cada backend
        for backend_name in backends_to_test:
            if time.time() - start_time > max_time:
                logger.warning("time_limit_reached", msg="9 minutes exceeded")
                break

            logger.info("testing_backend", backend=backend_name)

            try:
                # Skip marrakesh (muita fila)
                if "marrakesh" in backend_name:
                    logger.info(
                        "skipping_backend",
                        backend=backend_name,
                        reason="too_many_jobs",
                    )
                    continue

                # Criar circuito simples: Bell state
                qc = QuantumCircuit(2, 2, name="bell_state")
                qc.h(0)
                qc.cx(0, 1)
                qc.measure([0, 1], [0, 1])

                logger.info("created_circuit", backend=backend_name, qubits=2)

                # Executar com Sampler V2 usando backend name
                logger.info("backend_selected", backend=backend_name)

                # Transpilação automática para o backend
                from qiskit import transpile

                backend_obj = service.backend(backend_name)
                qc_transpiled = transpile(qc, backend=backend_obj)

                logger.info(
                    "circuit_transpiled",
                    backend=backend_name,
                    original_gates=len(qc.data),
                    transpiled_gates=len(qc_transpiled.data),
                )

                # Use Sampler direto com backend object (modo job)
                sampler = Sampler(mode=backend_obj)
                job = sampler.run([qc_transpiled], shots=100)

                logger.info("job_submitted", backend=backend_name, job_id=str(job.job_id()))

                # Esperar resultado
                result = job.result(timeout=120)

                # Extrair counts (V2 API - DataBin object)
                data_bin = result[0].data
                if hasattr(data_bin, "c"):
                    # Medidas classicamente armazenadas em 'c'
                    counts_obj = data_bin.c
                    counts = counts_obj.get_counts()
                else:
                    # Tentar acesso direto
                    counts = getattr(data_bin, "get_counts", lambda: {})()

                # Dados de benchmark
                benchmark_data["backends"][backend_name] = {
                    "status": "success",
                    "job_id": str(job.job_id()),
                    "counts": counts,
                    "total_shots": 100,
                }

                benchmark_data["metadata"]["successful_runs"] += 1

                logger.info(
                    "benchmark_complete",
                    backend=backend_name,
                    status="success",
                    counts=counts,
                )

            except Exception as e:
                logger.error("benchmark_failed", backend=backend_name, error=str(e))

                benchmark_data["backends"][backend_name] = {
                    "status": "failed",
                    "error": str(e),
                }

                benchmark_data["metadata"]["failed_runs"] += 1

            benchmark_data["metadata"]["total_backends_tested"] += 1

        benchmark_data["metadata"]["total_time_seconds"] = time.time() - start_time

        # Salvar resultados
        output_dir = Path("/home/fahbrain/projects/omnimind/data/benchmarks")
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"fast_ibm_benchmark_{timestamp}.json"

        with open(output_file, "w") as f:
            json.dump(benchmark_data, f, indent=2)

        logger.info("benchmark_results_saved", file=str(output_file))

        # Resumo
        print("\n" + "=" * 60)
        print("📊 IBM QUANTUM BENCHMARK RESULTS")
        print("=" * 60)
        print(f"⏱️  Total Time: {benchmark_data['metadata']['total_time_seconds']:.1f}s")
        print(
            f"✅ Successful: {benchmark_data['metadata']['successful_runs']} "
            f"❌ Failed: {benchmark_data['metadata']['failed_runs']}"
        )
        print("\nBackend Results:")

        for backend_name, data in benchmark_data["backends"].items():
            if data["status"] == "success":
                print(
                    f"\n  {backend_name}:"
                    f"\n    Counts: {data['counts']}"
                    f"\n    Shots: {data['total_shots']}"
                )
            else:
                print(f"\n  {backend_name}: ❌ {data['error'][:50]}")

        print(f"\n📁 Results saved: {output_file}")
        print("=" * 60 + "\n")

        return benchmark_data

    except ImportError as e:
        logger.error("import_error", msg=str(e))
        print("❌ Instale: pip install qiskit-ibm-runtime")


if __name__ == "__main__":
    benchmark_ibm_quantum()
