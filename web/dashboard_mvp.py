"""
OmniMind Psyche Control Panel (MVP)
Visualizes internal conflict resolution and audit chain.
"""

import streamlit as st
import pandas as pd
import altair as alt
import json
import time
from pathlib import Path
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Additional imports for IBM Quantum test integration
import subprocess
import shlex

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
from src.agents.psychoanalytic_analyst import PsychoanalyticDecisionSystem
from src.audit.immutable_audit import get_audit_system

# Page Config
st.set_page_config(
    page_title="OmniMind Psyche Control Panel",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize System
if "decision_system" not in st.session_state:
    st.session_state.decision_system = PsychoanalyticDecisionSystem()

if "messages" not in st.session_state:
    st.session_state.messages = []

audit_system = get_audit_system()

# --- Sidebar: Audit Chain ---
st.sidebar.title("🔒 Audit Chain")
st.sidebar.caption("Immutable Log of Cognitive Events")

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
                {
                    "input": prompt,
                    "decision": decision
                },
                category="cognitive"
            )

            # 3. Generate Response (Mocked for MVP, normally LLM)
            winner = decision["winner"]
            confidence = decision["confidence"]

            response_text = f"**[Decision: {winner} | Confidence: {confidence:.2f}]**\n\n"
            if winner == "avoid_conflict":
                response_text += "I sense tension. Perhaps we should approach this carefully to avoid distress."
            elif winner == "analyze_rationally":
                response_text += "Let's look at the facts. The logical implication is clear."
            elif winner == "follow_rules":
                response_text += "We must adhere to the established ethical guidelines in this matter."
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
            data.append({
                "Agent": v["agent"],
                "Score": v["score"],
                "Confidence": v["confidence"],
                "Weight": v["weight"]
            })

        df = pd.DataFrame(data)

        # Bar Chart of Scores
        chart = alt.Chart(df).mark_bar().encode(
            x='Agent',
            y='Score',
            color='Agent',
            tooltip=['Agent', 'Score', 'Confidence', 'Weight']
        ).properties(
            title="Agent Influence (Weight * Confidence)"
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
            tension = 1.0 - (scores[0] - scores[1]) # Higher difference = Lower tension
            st.progress(tension, text=f"Cognitive Tension: {tension:.2f}")
    else:
        st.info("Start a conversation to see internal dynamics.")

