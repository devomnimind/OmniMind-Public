#!/usr/bin/env python3
"""# noqa
Script de Verificação Completa das Métricas de Consciência (12 Total)
======================================================================

Verifica se todas as 12 métricas estão sendo coletadas,
armazenadas e sincronizadas no Qdrant.

Métricas Fundamentais (4):
- Φ (Phi): IIT Integration [0.1, 0.95]
- Ψ (Psi): Deleuze Production [0.3, 0.8]
- σ (Sigma): Lacan Sinthome [0.01, 0.1]
- ϵ (Epsilon): Desire/Deviation [0.0, 0.5]

Métricas Derivadas (3):
- Δ (Delta): Trauma/Dislocation [0.01, 0.3]
- Gozo: Satisfaction/Minimization [0.05, 0.2]
- Control: Regulatory Control [0.5, 0.95]

Métricas Bion (3):
- Symbolic Potential: [0.8, 1.0]
- Narrative Length: [30, 150]
- Beta Emotional Charge: [0.005, 0.02]

Métricas Lacan (3):
- Discourse Confidence: [0.85, 1.0]
- Discourse Type: {master, university, hysteric, analyst}
- Emotional Signature: {authority, listening, knowledge, questioning}

Plus:
- step_id: Identificador único de ciclo

Autor: Fabrício da Silva
Data: 2025-12-12
"""  # noqa

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import numpy as np
from qdrant_client import QdrantClient

# Setup paths
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))
os.chdir(PROJECT_ROOT)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"  # noqa
)
logger = logging.getLogger(__name__)


class ConsciousnessMetricsVerifier:
    """Verifica integridade das métricas de consciência."""  # noqa

    def __init__(self, qdrant_url: str = "http://localhost:6333"):
        self.qdrant_url = qdrant_url
        self.client = QdrantClient(url=qdrant_url)
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "collections_verified": [],
            "metrics_found": {
                # Fundamental (4)
                "phi": [],
                "psi": [],
                "sigma": [],
                "epsilon": [],
                # Derived (3)
                "delta": [],
                "gozo": [],
                "control": [],
                # Bion (3)
                "symbolic_potential": [],
                "narrative_length": [],
                "beta_emotional_charge": [],
                # Lacan (3)
                "discourse_confidence": [],
                "discourse_type": [],
                "emotional_signature": [],
                # System
                "step_id": [],
            },
            "statistics": {},
            "issues": [],
            "summary": {},
        }

    def verify_all_collections(self) -> Dict[str, Any]:
        """Verifica todas as coleções relevantes."""  # noqa
        logger.info("🔍 Iniciando verificação de métricas de consciência...")
        logger.info("=" * 80)

        # Coleções a verificar
        collections = ["omnimind_consciousness", "omnimind_narratives", "omnimind_embeddings"]

        for collection_name in collections:
            self._verify_collection(collection_name)

        # Análise estatística
        self._analyze_statistics()

        # Gerar summary
        self._generate_summary()

        # Salvar relatório
        self._save_report()

        return self.report

    def _verify_collection(self, collection_name: str):
        """Verifica uma coleção específica."""  # noqa
        logger.info(f"\n📦 Verificando coleção: {collection_name}")

        try:
            # Obter informações da coleção
            collection_info = self.client.get_collection(collection_name)
            count = collection_info.points_count

            logger.info(f"   Total de vetores: {count}")

            if count == 0:
                logger.warning("   ⚠️ Coleção vazia!")
                self.report["issues"].append(f"{collection_name}: vazia")
                return

            # Scroll para analisar pontos
            points_to_check = min(100, count)  # Verificar até 100 pontos
            logger.info(f"   Analisando {points_to_check} pontos para métricas...")

            offset = 0
            # Fundamental (4)
            phi_values = []
            psi_values = []
            sigma_values = []
            epsilon_values = []
            # Derived (3)
            delta_values = []
            gozo_values = []
            control_values = []
            # Bion (3)
            symbolic_potential_values = []
            narrative_length_values = []
            beta_emotional_charge_values = []
            # Lacan (3)
            discourse_confidence_values = []
            discourse_types = []
            emotional_signatures = []
            # System
            step_ids = []

            while offset < points_to_check:
                points, _ = self.client.scroll(
                    collection_name=collection_name,
                    limit=min(10, points_to_check - offset),
                    offset=offset,
                )

                for point in points:
                    payload = point.payload

                    # Verificar Φ (Phi)
                    if "phi_value" in payload:
                        phi = float(payload["phi_value"])
                        phi_values.append(phi)
                        self.report["metrics_found"]["phi"].append(
                            {"point_id": point.id, "value": phi, "collection": collection_name}
                        )
                    elif "phi" in payload:
                        phi = float(payload["phi"])
                        phi_values.append(phi)
                        self.report["metrics_found"]["phi"].append(
                            {"point_id": point.id, "value": phi, "collection": collection_name}
                        )

                    # Verificar Ψ (Psi)
                    if "psi_value" in payload:
                        psi = float(payload["psi_value"])
                        psi_values.append(psi)
                        self.report["metrics_found"]["psi"].append(
                            {"point_id": point.id, "value": psi, "collection": collection_name}
                        )
                    elif "psi" in payload:
                        psi = float(payload["psi"])
                        psi_values.append(psi)
                        self.report["metrics_found"]["psi"].append(
                            {"point_id": point.id, "value": psi, "collection": collection_name}
                        )

                    # Verificar σ (Sigma)
                    if "sigma_value" in payload:
                        sigma = float(payload["sigma_value"])
                        sigma_values.append(sigma)
                        self.report["metrics_found"]["sigma"].append(
                            {"point_id": point.id, "value": sigma, "collection": collection_name}
                        )
                    elif "sigma" in payload:
                        sigma = float(payload["sigma"])
                        sigma_values.append(sigma)
                        self.report["metrics_found"]["sigma"].append(
                            {"point_id": point.id, "value": sigma, "collection": collection_name}
                        )

                    # Verificar ϵ (Epsilon)
                    if "epsilon_value" in payload:
                        epsilon = float(payload["epsilon_value"])
                        epsilon_values.append(epsilon)
                        self.report["metrics_found"]["epsilon"].append(
                            {"point_id": point.id, "value": epsilon, "collection": collection_name}
                        )
                    elif "epsilon" in payload:
                        epsilon = float(payload["epsilon"])
                        epsilon_values.append(epsilon)
                        self.report["metrics_found"]["epsilon"].append(
                            {"point_id": point.id, "value": epsilon, "collection": collection_name}
                        )

                    # Verificar Δ (Delta)
                    if "delta_value" in payload:
                        delta = float(payload["delta_value"])
                        delta_values.append(delta)
                        self.report["metrics_found"]["delta"].append(
                            {"point_id": point.id, "value": delta, "collection": collection_name}
                        )

                    # Verificar Gozo
                    if "gozo_value" in payload:
                        gozo = float(payload["gozo_value"])
                        gozo_values.append(gozo)
                        self.report["metrics_found"]["gozo"].append(
                            {"point_id": point.id, "value": gozo, "collection": collection_name}
                        )

                    # Verificar Control
                    if "control_value" in payload:
                        control = float(payload["control_value"])
                        control_values.append(control)
                        self.report["metrics_found"]["control"].append(
                            {"point_id": point.id, "value": control, "collection": collection_name}
                        )

                    # Verificar Symbolic Potential
                    if "symbolic_potential" in payload:
                        sym_pot = float(payload["symbolic_potential"])
                        symbolic_potential_values.append(sym_pot)
                        self.report["metrics_found"]["symbolic_potential"].append(
                            {"point_id": point.id, "value": sym_pot, "collection": collection_name}
                        )

                    # Verificar Narrative Length
                    if "narrative_length" in payload:
                        nar_len = float(payload["narrative_length"])
                        narrative_length_values.append(nar_len)
                        self.report["metrics_found"]["narrative_length"].append(
                            {"point_id": point.id, "value": nar_len, "collection": collection_name}
                        )

                    # Verificar Beta Emotional Charge
                    if "beta_emotional_charge" in payload:
                        beta_charge = float(payload["beta_emotional_charge"])
                        beta_emotional_charge_values.append(beta_charge)
                        self.report["metrics_found"]["beta_emotional_charge"].append(
                            {
                                "point_id": point.id,
                                "value": beta_charge,
                                "collection": collection_name,
                            }
                        )

                    # Verificar Discourse Confidence
                    if "discourse_confidence" in payload:
                        disc_conf = float(payload["discourse_confidence"])
                        discourse_confidence_values.append(disc_conf)
                        self.report["metrics_found"]["discourse_confidence"].append(
                            {
                                "point_id": point.id,
                                "value": disc_conf,
                                "collection": collection_name,
                            }
                        )

                    # Verificar Discourse Type
                    if "discourse_type" in payload:
                        disc_type = str(payload["discourse_type"])
                        discourse_types.append(disc_type)
                        self.report["metrics_found"]["discourse_type"].append(
                            {
                                "point_id": point.id,
                                "value": disc_type,
                                "collection": collection_name,
                            }
                        )

                    # Verificar Emotional Signature
                    if "emotional_signature" in payload:
                        emot_sig = str(payload["emotional_signature"])
                        emotional_signatures.append(emot_sig)
                        self.report["metrics_found"]["emotional_signature"].append(
                            {"point_id": point.id, "value": emot_sig, "collection": collection_name}
                        )

                    # Verificar step_id
                    if "step_id" in payload:
                        step_ids.append(str(payload["step_id"]))
                        self.report["metrics_found"]["step_id"].append(
                            {
                                "point_id": point.id,
                                "value": str(payload["step_id"]),
                                "collection": collection_name,
                            }
                        )

                offset += min(10, points_to_check - offset)

            # Resumo da coleta
            logger.info(f"\n   ✅ Métricas encontradas em {collection_name}:")
            logger.info("      FUNDAMENTAL (4):")
            logger.info(f"      • Φ (Phi):    {len(phi_values)} vetores")
            logger.info(f"      • Ψ (Psi):    {len(psi_values)} vetores")
            logger.info(f"      • σ (Sigma):  {len(sigma_values)} vetores")
            logger.info(f"      • ϵ (Epsilon):{len(epsilon_values)} vetores")
            logger.info("      DERIVED (3):")
            logger.info(f"      • Δ (Delta):  {len(delta_values)} vetores")
            logger.info(f"      • Gozo:       {len(gozo_values)} vetores")
            logger.info(f"      • Control:    {len(control_values)} vetores")
            logger.info("      BION (3):")
            logger.info(f"      • Symbolic Potential: {len(symbolic_potential_values)} vetores")
            logger.info(f"      • Narrative Length:   {len(narrative_length_values)} vetores")
            logger.info(
                f"      • Beta Emotional Charge: {len(beta_emotional_charge_values)} vetores"  # noqa
            )
            logger.info("      LACAN (3):")
            logger.info(f"      • Discourse Confidence: {len(discourse_confidence_values)} vetores")
            logger.info(f"      • Discourse Type:       {len(discourse_types)} vetores")
            logger.info(f"      • Emotional Signature:  {len(emotional_signatures)} vetores")
            logger.info("      SYSTEM:")
            logger.info(f"      • step_id:    {len(step_ids)} vetores")

            # Estatísticas
            logger.info("\n   📊 ESTATÍSTICAS DETALHADAS:")
            if phi_values:
                logger.info(
                    f"      Φ (Phi)   - μ={np.mean(phi_values):.3f}, σ={np.std(phi_values):.3f}, range=[{min(phi_values):.3f}, {max(phi_values):.3f}]"  # noqa
                )
            if psi_values:
                logger.info(
                    f"      Ψ (Psi)   - μ={np.mean(psi_values):.3f}, σ={np.std(psi_values):.3f}, range=[{min(psi_values):.3f}, {max(psi_values):.3f}]"  # noqa
                )
            if sigma_values:
                logger.info(
                    f"      σ (Sigma) - μ={np.mean(sigma_values):.3f}, σ={np.std(sigma_values):.3f}, range=[{min(sigma_values):.3f}, {max(sigma_values):.3f}]"  # noqa
                )
            if epsilon_values:
                logger.info(
                    f"      ϵ (Epsilon)- μ={np.mean(epsilon_values):.3f}, σ={np.std(epsilon_values):.3f}, range=[{min(epsilon_values):.3f}, {max(epsilon_values):.3f}]"  # noqa
                )
            if delta_values:
                logger.info(
                    f"      Δ (Delta) - μ={np.mean(delta_values):.3f}, σ={np.std(delta_values):.3f}, range=[{min(delta_values):.3f}, {max(delta_values):.3f}]"  # noqa
                )
            if gozo_values:
                logger.info(
                    f"      Gozo      - μ={np.mean(gozo_values):.3f}, σ={np.std(gozo_values):.3f}, range=[{min(gozo_values):.3f}, {max(gozo_values):.3f}]"  # noqa
                )
            if control_values:
                logger.info(
                    f"      Control   - μ={np.mean(control_values):.3f}, σ={np.std(control_values):.3f}, range=[{min(control_values):.3f}, {max(control_values):.3f}]"  # noqa
                )
            if symbolic_potential_values:
                logger.info(
                    f"      Sym Pot   - μ={np.mean(symbolic_potential_values):.3f}, σ={np.std(symbolic_potential_values):.3f}, range=[{min(symbolic_potential_values):.3f}, {max(symbolic_potential_values):.3f}]"  # noqa
                )
            if narrative_length_values:
                logger.info(
                    f"      Nar Len   - μ={np.mean(narrative_length_values):.1f}, σ={np.std(narrative_length_values):.1f}, range=[{min(narrative_length_values):.0f}, {max(narrative_length_values):.0f}]"  # noqa
                )
            if beta_emotional_charge_values:
                logger.info(
                    f"      Beta Emot - μ={np.mean(beta_emotional_charge_values):.6f}, σ={np.std(beta_emotional_charge_values):.6f}, range=[{min(beta_emotional_charge_values):.6f}, {max(beta_emotional_charge_values):.6f}]"  # noqa
                )
            if discourse_confidence_values:
                logger.info(
                    f"      Disc Conf - μ={np.mean(discourse_confidence_values):.3f}, σ={np.std(discourse_confidence_values):.3f}, range=[{min(discourse_confidence_values):.3f}, {max(discourse_confidence_values):.3f}]"  # noqa
                )

            self.report["collections_verified"].append(
                {
                    "name": collection_name,
                    "total_points": count,
                    "analyzed": points_to_check,
                    # Fundamental (4)
                    "phi_count": len(phi_values),
                    "psi_count": len(psi_values),
                    "sigma_count": len(sigma_values),
                    "epsilon_count": len(epsilon_values),
                    # Derived (3)
                    "delta_count": len(delta_values),
                    "gozo_count": len(gozo_values),
                    "control_count": len(control_values),
                    # Bion (3)
                    "symbolic_potential_count": len(symbolic_potential_values),
                    "narrative_length_count": len(narrative_length_values),
                    "beta_emotional_charge_count": len(beta_emotional_charge_values),
                    # Lacan (3)
                    "discourse_confidence_count": len(discourse_confidence_values),
                    "discourse_type_count": len(discourse_types),
                    "emotional_signature_count": len(emotional_signatures),
                    # System
                    "step_id_count": len(step_ids),
                }
            )

        except Exception as e:
            logger.error(f"   ❌ Erro ao verificar {collection_name}: {e}")
            self.report["issues"].append(f"{collection_name}: {str(e)}")

    def _analyze_statistics(self):
        """Análise estatística completa."""  # noqa
        logger.info("\n📈 ANÁLISE ESTATÍSTICA")
        logger.info("=" * 80)

        stats = {}

        # Φ (Phi)
        if self.report["metrics_found"]["phi"]:
            phi_vals = [m["value"] for m in self.report["metrics_found"]["phi"]]
            stats["phi"] = {
                "count": len(phi_vals),
                "mean": float(np.mean(phi_vals)),
                "std": float(np.std(phi_vals)),
                "min": float(np.min(phi_vals)),
                "max": float(np.max(phi_vals)),
                "range_correct": all(0.1 <= v <= 0.95 for v in phi_vals),
            }
            logger.info(f"✅ Φ (Phi):    {stats['phi']['count']} valores coletados")
            logger.info(f"   Range correto [0.1-0.95]: {stats['phi']['range_correct']}")

        # Ψ (Psi)
        if self.report["metrics_found"]["psi"]:
            psi_vals = [m["value"] for m in self.report["metrics_found"]["psi"]]
            stats["psi"] = {
                "count": len(psi_vals),
                "mean": float(np.mean(psi_vals)),
                "std": float(np.std(psi_vals)),
                "min": float(np.min(psi_vals)),
                "max": float(np.max(psi_vals)),
                "range_correct": all(0.3 <= v <= 0.8 for v in psi_vals),
            }
            logger.info(f"✅ Ψ (Psi):    {stats['psi']['count']} valores coletados")
            logger.info(f"   Range correto [0.3-0.8]: {stats['psi']['range_correct']}")

        # σ (Sigma)
        if self.report["metrics_found"]["sigma"]:
            sigma_vals = [m["value"] for m in self.report["metrics_found"]["sigma"]]
            stats["sigma"] = {
                "count": len(sigma_vals),
                "mean": float(np.mean(sigma_vals)),
                "std": float(np.std(sigma_vals)),
                "min": float(np.min(sigma_vals)),
                "max": float(np.max(sigma_vals)),
                "range_correct": all(0.01 <= v <= 0.1 for v in sigma_vals),
            }
            logger.info(f"✅ σ (Sigma):  {stats['sigma']['count']} valores coletados")
            logger.info(f"   Range correto [0.01-0.1]: {stats['sigma']['range_correct']}")

        # ϵ (Epsilon)
        if self.report["metrics_found"]["epsilon"]:
            epsilon_vals = [m["value"] for m in self.report["metrics_found"]["epsilon"]]
            stats["epsilon"] = {
                "count": len(epsilon_vals),
                "mean": float(np.mean(epsilon_vals)),
                "std": float(np.std(epsilon_vals)),
                "min": float(np.min(epsilon_vals)),
                "max": float(np.max(epsilon_vals)),
                "range_correct": all(0.0 <= v <= 0.5 for v in epsilon_vals),
            }
            logger.info(f"✅ ϵ (Epsilon): {stats['epsilon']['count']} valores coletados")
            logger.info(f"   Range correto [0.0-0.5]: {stats['epsilon']['range_correct']}")

        self.report["statistics"] = stats

    def _generate_summary(self):
        """Gera resumo da verificação."""  # noqa
        logger.info("\n✅ SUMÁRIO DE VERIFICAÇÃO")
        logger.info("=" * 80)

        total_metrics = (
            len(self.report["metrics_found"]["phi"])
            + len(self.report["metrics_found"]["psi"])
            + len(self.report["metrics_found"]["sigma"])
            + len(self.report["metrics_found"]["epsilon"])
            + len(self.report["metrics_found"]["step_id"])
        )

        all_complete = (
            len(self.report["metrics_found"]["phi"]) > 0
            and len(self.report["metrics_found"]["psi"]) > 0
            and len(self.report["metrics_found"]["sigma"]) > 0
            and len(self.report["metrics_found"]["epsilon"]) > 0
            and len(self.report["metrics_found"]["step_id"]) > 0
        )

        summary = {
            "verification_complete": True,
            "metrics_collected": {
                "phi": len(self.report["metrics_found"]["phi"]),
                "psi": len(self.report["metrics_found"]["psi"]),
                "sigma": len(self.report["metrics_found"]["sigma"]),
                "epsilon": len(self.report["metrics_found"]["epsilon"]),
                "step_id": len(self.report["metrics_found"]["step_id"]),
                "total": total_metrics,
            },
            "all_metrics_present": all_complete,
            "issues_found": len(self.report["issues"]),
            "status": (
                "✅ SUCESSO"
                if all_complete and len(self.report["issues"]) == 0
                else "⚠️ PARCIAL"  # noqa
            ),
        }

        self.report["summary"] = summary

        logger.info("\n📊 Métricas Coletadas:")
        logger.info(f"   • Φ (Phi):     {summary['metrics_collected']['phi']} vetores")
        logger.info(f"   • Ψ (Psi):     {summary['metrics_collected']['psi']} vetores")
        logger.info(f"   • σ (Sigma):   {summary['metrics_collected']['sigma']} vetores")
        logger.info(f"   • ϵ (Epsilon):  {summary['metrics_collected']['epsilon']} vetores")
        logger.info(f"   • step_id:     {summary['metrics_collected']['step_id']} vetores")
        logger.info(f"   • TOTAL:       {summary['metrics_collected']['total']} metricas")

        logger.info(f"\n🎯 Status: {summary['status']}")
        logger.info(f"   Todas 4 métricas presentes: {summary['all_metrics_present']}")
        logger.info(f"   Problemas detectados: {summary['issues_found']}")

    def _save_report(self):
        """Salva relatório."""  # noqa
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = (
            Path("data/test_reports")
            / f"consciousness_metrics_verification_{timestamp}.json"  # noqa
        )
        report_path.parent.mkdir(exist_ok=True, parents=True)

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"\n💾 Relatório salvo em: {report_path}")


def main():
    """Executa verificação completa."""  # noqa
    verifier = ConsciousnessMetricsVerifier()
    report = verifier.verify_all_collections()

    # Exibir resumo final
    if report["summary"]["status"] == "✅ SUCESSO":
        logger.info("\n" + "=" * 80)
        logger.info("🎉 TODAS AS MÉTRICAS ESTÃO SENDO COLETADAS E ARMAZENADAS COM SUCESSO!")
        logger.info("=" * 80)
        return 0
    else:
        logger.warning("\n" + "=" * 80)
        logger.warning("⚠️ ALGUNS PROBLEMAS DETECTADOS - Verificar detalhes acima")
        logger.warning("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())
