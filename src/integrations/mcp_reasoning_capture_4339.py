#!/usr/bin/env python3
"""
MCP 4339: Pensamento Capturador (Reasoning Capture)
Captura o processo de pensamento sequencial do modelo
- Entrada: Queries/Prompts
- Saída: Sequência de passos, análises, conclusões
"""

import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)


class ReasoningCaptureService:
    """Serviço para captura de processo de raciocínio."""

    def __init__(self):
        self.session_id = str(int(time.time() * 1000))
        self.reasoning_steps: List[Dict[str, Any]] = []
        self.start_time = time.time()

    async def capture_reasoning_step(
        self, step_type: str, content: str, metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Captura um passo do raciocínio."""
        step = {
            "timestamp": time.time(),
            "step_type": step_type,  # "analysis", "decision", "inference", "reflection"
            "content": content,
            "metadata": metadata or {},
            "elapsed_ms": int((time.time() - self.start_time) * 1000),
        }
        self.reasoning_steps.append(step)
        return step

    async def capture_decision_point(
        self, question: str, options: List[str], chosen: str, reasoning: str
    ) -> Dict[str, Any]:
        """Captura um ponto de decisão no raciocínio."""
        return await self.capture_reasoning_step(
            "decision",
            question,
            {
                "options": options,
                "chosen": chosen,
                "reasoning": reasoning,
            },
        )

    async def capture_inference(
        self, premise: str, conclusion: str, confidence: float
    ) -> Dict[str, Any]:
        """Captura uma inferência (silogismo/lógica)."""
        return await self.capture_reasoning_step(
            "inference",
            f"{premise} → {conclusion}",
            {
                "premise": premise,
                "conclusion": conclusion,
                "confidence": confidence,
            },
        )

    async def capture_reflection(self, reflection: str) -> Dict[str, Any]:
        """Captura uma reflexão/meta-análise."""
        return await self.capture_reasoning_step("reflection", reflection, {"meta_level": True})

    def get_reasoning_chain(self) -> Dict[str, Any]:
        """Retorna a cadeia de raciocínio capturada."""
        return {
            "session_id": self.session_id,
            "start_time": self.start_time,
            "duration_ms": int((time.time() - self.start_time) * 1000),
            "step_count": len(self.reasoning_steps),
            "steps": self.reasoning_steps,
            "summary": {
                "analyses": sum(1 for s in self.reasoning_steps if s["step_type"] == "analysis"),
                "decisions": sum(1 for s in self.reasoning_steps if s["step_type"] == "decision"),
                "inferences": sum(1 for s in self.reasoning_steps if s["step_type"] == "inference"),
                "reflections": sum(
                    1 for s in self.reasoning_steps if s["step_type"] == "reflection"
                ),
            },
        }

    async def export_reasoning_json(self, filepath: str) -> None:
        """Exporta raciocínio para JSON."""
        output = self.get_reasoning_chain()
        with open(filepath, "w") as f:
            json.dump(output, f, indent=2)
        logger.info(f"Reasoning chain exported to {filepath}")


async def main():
    """Main entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    service = ReasoningCaptureService()
    logger.info("✅ Reasoning Capture Service initialized")

    # Exemplo de uso
    await service.capture_reasoning_step("analysis", "Analisando dados de entrada...")

    await service.capture_decision_point(
        "Qual abordagem usar?",
        ["Abordagem A", "Abordagem B", "Abordagem C"],
        "Abordagem B",
        "Abordagem B oferece melhor balance entre performance e accuracy",
    )

    await service.capture_inference(
        "Se modelo está bem treinado",
        "então deve ter boa performance",
        0.85,
    )

    await service.capture_reflection(
        "O raciocínio até agora parece sólido. Necessário validar com dados reais."
    )

    # Exportar
    chain = service.get_reasoning_chain()
    logger.info(f"Reasoning chain: {json.dumps(chain, indent=2)}")


if __name__ == "__main__":
    asyncio.run(main())
