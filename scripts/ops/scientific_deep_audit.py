#!/usr/bin/env python3
"""
AUDITORIA CIENTÍFICA PROFUNDA - OmniMind Codebase
Análise Estática Recursiva de todos os módulos em src/

Quádrupla Teórica:
1. MATEMÁTICA: Φ/IIT, MICS, ψ normalizações
2. TOPOLÓGICA: Simplicial complexes, manifolds, Borromean
3. ENTRÓPICA: σ actions, entropy, quantum entropy
4. PSICANALÍTICA: Freud/Deleuze/Lacan/Sinthome
"""
import ast
import re
from pathlib import Path
from collections import defaultdict
import json

PROJECT_ROOT = Path("/home/fahbrain/projects/omnimind")
SRC_DIR = PROJECT_ROOT / "src"

# Padrões de busca para cada dimensão
PATTERNS = {
    "MATEMATICA": [
        # IIT/Phi
        r"\bphi\b",
        r"\bPhi\b",
        r"Φ",
        r"IIT",
        r"integrated.information",
        r"MICS",
        r"mics",
        r"mutual.information",
        r"cause.effect",
        # Psi normalizations
        r"\bpsi\b",
        r"\bPsi\b",
        r"Ψ",
        r"normalization",
        r"normalize",
        # Cálculos matemáticos
        r"np\.linalg",
        r"scipy\.",
        r"matrix",
        r"eigenval",
        r"svd",
    ],
    "TOPOLOGICA": [
        r"simplicial",
        r"complex",
        r"manifold",
        r"Borromean",
        r"knot",
        r"homology",
        r"cohomology",
        r"topology",
        r"topological",
        r"betti",
        r"persistent.homology",
        r"nerve",
    ],
    "ENTROPICA": [
        r"\bsigma\b",
        r"σ",
        r"entropy",
        r"entropy_of_actions",
        r"quantum.entropy",
        r"von.neumann",
        r"shannon",
        r"mutual_info",
        r"uncertainty",
        r"surprise",
    ],
    "PSICANALITICA": [
        r"freud",
        r"Freud",
        r"deleuze",
        r"Deleuze",
        r"lacan",
        r"Lacan",
        r"sinthome",
        r"Sinthome",
        r"unconscious",
        r"drive",
        r"desire",
        r"jouissance",
        r"objet.petit.a",
        r"Real.*Symbolic.*Imaginary",
        r"Oedip",
        r"repression",
        r"symptom",
    ],
    "QUANTICO": [
        r"cuQuantum",
        r"qiskit",
        r"quantum",
        r"qubit",
        r"VQC",
        r"QSVM",
        r"QuantumCircuit",
        r"EntanglementEntropy",
        r"QPU",
    ],
}


def extract_imports(file_path):
    """Extrai todos os imports de um arquivo."""
    try:
        with open(file_path) as f:
            tree = ast.parse(f.read(), filename=str(file_path))

        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split(".")[0])

        return imports
    except:
        return set()


def extract_functions(file_path):
    """Extrai nomes de funções/classes."""
    try:
        with open(file_path) as f:
            tree = ast.parse(f.read(), filename=str(file_path))

        functions = []
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)

        return functions, classes
    except:
        return [], []


def scan_patterns(file_path, content=None):
    """Busca padrões da quádrupla teórica."""
    if content is None:
        try:
            with open(file_path) as f:
                content = f.read()
        except:
            return {}

    results = {}
    for category, patterns in PATTERNS.items():
        matches = 0
        for pattern in patterns:
            matches += len(re.findall(pattern, content, re.IGNORECASE))
        results[category] = matches > 0

    return results


def analyze_module(py_file):
    """Análise completa de um módulo."""
    rel_path = py_file.relative_to(SRC_DIR)

    try:
        with open(py_file) as f:
            content = f.read()
    except:
        content = ""

    # Extrair informações
    imports = extract_imports(py_file)
    functions, classes = extract_functions(py_file)
    patterns = scan_patterns(py_file, content)

    # Contar linhas
    lines = len(content.splitlines())

    # Detectar fórmulas matemáticas (comentários com equações)
    formulas = re.findall(r"#.*?[=∫∑∏Φψσ]", content)

    return {
        "path": str(rel_path),
        "folder": str(rel_path.parent),
        "name": py_file.stem,
        "lines": lines,
        "imports": list(imports),
        "functions_count": len(functions),
        "classes_count": len(classes),
        "formulas_count": len(formulas),
        "patterns": patterns,
    }


def build_dependency_graph(modules_data):
    """Constrói grafo de dependências."""
    graph = defaultdict(set)

    for module in modules_data:
        module_path = module["path"]
        module_folder = module["folder"]

        # Para cada import, verificar se aponta para src/
        for imp in module["imports"]:
            for other in modules_data:
                other_folder = other["folder"]
                if imp in other_folder or imp == other["name"]:
                    graph[module_path].add(other["path"])

    return graph


def find_orphans(modules_data, graph):
    """Encontra módulos órfãos (sem dependências bidirecionais)."""
    all_paths = {m["path"] for m in modules_data}
    orphans = []

    for module in modules_data:
        path = module["path"]
        outgoing = graph.get(path, set())

        # Verificar se alguém importa este módulo
        incoming = {k for k, v in graph.items() if path in v}

        if len(incoming) == 0 and len(outgoing) == 0:
            orphans.append({"path": path, "reason": "ISOLADO - Sem imports nem sendo importado"})
        elif len(incoming) == 0:
            orphans.append({"path": path, "reason": f"SEM INCOMING - {len(outgoing)} outgoing"})

    return orphans


def generate_quadruple_table(modules_data):
    """Gera tabela quádrupla."""
    rows = []

    for module in modules_data:
        pat = module["patterns"]
        rows.append(
            {
                "Pasta/Modulo": f"{module['folder']}/{module['name']}.py",
                "Φ/IIT": "✅" if pat.get("MATEMATICA") else "❌",
                "Topo": "✅" if pat.get("TOPOLOGICA") else "❌",
                "σ/Entropia": "✅" if pat.get("ENTROPICA") else "❌",
                "Psicanálise": "✅" if pat.get("PSICANALITICA") else "❌",
                "Quântico": "✅" if pat.get("QUANTICO") else "❌",
                "Linhas": module["lines"],
                "Funções": module["functions_count"],
                "Classes": module["classes_count"],
            }
        )

    return rows


def main():
    print("🔬 AUDITORIA CIENTÍFICA PROFUNDA - OMNIMIND")
    print("=" * 80)
    print(f"Raiz: {SRC_DIR}")
    print()

    # 1. Coletar todos os módulos Python
    py_files = list(SRC_DIR.rglob("*.py"))
    py_files = [f for f in py_files if "__pycache__" not in str(f)]

    print(f"📁 Total de módulos Python: {len(py_files)}")
    print()

    # 2. Analisar cada módulo
    print("🔍 Analisando módulos...")
    modules_data = []
    for py_file in py_files:
        data = analyze_module(py_file)
        modules_data.append(data)

    print(f"✅ {len(modules_data)} módulos analisados")
    print()

    # 3. Construir grafo de dependências
    print("🗺️  Construindo grafo de dependências...")
    graph = build_dependency_graph(modules_data)
    print(f"✅ {len(graph)} módulos com dependências")
    print()

    # 4. Encontrar órfãos
    print("🚨 Detectando módulos órfãos...")
    orphans = find_orphans(modules_data, graph)
    print(f"⚠️  {len(orphans)} módulos desconectados")
    print()

    # 5. Gerar tabela quádrupla
    print("📊 Gerando tabela quádrupla...")
    table = generate_quadruple_table(modules_data)

    # 6. Estatísticas
    stats = {
        "total_modules": len(modules_data),
        "total_lines": sum(m["lines"] for m in modules_data),
        "total_functions": sum(m["functions_count"] for m in modules_data),
        "total_classes": sum(m["classes_count"] for m in modules_data),
        "with_matematica": sum(1 for m in modules_data if m["patterns"].get("MATEMATICA")),
        "with_topologica": sum(1 for m in modules_data if m["patterns"].get("TOPOLOGICA")),
        "with_entropica": sum(1 for m in modules_data if m["patterns"].get("ENTROPICA")),
        "with_psicanalitica": sum(1 for m in modules_data if m["patterns"].get("PSICANALITICA")),
        "with_quantico": sum(1 for m in modules_data if m["patterns"].get("QUANTICO")),
        "orphans": len(orphans),
    }

    # 7. Salvar resultados
    output = {
        "timestamp": "2025-12-21T01:40:00-03:00",
        "stats": stats,
        "table": table,
        "orphans": orphans,
        "modules_detailed": modules_data,
    }

    output_path = PROJECT_ROOT / "data/audit/SCIENTIFIC_DEEP_AUDIT.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"💾 Relatório salvo: {output_path.relative_to(PROJECT_ROOT)}")

    # 8. Exibir resumo
    print("\n" + "=" * 80)
    print("📊 ESTATÍSTICAS GLOBAIS")
    print("=" * 80)
    for key, value in stats.items():
        print(f"{key:.<40} {value}")

    print("\n" + "=" * 80)
    print("🚨 TOP 10 MÓDULOS ÓRFÃOS")
    print("=" * 80)
    for i, orphan in enumerate(orphans[:10], 1):
        print(f"{i}. {orphan['path']}")
        print(f"   Razão: {orphan['reason']}")

    print("\n" + "=" * 80)
    print("📋 AMOSTRA TABELA QUÁDRUPLA (Primeiros 10)")
    print("=" * 80)
    for row in table[:10]:
        print(f"\n{row['Pasta/Modulo']}")
        print(
            f"  Φ/IIT: {row['Φ/IIT']} | Topo: {row['Topo']} | σ: {row['σ/Entropia']} | Psi: {row['Psicanálise']} | Q: {row['Quântico']}"
        )
        print(f"  {row['Linhas']} linhas, {row['Funções']} funções, {row['Classes']} classes")


if __name__ == "__main__":
    main()
