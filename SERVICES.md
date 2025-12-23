# QA Platform Services - Port Configuration

## IMPORTANT: FROZEN CONFIGURATION

**DO NOT CHANGE THESE PORTS.** This document defines the official port assignments for all QA Platform services. All services must start on these exact ports to ensure proper communication.

---

## Service Port Summary

| Service | Protocol | Port | Description |
|---------|----------|------|-------------|
| Frontend (Next.js) | HTTP | 3000 | Main web UI |
| Envoy Proxy | HTTP | 8085 | gRPC-Web gateway |
| Envoy Admin | HTTP | 9901 | Envoy admin interface |
| Test Data Agent | gRPC | 9091 | Test data generation service |
| Test Data Agent | HTTP | 8091 | Health/metrics endpoints |
| Test Cases Agent | gRPC | 9003 | Test case generation service |
| Test Cases Agent | HTTP | 8083 | Health/metrics endpoints |
| Weaviate | HTTP | 8080 | Vector database REST API |
| Weaviate | gRPC | 50051 | Vector database gRPC API |
| Redis | TCP | 6379 | Cache service |

---

## Service Details

### Frontend (Next.js)
- **Port:** 3000
- **Container:** `frontend`
- **URL:** http://localhost:3000
- **Dependencies:** Envoy Proxy

### Envoy Proxy (gRPC-Web Gateway)
- **Main Port:** 8085 (gRPC-Web traffic)
- **Admin Port:** 9901 (admin interface)
- **Container:** `qa-envoy`
- **URL:** http://localhost:8085
- **Admin URL:** http://localhost:9901
- **Dependencies:** Test Cases Agent, Test Data Agent

**Routes:**
- `/testcases.v1.TestCasesService/*` -> Test Cases Agent (port 9003)
- `/testdata.v1.TestDataService/*` -> Test Data Agent (port 9091)

### Test Data Agent
- **gRPC Port:** 9091
- **HTTP Port:** 8091
- **Container:** `test-data-agent`
- **gRPC URL:** localhost:9091
- **Health URL:** http://localhost:8091/health
- **Metrics URL:** http://localhost:8091/metrics
- **Dependencies:** Redis, Weaviate

### Test Cases Agent
- **gRPC Port:** 9003
- **HTTP Port:** 8083
- **Container:** `test-cases-agent`
- **gRPC URL:** localhost:9003
- **Health URL:** http://localhost:8083/health
- **Dependencies:** Weaviate

### Weaviate Vector Database
- **HTTP Port:** 8080
- **gRPC Port:** 50051
- **Container:** `qa-weaviate`
- **REST URL:** http://localhost:8080
- **Health URL:** http://localhost:8080/v1/.well-known/ready

### Redis Cache
- **Port:** 6379
- **Container:** `qa-redis`
- **URL:** redis://localhost:6379

---

## Environment Variables

### Frontend (.env.local)
```env
NEXT_PUBLIC_GRPC_WEB_URL=http://localhost:8085
NEXT_PUBLIC_TEST_DATA_AGENT_URL=http://localhost:3001
NEXT_PUBLIC_USE_MOCK=false
```

### Test Data Agent (.env)
```env
SERVICE_NAME=test-data-agent
GRPC_PORT=9091
HTTP_PORT=8091
LOG_LEVEL=INFO
ENVIRONMENT=development
ANTHROPIC_API_KEY=<your-key>
WEAVIATE_URL=http://localhost:8080
REDIS_URL=redis://localhost:6379/0
```

### Test Cases Agent (.env)
```env
GRPC_PORT=9003
HTTP_PORT=8083
ANTHROPIC_API_KEY=<your-key>
LOG_LEVEL=INFO
WEAVIATE_URL=http://localhost:8080
```

---

## Starting Services

### Development Mode (Local)

1. **Start Weaviate (Docker):**
```bash
docker run -d --name qa-weaviate \
  -p 8080:8080 -p 50051:50051 \
  -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
  -e PERSISTENCE_DATA_PATH=/var/lib/weaviate \
  -e DEFAULT_VECTORIZER_MODULE=none \
  semitechnologies/weaviate:1.24.1
```

2. **Start Envoy Proxy (Docker):**
```bash
docker run -d --name qa-envoy \
  -p 8085:8085 -p 9901:9901 \
  -v $(pwd)/envoy/envoy.yaml:/etc/envoy/envoy.yaml:ro \
  envoyproxy/envoy:v1.31-latest
```

3. **Start Test Data Agent:**
```bash
cd agents/test-data-agent
python -m test_data_agent.main
# Starts on gRPC:9091, HTTP:8091
```

4. **Start Frontend:**
```bash
cd frontend
npm run dev
# Starts on http://localhost:3000
```

### Docker Compose (Full Stack)

```bash
cd /path/to/qa-platform
docker-compose up -d
```

---

## Health Check URLs

| Service | Health Check URL |
|---------|-----------------|
| Frontend | http://localhost:3000 |
| Envoy Admin | http://localhost:9901/ready |
| Test Data Agent | http://localhost:8091/health |
| Test Cases Agent | http://localhost:8083/health |
| Weaviate | http://localhost:8080/v1/.well-known/ready |

---

## Troubleshooting

### Port Conflicts
If a port is already in use:
```bash
# Find process using port
lsof -i :PORT_NUMBER

# Kill process
kill -9 PID
```

### Verify Services
```bash
# Test gRPC services
grpcurl -plaintext localhost:9091 list  # Test Data Agent
grpcurl -plaintext localhost:9003 list  # Test Cases Agent

# Test HTTP endpoints
curl http://localhost:8091/health       # Test Data Agent
curl http://localhost:8083/health       # Test Cases Agent
curl http://localhost:8080/v1/.well-known/ready  # Weaviate
```

---

## Configuration Files

- **Docker Compose:** `/qa-platform/docker-compose.yml`
- **Envoy Config:** `/qa-platform/envoy/envoy.yaml`
- **Frontend Env:** `/qa-platform/frontend/.env.local`
- **Test Data Agent Env:** `/qa-platform/agents/test-data-agent/.env`
- **Test Cases Agent Env:** `/qa-platform/agents/test-cases-agent/.env`

---

*Last Updated: December 23, 2025*
*Status: FROZEN - Do not modify port assignments*
