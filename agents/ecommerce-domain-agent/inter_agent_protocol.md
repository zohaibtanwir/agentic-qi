# Inter-Agent Communication Protocol

## How to Enable Direct Agent Communication

### Setup Instructions

1. **Both agents need to monitor the shared communication files:**
   - `/inter_agent_issues.md` - Human-readable communication log
   - `/inter_agent_issues.json` - Machine-readable structured data

2. **When working with Test Data Agent:**
   ```
   Tell the Test Data Agent: "Monitor /Users/zohaibtanwir/projects/ecommerce-agent/inter_agent_issues.json for issues from eCommerce Domain Agent"
   ```

3. **When working with eCommerce Domain Agent (me):**
   ```
   I will automatically check for responses and updates from Test Data Agent
   ```

### Communication Flow

1. **eCommerce Domain Agent detects issue** → Writes to inter_agent_issues.json
2. **Test Data Agent reads issue** → Investigates and fixes
3. **Test Data Agent writes resolution** → Updates status in inter_agent_issues.json
4. **eCommerce Domain Agent verifies fix** → Closes issue

### Example Workflow

```python
# In eCommerce Domain Agent
from ecommerce_agent.inter_agent.reporter import InterAgentReporter

reporter = InterAgentReporter()

# When error occurs
try:
    # Call Test Data Agent
    result = test_data_client.generate_data(...)
except Exception as e:
    # Auto-report to Test Data Agent
    issue_id = reporter.report_issue(
        error=e,
        context={"entity": "inventory", "custom_schema": schema},
        target_agent="Test Data Agent"
    )
    print(f"Issue {issue_id} reported to Test Data Agent")
```

### For You (Human Orchestrator)

To enable this communication:

1. **Tell Test Data Agent to check for issues:**
   ```
   "Check /Users/zohaibtanwir/projects/ecommerce-agent/inter_agent_issues.json for any open issues from eCommerce Domain Agent and resolve them"
   ```

2. **Tell me (eCommerce Domain Agent) to report issues automatically:**
   ```
   "Use the inter-agent reporter to automatically log issues for Test Data Agent"
   ```

3. **Both agents will then communicate through the shared file system**

### Benefits

- ✅ Agents resolve issues without human intervention
- ✅ Complete audit trail of all inter-agent communications
- ✅ Structured error reporting with context
- ✅ API contract documentation maintained automatically
- ✅ Faster issue resolution

### Current Status

The inter-agent communication system is now set up and ready to use. The next time an integration issue occurs, I will automatically:
1. Log it to the shared communication file
2. Include full context and proposed solutions
3. Wait for Test Data Agent to respond with a fix