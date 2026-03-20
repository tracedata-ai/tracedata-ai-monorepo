name: tracedata-playbook
description: The single authoritative reference for TraceData—enforces architecture (FastAPI/LangGraph), direct telemetry ingestion, caching strategy (cache-aside, Redis TTL, invalidation), and premium Next.js standards.

# TraceData Playbook: Master Index

This is the **Skill Hub** for the TraceData capstone. Detailed specifications are split into modular files for better maintainability and industry-standard documentation.

---

## 📂 Modular Sub-Files

| Module             | Description                                                      | Location                               |
| :----------------- | :--------------------------------------------------------------- | :------------------------------------- |
| **Architecture**   | Core Stack, Multi-tenancy, Pipelines, MCP, Safety Intervention   | [architecture.md](./architecture.md)   |
| **Caching**        | Cache-Aside pattern, Redis TTL policy, strict invalidation rules | [caching.md](./caching.md)             |
| **Design System**  | Philosophy, Colors, Typography, Page Templates, Component Rules  | [design-system.md](./design-system.md) |
| **Implementation** | Project Structure, Component Anatomy, Agent Integration Patterns | [patterns.md](./patterns.md)           |
| **Compliance**     | Rubric Alignment: XRAI, Cybersecurity, Performance, A11y         | [compliance.md](./compliance.md)       |
| **Workflows**      | Task Templates for common development flows                      | [workflows.md](./workflows.md)         |

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
12. **Cache-Aside discipline**: For cacheable reads, check Redis first, then Postgres on miss, then backfill Redis with TTL.
13. **Strict invalidation on writes**: After successful update/delete/patch commits, invalidate affected Redis keys.
14. **TTL is mandatory**: Every Redis key must have expiration. Default 60 minutes, critical fast-moving state 5 minutes.
15. **Scope of caching**: Cache lookup data, auth/session state, and active trip summaries; do not cache high-volume telemetry history.

---

**Last Updated**: March 2026
**For**: TraceData Capstone Project
