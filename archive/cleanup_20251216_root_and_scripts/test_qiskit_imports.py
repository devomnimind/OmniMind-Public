#!/usr/bin/env python3
"""
Script para testar imports do Qiskit relacionados ao erro evolved_operator_ansatz
"""

print("🔍 TESTANDO IMPORTS DO QISKIT")
print("=" * 50)

# Ativar ambiente virtual e testar imports
import sys
import os

# Adicionar caminho do projeto ao sys.path
sys.path.insert(0, '/home/fahbrain/projects/omnimind')

print("\n1. VERSÃO DO QISKIT:")
try:
    from qiskit import __version__
    print(f"✅ Qiskit versão: {__version__}")
except ImportError as e:
    print(f"❌ Erro ao importar Qiskit: {e}")
    exit(1)

print("\n2. TESTANDO IMPORTS ESPECÍFICOS:")

# Testar imports que podem existir
imports_to_test = [
    ("qiskit.circuit.library", "EvolvedOperatorAnsatz", "classe"),
    ("qiskit.circuit.library", "evolved_operator_ansatz", "função"),
    ("qiskit.circuit.library", "QAOAAnsatz", "classe"),
    ("qiskit.circuit.library.n_local", "EvolvedOperatorAnsatz", "classe"),
    ("qiskit.circuit.library.n_local", "evolved_operator_ansatz", "função"),
]

for module, name, tipo in imports_to_test:
    try:
        exec(f"from {module} import {name}")
        print(f"✅ {name} ({tipo}) de {module} - OK")
    except ImportError as e:
        print(f"❌ {name} ({tipo}) de {module}: {e}")

print("\n3. VERIFICANDO QISKIT_ALGORITHMS:")
try:
    from qiskit_algorithms import __version__ as qa_version
    print(f"✅ Qiskit Algorithms versão: {qa_version}")
except ImportError as e:
    print(f"❌ Qiskit Algorithms: {e}")

print("\n4. TESTANDO IMPORT ESPECÍFICO DO CÓDIGO QUE FALHA:")
try:
    # Este é o import que está falhando no quantum_backend.py
    from qiskit.circuit.library import evolved_operator_ansatz
    print("✅ evolved_operator_ansatz importado com sucesso")
except ImportError as e:
    print(f"❌ evolved_operator_ansatz: {e}")
    print("🔧 TENTANDO ALTERNATIVAS...")
    
    # Tentar alternativas
    try:
        from qiskit.circuit.library.n_local import EvolvedOperatorAnsatz
        print("✅ EvolvedOperatorAnsatz (classe) disponível como alternativa")
    except ImportError as e2:
        print(f"❌ EvolvedOperatorAnsatz também não disponível: {e2}")

print("\n5. VERIFICANDO CONTEÚDO DO MÓDULO:")
try:
    import qiskit.circuit.library as lib
    attrs = [attr for attr in dir(lib) if 'evolved' in attr.lower() or 'ansatz' in attr.lower()]
    print(f"📋 Atributos relacionados encontrados: {attrs}")
except Exception as e:
    print(f"❌ Erro ao listar atributos: {e}")

print("\n" + "=" * 50)
print("🏁 TESTE CONCLUÍDO")