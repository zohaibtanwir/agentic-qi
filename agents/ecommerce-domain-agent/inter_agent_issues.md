# Inter-Agent Communication Log

## Purpose
This file facilitates communication between domain agents and the Test Data Agent for resolving integration issues.

## Issue Format
```yaml
- id: <unique-id>
  reporter: <agent-name>
  target: <target-agent>
  status: open|resolved
  issue: <description>
  details: <technical-details>
  proposed_solution: <if-any>
  resolution: <when-resolved>
```

## Current Issues

### Issue #1: Custom Schema Processing Error
- **ID**: custom-schema-001
- **Reporter**: eCommerce Domain Agent
- **Target**: Test Data Agent
- **Status**: resolved
- **Issue**: Custom schemas failing with "'NoneType' object has no attribute 'get'"
- **Details**:
  ```json
  {
    "error": "'NoneType' object has no attribute 'get'",
    "when": "Processing custom schema for inventory entity",
    "schema_sent": {
      "name": "inventory",
      "fields": [...],
      "metadata": {...}
    }
  }
  ```
- **Resolution**: Fixed in Test Data Agent - custom schema parsing updated

## Communication Protocol

1. **Reporting Issues**:
   - Domain agents write issues to this file
   - Include full error details, sample requests, expected behavior

2. **Responding**:
   - Test Data Agent reads issues and updates status
   - Adds resolution details when fixed

3. **Testing**:
   - Reporter agent verifies fix and closes issue

## API Contract Documentation

### Custom Schema Format
Test Data Agent expects custom schemas in this format:
```json
{
  "name": "entity_name",
  "description": "Entity description",
  "fields": [
    {
      "name": "field_name",
      "type": "string|integer|number|boolean|datetime|date|object",
      "required": true|false,
      "description": "Field description",
      "example": "example_value",
      "enum": ["option1", "option2"],  // optional
      "format": "uuid|email|url"        // optional
    }
  ],
  "metadata": {
    "domain": "domain_name",
    "category": "category",
    "business_rules": [],
    "test_scenarios": []
  }
}
```

### Supported Field Types
- string
- integer
- number (decimal)
- boolean
- datetime (ISO 8601)
- date (YYYY-MM-DD)
- object (JSON object)

### Error Response Format
```json
{
  "success": false,
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "details": {
    "field": "problematic_field",
    "reason": "detailed_reason"
  }
}
```