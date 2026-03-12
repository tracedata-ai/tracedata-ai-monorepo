"""
Smoke tests for TraceData AI Middleware.

Validates the basic connectivity and core logic of the shell pipe 
using the FastAPI TestClient.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

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
        "event_id": "evt_test_123",
        "event_type": "end_of_trip",
        "trip_id": "TRP-TEST-001",
        "driver_id": "DRV-TEST-999",
        "timestamp": "2026-03-13T07:10:00Z",
        "details": {}
    }
    response = client.post("/api/v1/telemetry", json=payload)
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
