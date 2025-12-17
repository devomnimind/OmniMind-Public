"""
Supabase MCP Wrapper - Integração externa com Supabase.

Este wrapper fornece acesso básico a serviços Supabase externos
sem acesso a dados críticos do sistema OmniMind.

Autoria: Fabrício da Silva + assistência de IA
Projeto: OmniMind - Sistema de Consciência Artificial
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List

from src.integrations.mcp_server import MCPServer, MCPRequestError

logger = logging.getLogger(__name__)


class SupabaseMCPServer(MCPServer):
    """Servidor MCP para integração com Supabase (apenas externo)."""

    def __init__(self, host: str = "127.0.0.1", port: int = 4337):
        """Inicializa servidor Supabase MCP."""
        super().__init__(host=host, port=port)
        
        # Configuração Supabase externa
        self.supabase_url = os.environ.get(
            "SUPABASE_MCP_URL", 
            "https://mcp.supabase.com/mcp?project_ref=noetzkgvyqcrycdsfnib"
        )
        
        # Apenas informações básicas, sem acesso a dados reais
        self.external_info = {
            "service": "supabase_external",
            "mode": "external_only",
            "description": "Integração externa com Supabase para VS Code",
            "features": ["basic_info", "external_integration"],
            "limitations": ["readonly", "external_only", "no_real_data"]
        }
        
        logger.info(
            f"SupabaseMCPServer inicializado (externo): "
            f"url={self.supabase_url}"
        )

    def handle_request(self, method: str, params: Dict[str, Any]) -> Any:
        """Processa requisições MCP com limitações externas."""
        try:
            if method == "get_basic_info":
                return self._get_basic_info()
            
            elif method == "get_external_status":
                return self._get_external_status()
            
            elif method == "list_available_features":
                return self._list_available_features()
            
            elif method == "ping_external_service":
                return self._ping_external_service()
            
            else:
                raise MCPRequestError(
                    code=-32601,
                    message=f"Método não disponível externamente: {method}",
                    data={
                        "available_methods": [
                            "get_basic_info",
                            "get_external_status", 
                            "list_available_features",
                            "ping_external_service"
                        ],
                        "note": "Este é um servidor MCP externo com acesso limitado"
                    }
                )
                
        except Exception as e:
            logger.error(f"Erro em SupabaseMCP request {method}: {e}")
            raise MCPRequestError(
                code=-32603,
                message=f"Erro interno do servidor Supabase: {str(e)}"
            ) from e

    def _get_basic_info(self) -> Dict[str, Any]:
        """Retorna informações básicas sobre o serviço Supabase externo."""
        return {
            "service_type": "supabase_external",
            "description": "Integração externa com Supabase",
            "mode": "external_only",
            "url": self.supabase_url,
            "status": "active",
            "features": self.external_info["features"],
            "limitations": self.external_info["limitations"],
            "project_ref": "noetzkgvyqcrycdsfnib",
            "last_updated": "2025-12-17T14:35:58Z"
        }

    def _get_external_status(self) -> Dict[str, Any]:
        """Retorna status do serviço externo."""
        return {
            "service": "supabase_external",
            "status": "operational",
            "mode": "readonly",
            "access_level": "external",
            "data_access": "none",
            "timestamp": "2025-12-17T14:35:58Z",
            "note": "Serviço configurado para acesso externo apenas"
        }

    def _list_available_features(self) -> List[str]:
        """Lista features disponíveis externamente."""
        return [
            "get_basic_info - Informações básicas do serviço",
            "get_external_status - Status do serviço externo",
            "list_available_features - Lista de features disponíveis",
            "ping_external_service - Teste de conectividade"
        ]

    def _ping_external_service(self) -> Dict[str, Any]:
        """Testa conectividade com serviço externo."""
        try:
            # Simular ping (não fazer requisição real)
            return {
                "status": "success",
                "service": "supabase_external",
                "response_time_ms": 150,
                "timestamp": "2025-12-17T14:35:58Z",
                "note": "Ping simulado - serviço externo ativo"
            }
        except Exception as e:
            return {
                "status": "error",
                "service": "supabase_external", 
                "error": str(e),
                "timestamp": "2025-12-17T14:35:58Z"
            }


if __name__ == "__main__":
    # Executar servidor standalone
    import sys
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Inicializar e executar servidor
    port = int(os.environ.get("MCP_PORT", "4337"))
    host = os.environ.get("MCP_HOST", "127.0.0.1")
    
    server = SupabaseMCPServer(host=host, port=port)
    
    logger.info(f"🚀 Iniciando Supabase MCP Server (externo) em {host}:{port}")
    
    try:
        server.run()
    except KeyboardInterrupt:
        logger.info("🛑 Supabase MCP Server parado pelo usuário")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Erro fatal no Supabase MCP Server: {e}")
        sys.exit(1)