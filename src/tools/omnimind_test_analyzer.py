#!/usr/bin/env python3
"""
🧪 OmniMind Test Suite Analyzer - Análise Completa
Ubuntu 22.04 LTS + GPU + Linux Containers + Sudo
Apuração completa para correção da suite pytest
"""

import ast
import json
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# Colors
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"


@dataclass
class TestMetrics:
    """Métricas de teste"""

    total_tests: int = 0
    total_files: int = 0
    passing: int = 0
    failing: int = 0
    skipped: int = 0
    xfail: int = 0
    errors: int = 0
    success_rate: float = 0.0
    avg_runtime: float = 0.0
    coverage_percent: float = 0.0


@dataclass
class EnvironmentInfo:
    """Informações do ambiente"""

    os_version: str
    python_version: str
    pytest_version: str
    docker_enabled: bool
    gpu_enabled: bool
    container_enabled: bool
    sudo_available: bool
    venv_active: bool
    venv_path: Optional[str] = None


@dataclass
class TestIssue:
    """Problema detectado em teste"""

    severity: str  # critical, high, medium, low
    type: str  # missing_fixture, deprecated, incompatible, etc
    test_file: str
    test_name: Optional[str]
    message: str
    suggestion: str
    affected_tests: int = 1


class OmniMindTestAnalyzer:
    """Analisador completo de suite pytest do OmniMind"""

    def __init__(self, repo_path: str = "/home/fahbrain/projects/omnimind"):
        self.repo_path = Path(repo_path)
        self.tests_dir = self.repo_path / "tests"
        self.src_dir = self.repo_path / "src"

        self.env_info: Optional[EnvironmentInfo] = None
        self.metrics = TestMetrics()
        self.issues: List[TestIssue] = []
        self.test_results: Dict[str, Any] = {}
        self.compatibility_matrix: Dict[str, List[str]] = {}
        self.conftest_fixtures: Set[str] = set()
        self.all_test_functions: Dict[str, List[str]] = {}
        self.deprecated_patterns: List[str] = []

        print(f"\n{CYAN}{'='*80}{RESET}")
        print(f"{BOLD}🧪 OmniMind Test Suite Analyzer{RESET}")
        print(f"{CYAN}{'='*80}{RESET}")
        print(f"📁 Repo: {self.repo_path}")
        print(f"📂 Tests: {self.tests_dir}")
        print(f"📂 Src: {self.src_dir}\n")

    def run_full_analysis(self) -> Dict[str, Any]:
        """Executa análise completa"""
        print(f"{BOLD}INICIANDO ANÁLISE COMPLETA...{RESET}\n")

        # 1. Environment
        self.analyze_environment()

        # 2. Scan fixtures
        self.extract_fixtures()

        # 3. Scan all tests
        self.scan_test_files()

        # 4. Detect issues
        self.detect_compatibility_issues()

        # 5. Run pytest
        self.run_pytest_analysis()

        # 6. Coverage analysis
        self.analyze_coverage()

        # 7. Generate report
        report = self.generate_report()

        print(f"\n{CYAN}{'='*80}{RESET}")
        print(f"{GREEN}✅ ANÁLISE CONCLUÍDA{RESET}")
        print(f"{CYAN}{'='*80}{RESET}\n")

        return report

    def analyze_environment(self):
        """Analisa configuração do ambiente"""
        print(f"{MAGENTA}[1/7]{RESET} 🔍 Analisando Ambiente...")

        # OS
        try:
            with open("/etc/os-release") as f:
                content = f.read()
                if "22.04" in content:
                    os_version = "Ubuntu 22.04 LTS"
                elif "jammy" in content:
                    os_version = "Ubuntu 22.04 LTS (jammy)"
                else:
                    os_version = "Linux (Unknown)"
        except Exception:
            os_version = "Unknown"

        # Python
        try:
            result = subprocess.run(["python3", "--version"], capture_output=True, text=True)
            python_version = result.stdout.strip()
        except Exception:
            python_version = "Unknown"

        # Pytest
        try:
            result = subprocess.run(["pytest", "--version"], capture_output=True, text=True)
            pytest_version = result.stdout.strip()
        except Exception:
            pytest_version = "Unknown"

        # Docker
        try:
            subprocess.run(["docker", "ps"], capture_output=True, timeout=5)
            docker_enabled = True
        except Exception:
            docker_enabled = False

        # GPU
        try:
            subprocess.run(["nvidia-smi"], capture_output=True, timeout=5)
            gpu_enabled = True
        except Exception:
            gpu_enabled = False

        # Linux Containers
        container_enabled = (
            Path("/run/systemd/container").exists()
            or Path("/.dockerenv").exists()
            or Path("/etc/lxc").exists()
        )

        # Sudo
        try:
            subprocess.run(["sudo", "-n", "true"], capture_output=True, timeout=5)
            sudo_available = True
        except Exception:
            sudo_available = False

        # VirtualEnv
        venv_active = hasattr(sys, "real_prefix") or (
            hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
        )
        venv_path = sys.prefix if venv_active else None

        self.env_info = EnvironmentInfo(
            os_version=os_version,
            python_version=python_version,
            pytest_version=pytest_version,
            docker_enabled=docker_enabled,
            gpu_enabled=gpu_enabled,
            container_enabled=container_enabled,
            sudo_available=sudo_available,
            venv_active=venv_active,
            venv_path=venv_path,
        )

        print(f"   {GREEN}✅{RESET} OS: {self.env_info.os_version}")
        print(f"   {GREEN}✅{RESET} Python: {self.env_info.python_version}")
        print(f"   {GREEN}✅{RESET} Pytest: {self.env_info.pytest_version}")
        print(f"   {'🐳' if docker_enabled else '❌'} Docker: {'Sim' if docker_enabled else 'Não'}")
        print(f"   {'🔋' if gpu_enabled else '❌'} GPU: {'Sim' if gpu_enabled else 'Não'}")
        print(
            f"   {'📦' if container_enabled else '❌'} Containers: "
            f"{'Sim' if container_enabled else 'Não'}"
        )
        print(f"   {'🔐' if sudo_available else '❌'} Sudo: {'Sim' if sudo_available else 'Não'}")
        print(f"   {'🐍' if venv_active else '❌'} VEnv: {venv_path or 'Não'}\n")

    def extract_fixtures(self):
        """Extrai todas as fixtures disponíveis"""
        print(f"{MAGENTA}[2/7]{RESET} 🔧 Extraindo Fixtures...")

        fixtures = set()

        # Global fixtures
        for conftest in self.tests_dir.rglob("conftest.py"):
            try:
                content = conftest.read_text(encoding="utf-8", errors="ignore")
                for match in re.finditer(r"@pytest\.fixture.*?\ndef\s+(\w+)", content, re.DOTALL):
                    fixtures.add(match.group(1))
            except Exception:
                pass

        # Built-in fixtures
        fixtures.update(
            [
                "tmp_path",
                "tmp_path_factory",
                "capsys",
                "capfd",
                "monkeypatch",
                "request",
                "fixture",
                "pytestmark",
                "marker",
                "config",
            ]
        )

        self.conftest_fixtures = fixtures
        print(f"   {GREEN}✅{RESET} Fixtures encontradas: {len(fixtures)}\n")

    def scan_test_files(self):
        """Escaneia todos os arquivos de teste"""
        print(f"{MAGENTA}[3/7]{RESET} 📖 Escaneando Arquivos de Teste...")

        test_files = list(self.tests_dir.rglob("test_*.py"))
        test_files += list(self.tests_dir.rglob("*_test.py"))

        print(f"   📁 Encontrados {len(test_files)} arquivos\n")

        for test_file in sorted(test_files):
            if "__pycache__" in str(test_file):
                continue

            try:
                with open(test_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                tree = ast.parse(content)
                test_funcs = []

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                        test_funcs.append(node.name)

                rel_path = str(test_file.relative_to(self.repo_path))
                self.all_test_functions[rel_path] = test_funcs
                self.metrics.total_tests += len(test_funcs)
                self.metrics.total_files += 1

                print(f"   📄 {CYAN}{rel_path}{RESET}")
                print(f"      └─ {len(test_funcs)} testes")

            except Exception as e:
                print(f"   {RED}❌ Erro em {test_file}: {e}{RESET}")
                self.issues.append(
                    TestIssue(
                        severity="high",
                        type="parse_error",
                        test_file=str(test_file),
                        test_name=None,
                        message=f"Erro ao parsear arquivo: {str(e)}",
                        suggestion="Verifique sintaxe Python do arquivo",
                    )
                )

        print(
            f"   {GREEN}✅{RESET} Total: {self.metrics.total_tests} testes "
            f"em {self.metrics.total_files} arquivos\n"
        )

    def detect_compatibility_issues(self):
        """Detecta problemas de compatibilidade"""
        print(f"{MAGENTA}[4/7]{RESET} 🔴 Detectando Problemas...")

        issues_found = 0

        for test_file, test_funcs in self.all_test_functions.items():
            filepath = self.repo_path / test_file

            try:
                content = filepath.read_text(encoding="utf-8", errors="ignore")
                tree = ast.parse(content)

                # Análise por padrão
                for node in ast.walk(tree):
                    # Check fixtures
                    if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                        params = [arg.arg for arg in node.args.args]
                        for param in params:
                            if param not in self.conftest_fixtures and param != "sel":
                                self.issues.append(
                                    TestIssue(
                                        severity="high",
                                        type="missing_fixture",
                                        test_file=test_file,
                                        test_name=node.name,
                                        message=f"Fixture não encontrada: '{param}'",
                                        suggestion="Defina a fixture em conftest.py",
                                    )
                                )
                                issues_found += 1

                    # Check deprecated
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name in ["imp", "distutils"]:
                                self.issues.append(
                                    TestIssue(
                                        severity="medium",
                                        type="deprecated_import",
                                        test_file=test_file,
                                        test_name=None,
                                        message=f"Import deprecado: '{alias.name}'",
                                        suggestion=(
                                            f"Substitua '{alias.name}' por " "alternativa moderna"
                                        ),
                                    )
                                )
                                issues_found += 1

            except Exception:
                pass

        print(f"   {YELLOW}⚠️  Problemas encontrados: {issues_found}{RESET}\n")

    def run_pytest_analysis(self):
        """Executa análise com pytest"""
        print(f"{MAGENTA}[5/7]{RESET} 🧪 Executando Pytest...")

        try:
            # Collect only
            result = subprocess.run(
                ["pytest", "--collect-only", "-q", str(self.tests_dir)],
                capture_output=True,
                text=True,
                timeout=60,
            )

            collect_output = result.stdout + result.stderr

            # Run tests with summary
            result = subprocess.run(
                ["pytest", "-v", "--tb=short", "--maxfail=5", str(self.tests_dir)],
                capture_output=True,
                text=True,
                timeout=300,
            )

            output = result.stdout + result.stderr

            # Parse results
            self.test_results = {
                "collect_output": collect_output,
                "run_output": output,
                "returncode": result.returncode,
            }

            # Extract metrics
            if "passed" in output:
                match = re.search(r"(\d+) passed", output)
                if match:
                    self.metrics.passing = int(match.group(1))

            if "failed" in output:
                match = re.search(r"(\d+) failed", output)
                if match:
                    self.metrics.failing = int(match.group(1))

            if "skipped" in output:
                match = re.search(r"(\d+) skipped", output)
                if match:
                    self.metrics.skipped = int(match.group(1))

            if "xfailed" in output:
                match = re.search(r"(\d+) xfailed", output)
                if match:
                    self.metrics.xfail = int(match.group(1))

            if "error" in output:
                match = re.search(r"(\d+) error", output)
                if match:
                    self.metrics.errors = int(match.group(1))

            # Calculate success rate
            total = self.metrics.passing + self.metrics.failing + self.metrics.errors
            if total > 0:
                self.metrics.success_rate = (self.metrics.passing / total) * 100

            print(f"   {GREEN}✅{RESET} Passed: {self.metrics.passing}")
            print(f"   {RED}❌{RESET} Failed: {self.metrics.failing}")
            print(f"   {YELLOW}⏭️ {RESET} Skipped: {self.metrics.skipped}")
            print(f"   {YELLOW}❌{RESET} XFailed: {self.metrics.xfail}")
            print(f"   {RED}🔥{RESET} Errors: {self.metrics.errors}")
            print(f"   {BOLD}📊 Taxa de sucesso: {self.metrics.success_rate:.1f}%{RESET}\n")

        except subprocess.TimeoutExpired:
            print(f"   {RED}❌ Timeout ao executar testes{RESET}\n")
        except Exception as e:
            print(f"   {RED}❌ Erro: {e}{RESET}\n")

    def analyze_coverage(self):
        """Analisa cobertura de testes"""
        print(f"{MAGENTA}[6/7]{RESET} 📊 Analisando Cobertura...")

        try:
            result = subprocess.run(
                ["pytest", "--cov=src", "--cov-report=term-missing", "-q", str(self.tests_dir)],
                capture_output=True,
                text=True,
                timeout=300,
            )

            output = result.stdout + result.stderr

            # Extract coverage percentage
            match = re.search(r"TOTAL\s+(\d+)\s+(\d+)\s+(\d+)%", output)
            if match:
                self.metrics.coverage_percent = float(match.group(3))

            print(f"   {GREEN}✅{RESET} Cobertura: {self.metrics.coverage_percent:.1f}%\n")

        except Exception:
            print(f"   {YELLOW}⚠️  Não foi possível analisar cobertura{RESET}\n")

    def generate_report(self) -> Dict[str, Any]:
        """Gera relatório executivo"""
        print(f"{MAGENTA}[7/7]{RESET} 📝 Gerando Relatório...\n")

        # Categorize issues by severity
        issues_by_severity = defaultdict(list)
        for issue in self.issues:
            issues_by_severity[issue.severity].append(asdict(issue))

        # Recommendations
        recommendations = self._generate_recommendations()

        report = {
            "timestamp": datetime.now().isoformat(),
            "environment": asdict(self.env_info) if self.env_info else {},
            "metrics": asdict(self.metrics),
            "summary": {
                "total_tests": self.metrics.total_tests,
                "total_files": self.metrics.total_files,
                "success_rate": f"{self.metrics.success_rate:.1f}%",
                "coverage": f"{self.metrics.coverage_percent:.1f}%",
                "total_issues": len(self.issues),
                "critical_issues": len(issues_by_severity.get("critical", [])),
                "high_issues": len(issues_by_severity.get("high", [])),
            },
            "test_breakdown": dict(
                sorted(self.all_test_functions.items(), key=lambda x: len(x[1]), reverse=True)
            ),
            "issues_by_severity": dict(issues_by_severity),
            "recommendations": recommendations,
            "next_steps": self._generate_next_steps(),
        }

        return report

    def _generate_recommendations(self) -> List[Dict[str, Any]]:
        """Gera recomendações baseadas em análise"""
        recommendations = []

        if self.env_info:
            # Environment checks
            if not self.env_info.gpu_enabled:
                recommendations.append(
                    {
                        "priority": "high",
                        "area": "GPU",
                        "message": "⚠️  GPU não detectada - Testes que usam GPU podem falhar",
                        "action": "Instale CUDA toolkit e nvidia-docker ou desative testes GPU",
                    }
                )

            if not self.env_info.docker_enabled:
                recommendations.append(
                    {
                        "priority": "medium",
                        "area": "Docker",
                        "message": (
                            "⚠️  Docker não disponível - " "Testes de containers não funcionarão"
                        ),
                        "action": "Instale Docker ou adicione fixtures para mock de containers",
                    }
                )

            if not self.env_info.sudo_available:
                recommendations.append(
                    {
                        "priority": "medium",
                        "area": "Permissões",
                        "message": "⚠️  Sudo sem password não configurado",
                        "action": "Configure sudoers para permitir commands sem password",
                    }
                )

        # Test issues
        if self.metrics.failing > 0:
            recommendations.append(
                {
                    "priority": "critical",
                    "area": "Testes",
                    "message": f"🔥 {self.metrics.failing} testes falhando",
                    "action": "Execute pytest com -vv para debugging detalhado",
                }
            )

        if self.metrics.success_rate < 80:
            recommendations.append(
                {
                    "priority": "high",
                    "area": "Qualidade",
                    "message": f"⚠️  Taxa de sucesso baixa: {self.metrics.success_rate:.1f}%",
                    "action": "Revise e corrija testes falhando antes de produção",
                }
            )

        if self.metrics.coverage_percent < 70:
            recommendations.append(
                {
                    "priority": "medium",
                    "area": "Cobertura",
                    "message": f"📊 Cobertura abaixo de 70%: {self.metrics.coverage_percent:.1f}%",
                    "action": "Adicione testes para aumentar cobertura",
                }
            )

        # Issue-based recommendations
        missing_fixtures = len([i for i in self.issues if i.type == "missing_fixture"])
        if missing_fixtures > 0:
            recommendations.append(
                {
                    "priority": "high",
                    "area": "Fixtures",
                    "message": f"🔧 {missing_fixtures} fixtures faltando",
                    "action": "Defina todas as fixtures em conftest.py",
                }
            )

        deprecated = len([i for i in self.issues if i.type == "deprecated_import"])
        if deprecated > 0:
            recommendations.append(
                {
                    "priority": "medium",
                    "area": "Deprecações",
                    "message": f"⚠️  {deprecated} imports deprecados encontrados",
                    "action": "Substitua por alternativas modernas",
                }
            )

        # General recommendations
        recommendations.extend(
            [
                {
                    "priority": "high",
                    "area": "Infraestrutura",
                    "message": "✅ Ubuntu 22.04 LTS detectado",
                    "action": "Atualize CI/CD para Python 3.10+",
                },
                {
                    "priority": "medium",
                    "area": "Monitoramento",
                    "message": "📈 Implemente CI/CD pipeline automático",
                    "action": "Configure GitHub Actions ou GitLab CI com análise de cobertura",
                },
            ]
        )

        return recommendations

    def _generate_next_steps(self) -> List[Dict[str, Any]]:
        """Gera próximos passos"""
        return [
            {
                "step": 1,
                "title": "Corrigir Testes Falhando",
                "command": "pytest -vv --tb=long --l",
                "description": "Execute testes com verbose output para identificar failures",
            },
            {
                "step": 2,
                "title": "Validar Fixtures",
                "command": "pytest --fixtures | grep -E 'test_|^[a-z]'",
                "description": "Liste todas as fixtures disponíveis e valide",
            },
            {
                "step": 3,
                "title": "Medir Cobertura",
                "command": "pytest --cov=src --cov-report=html",
                "description": "Gere relatório HTML de cobertura",
            },
            {
                "step": 4,
                "title": "Executar Lint",
                "command": "flake8 tests/ --max-line-length=88 && black --check tests/",
                "description": "Valide qualidade de código dos testes",
            },
            {
                "step": 5,
                "title": "Deploy Análise",
                "command": "python src/tools/analyze_test_suite.py > test_analysis_report.json",
                "description": "Salve relatório para histórico e CI/CD",
            },
        ]

    def export_report(self, report: Dict[str, Any], filename: str = "test_analysis_report.json"):
        """Exporta relatório para arquivo"""
        try:
            output_path = self.repo_path / filename

            with open(output_path, "w") as f:
                json.dump(report, f, indent=2, default=str)

            print(f"\n{GREEN}✅ Relatório salvo em: {output_path}{RESET}")

            # Also create markdown report
            self._create_markdown_report(report)

            return True

        except Exception as e:
            print(f"{RED}❌ Erro ao exportar: {e}{RESET}")
            return False

    def _create_markdown_report(self, report: Dict[str, Any]):
        """Cria relatório em Markdown"""
        try:
            md_content = """# 🧪 OmniMind Test Suite Analysis Report

**Data**: {report['timestamp']}

## 📊 Resumo Executivo

### Métricas Principais
- **Total de Testes**: {report['summary']['total_tests']}
- **Arquivos de Teste**: {report['summary']['total_files']}
- **Taxa de Sucesso**: {report['summary']['success_rate']}
- **Cobertura**: {report['summary']['coverage']}
- **Problemas Identificados**: {report['summary']['total_issues']}

### Resultado dos Testes
- ✅ Passed: {report['metrics']['passing']}
- ❌ Failed: {report['metrics']['failing']}
- ⏭️  Skipped: {report['metrics']['skipped']}
- ⚠️  XFailed: {report['metrics']['xfail']}
- 🔥 Errors: {report['metrics']['errors']}

## 🖥️ Ambiente

| Propriedade | Valor |
|---|---|
| OS | {report['environment'].get('os_version', 'Unknown')} |
| Python | {report['environment'].get('python_version', 'Unknown')} |
| Pytest | {report['environment'].get('pytest_version', 'Unknown')} |
| Docker | {'✅ Sim' if report['environment'].get('docker_enabled') else '❌ Não'} |
| GPU | {'✅ Sim' if report['environment'].get('gpu_enabled') else '❌ Não'} |
| Containers | {'✅ Sim' if report['environment'].get('container_enabled') else '❌ Não'} |
| Sudo | {'✅ Sim' if report['environment'].get('sudo_available') else '❌ Não'} |

## 🔴 Problemas Encontrados

"""

            for severity in ["critical", "high", "medium", "low"]:
                issues = report["issues_by_severity"].get(severity, [])
                if issues:
                    emoji = {"critical": "🔥", "high": "❌", "medium": "⚠️", "low": "ℹ️"}[severity]
                    md_content += f"\n### {emoji} {severity.upper()} ({len(issues)} problemas)\n\n"
                    for issue in issues[:5]:  # Top 5
                        md_content += f"- **{issue['type']}** ({issue['test_file']})\n"
                        md_content += f"  - Mensagem: {issue['message']}\n"
                        md_content += f"  - Sugestão: {issue['suggestion']}\n\n"

            md_content += "\n## 💡 Recomendações\n\n"
            for rec in report["recommendations"][:10]:
                priority_emoji = {"critical": "🔥", "high": "❌", "medium": "⚠️", "low": "ℹ️"}.get(
                    rec.get("priority", "low"), "ℹ️"
                )
                md_content += (
                    f"- **{rec.get('area')}** ({priority_emoji} "
                    f"{rec.get('priority', 'low')}): {rec.get('message')}\n"
                )
                md_content += f"  - Ação: {rec.get('action')}\n\n"

            md_content += "\n## 📋 Próximos Passos\n\n"
            for step in report["next_steps"]:
                md_content += f"### {step['step']}. {step['title']}\n"
                md_content += f"```bash\n{step['command']}\n```\n"
                md_content += f"{step['description']}\n\n"

            md_content += f"\n---\n*Relatório gerado automaticamente em {report['timestamp']}*\n"

            md_path = self.repo_path / "TEST_ANALYSIS_REPORT.md"
            md_path.write_text(md_content)

            print(f"{GREEN}✅ Relatório Markdown: {md_path}{RESET}")

        except Exception as e:
            print(f"{YELLOW}⚠️  Erro ao criar Markdown: {e}{RESET}")


def main():
    """Executa análise completa"""

    analyzer = OmniMindTestAnalyzer()
    report = analyzer.run_full_analysis()

    # Export reports
    analyzer.export_report(report, "test_analysis_report.json")

    print(f"\n{BOLD}{CYAN}{'='*80}{RESET}")
    print(f"{GREEN}🎉 ANÁLISE CONCLUÍDA COM SUCESSO{RESET}")
    print(f"{CYAN}{'='*80}{RESET}\n")

    print("📊 Arquivos gerados:")
    print("   - test_analysis_report.json")
    print("   - TEST_ANALYSIS_REPORT.md\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
