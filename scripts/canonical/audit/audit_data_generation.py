#!/usr/bin/env python3
"""
Auditoria de Geração e Persistência de Dados - OmniMind

Verifica se todos os módulos que deveriam gerar dados estão:
1. Gerando dados corretamente
2. Persistindo em locais esperados
3. Mantendo consistência com o que foi programado
4. Identificando anomalias

Autor: Fabrício da Silva + assistência de IA
Data: 2025-01-XX
"""

import json
import logging
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class DataGenerationAuditor:
    """Auditor de geração e persistência de dados."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data"
        self.logs_dir = project_root / "logs"
        self.issues: List[Dict[str, Any]] = []
        self.findings: Dict[str, Any] = defaultdict(dict)

    def audit_consciousness_metrics(self) -> Dict[str, Any]:
        """Audita geração de métricas de consciência (Φ, Ψ, σ)."""
        findings = {
            "module": "consciousness_metrics",
            "expected_files": [],
            "actual_files": [],
            "status": "unknown",
            "issues": [],
        }

        # Diretório esperado
        metrics_dir = self.data_dir / "monitor" / "consciousness_metrics"
        expected_files = [
            "phi_history.jsonl",
            "psi_history.jsonl",
            "sigma_history.jsonl",
        ]

        findings["expected_files"] = [str(metrics_dir / f) for f in expected_files]

        # Verificar se diretório existe
        if not metrics_dir.exists():
            findings["status"] = "missing_directory"
            findings["issues"].append(f"Diretório não existe: {metrics_dir}")
            return findings

        # Verificar arquivos
        for filename in expected_files:
            filepath = metrics_dir / filename
            if filepath.exists():
                findings["actual_files"].append(str(filepath))
                # Verificar se tem conteúdo
                try:
                    with open(filepath, "r") as f:
                        lines = f.readlines()
                        if lines:
                            # Verificar última linha
                            last_line = lines[-1].strip()
                            if last_line:
                                try:
                                    data = json.loads(last_line)
                                    findings[f"{filename}_last_entry"] = data
                                    findings[f"{filename}_count"] = len(lines)
                                except json.JSONDecodeError:
                                    findings["issues"].append(f"JSON inválido em {filename}")
                        else:
                            findings["issues"].append(f"{filename} está vazio")
                except Exception as e:
                    findings["issues"].append(f"Erro ao ler {filename}: {e}")
            else:
                findings["issues"].append(f"Arquivo não encontrado: {filename}")

        if len(findings["actual_files"]) == len(expected_files) and not findings["issues"]:
            findings["status"] = "ok"
        elif findings["actual_files"]:
            findings["status"] = "partial"
        else:
            findings["status"] = "missing"

        return findings

    def audit_consciousness_snapshots(self) -> Dict[str, Any]:
        """Audita snapshots de consciência."""
        findings = {
            "module": "consciousness_snapshots",
            "expected_files": [],
            "actual_files": [],
            "status": "unknown",
            "issues": [],
        }

        # Arquivo JSONL local
        snapshot_file = self.data_dir / "consciousness" / "snapshots.jsonl"
        findings["expected_files"].append(str(snapshot_file))

        if snapshot_file.exists():
            findings["actual_files"].append(str(snapshot_file))
            try:
                with open(snapshot_file, "r") as f:
                    lines = f.readlines()
                    if lines:
                        findings["snapshot_count"] = len(lines)
                        # Verificar última entrada
                        last_line = lines[-1].strip()
                        if last_line:
                            data = json.loads(last_line)
                            findings["last_snapshot"] = {
                                "snapshot_id": data.get("snapshot_id", "unknown"),
                                "timestamp": data.get("timestamp", "unknown"),
                                "phi_value": data.get("phi_value", 0.0),
                                "psi_value": data.get("psi_value", 0.0),
                                "sigma_value": data.get("sigma_value", 0.0),
                            }
                            findings["status"] = "ok"
                    else:
                        findings["issues"].append("Arquivo de snapshots vazio")
                        findings["status"] = "empty"
            except Exception as e:
                findings["issues"].append(f"Erro ao ler snapshots: {e}")
                findings["status"] = "error"
        else:
            findings["issues"].append("Arquivo de snapshots não encontrado")
            findings["status"] = "missing"

        return findings

    def audit_autopoietic_data(self) -> Dict[str, Any]:
        """Audita dados autopoiéticos."""
        findings = {
            "module": "autopoietic",
            "expected_files": [],
            "actual_files": [],
            "status": "unknown",
            "issues": [],
        }

        autopoietic_dir = self.data_dir / "autopoietic"
        expected_files = [
            "cycle_history.jsonl",
            "art_gallery.json",
            "narrative_history.json",
        ]

        findings["expected_files"] = [str(autopoietic_dir / f) for f in expected_files]

        if not autopoietic_dir.exists():
            findings["status"] = "missing_directory"
            findings["issues"].append(f"Diretório não existe: {autopoietic_dir}")
            return findings

        for filename in expected_files:
            filepath = autopoietic_dir / filename
            if filepath.exists():
                findings["actual_files"].append(str(filepath))
                try:
                    if filename.endswith(".jsonl"):
                        with open(filepath, "r") as f:
                            lines = f.readlines()
                            findings[f"{filename}_count"] = len(lines)
                    else:
                        with open(filepath, "r") as f:
                            data = json.load(f)
                            if isinstance(data, list):
                                findings[f"{filename}_count"] = len(data)
                            else:
                                findings[f"{filename}_keys"] = list(data.keys())
                except Exception as e:
                    findings["issues"].append(f"Erro ao ler {filename}: {e}")
            else:
                findings["issues"].append(f"Arquivo não encontrado: {filename}")

        if len(findings["actual_files"]) == len(expected_files):
            findings["status"] = "ok"
        elif findings["actual_files"]:
            findings["status"] = "partial"
        else:
            findings["status"] = "missing"

        return findings

    def audit_memory_data(self) -> Dict[str, Any]:
        """Audita dados de memória."""
        findings = {
            "module": "memory",
            "expected_storage": [],
            "actual_storage": [],
            "status": "unknown",
            "issues": [],
        }

        # Verificar Qdrant
        qdrant_dir = self.data_dir / "qdrant"
        if qdrant_dir.exists():
            findings["actual_storage"].append("qdrant_local")
            collections_dir = qdrant_dir / "collections"
            if collections_dir.exists():
                collections = list(collections_dir.iterdir())
                findings["qdrant_collections"] = [c.name for c in collections if c.is_dir()]

        # Verificar Supabase (via logs ou configuração)
        # Não podemos verificar diretamente, mas podemos verificar se há tentativas de conexão

        # Verificar arquivos de memória local
        memory_files = [
            self.data_dir / "sessions" / "*.json",
            self.data_dir / "known_solutions.json",
        ]

        for pattern in memory_files:
            if isinstance(pattern, Path):
                if pattern.exists():
                    findings["actual_storage"].append(str(pattern))

        if findings["actual_storage"]:
            findings["status"] = "ok"
        else:
            findings["status"] = "missing"
            findings["issues"].append("Nenhum armazenamento de memória encontrado")

        return findings

    def audit_agent_data(self) -> Dict[str, Any]:
        """Audita dados gerados por agentes."""
        findings = {
            "module": "agents",
            "expected_logs": [],
            "actual_logs": [],
            "status": "unknown",
            "issues": [],
        }

        # Verificar logs de agentes
        agent_logs = [
            self.logs_dir / "main_cycle.log",
            self.logs_dir / "backend_8000.log",
        ]

        for log_file in agent_logs:
            if log_file.exists():
                findings["actual_logs"].append(str(log_file))
                try:
                    # Verificar se tem conteúdo recente (últimas 24h)
                    mtime = log_file.stat().st_mtime
                    age_hours = (time.time() - mtime) / 3600
                    findings[f"{log_file.name}_age_hours"] = age_hours
                    if age_hours > 24:
                        findings["issues"].append(
                            f"{log_file.name} não foi atualizado nas últimas 24h"
                        )
                except Exception as e:
                    findings["issues"].append(f"Erro ao verificar {log_file.name}: {e}")

        if findings["actual_logs"]:
            findings["status"] = "ok"
        else:
            findings["status"] = "missing"

        return findings

    def audit_module_logs(self) -> Dict[str, Any]:
        """Audita logs de módulos."""
        findings = {
            "module": "module_logs",
            "expected_logs": [],
            "actual_logs": [],
            "status": "unknown",
            "issues": [],
        }

        module_logs_dir = self.logs_dir / "modules"
        if module_logs_dir.exists():
            log_files = list(module_logs_dir.glob("*.jsonl"))
            findings["actual_logs"] = [str(f) for f in log_files]

            for log_file in log_files:
                try:
                    with open(log_file, "r") as f:
                        lines = f.readlines()
                        findings[f"{log_file.name}_count"] = len(lines)
                except Exception as e:
                    findings["issues"].append(f"Erro ao ler {log_file.name}: {e}")

        if findings["actual_logs"]:
            findings["status"] = "ok"
        else:
            findings["status"] = "missing"
            findings["issues"].append("Nenhum log de módulo encontrado")

        return findings

    def run_full_audit(self) -> Dict[str, Any]:
        """Executa auditoria completa."""
        logger.info("🔍 Iniciando auditoria de geração e persistência de dados...")

        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "project_root": str(self.project_root),
            "audits": {},
            "summary": {},
        }

        # Executar todas as auditorias
        results["audits"]["consciousness_metrics"] = self.audit_consciousness_metrics()
        results["audits"]["consciousness_snapshots"] = self.audit_consciousness_snapshots()
        results["audits"]["autopoietic_data"] = self.audit_autopoietic_data()
        results["audits"]["memory_data"] = self.audit_memory_data()
        results["audits"]["agent_data"] = self.audit_agent_data()
        results["audits"]["module_logs"] = self.audit_module_logs()

        # Resumo
        total_audits = len(results["audits"])
        ok_count = sum(1 for a in results["audits"].values() if a.get("status") == "ok")
        partial_count = sum(1 for a in results["audits"].values() if a.get("status") == "partial")
        missing_count = sum(1 for a in results["audits"].values() if a.get("status") == "missing")

        results["summary"] = {
            "total_modules": total_audits,
            "ok": ok_count,
            "partial": partial_count,
            "missing": missing_count,
            "issues_found": sum(len(a.get("issues", [])) for a in results["audits"].values()),
        }

        return results

    def generate_report(self, results: Dict[str, Any]) -> str:
        """Gera relatório em markdown."""
        report = []
        report.append("# 📊 Relatório de Auditoria - Geração e Persistência de Dados")
        report.append("")
        report.append(f"**Data**: {results['timestamp']}")
        report.append(f"**Projeto**: {results['project_root']}")
        report.append("")

        # Resumo
        summary = results["summary"]
        report.append("## 📋 Resumo Executivo")
        report.append("")
        report.append(f"- **Total de Módulos Auditados**: {summary['total_modules']}")
        report.append(f"- **✅ OK**: {summary['ok']}")
        report.append(f"- **🟡 Parcial**: {summary['partial']}")
        report.append(f"- ❌ **Ausente**: {summary['missing']}")
        report.append(f"- **⚠️ Problemas Encontrados**: {summary['issues_found']}")
        report.append("")

        # Detalhes por módulo
        report.append("## 🔍 Detalhes por Módulo")
        report.append("")

        for module_name, audit in results["audits"].items():
            status_emoji = {
                "ok": "✅",
                "partial": "🟡",
                "missing": "❌",
                "error": "⚠️",
                "empty": "📭",
            }.get(audit.get("status", "unknown"), "❓")

            report.append(f"### {status_emoji} {module_name.replace('_', ' ').title()}")
            report.append("")
            report.append(f"**Status**: {audit.get('status', 'unknown')}")
            report.append("")

            if audit.get("issues"):
                report.append("**Problemas Encontrados**:")
                for issue in audit["issues"]:
                    report.append(f"- ⚠️ {issue}")
                report.append("")

            if audit.get("actual_files"):
                report.append("**Arquivos Encontrados**:")
                for file in audit["actual_files"]:
                    report.append(f"- ✅ {file}")
                report.append("")

            if audit.get("expected_files") and audit.get("status") != "ok":
                missing = set(audit["expected_files"]) - set(audit.get("actual_files", []))
                if missing:
                    report.append("**Arquivos Ausentes**:")
                    for file in missing:
                        report.append(f"- ❌ {file}")
                    report.append("")

        return "\n".join(report)


def main():
    """Função principal."""
    auditor = DataGenerationAuditor(PROJECT_ROOT)
    results = auditor.run_full_audit()

    # Salvar resultados
    report_file = PROJECT_ROOT / "data" / "reports" / "data_generation_audit.json"
    # Corrigir caminho do relatório markdown
    markdown_file = PROJECT_ROOT / "data" / "reports" / "data_generation_audit.md"
    report_file.parent.mkdir(parents=True, exist_ok=True)

    with open(report_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    # Gerar relatório markdown
    markdown_report = auditor.generate_report(results)
    markdown_file = PROJECT_ROOT / "data" / "reports" / "data_generation_audit.md"
    with open(markdown_file, "w") as f:
        f.write(markdown_report)

    # Exibir resumo
    print("\n" + "=" * 60)
    print("📊 RESUMO DA AUDITORIA")
    print("=" * 60)
    summary = results["summary"]
    print(f"✅ OK: {summary['ok']}/{summary['total_modules']}")
    print(f"🟡 Parcial: {summary['partial']}/{summary['total_modules']}")
    print(f"❌ Ausente: {summary['missing']}/{summary['total_modules']}")
    print(f"⚠️ Problemas: {summary['issues_found']}")
    print("")
    print(f"📄 Relatório completo: {markdown_file}")
    print("=" * 60)

    # Retornar código de saída baseado em problemas
    if summary["issues_found"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
