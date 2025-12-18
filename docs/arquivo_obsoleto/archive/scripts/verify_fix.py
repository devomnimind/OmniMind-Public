from src.metrics.consciousness_metrics import ConsciousnessCorrelates

simulated_system = {
    "coherence_history": [0.7, 0.8, 0.9],
    "nodes": {
        "n1": {"status": "ACTIVE", "integrity": 95},
        "n2": {"status": "ACTIVE", "integrity": 95},
    },
    "entropy": 15,
}

calculator = ConsciousnessCorrelates(simulated_system)
metrics = calculator.calculate_all()
print(f"ICI: {metrics['ICI']}")
print(f"PRS: {metrics['PRS']}")
