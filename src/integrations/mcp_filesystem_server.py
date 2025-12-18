"""
MCP Filesystem Server - Servidor MCP para operações seguras de filesystem.

Este servidor MCP implementa operações de filesystem seguras e controladas:
- Leitura segura de arquivos com restrições de caminho
- Listagem de diretórios com filtros de segurança
- Operações básicas de arquivo sem risco de segurança

Autor: OmniMind Security Team
Data: 2025-12-18
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.integrations.mcp_server import MCPConfig, MCPServer

logger = logging.getLogger(__name__)


class FilesystemMCPServer(MCPServer):
    """Servidor MCP para operações seguras de filesystem."""

    def __init__(self, allowed_paths: Optional[List[str]] = None) -> None:
        """Inicializa o servidor Filesystem MCP.

        Args:
            allowed_paths: Lista de caminhos permitidos. Se None, usa defaults seguros.
        """
        # Define caminhos padrão se não especificados
        if allowed_paths is None:
            project_root = Path(__file__).resolve().parents[2]
            allowed_paths = [
                str(project_root / "src"),
                str(project_root / "tests"),
                str(project_root / "docs"),
                str(project_root / "config"),
                str(project_root / "scripts"),
                str(project_root / "web"),
                str(project_root / "notebooks"),
            ]

        # Inicializar classe base com caminhos permitidos
        super().__init__(allowed_roots=allowed_paths)

        # Armazenar caminhos como Path objects para validações
        self.allowed_paths = [Path(p).resolve() for p in allowed_paths]
        self.max_file_size = 2 * 1024 * 1024  # 2MB

        # Registrar ferramentas MCP
        self.register_tools()

        logger.info(
            f"Filesystem MCP inicializado com {len(self.allowed_paths)} caminhos permitidos"
        )

    def _is_path_allowed(self, path: Path) -> bool:
        """Verifica se o caminho é permitido."""
        try:
            resolved_path = path.resolve()
            # Verificar se está dentro de algum caminho permitido
            for allowed in self.allowed_paths:
                if resolved_path.is_relative_to(allowed):
                    return True
            return False
        except (OSError, RuntimeError):
            return False

    def _validate_file_operation(self, file_path: str, operation: str) -> Path:
        """Valida operação de arquivo."""
        try:
            path = Path(file_path).resolve()

            if not self._is_path_allowed(path):
                raise ValueError(f"Caminho não permitido: {file_path}")

            if not path.exists():
                if operation in ["read", "list"]:
                    raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

            if operation == "read" and path.is_file():
                if path.stat().st_size > self.max_file_size:
                    raise ValueError(f"Arquivo muito grande: {path.stat().st_size} bytes")

            return path

        except Exception as e:
            logger.error(f"Erro na validação de {operation}: {e}")
            raise

    def register_tools(self) -> None:
        """Registra as ferramentas do servidor filesystem."""

        @self.tool("read_file")
        def read_file(file_path: str) -> str:
            """Lê o conteúdo de um arquivo de forma segura.

            Args:
                file_path: Caminho do arquivo a ser lido.

            Returns:
                Conteúdo do arquivo como string.
            """
            path = self._validate_file_operation(file_path, "read")

            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()

                logger.info(f"Arquivo lido: {file_path}")
                return content

            except UnicodeDecodeError:
                raise ValueError(f"Arquivo não é texto válido: {file_path}")
            except Exception as e:
                logger.error(f"Erro ao ler arquivo {file_path}: {e}")
                raise

        @self.tool("list_directory")
        def list_directory(dir_path: str) -> List[Dict[str, Any]]:
            """Lista o conteúdo de um diretório de forma segura.

            Args:
                dir_path: Caminho do diretório a ser listado.

            Returns:
                Lista de itens com nome, tipo e tamanho.
            """
            path = self._validate_file_operation(dir_path, "list")

            if not path.is_dir():
                raise ValueError(f"Não é um diretório: {dir_path}")

            try:
                items = []
                for item in path.iterdir():
                    if item.name.startswith("."):  # Pular arquivos ocultos
                        continue

                    item_info = {
                        "name": item.name,
                        "type": "directory" if item.is_dir() else "file",
                        "size": item.stat().st_size if item.is_file() else 0,
                    }
                    items.append(item_info)

                logger.info(f"Diretório listado: {dir_path} ({len(items)} itens)")
                return items

            except Exception as e:
                logger.error(f"Erro ao listar diretório {dir_path}: {e}")
                raise

        @self.tool("get_file_info")
        def get_file_info(file_path: str) -> Dict[str, Any]:
            """Obtém informações sobre um arquivo.

            Args:
                file_path: Caminho do arquivo.

            Returns:
                Dicionário com informações do arquivo.
            """
            path = self._validate_file_operation(file_path, "info")

            try:
                stat = path.stat()
                info = {
                    "name": path.name,
                    "path": str(path),
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                    "is_file": path.is_file(),
                    "is_dir": path.is_dir(),
                    "exists": True,
                }

                logger.info(f"Informações obtidas: {file_path}")
                return info

            except Exception as e:
                logger.error(f"Erro ao obter info do arquivo {file_path}: {e}")
                raise

        @self.tool("search_files")
        def search_files(directory: str, pattern: str) -> List[str]:
            """Busca arquivos por padrão em um diretório.

            Args:
                directory: Diretório base para busca.
                pattern: Padrão de busca (ex: *.py).

            Returns:
                Lista de caminhos encontrados.
            """
            path = self._validate_file_operation(directory, "search")

            if not path.is_dir():
                raise ValueError(f"Não é um diretório: {directory}")

            try:
                import fnmatch

                matches = []

                for root, dirs, files in os.walk(path):
                    root_path = Path(root)

                    # Verificar se o diretório atual é permitido
                    if not self._is_path_allowed(root_path):
                        continue

                    for file in files:
                        if fnmatch.fnmatch(file, pattern):
                            matches.append(str(Path(root) / file))

                    # Limitar resultados
                    if len(matches) > 100:
                        break

                logger.info(
                    f"Busca concluída: {directory} pattern:{pattern} ({len(matches)} encontrados)"
                )
                return matches[:100]  # Limitar a 100 resultados

            except Exception as e:
                logger.error(f"Erro na busca {directory} pattern:{pattern}: {e}")
                raise


def main() -> None:
    """Ponto de entrada principal."""
    import argparse

    parser = argparse.ArgumentParser(description="MCP Filesystem Server")
    parser.add_argument("--port", type=int, default=None, help="Porta do servidor")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host do servidor")
    parser.add_argument("--allowed-paths", nargs="+", help="Caminhos permitidos")

    args = parser.parse_args()

    # Usar porta do ambiente se não especificada
    port = args.port or int(os.environ.get("MCP_PORT", "4331"))
    host = args.host

    # Create config with custom host/port
    config = MCPConfig(host=host, port=port)

    server = FilesystemMCPServer(allowed_paths=args.allowed_paths)
    server.config = config  # Override the config
    server.start(daemon=False)


if __name__ == "__main__":
    main()
