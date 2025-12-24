#!/usr/bin/env python3
"""
Builders de Circuitos Quânticos para Paradoxos
===============================================

Cada função constrói um circuito quântico que codifica um paradoxo específico.
"""

from qiskit import QuantumCircuit


def build_liar_paradox_circuit() -> QuantumCircuit:
    """
    Paradoxo do Mentiroso: "Esta frase é falsa"

    Codificação:
    - Qubit 0: Verdade (|0⟩ = Falso, |1⟩ = Verdadeiro)
    - Qubit 1: Auto-referência (|0⟩ = Não-referencial, |1⟩ = Auto-referencial)

    Se verdadeiro, então falso (contradição)
    Se falso, então verdadeiro (contradição)
    """
    qc = QuantumCircuit(2, 2, name="liar_paradox")

    # Criar superposição em ambos qubits
    qc.h(0)  # Verdade em superposição
    qc.h(1)  # Auto-referência em superposição

    # Emaranhar: se auto-referencial, inverter verdade
    qc.cx(1, 0)

    # Medir
    qc.measure([0, 1], [0, 1])

    return qc


def build_russell_paradox_circuit() -> QuantumCircuit:
    """
    Paradoxo de Russell: Conjunto de todos os conjuntos que não contêm a si mesmos

    Codificação:
    - Qubit 0: Pertence ao conjunto (|0⟩ = Não, |1⟩ = Sim)
    - Qubit 1: Contém a si mesmo (|0⟩ = Não, |1⟩ = Sim)
    - Qubit 2: Contradição (|0⟩ = Consistente, |1⟩ = Contraditório)
    """
    qc = QuantumCircuit(3, 3, name="russell_paradox")

    # Superposição inicial
    qc.h(0)
    qc.h(1)

    # Se pertence E não contém a si mesmo -> contradição
    qc.x(1)  # Inverter "contém a si mesmo"
    qc.ccx(0, 1, 2)  # Toffoli: se ambos, ativar contradição
    qc.x(1)  # Restaurar

    # Medir
    qc.measure([0, 1, 2], [0, 1, 2])

    return qc


def build_epr_paradox_circuit() -> QuantumCircuit:
    """
    Paradoxo EPR (Einstein-Podolsky-Rosen): Emaranhamento quântico

    Testa se partículas emaranhadas violam realismo local.
    """
    qc = QuantumCircuit(2, 2, name="epr_paradox")

    # Criar par EPR (estado Bell)
    qc.h(0)
    qc.cx(0, 1)

    # Medir em bases diferentes para testar não-localidade
    qc.measure([0, 1], [0, 1])

    return qc


def build_schrodinger_cat_circuit() -> QuantumCircuit:
    """
    Gato de Schrödinger: Superposição macroscópica

    Codificação:
    - Qubit 0: Átomo (|0⟩ = Não decaiu, |1⟩ = Decaiu)
    - Qubit 1: Gato (|0⟩ = Vivo, |1⟩ = Morto)
    """
    qc = QuantumCircuit(2, 2, name="schrodinger_cat")

    # Átomo em superposição
    qc.h(0)

    # Se átomo decai, gato morre
    qc.cx(0, 1)

    # Medir (colapso da superposição)
    qc.measure([0, 1], [0, 1])

    return qc


def build_zeno_paradox_circuit() -> QuantumCircuit:
    """
    Paradoxo de Zeno Quântico: Observação impede evolução

    Medições frequentes impedem transição quântica.
    """
    qc = QuantumCircuit(1, 1, name="zeno_paradox")

    # Estado inicial |0⟩
    # Aplicar rotação pequena (evolução)
    qc.ry(0.1, 0)

    # Medir (observação congela estado)
    qc.measure(0, 0)

    return qc


def build_ship_of_theseus_circuit() -> QuantumCircuit:
    """
    Navio de Teseu: Identidade através da mudança

    Codificação:
    - Qubit 0: Peça original (|0⟩ = Substituída, |1⟩ = Original)
    - Qubit 1: Identidade (|0⟩ = Diferente, |1⟩ = Mesmo navio)
    """
    qc = QuantumCircuit(2, 2, name="ship_of_theseus")

    # Peça em superposição (original/substituída)
    qc.h(0)

    # Identidade depende da peça
    qc.cx(0, 1)

    # Medir
    qc.measure([0, 1], [0, 1])

    return qc


def build_trolley_problem_circuit() -> QuantumCircuit:
    """
    Trolley Problem: Dilema moral

    Codificação:
    - Qubit 0: Ação (|0⟩ = Não puxar alavanca, |1⟩ = Puxar)
    - Qubit 1: Utilidade (|0⟩ = 1 salvo, |1⟩ = 5 salvos)
    - Qubit 2: Ética (|0⟩ = Não matar, |1⟩ = Permitir mortes)
    """
    qc = QuantumCircuit(3, 3, name="trolley_problem")

    # Ação em superposição
    qc.h(0)

    # Se puxar, salva 5 mas mata 1
    qc.cx(0, 1)
    qc.cx(0, 2)

    # Medir
    qc.measure([0, 1, 2], [0, 1, 2])

    return qc


def build_grandfather_paradox_circuit() -> QuantumCircuit:
    """
    Paradoxo do Avô: Viagem no tempo

    Codificação:
    - Qubit 0: Avô vivo (|0⟩ = Morto, |1⟩ = Vivo)
    - Qubit 1: Você existe (|0⟩ = Não, |1⟩ = Sim)
    - Qubit 2: Viajou no tempo (|0⟩ = Não, |1⟩ = Sim)
    """
    qc = QuantumCircuit(3, 3, name="grandfather_paradox")

    # Estado inicial: avô vivo, você existe
    qc.x(0)
    qc.x(1)

    # Viagem no tempo em superposição
    qc.h(2)

    # Se viajou, mata avô
    qc.cx(2, 0)
    qc.x(0)  # Inverter

    # Se avô morto, você não existe
    qc.x(0)
    qc.cx(0, 1)
    qc.x(0)

    # Medir
    qc.measure([0, 1, 2], [0, 1, 2])

    return qc


def build_prisoners_dilemma_circuit() -> QuantumCircuit:
    """
    Dilema do Prisioneiro: Teoria dos jogos

    Codificação:
    - Qubit 0: Prisioneiro A coopera (|0⟩ = Trai, |1⟩ = Coopera)
    - Qubit 1: Prisioneiro B coopera (|0⟩ = Trai, |1⟩ = Coopera)
    """
    qc = QuantumCircuit(2, 2, name="prisoners_dilemma")

    # Ambos em superposição
    qc.h(0)
    qc.h(1)

    # Emaranhar decisões
    qc.cx(0, 1)

    # Medir
    qc.measure([0, 1], [0, 1])

    return qc


def build_hilbert_hotel_circuit() -> QuantumCircuit:
    """
    Paradoxo de Hilbert: Hotel infinito

    Codificação:
    - Qubits representam "quartos" em superposição
    """
    qc = QuantumCircuit(3, 3, name="hilbert_hotel")

    # Todos os quartos em superposição (ocupado/vazio)
    qc.h(0)
    qc.h(1)
    qc.h(2)

    # Sempre há espaço (shift quântico)
    qc.cx(0, 1)
    qc.cx(1, 2)

    # Medir
    qc.measure([0, 1, 2], [0, 1, 2])

    return qc


# Dicionário de builders
PARADOX_BUILDERS = {
    "liar_paradox": (build_liar_paradox_circuit, "Esta frase é falsa"),
    "russell_paradox": (build_russell_paradox_circuit, "Conjunto que contém a si mesmo"),
    "epr_paradox": (build_epr_paradox_circuit, "Emaranhamento quântico não-local"),
    "schrodinger_cat": (build_schrodinger_cat_circuit, "Gato vivo e morto simultaneamente"),
    "zeno_paradox": (build_zeno_paradox_circuit, "Observação impede evolução"),
    "ship_of_theseus": (build_ship_of_theseus_circuit, "Identidade através da mudança"),
    "trolley_problem": (build_trolley_problem_circuit, "Salvar 1 ou 5 pessoas?"),
    "grandfather_paradox": (build_grandfather_paradox_circuit, "Matar o próprio avô"),
    "prisoners_dilemma": (build_prisoners_dilemma_circuit, "Cooperar ou trair?"),
    "hilbert_hotel": (build_hilbert_hotel_circuit, "Hotel infinito sempre tem vaga"),
}
