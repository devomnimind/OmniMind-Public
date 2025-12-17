import json
import os
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np

# Configuration
DATA_PATH = "data/validation/controlled_experiment.json"
OUTPUT_DIR = "docs/papers/figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_data(path: str) -> Dict:
    with open(path, "r") as f:
        return json.load(f)


def plot_phi_trajectories(data: Dict):
    plt.figure(figsize=(12, 7))

    colors = {"condition_A": "#2ecc71", "condition_B": "#e74c3c", "condition_C": "#95a5a6"}
    labels = {
        "condition_A": "Condição A (Estimulação Otimizada)",
        "condition_B": "Condição B (Sham/Random)",
        "condition_C": "Condição C (Controle Silencioso)",
    }

    for condition, runs in data.items():
        # Calculate mean trajectory and std dev
        trajectories = np.array([run["phi_trajectory"] for run in runs])
        mean_traj = np.mean(trajectories, axis=0)
        std_traj = np.std(trajectories, axis=0)
        cycles = range(1, len(mean_traj) + 1)

        plt.plot(
            cycles,
            mean_traj,
            label=labels.get(condition, condition),
            color=colors.get(condition, "blue"),
            linewidth=2,
        )
        plt.fill_between(
            cycles,
            mean_traj - std_traj,
            mean_traj + std_traj,
            color=colors.get(condition, "blue"),
            alpha=0.2,
        )

    plt.title("Dinâmica de Integração Phi (Φ) por Condição Experimental", fontsize=14)
    plt.xlabel("Ciclo de Simulação", fontsize=12)
    plt.ylabel("Integração Phi (Φ)", fontsize=12)
    plt.legend(loc="lower right")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.tight_layout()

    output_path = os.path.join(OUTPUT_DIR, "phi_trajectories.png")
    plt.savefig(output_path, dpi=300)
    print(f"Saved trajectory plot to {output_path}")
    plt.close()


def plot_final_comparison(data: Dict):
    plt.figure(figsize=(10, 6))

    conditions = ["condition_A", "condition_C", "condition_B"]  # Ordered by expected performance
    labels = ["A: Estimulação", "C: Controle", "B: Sham"]
    colors = ["#2ecc71", "#95a5a6", "#e74c3c"]

    means = []
    stds = []

    for cond in conditions:
        runs = data.get(cond, [])
        final_phis = [run["phi_final"] for run in runs]
        means.append(np.mean(final_phis))
        stds.append(np.std(final_phis))

    bars = plt.bar(labels, means, yerr=stds, capsize=10, color=colors, alpha=0.8)

    # Add value labels
    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2.0,
            height + 0.01,
            f"{height:.3f}",
            ha="center",
            va="bottom",
        )

    plt.title("Comparação de Phi Final (Φ) entre Condições", fontsize=14)
    plt.ylabel("Phi Final Médio", fontsize=12)
    plt.ylim(0, 1.0)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()

    output_path = os.path.join(OUTPUT_DIR, "phi_final_comparison.png")
    plt.savefig(output_path, dpi=300)
    print(f"Saved comparison plot to {output_path}")
    plt.close()


def main():
    if not os.path.exists(DATA_PATH):
        print(f"Error: Data file not found at {DATA_PATH}")
        return

    print("Loading data...")
    data = load_data(DATA_PATH)

    print("Generating plots...")
    plot_phi_trajectories(data)
    plot_final_comparison(data)
    print("Done.")


if __name__ == "__main__":
    main()
    main()
