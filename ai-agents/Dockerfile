FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for psycopg2 and other tools
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# ENV variables for uv
ENV UV_SYSTEM_PYTHON=1
ENV UV_COMPILE_BYTECODE=1

# Copy dependencies first to leverage Docker cache
COPY pyproject.toml .

# Install dependencies
RUN uv pip install -r pyproject.toml

# Copy the rest of the application
COPY . .

# Copy and set up the entrypoint script
# (We copy it again separately to ensure permissions in some environments)
RUN chmod +x entrypoint.sh

# Expose the FastAPI port
EXPOSE 8000

# Use the entrypoint script to handle seeding and startup
ENTRYPOINT ["./entrypoint.sh"]
