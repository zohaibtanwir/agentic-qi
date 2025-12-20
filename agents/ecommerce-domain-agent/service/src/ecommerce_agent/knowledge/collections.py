"""Weaviate collection schemas for domain knowledge."""

from typing import Dict, Any, List

# Collection schemas for Weaviate
COLLECTION_SCHEMAS: List[Dict[str, Any]] = [
    {
        "class": "EcommerceEntity",
        "description": "eCommerce entity definitions with fields and relationships",
        "vectorizer": "text2vec-transformers",
        "moduleConfig": {
            "text2vec-transformers": {
                "poolingStrategy": "masked_mean",
                "vectorizeClassName": False,
            }
        },
        "properties": [
            {
                "name": "entity_name",
                "dataType": ["text"],
                "description": "Name of the entity",
                "moduleConfig": {
                    "text2vec-transformers": {
                        "skip": False,
                        "vectorizePropertyName": False,
                    }
                },
            },
            {
                "name": "description",
                "dataType": ["text"],
                "description": "Entity description",
            },
            {
                "name": "category",
                "dataType": ["text"],
                "description": "Entity category (core, transactional, financial, etc.)",
                "moduleConfig": {
                    "text2vec-transformers": {
                        "skip": True,
                        "vectorizePropertyName": False,
                    }
                },
            },
            {
                "name": "fields_json",
                "dataType": ["text"],
                "description": "JSON string of entity fields",
            },
            {
                "name": "relationships_json",
                "dataType": ["text"],
                "description": "JSON string of entity relationships",
            },
            {
                "name": "business_rules",
                "dataType": ["text[]"],
                "description": "Associated business rules",
            },
            {
                "name": "edge_cases",
                "dataType": ["text[]"],
                "description": "Associated edge cases",
            },
            {
                "name": "test_scenarios",
                "dataType": ["text[]"],
                "description": "Test scenario suggestions",
            },
        ],
    },
    {
        "class": "EcommerceWorkflow",
        "description": "eCommerce workflow definitions with steps",
        "vectorizer": "text2vec-transformers",
        "moduleConfig": {
            "text2vec-transformers": {
                "poolingStrategy": "masked_mean",
                "vectorizeClassName": False,
            }
        },
        "properties": [
            {
                "name": "workflow_name",
                "dataType": ["text"],
                "description": "Name of the workflow",
            },
            {
                "name": "description",
                "dataType": ["text"],
                "description": "Workflow description",
            },
            {
                "name": "steps_json",
                "dataType": ["text"],
                "description": "JSON string of workflow steps",
            },
            {
                "name": "involved_entities",
                "dataType": ["text[]"],
                "description": "Entities involved in this workflow",
            },
            {
                "name": "business_rules",
                "dataType": ["text[]"],
                "description": "Business rules for this workflow",
            },
            {
                "name": "edge_cases",
                "dataType": ["text[]"],
                "description": "Edge cases for this workflow",
            },
            {
                "name": "test_scenarios",
                "dataType": ["text[]"],
                "description": "Test scenario suggestions",
            },
        ],
    },
    {
        "class": "EcommerceRule",
        "description": "Business rules and validations",
        "vectorizer": "text2vec-transformers",
        "moduleConfig": {
            "text2vec-transformers": {
                "poolingStrategy": "masked_mean",
                "vectorizeClassName": False,
            }
        },
        "properties": [
            {
                "name": "rule_id",
                "dataType": ["text"],
                "description": "Rule identifier",
                "moduleConfig": {
                    "text2vec-transformers": {
                        "skip": True,
                        "vectorizePropertyName": False,
                    }
                },
            },
            {
                "name": "name",
                "dataType": ["text"],
                "description": "Rule name",
            },
            {
                "name": "entity",
                "dataType": ["text"],
                "description": "Entity this rule applies to",
            },
            {
                "name": "description",
                "dataType": ["text"],
                "description": "Rule description",
            },
            {
                "name": "condition",
                "dataType": ["text"],
                "description": "When this rule applies",
            },
            {
                "name": "constraint",
                "dataType": ["text"],
                "description": "What the rule enforces",
            },
            {
                "name": "severity",
                "dataType": ["text"],
                "description": "Rule severity (error, warning, info)",
                "moduleConfig": {
                    "text2vec-transformers": {
                        "skip": True,
                        "vectorizePropertyName": False,
                    }
                },
            },
            {
                "name": "validation_logic",
                "dataType": ["text"],
                "description": "Pseudo-code or description of validation",
            },
        ],
    },
    {
        "class": "EcommerceEdgeCase",
        "description": "Known edge cases and test scenarios",
        "vectorizer": "text2vec-transformers",
        "moduleConfig": {
            "text2vec-transformers": {
                "poolingStrategy": "masked_mean",
                "vectorizeClassName": False,
            }
        },
        "properties": [
            {
                "name": "edge_case_id",
                "dataType": ["text"],
                "description": "Edge case identifier",
                "moduleConfig": {
                    "text2vec-transformers": {
                        "skip": True,
                        "vectorizePropertyName": False,
                    }
                },
            },
            {
                "name": "name",
                "dataType": ["text"],
                "description": "Edge case name",
            },
            {
                "name": "category",
                "dataType": ["text"],
                "description": "Category (concurrency, network, boundary, etc.)",
            },
            {
                "name": "entity",
                "dataType": ["text"],
                "description": "Related entity",
            },
            {
                "name": "workflow",
                "dataType": ["text"],
                "description": "Related workflow",
            },
            {
                "name": "description",
                "dataType": ["text"],
                "description": "Edge case description",
            },
            {
                "name": "test_approach",
                "dataType": ["text"],
                "description": "How to test this edge case",
            },
            {
                "name": "expected_behavior",
                "dataType": ["text"],
                "description": "Expected system behavior",
            },
            {
                "name": "severity",
                "dataType": ["text"],
                "description": "Severity level",
                "moduleConfig": {
                    "text2vec-transformers": {
                        "skip": True,
                        "vectorizePropertyName": False,
                    }
                },
            },
            {
                "name": "example_data_json",
                "dataType": ["text"],
                "description": "JSON string of example test data",
            },
        ],
    },
    {
        "class": "EcommerceTestPattern",
        "description": "Successful test data patterns from past generations",
        "vectorizer": "text2vec-transformers",
        "moduleConfig": {
            "text2vec-transformers": {
                "poolingStrategy": "masked_mean",
                "vectorizeClassName": False,
            }
        },
        "properties": [
            {
                "name": "entity",
                "dataType": ["text"],
                "description": "Entity this pattern is for",
            },
            {
                "name": "scenario",
                "dataType": ["text"],
                "description": "Test scenario",
            },
            {
                "name": "context",
                "dataType": ["text"],
                "description": "Context description",
            },
            {
                "name": "data_json",
                "dataType": ["text"],
                "description": "JSON string of test data pattern",
            },
            {
                "name": "quality_score",
                "dataType": ["number"],
                "description": "Quality score of this pattern",
            },
            {
                "name": "usage_count",
                "dataType": ["int"],
                "description": "How many times this pattern was used",
            },
            {
                "name": "created_at",
                "dataType": ["text"],
                "description": "When this pattern was created",
            },
        ],
    },
]


def get_collection_names() -> List[str]:
    """Get list of all collection names."""
    return [schema["class"] for schema in COLLECTION_SCHEMAS]


def get_collection_schema(class_name: str) -> Dict[str, Any] | None:
    """Get schema for a specific collection."""
    for schema in COLLECTION_SCHEMAS:
        if schema["class"] == class_name:
            return schema
    return None