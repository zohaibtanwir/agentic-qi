# QA Platform Makefile
# Cross-agent commands for the monorepo

.PHONY: help proto up down build test health clean install lint

# Default target
help:
	@echo "QA Platform - Available Commands"
	@echo ""
	@echo "  make proto      - Regenerate gRPC code for all agents"
	@echo "  make up         - Start all agents with Docker Compose"
	@echo "  make down       - Stop all agents"
	@echo "  make build      - Build all agents"
	@echo "  make test       - Run tests for all agents"
	@echo "  make health     - Check health of all running agents"
	@echo "  make clean      - Clean build artifacts"
	@echo "  make install    - Install dependencies for all agents"
	@echo "  make lint       - Run linters for all agents"
	@echo ""
	@echo "Agent-specific:"
	@echo "  make proto-<agent>   - Regenerate proto for specific agent"
	@echo "  make test-<agent>    - Test specific agent"
	@echo "  make build-<agent>   - Build specific agent"
	@echo ""
	@echo "Beads:"
	@echo "  make bd-ready   - Show ready work"
	@echo "  make bd-list    - List all issues"
	@echo "  make bd-sync    - Sync beads database"

# ============================================================
# Proto Generation
# ============================================================

PROTO_DIR := protos
AGENTS := test-data-agent ecommerce-domain-agent test-cases-agent

# Generate protos for all agents
proto:
	@echo "🔄 Regenerating protos for all agents..."
	@for agent in $(AGENTS); do \
		echo "  → $$agent"; \
		$(MAKE) proto-$$agent; \
	done
	@echo "✅ Proto generation complete"

# Test Data Agent protos
proto-test-data-agent:
	@mkdir -p agents/test-data-agent/service/src/test_data_agent/proto
	@python -m grpc_tools.protoc \
		-I$(PROTO_DIR) \
		--python_out=agents/test-data-agent/service/src/test_data_agent/proto \
		--grpc_python_out=agents/test-data-agent/service/src/test_data_agent/proto \
		$(PROTO_DIR)/test_data.proto
	@touch agents/test-data-agent/service/src/test_data_agent/proto/__init__.py

# eCommerce Domain Agent protos
proto-ecommerce-domain-agent:
	@mkdir -p agents/ecommerce-domain-agent/service/src/ecommerce_domain_agent/proto
	@python -m grpc_tools.protoc \
		-I$(PROTO_DIR) \
		--python_out=agents/ecommerce-domain-agent/service/src/ecommerce_domain_agent/proto \
		--grpc_python_out=agents/ecommerce-domain-agent/service/src/ecommerce_domain_agent/proto \
		$(PROTO_DIR)/ecommerce_domain.proto $(PROTO_DIR)/test_data.proto
	@touch agents/ecommerce-domain-agent/service/src/ecommerce_domain_agent/proto/__init__.py

# Test Cases Agent protos (needs all three)
proto-test-cases-agent:
	@mkdir -p agents/test-cases-agent/service/src/test_cases_agent/proto
	@python -m grpc_tools.protoc \
		-I$(PROTO_DIR) \
		--python_out=agents/test-cases-agent/service/src/test_cases_agent/proto \
		--grpc_python_out=agents/test-cases-agent/service/src/test_cases_agent/proto \
		$(PROTO_DIR)/test_cases.proto $(PROTO_DIR)/test_data.proto $(PROTO_DIR)/ecommerce_domain.proto
	@touch agents/test-cases-agent/service/src/test_cases_agent/proto/__init__.py

# ============================================================
# Docker Compose
# ============================================================

up:
	@echo "🚀 Starting all agents..."
	docker-compose up -d
	@echo "✅ All agents started"
	@$(MAKE) health

down:
	@echo "🛑 Stopping all agents..."
	docker-compose down
	@echo "✅ All agents stopped"

logs:
	docker-compose logs -f

# ============================================================
# Build
# ============================================================

build:
	@echo "🔨 Building all agents..."
	@for agent in $(AGENTS); do \
		echo "  → $$agent"; \
		$(MAKE) build-$$agent; \
	done
	@echo "✅ Build complete"

build-test-data-agent:
	@cd agents/test-data-agent && docker build -t test-data-agent:latest ./service

build-ecommerce-domain-agent:
	@cd agents/ecommerce-domain-agent && docker build -t ecommerce-domain-agent:latest ./service

build-test-cases-agent:
	@cd agents/test-cases-agent && docker build -t test-cases-agent:latest ./service

# ============================================================
# Test
# ============================================================

test:
	@echo "🧪 Running tests for all agents..."
	@for agent in $(AGENTS); do \
		echo "  → $$agent"; \
		$(MAKE) test-$$agent || exit 1; \
	done
	@echo "✅ All tests passed"

test-test-data-agent:
	@cd agents/test-data-agent/service && pytest tests/ -v

test-ecommerce-domain-agent:
	@cd agents/ecommerce-domain-agent/service && pytest tests/ -v

test-test-cases-agent:
	@cd agents/test-cases-agent/service && pytest tests/ -v

# ============================================================
# Health Checks
# ============================================================

health:
	@echo "🏥 Checking agent health..."
	@echo ""
	@echo "Test Data Agent (8081):"
	@curl -s http://localhost:8081/health | jq . 2>/dev/null || echo "  ❌ Not running"
	@echo ""
	@echo "eCommerce Domain Agent (8082):"
	@curl -s http://localhost:8082/health | jq . 2>/dev/null || echo "  ❌ Not running"
	@echo ""
	@echo "Test Cases Agent (8083):"
	@curl -s http://localhost:8083/health | jq . 2>/dev/null || echo "  ❌ Not running"

# ============================================================
# Install Dependencies
# ============================================================

install:
	@echo "📦 Installing dependencies for all agents..."
	@for agent in $(AGENTS); do \
		echo "  → $$agent"; \
		cd agents/$$agent/service && pip install -e ".[dev]" && cd ../../..; \
	done
	@echo "✅ Dependencies installed"

# ============================================================
# Linting
# ============================================================

lint:
	@echo "🔍 Linting all agents..."
	@for agent in $(AGENTS); do \
		echo "  → $$agent"; \
		cd agents/$$agent/service && ruff check . && cd ../../..; \
	done
	@echo "✅ Linting complete"

# ============================================================
# Clean
# ============================================================

clean:
	@echo "🧹 Cleaning build artifacts..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Clean complete"

# ============================================================
# Beads Commands
# ============================================================

bd-ready:
	@bd ready

bd-list:
	@bd list

bd-sync:
	@bd sync
	@git add .beads/beads.jsonl
	@echo "✅ Beads synced"

bd-cross-agent:
	@echo "📋 Cross-agent issues:"
	@bd list --label-any "proto-change,ui-change,breaking" --status open

# ============================================================
# Network
# ============================================================

network:
	@docker network create qa-platform 2>/dev/null || echo "Network already exists"
