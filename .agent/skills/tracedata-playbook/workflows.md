# TraceData Workflows

Standardized templates for common development tasks.

## Task 1: Create a New Dashboard Page

1. Use `DashboardPageTemplate`.
2. Add stats via `StatCard`.
3. Use `DataTable` for lists.
4. Implement `DetailSheet` for row clicks.

## Task 2: Integrate a New Agent

1. Define request/response types in `lib/types/agents.ts`.
2. Create an API proxy in `pages/api/`.
3. Implement an "Agent-Aware" component in `components/agents/`.
4. Add XRAI (SHAP/LIME) if the agent provides scoring or predictions.

## Task 3: Add Safety Intervention

1. Add level-based UI logic (Urgency-based coloring).
2. Hook into `useSafetyAlerts` WebSocket.
3. Ensure sub-500ms notification display.

## Task 4: Create a New Backend Module (Python)

1. Place code within the correct `ai-agents/app/` subdirectory.
2. Add a **Module Docstring** at the top of the file.
3. Use **Pydantic Field Metadata** for all schema attributes.
4. Add **Google-style Docstrings** to all functions and classes.
5. Export components through `__init__.py` if part of a sub-package.
