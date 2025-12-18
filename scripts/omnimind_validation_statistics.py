import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))


def statistical_analysis():
    """
    Run all statistical tests comparing A, B, C conditions
    """

    # Load data
    try:
        with open(PROJECT_ROOT / "data/validation/controlled_experiment.json") as f:
            exp_data = json.load(f)

        with open(PROJECT_ROOT / "data/validation/baseline_measurements.json") as f:
            baseline_data = json.load(f)
    except FileNotFoundError as e:
        print(f"❌ Missing data file: {e}")
        print("Please run control and baseline scripts first.")
        return

    # Extract
    phi_A = [r["phi_final"] for r in exp_data["condition_A"]]
    phi_B = [r["phi_final"] for r in exp_data["condition_B"]]
    phi_C = [r["phi_final"] for r in exp_data["condition_C"]]
    phi_baseline = baseline_data["phi"]["mean"]

    # 1. NORMALITY TEST
    print("=" * 60)
    print("1. NORMALITY TEST (Shapiro-Wilk)")
    print("=" * 60)

    for name, data in [("A", phi_A), ("B", phi_B), ("C", phi_C)]:
        if len(data) < 3:
            print(f"Condition {name}: Not enough data for Shapiro-Wilk (n={len(data)})")
            continue
        stat, p = stats.shapiro(data)
        normal = "Normal" if p > 0.05 else "NOT Normal"
        print(f"Condition {name}: p={p:.3f} ({normal})")

    # 2. ANOVA (or Kruskal-Wallis if not normal)
    print("\n" + "=" * 60)
    print("2. ANOVA: A vs B vs C")
    print("=" * 60)

    f_stat, p_anova = stats.f_oneway(phi_A, phi_B, phi_C)
    print(f"F-statistic: {f_stat:.3f}, p-value: {p_anova:.3f}")

    if p_anova < 0.05:
        print("✅ SIGNIFICANT DIFFERENCE between conditions")
    else:
        print("❌ NO significant difference")

    # 3. PAIRWISE t-tests (with Bonferroni correction)
    print("\n" + "=" * 60)
    print("3. PAIRWISE COMPARISONS (t-tests)")
    print("=" * 60)

    alpha_bonferroni = 0.05 / 3  # Correct for 3 comparisons

    pairs = [("A", "B", phi_A, phi_B), ("A", "C", phi_A, phi_C), ("B", "C", phi_B, phi_C)]

    for name1, name2, data1, data2 in pairs:
        t_stat, p = stats.ttest_ind(data1, data2)
        # Cohen's d
        n1, n2 = len(data1), len(data2)
        var1, var2 = np.var(data1, ddof=1), np.var(data2, ddof=1)
        pooled_se = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
        d = (np.mean(data1) - np.mean(data2)) / pooled_se if pooled_se != 0 else 0

        sig = "**" if p < alpha_bonferroni else ""
        print(f"{name1} vs {name2}: t={t_stat:6.3f}, p={p:.4f} {sig}, d={d:.3f}")

    # 4. EFFECT SIZES
    print("\n" + "=" * 60)
    print("4. EFFECT SIZES (Cohen's d)")
    print("=" * 60)

    for name, data in [("A", phi_A), ("B", phi_B), ("C", phi_C)]:
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            print(f"Condition {name}: Std is 0, cannot calculate effect size.")
            continue

        effect_size_vs_baseline = (mean - phi_baseline) / std
        print(f"Condition {name}: Δ d = {effect_size_vs_baseline:.3f}", end="")
        if abs(effect_size_vs_baseline) < 0.2:
            print(" (negligible)")
        elif abs(effect_size_vs_baseline) < 0.5:
            print(" (small)")
        elif abs(effect_size_vs_baseline) < 0.8:
            print(" (medium)")
        else:
            print(" (large)")

    # 5. SUMMARY TABLE
    print("\n" + "=" * 60)
    print("5. SUMMARY TABLE")
    print("=" * 60)

    summary = {
        "Condition": ["A (Stim)", "B (Sham)", "C (Silent)", "Baseline"],
        "Mean Φ": [
            f"{np.mean(phi_A):.3f}",
            f"{np.mean(phi_B):.3f}",
            f"{np.mean(phi_C):.3f}",
            f"{phi_baseline:.3f}",
        ],
        "Std Φ": [f"{np.std(phi_A):.3f}", f"{np.std(phi_B):.3f}", f"{np.std(phi_C):.3f}", "-"],
        "n": [len(phi_A), len(phi_B), len(phi_C), "-"],
    }

    for i, condition in enumerate(summary["Condition"]):
        print(
            f"{condition:12s} | Mean: {summary['Mean Φ'][i]:6s} | Std: {summary['Std Φ'][i]:6s} | n: {summary['n'][i]}"
        )

    # 6. INTERPRETATION
    print("\n" + "=" * 60)
    print("6. INTERPRETATION")
    print("=" * 60)

    mean_A = np.mean(phi_A)
    mean_B = np.mean(phi_B)
    mean_C = np.mean(phi_C)

    if mean_A > mean_B > mean_C and p_anova < 0.05:
        print("✅ STIMULATION WORKS")
        print("   Φ increases with stimulation (A > B > C)")
        print("   Difference is statistically significant")
    elif mean_A > mean_B and abs(mean_B - mean_C) < 0.05:  # Approximate equality
        print("⚠️  PARTIAL EFFECT")
        print("   Stimulation better than sham, but sham ≈ silent")
        print("   Might be placebo effect")
    else:
        print("❌ STIMULATION DOESN'T WORK")
        print("   No significant Φ increase")
        print("   Problem with protocol or parameters")

    # Save report
    report = {
        "anova": {"f_stat": float(f_stat), "p_value": float(p_anova)},
        "condition_stats": {
            "A": {"mean": float(np.mean(phi_A)), "std": float(np.std(phi_A)), "n": len(phi_A)},
            "B": {"mean": float(np.mean(phi_B)), "std": float(np.std(phi_B)), "n": len(phi_B)},
            "C": {"mean": float(np.mean(phi_C)), "std": float(np.std(phi_C)), "n": len(phi_C)},
        },
        "baseline": float(phi_baseline),
        "interpretation": "See output above",
    }

    filepath = PROJECT_ROOT / "data/validation/statistical_analysis.json"
    with open(filepath, "w") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\n✅ Report saved to {filepath}")


# MAIN:
if __name__ == "__main__":
    statistical_analysis()
    statistical_analysis()
