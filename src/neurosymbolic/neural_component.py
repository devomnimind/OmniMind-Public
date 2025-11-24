"""
Componente Neural - Interface com LLMs e Transformers

Responsável por:
  - Inferência probabilística (Local via Ollama ou Remota via Hugging Face)
  - Processamento de linguagem natural
  - Geração criativa
  - Embeddings e representações latentes
"""

import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class NeuralInference:
    """Resultado de inferência neural."""

    answer: str
    confidence: float  # 0.0-1.0
    embedding: Optional[List[float]] = None
    alternatives: Optional[List[str]] = None
    raw_output: Optional[Dict[str, Any]] = None


class NeuralComponent:
    """
    Componente neural do sistema neurosymbolic.

    Integra-se com LLMs (Ollama local ou Hugging Face API) para raciocínio
    probabilístico e processamento de linguagem natural.
    """

    def __init__(
        self,
        model_name: str = "ollama/qwen2:7b-instruct",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        timeout: float = 60.0,
    ):
        """
        Inicializa componente neural.

        Args:
            model_name: Nome do modelo. Prefixos suportados:
                        - 'ollama/': Usa servidor local Ollama
                        - 'hf/': Usa Hugging Face Inference API
                        - Sem prefixo: Tenta Ollama por padrão
            temperature: Criatividade (0=determinístico, 1=criativo)
            max_tokens: Tamanho máximo de resposta
            timeout: Timeout de inferência em segundos
        """
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout

        # Configurações de API
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.hf_token = os.getenv("HUGGING_FACE_HUB_TOKEN")
        self.hf_space_url = os.getenv("HF_SPACE_URL")

        # Determinar provedor
        if model_name.startswith("hf/"):
            if model_name == "hf/space" or model_name == "hf/default":
                self.provider = "hf_space"
                self.model_name = "default"
            elif model_name == "hf/":
                self.provider = "huggingface"
                self.model_name = "Qwen/Qwen2.5-72B-Instruct"
            else:
                self.provider = "huggingface"
                self.model_name = model_name.replace("hf/", "")
        elif model_name.startswith("ollama/"):
            self.provider = "ollama"
            self.model_name = model_name.replace("ollama/", "")
        else:
            # Default para Ollama se não especificado
            self.provider = "ollama"
            self.model_name = model_name

        logger.info(
            f"Neural component initialized: {self.model_name} "
            f"(provider={self.provider}, temp={temperature})"
        )

    def infer(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        chain_of_thought: bool = True,
    ) -> NeuralInference:
        """
        Realizar inferência neural sobre query.

        Args:
            query: Pergunta ou problema
            context: Contexto adicional
            chain_of_thought: Incluir raciocínio passo-a-passo

        Returns:
            NeuralInference com resposta e confiança
        """
        logger.info(f"Neural inference ({self.provider}): {query[:100]}...")

        try:
            if self.provider == "ollama":
                return self._infer_ollama(query, context)
            elif self.provider == "huggingface":
                return self._infer_huggingface(query, context)
            elif self.provider == "hf_space":
                return self._infer_hf_space(query, context)
            else:
                return self._infer_stub(query)

        except Exception as e:
            logger.exception(f"Neural inference error ({self.provider})")
            # Fallback para stub em caso de erro
            return self._infer_stub(query, error=str(e))

    def _infer_hf_space(
        self, query: str, context: Optional[Dict[str, Any]] = None
    ) -> NeuralInference:
        """Inferência via HF Space Dedicado (FastAPI)."""
        if not self.hf_space_url:
            raise ValueError("HF_SPACE_URL not found in environment")

        url = f"{self.hf_space_url}/generate"
        headers = {"Authorization": f"Bearer {self.hf_token}"}

        payload = {
            "inputs": query,
            "parameters": {
                "max_new_tokens": self.max_tokens,
                "temperature": self.temperature,
            },
        }

        if context:
            # Adicionar contexto ao prompt se necessário (o app.py espera inputs string)
            payload["inputs"] = f"Context: {json.dumps(context)}\n\nQuery: {query}"

        response = requests.post(
            url, headers=headers, json=payload, timeout=self.timeout
        )
        response.raise_for_status()

        data = response.json()
        answer = data.get("generated_text", "")

        return NeuralInference(
            answer=answer,
            confidence=0.95,
            raw_output={"source": "hf_space", "data": data},
        )

    def _infer_ollama(
        self, query: str, context: Optional[Dict[str, Any]] = None
    ) -> NeuralInference:
        """Inferência via Ollama local."""
        url = f"{self.ollama_host}/api/generate"

        prompt = query
        if context:
            prompt = f"Context: {json.dumps(context)}\n\nQuery: {query}"

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens,
            },
        }

        response = requests.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()

        return NeuralInference(
            answer=data.get("response", ""),
            confidence=0.9,  # Ollama não retorna confiança direta facilmente
            raw_output=data,
        )

    def _infer_huggingface(
        self, query: str, context: Optional[Dict[str, Any]] = None
    ) -> NeuralInference:
        """Inferência via Hugging Face Inference API (Direct HTTP)."""
        if not self.hf_token:
            raise ValueError("HUGGING_FACE_HUB_TOKEN not found in environment")

        api_url = f"https://api-inference.huggingface.co/models/{self.model_name}"
        headers = {"Authorization": f"Bearer {self.hf_token}"}

        prompt = query
        if context:
            prompt = f"Context: {json.dumps(context)}\n\nQuery: {query}"

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": self.max_tokens,
                "temperature": self.temperature,
                "return_full_text": False,
            },
        }

        response = requests.post(
            api_url, headers=headers, json=payload, timeout=self.timeout
        )
        response.raise_for_status()

        # HF API retorna lista de dicts ou dict dependendo do modelo
        data = response.json()

        if isinstance(data, list) and len(data) > 0:
            answer = data[0].get("generated_text", "")
        elif isinstance(data, dict):
            answer = data.get("generated_text", "")
        else:
            answer = str(data)

        return NeuralInference(
            answer=answer,
            confidence=0.85,
            raw_output={"source": "huggingface_api", "data": data},
        )

    def _infer_stub(self, query: str, error: Optional[str] = None) -> NeuralInference:
        """Fallback stub para testes ou falhas."""
        msg = f" [Fallback due to error: {error}]" if error else ""

        if "true" in query.lower():
            answer = "Yes, that appears to be true." + msg
            confidence = 0.85
        elif "false" in query.lower():
            answer = "No, that appears to be false." + msg
            confidence = 0.80
        else:
            answer = f"Analyzing: {query[:50]}..." + msg
            confidence = 0.7

        return NeuralInference(
            answer=answer,
            confidence=confidence,
            alternatives=[f"Alternative 1 for: {query[:30]}"],
        )

    def embed(self, text: str) -> List[float]:
        """
        Gerar embedding para texto.

        Args:
            text: Texto a embeddar

        Returns:
            Vetor de embedding
        """
        logger.debug(f"Generating embedding: {text[:50]}...")

        try:
            if self.provider == "ollama":
                url = f"{self.ollama_host}/api/embeddings"
                payload = {"model": self.model_name, "prompt": text}
                response = requests.post(url, json=payload, timeout=self.timeout)
                response.raise_for_status()
                return response.json().get("embedding", [])

            elif self.provider == "huggingface" and self.hf_token:
                api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{self.model_name}"
                headers = {"Authorization": f"Bearer {self.hf_token}"}
                payload = {"inputs": text}

                response = requests.post(
                    api_url, headers=headers, json=payload, timeout=self.timeout
                )
                response.raise_for_status()

                # Retorna lista de floats (embedding) ou lista de lista (batch)
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    if isinstance(data[0], list):
                        return data[0]  # Batch size 1
                    return data
                return []

        except Exception as e:
            logger.error(f"Embedding error: {e}")

        # Fallback dummy
        return [0.5] * 768

    def batch_infer(
        self,
        queries: List[str],
        context: Optional[Dict[str, Any]] = None,
    ) -> List[NeuralInference]:
        """
        Inferências em batch para múltiplas queries.

        Args:
            queries: Lista de perguntas
            context: Contexto compartilhado

        Returns:
            Lista de NeuralInference
        """
        logger.info(f"Batch neural inference: {len(queries)} queries")
        return [self.infer(q, context) for q in queries]

    def process(self, input_data: Any) -> Dict[str, Any]:
        """
        Wrapper genérico para processamento (compatibilidade de interface).

        Args:
            input_data: Dados de entrada (texto ou dict)

        Returns:
            Resultado em formato de dicionário
        """
        query = str(input_data)
        result = self.infer(query)
        return {
            "answer": result.answer,
            "confidence": result.confidence,
            "embedding": result.embedding,
            "alternatives": result.alternatives,
        }
