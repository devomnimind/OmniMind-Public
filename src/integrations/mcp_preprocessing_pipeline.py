"""
MCP Server for preprocessing pipeline - orchestrates sanitizer, compressor, and router.
Port: 4320
"""

import logging
import time
from typing import Any, Dict, List, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from src.audit.immutable_audit import get_audit_system
from src.integrations.mcp_server import MCPConfig, MCPServer

logger = logging.getLogger(__name__)


class MCPClient:
    """HTTP/JSON-RPC client for communicating with MCPs."""

    def __init__(self, host: str, port: int, timeout: int = 5):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.base_url = f"http://{host}:{port}"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def call(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call method in remote MCP via JSON-RPC HTTP."""
        try:
            payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}

            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(f"{self.base_url}/rpc", json=payload)
                response.raise_for_status()

                result = response.json()

                if "error" in result:
                    raise MCPClientError(f"RPC error: {result['error']}")

                return result.get("result", {})

        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling {method}: {e}")
            raise MCPClientError(f"Failed to call {method}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in RPC call: {e}")
            raise

    def health_check(self) -> bool:
        """Check if MCP is available."""
        try:
            with httpx.Client(timeout=2) as client:
                response = client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except Exception:
            return False


class MCPClientError(Exception):
    """Error in MCP client communication."""

    pass


class PreprocessingPipelineMCPServer(MCPServer):
    """MCP Server that orchestrates the preprocessing pipeline."""

    def __init__(self, config: Optional[MCPConfig] = None):
        super().__init__(config or self._default_config())
        self.audit_system = get_audit_system()

        # Initialize MCP clients
        self.sanitizer = MCPClient("127.0.0.1", 4330)
        self.compressor = MCPClient("127.0.0.1", 4331)
        self.router = MCPClient("127.0.0.1", 4332)

        # Register methods
        self._methods.update(
            {
                "preprocess_message": self.preprocess_message,
                "health_check": self.health_check_pipeline,
                "get_config": self.get_config,
            }
        )

    @staticmethod
    def _default_config() -> MCPConfig:
        return MCPConfig(host="127.0.0.1", port=4320)

    def preprocess_message(
        self,
        message: str,
        context_candidates: Optional[List[Dict]] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Full preprocessing pipeline: sanitize → compress → route context.

        Args:
            message: Message to preprocess
            context_candidates: Optional list of context candidates for routing
            config: Configuration dict with enable flags for each step

        Returns:
            Dict with processed_message, metadata, and steps log
        """
        start_time = time.time()
        config = config or {}
        steps_log = []
        processed_message = message

        # Fallback strategies with explicit typing
        fallback_strategies: Dict[str, Dict[str, Any]] = {
            "sanitize": {
                "primary": lambda: self.sanitizer.call(
                    "sanitize_text",
                    {"text": processed_message, "rules": config.get("sanitize_rules", {})},
                ),
                "fallback": {"sanitized_text": processed_message, "redaction_map": {}},
            },
            "compress": {
                "primary": lambda: self.compressor.call(
                    "compress_text",
                    {
                        "text": processed_message,
                        "mode": config.get("compression_mode", "summary"),
                        "target_length": config.get("target_length"),
                    },
                ),
                "fallback": {"compressed_text": processed_message, "compression_ratio": 1.0},
            },
            "route": {
                "primary": lambda: self.router.call(
                    "route_context",
                    {
                        "query": processed_message,
                        "candidates": context_candidates or [],
                        "strategy": config.get("routing_strategy", "similarity"),
                        "top_k": config.get("top_k", 5),
                    },
                ),
                "fallback": {"selected_snippets": [], "selected_ids": []},
            },
        }

        metadata = {
            "sanitized": False,
            "compressed": False,
            "context_selected": 0,
            "total_processing_time": 0.0,
        }

        # Step 1: Sanitization
        if config.get("sanitize", True):
            try:
                logger.info("Starting sanitization step...")
                primary_result = fallback_strategies["sanitize"]["primary"]  # type: ignore
                result = primary_result()
                processed_message = result.get("sanitized_text", processed_message)
                metadata["sanitized"] = True

                steps_log.append(
                    {
                        "step": "sanitize",
                        "status": "success",
                        "redaction_map": result.get("redaction_map", {}),
                        "items_redacted": result.get("statistics", {}).get("items_redacted", 0),
                    }
                )

            except Exception as e:
                logger.warning(f"Sanitization failed, using fallback: {e}")
                result = fallback_strategies["sanitize"]["fallback"]

                steps_log.append({"step": "sanitize", "status": "error", "error": str(e)})

                if hasattr(self, "audit_system"):
                    self.audit_system.log_action(
                        action="step_fallback",
                        details={"step": "sanitize", "error": str(e)},
                        category="preprocessing_pipeline_mcp",
                    )

        # Step 2: Compression
        if config.get("compress", True):
            try:
                logger.info("Starting compression step...")
                primary_result = fallback_strategies["compress"]["primary"]  # type: ignore
                result = primary_result()
                processed_message = result.get("compressed_text", processed_message)
                metadata["compressed"] = True

                steps_log.append(
                    {
                        "step": "compress",
                        "status": "success",
                        "compression_ratio": result.get("compression_ratio", 1.0),
                        "mode": config.get("compression_mode", "summary"),
                    }
                )

            except Exception as e:
                logger.warning(f"Compression failed, using fallback: {e}")

                steps_log.append({"step": "compress", "status": "error", "error": str(e)})

                if hasattr(self, "audit_system"):
                    self.audit_system.log_action(
                        action="step_fallback",
                        details={"step": "compress", "error": str(e)},
                        category="preprocessing_pipeline_mcp",
                    )

        # Step 3: Context Routing
        if config.get("route_context", True) and context_candidates:
            try:
                logger.info("Starting context routing step...")
                primary_result = fallback_strategies["route"]["primary"]  # type: ignore
                result = primary_result()
                selected_snippets = result.get("selected_snippets", [])
                metadata["context_selected"] = len(selected_snippets)

                steps_log.append(
                    {
                        "step": "route_context",
                        "status": "success",
                        "selected_count": len(selected_snippets),
                        "strategy": config.get("routing_strategy", "similarity"),
                    }
                )

            except Exception as e:
                logger.warning(f"Context routing failed, using fallback: {e}")

                steps_log.append({"step": "route_context", "status": "error", "error": str(e)})

                if hasattr(self, "audit_system"):
                    self.audit_system.log_action(
                        action="step_fallback",
                        details={"step": "route_context", "error": str(e)},
                        category="preprocessing_pipeline_mcp",
                    )

        # Calculate total processing time
        metadata["total_processing_time"] = time.time() - start_time

        # Audit logging
        if hasattr(self, "audit_system"):
            self.audit_system.log_action(
                action="message_preprocessed",
                details={
                    "steps_completed": (sum(1 for s in steps_log if s["status"] == "success")),
                    "steps_failed": sum(1 for s in steps_log if s["status"] == "error"),
                    "processing_time": metadata["total_processing_time"],
                },
                category="preprocessing_pipeline_mcp",
            )

        return {
            "status": "success",
            "processed_message": processed_message,
            "metadata": metadata,
            "steps": steps_log,
        }

    def health_check_pipeline(self) -> Dict[str, Any]:
        """Check health of all pipeline components."""
        components_health = {
            "sanitizer": self.sanitizer.health_check(),
            "compressor": self.compressor.health_check(),
            "router": self.router.health_check(),
        }

        all_healthy = all(components_health.values())

        return {
            "status": "healthy" if all_healthy else "degraded",
            "components": components_health,
            "pipeline_operational": all_healthy,
        }

    def get_config(self) -> Dict[str, Any]:
        """Get current pipeline configuration."""
        return {
            "status": "success",
            "pipeline": {
                "name": "preprocessing_pipeline_mcp",
                "port": 4320,
                "components": {
                    "sanitizer": {"port": 4330, "type": "data_sanitization"},
                    "compressor": {"port": 4331, "type": "text_compression"},
                    "router": {"port": 4332, "type": "context_routing"},
                },
                "features": [
                    "message_preprocessing",
                    "data_sanitization",
                    "compression",
                    "context_routing",
                ],
                "default_config": {
                    "sanitize": True,
                    "compress": True,
                    "route_context": True,
                    "compression_mode": "summary",
                    "routing_strategy": "similarity",
                    "top_k": 5,
                },
            },
        }


if __name__ == "__main__":
    server = PreprocessingPipelineMCPServer()
    # run() method not available in base MCPServer yet
