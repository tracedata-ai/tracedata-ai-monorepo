# Day 3 Exercise Explained (Simple Guide)

This Day 3 exercise teaches you how to build a **single AI agent** that helps schedule a job at a lower-carbon time.

In plain words:

- You tell the agent when you want to run a job.
- The agent checks your saved preferences (allowed regions and allowed time shift).
- The agent finds a better time within your allowed window.
- The agent returns the best region and start time with the lowest carbon intensity.

---

## 1) What Problem Are We Solving?

Cloud regions can have different carbon intensity at different times.

Goal:

- Keep your requested time mostly the same.
- Allow a small shift (for example, +/- 60 minutes).
- Pick the cleanest (lowest-carbon) option in that window.

---

## 2) Big Picture Architecture

```mermaid
flowchart LR
    U[User] --> C[Chat Loop]
    C --> A[LLM Assistant]
    A -->|tool call| T[ToolNode]
    T --> P[(profile.json\npreferences)]
    T --> F[(mock_forecast.json\ncarbon data)]
    T --> A
    A --> C
    C --> U
```

What each part does:

- `run_chat.py`: runs the conversation loop.
- Assistant node: decides whether to answer directly or call tools.
- ToolNode: executes tools like `get_profile`, `update_prefs`, `recommend_best`.
- `memory/profile.json`: stores your preferences.
- `data/mock_forecast.json`: provides carbon forecast points.

---

## 3) End-to-End Conversation Flow

```mermaid
sequenceDiagram
    participant User
    participant Chat as run_chat.py
    participant LLM as Assistant (LLM)
    participant Tools as ToolNode
    participant Profile as profile.json
    participant Forecast as mock_forecast.json

    User->>Chat: "I want to schedule a job"
    Chat->>LLM: user message + system instruction
    LLM->>Tools: call get_profile()
    Tools->>Profile: read preferences
    Profile-->>Tools: regions + shift window
    Tools-->>LLM: profile result
    LLM-->>Chat: ask for desired time

    User->>Chat: "tomorrow 10am"
    Chat->>LLM: message
    LLM->>Tools: call recommend_best(start_iso)
    Tools->>Forecast: read forecast points
    Forecast-->>Tools: region time series
    Tools-->>LLM: best region + best time + carbon value
    LLM-->>Chat: concise recommendation
    Chat-->>User: final answer
```

---

## 4) Graph Logic in the Agent

The LangGraph setup is simple:

- Start at assistant.
- If assistant requests tools, go to tools.
- After tools run, return to assistant.
- End when assistant has no more tool calls.

```mermaid
stateDiagram-v2
    [*] --> Assistant
    Assistant --> Tools: tool_calls present
    Assistant --> End: no tool_calls
    Tools --> Assistant
    End --> [*]
```

---

## 5) How Recommendation Works

The `recommend_best` tool does this:

1. Read `regions_allowed` and `allowed_shift_minutes`.
2. Build a time window around desired start.
3. Check forecast points in allowed regions.
4. Keep only points inside the window.
5. Choose the one with smallest `g` (carbon intensity).

```mermaid
flowchart TD
    S[Start with desired time] --> P[Load profile]
    P --> W[Build +/- shift window]
    W --> D[Load forecast by region]
    D --> F[Filter points inside time window]
    F --> Q{Any valid points?}
    Q -- No --> N[Return no recommendation]
    Q -- Yes --> B[Pick point with lowest g]
    B --> R[Return region + time + g]
```

---

## 6) Preference Memory (Why It Matters)

If you say:

- "I prefer regions SG, EU_WEST"
- "remember allowed shift 90 minutes"

The agent updates `profile.json`, so later recommendations follow your new preferences automatically.

```mermaid
flowchart LR
    U[User preference message] --> L[LLM decides to call update_prefs]
    L --> T[update_prefs tool]
    T --> J[(profile.json updated)]
    J --> NX[Next recommendation uses new values]
```

---

## 7) Files You Should Focus On

- `day-3/carbon-aware-agent-workshop-local/carbon-aware-agent-workshop/solution/src/run_chat.py`
- `day-3/carbon-aware-agent-workshop-local/carbon-aware-agent-workshop/solution/src/tools.py`
- `day-3/carbon-aware-agent-workshop-local/carbon-aware-agent-workshop/solution/src/memory.py`
- `day-3/carbon-aware-agent-workshop-local/carbon-aware-agent-workshop/memory/profile.json`
- `day-3/carbon-aware-agent-workshop-local/carbon-aware-agent-workshop/data/mock_forecast.json`

---

## 8) Mental Model (One-Line Summary)

This is an **autonomous tool-using chat agent**: it understands your intent, reads/writes preference memory, checks forecast data, and returns a low-carbon schedule recommendation within your constraints.
