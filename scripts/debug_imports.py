try:
    import qiskit

    print(f"qiskit: {qiskit.__version__}")
except ImportError as e:
    print(f"qiskit import failed: {e}")

try:
    import qiskit_aer

    print(f"qiskit_aer: {qiskit_aer.__version__}")
except ImportError as e:
    print(f"qiskit_aer import failed: {e}")

try:
    from qiskit import QuantumCircuit

    print("QuantumCircuit imported")
except ImportError as e:
    print(f"QuantumCircuit import failed: {e}")

try:
    from qiskit_aer import AerSimulator

    print("AerSimulator imported")
except ImportError as e:
    print(f"AerSimulator import failed: {e}")

try:
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

    print("generate_preset_pass_manager imported")
except ImportError as e:
    print(f"generate_preset_pass_manager import failed: {e}")
