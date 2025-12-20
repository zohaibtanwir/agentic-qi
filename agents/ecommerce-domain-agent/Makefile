.PHONY: all dev build test clean proto install

# Default target
all: build

# Development setup
install:
	cd service && pip install -e ".[dev]"

# Run development environment
dev:
	docker-compose up

# Run service locally
dev-service:
	cd service && python -m ecommerce_agent.main

# Run UI locally (when implemented)
dev-ui:
	cd ui && pnpm dev

# Build Docker images
build:
	docker-compose build

# Run tests
test: test-service

test-service:
	cd service && pytest

test-ui:
	cd ui && pnpm test

# Generate protobuf code
proto:
	cd service && python -m grpc_tools.protoc \
		-I./protos \
		--python_out=./src/ecommerce_agent/proto \
		--grpc_python_out=./src/ecommerce_agent/proto \
		./protos/*.proto

# Clean up
clean:
	docker-compose down -v
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf service/dist service/build service/*.egg-info