"""
Sistema de Embeddings Locais do OmniMind

Gera embeddings semânticos para múltiplos tipos de conteúdo:
- Código fonte
- Documentação técnica
- Papers científicos
- Arquivos de configuração
- Relatórios de auditoria

Armazena no Qdrant para busca semântica abrangente do projeto.
"""

import asyncio
import hashlib
import logging
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Tipos de conteúdo suportados."""

    CODE = "code"
    DOCUMENTATION = "documentation"
    PAPER = "paper"
    CONFIG = "config"
    AUDIT = "audit"
    LOG = "log"
    DATA = "data"
    MODEL = "model"
    NOTEBOOK = "notebook"
    SYSTEM = "system"


@dataclass
class ContentChunk:
    """Chunk de conteúdo com metadados."""

    file_path: str
    start_line: int
    end_line: int
    content: str
    content_type: ContentType
    language: str
    title: Optional[str] = None
    section: Optional[str] = None
    function_name: Optional[str] = None
    class_name: Optional[str] = None


class OmniMindEmbeddings:
    """
    Sistema de embeddings abrangente para o projeto OmniMind.

    Indexa múltiplos tipos de conteúdo: código, documentação, papers,
    configurações e relatórios de auditoria.
    """

    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        collection_name: str = "omnimind_embeddings",
        model_name: str = "all-MiniLM-L6-v2",
        model: Optional[SentenceTransformer] = None,
        chunk_size_code: int = 100,  # linhas para código
        chunk_size_docs: int = 50,  # linhas para documentos
        overlap: int = 20,  # sobreposição entre chunks
        gpu_memory_threshold_mb: float = 500.0,  # Threshold para forçar GPU
        batch_size_embeddings: int = 32,  # Tamanho do batch para embeddings
        enable_async_execution: bool = True,  # Habilitar execução assíncrona
    ):
        self.qdrant_url = qdrant_url
        self.collection_name = collection_name
        self.model_name = model_name
        self.chunk_size_code = chunk_size_code
        self.chunk_size_docs = chunk_size_docs
        self.overlap = overlap
        self.gpu_memory_threshold_mb = gpu_memory_threshold_mb
        self.batch_size_embeddings = batch_size_embeddings
        self.enable_async_execution = enable_async_execution

        # Verificar se PyTorch está disponível para gerenciamento de GPU
        try:
            import torch

            self.torch_available = True
            self.torch = torch
        except ImportError:
            self.torch_available = False
            self.torch = None
            logger.warning("PyTorch não disponível. Gerenciamento de GPU desabilitado.")

        # Inicializar modelo
        if model is not None:
            self.model = model
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
        else:
            from src.utils.device_utils import get_sentence_transformer_device

            # Forçar GPU se threshold for atingido ou variável de ambiente
            force_gpu = os.getenv("OMNIMIND_FORCE_GPU_EMBEDDINGS", "").lower() in (
                "true",
                "1",
                "yes",
            )
            if force_gpu:
                device = "cuda"
                logger.info("GPU forçado via OMNIMIND_FORCE_GPU_EMBEDDINGS=true")
            else:
                device = get_sentence_transformer_device(self.gpu_memory_threshold_mb)

            logger.info(f"Carregando modelo: {model_name} (device={device})")

            # Configurar para usar apenas cache local
            os.environ["HF_HUB_OFFLINE"] = "1"
            cache_path = (
                "/home/fahbrain/.cache/huggingface/hub/"
                "models--sentence-transformers--all-MiniLM-L6-v2/"
                "snapshots/c9745ed1d9f207416be6d2e6f8de32d1f16199bf"
            )

            if os.path.exists(cache_path):
                logger.info(f"Usando modelo do cache local: {cache_path}")
                self.model = SentenceTransformer(cache_path, device=device)
            else:
                logger.warning("Modelo não encontrado no cache, tentando com local_files_only...")
                self.model = SentenceTransformer(model_name, device=device, local_files_only=True)
            self.embedding_dim = int(
                self.model.get_sentence_embedding_dimension() or 384
            )  # type: ignore
            logger.info(f"Modelo carregado. Dimensões: {self.embedding_dim}")

        # Inicializar cliente Qdrant
        self.client = QdrantClient(url=qdrant_url)

        # Criar coleção se não existir
        self._ensure_collection()

        # Estatísticas de uso de GPU
        self.gpu_memory_cleared_count = 0
        self.embedding_batches_processed = 0

        # Inicializar Qdrant
        self.client = QdrantClient(qdrant_url)

        # Criar coleção se não existir
        self._ensure_collection()

    def _ensure_collection(self):
        """Cria coleção se não existir."""
        try:
            collections = self.client.get_collections().collections or []
            collection_names = [info.name for info in collections]

            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=qmodels.VectorParams(
                        size=int(self.embedding_dim or 384),
                        distance=qmodels.Distance.COSINE,
                    ),
                )
                logger.info(f"Coleção criada: {self.collection_name} (dim={self.embedding_dim})")
        except Exception as exc:
            logger.error(f"Erro ao criar coleção: {exc}")

    def _cleanup_gpu_memory(self):
        """Limpa cache de memória GPU para prevenir fragmentação."""
        if self.torch_available and self.torch.cuda.is_available():
            try:
                self.torch.cuda.empty_cache()
                self.gpu_memory_cleared_count += 1
                logger.debug(f"GPU memory cache cleared (count: {self.gpu_memory_cleared_count})")
            except Exception as e:
                logger.warning(f"Erro ao limpar cache GPU: {e}")

    def _should_force_gpu_usage(self) -> bool:
        """Verifica se deve forçar uso de GPU baseado em threshold e variáveis de ambiente."""
        # Verificar variável de ambiente
        force_gpu = os.getenv("OMNIMIND_FORCE_GPU_EMBEDDINGS", "").lower() in ("true", "1", "yes")
        if force_gpu:
            return True

        # Verificar threshold de memória
        if not self.torch_available or not self.torch.cuda.is_available():
            return False

        try:
            total_mem = self.torch.cuda.get_device_properties(0).total_memory
            allocated = self.torch.cuda.memory_allocated(0)
            free_mem = total_mem - allocated

            free_mem_mb = free_mem / (1024 * 1024)
            return free_mem_mb >= self.gpu_memory_threshold_mb
        except Exception as e:
            logger.debug(f"Erro ao verificar memória GPU: {e}")
            return False

    async def _generate_embeddings_batch_async(self, texts: List[str]) -> List[List[float]]:
        """
        Gera embeddings de forma assíncrona para prevenir fragmentação de memória GPU.

        Args:
            texts: Lista de textos para gerar embeddings

        Returns:
            Lista de embeddings (vetores)
        """
        if not self.enable_async_execution:
            # Fallback para execução síncrona
            return self._generate_embeddings_batch_sync(texts)

        try:
            # Processar em batches menores para controlar uso de memória
            all_embeddings = []

            for i in range(0, len(texts), self.batch_size_embeddings):
                batch_texts = texts[i : i + self.batch_size_embeddings]

                # Gerar embeddings do batch
                batch_embeddings = self.model.encode(
                    batch_texts, normalize_embeddings=True, batch_size=self.batch_size_embeddings
                )

                # Converter para lista se necessário
                if hasattr(batch_embeddings, "tolist"):
                    batch_embeddings = batch_embeddings.tolist()
                elif isinstance(batch_embeddings, list):
                    pass  # Já é lista
                else:
                    batch_embeddings = [
                        emb.tolist() if hasattr(emb, "tolist") else list(emb)
                        for emb in batch_embeddings
                    ]

                all_embeddings.extend(batch_embeddings)
                self.embedding_batches_processed += 1

                # Limpar cache GPU após cada batch para prevenir fragmentação
                self._cleanup_gpu_memory()

                # Pequena pausa para estabilizar GPU
                await asyncio.sleep(0.01)

            return all_embeddings

        except Exception as e:
            logger.warning(f"Erro na geração assíncrona de embeddings, usando síncrona: {e}")
            return self._generate_embeddings_batch_sync(texts)

    def _generate_embeddings_batch_sync(self, texts: List[str]) -> List[List[float]]:
        """
        Gera embeddings de forma síncrona (fallback).

        Args:
            texts: Lista de textos para gerar embeddings

        Returns:
            Lista de embeddings (vetores)
        """
        try:
            embeddings = self.model.encode(
                texts, normalize_embeddings=True, batch_size=self.batch_size_embeddings
            )

            # Converter para lista
            if hasattr(embeddings, "tolist"):
                embeddings = embeddings.tolist()
            elif isinstance(embeddings, list):
                pass
            else:
                embeddings = [
                    emb.tolist() if hasattr(emb, "tolist") else list(emb) for emb in embeddings
                ]

            self.embedding_batches_processed += 1
            return embeddings

        except Exception as e:
            logger.error(f"Erro ao gerar embeddings: {e}")
            return []

    def _index_chunks_optimized(self, chunks: List[ContentChunk], source_id: str) -> int:
        """
        Indexa chunks com otimização de GPU e processamento assíncrono.

        Args:
            chunks: Lista de chunks para indexar
            source_id: ID da fonte dos chunks

        Returns:
            Número de chunks indexados
        """
        if not chunks:
            return 0

        try:
            # Preparar textos para embedding
            texts = [chunk.content for chunk in chunks]

            # Gerar embeddings (assíncrono se habilitado)
            if self.enable_async_execution:
                # Usar asyncio para execução assíncrona
                import asyncio

                embeddings = asyncio.run(self._generate_embeddings_batch_async(texts))
            else:
                embeddings = self._generate_embeddings_batch_sync(texts)

            if len(embeddings) != len(chunks):
                logger.error(f"Discrepância: {len(embeddings)} embeddings vs {len(chunks)} chunks")
                return 0

            # Criar pontos para Qdrant
            points = []
            for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                # Criar ID único
                content_hash = hashlib.sha256(
                    f"{source_id}_{idx}_{chunk.content}".encode()
                ).hexdigest()[:16]
                point_id = int(content_hash, 16)

                # Payload com metadados
                payload = {
                    "file_path": chunk.file_path,
                    "start_line": chunk.start_line,
                    "end_line": chunk.end_line,
                    "content": chunk.content[:1000],  # Limitar tamanho
                    "content_type": chunk.content_type.value,
                    "language": chunk.language,
                    "title": chunk.title,
                    "source_id": source_id,
                }

                points.append(
                    qmodels.PointStruct(
                        id=point_id, vector=embedding, payload=payload  # type: ignore
                    )
                )

            # Upsert no Qdrant
            if points:
                self.client.upsert(
                    collection_name=self.collection_name, points=points
                )  # type: ignore
                logger.debug(f"Indexado {len(points)} chunks otimizados de {source_id}")
                return len(points)

        except Exception as e:
            logger.error(f"Erro ao indexar chunks otimizados: {e}")

        return 0

    def _ensure_collection_backup(self):
        """Cria coleção se não existir (backup/legacy)."""
        try:
            collections = self.client.get_collections().collections or []
            collection_names = [info.name for info in collections]

            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=qmodels.VectorParams(
                        size=int(self.embedding_dim or 384),
                        distance=qmodels.Distance.COSINE,
                    ),
                )
                logger.info(f"Coleção criada: {self.collection_name} (dim={self.embedding_dim})")
        except Exception as exc:
            logger.error(f"Erro ao criar coleção: {exc}")

    def _chunk_file(self, file_path: str) -> List[ContentChunk]:
        """Divide arquivo em chunks baseado no tipo de conteúdo."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            if not lines:
                return []

            # Determinar tipo de conteúdo e tamanho de chunk
            content_type = self._detect_content_type(file_path)

            # Tamanhos de chunk otimizados por tipo
            chunk_sizes = {
                ContentType.CODE: self.chunk_size_code,
                ContentType.DOCUMENTATION: self.chunk_size_docs,
                ContentType.PAPER: self.chunk_size_docs,
                ContentType.CONFIG: 50,  # Configs são menores
                ContentType.AUDIT: self.chunk_size_docs,
                ContentType.LOG: 200,  # Logs podem ser maiores
                ContentType.DATA: 100,  # Dados estruturados
                ContentType.MODEL: 10,  # Metadados de modelo são pequenos
                ContentType.NOTEBOOK: 50,  # Notebooks têm células
                ContentType.SYSTEM: 30,  # Metadados do sistema
            }

            chunk_size = chunk_sizes.get(content_type, self.chunk_size_code)

            chunks = []
            i = 0

            while i < len(lines):
                # Calcular fim do chunk
                end = min(i + chunk_size, len(lines))

                # Extrair conteúdo
                content = "".join(lines[i:end])

                # Detectar linguagem/tipo
                language = self._detect_language(file_path)

                # Criar chunk
                chunk = ContentChunk(
                    file_path=file_path,
                    start_line=i + 1,  # 1-indexed
                    end_line=end,
                    content=content,
                    content_type=content_type,
                    language=language,
                )

                chunks.append(chunk)

                # Avançar com sobreposição
                i += chunk_size - self.overlap

            return chunks

        except Exception as exc:
            logger.error(f"Erro ao processar arquivo {file_path}: {exc}")
            return []

    def _detect_content_type(self, file_path: str) -> ContentType:
        """Detecta tipo de conteúdo baseado no caminho do arquivo."""
        path = Path(file_path)

        # Verificar se é notebook
        if ".ipynb" in str(path):
            return ContentType.NOTEBOOK

        # Verificar se é modelo
        if any(part in str(path) for part in ["models/", ".pkl", ".h5", ".onnx", ".pt", ".pb"]):
            return ContentType.MODEL

        # Verificar se é log
        if any(part in str(path) for part in ["logs/", ".log", "runtime_log"]):
            return ContentType.LOG

        # Verificar se é dados
        if any(part in str(path) for part in ["data/", ".json", ".jsonl", ".csv", ".parquet"]):
            return ContentType.DATA

        # Verificar se é metadados do sistema
        if "system://" in str(path):
            return ContentType.SYSTEM

        # Verificar se é documentação
        if any(part in str(path) for part in ["docs/", "papers/", "audit/", "README", "ROADMAP"]):
            if "papers/" in str(path):
                return ContentType.PAPER
            elif "audit/" in str(path):
                return ContentType.AUDIT
            else:
                return ContentType.DOCUMENTATION

        # Verificar se é configuração
        if any(
            part in str(path)
            for part in ["config/", ".yaml", ".yml", ".toml", ".json", ".ini", ".cfg"]
        ):
            return ContentType.CONFIG

        # Default: código
        return ContentType.CODE

    def _detect_language(self, file_path: str) -> str:
        """Detecta linguagem baseada na extensão."""
        ext = Path(file_path).suffix.lower()
        mapping = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".go": "go",
            ".rs": "rust",
            ".php": "php",
            ".rb": "ruby",
            ".md": "markdown",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".toml": "toml",
            ".ini": "ini",
            ".cfg": "config",
            ".sh": "bash",
            ".sql": "sql",
            ".ipynb": "notebook",
            ".html": "html",
            ".css": "css",
            ".vue": "vue",
            ".svelte": "svelte",
            ".log": "log",
            ".csv": "csv",
            ".parquet": "parquet",
        }
        return mapping.get(ext, "unknown")

    def index_file(self, file_path: str) -> int:
        """Indexa um arquivo de qualquer tipo suportado."""
        logger.info(f"Indexando arquivo: {file_path}")

        # Verificar se arquivo existe
        if not os.path.exists(file_path):
            logger.error(f"Arquivo não encontrado: {file_path}")
            return 0

        # Dividir em chunks
        chunks = self._chunk_file(file_path)
        if not chunks:
            logger.warning(f"Nenhum chunk gerado para {file_path}")
            return 0

        # Usar indexação otimizada com GPU
        count = self._index_chunks_optimized(chunks, f"file_{Path(file_path).name}")
        if count > 0:
            logger.info(f"Indexado {count} chunks de {file_path}")
        return count

    def _needs_reindexing(self, file_path: str) -> bool:
        """Verifica se um arquivo precisa ser reindexado baseado no timestamp."""
        try:
            # Buscar pontos existentes para este arquivo
            search_result = self.client.query_points(
                collection_name=self.collection_name,
                query=[0.0] * self.embedding_dim,  # Query dummy
                query_filter=qmodels.Filter(
                    must=[
                        qmodels.FieldCondition(
                            key="file_path",
                            match=qmodels.MatchValue(value=file_path),  # type: ignore
                        )
                    ]
                ),
                limit=1,
                with_payload=True,
            )

            if not search_result.points:
                return True  # Arquivo nunca foi indexado

            # Verificar timestamp de modificação
            file_mtime = os.path.getmtime(file_path)
            stored_mtime = search_result.points[0].payload.get("modified_time", 0)

            return file_mtime > stored_mtime

        except Exception as exc:
            logger.warning(f"Erro ao verificar reindexação para {file_path}: {exc}")
            return True  # Em caso de erro, reindexar

    def index_directory_simple(
        self,
        directory: str,
        extensions: Optional[List[str]] = None,
        incremental: bool = False,
        skip_patterns: Optional[List[str]] = None,
        min_file_size: int = 10,
    ) -> Dict[str, int]:
        """Indexa todos os arquivos suportados em um diretório (versão simples)."""
        if extensions is None:
            # Extensões para código
            extensions = [".py", ".js", ".ts", ".java", ".cpp", ".c", ".go", ".rs"]

        results = {}
        directory_path = Path(directory)

        # Coletar todos os arquivos primeiro
        all_files = []
        for ext in extensions:
            for file_path in directory_path.rglob(f"*{ext}"):
                if file_path.is_file():
                    # Aplicar filtros
                    file_str = str(file_path)

                    # Pular padrões especificados
                    if skip_patterns:
                        if any(pattern in file_str for pattern in skip_patterns):
                            continue

                    # Verificar tamanho mínimo
                    try:
                        if file_path.stat().st_size < min_file_size:
                            continue
                    except OSError:
                        continue  # Pular arquivos com problemas de acesso

                    all_files.append(file_str)

        if not all_files:
            return results

        logger.info(f"📁 Indexando {len(all_files)} arquivos em {directory}")

        # Processar arquivos em paralelo dentro do diretório
        def process_file_batch(file_batch: List[str]) -> Dict[str, int]:
            """Processa um batch de arquivos."""
            batch_results = {}
            for file_path in file_batch:
                try:
                    if incremental and not self._needs_reindexing(file_path):
                        logger.debug(f"Pulando {file_path} (não modificado)")
                        continue
                    count = self.index_file(file_path)
                    batch_results[file_path] = count
                except Exception as e:
                    logger.warning(f"Erro ao indexar {file_path}: {e}")
                    batch_results[file_path] = 0
            return batch_results

        # Dividir arquivos em batches para processamento paralelo
        batch_size = max(10, len(all_files) // 20)  # Ajustar batch size dinamicamente
        file_batches = [all_files[i : i + batch_size] for i in range(0, len(all_files), batch_size)]

        logger.info(f"📦 Processando em {len(file_batches)} batches de ~{batch_size} arquivos cada")

        # Processar batches em paralelo
        with ThreadPoolExecutor(max_workers=min(8, len(file_batches))) as executor:
            future_to_batch = {
                executor.submit(process_file_batch, batch): batch for batch in file_batches
            }

            for future in future_to_batch:
                try:
                    batch_results = future.result(timeout=300)  # 5 min timeout por batch
                    results.update(batch_results)
                except Exception as e:
                    logger.warning(f"Erro ao processar batch: {e}")

        logger.info(f"✅ Concluído: {len(results)} arquivos processados em {directory}")
        return results

    def index_omnimind_project(
        self,
        project_root: str,
        max_workers: int = 8,
        incremental: bool = False,
        skip_patterns: Optional[List[str]] = None,
        min_file_size: int = 10,
        stages: Optional[List[str]] = None,
        checkpoint_file: str = ".omnimind_embedding_checkpoint.json",
        cycle_min: Optional[int] = None,
        cycle_max: Optional[int] = None,
        no_mark_complete: bool = False,
    ) -> Dict[str, Dict[str, int]]:
        """
        Indexa todo o projeto OmniMind: código, documentação, papers, auditoria,
        dados, logs, modelos, notebooks, etc.

        Args:
            project_root: Caminho raiz do projeto
            max_workers: Número máximo de workers para paralelização
            incremental: Se True, só indexa arquivos modificados desde última indexação
            skip_patterns: Lista de padrões para pular arquivos (ex: ['node_modules'])
            min_file_size: Tamanho mínimo de arquivo em bytes
            stages: Lista de etapas a executar (None = todas as etapas)
            checkpoint_file: Arquivo para salvar checkpoints de progresso
            cycle_min: Número mínimo do ciclo para arquivos integration_loop_cycle_*.json
            cycle_max: Número máximo do ciclo para arquivos integration_loop_cycle_*.json
        """
        project_path = Path(project_root)
        results = {}

        # Carregar checkpoint se existir
        checkpoint_path = project_path / checkpoint_file
        completed_stages = set()
        if checkpoint_path.exists():
            try:
                import json

                with open(checkpoint_path, "r") as f:
                    checkpoint_data = json.load(f)
                    completed_stages = set(checkpoint_data.get("completed_stages", []))
                logger.info(f"📋 Checkpoint carregado: {len(completed_stages)} etapas concluídas")
            except Exception as e:
                logger.warning(f"Erro ao carregar checkpoint: {e}")

        if incremental:
            logger.info("🔄 Iniciando indexação incremental do projeto OmniMind")
        else:
            logger.info("🚀 Iniciando indexação completa do projeto OmniMind")

        # Definir etapas de indexação em ordem de prioridade
        all_stages = {
            # Etapa 1: Arquivos principais do projeto (sem ruídos)
            "core_code": {
                "name": "Código Principal",
                "dirs": ["src"],
                "extensions": [".py", ".js", ".ts", ".java", ".cpp", ".c", ".go", ".rs", ".sh"],
                "description": "Código fonte principal do sistema",
            },
            "tests": {
                "name": "Testes",
                "dirs": ["tests"],
                "extensions": [".py"],
                "description": "Arquivos de teste",
            },
            "scripts": {
                "name": "Scripts",
                "dirs": ["scripts"],
                "extensions": [".py", ".sh", ".bash"],
                "description": "Scripts de automação e desenvolvimento",
            },
            "configs": {
                "name": "Configurações",
                "dirs": ["config"],
                "extensions": [".yaml", ".yml", ".json", ".toml", ".ini", ".conf"],
                "description": "Arquivos de configuração",
            },
            "datasets": {
                "name": "Datasets",
                "dirs": ["datasets"],
                "extensions": [".json", ".jsonl", ".csv", ".txt"],
                "description": "Datasets de treinamento e validação",
            },
            "deploy": {
                "name": "Deploy",
                "dirs": ["deploy"],
                "extensions": [".yml", ".yaml", ".sh", ".dockerfile", ".Dockerfile"],
                "description": "Configurações de deployment",
            },
            "docs": {
                "name": "Documentação",
                "dirs": ["docs"],
                "extensions": [".md", ".txt", ".rst", ".adoc"],
                "description": "Documentação do projeto",
            },
            "archive": {
                "name": "Arquivo",
                "dirs": ["archive"],
                "extensions": [".md", ".txt", ".json", ".log"],
                "description": "Arquivos arquivados",
            },
            # Etapa 2: Ruídos controlados
            "logs_main": {
                "name": "Logs Principais",
                "dirs": ["logs"],
                "extensions": [".log", ".txt"],
                "skip_patterns": ["node_modules", "__pycache__", ".git"],
                "description": "Logs principais (excluindo ruídos)",
            },
            "node_modules_main": {
                "name": "Node Modules Principais",
                "dirs": ["node_modules"],
                "extensions": [".json", ".js", ".ts", ".md"],
                "max_files_per_dir": 100,
                "description": "Principais arquivos de node_modules (limitado)",
            },
            # Etapa 3: Dados produzidos pelo sistema
            "data_core": {
                "name": "Dados Core",
                "dirs": ["data"],
                "extensions": [".json", ".jsonl", ".yaml", ".yml"],
                "skip_dirs": ["reports/modules", "reports/logs"],
                "description": "Dados core do sistema (excluindo módulos massivos)",
            },
            "data_core_alerts": {
                "name": "Dados Core - Alertas",
                "dirs": ["data/alerts"],
                "extensions": [".json", ".jsonl", ".yaml", ".yml"],
                "description": "Dados de alertas do sistema",
            },
            "data_core_autopoietic": {
                "name": "Dados Core - Autopoiese",
                "dirs": ["data/autopoietic"],
                "extensions": [".json", ".jsonl", ".yaml", ".yml"],
                "description": "Dados autopoéticos do sistema",
            },
            "data_core_backup": {
                "name": "Dados Core - Backup",
                "dirs": ["data/backup"],
                "extensions": [".json", ".jsonl", ".yaml", ".yml"],
                "description": "Dados de backup do sistema",
            },
            "data_core_benchmarks": {
                "name": "Dados Core - Benchmarks",
                "dirs": ["data/benchmarks"],
                "extensions": [".json", ".jsonl", ".yaml", ".yml"],
                "description": "Dados de benchmarks do sistema",
            },
            "data_core_consciousness": {
                "name": "Dados Core - Consciência",
                "dirs": ["data/consciousness"],
                "extensions": [".json", ".jsonl", ".yaml", ".yml"],
                "description": "Dados de consciência do sistema",
            },
            "data_core_context": {
                "name": "Dados Core - Contexto",
                "dirs": ["data/context"],
                "extensions": [".json", ".jsonl", ".yaml", ".yml"],
                "description": "Dados de contexto do sistema",
            },
            "data_core_datasets": {
                "name": "Dados Core - Datasets",
                "dirs": ["data/datasets"],
                "extensions": [".json", ".jsonl", ".yaml", ".yml"],
                "description": "Datasets do sistema",
            },
            "data_core_ethics": {
                "name": "Dados Core - Ética",
                "dirs": ["data/ethics"],
                "extensions": [".json", ".jsonl", ".yaml", ".yml"],
                "description": "Dados éticos do sistema",
            },
            "data_core_experiments": {
                "name": "Dados Core - Experimentos",
                "dirs": ["data/experiments"],
                "extensions": [".json", ".jsonl", ".yaml", ".yml"],
                "description": "Dados de experimentos do sistema",
            },
            "data_core_forensics": {
                "name": "Dados Core - Forense",
                "dirs": ["data/forensics"],
                "extensions": [".json", ".jsonl", ".yaml", ".yml"],
                "description": "Dados forenses do sistema",
            },
            "data_core_integrity_baselines": {
                "name": "Dados Core - Baselines de Integridade",
                "dirs": ["data/integrity_baselines"],
                "extensions": [".json", ".jsonl", ".yaml", ".yml"],
                "description": "Baselines de integridade do sistema",
            },
            "data_core_long_term_logs": {
                "name": "Dados Core - Logs de Longo Prazo",
                "dirs": ["data/long_term_logs"],
                "extensions": [".json", ".jsonl", ".yaml", ".yml"],
                "description": "Logs de longo prazo do sistema",
            },
            "data_core_metrics": {
                "name": "Dados Core - Métricas",
                "dirs": ["data/metrics"],
                "extensions": [".json", ".jsonl", ".yaml", ".yml"],
                "description": "Métricas do sistema",
            },
            "data_core_ml": {
                "name": "Dados Core - Machine Learning",
                "dirs": ["data/ml"],
                "extensions": [".json", ".jsonl", ".yaml", ".yml"],
                "description": "Dados de machine learning do sistema",
            },
            "data_core_monitor": {
                "name": "Dados Core - Monitoramento",
                "dirs": ["data/monitor"],
                "extensions": [".json", ".jsonl", ".yaml", ".yml"],
                "description": "Dados de monitoramento do sistema",
            },
            "data_core_qdrant": {
                "name": "Dados Core - Qdrant",
                "dirs": ["data/qdrant"],
                "extensions": [".json", ".jsonl", ".yaml", ".yml"],
                "description": "Dados do Qdrant",
            },
            "data_core_reports_small": {
                "name": "Dados Core - Relatórios Pequenos",
                "dirs": ["data/reports"],
                "extensions": [".json", ".jsonl", ".yaml", ".yml"],
                "skip_dirs": ["reports/modules"],
                "description": "Relatórios pequenos (excluindo módulos massivos)",
            },
            "data_core_research": {
                "name": "Dados Core - Pesquisa",
                "dirs": ["data/research"],
                "extensions": [".json", ".jsonl", ".yaml", ".yml"],
                "description": "Dados de pesquisa do sistema",
            },
            "data_core_sessions": {
                "name": "Dados Core - Sessões",
                "dirs": ["data/sessions"],
                "extensions": [".json", ".jsonl", ".yaml", ".yml"],
                "description": "Dados de sessões do sistema",
            },
            "data_core_stimulation": {
                "name": "Dados Core - Estimulação",
                "dirs": ["data/stimulation"],
                "extensions": [".json", ".jsonl", ".yaml", ".yml"],
                "description": "Dados de estimulação do sistema",
            },
            "data_core_test_reports": {
                "name": "Dados Core - Relatórios de Teste",
                "dirs": ["data/test_reports"],
                "extensions": [".json", ".jsonl", ".yaml", ".yml"],
                "description": "Relatórios de teste do sistema",
            },
            "data_core_training": {
                "name": "Dados Core - Treinamento",
                "dirs": ["data/training"],
                "extensions": [".json", ".jsonl", ".yaml", ".yml"],
                "description": "Dados de treinamento do sistema",
            },
            "data_core_validation": {
                "name": "Dados Core - Validação",
                "dirs": ["data/validation"],
                "extensions": [".json", ".jsonl", ".yaml", ".yml"],
                "description": "Dados de validação do sistema",
            },
            "data_reports": {
                "name": "Relatórios",
                "dirs": ["reports"],
                "extensions": [".md", ".txt", ".json", ".html"],
                "skip_dirs": ["reports/modules"],
                "description": "Relatórios do sistema",
            },
            # Etapa 4: Arquivos kernel e sistema
            "kernel_files": {
                "name": "Arquivos Kernel",
                "dirs": ["kernel_ai", "quantum_ai", "neurosymbolic"],
                "extensions": [".py", ".md", ".txt"],
                "description": "Arquivos relacionados ao kernel AI",
            },
            "system_metadata": {
                "name": "Metadados Sistema",
                "dirs": [],
                "extensions": [],
                "description": "Metadados do sistema operacional",
            },
            # Etapa 5: Dados massivos (última prioridade)
            "data_modules": {
                "name": "Módulos de Dados",
                "dirs": ["data/reports/modules"],
                "extensions": [".json"],
                "batch_size": 1000,
                "max_workers": 2,
                "description": "Arquivos massivos de módulos (baixa prioridade)",
            },
            "exports": {
                "name": "Exports",
                "dirs": ["exports"],
                "extensions": [".json", ".csv", ".txt", ".md"],
                "description": "Arquivos de export",
            },
            "tmp": {
                "name": "Temporários",
                "dirs": ["tmp"],
                "extensions": [".txt", ".log", ".json"],
                "description": "Arquivos temporários",
            },
        }

        # Filtrar etapas a executar
        if stages:
            stages_to_run = [s for s in stages if s in all_stages]
        else:
            stages_to_run = list(all_stages.keys())

        # Executar etapas
        for stage_name in stages_to_run:
            if stage_name in completed_stages:
                logger.info(f"⏭️ Etapa '{stage_name}' já concluída, pulando...")
                continue

            stage_config = all_stages[stage_name]
            logger.info(f"📋 Executando etapa: {stage_config['name']} ({stage_name})")
            logger.info(f"   {stage_config['description']}")

            stage_results = {}

            # Indexar arquivos raiz importantes (apenas na primeira etapa)
            if stage_name == "core_code":
                logger.info("📋 Indexando arquivos raiz...")
                root_files = [
                    "README.md",
                    "ROADMAP.md",
                    "ROADMAP_PHASE_23_FUNDING.md",
                    "CHANGELOG.md",
                    "CONTRIBUTING.md",
                    "LICENSE",
                    "CITATION.cff",
                    "pyproject.toml",
                    "pytest.ini",
                    "mypy.ini",
                    "sonar-project.properties",
                    "requirements.txt",
                    "requirements-dev.txt",
                    "requirements-minimal.txt",
                ]
                for filename in root_files:
                    file_path = project_path / filename
                    if file_path.exists():
                        if incremental and not self._needs_reindexing(str(file_path)):
                            logger.info(f"  Pulando {filename} (não modificado)")
                            continue
                        count = self.index_file(str(file_path))
                        stage_results[f"root_{filename}"] = count

            # Indexar diretórios da etapa
            for dir_name in stage_config["dirs"]:
                dir_path = project_path / dir_name
                if dir_path.exists():
                    logger.info(f"  📁 Indexando {dir_name}...")

                    # Configurações específicas da etapa
                    stage_max_workers = stage_config.get("max_workers", max_workers)
                    stage_batch_size = stage_config.get("batch_size", None)
                    stage_skip_patterns = stage_config.get("skip_patterns", skip_patterns or [])
                    stage_skip_dirs = stage_config.get("skip_dirs", [])

                    # Aplicar filtros de diretório
                    if any(skip_dir in str(dir_path) for skip_dir in stage_skip_dirs):
                        logger.info(f"    Pulando diretório {dir_path} (skip_dirs)")
                        continue

                    # Indexar diretório
                    dir_results = self.index_directory(
                        str(dir_path),
                        stage_config["extensions"],
                        incremental,
                        stage_skip_patterns,
                        min_file_size,
                        max_workers_override=stage_max_workers,
                        batch_size_override=stage_batch_size,
                        cycle_min=cycle_min,
                        cycle_max=cycle_max,
                    )
                    stage_results.update(dir_results)

            # Indexar metadados do sistema (apenas na etapa específica)
            if stage_name == "system_metadata":
                logger.info("🖥️ Indexando metadados do sistema...")
                system_results = self.index_system_metadata()
                stage_results.update(system_results)

            # Salvar resultados da etapa
            results[stage_name] = stage_results

            # Salvar checkpoint (exceto para reports_small quando no_mark_complete=True)
            should_mark_complete = not (
                no_mark_complete and stage_name == "data_core_reports_small"
            )
            if should_mark_complete:
                completed_stages.add(stage_name)
                self._save_checkpoint(checkpoint_path, completed_stages, results)
                logger.info(
                    f"✅ Etapa '{stage_name}' concluída: {sum(stage_results.values())} chunks"
                )
            else:
                # Salvar checkpoint sem marcar como concluída
                self._save_checkpoint(checkpoint_path, completed_stages, results)
                logger.info(
                    f"✅ Etapa '{stage_name}' processada "
                    f"(não marcada como concluída): {sum(stage_results.values())} chunks"
                )

        return results

    def _save_checkpoint(
        self, checkpoint_path: Path, completed_stages: set, results: Dict[str, Dict[str, int]]
    ):
        """Salva checkpoint do progresso de indexação."""
        try:
            import json
            from datetime import datetime

            # Carregar dados existentes se o arquivo existir
            existing_data = {}
            if checkpoint_path.exists():
                try:
                    with open(checkpoint_path, "r") as f:
                        existing_data = json.load(f)
                except Exception as e:
                    logger.warning(f"Erro ao carregar checkpoint existente: {e}")

            # Combinar dados existentes com novos
            all_completed_stages = set(existing_data.get("completed_stages", [])) | completed_stages
            all_results = existing_data.get("results_summary", {})
            all_results.update(
                {
                    stage: sum(stage_results.values()) if isinstance(stage_results, dict) else 0
                    for stage, stage_results in results.items()
                }
            )

            checkpoint_data = {
                "timestamp": datetime.now().isoformat(),
                "completed_stages": list(all_completed_stages),
                "results_summary": all_results,
                "total_chunks": sum(all_results.values()),
            }

            with open(checkpoint_path, "w") as f:
                json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)

            logger.info(
                f"💾 Checkpoint salvo: {len(all_completed_stages)} etapas concluídas, "
                f"{checkpoint_data['total_chunks']} chunks totais"
            )

        except Exception as e:
            logger.warning(f"Erro ao salvar checkpoint: {e}")

    def index_directory(
        self,
        directory: str,
        extensions: List[str],
        incremental: bool = False,
        skip_patterns: Optional[List[str]] = None,
        min_file_size: int = 10,
        max_workers_override: Optional[int] = None,
        batch_size_override: Optional[int] = None,
        cycle_min: Optional[int] = None,
        cycle_max: Optional[int] = None,
    ) -> Dict[str, int]:
        """
        Indexa um diretório recursivamente com paralelização intra-diretório.

        Args:
            directory: Caminho do diretório
            extensions: Lista de extensões de arquivo a indexar
            incremental: Se True, só indexa arquivos modificados
            skip_patterns: Padrões de arquivo/diretório para pular
            min_file_size: Tamanho mínimo de arquivo em bytes
            max_workers_override: Override do número máximo de workers
            batch_size_override: Override do tamanho do batch
        """
        directory_path = Path(directory)
        results = {}

        # Usar overrides se fornecidos
        max_workers = max_workers_override if max_workers_override is not None else 4
        batch_size = batch_size_override if batch_size_override is not None else 64

        logger.info(
            f"🔍 Indexando diretório: {directory} (workers: {max_workers}, batch: {batch_size})"
        )

        # Coletar todos os arquivos primeiro
        all_files = []
        for ext in extensions:
            for file_path in directory_path.rglob(f"*{ext}"):
                if file_path.is_file():
                    # Verificar tamanho mínimo
                    if file_path.stat().st_size < min_file_size:
                        continue

                    # Verificar padrões de skip
                    if skip_patterns:
                        skip_file = False
                        file_str = str(file_path)
                        for pattern in skip_patterns:
                            if pattern in file_str:
                                skip_file = True
                                break
                        if skip_file:
                            continue

                    # Verificar se precisa reindexar (incremental)
                    if incremental and not self._needs_reindexing(str(file_path)):
                        continue

                    all_files.append(file_path)

        # Aplicar filtro de ciclo se especificado
        if cycle_min is not None or cycle_max is not None:
            filtered_files = []
            for file_path in all_files:
                file_name = file_path.name
                if "integration_loop_cycle_" in file_name and file_name.endswith(".json"):
                    try:
                        # Extrair número do ciclo do nome do arquivo
                        # Formato: integration_loop_cycle_{numero}_{timestamp}.json
                        parts = file_name.split("_")
                        if (
                            len(parts) >= 4
                            and parts[0] == "integration"
                            and parts[1] == "loop"
                            and parts[2] == "cycle"
                        ):
                            cycle_num = int(parts[3])

                            # Verificar se está dentro do intervalo
                            if cycle_min is not None and cycle_num < cycle_min:
                                continue
                            if cycle_max is not None and cycle_num > cycle_max:
                                continue

                            filtered_files.append(file_path)
                        else:
                            filtered_files.append(file_path)  # Não é arquivo de ciclo, incluir
                    except (ValueError, IndexError):
                        filtered_files.append(file_path)  # Erro no parsing, incluir
                else:
                    filtered_files.append(file_path)  # Não é arquivo de ciclo, incluir

            all_files = filtered_files
            logger.info(
                f"  Após filtro de ciclo ({cycle_min}-{cycle_max}): {len(all_files)} arquivos"
            )

        if not all_files:
            logger.info(f"  Nenhum arquivo encontrado em {directory}")
            return results

        logger.info(f"  Encontrados {len(all_files)} arquivos para indexar")

        # Processar arquivos em batches paralelos dentro do diretório
        batch_size_files = max(1, len(all_files) // max_workers)

        def process_batch(batch_files: List[Path]) -> Dict[str, int]:
            batch_results = {}
            for file_path in batch_files:
                try:
                    count = self.index_file(str(file_path))
                    batch_results[str(file_path)] = count
                except Exception as e:
                    logger.warning(f"Erro ao indexar {file_path}: {e}")
            return batch_results

        # Executar batches em paralelo
        batches = [
            all_files[i : i + batch_size_files] for i in range(0, len(all_files), batch_size_files)
        ]

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_batch = {executor.submit(process_batch, batch): batch for batch in batches}

            for future in as_completed(future_to_batch):
                batch_results = future.result()
                results.update(batch_results)

        total_chunks = sum(results.values())
        logger.info(f"  ✅ Diretório {directory}: {len(results)} arquivos, {total_chunks} chunks")

        return results
        """
        Indexa metadados do sistema/kernel da máquina para análise de como
        o OmniMind interage com configurações reais vs sandbox.
        """
        logger.info("🔧 Indexando metadados do sistema/kernel")

        results = {}

        # Comandos seguros para coletar informações do sistema
        system_commands = {
            "kernel_info": ["uname", "-a"],
            "cpu_info": ["lscpu"],
            "memory_info": ["free", "-h"],
            "disk_info": ["df", "-h"],
            "system_load": ["uptime"],
            "network_interfaces": ["ip", "addr", "show"],
            "processes_omnimind": ["ps", "aux", "|", "grep", "-i", "omnimind"],
            "python_version": ["python", "--version"],
            "pip_packages": ["pip", "list"],
            "environment_vars": ["env", "|", "grep", "-E", "(OMNIMIND|PYTHONPATH|PATH)"],
        }

        # Arquivos de sistema importantes (somente leitura)
        system_files = [
            "/proc/cpuinfo",
            "/proc/meminfo",
            "/proc/version",
            "/etc/os-release",
            "/etc/hostname",
            "/proc/sys/kernel/hostname",
        ]

        # Coletar output de comandos
        for name, cmd in system_commands.items():
            try:
                # Usar shell=True apenas para pipes
                if "|" in cmd:
                    result = subprocess.run(
                        " ".join(cmd), shell=True, capture_output=True, text=True, timeout=10
                    )
                else:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

                if result.returncode == 0:
                    content = result.stdout.strip()
                    if content:
                        # Criar chunks para conteúdo longo
                        chunks = self._chunk_text(content, f"system_{name}", ContentType.SYSTEM)
                        count = self._index_chunks_optimized(chunks, f"system_command_{name}")
                        results[f"cmd_{name}"] = count
                        logger.info(f"  Indexado comando {name}: {count} chunks")
                else:
                    logger.warning(f"Comando {name} falhou: {result.stderr}")

            except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError) as e:
                logger.warning(f"Erro ao executar comando {name}: {e}")

        # Indexar arquivos de sistema
        for file_path in system_files:
            if os.path.exists(file_path) and os.access(file_path, os.R_OK):
                try:
                    count = self.index_file(file_path)
                    results[f"file_{Path(file_path).name}"] = count
                    logger.info(f"  Indexado arquivo sistema {file_path}: {count} chunks")
                except (PermissionError, OSError) as e:
                    logger.warning(f"Erro ao indexar {file_path}: {e}")

        # Coletar informações específicas do OmniMind
        omnimind_system_info = self._collect_omnimind_system_info()
        if omnimind_system_info:
            chunks = self._chunk_text(
                omnimind_system_info, "omnimind_system_integration", ContentType.SYSTEM
            )
            count = self._index_chunks_optimized(chunks, "omnimind_system_integration")
            results["omnimind_system"] = count

        return results

    def _collect_omnimind_system_info(self) -> str:
        """Coleta informações específicas de como o OmniMind interage com o sistema."""
        info_lines = []

        # Verificar se está rodando em container/sandbox
        try:
            with open("/proc/1/cgroup", "r") as f:
                cgroup = f.read()
                if "docker" in cgroup.lower() or "containerd" in cgroup.lower():
                    info_lines.append("EXECUTION_ENVIRONMENT: Docker/Container")
                else:
                    info_lines.append("EXECUTION_ENVIRONMENT: Host System")
        except Exception:
            info_lines.append("EXECUTION_ENVIRONMENT: Unknown")

        # Verificar privilégios
        try:
            import os

            if os.geteuid() == 0:
                info_lines.append("PRIVILEGES: Root/Superuser")
            else:
                info_lines.append("PRIVILEGES: Regular User")
        except Exception:
            info_lines.append("PRIVILEGES: Unknown")

        # Verificar acesso a hardware
        try:
            import psutil

            cpu_count = psutil.cpu_count()
            memory = psutil.virtual_memory()
            info_lines.append(f"HARDWARE_ACCESS: CPU cores available: {cpu_count}")
            info_lines.append(f"HARDWARE_ACCESS: Memory available: {memory.total // (1024**3)}GB")
        except ImportError:
            info_lines.append("HARDWARE_ACCESS: psutil not available")
        except Exception:
            info_lines.append("HARDWARE_ACCESS: Error accessing hardware info")

        # Verificar configurações do Python
        try:
            import sys

            info_lines.append(f"PYTHON_CONFIG: Version {sys.version}")
            info_lines.append(f"PYTHON_CONFIG: Executable: {sys.executable}")
            info_lines.append(f"PYTHON_CONFIG: Platform: {sys.platform}")
        except Exception:
            info_lines.append("PYTHON_CONFIG: Error")

        # Verificar variáveis de ambiente relevantes
        relevant_env = {}
        for key in ["OMNIMIND_CONFIG", "PYTHONPATH", "CUDA_VISIBLE_DEVICES", "OMP_NUM_THREADS"]:
            value = os.environ.get(key)
            if value:
                relevant_env[key] = value

        if relevant_env:
            info_lines.append("ENVIRONMENT_VARS: " + str(relevant_env))
        else:
            info_lines.append("ENVIRONMENT_VARS: None relevant found")

        return "\n".join(info_lines)

    def _chunk_text(self, text: str, title: str, content_type: ContentType) -> List[ContentChunk]:
        """Cria chunks de texto puro (não de arquivo)."""
        lines = text.splitlines()
        if not lines:
            return []

        chunk_size = 50  # Para metadados do sistema
        chunks = []
        i = 0

        while i < len(lines):
            end = min(i + chunk_size, len(lines))
            content = "\n".join(lines[i:end])

            chunk = ContentChunk(
                file_path=f"system://{title}",
                start_line=i + 1,
                end_line=end,
                content=content,
                content_type=content_type,
                language="system",
                title=title,
            )

            chunks.append(chunk)
            i += chunk_size - self.overlap

        return chunks

    def _index_chunks(self, chunks: List[ContentChunk], source_id: str) -> int:
        """Indexa lista de chunks diretamente."""
        if not chunks:
            return 0

        points = []
        for idx, chunk in enumerate(chunks):
            # Gerar embedding
            embedding = self.model.encode(chunk.content, normalize_embeddings=True)

            # Criar ID único
            content_hash = hashlib.sha256(
                f"{source_id}_{idx}_{chunk.content}".encode()
            ).hexdigest()[:16]
            point_id = int(content_hash, 16)

            # Payload
            payload = {
                "file_path": chunk.file_path,
                "start_line": chunk.start_line,
                "end_line": chunk.end_line,
                "content": chunk.content[:1000],
                "content_type": chunk.content_type.value,
                "language": chunk.language,
                "title": chunk.title,
                "source_id": source_id,
            }

            points.append(
                qmodels.PointStruct(
                    id=point_id, vector=embedding.tolist(), payload=payload  # type: ignore
                )
            )

        if points:
            self.client.upsert(collection_name=self.collection_name, points=points)  # type: ignore
            return len(points)

        return 0

    def _index_docs_directory(self, directory: str) -> Dict[str, int]:
        """Indexa diretório de documentação (suporta .md, .txt, etc.)"""
        results = {}
        directory_path = Path(directory)

        # Extensões de documentação
        doc_extensions = [".md", ".txt", ".rst", ".adoc"]

        for ext in doc_extensions:
            for file_path in directory_path.rglob(f"*{ext}"):
                if file_path.is_file():
                    count = self.index_file(str(file_path))
                    results[str(file_path)] = count

        return results

    def search(
        self,
        query: str,
        top_k: int = 5,
        content_types: Optional[List[ContentType]] = None,
    ) -> List[Dict[str, Any]]:
        """Busca semântica no conteúdo indexado."""
        # Gerar embedding da query
        query_embedding = self.model.encode(query, normalize_embeddings=True)

        # Filtro por tipo de conteúdo se especificado
        query_filter = None
        if content_types:
            content_type_values = [ct.value for ct in content_types]
            query_filter = qmodels.Filter(
                must=[
                    qmodels.FieldCondition(
                        key="content_type",
                        match=qmodels.MatchAny(any=content_type_values),  # type: ignore
                    )
                ]
            )

        # Buscar no Qdrant
        search_result = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding.tolist(),  # type: ignore
            query_filter=query_filter,
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
                    "start_line": payload.get("start_line", 0),
                    "end_line": payload.get("end_line", 0),
                    "content": payload.get("content", ""),
                    "content_type": payload.get("content_type", ""),
                    "language": payload.get("language", ""),
                }
            )

        return results

    def get_stats(self) -> Dict[str, Any]:
        """Estatísticas da coleção."""
        try:
            collection_info = self.client.get_collection(self.collection_name)
            gpu_info = {}
            if self.torch_available and self.torch.cuda.is_available():
                try:
                    gpu_info = {
                        "gpu_memory_threshold_mb": self.gpu_memory_threshold_mb,
                        "gpu_memory_cleared_count": self.gpu_memory_cleared_count,
                        "embedding_batches_processed": self.embedding_batches_processed,
                        "gpu_device": self.torch.cuda.get_device_name(0),
                        "gpu_memory_allocated_mb": self.torch.cuda.memory_allocated(0)
                        / (1024 * 1024),
                        "gpu_memory_reserved_mb": self.torch.cuda.memory_reserved(0)
                        / (1024 * 1024),
                    }
                except Exception as e:
                    gpu_info = {"gpu_error": str(e)}

            return {
                "collection_name": self.collection_name,
                "vector_dim": self.embedding_dim,
                "total_chunks": collection_info.points_count,
                "model": self.model_name,
                "gpu_enabled": self.torch_available and self.torch.cuda.is_available(),
                "async_execution": self.enable_async_execution,
                "batch_size_embeddings": self.batch_size_embeddings,
                **gpu_info,
            }
        except Exception as exc:
            logger.error(f"Erro ao obter stats: {exc}")
            return {"error": str(exc)}


if __name__ == "__main__":
    # Exemplo de uso
    import sys

    if len(sys.argv) < 2:
        print("Uso: python code_embeddings.py <diretório>")
        sys.exit(1)

    directory = sys.argv[1]

    # Inicializar sistema
    embeddings = OmniMindEmbeddings()

    # Indexar diretório
    print(f"Indexando código em: {directory}")
    index_results = embeddings.index_directory(directory)

    total_chunks = sum(index_results.values())
    print(f"Total de chunks indexados: {total_chunks}")

    # Mostrar stats
    stats = embeddings.get_stats()
    print(f"Stats: {stats}")

    # Exemplo de busca
    query = "função para conectar banco de dados"
    search_results = embeddings.search(query, top_k=3)
    print(f"\nBusca por: '{query}'")
    for result in search_results:
        print(f"Score: {result['score']:.3f}")
        print(f"Arquivo: {result['file_path']}:{result['start_line']}-{result['end_line']}")
        print(f"Conteúdo: {result['content'][:200]}...")
        print("-" * 50)
