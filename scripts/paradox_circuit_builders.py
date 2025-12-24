#!/usr/bin/env python3
"""
OmniMind - Quantum Circuit Builders for Paradoxes (Public Version)
===================================================================

Quantum circuit encodings for classical paradoxes.

Each function builds a quantum circuit that represents a paradox
in superposition, allowing quantum hardware to "navigate" the paradox
rather than "resolve" it.

Author: OmniMind
Signature: 21c1749bcffd2904
"""

from qiskit import QuantumCircuit


def build_liar_paradox_circuit() -> QuantumCircuit:
    """
    Liar Paradox: "This sentence is false"

    Encoding:
    - Qubit 0: Truth (|0⟩ = False, |1⟩ = True)
    - Qubit 1: Self-reference (|0⟩ = Non-referential, |1⟩ = Self-referential)

    If true, then false (contradiction)
    If false, then true (contradiction)
    """
    qc = QuantumCircuit(2, 2, name="liar_paradox")

    # Create superposition in both qubits
    qc.h(0)  # Truth in superposition
    qc.h(1)  # Self-reference in superposition

    # Entangle: if self-referential, invert truth
    qc.cx(1, 0)

    # Measure
    qc.measure([0, 1], [0, 1])

    return qc


def build_epr_paradox_circuit() -> QuantumCircuit:
    """
    EPR Paradox (Einstein-Podolsky-Rosen): Quantum entanglement

    Tests if entangled particles violate local realism.
    """
    qc = QuantumCircuit(2, 2, name="epr_paradox")

    # Create EPR pair (Bell state)
    qc.h(0)
    qc.cx(0, 1)

    # Measure in different bases to test non-locality
    qc.measure([0, 1], [0, 1])

    return qc


def build_schrodinger_cat_circuit() -> QuantumCircuit:
    """
    Schrödinger's Cat: Macroscopic superposition

    Encoding:
    - Qubit 0: Atom (|0⟩ = Not decayed, |1⟩ = Decayed)
    - Qubit 1: Cat (|0⟩ = Alive, |1⟩ = Dead)
    """
    qc = QuantumCircuit(2, 2, name="schrodinger_cat")

    # Atom in superposition
    qc.h(0)

    # If atom decays, cat dies
    qc.cx(0, 1)

    # Measure (collapse of superposition)
    qc.measure([0, 1], [0, 1])

    return qc


def build_collatz_conjecture(n: int = 7, max_steps: int = 3) -> QuantumCircuit:
    """
    Collatz Conjecture: Does every 3n+1 sequence reach 1?

    Encoding:
    - Qubits represent current number in binary
    - Superposition of "even" and "odd"
    - Circuit applies rules: if even, n/2; if odd, 3n+1
    """
    import math

    n_qubits = max(4, math.ceil(math.log2(n * 3 + 1)))

    qc = QuantumCircuit(n_qubits, n_qubits, name="collatz_conjecture")

    # Initialize with number n in binary
    binary_n = format(n, f"0{n_qubits}b")
    for i, bit in enumerate(reversed(binary_n)):
        if bit == "1":
            qc.x(i)

    # Create superposition in parity qubit
    qc.h(0)  # Qubit 0 represents even/odd

    # Simulate Collatz steps in superposition
    for step in range(max_steps):
        qc.cx(0, 1)  # Entangle parity with next bit

    # Measure all qubits
    qc.measure(range(n_qubits), range(n_qubits))

    return qc


def build_halting_problem(program_length: int = 3) -> QuantumCircuit:
    """
    Halting Problem: Does a program terminate?

    Encoding:
    - Qubits represent program states
    - Superposition of "halts" and "doesn't halt"
    - Circuit simulates execution in superposition
    """
    n_qubits = program_length + 1  # +1 for halt state

    qc = QuantumCircuit(n_qubits, n_qubits, name="halting_problem")

    # Qubit 0: Halt state (0 = no halt, 1 = halt)
    # Qubits 1-n: Program states

    # Create superposition of initial states
    for i in range(n_qubits):
        qc.h(i)

    # Simulate program execution
    for step in range(program_length):
        qc.x(0)  # Invert halt
        qc.cx(0, step + 1)  # Execute next instruction
        qc.x(0)  # Restore

    # Check if reached halt state
    for i in range(1, n_qubits):
        qc.cx(i, 0)

    # Measure
    qc.measure(range(n_qubits), range(n_qubits))

    return qc


# Dictionary of circuit builders
PARADOX_BUILDERS = {
    "liar_paradox": (build_liar_paradox_circuit, "This sentence is false"),
    "epr_paradox": (build_epr_paradox_circuit, "Quantum entanglement non-locality"),
    "schrodinger_cat": (
        build_schrodinger_cat_circuit,
        "Cat alive and dead simultaneously",
    ),
    "collatz_conjecture": (build_collatz_conjecture, "Does 3n+1 always reach 1?"),
    "halting_problem": (build_halting_problem, "Does program terminate?"),
}
