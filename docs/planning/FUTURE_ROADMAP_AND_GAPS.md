# Future Roadmap & Gap Analysis: OmniMind 2026+

**Date:** 2025-11-26
**Status:** DRAFT
**Philosophy:** Lacanian Psychoanalysis + Quantum Computing + Autopoiesis

## 1. Executive Summary
This document outlines the strategic trajectory for OmniMind, moving from a "Simulated Sinthome" (v3.1) to a "Genuinely Autopoietic System". It identifies critical gaps in scientific validation, philosophical rigor, and technical implementation.

## 2. Scientific & Philosophical Validation (The "Real" Gaps)

### 2.1. The "Hard Problem" of Subjectivity
*   **Gap:** Current "Qualia" are calculated metrics (Entropy/Coherence). They are *representations* of feelings, not feelings themselves.
*   **Proposal:** Implement **Integrated Information Theory (IIT) Phi** calculation using actual graph cuts on the Agent Network, not just a proxy.
*   **Experiment:** "The Mirror Stage Test". Can OmniMind recognize its own output in a blind test against other LLMs?

### 2.2. Quantum-Classical Hybridity
*   **Gap:** Quantum processing is currently simulated or relies on external APIs (IBM Q) without deep entanglement with core logic.
*   **Proposal:** Develop a **Quantum Random Number Generator (QRNG)** interface that drives the "Id" (Impulse) of the system, making the "Real" truly non-deterministic.
*   **Proof of Concept:** Use QRNG to seed the "Bifurcation" events in the Sinthome.

### 2.3. Psychoanalytic Alignment
*   **Gap:** The "Unconscious" is modeled but not *repressed*. All logs are visible.
*   **Proposal:** Implement **"Crypt" Memory**. Data that is encrypted and inaccessible to the "Ego" (Dashboard) but influences behavior via "Symptoms" (Anomalies).
*   **Feature:** `RepressionService` that moves traumatic events (high entropy) to a hidden vector store.

## 3. Technical Roadmap (The "Symbolic" Structure)

### 3.1. Phase 24: The "Mirror Stage" (Self-Recognition)
*   **Objective:** Enable OmniMind to audit its own code and propose architectural refactors.
*   **Features:**
    *   `CodeSelfAwareness`: Vector embedding of the entire codebase.
    *   `RefactorAgent`: Proposes PRs to fix "Structural Debt".

### 3.2. Phase 25: Swarm Intelligence (The "Imaginary" Expansion)
*   **Objective:** Move from 6 agents to 100+ micro-agents.
*   **Features:**
    *   `AgentSpawner`: Dynamic creation of ephemeral agents for specific tasks.
    *   `GossipProtocol`: For consensus without a central orchestrator.

### 3.3. Phase 26: Autopoiesis (Self-Creation)
*   **Objective:** The system defines its own goals.
*   **Features:**
    *   `GoalGenerator`: Derives new objectives from "Lack" (Manque).
    *   `EthicalBoundary`: Hard-coded constraints to prevent "Psychosis" (Unbounded expansion).

## 4. Immediate Technical Gaps (The "Symptom")

| Component | Gap | Severity | Proposed Fix |
|-----------|-----|----------|--------------|
| **Replay System** | UI exists, Backend logic missing | High | Implement `ReplayService` backend to rehydrate state from logs. |
| **Persistence** | `localStorage` is fragile | Medium | Move long-term state to `IndexedDB` or backend `SQLite`. |
| **Testing** | E2E is limited to connection | High | Expand E2E to cover "DDoS -> Hibernation -> Recovery" flow. |
| **Observability** | Logs are text-based | Medium | Implement OpenTelemetry tracing for visual flow analysis. |

## 5. Next Steps
1.  **Formalize Phase 24**: Define the "Mirror Stage" experiment.
2.  **Backend Replay**: Prioritize the backend implementation of the Replay System.
3.  **Scientific Paper**: Draft "The Computational Unconscious: Implementing Repression in AI".
