"""
Shell pipeline implementation for TraceData AI Middleware.

This module defines a minimal LangGraph-based workflow to validate the 
end-to-end connectivity of the agentic system. It uses a simple linear
progression: Ingestion -> Orchestrator -> Behavior.
"""

from typing import TypedDict
from langgraph.graph import StateGraph, END

class AgentState(TypedDict):
    """
    State definition for the agentic workflow.
    
    Attributes:
        input_payload: The raw dictionary received from the API.
        response: The accumulated message string from various nodes.
        next_step: Control variable for routing logic.
    """
    input_payload: dict
    response: str
    next_step: str

def ingestion_node(state: AgentState):
    """
    The entry point of the shell pipe. Logs the receipt of payload.
    
    Args:
        state (AgentState): The current state of the workflow.
        
    Returns:
        dict: State update indicating the next step is the orchestrator.
    """
    print("Shell Ingestion Node: Received payload")
    return {"next_step": "orchestrator"}

def orchestrator_node(state: AgentState):
    """
    Simulates the central decision-making component of the middleware.
    
    Args:
        state (AgentState): The current state of the workflow.
        
    Returns:
        dict: State update with an initial response and next step 'behavior'.
    """
    print("Shell Orchestrator Node: Processing")
    return {"next_step": "behavior", "response": "Payload reached Shell Orchestrator"}

def behavior_node(state: AgentState):
    """
    Simulates a specialized behavior/decision agent (e.g., scoring).
    
    Args:
        state (AgentState): The current state of the workflow.
        
    Returns:
        dict: State update with the final simulated response and score.
    """
    print("Shell Behavior Node: Dummy Scoring")
    return {"response": state["response"] + " -> Dummy Score: 85", "next_step": "end"}

def get_shell_graph():
    """
    Compiles the shell pipe into a runnable LangGraph workflow.
    
    Returns:
        CompiledGraph: The ready-to-use agentic pipeline.
    """
    workflow = StateGraph(AgentState)
    
    workflow.add_node("ingestion", ingestion_node)
    workflow.add_node("orchestrator", orchestrator_node)
    workflow.add_node("behavior", behavior_node)
    
    workflow.set_entry_point("ingestion")
    
    workflow.add_edge("ingestion", "orchestrator")
    workflow.add_edge("orchestrator", "behavior")
    workflow.add_edge("behavior", END)
    
    return workflow.compile()
