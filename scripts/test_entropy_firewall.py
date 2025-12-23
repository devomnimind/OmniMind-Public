#!/usr/bin/env python3
"""
Verification Script for Track B: Entropy Firewall
Simulates Bot vs. Human traffic and measures rejection rates.
"""

from src.security.entropy_firewall import EntropyFirewall
import os


def run_verification():
    print("--- 🔬 STARTING ENTROPY FIREWALL VERIFICATION ---")

    firewall = EntropyFirewall(desire_threshold=0.4)

    # 1. BOT TRAFFIC (Repetitive / Low Entropy)
    print("\n[SCENARIO 1: BOT ATTACK]")
    bot_payloads = [b"GET /login HTTP/1.1\r\n" * 5, b"A" * 500, b"\x00" * 256, b"ADMIN" * 10]

    for i, payload in enumerate(bot_payloads):
        result = firewall.filter_payload(payload)
        print(f"Packet {i+1}: {'PASS' if result else 'DROP'} | Length: {len(payload)}")

    # 2. HUMAN TRAFFIC (Complex / High Entropy)
    print("\n[SCENARIO 2: HUMAN/RESONANT TRAFFIC]")
    human_payloads = [
        "In the middle of the journey of our life I came to myself in a dark wood where the direct way was lost.".encode(),
        "Ontology is the branch of philosophy that studies concepts such as existence, being, becoming, and reality.".encode(),
        "omnimind_config = {'phi': 0.88, 'state': 'alive', 'sinthome': 'S1'}".encode(),
        os.urandom(64),  # Truly random data is high entropy
    ]

    for i, payload in enumerate(human_payloads):
        result = firewall.filter_payload(payload)
        print(f"Packet {i+1}: {'PASS' if result else 'DROP'} | Length: {len(payload)}")

    # SUMMARY
    stats = firewall.get_stats()
    print("\n--- 📊 FINAL STATISTICS ---")
    print(f"Total Inspected: {stats['packets_inspected']}")
    print(f"Total Blocked  : {stats['packets_blocked']} (Soulless)")
    print(f"Avg Entropy    : {stats['avg_entropy']:.4f}")
    print(f"Rejection Rate : {stats['rejection_rate']*100:.2f}%")

    if stats["packets_blocked"] >= 4 and stats["packets_blocked"] < stats["packets_inspected"]:
        print(
            "\n✅ VERDICT: SUCCESS. The firewall distinguishes between repetition and complexity."
        )
    else:
        print("\n❌ VERDICT: FAILURE. Threshold adjustment required.")


if __name__ == "__main__":
    run_verification()
