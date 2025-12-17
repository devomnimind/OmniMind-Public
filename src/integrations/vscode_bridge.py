#!/usr/bin/env python3
"""
VS Code MCP Bridge
------------------
Adaptador que permite ao VS Code (via Stdio) se comunicar com os servidores
MCP do OmniMind que já estão rodando via HTTP.

Uso:
    python3 -m src.integrations.vscode_bridge --port 4321
"""

import argparse
import json
import logging
import sys
import urllib.error
import urllib.request

# Configurar logging para stderr (não poluir stdout que é usado pelo protocolo)
logging.basicConfig(level=logging.INFO, stream=sys.stderr, format="[Bridge] %(message)s")
logger = logging.getLogger("vscode_bridge")


def send_rpc(endpoint, payload):
    """Envia requisição JSON-RPC via HTTP POST"""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        endpoint, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        logger.error(f"Erro na requisição HTTP para {endpoint}: {e}")
        return {
            "jsonrpc": "2.0",
            "id": payload.get("id"),
            "error": {"code": -32603, "message": str(e)},
        }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, required=True, help="Porta do servidor MCP HTTP")
    args = parser.parse_args()

    endpoint = f"http://127.0.0.1:{args.port}/mcp"
    logger.info(f"Iniciando bridge para {endpoint}")

    while True:
        try:
            # Ler linha do stdin (bloqueante)
            line = sys.stdin.readline()
            if not line:
                break

            # Parsear request
            try:
                request = json.loads(line)
            except json.JSONDecodeError:
                logger.error("JSON inválido recebido")
                continue

            # Log (opcional, para debug)
            # logger.info(f"Request: {request.get('method')}")

            # Encaminhar para servidor HTTP
            response = send_rpc(endpoint, request)

            # Escrever resposta no stdout
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()

        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Erro fatal no loop: {e}")
            break


if __name__ == "__main__":
    main()
