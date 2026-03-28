FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml .
RUN pip install .

# Copy everything from backend context
COPY . .

# Convert line endings from CRLF to LF (Windows → Unix)
RUN sed -i 's/\r$//' entrypoint.sh

# Make entrypoint script executable
RUN chmod +x entrypoint.sh

# Default command (will be overridden by docker-compose)
CMD ["python", "-m", "api.main"]
