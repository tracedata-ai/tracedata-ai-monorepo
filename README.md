# TraceData AI Monorepo

AI-powered platform for tracing, auditing, and governing machine-learning pipelines.

## Project Structure

```
tracedata-ai-monorepo/
├── frontend/        # Next.js 16 (React 19, Tailwind CSS)
├── backend/         # FastAPI (Python)
├── core-platform/   # Java 17 + Spring Boot (modular monolith)
└── docker-compose.yml
```

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Engine ≥ 24)
- Docker Compose v2 (`docker compose` — note: no hyphen)

---

## Running with Docker Compose

### Frontend only (standalone)

Starts **only** the Next.js frontend. No backend or database required.

```bash
docker compose up frontend --build
```

Open → [http://localhost:3000](http://localhost:3000)

> **Note:** `NEXT_PUBLIC_*` environment variables are baked into the JS bundle at build time.
> The default API URL is `http://localhost:8000`. Override it before building if needed:
>
> ```bash
> NEXT_PUBLIC_API_URL=http://my-backend docker compose up frontend --build
> ```

---

### Full stack (frontend + backend + database)

Starts all services using the `full` profile.

```bash
docker compose --profile full up --build
```

| Service  | URL                         |
| -------- | --------------------------- |
| Frontend | http://localhost:3000       |
| Backend  | http://localhost:8000       |
| Postgres | `localhost:5432` (internal) |

---

### Useful commands

```bash
# Stop all running containers
docker compose --profile full down

# Stop and remove volumes (wipes the database)
docker compose --profile full down -v

# View logs for the frontend only
docker compose logs -f frontend

# Rebuild a single service without cache
docker compose build --no-cache frontend
```

---

## Local Development (without Docker)

```bash
# Frontend
cd frontend
npm install
npm run dev        # http://localhost:3000

# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload   # http://localhost:8000
```

---

## Environment Variables

Copy `frontend/.env.example` to `frontend/.env.local` for local development:

```bash
cp frontend/.env.example frontend/.env.local
```

| Variable                     | Default                 | Description          |
| ---------------------------- | ----------------------- | -------------------- |
| `NEXT_PUBLIC_API_URL`        | `http://localhost:8000` | Backend API base URL |
| `NEXT_PUBLIC_ENABLE_CHATBOT` | `true`                  | Toggle chatbot UI    |
| `NEXT_PUBLIC_AUTH_DOMAIN`    | `auth.tracedata.ai`     | Auth service domain  |
