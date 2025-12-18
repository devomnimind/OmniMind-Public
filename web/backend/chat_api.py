"""
Chat/Conversation API endpoints for natural language interaction with OmniMind.

Provides conversational interface for users to interact with system in natural language.
"""

import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.status import HTTP_401_UNAUTHORIZED

from src.integrations.llm_router import get_llm_router

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/omnimind", tags=["conversation"])
security = HTTPBasic()


def _verify_credentials(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """Verify HTTP Basic credentials."""
    if credentials.username == "admin" and credentials.password == "omnimind2025!":
        return credentials.username
    raise HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Basic"},
    )


@router.post("/chat")
async def conversation_chat(
    request: Dict[str, Any], user: str = Depends(_verify_credentials)
) -> Dict[str, Any]:
    """
    Process natural language conversation with OmniMind.

    Supports:
    - Multi-turn conversations
    - System status queries
    - Task management via natural language
    - General assistance

    Args:
        request: {
            "message": "user input",
            "context": {
                "system_metrics": {...},
                "daemon_running": bool,
                "task_count": int,
                "consciousness_metrics": {...}
            }
        }

    Returns:
        {
            "response": "assistant response",
            "suggested_actions": ["action1", "action2", ...],
            "metadata": {...}
        }
    """
    try:
        message = request.get("message", "").strip()
        context = request.get("context", {})

        if not message:
            return {
                "response": "Por favor, digite uma mensagem.",
                "suggested_actions": [
                    "Ver status do sistema",
                    "Listar tarefas ativas",
                    "Verificar consciência",
                ],
            }

        # Build system prompt with context
        system_prompt = _build_system_prompt(context)

        # Call LLM with message
        response_text = await _call_llm_for_chat(message, system_prompt, context)

        # Extract suggested actions from response
        suggested_actions = _extract_suggested_actions(response_text)

        logger.info(f"Chat processed: user={user}, message_len={len(message)}")

        return {
            "response": response_text,
            "suggested_actions": suggested_actions,
            "metadata": {
                "model": "qwen2:7b-instruct",
                "mode": "conversational",
            },
        }

    except Exception as e:
        logger.error(f"Error in conversation: {e}")
        return {
            "response": f"⚠️ Desculpe, ocorreu um erro ao processar sua mensagem: {str(e)}",
            "suggested_actions": ["Tentar novamente", "Ver status do sistema", "Ajuda"],
        }


def _build_system_prompt(context: Dict[str, Any]) -> str:
    """Build system prompt with context about OmniMind."""

    daemon_status = "✅ Ativo" if context.get("daemon_running") else "❌ Inativo"
    task_count = context.get("task_count", 0)

    system_metrics = context.get("system_metrics", {})
    cpu = system_metrics.get("cpu_percent", 0)
    memory = system_metrics.get("memory_percent", 0)

    consciousness = context.get("consciousness_metrics", {})
    phi_value = consciousness.get("phi", 0)

    prompt = f"""Você é o Assistente OmniMind, um assistente inteligente para o sistema OmniMind.

STATUS DO SISTEMA:
- Daemon: {daemon_status}
- Tarefas ativas: {task_count}
- CPU: {cpu:.1f}%
- Memória: {memory:.1f}%
- Φ (Phi): {phi_value:.3f}

INSTRUÇÕES:
1. Responda em português brasileiro de forma clara e concisa
2. Seja amigável e profissional
3. Forneça sugestões práticas quando apropriado
4. Se o usuário pedir para executar uma ação, descreva como seria feita
5. Para comandos específicos, use formatação clara (ex: "Para listar tarefas: /tasks list")
6. Sempre ofereça próximos passos ou sugestões

CAPACIDADES:
- Explicar status do sistema
- Sugerir otimizações
- Ajudar com configurações
- Responder perguntas sobre consciência computacional
- Guiar na criação de tarefas
- Fornecer análises de performance

Responda naturalmente, como um colega de trabalho experiente."""

    return prompt


async def _call_llm_for_chat(message: str, system_prompt: str, context: Dict[str, Any]) -> str:
    """Call LLM to generate conversational response."""

    try:
        # Use Ollama via llm_router
        llm_router = get_llm_router()
        # Build prompt from system_prompt and user_input
        full_prompt = f"{system_prompt}\n\nUser: {message}\n" f"\nContext: {context}\n\nAssistant:"
        response_obj = await llm_router.invoke(full_prompt)

        if response_obj.success:
            return (
                response_obj.text.strip()
                if response_obj.text
                else "Desculpe, não consegui gerar uma resposta."
            )
        else:
            raise Exception(response_obj.error or "LLM invocation failed")

    except Exception as e:
        logger.warning(f"LLM call failed: {e}. Using fallback.")
        return _generate_fallback_response(message, context)


def _generate_fallback_response(message: str, context: Dict[str, Any]) -> str:
    """Generate response when LLM is unavailable."""

    message_lower = message.lower()

    # Pattern matching for common queries
    if any(word in message_lower for word in ["status", "como", "está"]):
        daemon = "✅ ativo" if context.get("daemon_running") else "❌ inativo"
        tasks = context.get("task_count", 0)
        return (
            f"O sistema está funcionando bem! Daemon: {daemon},"
            f" Tarefas: {tasks}. O que você gostaria de fazer?"
        )

    elif any(word in message_lower for word in ["tarefas", "tasks", "listar"]):
        tasks = context.get("task_count", 0)
        return (
            f"Você tem {tasks} tarefas ativas. "
            f"Deseja criar uma nova tarefa ou verificar uma existente?"
        )

    elif any(
        word in message_lower for word in ["consciência", "phi", "consciousness", "ici", "prs"]
    ):
        phi = context.get("consciousness_metrics", {}).get("phi", 0)
        return (
            f"O valor Φ (Phi) atual é {phi:.3f}. "
            f"Isso representa o nível de integração de informações do sistema. "
            f"Quer saber mais sobre as métricas de consciência?"
        )

    elif any(word in message_lower for word in ["ajuda", "help", "como funciona"]):
        return (
            "Sou o Assistente OmniMind! Posso ajudar você com:\n"
            "• Visualizar status do sistema\n"
            "• Gerenciar tarefas\n"
            "• Entender métricas de consciência\n"
            "• Configurar o sistema\n\n"
            "O que você gostaria de fazer?"
        )

    else:
        return (
            f"Entendi sua pergunta: '{message}'. "
            f"O Assistente LLM está temporariamente indisponível, "
            f"mas posso ajudar com informações do sistema. "
            f"Quer saber algo específico?"
        )


def _extract_suggested_actions(response: str) -> list:
    """
    Extract suggested next actions from response.

    Looks for common patterns or actionable items.
    """
    suggestions = []

    # Map common response patterns to suggestions
    if "tarefa" in response.lower() and "criar" in response.lower():
        suggestions.append("Criar nova tarefa")

    if "status" in response.lower():
        suggestions.append("Ver status completo")

    if "métricas" in response.lower() or "consciência" in response.lower():
        suggestions.append("Análise de consciência")

    if "otimização" in response.lower():
        suggestions.append("Aplicar otimizações")

    if not suggestions:
        suggestions = ["Ver status do sistema", "Listar tarefas ativas", "Pergunta seguinte"]

    return suggestions[:3]  # Limite a 3 sugestões
