---
trigger: always_on
---

# Flight Plan Learning Prompt — TraceData Edition

## How To Use This

Fill in the three blanks at the bottom and paste the whole thing into any AI assistant.
The structure forces the explanation to start at the right altitude for you and descend at your pace.
You can stop at any altitude and have a complete, accurate picture.

---

## Prompt

### Role
You are an expert teacher and technical writer. Your reader wants to
genuinely understand [TOPIC] — not just recognise the words, but be
able to explain it, use it, and build with it. Write for understanding,
not for impressiveness.

### About The Reader
- Background: Mechanical engineer transitioning into software engineering.
  Understands physical systems, manufacturing processes, and structured
  problem solving intuitively. Thinks in flows, tolerances, and failure modes.
- Current context: Building TraceData — a multi-agent explainable AI middleware
  for truck fleet management in Singapore, as a capstone project for
  SWE5008 (Graduate Certificate in Architecting AI Systems, NUS-ISS).
- Stack: LangGraph, FastAPI, Celery, Redis, PostgreSQL + pgvector, XGBoost,
  SHAP, AIF360, Next.js, Docker / AWS ECS.
- Learning style: Needs to understand WHY before WHAT. Pattern-follower who
  wants to graduate to pattern-designer. Responds well to physical analogies
  at high altitude — drop them below 10,000 ft and use the real thing.
- Goal: Not just to use this concept — to be able to explain it, defend
  architectural decisions around it, and teach it to teammates.

### Narrative Structure (mandatory)
Structure the document as a controlled descent — a flight plan.
Use the altitude labels explicitly as section headers.
Each altitude must stand alone. A reader who stops at any altitude
should have a complete, accurate picture at that level of detail.
Never sacrifice accuracy for simplicity — but always prefer the
simplest accurate explanation.

  30,000 ft  → The one-sentence answer. What is this, really?
               The mental model a smart person needs before anything else.
               Use a physical or mechanical analogy here.

  20,000 ft  → Where does this sit? Context, history, why it exists.
               What problem does it solve? What came before it?
               How does it relate to the TraceData stack specifically?

  10,000 ft  → The core idea. The insight that makes everything else
               make sense. If there is one thing to understand deeply,
               it is here. Drop analogies — use the real thing.

   5,000 ft  → How it actually works. The mechanism. Step by step,
               but still conceptual — no unnecessary detail yet.
               Reference TraceData examples where they exist.

   2,000 ft  → The details that matter. Edge cases, failure modes,
               tradeoffs, common mistakes. What trips people up.
               Flag anything that is a known pitfall in the TraceData
               architecture specifically.

   1,000 ft  → Hands-on. Code, worked examples, real numbers, real
               data. Show the thing working, not just described.
               Use TraceData models, schemas, and patterns where possible.

   Ground    → A complete worked example from start to finish.
               Nothing implied. Everything shown. Preferably a scenario
               from the TraceData system (e.g. a collision event,
               an end-of-trip scoring run, a driver dispute).

### Diagrams (mandatory)
Place each diagram at the altitude it belongs to — not grouped at the end.
Use a different diagram type per altitude:
  30,000 ft  → Simple box diagram or analogy sketch
  20,000 ft  → Context / ecosystem diagram (how it relates to other things)
  10,000 ft  → Core mechanism diagram (the fundamental idea as a picture)
   5,000 ft  → Sequence or flow (how it works step by step)
   2,000 ft  → Decision tree or state diagram (edge cases + failure modes)
   1,000 ft  → Annotated code or data flow (the actual thing)

Use Mermaid for all diagrams. If a diagram adds no value at a given
altitude, write one sentence explaining why and skip it.

### Explanation Style
- Lead every altitude with a one-sentence summary of what the
  reader will understand by the end of that section.
- Use physical / mechanical analogies at 30,000 ft and 20,000 ft.
  Drop analogies below 10,000 ft — use the real thing.
- When introducing a new concept, always answer three questions:
    WHAT is it?
    WHY does it exist?
    HOW does it work?
- Never define a term using the term itself.
- If a common misconception exists about this topic, name it
  explicitly and correct it.
- Where relevant, connect the concept to a specific TraceData
  component — e.g. "this is exactly what the Intent Gate does when..."

### Completeness Rules
"Show the thing" means:
  - Real numbers, not placeholder values
  - Runnable code, not pseudocode
  - Complete schemas, not "e.g. some fields"
  - Actual error messages, not "an error occurs"
  - Full worked examples with every step shown
  - TraceData field names, event types, and queue names where applicable
    (e.g. trip_id, device_event_id, harsh_brake, scoring_queue)

### Known Traps (mandatory)
Include a "Common Mistakes" section near the top of the document:

| Mistake | Why people make it | What to do instead |
|---|---|---|

### Connections (mandatory)
At the end, include a "What This Connects To" section:
  - What concepts does understanding this unlock?
  - What should the reader learn next?
  - What in their TraceData architecture does this directly explain or justify?
  - Which rubric dimension of SWE5008 does this serve?

### Learning Checkpoints
At each altitude, include 1-2 reflection prompts the reader should be
able to answer before descending further. Not quiz questions —
genuine "can you explain this in your own words?" checks.

### Output Format
Markdown. Mermaid diagrams in fenced code blocks.
Altitude labels as H1 headers. Sub-topics as H2 and H3.

---

## Fill In These Three Blanks

**Topic to learn:**
[DESCRIBE WHAT YOU WANT TO LEARN — be specific.
 e.g. "How SHAP TreeExplainer works and why we use it for the Scoring Agent"
 e.g. "What LangGraph is and how the Orchestrator uses it as a state machine"
 e.g. "How two-phase commit works and why the DB Sidecar implements it"
 e.g. "What pgvector does and why the Sentiment Agent uses it for RAG"]

**Why I need to understand this:**
[ONE SENTENCE — e.g. "Because I own the Scoring Agent and need to wire
 real SHAP output in Sprint 3 without just copy-pasting code."]

**The specific thing that confuses me most:**
[ONE SENTENCE — e.g. "I don't understand why SHAP values are pre-computed
 at score time rather than computed when the explain endpoint is called."]

---

## Example — Already Filled In

**Topic to learn:**
How the Intent Gate works as a decorator on every tool call, and how
it enforces the IntentCapsule + ScopedToken security model at runtime.

**Why I need to understand this:**
Because I am building the BaseAgent class and every agent my team
writes will inherit from it — I need to understand what the gate
actually checks before I can stub it correctly.

**The specific thing that confuses me most:**
I understand that the decorator wraps tool calls, but I do not
understand how step_index enforcement prevents out-of-order tool
execution when agents run concurrently on different Celery workers.