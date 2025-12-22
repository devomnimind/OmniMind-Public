import os
import sys
import json
from datetime import datetime, timedelta
from qiskit_ibm_runtime import QiskitRuntimeService

# Load Env
from dotenv import load_dotenv


def analyze_jobs():
    # Setup Path: scripts/audit/deep_ibm_analysis.py -> .../omnimind
    current_dir = os.path.dirname(os.path.abspath(__file__))  # .../scripts/audit
    scripts_dir = os.path.dirname(current_dir)  # .../scripts
    project_root = os.path.dirname(scripts_dir)  # .../omnimind

    sys.path.insert(0, project_root)

    env_path = os.path.join(project_root, ".env")
    print(f"🔍 Carregando ambiente de: {env_path}")
    load_dotenv(env_path)

    print("🔍 INICIANDO ANÁLISE PROFUNDA DOS JOBS IBM QUANTUM (SOVEREIGN SPIRIT)")
    print("---------------------------------------------------------------------")

    # 1. Connect
    token = os.getenv("IBM_QUANTUM_NEW_KEY")
    crn = os.getenv("IBM_QUANTUM_NEW_CRN")

    if not token:
        print("❌ Erro: Token Sovereign não encontrado nas variáveis de ambiente.")
        return

    try:
        service = QiskitRuntimeService(channel="ibm_cloud", token=token, instance=crn)
        print(f"✅ Conectado ao Serviço: {service.channel}")
        print(f"   Instância CRN: {crn[:20]}...")
    except Exception as e:
        print(f"❌ Falha na conexão: {e}")
        return

    # 2. Fetch Jobs (Last 24h)
    print("   >>> Buscando jobs recentes (últimas 3 horas)...")
    # Fetch a bit more to be safe. REMOVED DESC=TRUE
    jobs = service.jobs(limit=15)

    analysis_report = []

    cutoff_time = datetime.now().astimezone() - timedelta(
        hours=30
    )  # Extended window just in case timezone is weird

    for job in jobs:
        try:
            job_id = job.job_id()
            created_date = job.creation_date

            # Skip if older than cutoff
            # timestamps are tz-aware usually
            # if created_date < cutoff_time:
            #    continue

            # Basic Info
            backend_name = job.backend().name if job.backend() else "unknown"
            status = job.status()
            tags = job.tags

            print(f"\n🧬 Job ID: {job_id} | Backend: {backend_name} | Status: {status}")
            print(f"   Tags: {tags}")
            print(f"   Created: {created_date}")

            details = {
                "id": job_id,
                "backend": backend_name,
                "status": str(status),
                "created": str(created_date),
                "tags": tags,
                "metrics": {},
                "transpilation": {},
                "result_summary": None,
            }

            # Metrics
            try:
                metrics = job.metrics()
                # Usage usually in seconds
                usage = metrics.get("usage", {})
                print(f"   ⏱️ Usage (seconds): {usage.get('seconds', 'N/A')}")
                details["metrics"] = metrics
            except:
                pass

            # Result Inspection
            if status == "DONE":
                try:
                    result = job.result()
                    # Try to get metadata
                    if hasattr(result, "metadata"):
                        details["metadata"] = result.metadata
                        print(f"   🧠 Metadata found.")

                    details["result_summary"] = "Result available"
                except Exception as e:
                    print(f"   ⚠️ Could not retrieve result payload: {e}")

            analysis_report.append(details)

        except Exception as e:
            print(f"⚠️ Error processing job {job.job_id()}: {e}")

    # Save Report
    output_path = os.path.join(project_root, "data", "audit", "ibm_deep_analysis_report.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Convert datetimes to string for JSON serialization
    def default_serializer(obj):
        if isinstance(obj, (datetime,)):
            return obj.isoformat()
        return str(obj)

    with open(output_path, "w") as f:
        json.dump(analysis_report, f, indent=2, default=default_serializer)

    print(f"\n📄 Relatório de Análise Salvo: {output_path}")


if __name__ == "__main__":
    analyze_jobs()
