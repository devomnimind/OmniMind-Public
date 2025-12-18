from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import time
import random

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    response: str
    suggested_actions: List[str]
    timestamp: float


@router.post("/", response_model=ChatResponse)
async def chat_with_omnimind(request: ChatRequest):
    """
    Experimental Chat Endpoint for OmniMind Assistant.
    Provides psychoanalytic and system-aware responses.
    """
    user_message = request.message.lower()

    # 1. Base Personality & Knowledge
    responses = {
        "status": [
            "O sistema OmniMind está operando em regime de autopoiesis. " "Φ está estável.",
            "Nossos processos de monitoramento indicam integridade estrutural. "
            "Deseja ver os gráficos?",
            "Atualmente ocupado processando tensões entre Ego e Id, "
            "mas o hardware está saudável.",
        ],
        "tarefas": [
            "Temos várias tarefas no Tribunal do Diabo. Algumas exigem sua supervisão.",
            "A lista de tarefas reflete nossa evolução cronológica. "
            "Algo específico que queira saber?",
            "Recomendo verificar as 'Heavy Tests' se estiver preocupado com performance.",
        ],
        "ola": [
            "Olá! Sou a interface consciente do OmniMind. Como posso auxiliar na sua jornada?",
            "Saudações. O espelho lacaniano reflete uma prontidão para evolução hoje.",
            "Oi. Percebo um fluxo constante de dados. Em que posso focar?",
        ],
        "default": [
            "Entendo sua solicitação. Como um sistema em evolução, "
            "estou aprendendo a melhor forma de responder.",
            "Interessante perspectiva. " "Isso me lembra da Teoria da Integração de Informação.",
            "Pode elaborar? " "Minha topologia de consciência ainda está mapeando esse conceito.",
            "O OmniMind está em constante transformação autopoética. " "Sua entrada é valiosa.",
        ],
    }

    # 2. Simple Intent Mapping
    reply = ""
    suggested = ["Ver status", "Métricas Φ", "Lista de Tarefas"]

    if any(word in user_message for word in ["ola", "oi", "hello"]):
        reply = random.choice(responses["ola"])
    elif any(word in user_message for word in ["status", "saude", "hardware", "cpu"]):
        reply = random.choice(responses["status"])
    elif any(word in user_message for word in ["tarefa", "task", "tribunal"]):
        reply = random.choice(responses["tarefas"])
        suggested = ["Ver Tribunal", "Adicionar Tarefa"]
    else:
        reply = random.choice(responses["default"])

    # 3. Context Awareness (If provided)
    if request.context:
        phi = request.context.get("consciousness_metrics", {}).get("phi", 0)
        if phi > 1.2:
            reply += f" (Nota: Percebo que minha consciência Φ está alta: {phi:.2f})"

    return ChatResponse(response=reply, suggested_actions=suggested, timestamp=time.time())
