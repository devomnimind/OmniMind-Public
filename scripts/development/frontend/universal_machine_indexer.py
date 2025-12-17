#!/usr/bin/env python3
"""
OmniMind Development & System Critical Indexer

Indexa apenas ambientes de desenvolvimento, plataformas e arquivos críticos do sistema/kernel.

Funcionalidades:
- Indexação de projetos de desenvolvimento
- Arquivos críticos do sistema e kernel
- Configurações de plataformas
- Estatísticas detalhadas
- Busca semântica focada
"""

import os
import sys
import logging
import hashlib
import mimetypes
import subprocess
import glob
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed

import psutil
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

# Forçar CPU para evitar problemas de memória
os.environ["CUDA_VISIBLE_DEVICES"] = ""

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

logger = logging.getLogger(__name__)


class UniversalContentType(Enum):
    """Tipos de conteúdo universais para indexação completa."""

    CODE = "code"
    DOCUMENTATION = "documentation"
    CONFIG = "config"
    DATA = "data"
    BINARY = "binary"
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    ARCHIVE = "archive"
    SYSTEM = "system"
    UNKNOWN = "unknown"


@dataclass
class UniversalContentChunk:
    """Chunk universal de qualquer tipo de conteúdo."""

    file_path: str
    content: str
    content_type: UniversalContentType
    mime_type: str
    size_bytes: int
    is_text: bool
    encoding: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class UniversalEmbeddingsIndexer:
    """
    Indexador focado em ambientes de desenvolvimento e arquivos críticos do sistema.

    Indexa apenas:
    - Projetos de desenvolvimento (código, documentação)
    - Arquivos críticos do sistema/kernel
    - Configurações de plataformas
    """

    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        collection_name: str = "development_system_embeddings",
        model_name: str = "all-MiniLM-L6-v2",
        max_file_size_mb: int = 10,  # Máximo 10MB por arquivo
        chunk_size: int = 1000,  # Caracteres por chunk
        max_workers: int = 4,  # Processamento paralelo
    ):
        self.qdrant_url = qdrant_url
        self.collection_name = collection_name
        self.model_name = model_name
        self.max_file_size_mb = max_file_size_mb
        self.chunk_size = chunk_size
        self.max_workers = max_workers

        # Inicializar modelo
        logger.info(f"Carregando modelo universal: {model_name}")
        self.model = SentenceTransformer(model_name, device="cpu")
        self.embedding_dim = self.model.get_sentence_embedding_dimension()

        # Inicializar Qdrant
        self.client = QdrantClient(qdrant_url)
        self._ensure_collection()

        # Estatísticas
        self.stats = {
            "files_processed": 0,
            "files_indexed": 0,
            "chunks_created": 0,
            "bytes_processed": 0,
            "errors": 0,
            "by_type": {},
            "by_extension": {},
        }

        # Cache de tipos MIME
        mimetypes.init()

        logger.info("🤖 Development & System Indexer inicializado")
        logger.info(f"📊 Modelo: {model_name} (dim={self.embedding_dim})")
        logger.info(f"🎯 Máximo por arquivo: {max_file_size_mb}MB")
        logger.info(f"⚡ Workers paralelos: {max_workers}")

    def _ensure_collection(self):
        """Cria coleção universal se não existir."""
        try:
            collections = self.client.get_collections().collections or []
            collection_names = [info.name for info in collections]

            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=qmodels.VectorParams(
                        size=self.embedding_dim, distance=qmodels.Distance.COSINE
                    ),
                )
                logger.info(f"📁 Coleção criada: {self.collection_name}")
        except Exception as exc:
            logger.error(f"❌ Erro ao criar coleção: {exc}")
            raise

    def detect_content_type(self, file_path: str) -> UniversalContentType:
        """Detecta tipo de conteúdo baseado em MIME type e extensão."""
        path = Path(file_path)
        ext = path.suffix.lower()

        # Detectar por MIME type
        mime_type, _ = mimetypes.guess_type(str(path))

        if mime_type:
            if mime_type.startswith("text/"):
                # Arquivos de código
                code_exts = {
                    ".py",
                    ".js",
                    ".ts",
                    ".java",
                    ".cpp",
                    ".c",
                    ".go",
                    ".rs",
                    ".php",
                    ".rb",
                    ".sh",
                    ".sql",
                }
                if ext in code_exts:
                    return UniversalContentType.CODE

                # Documentação
                doc_exts = {".md", ".txt", ".rst", ".adoc", ".pdf"}
                if ext in doc_exts:
                    return UniversalContentType.DOCUMENTATION

                # Configurações
                config_exts = {".yaml", ".yml", ".json", ".toml", ".ini", ".cfg", ".conf"}
                if ext in config_exts:
                    return UniversalContentType.CONFIG

                return UniversalContentType.TEXT

            elif mime_type.startswith("image/"):
                return UniversalContentType.IMAGE
            elif mime_type.startswith("audio/"):
                return UniversalContentType.AUDIO
            elif mime_type.startswith("video/"):
                return UniversalContentType.VIDEO
            elif mime_type in ["application/zip", "application/x-tar", "application/gzip"]:
                return UniversalContentType.ARCHIVE
            elif mime_type.startswith("application/"):
                return UniversalContentType.BINARY

        # Detectar por extensão (fallback)
        if ext in [".db", ".sqlite", ".csv", ".xlsx", ".xls"]:
            return UniversalContentType.DATA
        elif ext in [".exe", ".dll", ".so", ".dylib"]:
            return UniversalContentType.BINARY
        elif ext in [".log", ".out", ".err"]:
            return UniversalContentType.SYSTEM

        return UniversalContentType.UNKNOWN

    def can_process_file(self, file_path: str) -> bool:
        """Verifica se arquivo pode ser processado."""
        try:
            path = Path(file_path)

            # Verificar tamanho
            size_mb = path.stat().st_size / (1024 * 1024)
            if size_mb > self.max_file_size_mb:
                return False

            # Verificar se é arquivo regular
            if not path.is_file():
                return False

            # Verificar permissões
            if not os.access(path, os.R_OK):
                return False

            return True

        except Exception:
            return False

    def extract_text_content(self, file_path: str) -> Optional[str]:
        """Extrai conteúdo textual de qualquer arquivo."""
        try:
            path = Path(file_path)
            content_type = self.detect_content_type(file_path)

            # Arquivos de texto direto
            if content_type in [
                UniversalContentType.CODE,
                UniversalContentType.TEXT,
                UniversalContentType.CONFIG,
                UniversalContentType.DOCUMENTATION,
            ]:

                # Tentar diferentes encodings
                encodings = ["utf-8", "latin-1", "cp1252", "iso-8859-1"]
                for encoding in encodings:
                    try:
                        with open(path, "r", encoding=encoding) as f:
                            content = f.read()
                            # Limitar tamanho para evitar problemas de memória
                            if len(content) > 100000:  # 100KB max
                                content = content[:100000] + "...[TRUNCATED]"
                            return content
                    except UnicodeDecodeError:
                        continue

            # Arquivos PDF (se pdftotext estiver disponível)
            elif path.suffix.lower() == ".pdf":
                try:
                    result = subprocess.run(
                        ["pdftotext", "-layout", "-enc", "UTF-8", str(path), "-"],
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )
                    if result.returncode == 0:
                        return result.stdout
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    pass

            # Arquivos binários - extrair metadados
            else:
                # Para arquivos binários, criar descrição baseada em metadados
                stat = path.stat()
                mime_type, _ = mimetypes.guess_type(str(path))

                metadata = f"""
Arquivo: {path.name}
Tamanho: {stat.st_size} bytes
Tipo MIME: {mime_type or 'desconhecido'}
Modificado: {stat.st_mtime}
Permissões: {oct(stat.st_mode)}
Localização: {path.parent}
"""

                return metadata.strip()

        except Exception as e:
            logger.debug(f"Erro ao extrair conteúdo de {file_path}: {e}")

        return None

    def chunk_content(self, file_path: str) -> List[UniversalContentChunk]:
        """Divide arquivo em chunks processáveis."""
        content = self.extract_text_content(file_path)
        if not content:
            return []

        content_type = self.detect_content_type(file_path)
        path = Path(file_path)
        mime_type, _ = mimetypes.guess_type(str(path))

        # Para arquivos pequenos, um chunk só
        if len(content) <= self.chunk_size:
            return [
                UniversalContentChunk(
                    file_path=file_path,
                    content=content,
                    content_type=content_type,
                    mime_type=mime_type or "unknown",
                    size_bytes=path.stat().st_size,
                    is_text=True,
                    metadata={"chunk_index": 0, "total_chunks": 1},
                )
            ]

        # Dividir em chunks com sobreposição
        chunks = []
        overlap = min(200, self.chunk_size // 4)  # 25% de sobreposição

        i = 0
        chunk_index = 0
        total_chunks = (len(content) + self.chunk_size - overlap - 1) // (self.chunk_size - overlap)

        while i < len(content):
            end = min(i + self.chunk_size, len(content))
            chunk_content = content[i:end]

            chunks.append(
                UniversalContentChunk(
                    file_path=file_path,
                    content=chunk_content,
                    content_type=content_type,
                    mime_type=mime_type or "unknown",
                    size_bytes=path.stat().st_size,
                    is_text=True,
                    metadata={
                        "chunk_index": chunk_index,
                        "total_chunks": total_chunks,
                        "start_pos": i,
                        "end_pos": end,
                    },
                )
            )

            i += self.chunk_size - overlap
            chunk_index += 1

        return chunks

    def index_file(self, file_path: str) -> int:
        """Indexa um arquivo individual."""
        self.stats["files_processed"] += 1

        try:
            if not self.can_process_file(file_path):
                return 0

            # Criar chunks
            chunks = self.chunk_content(file_path)
            if not chunks:
                return 0

            # Gerar embeddings e armazenar
            points = []
            for chunk in chunks:
                try:
                    # Gerar embedding
                    embedding = self.model.encode(chunk.content, normalize_embeddings=True)

                    # Criar ID único
                    content_hash = hashlib.sha256(
                        f"{chunk.file_path}:{chunk.content}".encode()
                    ).hexdigest()[:16]
                    point_id = int(content_hash, 16)

                    # Payload com metadados
                    payload = {
                        "file_path": chunk.file_path,
                        "content": chunk.content[:2000],  # Limitar tamanho
                        "content_type": chunk.content_type.value,
                        "mime_type": chunk.mime_type,
                        "size_bytes": chunk.size_bytes,
                        "is_text": chunk.is_text,
                        "chunk_metadata": chunk.metadata or {},
                    }

                    points.append(
                        qmodels.PointStruct(id=point_id, vector=embedding.tolist(), payload=payload)
                    )

                except Exception as e:
                    logger.debug(f"Erro ao processar chunk de {file_path}: {e}")
                    continue

            # Upsert no Qdrant
            if points:
                self.client.upsert(collection_name=self.collection_name, points=points)

                # Atualizar estatísticas
                self.stats["files_indexed"] += 1
                self.stats["chunks_created"] += len(points)
                self.stats["bytes_processed"] += chunks[0].size_bytes

                # Estatísticas por tipo
                ct = chunks[0].content_type.value
                self.stats["by_type"][ct] = self.stats["by_type"].get(ct, 0) + 1

                # Estatísticas por extensão
                ext = Path(file_path).suffix.lower()
                self.stats["by_extension"][ext] = self.stats["by_extension"].get(ext, 0) + 1

                logger.debug(f"✅ Indexado: {file_path} ({len(points)} chunks)")
                return len(points)

        except Exception as e:
            self.stats["errors"] += 1
            logger.debug(f"❌ Erro ao indexar {file_path}: {e}")

        return 0

    def get_development_directories(self) -> List[str]:
        """Retorna diretórios de desenvolvimento focados no projeto OmniMind."""
        dev_dirs = []

        # Detectar raiz do projeto OmniMind (onde está o script)
        script_path = Path(__file__).resolve()
        project_root = script_path.parent.parent.parent.parent  # scripts/development/frontend -> root

        # Diretórios específicos do projeto OmniMind (PRIORIDADE)
        omnimind_dirs = [
            "src",
            "tests",
            "archive",
            "config",
            "data/datasets",
            "deploy",
            "scripts",
            "docs",
        ]

        for dir_name in omnimind_dirs:
            dir_path = project_root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                dev_dirs.append(str(dir_path))
                logger.info(f"✅ Diretório OmniMind encontrado: {dir_path}")

        # Diretórios adicionais de desenvolvimento (opcional, apenas se existirem)
        additional_paths = [
            "/mnt/dev_brain_clean",  # HD externo detectado
        ]

        for path in additional_paths:
            if os.path.exists(path) and os.access(path, os.R_OK):
                # Verificar se é um diretório de projeto (não indexar tudo)
                if any(
                    os.path.exists(os.path.join(path, marker))
                    for marker in [".git", "src", "package.json", "requirements.txt", "pyproject.toml"]
                ):
                    dev_dirs.append(path)
                    logger.info(f"✅ Diretório adicional encontrado: {path}")

        return sorted(set(dev_dirs))

    def get_system_critical_files(self) -> List[str]:
        """Retorna lista de arquivos críticos do sistema/kernel."""
        critical_files = []

        # Arquivos críticos do kernel e sistema
        kernel_files = [
            "/proc/version",
            "/proc/cmdline",
            "/proc/cpuinfo",
            "/proc/meminfo",
            "/proc/modules",
            "/proc/loadavg",
            "/proc/uptime",
            "/proc/version_signature",
            "/sys/kernel/version",
            "/sys/kernel/mm/ksm",
            "/boot/config-*",
            "/boot/System.map-*",
            "/usr/src/linux/.config",
            "/etc/os-release",
            "/etc/lsb-release",
            "/etc/debian_version",
            "/etc/redhat-release",
            "/etc/fstab",
            "/etc/hosts",
            "/etc/hostname",
            "/etc/resolv.conf",
            "/etc/passwd",  # Apenas estrutura, não conteúdo sensível
            "/etc/group",
            "/etc/shells",
            "/etc/environment",
            "/etc/profile",
            "/etc/bash.bashrc",
            "/etc/sysctl.conf",
            "/etc/modprobe.d/",
            "/etc/default/",
            "/var/log/dmesg",
            "/var/log/kern.log",
            "/var/log/syslog",
        ]

        # Arquivos de configuração de plataformas
        platform_configs = [
            "/etc/docker/daemon.json",
            "/etc/docker/daemon.json.d/",
            "/etc/containerd/config.toml",
            "/etc/systemd/system/",
            "/etc/systemd/user/",
            "/usr/lib/systemd/system/",
            "/etc/nginx/",
            "/etc/apache2/",
            "/etc/redis/",
            "/etc/postgresql/",
            "/etc/mysql/",
            "/etc/mongodb/",
            "/etc/qdrant/",
        ]

        all_critical = kernel_files + platform_configs

        for pattern in all_critical:
            if "*" in pattern:
                # Expandir glob patterns
                matches = glob.glob(pattern)
                critical_files.extend(matches)
            elif os.path.isfile(pattern):
                critical_files.append(pattern)
            elif os.path.isdir(pattern):
                # Adicionar todos os arquivos de texto do diretório
                try:
                    for root, dirs, files in os.walk(pattern):
                        for file in files:
                            file_path = os.path.join(root, file)
                            if self.can_process_file(file_path):
                                ext = Path(file_path).suffix.lower()
                                if ext in [".conf", ".cfg", ".ini", ".toml", ".yaml", ".yml", ".json", ".txt", ".sh"]:
                                    critical_files.append(file_path)
                except PermissionError:
                    logger.debug(f"Sem permissão para acessar: {pattern}")

        return sorted(set(critical_files))

    def index_development_and_system(self, exclude_patterns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Indexa apenas ambientes de desenvolvimento e arquivos críticos do sistema/kernel.

        Args:
            exclude_patterns: Padrões de caminho a excluir (regex)
        """
        if exclude_patterns is None:
            exclude_patterns = [
                r".*/\.git/.*",
                r".*/node_modules/.*",
                r".*/__pycache__/.*",
                r".*/\.cache/.*",
                r".*/\.venv/.*",
                r".*/venv/.*",
                r".*/env/.*",
                r".*\.pyc$",
                r".*\.pyo$",
                r".*/build/.*",
                r".*/dist/.*",
                r".*/target/.*",
                r".*/\.pytest_cache/.*",
                r".*/\.mypy_cache/.*",
            ]

        logger.info("🚀 Iniciando indexação de DESENVOLVIMENTO e SISTEMA CRÍTICO")
        logger.info("📁 Focando em: projeto OmniMind, código, kernel e configurações críticas")

        total_chunks_created = 0

        # 1. Indexar diretórios do projeto OmniMind (PRIORIDADE)
        logger.info("\n📂 Indexando diretórios do projeto OmniMind...")
        dev_dirs = self.get_development_directories()
        logger.info(f"📍 Diretórios encontrados: {len(dev_dirs)}")
        for dev_dir in dev_dirs:
            logger.info(f"   - {dev_dir}")

        for dev_dir in dev_dirs:
            logger.info(f"\n🔍 Indexando diretório: {dev_dir}")
            try:
                chunks = self._index_directory_focused(dev_dir, exclude_patterns)
                total_chunks_created += chunks
                logger.info(f"✅ {dev_dir}: {chunks} chunks criados")
            except KeyboardInterrupt:
                logger.warning(f"⏹️  Interrompido pelo usuário durante indexação de {dev_dir}")
                raise
            except MemoryError:
                logger.error(f"❌ Erro de memória ao indexar {dev_dir}")
                logger.info("💡 Tente reduzir max_workers ou processar diretórios separadamente")
                raise
            except Exception as e:
                logger.error(f"❌ Erro ao indexar {dev_dir}: {e}")
                import traceback
                logger.error(traceback.format_exc())
                logger.info("  Continuando com próximo diretório...")
                continue

        # 2. Indexar arquivos críticos do sistema/kernel (OPCIONAL - pode falhar por permissões)
        logger.info("\n🔧 Indexando arquivos críticos do sistema/kernel...")
        logger.info("⚠️  Nota: Alguns arquivos podem requerer permissões elevadas (sudo)")
        try:
            critical_files = self.get_system_critical_files()
            logger.info(f"📍 Arquivos críticos encontrados: {len(critical_files)}")

            indexed_count = 0
            for critical_file in critical_files:
                try:
                    chunks = self.index_file(critical_file)
                    total_chunks_created += chunks
                    if chunks > 0:
                        indexed_count += 1
                        if indexed_count % 10 == 0:
                            logger.info(f"  Progresso: {indexed_count}/{len(critical_files)} arquivos indexados")
                except PermissionError:
                    logger.debug(f"⚠️  Sem permissão para: {critical_file}")
                except Exception as e:
                    logger.debug(f"⚠️  Erro ao indexar {critical_file}: {e}")

            logger.info(f"✅ Arquivos críticos indexados: {indexed_count}/{len(critical_files)}")
        except Exception as e:
            logger.warning(f"⚠️  Erro ao processar arquivos críticos do sistema: {e}")
            logger.info("💡 Isso é normal se não tiver permissões sudo")

        # Estatísticas finais
        final_stats = self.get_stats()
        logger.info("\n🎉 Indexação concluída!")
        logger.info(f"📊 Total processado: {final_stats['files_processed']} arquivos")
        logger.info(f"✅ Total indexado: {final_stats['files_indexed']} arquivos")
        logger.info(f"🧩 Total chunks: {final_stats['chunks_created']}")
        logger.info(f"💾 Total bytes: {final_stats['bytes_processed'] / (1024**2):.2f} MB")

        return final_stats

    def _index_directory_focused(self, directory: str, exclude_patterns: List[str]) -> int:
        """Indexa diretório focado em arquivos de desenvolvimento."""
        chunks_created = 0

        # Extensões relevantes para desenvolvimento
        relevant_extensions = {
            ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".cpp", ".c", ".h", ".hpp",
            ".go", ".rs", ".php", ".rb", ".swift", ".kt", ".scala", ".clj",
            ".sh", ".bash", ".zsh", ".fish",
            ".md", ".txt", ".rst", ".adoc",
            ".yaml", ".yml", ".json", ".toml", ".ini", ".cfg", ".conf",
            ".sql", ".graphql", ".gql",
            ".dockerfile", ".dockerignore",
            ".gitignore", ".gitattributes",
            "Makefile", "CMakeLists.txt", "build.gradle", "pom.xml", "Cargo.toml",
            "package.json", "requirements.txt", "Pipfile", "pyproject.toml",
        }

        try:
            all_files = []
            for root, dirs, files in os.walk(directory):
                # Aplicar exclusões
                for pattern in exclude_patterns:
                    if re.search(pattern, root):
                        dirs[:] = []
                        break

                for file in files:
                    file_path = os.path.join(root, file)
                    # Verificar se é arquivo relevante
                    path_obj = Path(file_path)
                    if (
                        path_obj.suffix.lower() in relevant_extensions
                        or path_obj.name in relevant_extensions
                        or any(path_obj.name.startswith(ext) for ext in [".env", "Dockerfile", "Makefile"])
                    ):
                        all_files.append(file_path)

            logger.info(f"📂 Encontrados {len(all_files)} arquivos relevantes em {directory}")

            # Processar em lotes para evitar sobrecarga de memória
            batch_size = 500  # Processar 500 arquivos por vez
            total_batches = (len(all_files) + batch_size - 1) // batch_size
            logger.info(f"⚡ Processando {len(all_files)} arquivos em {total_batches} lotes de {batch_size}...")

            processed = 0
            for batch_num in range(total_batches):
                start_idx = batch_num * batch_size
                end_idx = min(start_idx + batch_size, len(all_files))
                batch_files = all_files[start_idx:end_idx]

                logger.info(f"  Lote {batch_num + 1}/{total_batches}: processando {len(batch_files)} arquivos...")
                logger.info(f"    Primeiros arquivos do lote: {batch_files[:3] if len(batch_files) >= 3 else batch_files}")

                try:
                    with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                        futures = {executor.submit(self.index_file, file_path): file_path for file_path in batch_files}

                        batch_processed = 0
                        for future in as_completed(futures):
                            processed += 1
                            batch_processed += 1

                            # Log de progresso mais frequente
                            if batch_processed % 10 == 0 or batch_processed == len(batch_files):
                                logger.info(f"    Lote {batch_num + 1}: {batch_processed}/{len(batch_files)} arquivos processados")

                            if processed % 50 == 0:
                                logger.info(f"    ⏳ Progresso geral: {processed}/{len(all_files)} arquivos processados ({processed*100//len(all_files)}%)")

                            try:
                                chunks = future.result(timeout=30)  # Timeout de 30s por arquivo
                                chunks_created += chunks
                                if chunks > 0 and batch_processed % 20 == 0:
                                    logger.debug(f"    ✅ {batch_processed} arquivos indexados no lote atual")
                            except TimeoutError:
                                file_path = futures[future]
                                logger.warning(f"⏱️  Timeout ao processar: {file_path}")
                            except Exception as e:
                                file_path = futures.get(future, "unknown")
                                logger.warning(f"⚠️  Erro ao processar {file_path}: {e}")

                    logger.info(f"  ✅ Lote {batch_num + 1}/{total_batches} concluído: {batch_processed} arquivos processados")

                except Exception as e:
                    logger.error(f"❌ Erro crítico no lote {batch_num + 1}: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
                    logger.info("  Continuando com próximo lote...")
                    continue

                # Pequena pausa entre lotes para evitar sobrecarga
                import time
                if batch_num < total_batches - 1:  # Não pausar no último lote
                    time.sleep(0.5)

        except Exception as e:
            logger.error(f"Erro ao indexar {directory}: {e}")

        return chunks_created


    def search_universal(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Busca semântica universal em todo o conteúdo indexado."""
        # Gerar embedding da query
        query_embedding = self.model.encode(query, normalize_embeddings=True)

        # Buscar no Qdrant
        search_result = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding.tolist(),
            limit=top_k,
            with_payload=True,
            with_vectors=False,
        )

        # Formatar resultados
        results = []
        for point in search_result.points:
            payload = point.payload or {}
            results.append(
                {
                    "score": float(point.score),
                    "file_path": payload.get("file_path", ""),
                    "content": payload.get("content", ""),
                    "content_type": payload.get("content_type", ""),
                    "mime_type": payload.get("mime_type", ""),
                    "size_bytes": payload.get("size_bytes", 0),
                    "is_text": payload.get("is_text", False),
                    "chunk_metadata": payload.get("chunk_metadata", {}),
                }
            )

        return results

    def get_stats(self) -> Dict[str, Any]:
        """Estatísticas detalhadas da indexação."""
        try:
            collection_info = self.client.get_collection(self.collection_name)
            base_stats = {
                "collection_name": self.collection_name,
                "vector_dim": self.embedding_dim,
                "total_chunks": collection_info.points_count,
                "model": self.model_name,
            }
        except Exception:
            base_stats = {"error": "Não foi possível obter stats da coleção"}

        # Combinar com stats locais
        base_stats.update(self.stats)
        return base_stats


def main():
    """Função principal para indexação completa."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    logger.info("🤖 OMNIMIND - Indexação de Desenvolvimento e Sistema Crítico")
    logger.info("=" * 60)

    # Verificar dependências
    try:
        import sentence_transformers
        import qdrant_client
        import psutil

        logger.info("✅ Dependências OK")
    except ImportError as e:
        logger.error(f"❌ Dependência faltando: {e}")
        sys.exit(1)

    # Verificar Qdrant
    try:
        client = QdrantClient("http://localhost:6333")
        collections = client.get_collections()
        logger.info("✅ Qdrant OK")
    except Exception as e:
        logger.error(f"❌ Qdrant inacessível: {e}")
        logger.error("💡 Execute: docker run -p 6333:6333 qdrant/qdrant")
        sys.exit(1)

    # Inicializar indexador universal
    indexer = UniversalEmbeddingsIndexer()

    # Indexar desenvolvimento e sistema crítico
    try:
        logger.info("🚀 Iniciando indexação de DESENVOLVIMENTO e SISTEMA...")
        logger.info("📁 Focando em: projetos, código, kernel e configurações")
        logger.info("💡 Dica: Se o script for interrompido, pode executar novamente - ele continua de onde parou")

        stats = indexer.index_development_and_system()

        logger.info("\n🎉 Indexação concluída!")
        logger.info("📊 Estatísticas finais:")
        for key, value in stats.items():
            if isinstance(value, dict):
                logger.info(f"   {key}:")
                for subkey, subvalue in value.items():
                    logger.info(f"      {subkey}: {subvalue}")
            else:
                logger.info(f"   {key}: {value}")

    except KeyboardInterrupt:
        logger.info("\n⏹️  Indexação interrompida pelo usuário (Ctrl+C)")
        stats = indexer.get_stats()
        logger.info("📊 Estatísticas parciais salvas")
        logger.info("💡 Execute novamente para continuar a indexação")

    except MemoryError:
        logger.error("\n❌ Erro de memória! Tente reduzir max_workers ou processar diretórios separadamente")
        stats = indexer.get_stats()
        logger.info("📊 Estatísticas parciais salvas")
        sys.exit(1)

    except Exception as e:
        logger.error(f"\n❌ Erro durante indexação: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        stats = indexer.get_stats()
        logger.info("📊 Estatísticas parciais salvas")
        logger.info("💡 Execute novamente para continuar")
        sys.exit(1)

    # Teste de busca
    try:
        logger.info("\n🔍 Testando busca universal...")
        test_queries = [
            "sistema de arquivos Linux",
            "configuração de rede",
            "código Python para machine learning",
            "documentação de API",
        ]

        for query in test_queries:
            logger.info(f"\n🔎 '{query}':")
            results = indexer.search_universal(query, top_k=3)

            for i, result in enumerate(results, 1):
                logger.info(f"   {i}. [{result['content_type']}] {result['file_path']}")
                logger.info(f"      Score: {result['score']:.3f}")
                logger.info(f"      Conteúdo: {result['content'][:100]}...")

    except Exception as e:
        logger.error(f"❌ Erro no teste de busca: {e}")

    logger.info("\n🎯 Sistema pronto para buscas semânticas focadas!")
    logger.info("\n💡 Uso:")
    logger.info("   from universal_machine_indexer import UniversalEmbeddingsIndexer")
    logger.info("   indexer = UniversalEmbeddingsIndexer()")
    logger.info("   results = indexer.search_universal('sua consulta')")


if __name__ == "__main__":
    main()
