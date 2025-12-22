#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "=========================================="
echo "  QA Platform - Starting All Services"
echo "=========================================="

# Check for .env file
if [ ! -f .env ]; then
    echo "Warning: .env file not found."
    echo "Please create .env with ANTHROPIC_API_KEY"
fi

# Start with Docker Compose
if command -v docker-compose &> /dev/null; then
    echo "Starting services with docker-compose..."
    docker-compose up -d
elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
    echo "Starting services with docker compose..."
    docker compose up -d
else
    echo "Docker not found. Starting services manually..."
    
    # Start Test Cases Agent
    echo "Starting Test Cases Agent..."
    cd "$PROJECT_ROOT/agents/test-cases-agent"
    python -m test_cases_agent.main &
    AGENT_PID=$!
    echo "  Test Cases Agent PID: $AGENT_PID"
    
    sleep 3
    
    # Start Frontend
    echo "Starting Frontend..."
    cd "$PROJECT_ROOT/frontend"
    npm run dev &
    FRONTEND_PID=$!
    echo "  Frontend PID: $FRONTEND_PID"
    
    echo ""
    echo "Services started manually (no Envoy proxy)"
    echo "Press Ctrl+C to stop"
    
    trap "kill $AGENT_PID $FRONTEND_PID 2>/dev/null" EXIT
    wait
    exit 0
fi

echo ""
echo "=========================================="
echo "  Services Started Successfully!"
echo "=========================================="
echo ""
echo "  Frontend:         http://localhost:3000"
echo "  Envoy Proxy:      http://localhost:8080"
echo "  Test Cases Agent: localhost:9003 (gRPC)"
echo "  Weaviate:         http://localhost:8084"
echo ""
echo "Use './scripts/stop-all.sh' to stop all services"
