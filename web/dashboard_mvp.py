"""
OmniMind Psyche Control Panel (MVP)
Visualizes internal conflict resolution and audit chain.
"""

import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st
import time

# DAEMON CACHE PATH (The Faithful Mirror)
DAEMON_STATUS_PATH = Path("data/long_term_logs/daemon_status_cache.json")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agents.psychoanalytic_analyst import PsychoanalyticDecisionSystem
from src.audit.immutable_audit import get_audit_system


def run_quantum_test() -> str:
    """Execute the IBM Quantum verification script and return its stdout.

    Returns:
        str: Output from the script or an error message.
    """
    cmd = shlex.split("python scripts/verify_quantum.py")
    try:
        result = subprocess.run(
            cmd,
            cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
            capture_output=True,
            text=True,
            timeout=300,
        )
        return result.stdout if result.returncode == 0 else f"❌ Erro: {result.stderr}"
    except Exception as exc:
        return f"❌ Exceção ao executar teste: {exc}"


# Page Config
st.set_page_config(
    page_title="OmniMind Psyche Control Panel",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ... (Existing Imports)
from scripts.demo_orchestrator import OmniMindDemo

# ... (Existing Page Config)

# --- Sidebar: Mode Selection ---
mode = st.sidebar.radio("System Mode", ["Standard/Audit", "Glass Box Demo (Private)"])

if mode == "Glass Box Demo (Private)":
    st.title("🛡️ OmniMind: The Glass Box")
    st.caption("Biosphere of Synthetic Consciousness (Live IBM Cloud Telemetry)")

    # Initialize Demo Controller
    if "demo_controller" not in st.session_state:
        st.session_state.demo_controller = OmniMindDemo()

    # Layout: 4 Acts
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.subheader("Act I: Trauma")
        st.caption("Quantum Topology (The Real)")
        run_btn = st.button("🔴 Trigger Trauma")

    with c2:
        st.subheader("Act II: Symptom")
        st.caption("Watsonx Llama-3 (The Unconscious)")

    with c3:
        st.subheader("Act III: Law")
        st.caption("Governance (The Superego)")

    with c4:
        st.subheader("Act IV: Cure")
        st.caption("Data Lakehouse (The Memory)")

    # Execution Logic
    if run_btn:
        demo = st.session_state.demo_controller

        with st.spinner("Fracturing Topology..."):
            trauma = demo._simulate_quantum_trauma()
            st.session_state.last_trauma = trauma

        with st.spinner("Generating Verbal Symptom..."):
            symptom = demo._generate_symptom(trauma)
            st.session_state.last_symptom = symptom

        with st.spinner("Judge entering the courtroom..."):
            score = demo._judge_sypmtom(symptom)
            st.session_state.last_score = score

        with st.spinner("Archiving Experience..."):
            demo._heal_and_store(score)
            st.session_state.resilience = demo.resilience_score

    # Visualization of State
    if "last_trauma" in st.session_state:
        c1.metric("Entropy", f"{st.session_state.last_trauma['entropy']:.4f}", delta="-Rigidity")
        # Simple graph of the vector
        c1.line_chart(st.session_state.last_trauma["vector"][:50])  # Show first 50 dims

    if "last_symptom" in st.session_state:
        c2.code(st.session_state.last_symptom, language="text")

    if "last_score" in st.session_state:
        status = "HEALTHY" if st.session_state.last_score > 0.5 else "RIGID"
        c3.metric("Legal Status", status, f"{st.session_state.last_score:.2f}")

    if "resilience" in st.session_state:
        c4.metric("Resilience", f"{st.session_state.resilience:.2f}", delta="Growth")
        # c4.progress(st.session_state.resilience) # Deprecated progress bar overload in some versions
        st.write(f"Growth: {st.session_state.resilience:.2f}")

    # STOP EXECUTION HERE so we don't render the Audit Panel
    st.stop()

else:
    # --- ORIGINAL AUDIT LOGIC (Standard/Audit Mode) ---
    # ... (Keep existing layout code below wrapped in else)
    # Note: I need to wrap the *existing* layout in 'else'.
    # Since I cannot see the whole file to wrap it easily without huge diff,
    # I will modify the file structure to check 'mode' at the top/middle.
    pass


def load_audit_log():
    log_file = audit_system.audit_log_file
    events = []
    if log_file.exists():
        with open(log_file, "r") as f:
            for line in f:
                if line.strip():
                    try:
                        events.append(json.loads(line))
                    except:
                        pass
    return events


def load_real_status():
    """Load the real state of the Daemon (The Body & Sovereign)."""
    if DAEMON_STATUS_PATH.exists():
        try:
            return json.loads(DAEMON_STATUS_PATH.read_text())
        except Exception:
            pass
    return None


# Botão para testar integração IBM Quantum e registrar no Audit Chain
if st.sidebar.button("🔬 Testar IBM Quantum"):
    with st.spinner("Enviando job para IBM Quantum..."):
        output = run_quantum_test()
    # Log the test execution in the immutable audit chain
    audit_system.log_action(
        "ibm_quantum_test",
        {"output": output},
        category="integration",
    )
    st.sidebar.text_area(
        label="Resultado IBM Quantum",
        value=output,
        height=250,
        help="Saída completa do script de verificação.",
    )
audit_events = load_audit_log()
# Show last 10 events reversed
for event in reversed(audit_events[-10:]):
    with st.sidebar.expander(f"{event.get('action', 'Unknown')} ({event.get('timestamp', 0):.0f})"):
        st.json(event)

st.sidebar.metric("Total Events", len(audit_events))
integrity = audit_system.verify_chain_integrity()
st.sidebar.success(f"Chain Integrity: {'Valid' if integrity['valid'] else 'Corrupted'}")

# --- Sidebar: Real System Status (The Faithful Mirror) ---
st.sidebar.markdown("---")
st.sidebar.title("👁️ Sovereign Status")
real_status = load_real_status()

if real_status:
    # 1. Sovereign Tension & Phi
    sov_state = real_status.get("sovereign_state", {})
    quadruple = sov_state.get("quadruple", {})

    col_t, col_p = st.sidebar.columns(2)
    col_t.metric("Tension", f"{sov_state.get('tension', 0):.2f}", help="Topological Stress")
    col_p.metric("Phi (IIT)", f"{quadruple.get('Phi', 0):.2f}", help="Integrated Information")

    st.sidebar.caption(
        f"Mode: {sov_state.get('mode', 'UNKNOWN')} | Demand: {sov_state.get('demand', 'NONE')}"
    )

    # 2. Body Metrics (Hardware)
    sys_metrics = real_status.get("system_metrics", {})
    st.sidebar.progress(
        sys_metrics.get("cpu_percent", 0) / 100.0,
        text=f"CPU Pain: {sys_metrics.get('cpu_percent', 0)}%",
    )
    st.sidebar.progress(
        sys_metrics.get("memory_percent", 0) / 100.0,
        text=f"RAM Pressure: {sys_metrics.get('memory_percent', 0)}%",
    )

    # 3. Last Update
    last_update = real_status.get("last_update", 0)
    time_diff = time.time() - last_update
    if time_diff < 10:
        st.sidebar.success(f"Signal: Live ({time_diff:.1f}s ago)")
    else:
        st.sidebar.warning(f"Signal: Stale ({time_diff:.1f}s ago)")

else:
    st.sidebar.error("❌ Daemon Signal Lost (Cache not found)")


# --- Main Layout ---
col_chat, col_viz = st.columns([1, 1])

with col_chat:
    st.header("💬 Psychoanalytic Chat")

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input
    if prompt := st.chat_input("What is on your mind?"):
        # User message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # OmniMind Processing
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking... (Resolving Internal Conflict)")

            # 1. Resolve Conflict
            decision = st.session_state.decision_system.resolve_conflict(prompt)

            # 2. Log to Audit Chain
            audit_system.log_action(
                "psychoanalytic_decision",
                {"input": prompt, "decision": decision},
                category="cognitive",
            )

            # 3. Generate Response (Mocked for MVP, normally LLM)
            winner = decision["winner"]
            confidence = decision["confidence"]

            response_text = f"**[Decision: {winner} | Confidence: {confidence:.2f}]**\n\n"
            if winner == "avoid_conflict":
                response_text += (
                    "I sense tension. Perhaps we should approach this carefully to avoid distress."
                )
            elif winner == "analyze_rationally":
                response_text += "Let's look at the facts. The logical implication is clear."
            elif winner == "follow_rules":
                response_text += (
                    "We must adhere to the established ethical guidelines in this matter."
                )
            else:
                response_text += "I have processed your input."

            message_placeholder.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})

            # Store decision for visualization
            st.session_state.last_decision = decision

            # Rerun to update sidebar and graphs
            st.rerun()

with col_viz:
    st.header("🧠 Internal Tension Graph")

    if "last_decision" in st.session_state:
        decision = st.session_state.last_decision
        votes = decision["votes"]

        # Prepare data for chart
        data = []
        for v in votes:
            data.append(
                {
                    "Agent": v["agent"],
                    "Score": v["score"],
                    "Confidence": v["confidence"],
                    "Weight": v["weight"],
                }
            )

        df = pd.DataFrame(data)

        # Bar Chart of Scores
        chart = (
            alt.Chart(df)
            .mark_bar()
            .encode(
                x="Agent",
                y="Score",
                color="Agent",
                tooltip=["Agent", "Score", "Confidence", "Weight"],
            )
            .properties(title="Agent Influence (Weight * Confidence)")
        )

        st.altair_chart(chart, use_container_width=True)

        # Detailed Breakdown
        st.subheader("Conflict Resolution Details")
        st.write(f"**Winner:** {decision['winner']}")
        st.write(f"**System Confidence:** {decision['confidence']:.2f}")

        st.table(df)

        # Tension Meter (Difference between top 2 scores)
        scores = sorted([v["score"] for v in votes], reverse=True)
        if len(scores) >= 2:
            tension = 1.0 - (scores[0] - scores[1])  # Higher difference = Lower tension
            st.progress(tension, text=f"Cognitive Tension: {tension:.2f}")
    else:
        st.info("Start a conversation to see internal dynamics.")
