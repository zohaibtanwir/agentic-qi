FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Copy source code
COPY src/ ./src/
COPY tests/ ./tests/

# Set Python path
ENV PYTHONPATH=/app/src

# Expose ports (gRPC: 9004, HTTP: 8084)
EXPOSE 9004 8084

# Run the agent
CMD ["python", "-m", "requirement_analysis_agent.server.main"]
