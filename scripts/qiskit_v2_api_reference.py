#!/usr/bin/env python3
"""Quick Reference: Qiskit Runtime V2 API Patterns."""

import json
import structlog
from datetime import datetime
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

logger = structlog.get_logger(__name__)


def pattern_1_basic_execution():
    """PATTERN 1: EXECUÇÃO BÁSICA (Job Mode)."""
    # Inicializar serviço (usa .env IBM_API_KEY)
    service = QiskitRuntimeService()
    backend = service.backend("ibm_fez")

    # Criar e transpilar circuito
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    qc_transpiled = transpile(qc, backend=backend)

    # Executar com Sampler
    sampler = Sampler(mode=backend)
    job = sampler.run([qc_transpiled], shots=100)
    result = job.result()
    counts = result[0].data.c.get_counts()
    print(f"Counts: {counts}")
    return counts


def execute_with_fallback(circuit, backend_name="ibm_fez", shots=100):
    """Execute em IBM com fallback para simulator."""
    try:
        service = QiskitRuntimeService()
        backend = service.backend(backend_name)
        qc_transpiled = transpile(circuit, backend=backend)

        sampler = Sampler(mode=backend)
        job = sampler.run([qc_transpiled], shots=shots)
        result = job.result(timeout=600)

        counts = result[0].data.c.get_counts()
        logger.info(
            "ibm_execution_success",
            backend=backend_name,
            shots=shots,
            num_outcomes=len(counts),
        )
        return counts

    except Exception as e:
        logger.warning("ibm_execution_failed", error=str(e), fallback_to="simulator")
        simulator = AerSimulator()
        qc_transpiled = transpile(circuit, backend=simulator)
        sampler = Sampler(mode=simulator)
        job = sampler.run([qc_transpiled], shots=shots)
        result = job.result()
        counts = result[0].data.c.get_counts()
        return counts


def benchmark_multiple_backends(circuit, backend_names, shots=100):
    """Executar circuito em múltiplos backends."""
    service = QiskitRuntimeService()
    results = {}

    for backend_name in backend_names:
        try:
            backend = service.backend(backend_name)
            qc_transpiled = transpile(circuit, backend=backend)

            sampler = Sampler(mode=backend)
            job = sampler.run([qc_transpiled], shots=shots)
            result = job.result(timeout=600)

            counts = result[0].data.c.get_counts()
            results[backend_name] = {
                "status": "success",
                "job_id": str(job.job_id()),
                "counts": counts,
                "total_shots": shots,
            }
            logger.info(
                "backend_execution_complete",
                backend=backend_name,
                job_id=results[backend_name]["job_id"],
            )

        except Exception as e:
            results[backend_name] = {"status": "failed", "error": str(e)}
            logger.error("backend_execution_failed", backend=backend_name, error=str(e))

    return results


def fast_benchmark(circuit, max_backends=2, timeout=600):
    """Execução rápida em N backends com melhor latência."""
    service = QiskitRuntimeService()
    results = {
        "timestamp": datetime.utcnow().isoformat(),
        "backends": {},
        "metadata": {
            "successful_runs": 0,
            "failed_runs": 0,
            "total_backends_tested": 0,
        },
    }

    backends = service.backends(filters=lambda x: x.status().operational)[:max_backends]
    results["metadata"]["total_backends_tested"] = len(backends)

    for backend in backends:
        try:
            qc_transpiled = transpile(circuit, backend=backend)
            sampler = Sampler(mode=backend)
            job = sampler.run([qc_transpiled], shots=100)
            result = job.result(timeout=timeout)

            counts = result[0].data.c.get_counts()
            results["backends"][backend.name] = {
                "status": "success",
                "job_id": str(job.job_id()),
                "counts": counts,
                "total_shots": 100,
            }
            results["metadata"]["successful_runs"] += 1

        except Exception as e:
            results["backends"][backend.name] = {"status": "failed", "error": str(e)}
            results["metadata"]["failed_runs"] += 1

    # Salvar resultados
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"benchmark_{timestamp}.json"
    with open(filename, "w") as f:
        json.dump(results, f, indent=2)

    return results


if __name__ == "__main__":
    # Teste rápido
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])

    # Usar fallback para teste seguro
    try:
        counts = execute_with_fallback(qc, "ibm_fez", shots=100)
        print(f"✅ Execution success: {counts}")
    except Exception as e:
        print(f"❌ Execution failed: {e}")
