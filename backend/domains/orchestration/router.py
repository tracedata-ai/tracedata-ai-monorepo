from fastapi import APIRouter
from pydantic import BaseModel

class ChatPayload(BaseModel):
    message: str

router = APIRouter()

@router.post("/chat-shell", tags=["agents"])
async def chat_shell(payload: ChatPayload):
    return {
        "status": "success",
        "response": f"DDD Orchestrator received: {payload.message}"
    }
