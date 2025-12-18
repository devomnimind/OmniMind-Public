#!/usr/bin/env python3
"""
🔍 ANALISADOR AUTOMÁTICO OMNIMIND SRC → READMEs por pasta

Analisa todas as pastas src/ e gera/complementa READMEs com:
- Classes principais e métodos
- Funções standalone com assinaturas
- Tipos e docstrings
- Estrutura de arquivos
- Integração com outros módulos

Usa AST para análise precisa sem imports (seguro).
"""

import ast
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# ============================================================================
# DATA MODELS
# ============================================================================


@dataclass
class ArgInfo:
    """Informação sobre um argumento de função."""

    name: str
    type_hint: str = "Any"
    default: Optional[str] = None


@dataclass
class MethodInfo:
    """Informação sobre um método de classe."""

    name: str
    signature: str
    args: List[ArgInfo]
    returns: str = "None"
    docstring: Optional[str] = None
    is_property: bool = False
    is_classmethod: bool = False
    is_staticmethod: bool = False


@dataclass
class ClassInfo:
    """Informação sobre uma classe."""

    name: str
    docstring: Optional[str] = None
    bases: List[str] = field(default_factory=list)
    methods: List[MethodInfo] = field(default_factory=list)
    file_path: str = ""
    line_number: int = 0


@dataclass
class FunctionInfo:
    """Informação sobre uma função standalone."""

    name: str
    signature: str
    args: List[ArgInfo]
    returns: str = "None"
    docstring: Optional[str] = None
    file_path: str = ""
    line_number: int = 0


@dataclass
class ModuleInfo:
    """Informação sobre um módulo (arquivo .py)."""

    path: str
    classes: List[ClassInfo] = field(default_factory=list)
    functions: List[FunctionInfo] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    docstring: Optional[str] = None


# ============================================================================
# AST ANALYZER
# ============================================================================


class ASTAnalyzer(ast.NodeVisitor):
    """Extrai informações de módulos Python via AST."""

    def __init__(self, source_code: str, file_path: str):
        self.source_code = source_code
        self.file_path = file_path
        self.module_info = ModuleInfo(path=file_path)
        self.current_class: Optional[ClassInfo] = None

    def analyze(self) -> ModuleInfo:
        """Analisa código e retorna ModuleInfo."""
        try:
            tree = ast.parse(self.source_code)
            self.module_info.docstring = ast.get_docstring(tree)
            self.visit(tree)
        except SyntaxError as e:
            print(f"⚠️  Syntax error em {self.file_path}: {e}")
        return self.module_info

    def visit_ClassDef(self, node: ast.ClassDef):
        """Visita definição de classe."""
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(ast.unparse(base))

        class_info = ClassInfo(
            name=node.name,
            docstring=ast.get_docstring(node),
            bases=bases,
            file_path=self.file_path,
            line_number=node.lineno,
        )

        # Extrair métodos
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method = self._extract_method(item, node.name)
                class_info.methods.append(method)

        self.module_info.classes.append(class_info)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Visita definição de função standalone."""
        # Pular se estiver dentro de classe (capturado em visit_ClassDef)
        if not self.current_class:
            func_info = self._extract_function(node)
            self.module_info.functions.append(func_info)
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import):
        """Captura imports."""
        for alias in node.names:
            self.module_info.imports.append(f"import {alias.name}")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Captura from imports."""
        module = node.module or ""
        names = ", ".join([alias.name for alias in node.names])
        self.module_info.imports.append(f"from {module} import {names}")
        self.generic_visit(node)

    def _extract_method(self, node: ast.FunctionDef, class_name: str) -> MethodInfo:
        """Extrai informações de um método."""
        signature = ast.unparse(node)
        args = self._extract_args(node)
        returns = ast.unparse(node.returns) if node.returns else "None"

        # Detectar decoradores
        is_property = any(
            isinstance(dec, ast.Name) and dec.id == "property" for dec in node.decorator_list
        )
        is_classmethod = any(
            isinstance(dec, ast.Name) and dec.id == "classmethod" for dec in node.decorator_list
        )
        is_staticmethod = any(
            isinstance(dec, ast.Name) and dec.id == "staticmethod" for dec in node.decorator_list
        )

        return MethodInfo(
            name=node.name,
            signature=signature,
            args=args,
            returns=returns,
            docstring=ast.get_docstring(node),
            is_property=is_property,
            is_classmethod=is_classmethod,
            is_staticmethod=is_staticmethod,
        )

    def _extract_function(self, node: ast.FunctionDef) -> FunctionInfo:
        """Extrai informações de uma função."""
        signature = ast.unparse(node)
        args = self._extract_args(node)
        returns = ast.unparse(node.returns) if node.returns else "None"

        return FunctionInfo(
            name=node.name,
            signature=signature,
            args=args,
            returns=returns,
            docstring=ast.get_docstring(node),
            file_path=self.file_path,
            line_number=node.lineno,
        )

    def _extract_args(self, node: ast.FunctionDef) -> List[ArgInfo]:
        """Extrai argumentos de uma função."""
        args = []
        for arg in node.args.args:
            type_hint = "Any"
            if arg.annotation:
                type_hint = ast.unparse(arg.annotation)
            args.append(ArgInfo(name=arg.arg, type_hint=type_hint))

        # Kwargs
        if node.args.kwarg:
            args.append(ArgInfo(name=f"**{node.args.kwarg.arg}", type_hint="Any"))

        return args


# ============================================================================
# README GENERATOR
# ============================================================================


class ReadmeGenerator:
    """Gera/complementa README.md para cada pasta src/."""

    def __init__(self, src_path: str = "src"):
        self.src_path = Path(src_path)
        self.folder_data: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {
                "modules": [],
                "classes": [],
                "functions": [],
            }
        )

    def analyze_folder(self, folder_path: Path):
        """Analisa todas arquivos Python em uma pasta."""
        for py_file in sorted(folder_path.glob("*.py")):
            if py_file.name.startswith("__"):
                continue

            self._analyze_file(py_file)

    def _analyze_file(self, file_path: Path):
        """Analisa um arquivo Python."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()

            analyzer = ASTAnalyzer(source, str(file_path.relative_to(self.src_path)))
            module_info = analyzer.analyze()

            folder_name = file_path.parent.name
            self.folder_data[folder_name]["modules"].append(module_info)

            # Agregar classes e funções
            self.folder_data[folder_name]["classes"].extend(module_info.classes)
            self.folder_data[folder_name]["functions"].extend(module_info.functions)

        except Exception as e:
            print(f"❌ Erro ao analisar {file_path}: {e}")

    def generate_all(self):
        """Gera READMEs para todas as pastas."""
        for folder in sorted(self.src_path.iterdir()):
            if not folder.is_dir() or folder.name.startswith("__"):
                continue

            self.analyze_folder(folder)

            # Gerar/complementar README
            readme_path = folder / "README.md"
            content = self._generate_readme(folder.name, self.folder_data[folder.name])

            # Se README existe, adicionar seção de API
            if readme_path.exists():
                existing = readme_path.read_text()
                content = self._merge_readmes(existing, content, folder.name)

            readme_path.write_text(content)
            print(f"✅ {readme_path}")

    def _generate_readme(self, folder_name: str, data: Dict) -> str:
        """Gera conteúdo README completo."""
        classes = data["classes"]
        functions = data["functions"]
        modules = data["modules"]

        content = f"""# 📁 {folder_name.upper()}

**{len(classes)} Classes | {len(functions)} Funções | {len(modules)} Módulos**

---

## 🏗️ Classes Principais

"""
        # Top 10 classes
        for cls in sorted(classes, key=lambda c: len(c.methods), reverse=True)[:10]:
            content += self._format_class(cls)

        content += "\n## ⚙️ Funções Públicas\n\n"

        # Top 15 functions
        for func in sorted(functions, key=lambda f: f.name)[:15]:
            content += self._format_function(func)

        content += f"\n## 📦 Módulos\n\n**Total:** {len(modules)} arquivos\n\n"
        for module in sorted(modules, key=lambda m: m.path):
            content += f"- `{Path(module.path).name}`: "
            if module.docstring:
                content += f"{module.docstring[:60]}...\n"
            else:
                content += f"{len(module.classes)} classes, {len(module.functions)} functions\n"

        return content

    def _format_class(self, cls: ClassInfo) -> str:
        """Formata informações de uma classe."""
        bases = f"({', '.join(cls.bases)})" if cls.bases else ""
        content = f"### `{cls.name}{bases}`\n\n"

        if cls.docstring:
            content += f"{cls.docstring}\n\n"

        # Top 5 métodos
        methods = [m for m in cls.methods if not m.name.startswith("_")][:5]
        if methods:
            content += "**Métodos principais:**\n\n"
            for method in methods:
                content += f"- `{method.name}({self._format_args_short(method.args)})` → `{method.returns}`\n"
                if method.docstring:
                    content += f"  > {method.docstring[:80]}...\n"

        content += "\n"
        return content

    def _format_function(self, func: FunctionInfo) -> str:
        """Formata informações de uma função."""
        args = self._format_args_short(func.args)
        content = f"#### `{func.name}({args})` → `{func.returns}`\n\n"

        if func.docstring:
            content += f"*{func.docstring[:100]}...*\n\n"

        return content

    def _format_args_short(self, args: List[ArgInfo]) -> str:
        """Formata argumentos de forma curta."""
        return ", ".join(
            [
                f"{a.name}: {a.type_hint.split('.')[-1]}"
                for a in args
                if not a.name.startswith("self")
            ]
        )[:50]

    def _merge_readmes(self, existing: str, new_content: str, folder_name: str) -> str:
        """Mescla README existente com novo conteúdo."""
        # Preservar seções existentes antes de API Reference
        if "## 🏗️ Classes Principais" in existing:
            # Se já tem seção de API, substituir apenas a parte
            before = existing.split("## 🏗️ Classes Principais")[0]
            return before + new_content
        else:
            # Adicionar seção de API ao final
            api_section = "\n---\n\n## 📚 API Reference\n\n" + new_content
            return existing + api_section


# ============================================================================
# MAIN
# ============================================================================


def main():
    """Executa análise e geração de READMEs."""
    print("\n" + "=" * 60)
    print("🔍 ANALISADOR SRC OMNIMIND")
    print("=" * 60 + "\n")

    generator = ReadmeGenerator("src")
    generator.generate_all()

    print("\n" + "=" * 60)
    print("✅ ANÁLISE COMPLETA!")
    print("=" * 60)
    print("\n📊 READMEs gerados/complementados em:")
    print("   src/*/README.md")
    print("\n💡 Próximos passos:")
    print("   - Revisar READMEs gerados")
    print("   - Adicionar exemplos de uso")
    print("   - Completar seções faltantes")
    print("\n")


if __name__ == "__main__":
    main()
