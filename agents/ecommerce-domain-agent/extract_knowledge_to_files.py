#!/usr/bin/env python
"""Extract knowledge documents from Python code to organized markdown files."""

import os
import sys
import json
from pathlib import Path

# Add path for imports
sys.path.insert(0, '/Users/zohaibtanwir/projects/ecommerce-agent/service/src')

from ecommerce_agent.knowledge.documents import (
    BUSINESS_RULES_DOCUMENTS,
    EDGE_CASES_DOCUMENTS,
    TEST_SCENARIOS_DOCUMENTS,
    BEST_PRACTICES_DOCUMENTS,
    PERFORMANCE_PATTERNS_DOCUMENTS,
    SECURITY_PATTERNS_DOCUMENTS
)

# Base directory for knowledge files
KNOWLEDGE_BASE = Path("/Users/zohaibtanwir/projects/ecommerce-agent/knowledge_base")

def ensure_directories():
    """Create directory structure."""
    dirs = [
        KNOWLEDGE_BASE / "business_rules",
        KNOWLEDGE_BASE / "edge_cases",
        KNOWLEDGE_BASE / "test_scenarios",
        KNOWLEDGE_BASE / "best_practices",
        KNOWLEDGE_BASE / "performance_patterns",
        KNOWLEDGE_BASE / "security_patterns",
    ]
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
    print(f"✅ Created directory structure at {KNOWLEDGE_BASE}")

def save_business_rules():
    """Save business rules as markdown files."""
    output_dir = KNOWLEDGE_BASE / "business_rules"

    for rule in BUSINESS_RULES_DOCUMENTS:
        filename = f"{rule['rule_id']}_{rule['name'].lower().replace(' ', '_')}.md"
        filepath = output_dir / filename

        content = f"""# {rule['rule_id']}: {rule['name']}

**Entity**: {rule['entity']}
**Severity**: {rule['severity']}

## Description
{rule['description']}

## Condition
{rule['condition']}

## Constraint
{rule['constraint']}

## Validation Logic
```python
{rule['validation_logic']}
```
"""
        filepath.write_text(content)
        print(f"  📝 {filename}")

    return len(BUSINESS_RULES_DOCUMENTS)

def save_edge_cases():
    """Save edge cases as markdown files."""
    output_dir = KNOWLEDGE_BASE / "edge_cases"

    for edge_case in EDGE_CASES_DOCUMENTS:
        filename = f"{edge_case['edge_case_id']}_{edge_case['name'].lower().replace(' ', '_')}.md"
        filepath = output_dir / filename

        # Parse JSON data
        example_data = json.loads(edge_case['example_data_json'])
        example_formatted = json.dumps(example_data, indent=2)

        content = f"""# {edge_case['edge_case_id']}: {edge_case['name']}

**Category**: {edge_case['category']}
**Entity**: {edge_case['entity']}
**Workflow**: {edge_case['workflow']}
**Severity**: {edge_case['severity']}

## Description
{edge_case['description']}

## Test Approach
{edge_case['test_approach']}

## Expected Behavior
{edge_case['expected_behavior']}

## Example Test Data
```json
{example_formatted}
```
"""
        filepath.write_text(content)
        print(f"  🔍 {filename}")

    return len(EDGE_CASES_DOCUMENTS)

def save_test_scenarios():
    """Save test scenarios as markdown files."""
    output_dir = KNOWLEDGE_BASE / "test_scenarios"

    for scenario in TEST_SCENARIOS_DOCUMENTS:
        filename = f"{scenario['scenario_id']}_{scenario['name'].lower().replace(' ', '_')}.md"
        filepath = output_dir / filename

        test_data = json.dumps(scenario['test_data'], indent=2)
        success_criteria = json.dumps(scenario['success_criteria'], indent=2)

        content = f"""# {scenario['scenario_id']}: {scenario['name']}

**Entity**: {scenario['entity']}

## Description
{scenario['description']}

## Test Data
```json
{test_data}
```

## Success Criteria
```json
{success_criteria}
```
"""
        filepath.write_text(content)
        print(f"  🧪 {filename}")

    return len(TEST_SCENARIOS_DOCUMENTS)

def save_best_practices():
    """Save best practices as markdown files."""
    output_dir = KNOWLEDGE_BASE / "best_practices"

    for practice in BEST_PRACTICES_DOCUMENTS:
        filename = f"{practice['practice_id']}_{practice['title'].lower().replace(' ', '_')}.md"
        filepath = output_dir / filename

        entities = ", ".join(practice['entities'])

        content = f"""# {practice['practice_id']}: {practice['title']}

**Category**: {practice['category']}
**Impact**: {practice['impact']}
**Entities**: {entities}

## Description
{practice['description']}
"""
        filepath.write_text(content)
        print(f"  ✨ {filename}")

    return len(BEST_PRACTICES_DOCUMENTS)

def save_performance_patterns():
    """Save performance patterns as markdown files."""
    output_dir = KNOWLEDGE_BASE / "performance_patterns"

    for pattern in PERFORMANCE_PATTERNS_DOCUMENTS:
        filename = f"{pattern['pattern_id']}_{pattern['title'].lower().replace(' ', '_')}.md"
        filepath = output_dir / filename

        metrics = json.dumps(pattern['impact_metrics'], indent=2)

        content = f"""# {pattern['pattern_id']}: {pattern['title']}

**Category**: {pattern['category']}

## Description
{pattern['description']}

## Impact Metrics
```json
{metrics}
```
"""
        filepath.write_text(content)
        print(f"  ⚡ {filename}")

    return len(PERFORMANCE_PATTERNS_DOCUMENTS)

def save_security_patterns():
    """Save security patterns as markdown files."""
    output_dir = KNOWLEDGE_BASE / "security_patterns"

    for pattern in SECURITY_PATTERNS_DOCUMENTS:
        filename = f"{pattern['pattern_id']}_{pattern['title'].lower().replace(' ', '_')}.md"
        filepath = output_dir / filename

        compliance = ", ".join(pattern.get('compliance', []))

        content = f"""# {pattern['pattern_id']}: {pattern['title']}

**Category**: {pattern['category']}
**Severity**: {pattern['severity']}
**Compliance**: {compliance if compliance else 'N/A'}

## Description
{pattern['description']}
"""
        filepath.write_text(content)
        print(f"  🔒 {filename}")

    return len(SECURITY_PATTERNS_DOCUMENTS)

def create_index():
    """Create an index README file."""
    index_path = KNOWLEDGE_BASE / "README.md"

    content = """# eCommerce Domain Knowledge Base

This knowledge base contains comprehensive documentation for the eCommerce Domain Agent.

## 📚 Contents

### 📋 Business Rules
Business rules and validations that govern the eCommerce system.
- Located in: `/business_rules/`
- Format: `BR###_rule_name.md`

### 🔍 Edge Cases
Known edge cases and complex scenarios that require special handling.
- Located in: `/edge_cases/`
- Format: `EC###_case_name.md`

### 🧪 Test Scenarios
Comprehensive test scenarios for various eCommerce workflows.
- Located in: `/test_scenarios/`
- Format: `TS###_scenario_name.md`

### ✨ Best Practices
Industry best practices and recommended patterns.
- Located in: `/best_practices/`
- Format: `BP###_practice_name.md`

### ⚡ Performance Patterns
Performance optimization strategies and patterns.
- Located in: `/performance_patterns/`
- Format: `PERF###_pattern_name.md`

### 🔒 Security Patterns
Security guidelines and compliance requirements.
- Located in: `/security_patterns/`
- Format: `SEC###_pattern_name.md`

## 🔧 Usage

These documents serve as:
1. **Reference Documentation** - For understanding domain rules and constraints
2. **Test Data Generation** - Context for generating realistic test data
3. **Quality Assurance** - Guidelines for testing and validation
4. **Training Data** - For RAG (Retrieval Augmented Generation) in AI models

## 📊 Statistics

| Category | Count |
|----------|-------|
| Business Rules | 10 |
| Edge Cases | 10 |
| Test Scenarios | 5 |
| Best Practices | 5 |
| Performance Patterns | 3 |
| Security Patterns | 3 |
| **Total Documents** | **36** |

## 🚀 Integration

These documents are:
- Indexed in Weaviate vector database for semantic search
- Used by the eCommerce Domain Agent for context-aware responses
- Available for manual review and updates
- Version controlled for tracking changes

---
*Generated from eCommerce Domain Agent Knowledge Base*
"""

    index_path.write_text(content)
    print(f"\n📚 Created index at {index_path}")

def main():
    """Main extraction process."""
    print("\n🚀 Extracting Knowledge Documents to Files\n")
    print("=" * 50)

    # Create directories
    ensure_directories()

    # Extract each category
    print("\n📋 Business Rules:")
    br_count = save_business_rules()

    print(f"\n🔍 Edge Cases:")
    ec_count = save_edge_cases()

    print(f"\n🧪 Test Scenarios:")
    ts_count = save_test_scenarios()

    print(f"\n✨ Best Practices:")
    bp_count = save_best_practices()

    print(f"\n⚡ Performance Patterns:")
    pp_count = save_performance_patterns()

    print(f"\n🔒 Security Patterns:")
    sp_count = save_security_patterns()

    # Create index
    create_index()

    # Summary
    total = br_count + ec_count + ts_count + bp_count + pp_count + sp_count
    print("\n" + "=" * 50)
    print(f"\n✅ Successfully extracted {total} knowledge documents!")
    print(f"📂 Location: {KNOWLEDGE_BASE}")
    print("\nYou can now browse and review the knowledge base files.")

if __name__ == "__main__":
    main()