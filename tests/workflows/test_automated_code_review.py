"""
Tests for automated_code_review module.
"""

from pathlib import Path

import pytest

from src.workflows.automated_code_review import (
    AutomatedCodeReviewer,
    CodeIssue,
    IssueSeverity,
    IssueCategory,
    ReviewResult,
)


class TestCodeIssue:
    """Tests for CodeIssue."""

    def test_code_issue_creation(self) -> None:
        """Test CodeIssue creation."""
        issue = CodeIssue(
            line_number=10,
            severity=IssueSeverity.WARNING,
            category=IssueCategory.STYLE,
            message="Line too long",
            suggestion="Break into multiple lines",
        )

        assert issue.line_number == 10
        assert issue.severity == IssueSeverity.WARNING
        assert issue.category == IssueCategory.STYLE


class TestReviewResult:
    """Tests for ReviewResult."""

    def test_review_result_creation(self) -> None:
        """Test ReviewResult creation."""
        result = ReviewResult(
            file_path="test.py",
            timestamp="2025-11-19T00:00:00",
        )

        assert result.file_path == "test.py"
        assert len(result.issues) == 0

    def test_add_issue(self) -> None:
        """Test adding issues to result."""
        result = ReviewResult(
            file_path="test.py",
            timestamp="2025-11-19T00:00:00",
        )

        result.add_issue(
            line=1,
            severity=IssueSeverity.ERROR,
            category=IssueCategory.SECURITY,
            message="Security issue",
        )

        assert len(result.issues) == 1
        assert result.issues[0].severity == IssueSeverity.ERROR


class TestAutomatedCodeReviewer:
    """Tests for AutomatedCodeReviewer."""

    @pytest.fixture
    def reviewer(self) -> AutomatedCodeReviewer:
        """Create reviewer instance."""
        return AutomatedCodeReviewer(min_score=8.0)

    @pytest.fixture
    def sample_code(self, tmp_path: Path) -> Path:
        """Create sample Python file."""
        code_file = tmp_path / "sample.py"
        code_file.write_text(
            '''"""Sample module."""

def hello_world() -> str:
    """Say hello."""
    return "Hello, World!"

if __name__ == "__main__":
    print(hello_world())
'''
        )
        return code_file

    def test_reviewer_initialization(self, reviewer: AutomatedCodeReviewer) -> None:
        """Test reviewer initialization."""
        assert reviewer.min_score == 8.0
        assert reviewer.max_complexity == 10

    def test_review_good_code(
        self, reviewer: AutomatedCodeReviewer, sample_code: Path
    ) -> None:
        """Test reviewing good code."""
        result = reviewer.review_file(sample_code)

        assert result.file_path == str(sample_code)
        assert result.metrics is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
