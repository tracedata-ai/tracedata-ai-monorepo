"""
API endpoints for interacting with the agentic middleware shells.
"""

from fastapi import APIRouter
from app.schemas import entities as schemas

router = APIRouter()

@router.post("/chat-shell", tags=["agents"])
async def chat_shell(payload: schemas.ChatPayload):
    """
    Dummy endpoint for testing direct chat interactions with the agentic shell.

    Args:
        payload (ChatPayload): The user's input message.

    Returns:
        dict: A simulated response from the chat agent.
    """
    return {
        "status": "success",
        "response": f"Hello from Dockerized Chat Shell Agent. You said: {payload.message}"
    }
