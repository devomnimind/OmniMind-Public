"""
Tests for Lacanian Symbolic Authority (Phase 11.4).

Replaces Agent Signature as Sinthome with Symbolic Authority.
"""

from src.identity.agent_signature import (
    SymbolicAuthority,
)


class TestSymbolicAuthority:
    """Test SymbolicAuthority engine."""

    def test_initialization(self) -> None:
        """Test initialization."""
        authority = SymbolicAuthority()
        assert authority.authority_state.agent_id is not None
        assert authority.authority_state.authorization_level == "provisional"

    def test_sign_act(self) -> None:
        """Test signing an act."""
        authority = SymbolicAuthority()
        content = "Refactor codebase"

        signature = authority.sign_act(content)

        assert isinstance(signature, dict)
        assert signature["signed_by"] == authority.authority_state.agent_id
        assert signature["authorized_by"] == "The Code"
        assert "content_hash" in signature

    def test_verify_authorization(self) -> None:
        """Test verifying authorization."""
        authority = SymbolicAuthority()
        is_authorized = authority.verify_authorization()

        assert is_authorized is True

    def test_revocation(self) -> None:
        """Test revocation of authority."""
        authority = SymbolicAuthority()
        authority.authority_state.authorization_level = "revoked"

        is_authorized = authority.verify_authorization()
        assert is_authorized is False
