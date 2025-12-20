"""Inter-agent communication and error reporting system."""

import json
import traceback
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path

from ecommerce_agent.utils.logging import get_logger

logger = get_logger(__name__)

class InterAgentReporter:
    """Handles communication between domain agents and Test Data Agent."""

    def __init__(self, agent_name: str = "eCommerce Domain Agent"):
        self.agent_name = agent_name
        self.issues_file = Path("/Users/zohaibtanwir/projects/ecommerce-agent/inter_agent_issues.json")
        self._ensure_issues_file()

    def _ensure_issues_file(self):
        """Ensure the issues file exists."""
        if not self.issues_file.exists():
            self.issues_file.write_text(json.dumps({
                "issues": [],
                "api_contracts": {},
                "communication_log": []
            }, indent=2))

    def report_issue(
        self,
        error: Exception,
        context: Dict[str, Any],
        target_agent: str = "Test Data Agent"
    ) -> str:
        """Report an issue to another agent."""
        issue_id = f"{self.agent_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        issue = {
            "id": issue_id,
            "reporter": self.agent_name,
            "target": target_agent,
            "timestamp": datetime.now().isoformat(),
            "status": "open",
            "error": {
                "message": str(error),
                "type": type(error).__name__,
                "traceback": traceback.format_exc()
            },
            "context": context,
            "proposed_solution": self._analyze_error(error, context)
        }

        # Load existing issues
        data = json.loads(self.issues_file.read_text())
        data["issues"].append(issue)

        # Add to communication log
        data["communication_log"].append({
            "timestamp": datetime.now().isoformat(),
            "from": self.agent_name,
            "to": target_agent,
            "action": "reported_issue",
            "issue_id": issue_id
        })

        # Save updated data
        self.issues_file.write_text(json.dumps(data, indent=2))

        logger.info(
            "Reported inter-agent issue",
            issue_id=issue_id,
            target=target_agent,
            error=str(error)
        )

        return issue_id

    def _analyze_error(self, error: Exception, context: Dict[str, Any]) -> Optional[str]:
        """Analyze error and propose solution."""
        error_msg = str(error)

        if "'NoneType' object has no attribute 'get'" in error_msg:
            return "Custom schema parsing issue - check JSON deserialization and None checks"
        elif "DNS resolution failed" in error_msg:
            return "Connection issue - verify service is running and accessible"
        elif "timeout" in error_msg.lower():
            return "Increase timeout or optimize generation for large requests"
        elif "invalid schema" in error_msg.lower():
            return "Schema validation issue - verify field types and required fields"

        return None

    def check_issues_status(self) -> Dict[str, Any]:
        """Check status of reported issues."""
        data = json.loads(self.issues_file.read_text())

        open_issues = [i for i in data["issues"] if i["status"] == "open"]
        resolved_issues = [i for i in data["issues"] if i["status"] == "resolved"]

        return {
            "total_issues": len(data["issues"]),
            "open": len(open_issues),
            "resolved": len(resolved_issues),
            "open_issues": open_issues
        }

    def update_api_contract(self, contract_name: str, contract_data: Dict[str, Any]):
        """Update API contract documentation."""
        data = json.loads(self.issues_file.read_text())
        data["api_contracts"][contract_name] = {
            "updated_by": self.agent_name,
            "timestamp": datetime.now().isoformat(),
            "contract": contract_data
        }
        self.issues_file.write_text(json.dumps(data, indent=2))

        logger.info(
            "Updated API contract",
            contract=contract_name,
            agent=self.agent_name
        )

    def get_api_contract(self, contract_name: str) -> Optional[Dict[str, Any]]:
        """Get API contract details."""
        data = json.loads(self.issues_file.read_text())
        return data["api_contracts"].get(contract_name)


# Usage example in the orchestrator when an error occurs:
def handle_test_data_agent_error(error: Exception, request_context: Dict[str, Any]):
    """Handle and report Test Data Agent errors."""
    reporter = InterAgentReporter()

    # Report the issue
    issue_id = reporter.report_issue(
        error=error,
        context={
            "request": request_context,
            "entity": request_context.get("entity"),
            "custom_schema": request_context.get("custom_schema"),
            "generation_method": request_context.get("generation_method")
        },
        target_agent="Test Data Agent"
    )

    # Log for monitoring
    logger.error(
        "Test Data Agent error reported",
        issue_id=issue_id,
        error=str(error)
    )

    return issue_id