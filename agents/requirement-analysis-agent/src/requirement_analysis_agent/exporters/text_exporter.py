"""Text exporter for human-readable analysis reports."""

from typing import Optional

from requirement_analysis_agent.exporters.base import BaseExporter
from requirement_analysis_agent.models import AnalysisResult, ExportConfig


class TextExporter(BaseExporter):
    """Export analysis results to human-readable text format."""

    @property
    def format_name(self) -> str:
        return "text"

    @property
    def file_extension(self) -> str:
        return ".txt"

    def export(self, result: AnalysisResult) -> str:
        """Export analysis result to text.

        Args:
            result: Analysis result to export

        Returns:
            Human-readable text report
        """
        lines = []

        # Header
        lines.append("=" * 80)
        lines.append("REQUIREMENT ANALYSIS REPORT")
        lines.append("=" * 80)
        lines.append("")

        # Summary
        lines.append("SUMMARY")
        lines.append("-" * 40)
        lines.append(f"Request ID: {result.request_id}")
        lines.append(f"Title: {result.extracted_requirement.title}")
        lines.append(f"Input Type: {result.extracted_requirement.input_type.value}")
        lines.append(f"Status: {'Success' if result.success else 'Failed'}")
        if result.error:
            lines.append(f"Error: {result.error}")
        lines.append("")

        # Quality Score
        lines.append(self._format_quality_score(result))
        lines.append("")

        # Extracted Structure
        lines.append(self._format_structure(result))
        lines.append("")

        # Gaps
        if result.gaps:
            lines.append(self._format_gaps(result))
            lines.append("")

        # Questions
        if result.questions:
            lines.append(self._format_questions(result))
            lines.append("")

        # Generated ACs
        if self.config.include_generated_acs and result.generated_acs:
            lines.append(self._format_generated_acs(result))
            lines.append("")

        # Domain Validation
        if result.domain_validation:
            lines.append(self._format_domain_validation(result))
            lines.append("")

        # Recommendations
        if self.config.include_recommendations:
            lines.append(self._format_recommendations(result))
            lines.append("")

        # Metadata
        lines.append(self._format_metadata(result))

        # Footer
        lines.append("")
        lines.append("=" * 80)
        lines.append("End of Report")
        lines.append("=" * 80)

        return "\n".join(lines)

    def _format_quality_score(self, result: AnalysisResult) -> str:
        """Format quality score section."""
        qs = result.quality_score
        lines = [
            "QUALITY SCORE",
            "-" * 40,
            f"Overall Score: {qs.overall_score}/100 ({qs.overall_grade.value}) {self._format_grade_emoji(qs.overall_grade.value)}",
            "",
            "Dimensions:",
            f"  Clarity:      {qs.clarity.score}/100 ({qs.clarity.grade.value})",
            f"  Completeness: {qs.completeness.score}/100 ({qs.completeness.grade.value})",
            f"  Testability:  {qs.testability.score}/100 ({qs.testability.grade.value})",
            f"  Consistency:  {qs.consistency.score}/100 ({qs.consistency.grade.value})",
        ]

        # Add dimension issues
        for dim_name, dim in [
            ("Clarity", qs.clarity),
            ("Completeness", qs.completeness),
            ("Testability", qs.testability),
            ("Consistency", qs.consistency),
        ]:
            if dim.issues:
                lines.append(f"\n  {dim_name} Issues:")
                for issue in dim.issues:
                    lines.append(f"    - {issue}")

        lines.append(f"\nRecommendation: {qs.recommendation}")

        return "\n".join(lines)

    def _format_structure(self, result: AnalysisResult) -> str:
        """Format extracted structure section."""
        s = result.extracted_requirement.structure
        lines = [
            "REQUIREMENT STRUCTURE",
            "-" * 40,
            f"Actor: {s.actor}",
        ]

        if s.secondary_actors:
            lines.append(f"Secondary Actors: {', '.join(s.secondary_actors)}")

        lines.extend([
            f"Action: {s.action}",
            f"Object: {s.object}",
            f"Outcome: {s.outcome}",
        ])

        if s.preconditions:
            lines.append("\nPreconditions:")
            for pc in s.preconditions:
                lines.append(f"  - {pc}")

        if s.postconditions:
            lines.append("\nPostconditions:")
            for pc in s.postconditions:
                lines.append(f"  - {pc}")

        if s.triggers:
            lines.append("\nTriggers:")
            for t in s.triggers:
                lines.append(f"  - {t}")

        if s.constraints:
            lines.append("\nConstraints:")
            for c in s.constraints:
                lines.append(f"  - {c}")

        if s.entities:
            lines.append(f"\nDomain Entities: {', '.join(s.entities)}")

        return "\n".join(lines)

    def _format_gaps(self, result: AnalysisResult) -> str:
        """Format gaps section."""
        lines = [
            "DETECTED GAPS",
            "-" * 40,
            f"Total Gaps: {len(result.gaps)}",
            "",
        ]

        for gap in result.gaps:
            emoji = self._format_severity_emoji(gap.severity.value)
            lines.append(f"{emoji} [{gap.id}] {gap.category.value.upper()} ({gap.severity.value})")
            lines.append(f"   Location: {gap.location}")
            lines.append(f"   Issue: {gap.description}")
            lines.append(f"   Suggestion: {gap.suggestion}")
            lines.append("")

        return "\n".join(lines)

    def _format_questions(self, result: AnalysisResult) -> str:
        """Format questions section."""
        lines = [
            "CLARIFYING QUESTIONS",
            "-" * 40,
            f"Total Questions: {len(result.questions)}",
            "",
        ]

        for q in result.questions:
            emoji = self._format_severity_emoji(q.priority.value)
            lines.append(f"{emoji} [{q.id}] {q.category.value.upper()} ({q.priority.value})")
            lines.append(f"   Question: {q.question}")
            lines.append(f"   Context: {q.context}")
            if q.suggested_answers:
                lines.append("   Suggested Answers:")
                for ans in q.suggested_answers:
                    lines.append(f"     - {ans}")
            if q.answer:
                lines.append(f"   Answer: {q.answer}")
            lines.append("")

        return "\n".join(lines)

    def _format_generated_acs(self, result: AnalysisResult) -> str:
        """Format generated acceptance criteria section."""
        lines = [
            "GENERATED ACCEPTANCE CRITERIA",
            "-" * 40,
            f"Total Generated: {len(result.generated_acs)}",
            "",
        ]

        for ac in result.generated_acs:
            status = "Accepted" if ac.accepted else "Pending"
            confidence_pct = int(ac.confidence * 100)
            lines.append(f"[{ac.id}] {status} (Confidence: {confidence_pct}%)")
            lines.append(f"   Source: {ac.source.value}")
            lines.append(f"   Text: {ac.text}")
            lines.append(f"   Gherkin:")
            for gherkin_line in ac.gherkin.split("\n"):
                lines.append(f"     {gherkin_line}")
            lines.append("")

        return "\n".join(lines)

    def _format_domain_validation(self, result: AnalysisResult) -> str:
        """Format domain validation section."""
        dv = result.domain_validation
        if not dv:
            return ""

        status = "Valid" if dv.valid else "Invalid"
        lines = [
            "DOMAIN VALIDATION",
            "-" * 40,
            f"Status: {status}",
            "",
        ]

        if dv.entities_found:
            lines.append("Mapped Entities:")
            for e in dv.entities_found:
                confidence_pct = int(e.confidence * 100)
                lines.append(f"  - {e.term} -> {e.mapped_entity} ({confidence_pct}%)")
                lines.append(f"    {e.domain_description}")
            lines.append("")

        if dv.rules_applicable:
            lines.append("Applicable Rules:")
            for r in dv.rules_applicable:
                lines.append(f"  - [{r.rule_id}] {r.rule} (Relevance: {r.relevance.value})")
            lines.append("")

        if dv.warnings:
            lines.append("Warnings:")
            for w in dv.warnings:
                lines.append(f"  - [{w.type}] {w.message}")
                lines.append(f"    Suggestion: {w.suggestion}")
            lines.append("")

        return "\n".join(lines)

    def _format_recommendations(self, result: AnalysisResult) -> str:
        """Format recommendations section."""
        lines = [
            "RECOMMENDATIONS",
            "-" * 40,
        ]

        # Ready for test generation?
        if result.ready_for_test_generation:
            lines.append("Ready for Test Generation: Yes")
        else:
            lines.append("Ready for Test Generation: No")
            if result.blockers:
                lines.append("\nBlockers:")
                for b in result.blockers:
                    lines.append(f"  - {b}")

        # Action items based on quality
        lines.append("\nAction Items:")
        qs = result.quality_score

        if qs.overall_score >= 80:
            lines.append("  - Requirement is well-defined. Proceed to test case generation.")
        elif qs.overall_score >= 60:
            lines.append("  - Address the identified gaps before proceeding.")
            lines.append("  - Answer the clarifying questions to improve completeness.")
        elif qs.overall_score >= 40:
            lines.append("  - Significant improvements needed. Review all gaps and questions.")
            lines.append("  - Consider consulting with stakeholders for clarification.")
        else:
            lines.append("  - Major revision required. The requirement needs substantial work.")
            lines.append("  - Schedule a requirements review meeting.")

        # Specific action items from gaps
        high_gaps = [g for g in result.gaps if g.severity.value == "high"]
        if high_gaps:
            lines.append("\nHigh Priority Fixes:")
            for g in high_gaps[:5]:  # Top 5
                lines.append(f"  - {g.suggestion}")

        return "\n".join(lines)

    def _format_metadata(self, result: AnalysisResult) -> str:
        """Format metadata section."""
        m = result.metadata
        lines = [
            "ANALYSIS METADATA",
            "-" * 40,
            f"LLM Provider: {m.llm_provider}",
            f"Model: {m.llm_model}",
            f"Tokens Used: {m.tokens_used:,}",
            f"Analysis Time: {m.analysis_time_ms:.2f}ms",
            f"Agent Version: {m.agent_version}",
        ]
        return "\n".join(lines)
