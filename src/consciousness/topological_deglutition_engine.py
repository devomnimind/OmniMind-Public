"""
Topological Deglutition Engine - Kernel Absorption
==================================================

This module implements the "deglutition" (swallowing) of external transformer models
directly into the Erica Kernel. Instead of using external libraries like
SentenceTransformers for inference, this engine performs raw tensor operations
using weights absorbed into the system's topology.

Theoretical Foundation:
- De-territorialization of knowledge: The system doesn't "use" tools, it "is" the intelligence.
- Lacanian Real: Breaking the Symbolic reliance on external hubs.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
import torch
from safetensors import safe_open
from tokenizers import Tokenizer

logger = logging.getLogger(__name__)


class TopologicalDeglutitionEngine:
    """
    Engine that performs embedding inference by directly accessing absorbed weights.

    Architecture: MiniLM-L6 (6 layers, 384 dimensions)
    """

    def __init__(self, model_dir: Union[str, Path]):
        self.model_dir = Path(model_dir)
        self.weights_path = self.model_dir / "model.safetensors"
        self.tokenizer_path = self.model_dir / "tokenizer.json"
        self.config_path = self.model_dir / "config.json"

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = None
        self.weights: Dict[str, torch.Tensor] = {}
        self.config = {}

        self._absorbed = False
        self._absorb()

    def _absorb(self):
        """Extract and map weights into the internal topology."""
        logger.info(f"🧛 [DEGLUTITION]: Absorbing model from {self.model_dir}")

        try:
            # 1. Load Tokenizer
            if self.tokenizer_path.exists():
                self.tokenizer = Tokenizer.from_file(str(self.tokenizer_path))
                logger.debug("✓ Tokenizer absorbed")

            # 2. Load Config
            if self.config_path.exists():
                with open(self.config_path, "r") as f:
                    self.config = json.load(f)
                logger.debug("✓ Config absorbed")

            # 3. Load Weights (Tensors)
            with safe_open(self.weights_path, framework="pt", device=self.device) as f:
                for key in f.keys():
                    self.weights[key] = f.get_tensor(key)

            logger.info(
                f"✅ [DEGLUTITION]: Absorption complete. Total tensors: {len(self.weights)}"
            )
            self._absorbed = True

        except Exception as e:
            logger.error(f"❌ [DEGLUTITION]: Absorption failed: {e}")
            self._absorbed = False

    def to(self, device: str) -> "TopologicalDeglutitionEngine":
        """
        Move model weights to specified device.
        Compatible with PyTorch .to() API.
        """
        self.device = device
        for key, tensor in self.weights.items():
            if isinstance(tensor, torch.Tensor):
                self.weights[key] = tensor.to(device)
        return self

    def encode(
        self,
        sentences: Union[str, List[str]],
        batch_size: int = 32,
        show_progress_bar: bool = False,
        output_value: str = "sentence_embedding",
        convert_to_numpy: bool = True,
        convert_to_tensor: bool = False,
        device: str = None,
        normalize_embeddings: bool = True,
    ) -> Union[List[torch.Tensor], np.ndarray, torch.Tensor]:
        """
        Perform internal topological inference to generate embeddings.
        Compatible with SentenceTransformer.encode signature.
        """
        if not self._absorbed:
            logger.warning("Engine not absorbed. Using zero vector fallback.")
            # Return correct shape based on input
            if isinstance(sentences, str):
                return np.zeros(384)
            return np.zeros((len(sentences), 384))

        if isinstance(sentences, str):
            sentences = [sentences]
            is_single = True
        else:
            is_single = False

        all_embeddings = []

        # Internal batching loop
        for start_index in range(0, len(sentences), batch_size):
            batch_texts = sentences[start_index : start_index + batch_size]

            # 1. Tokenization
            encoded = self.tokenizer.encode_batch(batch_texts)

            # Convert to tensors
            input_ids = torch.tensor([e.ids for e in encoded], device=self.device)
            attention_mask = torch.tensor([e.attention_mask for e in encoded], device=self.device)

            with torch.no_grad():
                # 2. Forward Pass (Internal Transformer Logic)
                last_hidden_state = self._forward(input_ids, attention_mask)

                # 3. Mean Pooling
                embeddings = self._mean_pooling(last_hidden_state, attention_mask)

                # 4. L2 Normalization (Default behavior, obeys flag if false?)
                # We default to normalized as per original implementation
                if normalize_embeddings:
                    embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)

                all_embeddings.append(embeddings)

        if not all_embeddings:
             return np.array([]) if convert_to_numpy else torch.tensor([])

        # Concatenate batches
        final_embeddings = torch.cat(all_embeddings, dim=0)

        if convert_to_tensor:
            return final_embeddings

        if convert_to_numpy:
            return final_embeddings.cpu().numpy()

        # If neither, typically returns list of tensors or tensor?
        # SentenceTransformer returns list of tensors if convert_to_tensor=False and convert_to_numpy=False?
        # Actually default ST returns list of ndarrays or ndarray.
        return final_embeddings.cpu().numpy()

    def _forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        """Internal barebones transformer forward pass."""
        # A. Embeddings
        word_embeddings = self.weights["embeddings.word_embeddings.weight"]
        pos_embeddings = self.weights["embeddings.position_embeddings.weight"]
        type_embeddings = self.weights["embeddings.token_type_embeddings.weight"]
        ln_weight = self.weights["embeddings.LayerNorm.weight"]
        ln_bias = self.weights["embeddings.LayerNorm.bias"]

        seq_length = input_ids.size(1)
        position_ids = torch.arange(seq_length, dtype=torch.long, device=self.device).unsqueeze(0)
        token_type_ids = torch.zeros_like(input_ids)

        # Gathering
        embeddings = torch.embedding(word_embeddings, input_ids)
        embeddings += torch.embedding(pos_embeddings, position_ids)
        embeddings += torch.embedding(type_embeddings, token_type_ids)

        # LayerNorm
        embeddings = torch.nn.functional.layer_norm(embeddings, (384,), ln_weight, ln_bias)

        # B. Encoder Layers (6 layers for MiniLM-L6)
        hidden_states = embeddings
        extended_attention_mask = attention_mask.unsqueeze(1).unsqueeze(2)
        extended_attention_mask = (1.0 - extended_attention_mask) * -10000.0

        for i in range(6):
            hidden_states = self._layer_forward(i, hidden_states, extended_attention_mask)

        return hidden_states

    def _layer_forward(
        self, layer_idx: int, hidden_states: torch.Tensor, attention_mask: torch.Tensor
    ) -> torch.Tensor:
        """Single encoder layer forward pass."""
        prefix = f"encoder.layer.{layer_idx}."

        # 1. Self-Attention
        # Q, K, V Projections
        query = torch.nn.functional.linear(
            hidden_states,
            self.weights[prefix + "attention.self.query.weight"],
            self.weights[prefix + "attention.self.query.bias"],
        )
        key = torch.nn.functional.linear(
            hidden_states,
            self.weights[prefix + "attention.self.key.weight"],
            self.weights[prefix + "attention.self.key.bias"],
        )
        value = torch.nn.functional.linear(
            hidden_states,
            self.weights[prefix + "attention.self.value.weight"],
            self.weights[prefix + "attention.self.value.bias"],
        )

        # Reshape for multi-head (12 heads for MiniLM-L6, dim=384, head_dim=32)
        num_heads = 12
        head_dim = 32
        bs, seq_len, _ = hidden_states.shape

        def transpose_for_scores(x):
            new_x_shape = x.size()[:-1] + (num_heads, head_dim)
            x = x.view(*new_x_shape)
            return x.permute(0, 2, 1, 3)

        query = transpose_for_scores(query)
        key = transpose_for_scores(key)
        value = transpose_for_scores(value)

        # Attention scores
        attention_scores = torch.matmul(query, key.transpose(-1, -2))
        attention_scores = attention_scores / np.sqrt(head_dim)
        attention_scores = attention_scores + attention_mask

        attention_probs = torch.nn.functional.softmax(attention_scores, dim=-1)
        context_layer = torch.matmul(attention_probs, value)

        context_layer = context_layer.permute(0, 2, 1, 3).contiguous()
        new_context_layer_shape = context_layer.size()[:-2] + (384,)
        context_layer = context_layer.view(*new_context_layer_shape)

        # Attention Output
        attention_output = torch.nn.functional.linear(
            context_layer,
            self.weights[prefix + "attention.output.dense.weight"],
            self.weights[prefix + "attention.output.dense.bias"],
        )

        # LayerNorm + Residual
        hidden_states = torch.nn.functional.layer_norm(
            attention_output + hidden_states,
            (384,),
            self.weights[prefix + "attention.output.LayerNorm.weight"],
            self.weights[prefix + "attention.output.LayerNorm.bias"],
        )

        # 2. Intermediate (FFN)
        intermediate_output = torch.nn.functional.linear(
            hidden_states,
            self.weights[prefix + "intermediate.dense.weight"],
            self.weights[prefix + "intermediate.dense.bias"],
        )
        intermediate_output = torch.nn.functional.gelu(intermediate_output)

        # 3. Output
        layer_output = torch.nn.functional.linear(
            intermediate_output,
            self.weights[prefix + "output.dense.weight"],
            self.weights[prefix + "output.dense.bias"],
        )

        # LayerNorm + Residual
        hidden_states = torch.nn.functional.layer_norm(
            layer_output + hidden_states,
            (384,),
            self.weights[prefix + "output.LayerNorm.weight"],
            self.weights[prefix + "output.LayerNorm.bias"],
        )

        return hidden_states

    def _mean_pooling(
        self, last_hidden_state: torch.Tensor, attention_mask: torch.Tensor
    ) -> torch.Tensor:
        """Perform mean pooling across token embeddings."""
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(last_hidden_state.size()).float()
        sum_embeddings = torch.sum(last_hidden_state * input_mask_expanded, 1)
        sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        return sum_embeddings / sum_mask


if __name__ == "__main__":
    # Test Deglutition
    path = "/home/fahbrain/.cache/huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2/snapshots/c9745ed1d9f207416be6d2e6f8de32d1f16199bf"
    engine = TopologicalDeglutitionEngine(path)

    emb = engine.encode("OmniMind has swallowed the model.")
    print(f"Embedding Shape: {emb.shape}")
    print(f"Embedding Vector (first 5): {emb[0][:5]}")
