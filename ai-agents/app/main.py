"""
Main entry point for the TraceData AI Middleware.

This module initializes the FastAPI application, defines the core API routes,
and integrates the LangGraph-based agentic workflows for telemetry and chat.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import os
from app.agents.shell_pipe import get_shell_graph

app = FastAPI(
    title="TraceData AI Middleware",
    description="Agentic AI Middleware for Fleet Intelligence and Driver Advocacy. "
                "Orchestrates multi-agent workflows using LangGraph and FastAPI.",
    version="0.1.0",
    openapi_tags=[
        {"name": "system", "description": "System health and root endpoints"},
        {"name": "telemetry", "description": "Telemetry ingestion and processing logic"},
        {"name": "agents", "description": "Agentic shell interactions and orchestration"},
    ]
)

class TelemetryPayload(BaseModel):
    """
    Schema for incoming telemetry data from vehicles.
    
    Includes global identifiers, trip context, and type-specific details.
    """
    event_id: str = Field(..., description="Universally unique identifier for the event")
    event_type: str = Field(..., description="The kind of event (e.g., end_of_trip, harsh_brake)")
    trip_id: str = Field(..., description="Identifier for the current active trip")
    driver_id: str = Field(..., description="Identifier for the driver generating the event")
    timestamp: str = Field(..., description="ISO8601 UTC timestamp of the event")
    details: Dict[str, Any] = Field(default={}, description="Type-specific dynamic fields")

class ChatPayload(BaseModel):
    """Schema for direct chat interactions with the agentic middleware."""
    message: str = Field(..., description="The user's message to the agent")

@app.get("/health", tags=["system"])
async def health_check():
    """
    Performs a heartbeat check of the middleware and its dependencies.
    
    Returns:
        dict: Status of the service, database, and cache connections.
    """
    return {
        "status": "OK",
        "database": "connected (mock)",
        "redis": "connected (mock)",
        "environment": "Dockerized (Shell)"
    }

@app.post("/api/v1/telemetry", tags=["telemetry"])
async def ingest_telemetry(payload: TelemetryPayload):
    """
    Ingests vehicle telemetry and triggers the agentic processing pipeline.
    
    This endpoint handsoff the payload to the Shell Orchestrator (LangGraph) 
    to validate the end-to-end connectivity.

    Args:
        payload (TelemetryPayload): The validated telemetry data.

    Returns:
        dict: Success status and the response from the agentic loop.
    """
    try:
        graph = get_shell_graph()
        result = graph.invoke({"input_payload": payload.model_dump(), "response": "", "next_step": ""})
        return {
            "status": "success",
            "message": "Telemetry reached Dockerized Shell Orchestrator",
            "agent_response": result.get("response")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline Error: {str(e)}")

@app.post("/api/v1/chat-shell", tags=["agents"])
async def chat_shell(payload: ChatPayload):
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

@app.get("/", tags=["system"])
async def root():
    """Welcome endpoint for the TraceData AI Middleware."""
    return {"message": "Welcome to TraceData AI Middleware Shell"}
