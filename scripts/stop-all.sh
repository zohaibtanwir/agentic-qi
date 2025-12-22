#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "=========================================="
echo "  QA Platform - Stopping All Services"
echo "=========================================="

# Stop with Docker Compose
if command -v docker-compose &> /dev/null; then
    echo "Stopping services with docker-compose..."
    docker-compose down
elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
    echo "Stopping services with docker compose..."
    docker compose down
else
    echo "Docker not found. Stopping manual processes..."
    pkill -f "test_cases_agent.main" 2>/dev/null || true
    pkill -f "next dev" 2>/dev/null || true
    pkill -f "next start" 2>/dev/null || true
fi

echo ""
echo "All services stopped."
