import os
import ast
import json
from collections import defaultdict


class ProjectCartographer:
    def __init__(self, root_dirs=["./src", "./scripts"]):
        self.root_dirs = root_dirs
        self.project_map = {}
        self.concept_tags = {
            "COGNITION": ["phi", "iit", "tononi", "integration", "workspace", "global_workspace"],
            "PSYCHOANALYSIS": [
                "lacan",
                "freud",
                "desire",
                "drive",
                "jouissance",
                "unconscious",
                "castration",
            ],
            "PHILOSOPHY": ["deleuze", "rhizome", "territory", "deterritorialization", "machine"],
            "MEMORY": ["qdrant", "chroma", "vector", "embedding", "retrieval", "alchemist"],
            "SYSTEM": ["sovereign", "daemon", "process", "linux", "gpu", "cpu", "membrane"],
            "LEGACY": ["devbrain", "old_core", "deprecated"],
        }

    def analyze_file(self, filepath):
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            try:
                content = f.read()
                tree = ast.parse(content)
            except:
                return None

        imports = []
        classes = []
        functions = []
        concepts_found = set()

        # 1. Análise AST (Estrutura)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    imports.append(n.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, ast.FunctionDef):
                functions.append(node.name)

        # 2. Análise Semântica (Conceitos)
        content_lower = content.lower()
        for category, keywords in self.concept_tags.items():
            for kw in keywords:
                if kw in content_lower:
                    concepts_found.add(category)

        return {
            "path": filepath,
            "imports": list(set(imports)),
            "classes": classes,
            "functions_count": len(functions),
            "concepts": list(concepts_found),
            "loc": len(content.splitlines()),
        }

    def scan(self):
        for root_dir in self.root_dirs:
            for root, _, files in os.walk(root_dir):
                for file in files:
                    if file.endswith(".py"):
                        path = os.path.join(root, file)
                        analysis = self.analyze_file(path)
                        if analysis:
                            self.project_map[path] = analysis
        return self.project_map


if __name__ == "__main__":
    mapper = ProjectCartographer()
    data = mapper.scan()

    # Salva o JSON para análise do Fabrício
    with open("omnimind_structure_map.json", "w") as f:
        json.dump(data, f, indent=2)

    print("Mapeamento concluído. JSON gerado.")
