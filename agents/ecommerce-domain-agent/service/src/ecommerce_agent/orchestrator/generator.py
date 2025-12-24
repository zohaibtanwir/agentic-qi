"""Test data generation orchestrator."""

import json
import uuid
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

from ecommerce_agent.clients.test_data_client import get_test_data_client
from ecommerce_agent.enrichment.enricher import get_enricher, EnrichmentResult
from ecommerce_agent.knowledge.retriever import get_retriever
from ecommerce_agent.orchestrator.schema_builder import get_schema_builder
from ecommerce_agent.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class GenerationRequest:
    """Test data generation request."""

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
    generation_method: str = "HYBRID"  # TRADITIONAL, LLM, RAG, HYBRID


@dataclass
class GenerationResult:
    """Test data generation result."""

    request_id: str
    success: bool
    data: str
    record_count: int
    entity: str
    workflow: Optional[str] = None
    scenario: Optional[str] = None
    metadata: Dict[str, Any] = None
    enrichment_metadata: Dict[str, Any] = None
    generation_metadata: Dict[str, Any] = None
    error: Optional[str] = None
    generated_at: str = None

    def __post_init__(self):
        if not self.generated_at:
            self.generated_at = datetime.now(timezone.utc).isoformat()


class GenerationOrchestrator:
    """Orchestrates test data generation with enrichment."""

    def __init__(self, use_knowledge: bool = True, store_patterns: bool = True):
        """
        Initialize the generation orchestrator.

        Args:
            use_knowledge: Whether to use knowledge retrieval
            store_patterns: Whether to store successful patterns
        """
        self.enricher = get_enricher(use_knowledge=use_knowledge)
        self.use_knowledge = use_knowledge
        self.store_patterns = store_patterns

        if use_knowledge and store_patterns:
            try:
                self.retriever = get_retriever()
            except Exception as e:
                logger.warning("Knowledge storage not available", error=str(e))
                self.retriever = None
                self.store_patterns = False
        else:
            self.retriever = None
            self.store_patterns = False

    async def generate(
        self,
        request: GenerationRequest,
        request_id: Optional[str] = None,
    ) -> GenerationResult:
        """
        Generate test data with orchestration.

        Args:
            request: Generation request
            request_id: Optional request ID (generated if not provided)

        Returns:
            Generation result with data and metadata
        """
        # Generate request ID if not provided
        if not request_id:
            request_id = str(uuid.uuid4())

        logger.info(
            "Starting generation orchestration",
            request_id=request_id,
            entity=request.entity,
            count=request.count,
        )

        try:
            # Step 1: Enrich the request
            enrichment_result = await self._enrich_request(request)

            if not enrichment_result.enriched:
                logger.warning(
                    "Enrichment failed, using minimal context",
                    request_id=request_id,
                    error=enrichment_result.error,
                )

            # Step 2: Call Test Data Agent
            generation_result = await self._call_test_data_agent(
                request_id=request_id,
                request=request,
                enrichment=enrichment_result,
            )

            # Step 3: Process and validate results
            processed_result = self._process_result(
                request_id=request_id,
                request=request,
                enrichment=enrichment_result,
                raw_result=generation_result,
            )

            # Step 4: Store successful pattern if enabled
            if processed_result.success and self.store_patterns:
                await self._store_pattern(processed_result)

            logger.info(
                "Generation orchestration complete",
                request_id=request_id,
                success=processed_result.success,
                record_count=processed_result.record_count,
            )

            return processed_result

        except Exception as e:
            logger.error(
                "Generation orchestration failed",
                request_id=request_id,
                error=str(e),
            )

            return GenerationResult(
                request_id=request_id,
                success=False,
                data="",
                record_count=0,
                entity=request.entity,
                workflow=request.workflow,
                scenario=request.scenario,
                error=f"Orchestration failed: {str(e)}",
            )

    async def _enrich_request(
        self,
        request: GenerationRequest,
    ) -> EnrichmentResult:
        """Enrich the generation request."""
        return await self.enricher.enrich_request(
            entity=request.entity,
            count=request.count,
            workflow=request.workflow,
            scenario=request.scenario,
            user_context=request.context,
            user_scenarios=request.scenarios,
            include_edge_cases=request.include_edge_cases,
            production_like=request.production_like,
        )

    async def _call_test_data_agent(
        self,
        request_id: str,
        request: GenerationRequest,
        enrichment: EnrichmentResult,
    ) -> Dict[str, Any]:
        """Call the Test Data Agent with enriched request."""
        # Get Test Data Agent client
        client = await get_test_data_client()

        # Determine if we need a custom schema
        schema_builder = get_schema_builder()
        strategy, custom_schema = schema_builder.determine_generation_strategy(request.entity)

        logger.info(
            "Generation strategy determined",
            request_id=request_id,
            entity=request.entity,
            strategy=strategy,
            generation_method=request.generation_method,
            has_custom_schema=custom_schema is not None,
        )

        # Prepare the call with optional custom schema
        result = await client.generate_data(
            request_id=request_id,
            domain="ecommerce",  # Fixed for this agent
            entity=request.entity,
            count=request.count,
            context=enrichment.context,
            hints=enrichment.hints,
            scenarios=enrichment.scenarios,
            constraints=enrichment.constraints,
            output_format=request.output_format,
            use_cache=request.use_cache,
            production_like=request.production_like,
            custom_schema=custom_schema,  # Pass custom schema if needed
            generation_method=request.generation_method,  # Pass generation method
        )

        return result

    def _process_result(
        self,
        request_id: str,
        request: GenerationRequest,
        enrichment: EnrichmentResult,
        raw_result: Dict[str, Any],
    ) -> GenerationResult:
        """Process and validate generation result."""
        # Build result
        result = GenerationResult(
            request_id=request_id,
            success=raw_result.get("success", False),
            data=raw_result.get("data", ""),
            record_count=raw_result.get("record_count", 0),
            entity=request.entity,
            workflow=request.workflow,
            scenario=request.scenario,
            error=raw_result.get("error"),
        )

        # Add metadata
        result.metadata = {
            "output_format": request.output_format,
            "use_cache": request.use_cache,
            "production_like": request.production_like,
            "include_edge_cases": request.include_edge_cases,
        }

        # Add enrichment metadata
        result.enrichment_metadata = enrichment.metadata

        # Add generation metadata from Test Data Agent
        if "metadata" in raw_result:
            result.generation_metadata = raw_result["metadata"]

        # Validate data if successful
        if result.success and result.data:
            try:
                # Try to parse JSON to validate structure
                if request.output_format == "JSON":
                    data_obj = json.loads(result.data)

                    # Count actual records
                    if isinstance(data_obj, list):
                        result.record_count = len(data_obj)
                    elif isinstance(data_obj, dict) and "data" in data_obj:
                        result.record_count = len(data_obj["data"])

            except json.JSONDecodeError as e:
                logger.warning(
                    "Generated data is not valid JSON",
                    request_id=request_id,
                    error=str(e),
                )
                # Don't fail the result, just note it
                if not result.metadata:
                    result.metadata = {}
                result.metadata["json_valid"] = False

        return result

    async def _store_pattern(
        self,
        result: GenerationResult,
    ) -> None:
        """Store successful generation pattern for future use."""
        if not self.retriever or not result.data:
            return

        try:
            # Calculate quality score based on success metrics
            quality_score = self._calculate_quality_score(result)

            # Store as test pattern
            from ecommerce_agent.knowledge.indexer import get_indexer

            indexer = get_indexer()

            pattern = {
                "entity": result.entity,
                "scenario": result.scenario or "default",
                "workflow": result.workflow,
                "data": result.data[:5000],  # Truncate for storage
                "quality_score": quality_score,
                "record_count": result.record_count,
                "metadata": {
                    "request_id": result.request_id,
                    "generated_at": result.generated_at,
                },
            }

            await indexer.add_test_pattern(
                entity=pattern["entity"],
                scenario=pattern["scenario"],
                data=pattern["data"],
                quality_score=pattern["quality_score"],
                metadata=pattern["metadata"],
            )

            logger.info(
                "Stored successful pattern",
                entity=result.entity,
                scenario=result.scenario,
                quality_score=quality_score,
            )

        except Exception as e:
            logger.warning("Could not store pattern", error=str(e))

    def _calculate_quality_score(
        self,
        result: GenerationResult,
    ) -> float:
        """Calculate quality score for generated data."""
        score = 0.0

        # Base score for successful generation
        if result.success:
            score += 0.5

        # Score based on record count match
        if result.record_count > 0:
            score += 0.2

        # Score for valid JSON
        if result.metadata and result.metadata.get("json_valid", True):
            score += 0.1

        # Score for enrichment
        if result.enrichment_metadata:
            if result.enrichment_metadata.get("business_rules_count", 0) > 0:
                score += 0.1
            if result.enrichment_metadata.get("edge_cases_count", 0) > 0:
                score += 0.05

        # Score from Test Data Agent metrics
        if result.generation_metadata:
            if result.generation_metadata.get("coherence_score", 0) > 0.7:
                score += 0.05

        return min(score, 1.0)  # Cap at 1.0

    async def generate_batch(
        self,
        requests: List[GenerationRequest],
    ) -> List[GenerationResult]:
        """
        Generate test data for multiple requests.

        Args:
            requests: List of generation requests

        Returns:
            List of generation results
        """
        results = []

        for request in requests:
            result = await self.generate(request)
            results.append(result)

        return results

    async def generate_stream(
        self,
        request: GenerationRequest,
        request_id: Optional[str] = None,
    ):
        """
        Generate test data with streaming (for large requests).

        This is an async generator that yields data chunks.
        """
        # Generate request ID if not provided
        if not request_id:
            request_id = str(uuid.uuid4())

        logger.info(
            "Starting streaming generation",
            request_id=request_id,
            entity=request.entity,
            count=request.count,
        )

        try:
            # Enrich the request
            enrichment_result = await self._enrich_request(request)

            # Get Test Data Agent client
            client = await get_test_data_client()

            # Stream from Test Data Agent
            async for chunk in client.generate_data_stream(
                request_id=request_id,
                domain="ecommerce",
                entity=request.entity,
                count=request.count,
                context=enrichment_result.context,
                hints=enrichment_result.hints,
                scenarios=enrichment_result.scenarios,
                constraints=enrichment_result.constraints,
            ):
                yield chunk

        except Exception as e:
            logger.error(
                "Streaming generation failed",
                request_id=request_id,
                error=str(e),
            )
            yield {
                "error": str(e),
                "is_final": True,
            }

    def validate_request(
        self,
        request: GenerationRequest,
    ) -> tuple[bool, List[str]]:
        """
        Validate a generation request.

        Args:
            request: Request to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Validate entity
        if not request.entity:
            errors.append("Entity is required")

        # Validate count
        if request.count <= 0:
            errors.append("Count must be positive")
        elif request.count > 10000:
            errors.append("Count cannot exceed 10000")

        # Validate output format
        valid_formats = ["JSON", "CSV", "SQL"]
        if request.output_format not in valid_formats:
            errors.append(f"Output format must be one of {valid_formats}")

        # Validate scenarios if provided
        if request.scenarios:
            total_scenario_count = sum(
                s.get("count", 0) for s in request.scenarios
            )
            if total_scenario_count > request.count:
                errors.append("Total scenario count exceeds requested count")

        is_valid = len(errors) == 0
        return is_valid, errors


# Singleton instance
_orchestrator: Optional[GenerationOrchestrator] = None


def get_orchestrator(
    use_knowledge: bool = True,
    store_patterns: bool = True,
) -> GenerationOrchestrator:
    """Get singleton generation orchestrator."""
    global _orchestrator
    if not _orchestrator:
        _orchestrator = GenerationOrchestrator(
            use_knowledge=use_knowledge,
            store_patterns=store_patterns,
        )
    return _orchestrator