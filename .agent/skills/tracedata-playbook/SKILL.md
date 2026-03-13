name: tracedata-playbook
description: The single authoritative reference for TraceData—enforces architecture (FastAPI/LangGraph), direct telemetry ingestion, and premium Next.js standards.

# TraceData Playbook: Master Index

This is the **Skill Hub** for the TraceData capstone. Detailed specifications are split into modular files for better maintainability and industry-standard documentation.

---

## 📂 Modular Sub-Files

| Module | Description | Location |
| :--- | :--- | :--- |
| **Architecture** | Core Stack, Multi-tenancy, Pipelines, MCP, Safety Intervention | [architecture.md](file:///d:/learning-projects/tracedata-ai-monorepo/.agent/skills/tracedata-playbook/architecture.md) |
| **Design System** | Philosophy, Colors, Typography, Page Templates, Component Rules | [design-system.md](file:///d:/learning-projects/tracedata-ai-monorepo/.agent/skills/tracedata-playbook/design-system.md) |
| **Implementation** | Project Structure, Component Anatomy, Agent Integration Patterns | [patterns.md](file:///d:/learning-projects/tracedata-ai-monorepo/.agent/skills/tracedata-playbook/patterns.md) |
| **Compliance** | Rubric Alignment: XRAI, Cybersecurity, Performance, A11y | [compliance.md](file:///d:/learning-projects/tracedata-ai-monorepo/.agent/skills/tracedata-playbook/compliance.md) |
| **Workflows** | Task Templates for common development flows | [workflows.md](file:///d:/learning-projects/tracedata-ai-monorepo/.agent/skills/tracedata-playbook/workflows.md) |

---

## 🔧 Core Directives for Your IDE Agent

When scaffolding or modifying code:

1. **Always verify constraints**: Confirm new services fit within Python FastAPI + LangGraph + Next.js boundary.
2. **Tenant context first**: Never process data without validated `tenant_id`.
3. **Templates, not scratch**: Use `DashboardPageTemplate`, `StatCard`, `DataTable`, and `DetailSheet`.
4. **No native buttons**: Always use `<Button />` from Shadcn.
5. **Document rubric alignment**: Every component/page should note which rubric area it addresses (XRAI, Security, etc.).
6. **Reference architecture docs**: Comment with A1–A5, A16, A20 references where applicable.
7. **Traceability first**: Ensure all agent actions write to their respective Postgres tables with the `trip_id` identifier.
8. **Explain the "why"**: Especially for scoring/predictions—use SHAP/LIME (XRAI).
9. **Accessibility & Performance**: Include ARIA labels, keyboard nav, lazy loading, and sub-500ms websocket response for safety.
10. **Maintainable Code**: Document all complex logic using JSDoc-style technical comments (Frontend) or Google-style docstrings (Backend).
11. **Self-Documenting APIs**: Use Pydantic `Field` metadata descriptions to ensure Swagger/OpenAPI documentation is rich and actionable.

---

**Last Updated**: March 2026
**For**: TraceData Capstone Project
