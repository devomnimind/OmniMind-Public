"""Tests for Solution Lookup Engine - Phase 26C"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import pytest

from autonomous.solution_lookup_engine import SolutionLookupEngine


class TestSolutionLookupEngine:
    """Test Solution Lookup Engine"""

    def test_init_without_db(self):
        """Test initialization without solutions DB"""
        # Use non-existent path
        engine = SolutionLookupEngine(solutions_db_path=Path("/tmp/nonexistent.json"))
        assert engine is not None
        assert len(engine.local_solutions) == 0

    def test_init_with_db(self):
        """Test initialization with solutions DB"""
        # Create temp solutions DB
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            solutions_db = {
                "version": "1.0",
                "total_solutions": 2,
                "sources": ["test"],
                "solutions": [
                    {
                        "id": "test_1",
                        "source": "test",
                        "problem": {
                            "description": "memory usage high",
                            "type": "MEMORY",
                        },
                        "solution": {
                            "description": "reduce batch size",
                            "confidence": 0.9,
                        },
                    },
                    {
                        "id": "test_2",
                        "source": "test",
                        "problem": {
                            "description": "cpu usage high",
                            "type": "PERFORMANCE",
                        },
                        "solution": {
                            "description": "enable GPU",
                            "confidence": 0.8,
                        },
                    },
                ],
            }
            json.dump(solutions_db, f)
            db_path = Path(f.name)

        try:
            engine = SolutionLookupEngine(solutions_db_path=db_path)
            assert len(engine.local_solutions) == 2
        finally:
            db_path.unlink()

    def test_search_local_found(self):
        """Test local search finds solution"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            solutions_db = {
                "version": "1.0",
                "total_solutions": 1,
                "sources": ["test"],
                "solutions": [
                    {
                        "id": "test_1",
                        "source": "test",
                        "problem": {
                            "description": "memory usage high 95 percent",
                            "type": "MEMORY",
                        },
                        "solution": {
                            "description": "reduce batch size to 4",
                            "confidence": 0.9,
                        },
                    },
                ],
            }
            json.dump(solutions_db, f)
            db_path = Path(f.name)

        try:
            engine = SolutionLookupEngine(solutions_db_path=db_path)

            issue = {
                "type": "MEMORY",
                "description": "memory usage high",
            }

            solution = engine.search_local(issue)

            assert solution is not None
            assert solution["confidence"] > 0.5
        finally:
            db_path.unlink()

    @pytest.mark.skipif(
        os.getenv("OMNIMIND_FORCE_GPU") == "true",
        reason="CUDA OOM - skipping GPU tests in fast suite",
    )
    def test_search_local_not_found(self):
        """Test local search doesn't find unrelated solution"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            solutions_db = {
                "version": "1.0",
                "total_solutions": 1,
                "sources": ["test"],
                "solutions": [
                    {
                        "id": "test_1",
                        "source": "test",
                        "problem": {
                            "description": "cpu usage high",
                            "type": "PERFORMANCE",
                        },
                        "solution": {
                            "description": "enable GPU",
                            "confidence": 0.9,
                        },
                    },
                ],
            }
            json.dump(solutions_db, f)
            db_path = Path(f.name)

        try:
            engine = SolutionLookupEngine(solutions_db_path=db_path)

            issue = {
                "type": "MEMORY",
                "description": "memory usage high",
            }

            solution = engine.search_local(issue)

            # Should not find (different type)
            assert solution is None
        finally:
            db_path.unlink()

    @pytest.mark.skipif(
        os.getenv("OMNIMIND_FORCE_GPU") == "true",
        reason="CUDA OOM - skipping GPU tests in fast suite",
    )
    def test_find_solution_manual_required(self):
        """Test find_solution returns MANUAL_REQUIRED when no solution found"""
        engine = SolutionLookupEngine(solutions_db_path=Path("/tmp/nonexistent.json"))

        issue = {
            "type": "UNKNOWN_TYPE",
            "description": "unknown problem",
        }

        result = engine.find_solution(issue)

        assert result["source"] == "MANUAL_REQUIRED"
        assert result["confidence"] == 0
        assert len(result.get("suggestions", [])) > 0
