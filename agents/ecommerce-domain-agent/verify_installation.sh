#!/bin/bash

echo "🔍 eCommerce Domain Agent - Installation Verification"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Python is installed
echo "1. Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo -e "   ${GREEN}✓${NC} Python installed: $PYTHON_VERSION"
else
    echo -e "   ${RED}✗${NC} Python not found"
    exit 1
fi

# Check if required directories exist
echo ""
echo "2. Checking project structure..."
DIRS=("service/src/ecommerce_agent" "service/protos" "service/tests")
for dir in "${DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "   ${GREEN}✓${NC} Directory exists: $dir"
    else
        echo -e "   ${RED}✗${NC} Directory missing: $dir"
    fi
done

# Check if proto files exist
echo ""
echo "3. Checking proto files..."
if [ -f "service/protos/ecommerce_domain.proto" ]; then
    echo -e "   ${GREEN}✓${NC} ecommerce_domain.proto exists"
else
    echo -e "   ${RED}✗${NC} ecommerce_domain.proto missing"
fi

# Check if generated proto files exist
echo ""
echo "4. Checking generated protobuf files..."
PROTO_FILES=("ecommerce_domain_pb2.py" "ecommerce_domain_pb2_grpc.py")
for file in "${PROTO_FILES[@]}"; do
    if [ -f "service/src/ecommerce_agent/proto/$file" ]; then
        echo -e "   ${GREEN}✓${NC} Generated file exists: $file"
    else
        echo -e "   ${RED}✗${NC} Generated file missing: $file"
    fi
done

# Check if Docker files exist
echo ""
echo "5. Checking Docker configuration..."
if [ -f "docker-compose.yml" ] && [ -f "service/Dockerfile" ]; then
    echo -e "   ${GREEN}✓${NC} Docker files present"
else
    echo -e "   ${RED}✗${NC} Docker files missing"
fi

# Run Python tests
echo ""
echo "6. Running unit tests..."
cd service 2>/dev/null || cd .
python3 -m pytest tests/unit -q 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "   ${GREEN}✓${NC} All tests passing"
else
    echo -e "   ${RED}✗${NC} Some tests failing"
fi

# Test server initialization
echo ""
echo "7. Testing server initialization..."
python3 test_server.py 2>/dev/null | grep -q "All components initialized successfully"
if [ $? -eq 0 ]; then
    echo -e "   ${GREEN}✓${NC} Server initializes correctly"
else
    echo -e "   ${RED}✗${NC} Server initialization failed"
fi

echo ""
echo "=================================================="
echo "Verification complete!"
echo ""
echo "To start the service:"
echo "  - Local: cd service && python -m ecommerce_agent.main"
echo "  - Docker: docker-compose up"
echo ""
echo "Service endpoints:"
echo "  - gRPC: localhost:9002"
echo "  - Health: http://localhost:8082/health"