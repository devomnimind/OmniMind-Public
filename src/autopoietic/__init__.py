"""
Autopoietic Infrastructure Module - Self-Creating Systems

Implements Maturana & Varela's autopoiesis for cloud infrastructure:
- Self-production
- Self-maintenance
- Self-evolution
- Infrastructure-as-Desire

Author: Project conceived by Fabrício da Silva. Implementation followed an iterative AI-assisted
method: the author defined concepts and queried various AIs on construction, integrated code via
VS Code/Copilot, tested resulting errors, cross-verified validity with other models, and refined
prompts/corrections in a continuous cycle of human-led AI development.
from GitHub Copilot (Claude Haiku 4.5 and Grok Code Fast 1), with constant code review
and debugging across various models including Gemini and Perplexity AI, under
theoretical coordination by the author.
"""

from typing import List

__version__ = "1.0.0"
__author__ = (
    "This work was conceived by Fabrício da Silva and implemented with AI assistance "
    "from GitHub Copilot (Claude Haiku 4.5 and Grok Code Fast 1), with constant code "
    "review and debugging across various models including Gemini and Perplexity AI, "
    "under theoretical coordination by the author."
)

__all__: List[str] = [
    "AutopoieticSystem",
    "DesireEngine",
    "EvolutionaryArchitecture",
    "HybridInfrastructure",
]
