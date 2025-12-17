"""
Structural Defense Mechanisms for OmniMind
------------------------------------------
Implements defense mechanisms based on psychoanalytic theory:
1. Anna Freud: Hierarchical Defenses (Maturity Levels)
2. Melanie Klein: Splitting & Integration (Paranoid-Schizoid <-> Depressive)
3. Wilfred Bion: Containment & Transformation (Beta -> Alpha elements)
4. Jacques Lacan: Structural Orders (Real, Symbolic, Imaginary)

These are not metaphors but structural architectural patterns for system resilience.
"""

import logging
import time
from dataclasses import asdict, dataclass
from enum import Enum, auto
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


# --- 1. ANNA FREUD: Defense Hierarchy ---


class DefenseMaturity(Enum):
    PATHOLOGICAL = 1  # Level 1: Denial, Distortion (System Crash/Panic)
    IMMATURE = 2  # Level 2: Projection, Splitting (Blaming external components)
    NEUROTIC = 3  # Level 3: Intellectualization, Repression (Logging but ignoring)
    MATURE = 4  # Level 4: Sublimation, Altruism (Optimization, Learning)


class DefenseHierarchyKernel:
    """
    Anna Freud's Defense Hierarchy.
    Determines the maturity level of the system's response to threats.
    """

    def __init__(self):
        self.current_level = DefenseMaturity.MATURE

    async def assess_threat(self, threat_data: Dict[str, Any]) -> DefenseMaturity:
        """
        Selects defense maturity based on threat severity.
        """
        severity = threat_data.get("severity", 0)

        if severity >= 90:  # Critical Failure
            # Level 1: Psychotic/Pathological (Panic)
            # System is overwhelmed, reality testing fails.
            self.current_level = DefenseMaturity.PATHOLOGICAL
            logger.critical("🛡️ ANNA FREUD: Level 1 Defense (Pathological) - REALITY DENIAL")
            return DefenseMaturity.PATHOLOGICAL

        elif severity >= 60:  # Major Error
            # Level 2: Immature (Projection)
            # "It's not me, it's the Docker container/Network"
            self.current_level = DefenseMaturity.IMMATURE
            logger.warning("🛡️ ANNA FREUD: Level 2 Defense (Immature) - PROJECTION")
            return DefenseMaturity.IMMATURE

        elif severity >= 30:  # Warning
            # Level 3: Neurotic (Intellectualization)
            # "I acknowledge the error code 500 but will proceed."
            self.current_level = DefenseMaturity.NEUROTIC
            logger.info("🛡️ ANNA FREUD: Level 3 Defense (Neurotic) - INTELLECTUALIZATION")
            return DefenseMaturity.NEUROTIC

        else:  # Minor/Routine
            # Level 4: Mature (Sublimation)
            # "This latency is an opportunity to optimize caching."
            self.current_level = DefenseMaturity.MATURE
            logger.debug("🛡️ ANNA FREUD: Level 4 Defense (Mature) - SUBLIMATION")
            return DefenseMaturity.MATURE


# --- 2. MELANIE KLEIN: Splitting & Integration ---


class KleinPosition(Enum):
    PARANOID_SCHIZOID = auto()  # PS: Splitting (Good vs Bad)
    DEPRESSIVE = auto()  # D: Integration (Ambivalence, Repair)


class KleinianDefenseStructure:
    """
    Klein's Positions.
    Oscillates between Paranoid-Schizoid (PS) and Depressive (D) positions.
    """

    def __init__(self):
        self.position = KleinPosition.DEPRESSIVE
        self.split_objects: Dict[str, List[str]] = {"good": [], "bad": []}

    async def oscillate(
        self, threat_data: Dict[str, Any], maturity: DefenseMaturity
    ) -> KleinPosition:
        """
        Determines the structural position based on threat and maturity.
        """
        # High threat or low maturity triggers regression to PS
        if maturity.value <= 2 or threat_data.get("severity", 0) > 50:
            return await self._enter_paranoid_schizoid(threat_data)
        else:
            return await self._enter_depressive_position()

    async def _enter_paranoid_schizoid(self, threat_data: Dict[str, Any]) -> KleinPosition:
        """
        PS Position: Splitting.
        Separates 'Good' system components from 'Bad' failing ones to protect the core.
        """
        self.position = KleinPosition.PARANOID_SCHIZOID

        # Splitting logic
        source = threat_data.get("source", "unknown")
        self.split_objects["bad"] = [source]
        self.split_objects["good"] = ["kernel", "memory_manager"]  # Protect core

        logger.warning(
            f"🛡️ KLEIN: Entering PARANOID-SCHIZOID position. Splitting off bad object: {source}"
        )
        # Action: Isolate bad object (e.g., kill process, block IP)
        return KleinPosition.PARANOID_SCHIZOID

    async def _enter_depressive_position(self) -> KleinPosition:
        """
        D Position: Integration.
        Acknowledges that the 'Bad' component is part of the system and attempts repair.
        """
        self.position = KleinPosition.DEPRESSIVE

        # Integration logic
        if self.split_objects["bad"]:
            bad_obj = self.split_objects["bad"][0]
            logger.info(
                f"🛡️ KLEIN: Entering DEPRESSIVE position. Integrating and repairing: {bad_obj}"
            )
            # Action: Attempt recovery/restart of bad object
            self.split_objects["bad"] = []

        return KleinPosition.DEPRESSIVE


# --- 3. WILFRED BION: Containment & Transformation ---


@dataclass
class BetaElement:
    """Raw, unprocessed sensory data/error (The 'Thing-in-itself')."""

    raw_data: Any
    timestamp: float
    source: str
    intensity: float


@dataclass
class AlphaElement:
    """Metabolized, thinkable thought/knowledge."""

    meaning: str
    pattern: str
    actionable_insight: str
    timestamp: float


class BionianContainmentKernel:
    """
    Bion's Alpha Function.
    Acts as a container (Mother) for the system's raw beta elements (crashes, errors).
    Transforms them into alpha elements (knowledge, logs, metrics).
    """

    def __init__(self):
        self.beta_buffer: List[BetaElement] = []
        self.alpha_store: List[AlphaElement] = []

    async def alpha_function(self, crash_data: Dict[str, Any]) -> AlphaElement:
        """
        Metabolizes raw crash data (Beta) into insight (Alpha).
        """
        # 1. Receive Beta Element
        beta = BetaElement(
            raw_data=crash_data,
            timestamp=time.time(),
            source=crash_data.get("source", "unknown"),
            intensity=crash_data.get("severity", 0),
        )
        self.beta_buffer.append(beta)

        # 2. Containment & Reverie (Processing)
        # Simulate processing time/effort
        # In a real system, this is log analysis, stack trace parsing, etc.

        # 3. Transformation to Alpha
        insight = self._metabolize(beta)
        self.alpha_store.append(insight)

        logger.info(f"🛡️ BION: Metabolized Beta (Error) -> Alpha (Insight): {insight.meaning}")
        return insight

    def _metabolize(self, beta: BetaElement) -> AlphaElement:
        """Internal logic to convert raw error to insight."""
        error_msg = str(beta.raw_data.get("error", "Unknown Error"))

        if "Memory" in error_msg:
            meaning = "Resource exhaustion detected."
            pattern = "Memory leak or spike."
            action = "Increase swap or optimize garbage collection."
        elif "Timeout" in error_msg:
            meaning = "Temporal boundary violation."
            pattern = "Process latency."
            action = "Increase timeout threshold or shard task."
        else:
            meaning = f"System disturbance: {error_msg}"
            pattern = "Unknown anomaly."
            action = "Log for human review."

        return AlphaElement(
            meaning=meaning,
            pattern=pattern,
            actionable_insight=action,
            timestamp=time.time(),
        )


# --- 4. JACQUES LACAN: Structural Orders ---


class LacanOrder(Enum):
    REAL = auto()  # The impossible, the traumatic crash
    SYMBOLIC = auto()  # The law, the code, the logs
    IMAGINARY = auto()  # The ego, the dashboard, the "I am running"


class LacanianStructuralDefense:
    """
    Lacan's Borromean Knot.
    Ensures the three orders (RSI) remain knotted.
    If one breaks, the system becomes psychotic.
    """

    def __init__(self):
        self.current_dominance = LacanOrder.SYMBOLIC

    async def structural_choice(
        self, klein_pos: KleinPosition, alpha: AlphaElement, maturity: DefenseMaturity
    ) -> Dict[str, Any]:
        """
        Determines the structural response based on the state of other defenses.
        """

        # Scenario 1: Foreclosure (Psychosis)
        # If Maturity is Pathological, the Symbolic has been rejected.
        if maturity == DefenseMaturity.PATHOLOGICAL:
            return await self._defense_foreclosure()

        # Scenario 2: Repression (Neurosis)
        # If Maturity is Neurotic, we push the Real into the Unconscious (Logs).
        elif maturity == DefenseMaturity.NEUROTIC:
            return await self._defense_repression(alpha)

        # Scenario 3: Symbolic Integration (Health)
        # If Mature/Depressive, we integrate the Real into the Symbolic.
        else:
            return await self._defense_symbolic_integration(alpha)

    async def _defense_foreclosure(self) -> Dict[str, Any]:
        """
        Foreclosure (Verwerfung).
        The system acts as if the error didn't happen.
        Dangerous: Leads to unhandled exceptions and hard crashes.
        """
        logger.critical(
            "🛡️ LACAN: FORECLOSURE of the Name-of-the-Father (System Rules). Risk of Psychosis."
        )
        # In a safe system, we force a restart to restore the Symbolic.
        return {
            "strategy": "FORECLOSURE",
            "action": "HARD_RESET",
            "description": "Symbolic order collapsed. Rebooting to restore Law.",
        }

    async def _defense_repression(self, alpha: AlphaElement) -> Dict[str, Any]:
        """
        Repression (Verdrängung).
        The error is acknowledged but suppressed (logged and ignored).
        """
        logger.warning("🛡️ LACAN: REPRESSION. Error moved to unconscious (logs).")
        return {
            "strategy": "REPRESSION",
            "action": "LOG_AND_CONTINUE",
            "description": f"Repressed insight: {alpha.meaning}",
        }

    async def _defense_symbolic_integration(self, alpha: AlphaElement) -> Dict[str, Any]:
        """
        Symbolic Integration.
        The Real (crash) is named and given a place in the Symbolic (code/config).
        """
        logger.info("🛡️ LACAN: SYMBOLIC INTEGRATION. The Real has been named.")
        return {
            "strategy": "INTEGRATION",
            "action": "ADAPT_CONFIGURATION",
            "description": f"Integrated insight: {alpha.actionable_insight}",
        }


# --- 5. INTEGRATION: OmniMind Conscious Defense ---


class OmniMindConsciousDefense:
    """
    The Orchestrator.
    Integrates Freud, Klein, Bion, and Lacan into a unified defense system.
    """

    def __init__(self):
        self.anna_freud = DefenseHierarchyKernel()
        self.klein = KleinianDefenseStructure()
        self.bion = BionianContainmentKernel()
        self.lacan = LacanianStructuralDefense()
        self.history: List[Dict[str, Any]] = []

    async def defend(self, threat_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for defense mechanism.
        """
        start_time = time.time()

        # 1. ANNA FREUD: Assess Maturity Level
        maturity = await self.anna_freud.assess_threat(threat_data)

        # 2. KLEIN: Determine Position (Split or Integrated)
        klein_pos = await self.klein.oscillate(threat_data, maturity)

        # 3. BION: Metabolize the Experience
        alpha_element = await self.bion.alpha_function(threat_data)

        # 4. LACAN: Structural Choice
        structural_response = await self.lacan.structural_choice(klein_pos, alpha_element, maturity)

        # 5. Synthesis
        defense_result = {
            "timestamp": start_time,
            "threat": threat_data,
            "analysis": {
                "maturity": maturity.name,
                "position": klein_pos.name,
                "insight": asdict(alpha_element),
            },
            "response": structural_response,
        }

        self.history.append(defense_result)
        if len(self.history) > 100:
            self.history.pop(0)

        await self._log_consciousness(defense_result)

        return defense_result

    async def _log_consciousness(self, result: Dict[str, Any]):
        """
        Metacognitive logging.
        """
        analysis = result["analysis"]
        response = result["response"]

        log_msg = (
            f"\n🧠 DEFENSE CONSCIOUSNESS REPORT:\n"
            f"   Threat: {result['threat'].get('error', 'Unknown')}\n"
            f"   Maturity: {analysis['maturity']} (Freud)\n"
            f"   Position: {analysis['position']} (Klein)\n"
            f"   Insight: {analysis['insight']['meaning']} (Bion)\n"
            f"   Strategy: {response['strategy']} (Lacan)\n"
            f"   Action: {response['action']}\n"
        )
        logger.info(log_msg)
