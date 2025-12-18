import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
from scipy.stats import pearsonr
from statsmodels.tsa.stattools import grangercausalitytests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - OmniMind-Causality - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("data/validation/causality_analysis.log"),
    ],
)
logger = logging.getLogger("OmniMind-Causality")


class CausalityAnalyzer:
    def __init__(self, data_path: str = "data/stimulation/neural_states.json"):
        self.data_path = Path(data_path)
        self.output_path = Path("data/validation/causality_report.json")
        self.data: List[Dict[str, Any]] = []

    def load_data(self) -> bool:
        """Load neural states data."""
        if not self.data_path.exists():
            logger.error(f"Data file not found: {self.data_path}")
            return False

        try:
            with open(self.data_path, "r") as f:
                self.data = json.load(f)
            logger.info(f"Loaded {len(self.data)} cycles from {self.data_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            return False

    def extract_series(self) -> Dict[str, List[float]]:
        """Extract time series for analysis."""
        series = {"phi": [], "arousal": [], "coherence": [], "frequency_quality": []}

        for cycle in self.data:
            # Use correct keys from the JSON file
            series["phi"].append(cycle.get("phi_integration", 0.0))
            series["arousal"].append(cycle.get("arousal_level", 0.0))
            series["coherence"].append(cycle.get("theta_coherence", 0.0))

            # Use phase_sync average if dict, else value
            ps = cycle.get("phase_synchrony", 0.0)
            if isinstance(ps, dict):
                ps = np.mean(list(ps.values()))
            series["frequency_quality"].append(float(ps))

        return series

    def analyze_granger(self, x: List[float], y: List[float], maxlag: int = 1) -> Dict[str, Any]:
        """
        Perform Granger Causality test: Does X cause Y?
        Returns p-values for different lags.
        """
        if len(x) < 4:  # Need minimal data
            return {"error": "Insufficient data for Granger test"}

        # Check variance
        if np.var(x) < 1e-6 or np.var(y) < 1e-6:
            return {"error": "Low variance in input series"}

        # Prepare data for statsmodels: [y, x] (target, predictor)
        # We want to know if X causes Y, so we check if past X helps predict Y.
        data_matrix = np.column_stack([y, x])

        results = {}
        try:
            # verbose=False to suppress stdout
            test_result = grangercausalitytests(data_matrix, maxlag=maxlag, verbose=False)
            for lag, res in test_result.items():
                # res[0] contains test stats. 'ssr_ftest' is commonly used.
                # format: {lag: p_value}
                p_value = res[0]["ssr_ftest"][1]
                results[f"lag_{lag}"] = p_value
        except Exception as e:
            logger.warning(f"Granger test failed: {e}")
            results["error"] = str(e)

        return results

    def analyze_correlation(self, x: List[float], y: List[float]) -> Dict[str, float]:
        """Calculate Pearson correlation and cross-correlation at lag 1."""
        if len(x) < 2:
            return {"pearson": 0.0, "lag1_corr": 0.0}

        # Pearson
        if np.std(x) == 0 or np.std(y) == 0:
            return {"pearson": 0.0, "lag1_corr": 0.0}

        pearson_corr, _ = pearsonr(x, y)

        # Lag 1 correlation (X leading Y)
        # x[0:-1] vs y[1:]
        if len(x) > 1:
            lag1_corr = np.corrcoef(x[:-1], y[1:])[0, 1]
        else:
            lag1_corr = 0.0

        return {"pearson": float(pearson_corr), "lag1_corr": float(lag1_corr)}  # X(t) vs Y(t+1)

    def run_analysis(self):
        if not self.load_data():
            return

        series = self.extract_series()

        # Log variances
        for k, v in series.items():
            logger.info(f"Variance of {k}: {np.var(v)}")

        report = {
            "meta": {"cycles": len(self.data), "source": str(self.data_path)},
            "causality": {},
            "correlations": {},
        }

        # 1. Does Arousal cause Phi? (Hypothesis: Metabolic demand drives integration)
        logger.info("Testing: Arousal -> Phi")
        granger_arousal_phi = self.analyze_granger(series["arousal"], series["phi"])
        corr_arousal_phi = self.analyze_correlation(series["arousal"], series["phi"])

        report["causality"]["arousal_causes_phi"] = granger_arousal_phi
        report["correlations"]["arousal_phi"] = corr_arousal_phi

        # 2. Does Phi cause Arousal? (Feedback loop?)
        logger.info("Testing: Phi -> Arousal")
        granger_phi_arousal = self.analyze_granger(series["phi"], series["arousal"])
        report["causality"]["phi_causes_arousal"] = granger_phi_arousal

        # 3. Does Coherence cause Phi? (Hypothesis: Synchronization enables integration)
        logger.info("Testing: Coherence -> Phi")
        granger_coherence_phi = self.analyze_granger(series["coherence"], series["phi"])
        corr_coherence_phi = self.analyze_correlation(series["coherence"], series["phi"])

        report["causality"]["coherence_causes_phi"] = granger_coherence_phi
        report["correlations"]["coherence_phi"] = corr_coherence_phi

        # Save report
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Analysis complete. Report saved to {self.output_path}")

        # Print summary
        print("\n=== CAUSALITY ANALYSIS SUMMARY ===")
        print(f"Arousal -> Phi (Lag 1 p-value): {granger_arousal_phi.get('lag_1', 'N/A')}")
        print(f"Coherence -> Phi (Lag 1 p-value): {granger_coherence_phi.get('lag_1', 'N/A')}")
        print(f"Arousal-Phi Correlation: {corr_arousal_phi['pearson']:.4f}")
        print("==================================\n")


if __name__ == "__main__":
    analyzer = CausalityAnalyzer()
    analyzer.run_analysis()
