"""
huggingface_hub_stub.py

Stub de segurança para huggingface_hub - fornece apenas o mínimo necessário
sem depender de Internet, autenticação, ou vulnerabilidades.

Uso: Adicione ao sys.modules ANTES de importar transformers
"""

from typing import Optional


def get_full_repo_name(
    model_id: str,
    organization: Optional[str] = None,
    token: Optional[str] = None,
) -> str:
    """
    Retorna nome completo do repositório.

    Stub: Apenas formata a string, não faz chamadas HTTP.
    """
    if organization:
        return f"{organization}/{model_id}"
    return model_id


def hf_hub_download(repo_id: str, filename: str, **kwargs) -> str:
    """
    Stub para download de arquivos do Hub.
    Levanta erro se for chamado (não deve ser necessário em modo offline).
    """
    raise RuntimeError(
        f"huggingface_hub_stub: Tentativa de download remoto de {repo_id}/{filename}. "
        "Use modelos locais ou cache pré-existente."
    )


# Compatibilidade com imports
__version__ = "0.23.0"  # Finge ser compatível
