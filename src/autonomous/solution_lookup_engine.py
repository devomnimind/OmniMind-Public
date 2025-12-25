"""Solution Lookup Engine - Phase 26C

Searches for solutions: local dataset → internet → papers.

Author: Fabrício da Silva + assistência de IA (Copilot GitHub/Cursor/Gemini/Perplexity)
License: MIT
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List


from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class SolutionLookupEngine:
    """Busca soluções conhecidas primeiro (local → internet → papers)"""

    def __init__(self, solutions_db_path: Path | None = None):
        """Initialize solution lookup engine

        Args:
            solutions_db_path: Path to known_solutions.json (default: data/known_solutions.json)
        """
        # Load local solutions database
        if solutions_db_path is None:
            base_dir = Path(__file__).resolve().parents[2]
            solutions_db_path = base_dir / "data" / "known_solutions.json"

        self.solutions_db_path = Path(solutions_db_path)
        self.local_solutions = self._load_local_solutions()

        # Initialize embedding model for semantic search
        # Migrated to Safe Loader (Topological Deglutition) to prevent Memory Overflow
        from src.embeddings.safe_transformer_loader import load_sentence_transformer_safe

        # This will now use the global cache if available
        self.embedder, _ = load_sentence_transformer_safe(model_name="all-MiniLM-L6-v2")

        logger.info(
            f"SolutionLookupEngine initialized: {len(self.local_solutions)} local solutions"
        )

    def _load_local_solutions(self) -> List[Dict[str, Any]]:
        """Load local solutions database

        Returns:
            List of solution dictionaries
        """
        if not self.solutions_db_path.exists():
            logger.warning(
                f"Solutions database not found at {self.solutions_db_path}. "
                "Run scripts/build_solutions_knowledge_base.py first."
            )
            return []

        try:
            with open(self.solutions_db_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("solutions", [])
        except Exception as e:
            logger.error(f"Error loading solutions database: {e}")
            return []

    def find_solution(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Find solution for issue (local → internet → papers)

        Args:
            issue: Issue dictionary (from ProblemDetectionEngine)

        Returns:
            Solution dict with source and confidence
        """
        issue_type = issue.get("type", "")

        logger.info("[PHASE 26C] Buscando solução para %s...", issue_type)

        # 1. Local dataset (mais rápido)
        local_solution = self.search_local(issue)

        if local_solution and local_solution.get("confidence", 0) > 0.8:
            confidence = local_solution["confidence"]
            logger.info(
                f"[PHASE 26C] Solução encontrada em dataset local "
                f"(confidence: {confidence:.2f})"
            )
            return {
                "source": "LOCAL_DATASET",
                "solution": local_solution,
                "confidence": local_solution["confidence"],
            }

        # 2. Internet (se problema não está documentado)
        logger.info("[PHASE 26C] Problema não está em dataset local. Buscando internet...")
        internet_solution = self.search_internet(issue)

        if internet_solution:
            confidence = internet_solution.get("confidence", 0.6)
            logger.info(
                f"[PHASE 26C] Solução encontrada na internet " f"(confidence: {confidence:.2f})"
            )
            return {
                "source": "INTERNET",
                "solution": internet_solution,
                "confidence": internet_solution.get("confidence", 0.6),
            }

        # 3. Papers (para problemas complexos)
        logger.info("[PHASE 26C] Buscando em papers científicos...")
        paper_solution = self.search_papers(issue)

        if paper_solution:
            logger.info("[PHASE 26C] Solução encontrada em papers (confidence: 0.5)")
            return {
                "source": "PAPERS",
                "solution": paper_solution,
                "confidence": 0.5,  # Menor confiança, precisa validação
            }

        # 4. Não encontrou → Manual (com sugestões)
        logger.warning("[PHASE 26C] Nenhuma solução encontrada. Requer intervenção manual.")
        return {
            "source": "MANUAL_REQUIRED",
            "suggestions": self.generate_suggestions(issue),
            "confidence": 0,
        }

    def search_local(self, issue: Dict[str, Any]) -> Dict[str, Any] | None:
        """Search in local solutions database

        Args:
            issue: Issue dictionary

        Returns:
            Solution dict or None
        """
        if not self.local_solutions:
            return None

        issue_type = issue.get("type", "")
        issue_description = issue.get("description", "")

        # Embed issue description
        issue_embedding = self.embedder.encode(issue_description)

        best_match = None
        best_similarity = 0.0

        for solution in self.local_solutions:
            problem_desc = solution.get("problem", {}).get("description", "")
            problem_type = solution.get("problem", {}).get("type", "")

            # Type match first
            if issue_type and problem_type and issue_type not in problem_type:
                continue

            # Semantic similarity
            if problem_desc:
                problem_embedding = self.embedder.encode(problem_desc)
                similarity = cosine_similarity([issue_embedding], [problem_embedding])[0][0]

                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = solution

        if best_match and best_similarity > 0.5:  # Threshold
            return {
                **best_match,
                "confidence": float(best_similarity),
                "similarity": float(best_similarity),
            }

        return None

    def search_internet(self, issue: Dict[str, Any]) -> Dict[str, Any] | None:
        """Search internet (StackOverflow, GitHub, etc)

        Args:
            issue: Issue dictionary

        Returns:
            Solution dict or None
        """
        from autonomous.internet_search import InternetSearch

        internet_search = InternetSearch()

        # Build query from issue
        query = f"{issue.get('type', '')} {issue.get('description', '')}"
        results = internet_search.search(query)

        if results["results"]:
            # Return best result
            best_result = results["results"][0]
            return {
                "solution": best_result.get("solution", ""),
                "confidence": best_result.get("confidence", 0.5),
                "source_url": best_result.get("url", ""),
            }

        return None

    def search_papers(self, issue: Dict[str, Any]) -> Dict[str, Any] | None:
        """Search in scientific papers via Phase 24

        Args:
            issue: Issue dictionary

        Returns:
            Solution dict or None
        """
        from autonomous.paper_search import PaperSearch

        paper_search = PaperSearch()

        # Build query from issue
        query = f"{issue.get('type', '')} {issue.get('description', '')}"
        papers = paper_search.search_papers(query, top_k=5)

        if papers:
            # Return best paper
            best_paper = papers[0]
            return {
                "solution": best_paper.get("solution", ""),
                "confidence": best_paper.get("confidence", 0.5),
                "paper_id": best_paper.get("paper_id", ""),
                "title": best_paper.get("title", ""),
            }

        return None

    def generate_suggestions(self, issue: Dict[str, Any]) -> List[str]:
        """Generate suggestions for manual intervention

        Args:
            issue: Issue dictionary

        Returns:
            List of suggestion strings
        """
        issue_type = issue.get("type", "")
        suggestions = []

        if issue_type == "MEMORY":
            suggestions.extend(
                [
                    "Reduzir batch_size",
                    "Desabilitar cache de embeddings",
                    "Usar modelo menor",
                    "Limpar memória não utilizada",
                ]
            )
        elif issue_type == "GPU_MEMORY":
            suggestions.extend(
                [
                    "Limpar cache de GPU (torch.cuda.empty_cache())",
                    "Reduzir batch_size",
                    "Usar mixed precision (FP16)",
                    "Liberar tensores não utilizados",
                ]
            )
        elif issue_type == "PERFORMANCE":
            suggestions.extend(
                [
                    "Otimizar código crítico",
                    "Usar GPU se disponível",
                    "Reduzir processamento desnecessário",
                    "Paralelizar operações",
                ]
            )
        elif issue_type == "SEMANTIC_DRIFT":
            suggestions.extend(
                [
                    "Re-treinar embeddings",
                    "Atualizar knowledge graph",
                    "Recalibrar semantic memory",
                ]
            )
        else:
            # Generic suggestions for unknown types
            suggestions.extend(
                [
                    "Verificar logs para mais detalhes",
                    "Consultar documentação",
                    "Revisar configurações do sistema",
                ]
            )

        return suggestions
