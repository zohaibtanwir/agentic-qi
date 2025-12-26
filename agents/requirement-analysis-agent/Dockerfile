FROM python:3.13-slim

WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app/src

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files (src needed before pip install -e .)
COPY pyproject.toml ./
COPY README.md ./
COPY src/ ./src/

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -e .

# Copy tests
COPY tests/ ./tests/

# Expose ports (gRPC: 9004, HTTP: 8084)
EXPOSE 9004 8084

# Run the agent
CMD ["python", "-m", "requirement_analysis_agent.server.main"]
