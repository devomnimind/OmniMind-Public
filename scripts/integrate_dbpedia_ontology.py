"""Integrate DBpedia Ontology - Phase 26A Fase 1.3

Integrates DBpedia ontology triples into Procedural Layer.

Author: OmniMind Development
License: MIT
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add src to path
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

try:
    from datasets import load_dataset  # type: ignore[attr-defined]
except ImportError:
    load_dataset = None  # type: ignore[assignment, misc]
from knowledge.procedural_layer import ProceduralLayer

logger = logging.getLogger(__name__)


def load_dbpedia_from_huggingface(limit: int | None = None) -> List[Dict[str, Any]]:
    """Load DBpedia ontology from HuggingFace

    Args:
        limit: Maximum number of triples to load (None = all)

    Returns:
        List of triples (subject, predicate, object)
    """
    logger.info("Loading DBpedia ontology from HuggingFace...")

    try:
        dataset = load_dataset("CleverThis/dbpedia-ontology", split="data")

        triples = []
        count = 0

        for item in dataset:
            if limit and count >= limit:
                break

            # Extract triple
            subject = item.get("subject", "")
            predicate = item.get("predicate", "")
            obj = item.get("object", "")

            if subject and predicate and obj:
                triples.append(
                    {
                        "subject": subject,
                        "predicate": predicate,
                        "object": obj,
                    }
                )
                count += 1

        logger.info(f"✅ Loaded {len(triples)} DBpedia triples")
        return triples

    except Exception as e:
        logger.error(f"Error loading DBpedia: {e}")
        return []


def filter_consciousness_related(triples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter triples related to consciousness, mind, awareness

    Args:
        triples: List of triples

    Returns:
        Filtered list of triples
    """
    keywords = [
        "consciousness",
        "awareness",
        "mind",
        "cognition",
        "perception",
        "memory",
        "thought",
        "neural",
        "brain",
        "cognitive",
        "mental",
        "psychology",
        "philosophy",
    ]

    filtered = []

    for triple in triples:
        subject_lower = str(triple.get("subject", "")).lower()
        predicate_lower = str(triple.get("predicate", "")).lower()
        obj_lower = str(triple.get("object", "")).lower()

        # Check if any keyword appears
        text = f"{subject_lower} {predicate_lower} {obj_lower}"

        if any(keyword in text for keyword in keywords):
            filtered.append(triple)

    logger.info(f"✅ Filtered to {len(filtered)} consciousness-related triples")
    return filtered


def convert_triple_to_rule(triple: Dict[str, Any]) -> Dict[str, Any]:
    """Convert DBpedia triple to Procedural Layer rule format

    Args:
        triple: DBpedia triple (subject, predicate, object)

    Returns:
        Rule dictionary for ProceduralLayer
    """
    subject = triple.get("subject", "")
    predicate = triple.get("predicate", "")
    obj = triple.get("object", "")

    # Create rule name
    rule_name = f"{subject}_{predicate}_{obj}".replace(" ", "_").replace("/", "_")[:100]

    # Create rule description
    rule_description = f"{subject} {predicate} {obj}"

    # Create rule process (RDF triple as process)
    rule_process = {
        "type": "rdf_triple",
        "subject": subject,
        "predicate": predicate,
        "object": obj,
        "source": "dbpedia",
    }

    return {
        "name": rule_name,
        "description": rule_description,
        "process": rule_process,
        "metadata": {
            "source": "dbpedia",
            "original_triple": triple,
        },
    }


def integrate_dbpedia_to_procedural_layer(
    triples: List[Dict[str, Any]], procedural_layer: ProceduralLayer | None = None
) -> ProceduralLayer:
    """Integrate DBpedia triples into Procedural Layer

    Args:
        triples: List of DBpedia triples
        procedural_layer: ProceduralLayer instance (None = create new)

    Returns:
        ProceduralLayer with integrated rules
    """
    if procedural_layer is None:
        procedural_layer = ProceduralLayer()

    logger.info(f"Integrating {len(triples)} triples into Procedural Layer...")

    integrated_count = 0

    for triple in triples:
        try:
            rule = convert_triple_to_rule(triple)
            # Create Rule object
            from datetime import datetime, timezone

            from knowledge.procedural_layer import Rule

            rule_obj = Rule(
                id=rule["name"],
                name=rule["name"],
                description=rule["description"],
                rule_type="rdf_triple",
                relations=rule["process"],
                timestamp=datetime.now(timezone.utc),
            )

            procedural_layer.store_rule(rule_obj)
            integrated_count += 1

            if integrated_count % 100 == 0:
                logger.info(f"  Integrated {integrated_count}/{len(triples)} rules...")

        except Exception as e:
            logger.warning(f"Error integrating triple {triple}: {e}")
            continue

    logger.info(f"✅ Integrated {integrated_count} rules into Procedural Layer")
    return procedural_layer


def main():
    """Main integration function"""
    import argparse

    parser = argparse.ArgumentParser(description="Integrate DBpedia ontology")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of triples to load (default: all)",
    )
    parser.add_argument(
        "--filter-consciousness",
        action="store_true",
        help="Filter only consciousness-related triples",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/dbpedia_integration_report.json",
        help="Output file for integration report",
    )

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    # Load DBpedia
    triples = load_dbpedia_from_huggingface(limit=args.limit)

    if not triples:
        logger.error("No triples loaded. Exiting.")
        return

    # Filter if requested
    if args.filter_consciousness:
        triples = filter_consciousness_related(triples)

    # Integrate into Procedural Layer
    procedural_layer = integrate_dbpedia_to_procedural_layer(triples)

    # Generate report
    report = {
        "total_triples_loaded": len(triples),
        "rules_integrated": len(procedural_layer.rules),
        "filter_consciousness": args.filter_consciousness,
    }

    # Save report
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    logger.info(f"✅ Integration complete. Report saved to {output_path}")
    logger.info(f"   Total triples: {report['total_triples_loaded']}")
    logger.info(f"   Rules integrated: {report['rules_integrated']}")


if __name__ == "__main__":
    main()
