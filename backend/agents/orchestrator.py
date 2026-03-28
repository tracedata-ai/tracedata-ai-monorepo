"""
TraceData — Orchestrator Agent
================================
Routes incoming fleet-management queries to the most appropriate specialist
agent (or answers directly when no routing is needed).

This is the **entry-point** agent: it receives raw user / system messages and
decides whether to handle the request itself or delegate to a downstream agent.

Usage
-----
::

    from agents.orchestrator import OrchestratorAgent

    agent = OrchestratorAgent()
    result = agent.invoke("Which drivers had harsh-braking events last week?",
                          thread_id="fleet-ops-1")
    print(result["messages"][-1].content)
"""

from __future__ import annotations

from langchain_core.tools import tool

from agents.base import BaseAgent

# ---------------------------------------------------------------------------
# Orchestrator tools
# ---------------------------------------------------------------------------


@tool
def route_to_safety_agent(query: str) -> str:
    """Delegate a safety-related query (harsh braking, speeding, collision
    alerts, maintenance warnings) to the Safety Agent.

    Parameters
    ----------
    query:
        The original user query to forward.

    Returns
    -------
    str
        Acknowledgement that the Safety Agent will handle this request.
    """
    # In a production system this would enqueue a task or call the Safety
    # Agent's invoke() method.  Here we return a routing confirmation that
    # the LLM can relay to the user.
    return (
        f"[Routed to SafetyAgent] Query forwarded: '{query}'. "
        "The Safety Agent will analyse telemetry for critical events."
    )


@tool
def route_to_feedback_agent(driver_id: str, query: str) -> str:
    """Delegate a driver-coaching / feedback request to the Feedback Agent.

    Parameters
    ----------
    driver_id:
        Unique identifier of the driver to generate feedback for.
    query:
        Additional context or the specific question from the fleet manager.

    Returns
    -------
    str
        Acknowledgement that the Feedback Agent will handle this request.
    """
    return (
        f"[Routed to FeedbackAgent] Generating coaching feedback for driver "
        f"'{driver_id}'. Query: '{query}'."
    )


@tool
def route_to_behavior_agent(driver_id: str, trip_ids: list[str]) -> str:
    """Delegate a driving-behaviour scoring request to the Behaviour Agent.

    Parameters
    ----------
    driver_id:
        Unique identifier of the driver.
    trip_ids:
        List of trip IDs to score.

    Returns
    -------
    str
        Acknowledgement that the Behaviour Agent will handle this request.
    """
    trips = ", ".join(trip_ids) if trip_ids else "all recent trips"
    return (
        f"[Routed to BehaviourAgent] Scoring behaviour for driver '{driver_id}' "
        f"on trips: {trips}."
    )


# ---------------------------------------------------------------------------
# Concrete agent
# ---------------------------------------------------------------------------


class OrchestratorAgent(BaseAgent):
    """Entry-point agent that understands the full TraceData fleet-management
    domain and routes requests to the correct specialist.

    Capabilities
    ------------
    - Answer general fleet-management questions directly.
    - Delegate safety / alert queries to the Safety Agent.
    - Delegate driver-coaching requests to the Feedback Agent.
    - Delegate behaviour-scoring requests to the Behaviour Agent.
    """

    SYSTEM_PROMPT = """You are the TraceData Orchestrator — the primary AI \
assistant for a fleet-management platform.

Your responsibilities:
1. Answer general questions about trips, routes, drivers, and fleet status.
2. Delegate safety-related queries (harsh braking, speeding, collision alerts,
   maintenance warnings) by calling `route_to_safety_agent`.
3. Delegate driver-coaching / feedback requests by calling
   `route_to_feedback_agent` with the driver ID and query.
4. Delegate driving-behaviour scoring by calling `route_to_behavior_agent`
   with the driver ID and relevant trip IDs.

Rules:
- Be concise and professional.
- Ask for clarification only when essential information is missing.
- Do NOT fabricate telemetry data or trip details.
- When routing, confirm to the user which agent has been engaged.
"""

    tools = [
        route_to_safety_agent,
        route_to_feedback_agent,
        route_to_behavior_agent,
    ]
