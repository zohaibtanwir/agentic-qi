"""Defect prediction and analysis orchestrator."""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from ecommerce_agent.clients.defect_analyzer import DefectAnalyzerClient
from ecommerce_agent.domain.entities import get_entity
from ecommerce_agent.utils.logging import get_logger

logger = get_logger(__name__)

class DefectSeverity(Enum):
    """Defect severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    TRIVIAL = "trivial"

class DefectCategory(Enum):
    """Defect categories."""
    FUNCTIONAL = "functional"
    PERFORMANCE = "performance"
    SECURITY = "security"
    USABILITY = "usability"
    COMPATIBILITY = "compatibility"
    DATA_INTEGRITY = "data_integrity"
    INTEGRATION = "integration"
    BUSINESS_LOGIC = "business_logic"

@dataclass
class DefectPrediction:
    """Predicted defect."""
    id: str
    entity: str
    workflow: str
    category: DefectCategory
    severity: DefectSeverity
    probability: float  # 0.0 to 1.0
    description: str
    potential_cause: str
    impact: str
    prevention_strategy: str
    detection_method: str
    affected_components: List[str]
    related_business_rules: List[str]
    estimated_fix_effort: str  # hours or story points

@dataclass
class DefectAnalysis:
    """Defect analysis report."""
    entity: str
    workflow: Optional[str]
    total_predictions: int
    high_risk_count: int
    predictions: List[DefectPrediction]
    risk_score: float  # Overall risk score 0.0 to 1.0
    recommendations: List[str]
    mitigation_plan: Dict[str, List[str]]
    test_focus_areas: List[str]


class DefectOrchestrator:
    """Orchestrates defect prediction and analysis with domain enrichment."""

    def __init__(self):
        self.client = DefectAnalyzerClient()

    async def predict_defects(
        self,
        entity_name: str,
        workflow: Optional[str] = None,
        code_changes: Optional[Dict[str, Any]] = None,
        historical_data: Optional[List[Dict[str, Any]]] = None,
        generation_method: str = "llm"
    ) -> DefectAnalysis:
        """
        Predict potential defects for an entity or workflow.

        Args:
            entity_name: Name of the domain entity
            workflow: Specific workflow to analyze
            code_changes: Recent code changes for analysis
            historical_data: Historical defect data
            generation_method: Method to use (traditional, llm, rag, hybrid)

        Returns:
            DefectAnalysis with predictions and recommendations
        """
        # Get entity definition for domain context
        entity = get_entity(entity_name)
        if not entity:
            raise ValueError(f"Entity '{entity_name}' not found")

        # Build request with domain enrichment
        request = {
            "entity": entity_name,
            "workflow": workflow,
            "generation_method": generation_method,
            "code_changes": code_changes,
            "historical_data": historical_data,
            "domain_context": {
                "entity_definition": {
                    "name": entity.name,
                    "description": entity.description,
                    "fields": [
                        {
                            "name": f.name,
                            "type": f.type,
                            "required": f.required,
                            "validations": f.validations
                        }
                        for f in entity.fields
                    ],
                    "relationships": [
                        {
                            "target": r.target,
                            "type": r.type,
                            "required": r.required
                        }
                        for r in entity.relationships
                    ],
                },
                "business_rules": entity.business_rules,
                "edge_cases": entity.edge_cases,
                "known_issues": self._get_known_issues(entity_name)
            }
        }

        logger.info(
            "Predicting defects",
            entity=entity_name,
            workflow=workflow,
            method=generation_method
        )

        try:
            # Call Defect Analyzer agent
            result = await self.client.analyze_defects(request)

            # Transform response to DefectAnalysis
            analysis = self._build_defect_analysis(result, entity_name, workflow)

            logger.info(
                "Defect prediction completed",
                entity=entity_name,
                total_predictions=analysis.total_predictions,
                high_risk_count=analysis.high_risk_count,
                risk_score=analysis.risk_score
            )

            return analysis

        except Exception as e:
            logger.error(
                "Failed to predict defects",
                entity=entity_name,
                workflow=workflow,
                error=str(e)
            )
            raise

    def _build_defect_analysis(
        self,
        result: Dict[str, Any],
        entity_name: str,
        workflow: Optional[str]
    ) -> DefectAnalysis:
        """Build DefectAnalysis from Defect Analyzer response."""
        predictions = []

        for pred in result.get("predictions", []):
            prediction = DefectPrediction(
                id=pred.get("id"),
                entity=entity_name,
                workflow=workflow or pred.get("workflow", ""),
                category=DefectCategory(pred.get("category", "functional")),
                severity=DefectSeverity(pred.get("severity", "medium")),
                probability=pred.get("probability", 0.5),
                description=pred.get("description", ""),
                potential_cause=pred.get("potential_cause", ""),
                impact=pred.get("impact", ""),
                prevention_strategy=pred.get("prevention_strategy", ""),
                detection_method=pred.get("detection_method", ""),
                affected_components=pred.get("affected_components", []),
                related_business_rules=pred.get("related_business_rules", []),
                estimated_fix_effort=pred.get("estimated_fix_effort", "2 hours")
            )
            predictions.append(prediction)

        high_risk_count = sum(
            1 for p in predictions
            if p.severity in [DefectSeverity.CRITICAL, DefectSeverity.HIGH]
            and p.probability > 0.7
        )

        return DefectAnalysis(
            entity=entity_name,
            workflow=workflow,
            total_predictions=len(predictions),
            high_risk_count=high_risk_count,
            predictions=predictions,
            risk_score=result.get("risk_score", 0.0),
            recommendations=result.get("recommendations", []),
            mitigation_plan=result.get("mitigation_plan", {}),
            test_focus_areas=result.get("test_focus_areas", [])
        )

    def _get_known_issues(self, entity_name: str) -> List[Dict[str, Any]]:
        """Get known issues for an entity from historical data."""
        # This would typically query a defect database
        # For now, return common ecommerce issues
        known_issues = {
            "cart": [
                {
                    "issue": "Race condition in concurrent cart updates",
                    "frequency": "medium",
                    "impact": "Data inconsistency"
                },
                {
                    "issue": "Cart abandonment after session timeout",
                    "frequency": "high",
                    "impact": "Lost sales"
                }
            ],
            "order": [
                {
                    "issue": "Payment processing timeout",
                    "frequency": "low",
                    "impact": "Order failure"
                },
                {
                    "issue": "Inventory mismatch during checkout",
                    "frequency": "medium",
                    "impact": "Overselling"
                }
            ],
            "payment": [
                {
                    "issue": "Duplicate payment submission",
                    "frequency": "low",
                    "impact": "Double charging"
                },
                {
                    "issue": "3DS authentication failure",
                    "frequency": "medium",
                    "impact": "Transaction decline"
                }
            ]
        }
        return known_issues.get(entity_name.lower(), [])

    async def analyze_code_quality(
        self,
        entity_name: str,
        code_metrics: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze code quality and predict defect-prone areas.

        Args:
            entity_name: Name of the entity
            code_metrics: Code complexity metrics

        Returns:
            Code quality analysis report
        """
        entity = get_entity(entity_name)
        if not entity:
            raise ValueError(f"Entity '{entity_name}' not found")

        # Analyze code quality indicators
        quality_analysis = {
            "entity": entity_name,
            "quality_score": 0.0,
            "complexity_hotspots": [],
            "defect_prone_areas": [],
            "recommendations": []
        }

        # Identify areas likely to have defects
        if len(entity.business_rules) > 5:
            quality_analysis["defect_prone_areas"].append(
                "Complex business logic - high rule count"
            )
            quality_analysis["recommendations"].append(
                "Add comprehensive unit tests for business rules"
            )

        if len(entity.relationships) > 3:
            quality_analysis["defect_prone_areas"].append(
                "Multiple dependencies - integration risk"
            )
            quality_analysis["recommendations"].append(
                "Focus on integration testing"
            )

        # Calculate quality score
        base_score = 80
        score_deductions = {
            "business_rules": min(len(entity.business_rules) * 2, 20),
            "relationships": min(len(entity.relationships) * 3, 15),
            "edge_cases": min(len(entity.edge_cases), 10)
        }

        quality_score = base_score - sum(score_deductions.values())
        quality_analysis["quality_score"] = max(quality_score, 0)

        return quality_analysis

    async def get_defect_trends(
        self,
        entity_name: str,
        time_period: str = "30d"
    ) -> Dict[str, Any]:
        """
        Get defect trends for an entity.

        Args:
            entity_name: Name of the entity
            time_period: Time period for analysis

        Returns:
            Defect trend analysis
        """
        # This would typically analyze historical defect data
        # For now, return simulated trend data
        trends = {
            "entity": entity_name,
            "time_period": time_period,
            "total_defects": 0,
            "trend": "stable",
            "categories": {
                "functional": 0,
                "performance": 0,
                "security": 0,
                "usability": 0
            },
            "severity_distribution": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            },
            "prediction": "Based on current trends, defect rate is expected to remain stable"
        }

        return trends


def get_defect_orchestrator() -> DefectOrchestrator:
    """Get defect orchestrator instance."""
    return DefectOrchestrator()