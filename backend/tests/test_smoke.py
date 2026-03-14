"""
Smoke tests for TraceData AI Middleware.

Validates the basic connectivity and core logic of the shell pipe 
using the FastAPI TestClient.
"""

from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

def test_health_check():
    """Verifies that the system health endpoint is operational and returns Docker context."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "OK"
    assert "environment" in response.json()

def test_telemetry_ingestion_shell():
    """
    Validates end-to-end telemetry flow through the LangGraph shell pipe.
    
    Verifies that the orchestrator is reached and a dummy score is returned.
    """
    payload = {
        "event_id": str(uuid.uuid4()),
        "event_type": "end_of_trip",
        "trip_id": "550e8400-e29b-41d4-a716-446655440000",
        "driver_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
        "timestamp": "2026-03-13T07:10:00Z",
        "details": {
            "category": "normal_operation",
            "priority": "low"
        }
    }
    response = client.post("/api/v1/telemetry", json=payload)
    if response.status_code != 200:
        print(f"\nDEBUG ERROR: {response.json()}")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "Payload reached Shell Orchestrator" in response.json()["agent_response"]
    assert "Dummy Score: 85" in response.json()["agent_response"]

def test_chat_shell():
    """Verifies the chat shell endpoint returns a valid simulated response."""
    payload = {"message": "Test Message"}
    response = client.post("/api/v1/chat-shell", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "Test Message" in response.json()["response"]

def test_root():
    """Verifies the root greeting endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "TraceData" in response.json()["message"]
