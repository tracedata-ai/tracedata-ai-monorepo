# ─────────────────────────────────────────────────────────────────────────────
#  TraceData.ai Backend — Dockerfile
#
#  Multi-stage build:
#    Stage 1 (builder): installs all deps including gcc for C extensions
#    Stage 2 (runtime): slim image with only installed packages, no build tools
#
#  WHY MULTI-STAGE?
#    aif360 and psycopg2-binary require C++ compilation. The gcc toolchain adds
#    ~400MB. Multi-stage gives us the compiled output without the bloat in the
#    final image — smaller attack surface, faster pulls.
# ─────────────────────────────────────────────────────────────────────────────

# ── Stage 1: Build ────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# System build deps for:
#   - psycopg2-binary: libpq-dev
#   - aif360 / numpy: gcc, g++
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: Runtime ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

WORKDIR /app

# Runtime system deps (libpq for asyncpg connection)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy compiled packages from builder — no gcc in final image
COPY --from=builder /install /usr/local

# Copy application source
COPY app/ ./app/

# Non-root user — never run containers as root in prod
RUN useradd --create-home --shell /bin/bash --uid 1001 appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Single uvicorn worker in dev.
# In prod: gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
