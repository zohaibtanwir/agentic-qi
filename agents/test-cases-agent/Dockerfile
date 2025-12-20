# Build stage
FROM python:3.11-slim as builder

WORKDIR /build

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml ./
COPY README.md ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip wheel --no-cache-dir --wheel-dir /wheels .

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN groupadd -r testcases && useradd -r -g testcases testcases

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder
COPY --from=builder /wheels /wheels

# Install Python packages
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir /wheels/* \
    && rm -rf /wheels

# Copy application code
COPY --chown=testcases:testcases . .

# Generate proto files
RUN python -m grpc_tools.protoc \
    -I./protos \
    --python_out=./src/test_cases_agent/proto \
    --grpc_python_out=./src/test_cases_agent/proto \
    ./protos/test_cases.proto \
    ./protos/test_data.proto \
    ./protos/ecommerce_domain.proto \
    && sed -i 's/^import \([a-z_]*_pb2\)/from . import \1/' src/test_cases_agent/proto/*_grpc.py

# Switch to non-root user
USER testcases

# Expose ports
EXPOSE 9003 8083 9090

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8083/health || exit 1

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    GRPC_PORT=9003 \
    HTTP_PORT=8083 \
    LOG_LEVEL=INFO

# Run the application
CMD ["python", "-m", "test_cases_agent.main"]