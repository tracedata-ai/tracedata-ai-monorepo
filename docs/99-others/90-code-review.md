# TraceData AI Monorepo — Code Review

**Date:** 2026-03-20  
**Scope:** `backend/` (FastAPI API layer) and `frontend/` (Next.js application)  
**Status:** Review only — no changes made

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Backend Review](#2-backend-review)
   - [Strengths](#21-strengths)
   - [Critical Issues](#22-critical-issues)
   - [Improvement Suggestions](#23-improvement-suggestions)
3. [Frontend Review](#3-frontend-review)
   - [Strengths](#31-strengths)
   - [Issues Found](#32-issues-found)
   - [Improvement Suggestions](#33-improvement-suggestions)
4. [Security Summary](#4-security-summary)
5. [Prioritised Action Plan](#5-prioritised-action-plan)

---

## 1. Executive Summary

The TraceData codebase has a **well-thought-out foundation**: clean domain model, async-first FastAPI API, proper multi-tenant isolation, and a composable Next.js frontend. The engineering conventions (typing, docstrings, commit guidelines, structured logging) are above average for an MVP-stage project.

The main gaps are:

| Area | Gap | Risk |
|------|-----|------|
| Auth | No authentication or authorisation anywhere | 🔴 Critical |
| Enum validation | Status/severity fields are plain `str` | 🔴 High |
| CORS config | Wildcard `"*"` alongside credentials flag | 🔴 High |
| Missing pages | Routes page uses static mock data; no backend integration | 🟡 Medium |
| Frontend state | Role lost on page refresh (in-memory only) | 🟡 Medium |
| No UPDATE/DELETE | API is create + read only | 🟡 Medium |
| Test coverage | Only 4 schema smoke tests exist | 🟡 Medium |
| Placeholder data | `Math.random()` in production-bound UI paths | 🟡 Medium |

---

## 2. Backend Review

### 2.1 Strengths

- **Async-first architecture** — `asyncpg` + SQLAlchemy 2.0 async sessions + `Depends(get_db)` is the correct pattern; no blocking calls in route handlers.
- **Clean layer separation** — models (`app/models`), schemas (`app/schemas`), and routers (`app/api/v1`) are in separate packages with single responsibilities.
- **Multi-tenant safety by design** — every entity has `tenant_id` (indexed, non-null). UUID primary keys prevent sequential ID enumeration.
- **Request correlation** — `RequestIdMiddleware` propagates `X-Request-ID` through `ContextVar` into every log line. This is essential for production debugging.
- **Excellent docstrings** — `main.py`, `deps.py`, `database.py`, and the middleware are thoroughly documented; junior engineers can follow the code without a guide.
- **Settings via pydantic-settings** — all config comes from `.env`, with sensible defaults. The `@lru_cache` singleton pattern is correct.
- **`expire_on_commit=False`** on `AsyncSessionLocal` — prevents lazy-load errors when the session commits before Pydantic serialises the returned ORM object.

---

### 2.2 Critical Issues

#### C1 — No authentication or authorisation

Every endpoint is fully public. Anyone who can reach port 8000 can read or write any tenant's data. There is no JWT verification, API-key check, or session validation.

**Fix (short term):** Add a FastAPI dependency that validates a Bearer token:

```python
# app/api/deps.py  (addition)
from fastapi import Header, HTTPException, status

async def require_auth(authorization: str = Header(...)) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    token = authorization.removeprefix("Bearer ")
    # TODO: verify JWT signature with python-jose / authlib
    return token
```

Then add it to the router (or individual endpoints while testing):

```python
@router.get("/", dependencies=[Depends(require_auth)])
```

**Fix (production):** Integrate `python-jose` for JWT validation and add a `current_user` dependency that enforces `user.tenant_id == resource.tenant_id`.

---

#### C2 — CORS wildcard with `allow_credentials=True`

```python
# main.py — current (problematic)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],   # ← wildcard makes credentials flag meaningless
    allow_credentials=True,
    ...
)
```

Browsers reject `allow_credentials=True` when the origin is `"*"`. The list also contains a concrete origin and the wildcard simultaneously, which is never the correct configuration.

**Fix:**

```python
# Development
allow_origins = ["http://localhost:3000"]

# Production — read from settings
allow_origins = settings.allowed_origins  # e.g. ["https://app.tracedata.ai"]
```

Remove the `"*"` entry entirely. The wildcard is only safe on fully public, read-only endpoints with no cookies or auth headers.

---

#### C3 — Status/enum fields are unvalidated plain strings

Every model and schema uses bare `str` for status, severity, experience level, etc.:

```python
# models/driver.py — current
status: Mapped[str] = mapped_column(String(20), default="active")
experience_level: Mapped[str] = mapped_column(String(20), default="novice")
```

```python
# schemas/driver.py — current
status: str = Field("active", description="active | inactive | suspended")
experience_level: str = Field("novice", description="novice | intermediate | expert")
```

The description says what the values should be, but nothing enforces it. A client can POST `{"status": "banana"}` and it will be stored in the database.

**Fix — use Python `StrEnum` and Pydantic `Literal`:**

```python
# app/enums.py  (new file)
from enum import StrEnum

class DriverStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class ExperienceLevel(StrEnum):
    NOVICE = "novice"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"

class IssueSeverity(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
```

```python
# schemas/driver.py — improved
from app.enums import DriverStatus, ExperienceLevel

class DriverCreate(BaseModel):
    status: DriverStatus = DriverStatus.ACTIVE
    experience_level: ExperienceLevel = ExperienceLevel.NOVICE
```

Pydantic will automatically reject any value not in the enum, and OpenAPI will generate a proper `enum` dropdown in Swagger.

---

#### C4 — `email` field has no format validation

```python
# schemas/driver.py — current
email: str = Field(..., description="Driver's email address")
```

Any string passes, including `"not-an-email"`.

**Fix:**

```python
from pydantic import EmailStr

email: EmailStr = Field(..., description="Driver's email address")
```

`EmailStr` is included with `pydantic[email]` (already a transitive dependency via `pydantic-settings`).

---

#### C5 — `status_filter` query param in `list_trips` is not validated

```python
# api/v1/trips.py — current
status_filter: str | None = Query(None, alias="status")
```

A client can send `?status=invalid` and the query silently returns no rows instead of returning a 422.

**Fix:**

```python
from app.enums import TripStatus

status_filter: TripStatus | None = Query(None, alias="status")
```

---

#### C6 — `VehicleCreate.year` upper bound is year 2100

```python
year: int = Field(..., ge=1990, le=2100)
```

While not a security issue, `le=2100` is wider than necessary. A tighter upper bound such as `le=datetime.now().year + 2` would catch data entry errors sooner (e.g. someone typing `2222` instead of `2022`). This can be done with a Pydantic `@field_validator`.

---

#### C7 — `db.flush()` pattern relies on implicit commit in `get_db`

The `create_*` handlers call `db.flush()` + `db.refresh()` to get the generated `id` without committing:

```python
db.add(driver)
await db.flush()
await db.refresh(driver)
return driver
```

Commit happens in `get_db`:

```python
yield session
await session.commit()   # ← commits everything after the handler returns
```

This is correct **today**, but it means any exception raised after `flush()` and before the response is serialised will leave no trace in the DB (the rollback in `get_db` handles this). The concern is that future developers may add post-flush side effects (e.g. sending a message to Redis) that run before the commit, then get confused when the DB record disappears on error.

**Recommendation:** Add a comment in `deps.py` explaining the commit-on-yield pattern so future maintainers understand the flow, and consider adding an explicit `await session.commit()` at the end of each create handler for clarity:

```python
async def create_driver(payload: DriverCreate, db: AsyncSession = Depends(get_db)) -> Driver:
    driver = Driver(**payload.model_dump())
    db.add(driver)
    await db.flush()
    await db.refresh(driver)
    # Commit happens automatically in get_db when no exception is raised.
    return driver
```

---

#### C8 — No `UPDATE` or `DELETE` endpoints

All 7 resource routers only implement `GET list`, `GET by id`, and `POST create`. There is no way to:
- Update a trip status to `completed`
- Reassign a driver to a different vehicle
- Cancel a maintenance record
- Suspend a driver

This means even the basic CRUD lifecycle is blocked. The Behavior Agent (when implemented) will need `PATCH /trips/{id}` at minimum to write back the `safety_score` and `score_explanation`.

**Minimum additions needed:**

```python
# PATCH /trips/{trip_id} — update status and/or safety score
@router.patch("/{trip_id}", response_model=TripRead)
async def update_trip(
    trip_id: uuid.UUID,
    payload: TripUpdate,       # new schema: status?, safety_score?, score_explanation?
    db: AsyncSession = Depends(get_db),
) -> Trip:
    trip = await db.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(trip, field, value)
    await db.flush()
    await db.refresh(trip)
    return trip
```

---

#### C9 — `tenants.py` exposes all tenants with no pagination or auth check

```python
@router.get("/", response_model=list[TenantRead])
async def list_tenants(db: AsyncSession = Depends(get_db)) -> list[Tenant]:
    result = await db.execute(select(Tenant))
    return list(result.scalars().all())
```

There is no `skip`/`limit`, and no authorisation. In a multi-tenant SaaS product, tenants should not be able to discover each other's existence.

**Fix:** Add pagination and restrict to admin-only once auth is in place.

---

#### C10 — `secret_key` has a weak default

```python
# core/config.py
secret_key: str = "changeme"
```

If this default leaks into a staging or production environment (e.g. a misconfigured deployment), the whole JWT signing chain is compromised. Pydantic-settings cannot enforce a minimum entropy check on a plain `str`.

**Fix — fail fast in production:**

```python
from pydantic import field_validator

@field_validator("secret_key")
@classmethod
def secret_key_must_be_strong(cls, v: str, info: ValidationInfo) -> str:
    if info.data.get("app_env") == "production" and (not v or v == "changeme"):
        raise ValueError("secret_key must be explicitly set in production")
    return v
```

---

### 2.3 Improvement Suggestions

#### S1 — Add `OrderBy` + cursor pagination to list endpoints

All list endpoints use `OFFSET`-based pagination:

```python
query = select(Driver).offset(skip).limit(limit)
```

`OFFSET` pagination degrades at scale because the database must scan and discard `skip` rows before returning results. For the trips table (which will grow fast), this will become a bottleneck.

**Preferred approach — keyset pagination:**

```python
# Return trips created before a given cursor (UUID or timestamp)
@router.get("/")
async def list_trips(
    limit: int = Query(50, le=200),
    before: datetime | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[TripRead]:
    query = select(Trip).order_by(Trip.created_at.desc()).limit(limit)
    if before:
        query = query.where(Trip.created_at < before)
    ...
```

At minimum, add an `ORDER BY created_at DESC` to every list endpoint so the results are deterministic.

---

#### S2 — Add `total` count to list responses

Currently list endpoints return a raw JSON array. Clients cannot display "Showing 1–50 of 312 trips" without a second count query.

**Suggestion — wrap in an envelope:**

```python
class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    limit: int
    offset: int
```

Or use a `X-Total-Count` response header (simpler, avoids breaking existing consumers).

---

#### S3 — Structured error responses

FastAPI returns plain `{"detail": "Driver not found"}` for 404s. Adding a consistent error envelope makes client error handling more reliable:

```python
class ErrorResponse(BaseModel):
    code: str          # machine-readable, e.g. "DRIVER_NOT_FOUND"
    message: str       # human-readable
    request_id: str    # from ContextVar for support tickets

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            code=exc.detail.upper().replace(" ", "_"),
            message=exc.detail,
            request_id=get_request_id(),
        ).model_dump(),
    )
```

---

#### S4 — Separate read and write schemas for `Trip`

`TripRead` inherits from `TripCreate`, which means clients sending a POST body could theoretically include `safety_score` (it will be ignored by the ORM, but it leaks into the OpenAPI schema and confuses API consumers).

**Fix:**

```python
class TripBase(BaseModel):
    tenant_id: uuid.UUID
    driver_id: uuid.UUID
    vehicle_id: uuid.UUID
    route_id: uuid.UUID | None = None

class TripCreate(TripBase):
    status: TripStatus = TripStatus.ACTIVE
    # No safety_score here — it is set by the Behavior Agent only

class TripRead(TripBase):
    id: uuid.UUID
    status: TripStatus
    safety_score: Decimal | None = None
    score_explanation: str | None = None
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
```

---

#### S5 — Add `alembic` migration skeleton

`create_all()` is used on startup:

```python
async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
```

This is safe for development but will silently skip schema changes in production (it never drops or alters existing columns). `alembic` is already in `pyproject.toml` as a dependency — it just needs to be initialised:

```bash
cd backend
alembic init alembic
# Edit alembic/env.py to import Base and use the async engine
alembic revision --autogenerate -m "initial schema"
```

---

#### S6 — Route filter missing `tenant_id`

`list_routes` is the only list endpoint that does **not** accept a `tenant_id` filter:

```python
async def list_routes(skip: int = 0, limit: int = 50, db: ...) -> list[Route]:
```

If routes are shared across tenants this is intentional, but if each tenant owns its routes (as the FK on `Route.tenant_id` implies) the filter is missing.

---

#### S7 — Consider `AsyncSession.scalar_one_or_none()` for single-object fetches

```python
# Current pattern — two calls
result = await db.execute(select(Driver).where(Driver.id == driver_id))
driver = result.scalar_one_or_none()
```

The `db.get()` pattern used in the codebase is fine for primary-key lookups (it uses the identity map cache). Just make sure it is not used for filtered lookups (e.g. `db.get(Driver, email)` won't work). The current code is correct in this regard — `db.get()` is only used with PK UUID arguments.

---

## 3. Frontend Review

### 3.1 Strengths

- **Composition pattern** — `DashboardPageTemplate` and `DataTable` avoid copy-pasting layout boilerplate across all pages; adding a new data page takes ~50 lines.
- **Agent flow visualisation** — the React Flow canvas with live status simulation is a strong demo-layer feature. Using `dynamic` with `ssr: false` avoids hydration mismatches from the canvas library.
- **Proper TypeScript** — all API return types and component props are typed. No implicit `any` usage in components.
- **`useRole()` guard** — throwing an error when `useRole()` is called outside `RoleProvider` gives developers an immediate, clear failure message.
- **Skeleton loading states** — `Skeleton` components are used consistently in data pages (drivers, trips) during the loading phase.
- **`cache: "no-store"`** on all API fetches — prevents stale fleet data from being served from the Next.js data cache, which is correct for real-time telemetry.

---

### 3.2 Issues Found

#### F1 — Role is lost on page refresh

```typescript
// lib/role-context.tsx
const [role, setRole] = useState<UserRole>(null);
```

`useState` is volatile — the role resets to `null` when the user refreshes the browser. The login page lets the user choose "Fleet Manager", they land on `/fleet-manager`, and if they refresh the page the context is `null`. Any component that calls `useRole()` will receive `null` and may render incorrectly.

**Fix — persist to `sessionStorage`:**

```typescript
const [role, setRole] = useState<UserRole>(() => {
  if (typeof window === "undefined") return null;
  return (sessionStorage.getItem("role") as UserRole) ?? null;
});

const handleSetRole = (newRole: UserRole) => {
  setRole(newRole);
  if (newRole) sessionStorage.setItem("role", newRole);
  else sessionStorage.removeItem("role");
};
```

---

#### F2 — `Math.random()` used in production code path

```typescript
// fleet-manager/drivers/page.tsx
hoursToday: Math.random() * 8,   // Placeholder
```

This introduces non-determinism. Every time the drivers page is visited, hours change. It also means tests can never make deterministic assertions about the rendered value.

**Fix:** Replace with a constant placeholder or `null` until the real `hoursToday` field is available from the API. Display `"—"` or `"N/A"` in the table cell when the value is absent.

---

#### F3 — Routes page is entirely static mock data

```typescript
// fleet-manager/routes/page.tsx — current
import { routeRows } from "@/lib/sample-data";

export default function RoutesPage() {
  const stats = [{ label: "Total Routes", value: routeRows.length, ... }];
  return <DataTable columns={columns} data={routeRows} />;
}
```

The fleet-manager routes page is the only one that never calls the backend. The `GET /api/v1/routes` endpoint exists and returns real data — the frontend just does not use it.

**Fix — follow the drivers/trips pattern:**

```typescript
"use client";

import { useEffect, useState } from "react";

// Add to lib/api.ts
export type Route = {
  id: string;
  tenant_id: string;
  name: string;
  start_location: string;
  end_location: string;
  distance_km: string | null;
  route_type: string;
};
export async function getRoutes(): Promise<Route[]> {
  return apiGet<Route[]>("/routes");
}

// routes/page.tsx
export default function RoutesPage() {
  const [routes, setRoutes] = useState<Route[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getRoutes()
      .then(setRoutes)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);
  ...
}
```

---

#### F4 — No error UI for failed API calls

All data-fetch `useEffect` hooks log to the console on failure but show nothing in the UI:

```typescript
} catch (error) {
  console.error("Failed to fetch drivers:", error);
} finally {
  setLoading(false);
}
```

After the failure, the page renders with an empty table and no indication that something went wrong. Users will assume there are simply no records.

**Fix — add an `error` state:**

```typescript
const [error, setError] = useState<string | null>(null);

// in catch block:
setError("Could not load driver data. Please try again.");

// in render:
{error && (
  <div className="rounded-lg bg-red-50 border border-red-200 p-4 text-sm text-red-700">
    {error}
  </div>
)}
```

---

#### F5 — `DataTable` has a suppressed ESLint warning

```typescript
// data-table.tsx
// eslint-disable-next-line react-hooks/incompatible-library
const table = useReactTable({ ... });
```

The `react-hooks/incompatible-library` warning comes from TanStack Table v8 calling React hooks in a non-component context. This is a known false-positive for `useReactTable`. However, leaving a `disable` comment without explanation makes it easy to miss if the rule changes or if a real violation is added nearby.

**Fix — add an inline justification:**

```typescript
// eslint-disable-next-line react-hooks/incompatible-library -- TanStack Table v8 calls hooks internally; safe to disable here
const table = useReactTable({ ... });
```

---

#### F6 — `apiGet` does not attach auth headers

```typescript
async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    cache: "no-store",
  });
  ...
}
```

Once authentication is added to the backend, `apiGet` will need to include a `Bearer` token. The current shape makes this a single-place change, which is good — but it is worth flagging now so the token source (cookie, localStorage, React context) is decided before the auth layer is added.

---

#### F7 — `AppShell` page title map and `AppSidebar` navigation items are duplicated

```typescript
// app-shell.tsx
const pageTitles: Record<string, string> = {
  "/fleet-manager": "Fleet Dashboard",
  "/fleet-manager/routes": "Routes",
  ...
};

// app-sidebar.tsx
const fleetManagerItems = [
  { label: "Dashboard", href: "/fleet-manager", ... },
  { label: "Routes", href: "/fleet-manager/routes", ... },
  ...
];
```

The two lists must be kept in sync manually. Adding a new page means editing two files.

**Fix — derive titles from the navigation config:**

```typescript
// lib/nav-config.ts  (new file)
export const fleetManagerNav = [
  { label: "Fleet Dashboard", href: "/fleet-manager", icon: LayoutDashboard },
  { label: "Routes",          href: "/fleet-manager/routes", icon: Route },
  ...
] as const;

// app-shell.tsx
import { fleetManagerNav, driverNav } from "@/lib/nav-config";
const allItems = [...fleetManagerNav, ...driverNav];
const currentTitle = allItems.find(i => pathname === i.href)?.label ?? "TraceData";

// app-sidebar.tsx — import and use the same arrays
```

---

#### F8 — Login page `Select` value prop passes `null` when it should be `undefined`

```typescript
// login/page.tsx — current
<Select
  value={selectedRole || null}   // ← null is not a valid controlled value in React
  onValueChange={(value) => setSelectedRole(value ?? "")}
>
```

Passing `null` to a controlled `Select` component from `@base-ui/react` (or Radix) can cause the internal uncontrolled/controlled state warning. Controlled form inputs should use `""` (empty string) or `undefined` to represent "no selection", not `null`.

**Fix:**

```typescript
<Select
  value={selectedRole || ""}
  onValueChange={setSelectedRole}
>
```

---

#### F9 — `AgentFlowPage` uses raw HTML `<button>` elements instead of the `Button` component

```typescript
// fleet-manager/agent-flow/page.tsx
<button
  onClick={() => setKey((k) => k + 1)}
  className="flex items-center gap-1.5 rounded-md border border-[#e5e7eb] ..."
>
```

The rest of the application uses the `Button` component from `@/components/ui/button` (which wraps `@base-ui/react`). Using raw `<button>` elements bypasses the shared style token system, leading to style drift.

**Fix:**

```typescript
import { Button } from "@/components/ui/button";

<Button variant="outline" size="sm" onClick={() => setKey((k) => k + 1)}>
  <RefreshCw className="h-3 w-3" />
  Reset
</Button>
```

---

#### F10 — `AppShell` page title map is missing the `/fleet-manager/agent-flow` entry

```typescript
// app-shell.tsx — current
const pageTitles: Record<string, string> = {
  "/fleet-manager": "Fleet Dashboard",
  "/fleet-manager/routes": "Routes",
  "/fleet-manager/trips": "Trips",
  "/fleet-manager/drivers": "Drivers",
  "/fleet-manager/issues": "Issues & Incidents",
  "/fleet-manager/telemetry-simulator": "Telemetry Simulator",
  // ← /fleet-manager/agent-flow is missing
  "/driver": "Driver Portal",
  "/driver/trips": "My Trips",
};
```

Visiting `/fleet-manager/agent-flow` will fall back to `"TraceData"` in the sticky header instead of `"Agent Flow"`.

**Fix:** Add the missing entry:

```typescript
"/fleet-manager/agent-flow": "Agent Flow",
```

---

### 3.3 Improvement Suggestions

#### FS1 — Move API data types to a shared `types/` directory

Currently, frontend type definitions live in `lib/api.ts` alongside the fetch functions. As the app grows, components importing from `lib/api.ts` just to access a type create an implicit coupling to the fetch layer.

**Suggested structure:**

```
src/
  types/
    api.ts          ← Vehicle, Driver, Trip, Issue, Route, Tenant
  lib/
    api.ts          ← fetch functions only, imports from @/types/api
```

---

#### FS2 — Use `React Query` or `SWR` for data fetching

All data pages implement the same `useState + useEffect + try/catch + setLoading/setError` pattern. This boilerplate can be replaced with `@tanstack/react-query` (already partially in the dependency tree via `@tanstack/react-table`):

```typescript
// Before (manual boilerplate in every component)
const [drivers, setDrivers] = useState<DriverRow[]>([]);
const [loading, setLoading] = useState(true);
useEffect(() => { getDrivers().then(setDrivers); }, []);

// After (react-query)
const { data: drivers = [], isLoading, error } = useQuery({
  queryKey: ["drivers"],
  queryFn: getDrivers,
});
```

Benefits: built-in loading/error states, automatic refetch on window focus, request deduplication, and easy cache invalidation when mutations are added.

---

#### FS3 — Add an `<ErrorBoundary>` around route segments

If `AgentFlowCanvas` (or any other component) throws during render, the entire page goes blank. React's error boundary pattern limits the blast radius:

```typescript
// app/fleet-manager/agent-flow/layout.tsx
import { ErrorBoundary } from "react-error-boundary";

export default function AgentFlowLayout({ children }: { children: React.ReactNode }) {
  return (
    <ErrorBoundary fallback={<div>Agent flow failed to load. <button onClick={() => location.reload()}>Retry</button></div>}>
      {children}
    </ErrorBoundary>
  );
}
```

---

#### FS4 — Replace hardcoded hex colours with design tokens

The agent-flow page uses inline hex strings that are not part of the Tailwind config or CSS variables:

```typescript
// fleet-manager/agent-flow/page.tsx
className="... bg-white px-6 py-3 text-[#111827]"
// AgentNode.tsx
style={{ borderLeftColor: "#3b82f6" }}
```

These are the same colours as Tailwind's `gray-900` and `blue-500` respectively. Using Tailwind classes keeps the design system consistent and respects dark-mode overrides if added later.

---

#### FS5 — `DashboardPageTemplate` children area has a redundant `max-w-[1600px]` wrapper

```typescript
// DashboardPageTemplate.tsx
<div className="mx-auto max-w-[1600px]">     {/* ← outer */}
  ...
  <div className="max-w-[1600px]">{children}</div>  {/* ← inner — redundant */}
</div>
```

The inner `max-w-[1600px]` is inside the outer one and has no effect. Remove it.

---

#### FS6 — `fatigueRisk` computation for drivers has an incomplete mapping

```typescript
// fleet-manager/drivers/page.tsx
fatigueRisk: d.experience_level === "novice" ? "High" : "Low",
```

This only handles `"novice"` and everything else as `"Low"`, so `"intermediate"` drivers are always shown as "Low" and `"Medium"` is never emitted. The mapping should include all three experience levels:

```typescript
const fatigueMap: Record<string, DriverRow["fatigueRisk"]> = {
  novice: "High",
  intermediate: "Medium",
  expert: "Low",
};
fatigueRisk: fatigueMap[d.experience_level] ?? "Medium",
```

---

## 4. Security Summary

| # | Finding | Severity | Status |
|---|---------|----------|--------|
| 1 | No authentication — all endpoints are open | 🔴 Critical | Not fixed (needs auth layer) |
| 2 | `allow_credentials=True` with wildcard CORS origin | 🔴 High | Not fixed (see C2) |
| 3 | `secret_key` defaults to `"changeme"` | 🔴 High | Not fixed (see C10) |
| 4 | Enum fields are unvalidated plain strings | 🟡 Medium | Not fixed (see C3) |
| 5 | `tenants` endpoint exposes all tenants with no access control | 🟡 Medium | Not fixed (see C9) |
| 6 | No rate limiting on any endpoint | 🟡 Medium | Not fixed |
| 7 | Frontend role stored in memory (lost on refresh) | 🟢 Low | Not fixed (see F1) |
| 8 | SQL injection — protected by ORM parameterised queries | ✅ Safe | No action needed |
| 9 | XSS — React auto-escapes JSX, Pydantic validates input | ✅ Safe | No action needed |

---

## 5. Prioritised Action Plan

### 🔴 P0 — Do before any user testing

| Task | File(s) |
|------|---------|
| Fix CORS: remove wildcard, restrict to known origins | `backend/app/main.py` |
| Add enum validation to all schemas | `backend/app/schemas/*.py`, `backend/app/enums.py` (new) |
| Add `EmailStr` to driver schema | `backend/app/schemas/driver.py` |
| Add missing `agent-flow` entry to page title map | `frontend/src/components/app-shell.tsx` |

### 🟠 P1 — Before beta / production handoff

| Task | File(s) |
|------|---------|
| Implement JWT authentication (at minimum an API key middleware) | `backend/app/api/deps.py`, `backend/core/config.py` |
| Add `PATCH` endpoints for Trip (status + safety_score) and Driver (status) | `backend/app/api/v1/trips.py`, `drivers.py` |
| Persist role to `sessionStorage` | `frontend/src/lib/role-context.tsx` |
| Remove `Math.random()` from drivers page | `frontend/src/app/fleet-manager/drivers/page.tsx` |
| Add error UI to all data-fetch pages | All `fleet-manager/*/page.tsx` |
| Connect routes page to `GET /api/v1/routes` | `frontend/src/app/fleet-manager/routes/page.tsx` |
| Initialise Alembic migrations | `backend/alembic/` |

### 🟡 P2 — Quality-of-life improvements

| Task | File(s) |
|------|---------|
| Extract shared nav config to deduplicate `pageTitles` and nav items | `frontend/src/lib/nav-config.ts` (new) |
| Replace `Math.random()`-based fatigue with proper `experience_level` mapping | `frontend/src/app/fleet-manager/drivers/page.tsx` |
| Replace raw `<button>` in agent-flow page with `Button` component | `frontend/src/app/fleet-manager/agent-flow/page.tsx` |
| Add `ORDER BY` and keyset pagination to list endpoints | `backend/app/api/v1/*.py` |
| Add `secret_key` production validation | `backend/core/config.py` |
| Fix `Select` null value in login page | `frontend/src/app/login/page.tsx` |
| Add `tenant_id` filter to `list_routes` | `backend/app/api/v1/routes.py` |
| Add `total` count to paginated responses | `backend/app/api/v1/*.py` |
| Remove redundant inner `max-w` wrapper in `DashboardPageTemplate` | `frontend/src/components/shared/DashboardPageTemplate.tsx` |
