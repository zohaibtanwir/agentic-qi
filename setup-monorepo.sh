#!/bin/bash
# QA Platform Monorepo Setup Script
# Run this from /Users/zohaibtanwir/projects/

set -e

echo "🚀 Setting up QA Platform Monorepo..."

# Create main directory
mkdir -p qa-platform
cd qa-platform

# Initialize git
git init

# Create directory structure
echo "📁 Creating directory structure..."
mkdir -p protos
mkdir -p packages/design-system/src/tokens/themes
mkdir -p packages/design-system/src/components
mkdir -p agents
mkdir -p docs/ADR
mkdir -p scripts

# Create .gitignore
cat > .gitignore << 'EOF'
# Dependencies
node_modules/
__pycache__/
*.pyc
.venv/
venv/

# Build outputs
dist/
build/
*.egg-info/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Environment
.env
.env.local
*.local

# Beads (local only)
.beads/beads.db
.beads/beads.db-*
.beads/bd.sock
.beads/bd.pipe
.beads/.exclusive-lock

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Test coverage
.coverage
htmlcov/
.pytest_cache/

# Generated proto files (keep source, ignore generated)
*_pb2.py
*_pb2_grpc.py
*_pb2.pyi
EOF

echo "✅ Created .gitignore"

# Placeholder for agents (will be populated by migration)
touch agents/.gitkeep

echo ""
echo "📋 Next Steps:"
echo "1. Copy your existing agents into the agents/ directory:"
echo "   cp -r ../test_data_agent ./agents/test-data-agent"
echo "   cp -r ../ecommerce-agent ./agents/ecommerce-domain-agent"
echo "   cp -r ../test-cases-agent ./agents/test-cases-agent"
echo ""
echo "2. Copy your proto files to protos/:"
echo "   cp agents/*/protos/*.proto ./protos/"
echo ""
echo "3. Initialize beads:"
echo "   bd init --quiet"
echo ""
echo "4. Initial commit:"
echo "   git add -A"
echo "   git commit -m 'Initialize QA Platform monorepo'"
echo ""
echo "🎉 Monorepo structure ready!"
EOF
