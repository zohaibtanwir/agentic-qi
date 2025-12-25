"""JSON exporter for machine-readable analysis reports."""

import json
from datetime import datetime, timezone
from typing import Any, Optional

from requirement_analysis_agent.exporters.base import BaseExporter
from requirement_analysis_agent.models import AnalysisResult, ExportConfig


class JSONExporter(BaseExporter):
    """Export analysis results to JSON format."""

    def __init__(self, config: Optional[ExportConfig] = None, indent: int = 2):
        """Initialize JSON exporter.

        Args:
            config: Export configuration
            indent: JSON indentation level
        """
        super().__init__(config)
        self.indent = indent

    @property
    def format_name(self) -> str:
        return "json"

    @property
    def file_extension(self) -> str:
        return ".json"

    def export(self, result: AnalysisResult) -> str:
        """Export analysis result to JSON.

        Args:
            result: Analysis result to export

        Returns:
            JSON string
        """
        data = self._build_export_dict(result)
        return json.dumps(data, indent=self.indent, ensure_ascii=False)

    def _build_export_dict(self, result: AnalysisResult) -> dict[str, Any]:
        """Build the export dictionary.

        Args:
            result: Analysis result

        Returns:
            Dictionary for JSON serialization
        """
        export_data = {
            "export_metadata": {
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "format": self.format_name,
                "config": {
                    "include_recommendations": self.config.include_recommendations,
                    "include_generated_acs": self.config.include_generated_acs,
                },
            },
            "request_id": result.request_id,
            "success": result.success,
            "error": result.error,
            "quality_score": self._format_quality_score(result),
            "extracted_requirement": self._format_extracted_requirement(result),
            "gaps": self._format_gaps(result),
            "questions": self._format_questions(result),
            "ready_for_test_generation": result.ready_for_test_generation,
            "blockers": result.blockers,
            "analysis_metadata": self._format_metadata(result),
        }

        # Optionally include generated ACs
        if self.config.include_generated_acs:
            export_data["generated_acs"] = self._format_generated_acs(result)

        # Include domain validation if present
        if result.domain_validation:
            export_data["domain_validation"] = self._format_domain_validation(result)

        # Include recommendations if configured
        if self.config.include_recommendations:
            export_data["recommendations"] = self._build_recommendations(result)

        return export_data

    def _format_quality_score(self, result: AnalysisResult) -> dict[str, Any]:
        """Format quality score for JSON."""
        qs = result.quality_score
        return {
            "overall_score": qs.overall_score,
            "overall_grade": qs.overall_grade.value,
            "recommendation": qs.recommendation,
            "dimensions": {
                "clarity": {
                    "score": qs.clarity.score,
                    "grade": qs.clarity.grade.value,
                    "issues": qs.clarity.issues,
                },
                "completeness": {
                    "score": qs.completeness.score,
                    "grade": qs.completeness.grade.value,
                    "issues": qs.completeness.issues,
                },
                "testability": {
                    "score": qs.testability.score,
                    "grade": qs.testability.grade.value,
                    "issues": qs.testability.issues,
                },
                "consistency": {
                    "score": qs.consistency.score,
                    "grade": qs.consistency.grade.value,
                    "issues": qs.consistency.issues,
                },
            },
        }

    def _format_extracted_requirement(self, result: AnalysisResult) -> dict[str, Any]:
        """Format extracted requirement for JSON."""
        er = result.extracted_requirement
        s = er.structure
        return {
            "title": er.title,
            "description": er.description,
            "input_type": er.input_type.value,
            "original_acs": er.original_acs,
            "structure": {
                "actor": s.actor,
                "secondary_actors": s.secondary_actors,
                "action": s.action,
                "object": s.object,
                "outcome": s.outcome,
                "preconditions": s.preconditions,
                "postconditions": s.postconditions,
                "triggers": s.triggers,
                "constraints": s.constraints,
                "entities": s.entities,
            },
        }

    def _format_gaps(self, result: AnalysisResult) -> list[dict[str, Any]]:
        """Format gaps for JSON."""
        return [
            {
                "id": g.id,
                "category": g.category.value,
                "severity": g.severity.value,
                "description": g.description,
                "location": g.location,
                "suggestion": g.suggestion,
            }
            for g in result.gaps
        ]

    def _format_questions(self, result: AnalysisResult) -> list[dict[str, Any]]:
        """Format questions for JSON."""
        return [
            {
                "id": q.id,
                "priority": q.priority.value,
                "category": q.category.value,
                "question": q.question,
                "context": q.context,
                "suggested_answers": q.suggested_answers,
                "answer": q.answer,
            }
            for q in result.questions
        ]

    def _format_generated_acs(self, result: AnalysisResult) -> list[dict[str, Any]]:
        """Format generated ACs for JSON."""
        return [
            {
                "id": ac.id,
                "source": ac.source.value,
                "confidence": ac.confidence,
                "text": ac.text,
                "gherkin": ac.gherkin,
                "accepted": ac.accepted,
            }
            for ac in result.generated_acs
        ]

    def _format_domain_validation(self, result: AnalysisResult) -> dict[str, Any]:
        """Format domain validation for JSON."""
        dv = result.domain_validation
        if not dv:
            return {}

        return {
            "valid": dv.valid,
            "entities_found": [
                {
                    "term": e.term,
                    "mapped_entity": e.mapped_entity,
                    "confidence": e.confidence,
                    "domain_description": e.domain_description,
                }
                for e in dv.entities_found
            ],
            "rules_applicable": [
                {
                    "rule_id": r.rule_id,
                    "rule": r.rule,
                    "relevance": r.relevance.value,
                }
                for r in dv.rules_applicable
            ],
            "warnings": [
                {
                    "type": w.type,
                    "message": w.message,
                    "suggestion": w.suggestion,
                }
                for w in dv.warnings
            ],
        }

    def _format_metadata(self, result: AnalysisResult) -> dict[str, Any]:
        """Format metadata for JSON."""
        m = result.metadata
        return {
            "llm_provider": m.llm_provider,
            "llm_model": m.llm_model,
            "tokens_used": m.tokens_used,
            "analysis_time_ms": m.analysis_time_ms,
            "input_type": m.input_type.value,
            "agent_version": m.agent_version,
        }

    def _build_recommendations(self, result: AnalysisResult) -> dict[str, Any]:
        """Build recommendations section."""
        qs = result.quality_score
        recommendations = {
            "summary": "",
            "action_items": [],
            "priority_fixes": [],
        }

        # Summary based on quality score
        if qs.overall_score >= 80:
            recommendations["summary"] = "Requirement is well-defined. Ready for test case generation."
        elif qs.overall_score >= 60:
            recommendations["summary"] = "Requirement needs minor improvements. Address gaps and questions."
        elif qs.overall_score >= 40:
            recommendations["summary"] = "Significant improvements needed. Review with stakeholders."
        else:
            recommendations["summary"] = "Major revision required. Schedule requirements review."

        # Action items
        if qs.overall_score < 80:
            if result.gaps:
                recommendations["action_items"].append(
                    f"Address {len(result.gaps)} identified gaps"
                )
            if result.questions:
                recommendations["action_items"].append(
                    f"Answer {len(result.questions)} clarifying questions"
                )
            if not result.ready_for_test_generation:
                recommendations["action_items"].append(
                    "Resolve blockers before test generation"
                )

        # High priority fixes from gaps
        high_gaps = [g for g in result.gaps if g.severity.value == "high"]
        recommendations["priority_fixes"] = [
            {
                "gap_id": g.id,
                "suggestion": g.suggestion,
            }
            for g in high_gaps[:5]
        ]

        return recommendations
