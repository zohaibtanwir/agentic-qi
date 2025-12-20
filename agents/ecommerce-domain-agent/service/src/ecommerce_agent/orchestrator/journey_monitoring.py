"""Customer journey monitoring and analysis orchestrator."""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from ecommerce_agent.domain.entities import get_entity
from ecommerce_agent.utils.logging import get_logger

logger = get_logger(__name__)

class JourneyStage(Enum):
    """Customer journey stages."""
    DISCOVERY = "discovery"
    CONSIDERATION = "consideration"
    PURCHASE = "purchase"
    FULFILLMENT = "fulfillment"
    POST_PURCHASE = "post_purchase"
    RETENTION = "retention"

class EventType(Enum):
    """Journey event types."""
    PAGE_VIEW = "page_view"
    SEARCH = "search"
    PRODUCT_VIEW = "product_view"
    ADD_TO_CART = "add_to_cart"
    REMOVE_FROM_CART = "remove_from_cart"
    CHECKOUT_START = "checkout_start"
    PAYMENT = "payment"
    ORDER_COMPLETE = "order_complete"
    SHIPMENT = "shipment"
    DELIVERY = "delivery"
    REVIEW = "review"
    RETURN = "return"
    SUPPORT = "support"

class JourneyHealth(Enum):
    """Journey health status."""
    HEALTHY = "healthy"
    AT_RISK = "at_risk"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

@dataclass
class JourneyEvent:
    """Individual journey event."""
    event_id: str
    timestamp: datetime
    event_type: EventType
    entity: str
    stage: JourneyStage
    details: Dict[str, Any]
    duration_ms: int
    success: bool
    error: Optional[str]

@dataclass
class JourneyStep:
    """Step in customer journey."""
    step_id: str
    name: str
    stage: JourneyStage
    expected_events: List[EventType]
    actual_events: List[JourneyEvent]
    duration_ms: int
    status: str  # completed, in_progress, skipped, failed
    conversion_rate: float
    drop_off_rate: float

@dataclass
class CustomerJourney:
    """Complete customer journey."""
    journey_id: str
    customer_id: str
    start_time: datetime
    end_time: Optional[datetime]
    current_stage: JourneyStage
    health: JourneyHealth
    steps: List[JourneyStep]
    events: List[JourneyEvent]
    total_duration_ms: int
    conversion_funnel: Dict[str, float]
    bottlenecks: List[str]
    recommendations: List[str]

@dataclass
class JourneyAnalysis:
    """Journey monitoring analysis."""
    total_journeys: int
    active_journeys: int
    completed_journeys: int
    abandoned_journeys: int
    average_duration_ms: int
    conversion_rate: float
    stage_metrics: Dict[JourneyStage, Dict[str, Any]]
    top_drop_off_points: List[Dict[str, Any]]
    health_distribution: Dict[JourneyHealth, int]
    insights: List[str]
    optimization_opportunities: List[str]


class JourneyMonitoringOrchestrator:
    """Orchestrates customer journey monitoring and analysis."""

    def __init__(self):
        pass

    async def monitor_journey(
        self,
        customer_id: str,
        journey_id: Optional[str] = None,
        real_time: bool = False
    ) -> CustomerJourney:
        """
        Monitor a customer journey.

        Args:
            customer_id: Customer identifier
            journey_id: Specific journey to monitor
            real_time: Enable real-time monitoring

        Returns:
            CustomerJourney with current status
        """
        # Generate journey ID if not provided
        if not journey_id:
            journey_id = f"JOURNEY-{customer_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        logger.info(
            "Monitoring customer journey",
            journey_id=journey_id,
            customer_id=customer_id,
            real_time=real_time
        )

        # Simulate journey monitoring
        events = self._generate_journey_events(customer_id)
        steps = self._analyze_journey_steps(events)
        health = self._assess_journey_health(steps, events)

        journey = CustomerJourney(
            journey_id=journey_id,
            customer_id=customer_id,
            start_time=events[0].timestamp if events else datetime.now(),
            end_time=events[-1].timestamp if events and health == JourneyHealth.COMPLETED else None,
            current_stage=self._determine_current_stage(events),
            health=health,
            steps=steps,
            events=events,
            total_duration_ms=self._calculate_total_duration(events),
            conversion_funnel=self._build_conversion_funnel(steps),
            bottlenecks=self._identify_bottlenecks(steps, events),
            recommendations=self._generate_journey_recommendations(steps, events, health)
        )

        logger.info(
            "Journey monitoring complete",
            journey_id=journey_id,
            health=health.value,
            current_stage=journey.current_stage.value
        )

        return journey

    async def analyze_journeys(
        self,
        entity_name: Optional[str] = None,
        time_period: str = "24h",
        segment: Optional[str] = None
    ) -> JourneyAnalysis:
        """
        Analyze multiple customer journeys.

        Args:
            entity_name: Focus on specific entity
            time_period: Analysis time period
            segment: Customer segment to analyze

        Returns:
            JourneyAnalysis with insights
        """
        logger.info(
            "Analyzing customer journeys",
            entity=entity_name,
            time_period=time_period,
            segment=segment
        )

        # Simulate journey analysis
        analysis = JourneyAnalysis(
            total_journeys=1000,
            active_journeys=150,
            completed_journeys=750,
            abandoned_journeys=100,
            average_duration_ms=3600000,  # 1 hour average
            conversion_rate=75.0,
            stage_metrics=self._generate_stage_metrics(),
            top_drop_off_points=self._identify_drop_off_points(),
            health_distribution={
                JourneyHealth.HEALTHY: 600,
                JourneyHealth.AT_RISK: 200,
                JourneyHealth.COMPLETED: 750,
                JourneyHealth.ABANDONED: 100,
                JourneyHealth.BLOCKED: 50
            },
            insights=self._generate_insights(entity_name),
            optimization_opportunities=self._identify_optimization_opportunities(entity_name)
        )

        logger.info(
            "Journey analysis complete",
            total_journeys=analysis.total_journeys,
            conversion_rate=analysis.conversion_rate
        )

        return analysis

    def _generate_journey_events(self, customer_id: str) -> List[JourneyEvent]:
        """Generate simulated journey events."""
        import random
        from datetime import timedelta

        events = []
        base_time = datetime.now() - timedelta(hours=2)

        # Typical ecommerce journey events
        event_sequence = [
            (EventType.PAGE_VIEW, "homepage", JourneyStage.DISCOVERY),
            (EventType.SEARCH, "search", JourneyStage.DISCOVERY),
            (EventType.PRODUCT_VIEW, "product", JourneyStage.CONSIDERATION),
            (EventType.ADD_TO_CART, "cart", JourneyStage.CONSIDERATION),
            (EventType.CHECKOUT_START, "checkout", JourneyStage.PURCHASE),
            (EventType.PAYMENT, "payment", JourneyStage.PURCHASE),
            (EventType.ORDER_COMPLETE, "order", JourneyStage.PURCHASE),
        ]

        for idx, (event_type, entity, stage) in enumerate(event_sequence):
            event = JourneyEvent(
                event_id=f"EVT-{idx+1:05d}",
                timestamp=base_time + timedelta(minutes=idx * 5),
                event_type=event_type,
                entity=entity,
                stage=stage,
                details={"customer_id": customer_id},
                duration_ms=random.randint(100, 5000),
                success=True,
                error=None
            )
            events.append(event)

        return events

    def _analyze_journey_steps(self, events: List[JourneyEvent]) -> List[JourneyStep]:
        """Analyze journey events into steps."""
        steps = []

        # Group events by stage
        stage_events = {}
        for event in events:
            if event.stage not in stage_events:
                stage_events[event.stage] = []
            stage_events[event.stage].append(event)

        # Create steps for each stage
        for idx, (stage, stage_event_list) in enumerate(stage_events.items()):
            step = JourneyStep(
                step_id=f"STEP-{idx+1:03d}",
                name=f"{stage.value.replace('_', ' ').title()} Stage",
                stage=stage,
                expected_events=[e.event_type for e in stage_event_list],
                actual_events=stage_event_list,
                duration_ms=sum(e.duration_ms for e in stage_event_list),
                status="completed",
                conversion_rate=90.0 - (idx * 5),  # Simulated declining conversion
                drop_off_rate=10.0 + (idx * 2)  # Simulated increasing drop-off
            )
            steps.append(step)

        return steps

    def _assess_journey_health(
        self,
        steps: List[JourneyStep],
        events: List[JourneyEvent]
    ) -> JourneyHealth:
        """Assess overall journey health."""
        if not events:
            return JourneyHealth.ABANDONED

        last_event = events[-1]

        if last_event.event_type == EventType.ORDER_COMPLETE:
            return JourneyHealth.COMPLETED
        elif any(not e.success for e in events):
            return JourneyHealth.BLOCKED
        elif (datetime.now() - last_event.timestamp).seconds > 3600:  # > 1 hour idle
            return JourneyHealth.ABANDONED
        elif any(step.drop_off_rate > 20 for step in steps):
            return JourneyHealth.AT_RISK
        else:
            return JourneyHealth.HEALTHY

    def _determine_current_stage(self, events: List[JourneyEvent]) -> JourneyStage:
        """Determine current journey stage."""
        if not events:
            return JourneyStage.DISCOVERY

        return events[-1].stage

    def _calculate_total_duration(self, events: List[JourneyEvent]) -> int:
        """Calculate total journey duration."""
        if not events:
            return 0

        return sum(e.duration_ms for e in events)

    def _build_conversion_funnel(self, steps: List[JourneyStep]) -> Dict[str, float]:
        """Build conversion funnel metrics."""
        funnel = {}

        for step in steps:
            funnel[step.stage.value] = step.conversion_rate

        return funnel

    def _identify_bottlenecks(
        self,
        steps: List[JourneyStep],
        events: List[JourneyEvent]
    ) -> List[str]:
        """Identify journey bottlenecks."""
        bottlenecks = []

        # Check for high drop-off steps
        for step in steps:
            if step.drop_off_rate > 15:
                bottlenecks.append(f"High drop-off at {step.name}: {step.drop_off_rate:.1f}%")

        # Check for slow events
        slow_events = [e for e in events if e.duration_ms > 3000]
        if slow_events:
            bottlenecks.append(f"Slow performance in {len(slow_events)} events")

        return bottlenecks

    def _generate_journey_recommendations(
        self,
        steps: List[JourneyStep],
        events: List[JourneyEvent],
        health: JourneyHealth
    ) -> List[str]:
        """Generate journey optimization recommendations."""
        recommendations = []

        if health == JourneyHealth.ABANDONED:
            recommendations.append("Implement cart abandonment recovery campaign")
            recommendations.append("Send reminder notifications for incomplete journeys")

        elif health == JourneyHealth.AT_RISK:
            recommendations.append("Simplify checkout process to reduce friction")
            recommendations.append("Offer assistance through live chat")

        elif health == JourneyHealth.BLOCKED:
            recommendations.append("Investigate and fix blocking errors")
            recommendations.append("Provide alternative payment methods")

        # Add step-specific recommendations
        for step in steps:
            if step.drop_off_rate > 20:
                recommendations.append(f"Optimize {step.name} to reduce {step.drop_off_rate:.1f}% drop-off")

        return recommendations

    def _generate_stage_metrics(self) -> Dict[JourneyStage, Dict[str, Any]]:
        """Generate metrics for each journey stage."""
        return {
            JourneyStage.DISCOVERY: {
                "avg_duration_ms": 300000,
                "conversion_rate": 95.0,
                "drop_off_rate": 5.0,
                "events_count": 2500
            },
            JourneyStage.CONSIDERATION: {
                "avg_duration_ms": 600000,
                "conversion_rate": 80.0,
                "drop_off_rate": 15.0,
                "events_count": 2000
            },
            JourneyStage.PURCHASE: {
                "avg_duration_ms": 900000,
                "conversion_rate": 75.0,
                "drop_off_rate": 20.0,
                "events_count": 1500
            }
        }

    def _identify_drop_off_points(self) -> List[Dict[str, Any]]:
        """Identify top drop-off points in journeys."""
        return [
            {
                "location": "Checkout - Payment",
                "drop_off_rate": 25.0,
                "affected_journeys": 250,
                "reason": "Payment failures and form complexity"
            },
            {
                "location": "Cart - Checkout Start",
                "drop_off_rate": 20.0,
                "affected_journeys": 200,
                "reason": "Shipping cost surprise"
            },
            {
                "location": "Product View - Add to Cart",
                "drop_off_rate": 15.0,
                "affected_journeys": 150,
                "reason": "Price or availability concerns"
            }
        ]

    def _generate_insights(self, entity_name: Optional[str]) -> List[str]:
        """Generate journey insights."""
        insights = [
            "75% of customers complete purchase within 1 hour of starting journey",
            "Mobile users have 10% higher abandonment rate than desktop",
            "Customers who use search are 2x more likely to convert",
            "Weekend traffic shows 30% higher conversion rates"
        ]

        if entity_name == "cart":
            insights.append("Cart abandonment peaks at payment stage (25%)")
        elif entity_name == "order":
            insights.append("Express shipping users have 15% higher completion rate")

        return insights

    def _identify_optimization_opportunities(self, entity_name: Optional[str]) -> List[str]:
        """Identify optimization opportunities."""
        opportunities = [
            "Implement one-click checkout for returning customers",
            "Add progress indicators to multi-step processes",
            "Optimize page load times for mobile users",
            "Personalize product recommendations based on journey stage"
        ]

        if entity_name:
            entity = get_entity(entity_name)
            if entity and len(entity.edge_cases) > 0:
                opportunities.append(f"Address {len(entity.edge_cases)} edge cases in {entity_name} workflow")

        return opportunities

    async def setup_alerts(
        self,
        alert_conditions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Setup journey monitoring alerts.

        Args:
            alert_conditions: Conditions for triggering alerts

        Returns:
            Alert configuration
        """
        alerts_config = {
            "alert_id": f"ALERT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "conditions": alert_conditions,
            "enabled": True,
            "channels": ["email", "slack", "dashboard"],
            "frequency": "real-time"
        }

        logger.info(
            "Journey alerts configured",
            alert_id=alerts_config["alert_id"]
        )

        return alerts_config


def get_journey_monitoring_orchestrator() -> JourneyMonitoringOrchestrator:
    """Get journey monitoring orchestrator instance."""
    return JourneyMonitoringOrchestrator()