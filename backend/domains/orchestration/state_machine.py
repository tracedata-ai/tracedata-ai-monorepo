from typing import TypedDict
from langgraph.graph import StateGraph, END

class AgentState(TypedDict):
    input_payload: dict
    response: str
    next_step: str

def ingestion_node(state: AgentState):
    print("DDD Orchestration: Ingestion Node")
    return {"next_step": "orchestrator"}

def orchestrator_node(state: AgentState):
    print("DDD Orchestration: Deterministic Routing")
    return {"next_step": "behavior", "response": "Routed by DDD Orchestrator"}

def behavior_node(state: AgentState):
    print("DDD Orchestration: Behavior Node")
    return {"response": state["response"] + " -> Scored", "next_step": "end"}

def get_shell_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("ingestion", ingestion_node)
    workflow.add_node("orchestrator", orchestrator_node)
    workflow.add_node("behavior", behavior_node)
    workflow.set_entry_point("ingestion")
    workflow.add_edge("ingestion", "orchestrator")
    workflow.add_edge("orchestrator", "behavior")
    workflow.add_edge("behavior", END)
    return workflow.compile()
