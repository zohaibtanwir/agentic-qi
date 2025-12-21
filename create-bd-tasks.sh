#!/bin/bash

# Frontend tasks (continuing)
bd create --type task --priority P1 --labels "frontend,ui" --parent "test-cases-agent-uzh" --title "Task 7.4: Create Layout Components" --description "Build Header, Sidebar, Footer components with navigation"

bd create --type task --priority P1 --labels "frontend,ui" --parent "test-cases-agent-uzh" --title "Task 7.5: Build Dashboard Page" --description "Create main dashboard with agent status cards and quick actions"

bd create --type task --priority P1 --labels "frontend,ui,test-data-agent" --parent "test-cases-agent-uzh" --title "Task 7.6: Build Test Data Agent View" --description "Create UI for data generation form, schema selector, and preview"

bd create --type task --priority P1 --labels "frontend,ui,test-cases-agent" --parent "test-cases-agent-uzh" --title "Task 7.7: Build Test Cases Agent View" --description "Create UI for test case generation, list view, and coverage visualization"

bd create --type task --priority P1 --labels "frontend,ui,ecommerce-domain-agent" --parent "test-cases-agent-uzh" --title "Task 7.8: Build eCommerce Domain Agent View" --description "Create UI for domain context, business rules, and edge cases display"

bd create --type task --priority P2 --labels "frontend,api" --parent "test-cases-agent-uzh" --title "Task 7.9: Implement State Management" --description "Set up React Query for server state management"

bd create --type task --priority P2 --labels "frontend,ui" --parent "test-cases-agent-uzh" --title "Task 7.10: Add Error Handling & Loading States" --description "Implement error boundaries, loading spinners, and toast notifications"

bd create --type task --priority P2 --labels "frontend,testing" --parent "test-cases-agent-uzh" --title "Task 7.11: Frontend Integration Testing" --description "Test UI with all backend agents, fix integration issues"

# Documentation epic and tasks
DOCS_EPIC=$(bd create --type epic --priority P1 --labels "documentation" --title "Phase 8: Documentation" --silent)

bd create --type task --priority P1 --labels "documentation,setup" --parent "$DOCS_EPIC" --title "Task 8.1: Create docs Folder Structure" --description "Set up docs/ folder with prd/, architecture/, api/, guides/, tasks/, decisions/, deployment/, troubleshooting/, changelog/"

bd create --type task --priority P1 --labels "documentation,architecture" --parent "$DOCS_EPIC" --title "Task 8.2: Write Platform Overview Documentation" --description "Create comprehensive platform overview, system design, and architecture docs"

bd create --type task --priority P1 --labels "documentation,api" --parent "$DOCS_EPIC" --title "Task 8.3: Write API Documentation" --description "Document all gRPC APIs with examples for each agent"

bd create --type task --priority P1 --labels "documentation,guides" --parent "$DOCS_EPIC" --title "Task 8.4: Write Getting Started Guide" --description "Create setup and development guides for new developers"

bd create --type task --priority P2 --labels "documentation,prd" --parent "$DOCS_EPIC" --title "Task 8.5: Write PRD Documents" --description "Create PRD documents for platform, each agent, and frontend"

bd create --type task --priority P2 --labels "documentation,decisions" --parent "$DOCS_EPIC" --title "Task 8.6: Create Architecture Decision Records" --description "Document key technology decisions (gRPC, Python, Next.js, etc.)"

bd create --type task --priority P2 --labels "documentation,deployment" --parent "$DOCS_EPIC" --title "Task 8.7: Write Deployment Documentation" --description "Create Docker, K8s, and production deployment guides"

bd create --type task --priority P3 --labels "documentation,support" --parent "$DOCS_EPIC" --title "Task 8.8: Create Troubleshooting Guide" --description "Document common errors, debugging steps, and FAQ"

# Platform Integration epic and tasks
PLATFORM_EPIC=$(bd create --type epic --priority P1 --labels "deployment,integration" --title "Phase 9: Platform Integration & Deployment" --silent)

bd create --type task --priority P1 --labels "deployment,docker" --parent "$PLATFORM_EPIC" --title "Task 9.1: Create Docker Compose Configuration" --description "Set up docker-compose.yml for all agents + frontend + Weaviate"

bd create --type task --priority P2 --labels "backend,api" --parent "$PLATFORM_EPIC" --title "Task 9.2: Add REST Proxy Layer (Optional)" --description "Create REST API proxies for easier browser communication (alternative to gRPC-Web)"

bd create --type task --priority P2 --labels "devops,tools" --parent "$PLATFORM_EPIC" --title "Task 9.3: Create Utility Scripts" --description "Create start-all-agents.sh, stop-all-agents.sh, setup-dev.sh scripts"

bd create --type task --priority P2 --labels "devops,ci-cd" --parent "$PLATFORM_EPIC" --title "Task 9.4: Set Up CI/CD Pipeline" --description "Configure GitHub Actions for testing, building, and deployment"

bd create --type task --priority P3 --labels "deployment,kubernetes" --parent "$PLATFORM_EPIC" --title "Task 9.5: Create Kubernetes Manifests" --description "Create K8s deployments, services, and ingress configurations"

bd create --type task --priority P1 --labels "testing,integration" --parent "$PLATFORM_EPIC" --title "Task 9.6: End-to-End Platform Testing" --description "Test complete platform flow: UI → Test Cases Agent → Domain Agent → Test Data Agent"

bd create --type task --priority P3 --labels "optimization,performance" --parent "$PLATFORM_EPIC" --title "Task 9.7: Performance Optimization" --description "Optimize agent response times, add caching, and improve LLM prompts"

bd create --type task --priority P2 --labels "security,audit" --parent "$PLATFORM_EPIC" --title "Task 9.8: Security Audit" --description "Review API security, add authentication/authorization if needed"

echo "All tasks created successfully!"
