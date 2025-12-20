"""HTTP API endpoints for eCommerce Domain Agent."""

from fastapi import HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid

from ecommerce_agent.orchestrator.generator import (
    GenerationRequest,
    GenerationOrchestrator,
    get_orchestrator,
)
from ecommerce_agent.orchestrator.test_cases import (
    get_test_case_orchestrator,
    TestCaseType,
)
from ecommerce_agent.orchestrator.defects import get_defect_orchestrator
from ecommerce_agent.orchestrator.business_rules import get_business_rules_orchestrator
from ecommerce_agent.orchestrator.journey_monitoring import get_journey_monitoring_orchestrator
from ecommerce_agent.server.knowledge_api import router as knowledge_router
from ecommerce_agent.utils.logging import get_logger

logger = get_logger(__name__)


class GenerateRequest(BaseModel):
    """HTTP request for test data generation."""
    entity: str
    count: int = 10
    workflow: Optional[str] = None
    scenario: Optional[str] = None
    context: Optional[str] = None
    scenarios: Optional[List[Dict[str, Any]]] = None
    output_format: str = "JSON"
    include_edge_cases: bool = True
    production_like: bool = True
    use_cache: bool = True
    generation_method: str = "HYBRID"


class GenerateResponse(BaseModel):
    """HTTP response for test data generation."""
    success: bool
    data: str
    metadata: Dict[str, Any]


# Test Cases API Models
class TestCasesRequest(BaseModel):
    """Request for test case generation."""
    entity: str
    workflow: Optional[str] = None
    test_types: Optional[List[str]] = None
    generation_method: str = "llm"
    count: int = 10
    include_edge_cases: bool = True
    include_negative_tests: bool = True


class TestCasesResponse(BaseModel):
    """Response for test case generation."""
    success: bool
    test_suite: Dict[str, Any]
    metadata: Dict[str, Any]


# Defect Prediction API Models
class DefectPredictionRequest(BaseModel):
    """Request for defect prediction."""
    entity: str
    workflow: Optional[str] = None
    code_changes: Optional[Dict[str, Any]] = None
    historical_data: Optional[List[Dict[str, Any]]] = None
    generation_method: str = "llm"


class DefectPredictionResponse(BaseModel):
    """Response for defect prediction."""
    success: bool
    analysis: Dict[str, Any]
    metadata: Dict[str, Any]


# Business Rules API Models
class BusinessRulesRequest(BaseModel):
    """Request for business rules validation."""
    entity: str
    test_data: Dict[str, Any]
    workflow: Optional[str] = None
    rules_to_validate: Optional[List[str]] = None


class BusinessRulesResponse(BaseModel):
    """Response for business rules validation."""
    success: bool
    validation_report: Dict[str, Any]
    metadata: Dict[str, Any]


# Journey Monitoring API Models
class JourneyMonitoringRequest(BaseModel):
    """Request for journey monitoring."""
    customer_id: Optional[str] = None
    journey_id: Optional[str] = None
    real_time: bool = False
    entity_focus: Optional[str] = None
    time_period: str = "24h"


class JourneyMonitoringResponse(BaseModel):
    """Response for journey monitoring."""
    success: bool
    journey_data: Dict[str, Any]
    metadata: Dict[str, Any]


async def generate_handler(request: GenerateRequest) -> GenerateResponse:
    """Handle test data generation requests."""
    try:
        # Create a unique request ID
        request_id = str(uuid.uuid4())

        logger.info(
            "Received generation request",
            request_id=request_id,
            entity=request.entity,
            count=request.count,
            generation_method=request.generation_method,
        )

        # Get the orchestrator
        orchestrator = get_orchestrator()

        # Create orchestrator request
        orch_request = GenerationRequest(
            entity=request.entity,
            count=request.count,
            workflow=request.workflow,
            scenario=request.scenario,
            context=request.context,
            scenarios=request.scenarios,
            output_format=request.output_format,
            include_edge_cases=request.include_edge_cases,
            production_like=request.production_like,
            use_cache=request.use_cache,
            generation_method=request.generation_method,
        )

        # Orchestrate the generation
        result = await orchestrator.generate(orch_request)

        # Prepare response
        response = GenerateResponse(
            success=result.success,
            data=result.data,
            metadata={
                "request_id": result.request_id,
                "entity": result.entity,
                "record_count": result.record_count,
                "generated_at": result.generated_at,
                "generation_method": request.generation_method,
                "enrichment_metadata": result.enrichment_metadata,
                "generation_metadata": result.generation_metadata,
                "workflow": result.workflow,
                "scenario": result.scenario,
                "is_mock": False,  # This is real data from Test Data Agent
            }
        )

        if result.error:
            response.metadata["error"] = result.error

        logger.info(
            "Generation request completed",
            request_id=request_id,
            success=result.success,
            record_count=result.record_count,
        )

        return response

    except Exception as e:
        logger.error(
            "Generation request failed",
            error=str(e),
            entity=request.entity,
        )
        raise HTTPException(status_code=500, detail=str(e))


def add_api_routes(app):
    """Add API routes to the FastAPI app."""

    # Include the knowledge API router
    app.include_router(knowledge_router)

    @app.post("/api/generate", response_model=GenerateResponse)
    async def generate(request: GenerateRequest):
        """Generate test data via orchestration."""
        return await generate_handler(request)

    @app.get("/api/entities")
    async def list_entities():
        """List available entities."""
        # This would normally come from a service
        from ecommerce_agent.orchestrator.schema_builder import get_schema_builder
        builder = get_schema_builder()

        return {
            "predefined": list(builder.TEST_DATA_AGENT_PREDEFINED),
            "domain": list(builder.DOMAIN_ENTITIES),
        }

    @app.post("/api/test-cases", response_model=TestCasesResponse)
    async def generate_test_cases(request: TestCasesRequest):
        """Generate test cases for an entity."""
        try:
            orchestrator = get_test_case_orchestrator()

            # Convert string test types to enum
            test_types = None
            if request.test_types:
                test_types = [TestCaseType[t.upper()] for t in request.test_types]

            test_suite = await orchestrator.generate_test_cases(
                entity_name=request.entity,
                workflow=request.workflow,
                test_types=test_types,
                generation_method=request.generation_method,
                count=request.count,
                include_edge_cases=request.include_edge_cases,
                include_negative_tests=request.include_negative_tests
            )

            # Convert to dict for JSON response
            suite_dict = {
                "id": test_suite.id,
                "name": test_suite.name,
                "entity": test_suite.entity,
                "workflow": test_suite.workflow,
                "total_cases": test_suite.total_cases,
                "coverage_percentage": test_suite.coverage_percentage,
                "estimated_duration": test_suite.estimated_duration,
                "test_cases": [
                    {
                        "id": tc.id,
                        "name": tc.name,
                        "description": tc.description,
                        "type": tc.type.value,
                        "priority": tc.priority.value,
                        "preconditions": tc.preconditions,
                        "steps": tc.steps,
                        "postconditions": tc.postconditions,
                        "test_data": tc.test_data,
                        "business_rules": tc.business_rules,
                        "expected_behavior": tc.expected_behavior,
                        "edge_cases": tc.edge_cases,
                        "automation_feasibility": tc.automation_feasibility,
                        "estimated_duration": tc.estimated_duration
                    }
                    for tc in test_suite.test_cases
                ]
            }

            return TestCasesResponse(
                success=True,
                test_suite=suite_dict,
                metadata={"generation_method": request.generation_method}
            )
        except Exception as e:
            logger.error("Test case generation failed", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/defect-prediction", response_model=DefectPredictionResponse)
    async def predict_defects(request: DefectPredictionRequest):
        """Predict defects for an entity."""
        try:
            orchestrator = get_defect_orchestrator()

            analysis = await orchestrator.predict_defects(
                entity_name=request.entity,
                workflow=request.workflow,
                code_changes=request.code_changes,
                historical_data=request.historical_data,
                generation_method=request.generation_method
            )

            # Convert to dict for JSON response
            analysis_dict = {
                "entity": analysis.entity,
                "workflow": analysis.workflow,
                "total_predictions": analysis.total_predictions,
                "high_risk_count": analysis.high_risk_count,
                "risk_score": analysis.risk_score,
                "recommendations": analysis.recommendations,
                "mitigation_plan": analysis.mitigation_plan,
                "test_focus_areas": analysis.test_focus_areas,
                "predictions": [
                    {
                        "id": p.id,
                        "entity": p.entity,
                        "workflow": p.workflow,
                        "category": p.category.value,
                        "severity": p.severity.value,
                        "probability": p.probability,
                        "description": p.description,
                        "potential_cause": p.potential_cause,
                        "impact": p.impact,
                        "prevention_strategy": p.prevention_strategy,
                        "detection_method": p.detection_method,
                        "affected_components": p.affected_components,
                        "related_business_rules": p.related_business_rules,
                        "estimated_fix_effort": p.estimated_fix_effort
                    }
                    for p in analysis.predictions
                ]
            }

            return DefectPredictionResponse(
                success=True,
                analysis=analysis_dict,
                metadata={"generation_method": request.generation_method}
            )
        except Exception as e:
            logger.error("Defect prediction failed", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/business-rules", response_model=BusinessRulesResponse)
    async def validate_business_rules(request: BusinessRulesRequest):
        """Validate business rules for test data."""
        try:
            orchestrator = get_business_rules_orchestrator()

            report = await orchestrator.validate_business_rules(
                entity_name=request.entity,
                test_data=request.test_data,
                workflow=request.workflow,
                rules_to_validate=request.rules_to_validate
            )

            # Convert to dict for JSON response
            report_dict = {
                "entity": report.entity,
                "workflow": report.workflow,
                "total_rules": report.total_rules,
                "passed": report.passed,
                "failed": report.failed,
                "warnings": report.warnings,
                "compliance_score": report.compliance_score,
                "recommendations": report.recommendations,
                "critical_failures": report.critical_failures,
                "results": [
                    {
                        "rule_id": r.rule_id,
                        "rule_name": r.rule_name,
                        "status": r.status.value,
                        "message": r.message,
                        "details": r.details,
                        "test_data_used": r.test_data_used,
                        "execution_time_ms": r.execution_time_ms
                    }
                    for r in report.results
                ]
            }

            return BusinessRulesResponse(
                success=True,
                validation_report=report_dict,
                metadata={"entity": request.entity}
            )
        except Exception as e:
            logger.error("Business rules validation failed", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/journey-monitoring", response_model=JourneyMonitoringResponse)
    async def monitor_journey(request: JourneyMonitoringRequest):
        """Monitor customer journey."""
        try:
            orchestrator = get_journey_monitoring_orchestrator()

            if request.customer_id:
                # Monitor specific journey
                journey = await orchestrator.monitor_journey(
                    customer_id=request.customer_id,
                    journey_id=request.journey_id,
                    real_time=request.real_time
                )

                journey_dict = {
                    "journey_id": journey.journey_id,
                    "customer_id": journey.customer_id,
                    "start_time": journey.start_time.isoformat(),
                    "end_time": journey.end_time.isoformat() if journey.end_time else None,
                    "current_stage": journey.current_stage.value,
                    "health": journey.health.value,
                    "total_duration_ms": journey.total_duration_ms,
                    "conversion_funnel": journey.conversion_funnel,
                    "bottlenecks": journey.bottlenecks,
                    "recommendations": journey.recommendations,
                    "steps": [
                        {
                            "step_id": s.step_id,
                            "name": s.name,
                            "stage": s.stage.value,
                            "duration_ms": s.duration_ms,
                            "status": s.status,
                            "conversion_rate": s.conversion_rate,
                            "drop_off_rate": s.drop_off_rate
                        }
                        for s in journey.steps
                    ]
                }

                return JourneyMonitoringResponse(
                    success=True,
                    journey_data=journey_dict,
                    metadata={"type": "individual_journey"}
                )
            else:
                # Analyze multiple journeys
                analysis = await orchestrator.analyze_journeys(
                    entity_name=request.entity_focus,
                    time_period=request.time_period
                )

                analysis_dict = {
                    "total_journeys": analysis.total_journeys,
                    "active_journeys": analysis.active_journeys,
                    "completed_journeys": analysis.completed_journeys,
                    "abandoned_journeys": analysis.abandoned_journeys,
                    "average_duration_ms": analysis.average_duration_ms,
                    "conversion_rate": analysis.conversion_rate,
                    "stage_metrics": {k.value: v for k, v in analysis.stage_metrics.items()},
                    "top_drop_off_points": analysis.top_drop_off_points,
                    "health_distribution": {k.value: v for k, v in analysis.health_distribution.items()},
                    "insights": analysis.insights,
                    "optimization_opportunities": analysis.optimization_opportunities
                }

                return JourneyMonitoringResponse(
                    success=True,
                    journey_data=analysis_dict,
                    metadata={"type": "journey_analysis", "time_period": request.time_period}
                )
        except Exception as e:
            logger.error("Journey monitoring failed", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))