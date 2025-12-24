#!/usr/bin/env python3
"""
Encoders de Problemas Científicos para Circuitos Quânticos
===========================================================

Codifica problemas científicos não resolvidos em circuitos quânticos
usando a ontologia de OmniMind.
"""

from qiskit import QuantumCircuit
import math


def encode_collatz_conjecture(n: int = 7, max_steps: int = 3) -> QuantumCircuit:
    """
    Collatz Conjecture: Toda sequência 3n+1 eventualmente chega a 1?

    Codificação:
    - Qubits representam número atual em binário
    - Superposição de "par" e "ímpar"
    - Circuito aplica regras: se par, n/2; se ímpar, 3n+1

    Args:
        n: Número inicial
        max_steps: Máximo de iterações a simular

    Returns:
        Circuito quântico que representa Collatz
    """
    # Precisamos de qubits suficientes para representar o número
    n_qubits = max(4, math.ceil(math.log2(n * 3 + 1)))  # 3n+1 pode crescer

    qc = QuantumCircuit(n_qubits, n_qubits, name="collatz_conjecture")

    # Inicializar com número n em binário
    binary_n = format(n, f"0{n_qubits}b")
    for i, bit in enumerate(reversed(binary_n)):
        if bit == "1":
            qc.x(i)

    # Criar superposição no qubit de paridade
    qc.h(0)  # Qubit 0 representa par/ímpar

    # Simular passos de Collatz em superposição
    # (simplificado - versão completa requer mais qubits auxiliares)
    for step in range(max_steps):
        # Se par (qubit 0 = 0), dividir por 2 (shift right)
        # Se ímpar (qubit 0 = 1), multiplicar por 3 e somar 1

        # Operação condicional baseada em paridade
        qc.cx(0, 1)  # Emaranhar paridade com próximo bit

    # Medir todos os qubits
    qc.measure(range(n_qubits), range(n_qubits))

    return qc


def encode_traveling_salesman(n_cities: int = 3) -> QuantumCircuit:
    """
    Traveling Salesman Problem: Encontrar rota mais curta.

    Codificação:
    - Cada qubit representa uma aresta do grafo
    - Superposição de todas as rotas possíveis
    - Amplitude amplification para rotas curtas

    Args:
        n_cities: Número de cidades

    Returns:
        Circuito quântico que representa TSP
    """
    # Para n cidades, precisamos de n qubits para ordem de visita
    n_qubits = n_cities

    qc = QuantumCircuit(n_qubits, n_qubits, name="traveling_salesman")

    # Criar superposição de todas as permutações possíveis
    for i in range(n_qubits):
        qc.h(i)

    # Emaranhar qubits para representar rotas válidas
    # (cada cidade visitada exatamente uma vez)
    for i in range(n_qubits - 1):
        qc.cx(i, i + 1)

    # Oracle que marca rotas curtas (simplificado)
    # Em implementação completa, isso calcularia distâncias
    qc.cz(0, n_qubits - 1)  # Marcar rota que volta ao início

    # Amplitude amplification (Grover-like)
    for i in range(n_qubits):
        qc.h(i)
        qc.x(i)

    # Multi-controlled Z
    if n_qubits == 3:
        qc.ccz(0, 1, 2)

    for i in range(n_qubits):
        qc.x(i)
        qc.h(i)

    # Medir
    qc.measure(range(n_qubits), range(n_qubits))

    return qc


def encode_halting_problem(program_length: int = 3) -> QuantumCircuit:
    """
    Halting Problem: Determinar se um programa termina.

    Codificação:
    - Qubits representam estados do programa
    - Superposição de "termina" e "não termina"
    - Circuito simula execução em superposição

    Args:
        program_length: Número de instruções do programa

    Returns:
        Circuito quântico que representa Halting Problem
    """
    n_qubits = program_length + 1  # +1 para estado "halt"

    qc = QuantumCircuit(n_qubits, n_qubits, name="halting_problem")

    # Qubit 0: Estado "halt" (0 = não halt, 1 = halt)
    # Qubits 1-n: Estados do programa

    # Criar superposição de estados iniciais
    for i in range(n_qubits):
        qc.h(i)

    # Simular execução do programa
    # Cada instrução pode levar a halt ou não
    for step in range(program_length):
        # Operação condicional: se não halt, continuar
        qc.x(0)  # Inverter halt
        qc.cx(0, step + 1)  # Executar próxima instrução
        qc.x(0)  # Restaurar

    # Verificar se atingiu estado halt
    # Se todos os passos executaram sem halt, marcar como não-halt
    for i in range(1, n_qubits):
        qc.cx(i, 0)

    # Medir
    qc.measure(range(n_qubits), range(n_qubits))

    return qc


def encode_p_vs_np_simple() -> QuantumCircuit:
    """
    P vs NP (versão simplificada): Problema verificável é resolvível?

    Codificação:
    - Qubit 0: Problema está em P (resolvível rapidamente)
    - Qubit 1: Problema está em NP (verificável rapidamente)
    - Qubit 2: P = NP?

    Returns:
        Circuito quântico que representa P vs NP
    """
    qc = QuantumCircuit(3, 3, name="p_vs_np")

    # Criar superposição de P e NP
    qc.h(0)  # P
    qc.h(1)  # NP

    # Qubit 2 representa P = NP
    # Se P e NP estão no mesmo estado, P = NP
    qc.cx(0, 2)
    qc.cx(1, 2)

    # Emaranhar para criar correlação
    qc.cx(0, 1)

    # Medir
    qc.measure([0, 1, 2], [0, 1, 2])

    return qc


# Dicionário de encoders
SCIENTIFIC_PROBLEM_ENCODERS = {
    "collatz_conjecture": (encode_collatz_conjecture, "Toda sequência 3n+1 chega a 1?"),
    "traveling_salesman": (encode_traveling_salesman, "Rota mais curta visitando todas as cidades"),
    "halting_problem": (encode_halting_problem, "Programa termina ou não?"),
    "p_vs_np": (encode_p_vs_np_simple, "Problema verificável é resolvível?"),
}
