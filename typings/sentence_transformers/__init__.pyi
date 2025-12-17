"""Type stubs for sentence_transformers."""

from typing import Any, List, Union
import numpy as np

class SentenceTransformer:
    """Sentence transformer for generating embeddings."""

    def __init__(self, model_name_or_path: str, **kwargs: Any) -> None: ...
    def encode(
        self,
        sentences: Union[str, List[str]],
        batch_size: int = 32,
        show_progress_bar: bool = False,
        convert_to_numpy: bool = True,
        **kwargs: Any
    ) -> Union[np.ndarray[Any], List[np.ndarray[Any]]]: ...

__all__ = ["SentenceTransformer"]
