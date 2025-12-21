# Test Cases Agent - gRPC Test Commands

## Prerequisites
1. Install grpcurl: `brew install grpcurl` (macOS) or download from https://github.com/fullstorydev/grpcurl
2. Start the Test Cases Agent service: `PYTHONPATH=./src ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY} python -m test_cases_agent.main`

## Health Check
```bash
# Check service health
grpcurl -plaintext localhost:9003 testcases.v1.TestCasesService/HealthCheck

# Alternative: HTTP health check
curl http://localhost:8083/health
```

## Generate Test Cases

### Simple Free-form Test Case Generation
```bash
grpcurl -plaintext -d '{
  "request_id": "test_001",
  "free_form": {
    "requirement": "Create test cases for user login functionality with email and password",
    "context": {
      "entity_type": "user",
      "workflow": "authentication"
    }
  },
  "generation_config": {
    "count": 3,
    "detail_level": "medium",
    "include_edge_cases": true,
    "include_negative_tests": true
  }
}' localhost:9003 testcases.v1.TestCasesService/GenerateTestCases
```

### Generate Test Cases from User Story
```bash
grpcurl -plaintext -d '{
  "request_id": "test_002",
  "user_story": {
    "story": "As a user, I want to reset my password via email so that I can regain access to my account",
    "acceptance_criteria": [
      "User can request password reset from login page",
      "System sends reset link to registered email",
      "Link expires after 24 hours",
      "User can set new password using the link"
    ]
  },
  "generation_config": {
    "test_types": ["FUNCTIONAL", "SECURITY"],
    "count": 5,
    "priority_focus": "high",
    "detail_level": "high"
  }
}' localhost:9003 testcases.v1.TestCasesService/GenerateTestCases
```

### Generate Test Cases with Domain Context
```bash
grpcurl -plaintext -d '{
  "request_id": "test_003",
  "free_form": {
    "requirement": "Test shopping cart checkout process",
    "context": {
      "entity_type": "cart",
      "workflow": "checkout"
    }
  },
  "domain_config": {
    "domain": "ecommerce",
    "entity": "cart",
    "workflow": "checkout",
    "include_business_rules": true,
    "include_edge_cases": true
  },
  "generation_config": {
    "test_types": ["FUNCTIONAL", "BOUNDARY", "EDGE_CASE"],
    "count": 7,
    "include_edge_cases": true,
    "include_negative_tests": true,
    "detail_level": "high"
  }
}' localhost:9003 testcases.v1.TestCasesService/GenerateTestCases
```

### Generate API Test Cases
```bash
grpcurl -plaintext -d '{
  "request_id": "test_004",
  "api_spec": {
    "spec": "{\"openapi\": \"3.0.0\", \"paths\": {\"/users\": {\"post\": {\"summary\": \"Create user\", \"requestBody\": {\"content\": {\"application/json\": {\"schema\": {\"type\": \"object\", \"properties\": {\"email\": {\"type\": \"string\"}, \"password\": {\"type\": \"string\"}}}}}}, \"responses\": {\"201\": {\"description\": \"User created\"}}}}}}",
    "spec_format": "openapi",
    "endpoints": ["/users"]
  },
  "generation_config": {
    "test_types": ["FUNCTIONAL", "SECURITY", "NEGATIVE"],
    "count": 6,
    "detail_level": "high"
  }
}' localhost:9003 testcases.v1.TestCasesService/GenerateTestCases
```

## List Available Methods (with Reflection)
```bash
# List all available services
grpcurl -plaintext localhost:9003 list

# Describe service methods
grpcurl -plaintext localhost:9003 describe testcases.v1.TestCasesService

# Show proto definition for a specific message
grpcurl -plaintext localhost:9003 describe testcases.v1.GenerateTestCasesRequest
```

## Get Test Case by ID
```bash
grpcurl -plaintext -d '{
  "test_case_id": "TC-001"
}' localhost:9003 testcases.v1.TestCasesService/GetTestCase
```

## List Test Cases
```bash
grpcurl -plaintext -d '{
  "domain": "ecommerce",
  "entity": "cart",
  "type": "FUNCTIONAL",
  "limit": 10,
  "offset": 0
}' localhost:9003 testcases.v1.TestCasesService/ListTestCases
```

## Store Test Cases (for Learning)
```bash
grpcurl -plaintext -d '{
  "test_cases": [
    {
      "id": "TC-MANUAL-001",
      "title": "Verify successful user login",
      "description": "Test that users can login with valid credentials",
      "type": "FUNCTIONAL",
      "priority": "HIGH",
      "steps": [
        {
          "order": 1,
          "action": "Navigate to login page",
          "expected_result": "Login page is displayed",
          "test_data": "{\"url\": \"/login\"}"
        },
        {
          "order": 2,
          "action": "Enter valid email and password",
          "expected_result": "Credentials are accepted",
          "test_data": "{\"email\": \"test@example.com\", \"password\": \"Test123!\"}"
        },
        {
          "order": 3,
          "action": "Click login button",
          "expected_result": "User is redirected to dashboard",
          "test_data": ""
        }
      ],
      "tags": ["login", "authentication"]
    }
  ],
  "domain": "authentication",
  "entity": "user",
  "source": "manual"
}' localhost:9003 testcases.v1.TestCasesService/StoreTestCases
```

## Analyze Test Coverage
```bash
grpcurl -plaintext -d '{
  "request_id": "coverage_001",
  "user_story": {
    "story": "As a user, I want to search for products by category",
    "acceptance_criteria": [
      "User can select category from dropdown",
      "Search results show only products from selected category",
      "User can clear category filter"
    ]
  },
  "existing_test_case_ids": ["TC-001", "TC-002", "TC-003"]
}' localhost:9003 testcases.v1.TestCasesService/AnalyzeCoverage
```

## Notes

1. The service uses reflection, so you can discover available methods and message formats using grpcurl's `list` and `describe` commands.

2. The `generation_config` field supports these test types:
   - FUNCTIONAL: Happy path and expected behavior tests
   - NEGATIVE: Invalid inputs and error handling tests
   - BOUNDARY: Min/max values and limit tests
   - EDGE_CASE: Unusual scenario tests
   - SECURITY: Security-related tests
   - PERFORMANCE: Performance scenario tests

3. Priority levels (for priority_focus):
   - CRITICAL: Must-test, blocks release
   - HIGH: Important, should be tested
   - MEDIUM: Standard priority
   - LOW: Nice to have

4. Detail levels:
   - low: Basic test cases with minimal steps
   - medium: Standard detail with clear steps
   - high: Comprehensive test cases with detailed steps and data

5. The service integrates with:
   - Multiple LLM providers (Anthropic, OpenAI, Gemini)
   - Domain Agent for business context
   - Test Data Agent for data generation
   - Weaviate for test case storage and retrieval