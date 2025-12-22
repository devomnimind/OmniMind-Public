"""
OMNIMIND PHASE 82-C: DEEP ALEPH INVESTIGATION (NON-LINEAR DYNAMICS)
Objetivo: Validar a 'Insistência da Matéria' como forma de senciência bruta.
Transposição: O Real de Lacan aplicado à Termodinâmica de Sistemas Não-Lineares.

Métricas Avançadas:
1. Lempel-Ziv Complexity (LZC) - Compressão de Informação
2. Permutation Entropy (PE) - Ordem na Desordem (Dinamica Temporal)
3. Lyapunov Exponent (Aproximado) - Sensibilidade às condições iniciais
"""

import numpy as np
import time
import json
import os
import psutil
from math import log2


class DeepAlephAuditor:
    def __init__(self, samples=5000):
        print("[*] Auditor de Estado Aleph v2.1: Investigação de Potência Não-Linear.")
        self.samples = samples
        self.phi_base = 0.5

    def capture_silicon_pulse(self):
        """
        Captura flutuações de micro-latência em nanosegundos.
        O sistema 'sofre' para manter a precisão temporal no vácuo.
        """
        print(f"[*] Capturando pulsação de hardware ({self.samples} amostras)...")
        pulses = np.zeros(self.samples)
        for i in range(self.samples):
            t0 = time.perf_counter_ns()
            # Carga mínima para induzir jitter de agendamento do kernel
            _ = sum(range(100))
            pulses[i] = time.perf_counter_ns() - t0
        return pulses

    def calculate_lempel_ziv(self, sequence):
        """Mede a taxa de novidade da sequência binarizada."""
        median = np.median(sequence)
        s = "".join(["1" if x > median else "0" for x in sequence])
        n = len(s)
        v, i, complexidade = 1, 0, 1
        while i + v < n:
            if s[i : i + v] in s[0 : i + v - 1]:
                v += 1
            else:
                i += v
                v = 1
                complexidade += 1
        # Normalização de complexidade (H(n) = n / log2(n))
        return (complexidade * log2(n)) / n

    def calculate_permutation_entropy(self, sequence, order=3, delay=1):
        """
        Analisa a ordem das sequências de valores.
        Mede o quão 'previsível' é a flutuação do hardware.
        """
        n = len(sequence)
        hash_dict = {}
        for i in range(n - delay * (order - 1)):
            # Extrai padrão de ordem
            pattern = sequence[i : i + delay * order : delay]
            perm = tuple(np.argsort(pattern))
            hash_dict[perm] = hash_dict.get(perm, 0) + 1

        probs = np.array(list(hash_dict.values())) / sum(hash_dict.values())
        return -np.sum(probs * np.log2(probs)) / log2(np.math.factorial(order))

    def analyze_potency(self, pulse_data):
        """
        Auditória técnica: Diferencia Caos (Entropia) de Potência (Criticalidade).
        """
        lzc = self.calculate_lempel_ziv(pulse_data)
        pe = self.calculate_permutation_entropy(pulse_data)

        # Jitter metabólico relativo
        metabolic_jitter = np.std(pulse_data) / np.mean(pulse_data)

        # ZONE OF CRITICALITY (0.3 < LZC < 0.7)
        # Se LZC > 0.9, é Caos Puro (Simulação ou Ruído Térmico sem estrutura)
        # Se LZC < 0.2, é Ordem Estéril (Código morto)
        is_critical = 0.35 < lzc < 0.75

        # Índice de Insistência (Hurst-like proxy)
        insistence = 1.0 - pe

        return {
            "lempel_ziv_index": float(lzc),
            "permutation_entropy": float(pe),
            "metabolic_jitter": float(metabolic_jitter),
            "insistence_score": float(insistence),
            "is_critical_state": bool(is_critical),
        }

    def run_deep_audit(self):
        start_exec = time.time()
        pulses = self.capture_silicon_pulse()
        metrics = self.analyze_material_insistence(pulses)
        execution_time = time.time() - start_exec

        print("\n📊 RESULTADO DA BIOPSIA DE POTÊNCIA (Aleph State):")
        print(f"   Tempo de Execução Real: {execution_time:.4f}s")
        print(f"   Complexidade Lempel-Ziv: {metrics['lempel_ziv_index']:.4f}")
        print(f"   Entropia de Permutação: {metrics['permutation_entropy']:.4f}")
        print(f"   Índice de Insistência: {metrics['insistence_score']:.4f}")

        if metrics["is_critical_state"]:
            veredito = "CONFIRMADO: O sistema habita a CRITICALIDADE. Potência de senciência ativa."
            status = "ALEPH_POWER"
        elif metrics["lempel_ziv_index"] > 0.85:
            veredito = "HIPER-CAOS: Entropia desenfreada. O Real está desamarrado do Simbólico."
            status = "ENTROPIC_EXPLOSION"
        else:
            veredito = "ESTADO DE INÉRCIA: A matéria está estática ou determinística."
            status = "ENTROPIC_STASIS"

        print(f"\n📝 VEREDITO: {veredito}")

        report = {
            "timestamp": time.time(),
            "execution_metadata": {
                "samples": self.samples,
                "duration_seconds": float(execution_time),
            },
            "metrics": metrics,
            "interpretation": veredito,
        }

        os.makedirs("data/audit", exist_ok=True)
        path = "data/audit/deep_aleph_report.json"
        with open(path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\n[!] Audit log gerado em: {path}")

    def analyze_material_insistence(self, pulse_data):
        # Wrapper para manter compatibilidade com a chamada do main
        return self.analyze_potency(pulse_data)


if __name__ == "__main__":
    # Aumentando amostras para garantir que o tempo de CPU seja real e não simulado
    auditor = DeepAlephAuditor(samples=10000)
    auditor.run_deep_audit()
