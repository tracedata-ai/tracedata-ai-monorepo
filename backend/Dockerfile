# ── Stage 1: Builder ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml .
RUN uv sync --no-dev

# ── Stage 2: Runtime ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

WORKDIR /app

# Apply Debian security updates in the runtime image.
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy backend source used by workers/API commands.
COPY . .

# Convert line endings from CRLF to LF (Windows -> Unix)
RUN sed -i 's/\r$//' entrypoint.sh && chmod +x entrypoint.sh

# Default command (overridden by docker-compose services)
CMD ["python", "-m", "api.main"]
