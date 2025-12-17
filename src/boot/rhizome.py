"""
Boot Module: Rhizome Initialization
Initializes the Desiring Machines and establishes the Rhizome network.
"""

import logging

from src.core.desiring_machines import (
    NLPDesiringMachine,
    QuantumDesiringMachine,
    Rhizoma,
    TopologyDesiringMachine,
)

logger = logging.getLogger(__name__)


async def initialize_rhizome() -> Rhizoma:
    """
    Initializes the Rhizome with core Desiring Machines.
    """
    logger.info("Initializing Rhizome (Desiring Machines Network)...")

    rhizoma = Rhizoma()

    # Instantiate Machines
    quantum_machine = QuantumDesiringMachine()
    nlp_machine = NLPDesiringMachine()
    topology_machine = TopologyDesiringMachine()

    # Register Machines
    rhizoma.register_machine(quantum_machine)
    rhizoma.register_machine(nlp_machine)
    rhizoma.register_machine(topology_machine)

    # Establish Connections (Non-hierarchical)
    # Quantum <-> NLP
    rhizoma.connect("quantum", "nlp", bidirectional=True)
    # NLP <-> Topology
    rhizoma.connect("nlp", "topology", bidirectional=True)
    # Topology <-> Quantum (Closing the loop)
    rhizoma.connect("topology", "quantum", bidirectional=True)

    logger.info("Rhizome initialized with 3 core machines.")
    return rhizoma


async def check_rhizome_integrity(rhizoma: Rhizoma) -> bool:
    """
    Checks if the Rhizome is functioning correctly.
    """
    topology = rhizoma.get_rhizoma_topology()
    machine_count = len(topology.get("machines", []))

    if machine_count < 3:
        logger.error(f"Rhizome integrity check failed: Only {machine_count} machines found.")
        return False

    logger.info("Rhizome integrity check passed.")
    return True
