"""Playbook registry for OmniMind SecurityAgent."""

from .data_exfiltration_response import DataExfiltrationPlaybook
from .intrusion_response import IntrusionPlaybook
from .malware_response import MalwarePlaybook
from .privilege_escalation_response import PrivilegeEscalationPlaybook
from .rootkit_response import RootkitPlaybook

__all__ = [
    "RootkitPlaybook",
    "IntrusionPlaybook",
    "MalwarePlaybook",
    "PrivilegeEscalationPlaybook",
    "DataExfiltrationPlaybook",
]
