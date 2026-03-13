"""
Main entry point for the TraceData AI Middleware.

This module initializes the FastAPI application, defines the core API routes,
and integrates the LangGraph-based agentic workflows for telemetry and chat.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import os
from app.agents.shell_pipe import get_shell_graph
from app.api.v1.api import api_router
from app.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from app.models import entities as models
import uuid
import json

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

# Configure CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

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
        dict: Status of the service and database.
    """
    return {
        "status": "OK",
        "database": "connected (mock)",
        "environment": "Dockerized (Shell)"
    }

@app.post("/api/v1/telemetry", tags=["telemetry"])
async def ingest_telemetry(payload: TelemetryPayload, db: Session = Depends(get_db)):
    """
    Ingests vehicle telemetry and triggers the agentic processing pipeline.
    
    Now also persists the event to the database to support frontend testing 
    and manual trigger buttons, bypassing Kafka for now.
    """
    try:
        # 1. Persist to TelemetryEvent table (Manual Trigger / Button Support)
        # Find numeric indices for relationships if needed, or just use UUIDs from payload
        new_event = models.TelemetryEvent(
            id=uuid.uuid4(),
            trip_id=uuid.UUID(payload.trip_id),
            vehicle_id=uuid.uuid4(), # Placeholder if not in payload, should ideally be in payload
            driver_id=uuid.UUID(payload.driver_id),
            event_type=payload.event_type,
            category=payload.details.get("category", "manual_trigger"),
            priority=payload.details.get("priority", "medium"),
            latitude=payload.details.get("lat"),
            longitude=payload.details.get("lon"),
            details=json.dumps(payload.details)
        )
        
        # Try to find the vehicle_id from the trip if not provided
        trip = db.query(models.Trip).filter(models.Trip.id == new_event.trip_id).first()
        if trip:
            new_event.vehicle_id = trip.vehicle_id
            
        db.add(new_event)
        db.commit()

        # 2. Trigger Shell Graph
        graph = get_shell_graph()
        result = graph.invoke({"input_payload": payload.model_dump(), "response": "", "next_step": ""})
        
        return {
            "status": "success",
            "message": "Telemetry persisted and reached Orchestrator",
            "event_id": str(new_event.id),
            "agent_response": result.get("response")
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Inversion Error: {str(e)}")

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
