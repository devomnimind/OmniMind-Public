from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from collections import OrderedDict
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from chromadb import Client
from chromadb.config import Settings
from chromadb.utils import embedding_functions

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

AlertCallback = Callable[[str], None]


class AgenticMemory:
    def __init__(
        self,
        client: Optional[Client] = None,
        persist_directory: Optional[str] = None,
        embedding_function: Optional[Any] = None,
        cache_limit: int = 64,
        alert_callback: Optional[AlertCallback] = None,
    ) -> None:
        settings_kwargs: dict = {}
        if persist_directory:
            settings_kwargs["persist_directory"] = persist_directory
        settings = Settings(**settings_kwargs)
        self.client = client or Client(settings=settings)
        self.embedding_function = (
            embedding_function or embedding_functions.DefaultEmbeddingFunction()
        )
        self._collections: Dict[str, Any] = {}
        self.episodic = self._get_collection("episodic")
        self.semantic = self._get_collection("semantic")
        self.procedural = self._get_collection("procedural")
        self.alert_callback = alert_callback
        self.alerts: List[str] = []
        self._query_cache: OrderedDict[str, List[Dict[str, Any]]] = OrderedDict()
        self._cache_limit = cache_limit
        self.cache_hits = 0
        self.version_counter = 0

    def _get_collection(self, name: str) -> Any:
        if name in self._collections:
            return self._collections[name]
        collection = self.client.get_or_create_collection(
            name, embedding_function=self.embedding_function
        )
        self._collections[name] = collection
        return collection

    async def store_episode(self, episode: Dict[str, Any]) -> str:
        self.version_counter += 1
        collection = self.episodic
        episode_id = hashlib.md5(
            f"{episode.get('task', '')}_{datetime.now().timestamp()}".encode()
        ).hexdigest()
        document = json.dumps(episode, ensure_ascii=False)
        metadata = {
            "type": "episode",
            "task": episode.get("task", ""),
            "status": episode.get("status", "success"),
            "version": self.version_counter,
            "timestamp": episode.get("timestamp", datetime.now().isoformat()),
        }
        await self._run_in_thread(
            collection.add, ids=[episode_id], documents=[document], metadatas=[metadata]
        )
        return episode_id

    async def extract_semantic(self, text: str, context: str = "") -> str:
        collection = self.semantic
        concept_id = hashlib.md5(f"{text}_{context}".encode()).hexdigest()
        metadata = {
            "type": "semantic",
            "source_context": context,
            "text_length": len(text),
            "timestamp": datetime.now().isoformat(),
        }
        await self._run_in_thread(
            collection.add, ids=[concept_id], documents=[text], metadatas=[metadata]
        )
        return concept_id

    async def store_procedure(self, problem: str, solution: str) -> str:
        collection = self.procedural
        proc_id = hashlib.md5(f"{problem}_{solution}".encode()).hexdigest()
        procedure = {
            "problem": problem,
            "solution": solution,
            "script": f"# Auto-generated fix\n# Problem: {problem}\n# Solution: {solution}",
        }
        metadata = {
            "type": "procedure",
            "problem_hash": hashlib.md5(problem.encode()).hexdigest(),
            "created_at": datetime.now().isoformat(),
        }
        await self._run_in_thread(
            collection.add,
            ids=[proc_id],
            documents=[json.dumps(procedure)],
            metadatas=[metadata],
        )
        return proc_id

    async def query_similar_episodes(
        self, task: str, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        if task in self._query_cache:
            self.cache_hits += 1
            return self._query_cache[task]
        collection = self.episodic
        results = await self._run_in_thread(
            collection.query, query_texts=[task], n_results=top_k
        )
        stored: List[Dict[str, Any]] = []
        ids = results.get("ids", [[]])[0]
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        for item_id, doc, metadata in zip(ids, documents, metadatas):
            stored.append({"id": item_id, "document": doc, "metadata": metadata})
        self._query_cache[task] = stored
        if len(self._query_cache) > self._cache_limit:
            self._query_cache.popitem(last=False)
        return stored

    async def query_procedures(
        self, problem: str, top_k: int = 3
    ) -> List[Dict[str, Any]]:
        collection = self.procedural
        results = await self._run_in_thread(
            collection.query, query_texts=[problem], n_results=top_k
        )
        stored: List[Dict[str, Any]] = []
        for item_id, doc in zip(
            results.get("ids", [[]])[0], results.get("documents", [[]])[0]
        ):
            try:
                stored.append(json.loads(doc))
            except json.JSONDecodeError:
                stored.append({"id": item_id, "document": doc})
        return stored

    async def consolidate_memory(self) -> Dict[str, Any]:
        episodes = await self._run_in_thread(self.episodic.get)
        unique_tasks = set()
        duplicate_count = 0
        for metadata in episodes.get("metadatas", []):
            task = metadata.get("task", "")
            if task in unique_tasks:
                duplicate_count += 1
            else:
                unique_tasks.add(task)
        self.version_counter += 1
        summary = {
            "total_episodes": len(episodes.get("ids", [])),
            "unique_tasks": len(unique_tasks),
            "duplicates_removed": duplicate_count,
            "version": self.version_counter,
            "consolidation_timestamp": datetime.now().isoformat(),
        }
        return summary

    async def cache_info(self) -> Dict[str, int]:
        return {"cache_hits": self.cache_hits, "active_cache": len(self._query_cache)}

    async def _run_in_thread(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        try:
            return await asyncio.to_thread(func, *args, **kwargs)
        except Exception as exc:
            self._record_alert(f"Memory operation failed: {exc}")
            logger.error("Memory operation failure", exc_info=True)
            raise

    def _record_alert(self, message: str) -> None:
        self.alerts.append(message)
        if self.alert_callback:
            try:
                self.alert_callback(message)
            except Exception as exc:
                logger.error("Alert callback failed", exc_info=True)
