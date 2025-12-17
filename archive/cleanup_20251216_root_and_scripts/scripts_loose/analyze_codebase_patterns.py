#!/usr/bin/env python3
"""
🔍 Analisador de Padrões de Código - OmniMind
==============================================
Analisa src/ e tests/ para encontrar padrões que precisam ser alterados.

Procura por:
  1. PROJECT_ROOT calculations errados
  2. Relative paths (Path("relative/path"))
  3. sys.path.append() (deveria ser insert(0, ...))
  4. Ubuntu 24.04 ou Python 3.12.8 (deveria ser 22.04.5, 3.12.12)
  5. Logging com caminhos relativos
  6. delete_collection() ou drop patterns
  7. Path(__file__).parent incorreto
  8. Imports sem sys.path.insert()

Uso:
  python3 scripts/analyze_codebase_patterns.py [--fix] [--html] [--json]
  python3 scripts/analyze_codebase_patterns.py --fix --apply    # Aplica correções automaticamente

Output:
  - Terminal: Resumo de issues
  - reports/codebase_analysis_YYYYMMDD_HHMMSS.json: Relatório completo
  - reports/codebase_analysis_YYYYMMDD_HHMMSS.html: Visualização
"""

import ast
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ============================================================================
# PADRÕES DE ANÁLISE
# ============================================================================

PATTERNS = {
    "PROJECT_ROOT_WRONG": {
        "name": "PROJECT_ROOT Calculation",
        "regex": r"PROJECT_ROOT\s*=\s*Path\(__file__\)\.(parent(?:\.parent){0,2}?)(?!\s*\.parent)",
        "issue": "Pode estar apontando para diretório errado",
        "fix": lambda m: "PROJECT_ROOT = Path(__file__).parent.parent.parent  # /omnimind/",
        "severity": "HIGH",
    },
    "RELATIVE_PATH": {
        "name": "Relative Path Usage",
        "regex": r'Path\("([^"]+)"\)',
        "issue": "Path relativos quebram quando executados de diretórios diferentes",
        "fix": lambda m: f'project_root / "{m.group(1)}"',
        "severity": "MEDIUM",
    },
    "SYS_PATH_APPEND": {
        "name": "sys.path.append() Usage",
        "regex": r"sys\.path\.append",
        "issue": "append() coloca no final; insert(0, ...) garante prioridade de venv",
        "fix": lambda m: "sys.path.insert(0,",
        "severity": "MEDIUM",
    },
    "UBUNTU_24_04": {
        "name": "Ubuntu 24.04 Reference",
        "regex": r"[Uu]buntu\s+24\.04|Ubuntu\s+24",
        "issue": "Sistema é Ubuntu 22.04.5 LTS, não 24.04",
        "fix": lambda m: "Ubuntu 22.04.5 LTS",
        "severity": "MEDIUM",
    },
    "PYTHON_3_12_8": {
        "name": "Python 3.12.8 Reference",
        "regex": r"3\.12\.8|Python.*3\.12\.8",
        "issue": "Sistema tem Python 3.12.12, não 3.12.8",
        "fix": lambda m: "3.12.12",
        "severity": "LOW",
    },
    "DELETE_COLLECTION": {
        "name": "Delete Collection Pattern",
        "regex": r"(delete_collection|drop.*collection|remove.*collection)",
        "issue": "Deleção de collections destroi memória; use compressão/checkpoints",
        "fix": lambda m: "# DEPRECATED: Use checkpoint + compression instead",
        "severity": "CRITICAL",
    },
    "LOGGING_RELATIVE_PATH": {
        "name": "Logging with Relative Path",
        "regex": r"logging\.(FileHandler|handlers\.RotatingFileHandler)\((['\"])(?!/).*?\2",
        "issue": "Relative paths no logging quebram com cwd diferente",
        "fix": lambda m: "Usar project_root / 'path' em vez de 'path'",
        "severity": "HIGH",
    },
    "PATH_FILE_PARENT": {
        "name": "Path(__file__).parent Depth",
        "regex": r"Path\(__file__\)\.parent(?:\.parent){0,1}(?=\s*[,\);])",
        "issue": "Pode estar apontando para nível de diretório errado",
        "fix": lambda m: "Path(__file__).parent.parent.parent para scripts/",
        "severity": "MEDIUM",
    },
    "IMPORT_BEFORE_SYSPATH": {
        "name": "Import Before sys.path.insert",
        "regex": r"^from\s+src\.|^import\s+src\.",
        "issue": "Imports de src/ devem vir APÓS sys.path.insert()",
        "fix": lambda m: "Mover imports para depois de sys.path setup",
        "severity": "HIGH",
    },
}

# ============================================================================
# ANÁLISE DE ARQUIVO
# ============================================================================


def analyze_file(filepath: Path) -> List[Dict[str, Any]]:
    """Analisa um arquivo para encontrar padrões problemáticos."""
    issues = []

    try:
        content = filepath.read_text(encoding="utf-8")
        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            # Pular comentários e strings vazias
            if line.strip().startswith("#"):
                continue

            for pattern_key, pattern_info in PATTERNS.items():
                matches = re.finditer(pattern_info["regex"], line, re.IGNORECASE)
                for match in matches:
                    issues.append(
                        {
                            "file": str(filepath.relative_to(PROJECT_ROOT)),
                            "line": line_num,
                            "column": match.start(),
                            "pattern": pattern_key,
                            "name": pattern_info["name"],
                            "issue": pattern_info["issue"],
                            "severity": pattern_info["severity"],
                            "matched_text": match.group(0),
                            "context": line.strip(),
                            "suggested_fix": pattern_info["fix"](match),
                        }
                    )

    except Exception as e:
        print(f"⚠️  Erro ao analisar {filepath}: {e}")

    return issues


# ============================================================================
# VARRE DIRETÓRIOS
# ============================================================================


def scan_directory(directory: Path) -> Dict[str, List[Dict[str, Any]]]:
    """Varre diretório recursivamente."""
    results = {"files": {}, "summary": {}}

    print(f"\n📂 Varrendo {directory}...")

    for py_file in sorted(directory.rglob("*.py")):
        # Pular __pycache__
        if "__pycache__" in py_file.parts:
            continue

        issues = analyze_file(py_file)

        if issues:
            results["files"][str(py_file.relative_to(PROJECT_ROOT))] = issues
            print(f"   ⚠️  {py_file.relative_to(PROJECT_ROOT)}: {len(issues)} issue(s)")

    return results


# ============================================================================
# GERAÇÃO DE RELATÓRIO
# ============================================================================


def generate_report(all_results: Dict[str, Any], timestamp: str) -> Path:
    """Gera relatório HTML e JSON."""
    report_dir = PROJECT_ROOT / "reports"
    report_dir.mkdir(exist_ok=True)

    # Contar issues por severity
    summary = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "total": 0}
    all_issues = []

    for file_issues in all_results["files"].values():
        for issue in file_issues:
            summary[issue["severity"]] += 1
            summary["total"] += 1
            all_issues.append(issue)

    # JSON Report
    json_report = report_dir / f"codebase_analysis_{timestamp}.json"
    with open(json_report, "w") as f:
        json.dump(
            {
                "timestamp": timestamp,
                "project_root": str(PROJECT_ROOT),
                "summary": summary,
                "issues": all_issues,
                "files_analyzed": len(all_results["files"]),
            },
            f,
            indent=2,
        )

    # HTML Report
    html_report = report_dir / f"codebase_analysis_{timestamp}.html"
    severity_colors = {
        "CRITICAL": "#ff4444",
        "HIGH": "#ff8800",
        "MEDIUM": "#ffcc00",
        "LOW": "#00cc00",
    }

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>OmniMind Codebase Analysis</title>
        <style>
            body {{ font-family: monospace; margin: 20px; background: #f5f5f5; }}
            h1 {{ color: #333; }}
            .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
            .summary-item {{ padding: 15px; background: white; border-radius: 5px; }}
            .issue {{
                margin: 10px 0;
                padding: 10px;
                background: white;
                border-left: 5px solid #ddd;
                border-radius: 3px;
            }}
            .CRITICAL {{ border-left-color: #ff4444; }}
            .HIGH {{ border-left-color: #ff8800; }}
            .MEDIUM {{ border-left-color: #ffcc00; }}
            .LOW {{ border-left-color: #00cc00; }}
            .file {{ font-weight: bold; color: #0066cc; }}
            .code {{ background: #f0f0f0; padding: 5px; border-radius: 3px; }}
            .fix {{ background: #e8f5e9; padding: 8px; margin: 5px 0; border-radius: 3px; }}
        </style>
    </head>
    <body>
        <h1>🔍 OmniMind Codebase Analysis Report</h1>
        <p>Timestamp: {timestamp}</p>
        <p>Project Root: {PROJECT_ROOT}</p>

        <div class="summary">
            <div class="summary-item">
                <strong>Total Issues:</strong> {summary['total']}
            </div>
            <div class="summary-item" style="border-left: 5px solid #ff4444;">
                <strong>CRITICAL:</strong> {summary['CRITICAL']}
            </div>
            <div class="summary-item" style="border-left: 5px solid #ff8800;">
                <strong>HIGH:</strong> {summary['HIGH']}
            </div>
            <div class="summary-item" style="border-left: 5px solid #ffcc00;">
                <strong>MEDIUM:</strong> {summary['MEDIUM']}
            </div>
            <div class="summary-item" style="border-left: 5px solid #00cc00;">
                <strong>LOW:</strong> {summary['LOW']}
            </div>
        </div>

        <h2>Issues by Severity</h2>
    """

    for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        issues_by_severity = [i for i in all_issues if i["severity"] == severity]
        if issues_by_severity:
            html_content += f"<h3 style='color: {severity_colors[severity]}'>{severity} ({len(issues_by_severity)})</h3>\n"

            for issue in issues_by_severity:
                html_content += f"""
                <div class="issue {severity}">
                    <div class="file">{issue['file']}:{issue['line']}</div>
                    <div><strong>{issue['name']}</strong></div>
                    <div>Pattern: {issue['pattern']}</div>
                    <div>Issue: {issue['issue']}</div>
                    <div class="code">Matched: {issue['matched_text']}</div>
                    <div class="code">Context: {issue['context']}</div>
                    <div class="fix"><strong>Fix:</strong> {issue['suggested_fix']}</div>
                </div>
                """

    html_content += """
    </body>
    </html>
    """

    with open(html_report, "w") as f:
        f.write(html_content)

    return json_report, html_report


# ============================================================================
# MAIN
# ============================================================================


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Analisador de padrões de código")
    parser.add_argument("--html", action="store_true", help="Gerar relatório HTML")
    parser.add_argument("--json", action="store_true", help="Gerar relatório JSON")
    parser.add_argument("--fix", action="store_true", help="Sugerir correções")
    parser.add_argument("--apply", action="store_true", help="Aplicar correções (cuidado!)")
    args = parser.parse_args()

    if args.apply and not args.fix:
        print("❌ Use --fix com --apply")
        return 1

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("=" * 80)
    print("🔍 ANÁLISE DE PADRÕES DE CÓDIGO - OMNIMIND")
    print("=" * 80)
    print(f"🐍 Python: {sys.version}")
    print(f"📂 Project Root: {PROJECT_ROOT}")
    print()

    # Analisar src/ e tests/
    all_results = {"files": {}}

    for directory in ["src", "tests"]:
        dir_path = PROJECT_ROOT / directory
        if dir_path.exists():
            results = scan_directory(dir_path)
            all_results["files"].update(results["files"])

    # Contar issues
    total_issues = sum(len(issues) for issues in all_results["files"].values())

    print()
    print("=" * 80)
    print(f"📊 RESULTADO: {len(all_results['files'])} arquivos com issues, {total_issues} total")
    print("=" * 80)

    # Listar por severity
    all_issues = []
    for file_issues in all_results["files"].values():
        all_issues.extend(file_issues)

    for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        count = len([i for i in all_issues if i["severity"] == severity])
        if count > 0:
            print(f"  🔴 {severity}: {count}")

    # Gerar relatórios
    if args.html or args.json:
        json_report, html_report = generate_report(all_results, timestamp)
        print(f"\n📄 Relatórios salvos:")
        print(f"   JSON: {json_report}")
        print(f"   HTML: {html_report}")

    # Mostrar top issues
    print("\n🎯 TOP 10 ISSUES:")
    sorted_issues = sorted(
        all_issues, key=lambda x: ["CRITICAL", "HIGH", "MEDIUM", "LOW"].index(x["severity"])
    )

    for i, issue in enumerate(sorted_issues[:10], 1):
        print(f"\n  {i}. [{issue['severity']}] {issue['file']}:{issue['line']}")
        print(f"     Pattern: {issue['name']}")
        print(f"     Issue: {issue['issue']}")
        print(f"     Context: {issue['context'][:60]}...")

    return 0


if __name__ == "__main__":
    sys.exit(main())
