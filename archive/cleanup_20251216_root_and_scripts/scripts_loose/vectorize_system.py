#!/usr/bin/env python3
"""
Script para vetorização completa do sistema Ubuntu e OmniMind.

Vetoriza:
1. Todo o projeto OmniMind (código, docs, dados)
2. Arquivos seguros do kernel Ubuntu (/proc, /sys, /etc)
3. Programas e bibliotecas do sistema
4. Configurações do sistema
5. Logs do sistema (se acessíveis)

Uso:
    python vectorize_system.py                    # Vetorização completa
    python vectorize_system.py --ubuntu-only     # Apenas sistema Ubuntu
    python vectorize_system.py --omnimind-only   # Apenas projeto OmniMind
    python vectorize_system.py --kernel-only     # Apenas arquivos do kernel
    python vectorize_system.py --help            # Ajuda

Requisitos:
- Qdrant rodando (docker-compose -f deploy/docker-compose.yml up -d qdrant)
- Permissões de leitura para arquivos do sistema
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import tomli  # type: ignore
except ImportError:
    import tomllib as tomli  # type: ignore

from embeddings.code_embeddings import OmniMindEmbeddings

# Adicionar src ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(project_root / "logs" / "system_vectorization.log", mode="a"),
    ],
)

logger = logging.getLogger(__name__)


def load_config() -> Dict:
    """Carrega configuração do arquivo TOML."""
    config_path = project_root / "config" / "system_vectorization.toml"

    if not config_path.exists():
        logger.warning(f"Arquivo de configuração não encontrado: {config_path}")
        return {}

    try:
        with open(config_path, "rb") as f:
            config = tomli.load(f)
        logger.info(f"✅ Configuração carregada de {config_path}")
        return config
    except Exception as e:
        logger.error(f"Erro ao carregar configuração: {e}")
        return {}


class SystemVectorizer:
    """Vetoriza sistema Ubuntu e projeto OmniMind."""

    def __init__(self, qdrant_url: str = "http://localhost:6333", config: Optional[Dict] = None):
        self.project_root = project_root
        self.config = config or load_config()
        self.embeddings = OmniMindEmbeddings(qdrant_url=qdrant_url)
        logger.info("🧠 SystemVectorizer inicializado")

    def vectorize_ubuntu_system(self) -> Dict[str, int]:
        """
        Vetoriza arquivos seguros do sistema Ubuntu.

        Inclui:
        - Arquivos do kernel (/proc, /sys)
        - Configurações (/etc)
        - Logs do sistema (/var/log, se acessível)
        - Informações de hardware
        """
        logger.info("🐧 Iniciando vetorização do sistema Ubuntu")

        results = {}

        # Carregar configurações
        sys_config = self.config.get("system_vectorization", {})
        kernel_files = sys_config.get("kernel_files", [])
        system_configs = sys_config.get("system_configs", [])
        system_dirs = sys_config.get("system_dirs", [])
        exclude_patterns = sys_config.get("exclude_patterns", [])
        max_files_per_dir = sys_config.get("max_files_per_dir", 100)
        max_file_size_mb = sys_config.get("max_file_size_mb", 10)

        # Combinar arquivos do kernel e configurações
        all_files = kernel_files + system_configs

        # Vetorizar arquivos individuais do kernel
        logger.info("📄 Vetorizando arquivos do kernel...")
        for file_path in all_files:
            if self._should_exclude(file_path, exclude_patterns):
                logger.debug(f"  ⏭️ Excluído: {file_path}")
                continue

            if os.path.exists(file_path) and os.access(file_path, os.R_OK):
                try:
                    # Verificar se é um arquivo de texto seguro
                    if self._is_safe_text_file(file_path, max_file_size_mb):
                        count = self.embeddings.index_file(file_path)
                        results[f"kernel_{Path(file_path).name}"] = count
                        logger.info(f"  ✅ {file_path}: {count} chunks")
                    else:
                        logger.info(f"  ⏭️ Pulado (não é texto seguro): {file_path}")
                except (PermissionError, OSError, UnicodeDecodeError) as e:
                    logger.warning(f"  ❌ Erro ao vetorizar {file_path}: {e}")
            else:
                logger.debug(f"  ⏭️ Arquivo não acessível: {file_path}")

        # Vetorizar diretórios do sistema (com limites)
        for dir_path in system_dirs:
            if not self._should_exclude(dir_path, exclude_patterns):
                if os.path.exists(dir_path) and os.access(dir_path, os.R_OK):
                    logger.info(f"📁 Vetorizando diretório: {dir_path}")
                    dir_results = self._vectorize_system_directory(dir_path, max_files_per_dir)
                    results.update(dir_results)

        # Coletar metadados do sistema via comandos
        logger.info("🔧 Coletando metadados do sistema...")
        system_results = self.embeddings.index_system_metadata()
        results.update(system_results)

        # Vetorizar programas e bibliotecas importantes
        logger.info("📦 Vetorizando programas do sistema...")
        programs_results = self._vectorize_system_programs()
        results.update(programs_results)

        total_chunks = sum(results.values())
        logger.info(f"✅ Sistema Ubuntu vetorizado: {len(results)} arquivos, {total_chunks} chunks")

        return results

    def _is_safe_text_file(self, file_path: str, max_file_size_mb: int = 10) -> bool:
        """Verifica se um arquivo é seguro para vetorização (texto legível)."""
        try:
            # Verificar tamanho (evitar arquivos muito grandes)
            if os.path.getsize(file_path) > max_file_size_mb * 1024 * 1024:
                return False

            # Tentar ler primeiras linhas
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                sample = f.read(1024)  # Primeiros 1KB

            # Verificar se contém caracteres de controle excessivos
            control_chars = sum(1 for c in sample if ord(c) < 32 and c not in "\n\r\t")
            if control_chars > len(sample) * 0.1:  # Mais de 10% caracteres de controle
                return False

            return True

        except (OSError, UnicodeDecodeError):
            return False

    def _should_exclude(self, file_path: str, exclude_patterns: List[str]) -> bool:
        """Verifica se um arquivo deve ser excluído baseado nos padrões."""
        from fnmatch import fnmatch

        for pattern in exclude_patterns:
            if fnmatch(file_path, pattern) or pattern in file_path:
                return True
        return False

    def _vectorize_system_directory(self, dir_path: str, max_files: int = 100) -> Dict[str, int]:
        """Vetoriza um diretório do sistema com limites de segurança."""
        results = {}
        file_count = 0

        # Carregar extensões da configuração
        sys_config = self.config.get("system_vectorization", {})
        extensions = sys_config.get(
            "system_extensions", [".conf", ".txt", ".md", ".yaml", ".yml", ".json", ".service"]
        )
        exclude_patterns = sys_config.get("exclude_patterns", [])

        try:
            dir_path_obj = Path(dir_path)

            # Coletar arquivos de texto
            text_files = []
            for ext in extensions:
                for file_path in dir_path_obj.rglob(f"*{ext}"):
                    if (
                        file_path.is_file()
                        and not self._should_exclude(str(file_path), exclude_patterns)
                        and self._is_safe_text_file(str(file_path))
                    ):
                        text_files.append(file_path)
                        if len(text_files) >= max_files:
                            break
                if len(text_files) >= max_files:
                    break

            logger.info(f"  📄 Encontrados {len(text_files)} arquivos de texto em {dir_path}")

            # Vetorizar arquivos
            for file_path in text_files:
                try:
                    count = self.embeddings.index_file(str(file_path))
                    results[f"system_{file_path.name}"] = count
                    file_count += 1

                    if file_count % 10 == 0:
                        logger.info(f"    Processados {file_count}/{len(text_files)} arquivos...")

                except Exception as e:
                    logger.warning(f"    Erro ao vetorizar {file_path}: {e}")

        except Exception as e:
            logger.warning(f"Erro ao vetorizar diretório {dir_path}: {e}")

        return results

    def _vectorize_system_programs(self) -> Dict[str, int]:
        """Vetoriza informações sobre programas instalados."""
        results = {}

        # Carregar comandos da configuração
        sys_config = self.config.get("system_vectorization", {})
        system_commands_config = self.config.get("system_commands", {})

        # Combinar comandos padrão com configuração
        program_commands = {
            "installed_packages": system_commands_config.get(
                "installed_packages", ["dpkg", "--list"]
            ),
            "python_packages": system_commands_config.get("python_packages", ["pip", "list"]),
            "node_packages": (
                system_commands_config.get("node_packages") if self._command_exists("npm") else None
            ),
            "system_services": system_commands_config.get(
                "system_services", ["systemctl", "list-units", "--type=service", "--state=active"]
            ),
            "kernel_modules": system_commands_config.get("kernel_modules", ["lsmod"]),
            "pci_devices": system_commands_config.get("pci_devices", ["lspci"]),
            "usb_devices": system_commands_config.get("usb_devices", ["lsusb"]),
            "network_interfaces": system_commands_config.get("network_interfaces", ["ip", "addr"]),
            "disk_usage": system_commands_config.get("disk_usage", ["df", "-h"]),
            "memory_info": system_commands_config.get("memory_info", ["free", "-h"]),
            "cpu_info": system_commands_config.get("cpu_info", ["lscpu"]),
            "system_uptime": system_commands_config.get("system_uptime", ["uptime"]),
        }

        command_timeout = sys_config.get("command_timeout", 30)

        for name, cmd in program_commands.items():
            if cmd is None:
                continue

            try:
                import subprocess

                # Usar shell=True apenas para comandos complexos
                if "|" in cmd or ">" in " ".join(cmd):
                    result = subprocess.run(
                        " ".join(cmd),
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=command_timeout,
                    )
                else:
                    result = subprocess.run(
                        cmd, capture_output=True, text=True, timeout=command_timeout
                    )

                if result.returncode == 0 and result.stdout.strip():
                    content = result.stdout.strip()
                    if len(content) > 1000:  # Apenas se houver conteúdo significativo
                        # Criar chunks para conteúdo longo
                        from embeddings.code_embeddings import ContentType

                        chunks = self.embeddings._chunk_text(
                            content, f"system_{name}", ContentType.SYSTEM
                        )
                        count = self.embeddings._index_chunks_optimized(
                            chunks, f"system_program_{name}"
                        )
                        results[f"program_{name}"] = count
                        logger.info(f"  📦 {name}: {count} chunks")
                else:
                    logger.debug(f"  ⏭️ Comando {name} sem output ou falhou")

            except (
                subprocess.TimeoutExpired,
                FileNotFoundError,
                PermissionError,
            ) as e:  # type: ignore[possibly-unbound-variable,name-defined]
                # subprocess imported conditionally above
                logger.warning(f"  ❌ Erro no comando {name}: {e}")

        return results

    def _command_exists(self, command: str) -> bool:
        """Verifica se um comando existe no sistema."""
        try:
            import subprocess

            subprocess.run([command, "--version"], capture_output=True, timeout=5)
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):  # type: ignore[attr-defined]
            return False

    def vectorize_omnimind_project(self, incremental: bool = False) -> Dict[str, Dict[str, int]]:
        """Vetoriza todo o projeto OmniMind."""
        logger.info("🧠 Iniciando vetorização do projeto OmniMind")

        # Carregar configurações
        omnimind_config = self.config.get("omnimind", {})
        project_dirs = omnimind_config.get(  # noqa: F841 - Para configuração futura
            "project_dirs", ["src", "docs", "scripts", "tests", "config", "notebooks"]
        )
        code_extensions = omnimind_config.get(  # noqa: F841 - Para configuração futura
            "code_extensions",
            [
                ".py",
                ".js",
                ".ts",
                ".html",
                ".css",
                ".md",
                ".txt",
                ".yaml",
                ".yml",
                ".json",
                ".toml",
                ".ini",
            ],
        )
        indexing_config = self.config.get("indexing", {})
        max_workers = indexing_config.get("max_workers", 4)
        min_file_size = indexing_config.get("min_file_size", 10)

        # Usar a funcionalidade existente de indexação do projeto
        results = self.embeddings.index_omnimind_project(
            str(self.project_root),
            max_workers=max_workers,
            incremental=incremental,
            min_file_size=min_file_size,
        )

        total_chunks = sum(sum(stage_results.values()) for stage_results in results.values())
        logger.info(f"✅ Projeto OmniMind vetorizado: {total_chunks} chunks totais")

        return results

    def vectorize_kernel_files(self) -> Dict[str, int]:
        """Vetoriza especificamente arquivos relacionados ao kernel AI."""
        logger.info("🧠 Iniciando vetorização de arquivos do kernel AI")

        # Carregar configurações
        omnimind_config = self.config.get("omnimind", {})
        kernel_dirs = omnimind_config.get(
            "kernel_dirs",
            [
                "kernel_ai",
                "quantum_ai",
                "neurosymbolic",
                "src/consciousness",
                "src/memory",
                "src/orchestrator",
            ],
        )

        results = {}

        for dir_name in kernel_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                logger.info(f"📁 Vetorizando {dir_name}...")
                dir_results = self.embeddings.index_directory(
                    str(dir_path),
                    extensions=[".py", ".md", ".txt", ".yaml", ".yml"],
                    incremental=False,
                    min_file_size=1,  # Mesmo arquivos pequenos do kernel
                )
                results.update(dir_results)

        total_chunks = sum(results.values())
        logger.info(
            f"✅ Arquivos do kernel vetorizados: {len(results)} arquivos, {total_chunks} chunks"
        )

        return results

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas da vetorização."""
        return self.embeddings.get_stats()

    def search_system(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Busca semântica no conteúdo do sistema vetorizado."""
        # Carregar configurações de busca
        search_config = self.config.get("search", {})
        max_top_k = search_config.get("max_top_k", 50)
        score_threshold = search_config.get("score_threshold", 0.7)

        # Limitar top_k
        top_k = min(top_k, max_top_k)

        from embeddings.code_embeddings import ContentType

        results = self.embeddings.search(query, top_k=top_k, content_types=[ContentType.SYSTEM])

        # Filtrar por score threshold
        filtered_results = [r for r in results if r.get("score", 0) >= score_threshold]

        return filtered_results


def main():
    parser = argparse.ArgumentParser(
        description="Vetorização completa do sistema Ubuntu e OmniMind"
    )
    parser.add_argument(
        "--ubuntu-only",
        action="store_true",
        help="Vetorizar apenas o sistema Ubuntu",
    )
    parser.add_argument(
        "--omnimind-only",
        action="store_true",
        help="Vetorizar apenas o projeto OmniMind",
    )
    parser.add_argument(
        "--kernel-only",
        action="store_true",
        help="Vetorizar apenas arquivos do kernel AI",
    )
    parser.add_argument(
        "--incremental",
        action="store_true",
        help="Indexação incremental (só arquivos modificados)",
    )
    parser.add_argument(
        "--qdrant-url",
        default="http://localhost:6333",
        help="URL do Qdrant (padrão: http://localhost:6333)",
    )
    parser.add_argument(
        "--search",
        help="Realizar busca semântica no sistema vetorizado",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Mostrar estatísticas da coleção",
    )

    args = parser.parse_args()

    try:
        logger.info("🚀 Iniciando SystemVectorizer")
        vectorizer = SystemVectorizer(qdrant_url=args.qdrant_url)

        # Verificar se Qdrant está rodando
        import requests

        try:
            response = requests.get(f"{args.qdrant_url}/healthz", timeout=5)
            if response.status_code not in [200, 404]:
                logger.error("Qdrant não está respondendo. Inicie com:")
                logger.error("  docker-compose -f deploy/docker-compose.yml up -d qdrant")
                sys.exit(1)
        except Exception as e:
            logger.error(f"Erro ao conectar com Qdrant: {e}")
            logger.error("Certifique-se de que o Qdrant está rodando")
            sys.exit(1)

        # Executar vetorização baseada nos argumentos
        if args.stats:
            stats = vectorizer.get_stats()
            print("📊 Estatísticas da vetorização:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
            return

        if args.search:
            results = vectorizer.search_system(args.search)
            print(f"🔍 Busca: '{args.search}'")
            for result in results:
                print(f"Score: {result['score']:.3f}")
                print(f"Arquivo: {result['file_path']}")
                print(f"Conteúdo: {result['content'][:200]}...")
                print("-" * 50)
            return

        total_chunks = 0

        # Vetorização do sistema Ubuntu
        if not args.omnimind_only and not args.kernel_only:
            logger.info("🐧 Vetorizando sistema Ubuntu...")
            ubuntu_results = vectorizer.vectorize_ubuntu_system()
            ubuntu_chunks = sum(ubuntu_results.values())
            total_chunks += ubuntu_chunks
            logger.info(f"✅ Ubuntu: {len(ubuntu_results)} arquivos, {ubuntu_chunks} chunks")

        # Vetorização do projeto OmniMind
        if not args.ubuntu_only and not args.kernel_only:
            logger.info("🧠 Vetorizando projeto OmniMind...")
            omnimind_results = vectorizer.vectorize_omnimind_project(incremental=args.incremental)
            omnimind_chunks = sum(sum(stage.values()) for stage in omnimind_results.values())
            total_chunks += omnimind_chunks
            logger.info(f"✅ OmniMind: {omnimind_chunks} chunks")

        # Vetorização específica do kernel
        if args.kernel_only:
            logger.info("🧠 Vetorizando arquivos do kernel AI...")
            kernel_results = vectorizer.vectorize_kernel_files()
            kernel_chunks = sum(kernel_results.values())
            total_chunks += kernel_chunks
            logger.info(f"✅ Kernel AI: {len(kernel_results)} arquivos, {kernel_chunks} chunks")

        # Estatísticas finais
        stats = vectorizer.get_stats()
        logger.info("🎉 Vetorização concluída!")
        logger.info(f"📊 Total de chunks: {total_chunks}")
        logger.info(f"📊 Coleção: {stats.get('collection_name', 'unknown')}")
        logger.info(f"📊 Dimensão dos vetores: {stats.get('vector_dim', 'unknown')}")

        # Exemplo de busca
        logger.info("🔍 Testando busca no sistema...")
        test_queries = [
            "informações do processador",
            "configuração do kernel",
            "versão do sistema operacional",
        ]

        for query in test_queries:
            results = vectorizer.search_system(query, top_k=1)
            if results:
                logger.info(
                    f"  ✅ '{query}' -> {results[0]['file_path']} "
                    f"(score: {results[0]['score']:.3f})"
                )

    except KeyboardInterrupt:
        logger.info("⏹️ Vetorização interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Erro durante vetorização: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
