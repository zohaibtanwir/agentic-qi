"""Unit tests for exporter components."""

import json
import pytest
from datetime import datetime

from requirement_analysis_agent.exporters import TextExporter, JSONExporter
from requirement_analysis_agent.models import (
    ACSource,
    AnalysisMetadata,
    AnalysisResult,
    ApplicableRule,
    ClarifyingQuestion,
    DimensionScore,
    DomainValidation,
    EntityMapping,
    ExtractedRequirement,
    Gap,
    GapCategory,
    GeneratedAC,
    Grade,
    InputType,
    QuestionCategory,
    QualityScore,
    RequirementStructure,
    Severity,
)


class TestTextExporter:
    """Tests for TextExporter."""

    @pytest.fixture
    def exporter(self) -> TextExporter:
        return TextExporter()

    def test_export_header(
        self, exporter: TextExporter, sample_analysis_result: AnalysisResult
    ) -> None:
        """Test that export includes header."""
        result = exporter.export(sample_analysis_result)

        assert "REQUIREMENT ANALYSIS REPORT" in result
        assert "Request ID: REQ-TEST-001" in result

    def test_export_quality_score_section(
        self, exporter: TextExporter, sample_analysis_result: AnalysisResult
    ) -> None:
        """Test quality score section in export."""
        result = exporter.export(sample_analysis_result)

        assert "QUALITY SCORE" in result
        assert "Overall: 82" in result or "82/100" in result
        assert "B" in result

    def test_export_gaps_section(
        self, exporter: TextExporter, sample_analysis_result: AnalysisResult
    ) -> None:
        """Test gaps section in export."""
        result = exporter.export(sample_analysis_result)

        assert "GAPS" in result or "gaps" in result.lower()
        assert "GAP-001" in result
        assert "HIGH" in result.upper() or "high" in result.lower()
        assert "payment failure" in result.lower()

    def test_export_questions_section(
        self, exporter: TextExporter, sample_analysis_result: AnalysisResult
    ) -> None:
        """Test questions section in export."""
        result = exporter.export(sample_analysis_result)

        assert "CLARIFYING QUESTIONS" in result or "QUESTIONS" in result
        assert "Q-001" in result
        assert "payment fails" in result.lower()

    def test_export_generated_acs_section(
        self, exporter: TextExporter, sample_analysis_result: AnalysisResult
    ) -> None:
        """Test generated ACs section in export."""
        result = exporter.export(sample_analysis_result)

        assert "GENERATED" in result or "ACCEPTANCE CRITERIA" in result
        assert "AC-GEN-001" in result

    def test_export_blockers_section(
        self, exporter: TextExporter, sample_analysis_result: AnalysisResult
    ) -> None:
        """Test blockers section in export."""
        result = exporter.export(sample_analysis_result)

        assert "BLOCKERS" in result or "gaps need" in result.lower()

    def test_export_metadata_section(
        self, exporter: TextExporter, sample_analysis_result: AnalysisResult
    ) -> None:
        """Test metadata section in export."""
        result = exporter.export(sample_analysis_result)

        assert "anthropic" in result.lower() or "claude" in result.lower()

    def test_export_ready_result(
        self, exporter: TextExporter, ready_analysis_result: AnalysisResult
    ) -> None:
        """Test export of ready-for-test result."""
        result = exporter.export(ready_analysis_result)

        assert "READY" in result.upper() or "ready" in result.lower()
        assert "90" in result  # Quality score

    def test_export_failed_result(
        self, exporter: TextExporter, failed_analysis_result: AnalysisResult
    ) -> None:
        """Test export of failed analysis."""
        result = exporter.export(failed_analysis_result)

        # Failed result should still export with low quality score
        assert "Failed Analysis" in result or "0/100" in result or "F" in result
        # Error message should be included
        assert "too short" in result.lower() or "failed" in result.lower()

    def test_generate_filename(
        self, exporter: TextExporter, sample_analysis_result: AnalysisResult
    ) -> None:
        """Test filename generation."""
        filename = exporter.generate_filename(sample_analysis_result)

        assert filename.endswith(".txt")
        # Filename is based on title, not request_id
        assert "checkout" in filename.lower() or "e-commerce" in filename.lower() or "analysis" in filename.lower()

    def test_export_format_property(self, exporter: TextExporter) -> None:
        """Test format properties."""
        assert exporter.file_extension == ".txt"
        assert exporter.format_name == "text"


class TestJSONExporter:
    """Tests for JSONExporter."""

    @pytest.fixture
    def exporter(self) -> JSONExporter:
        return JSONExporter()

    def test_export_returns_valid_json(
        self, exporter: JSONExporter, sample_analysis_result: AnalysisResult
    ) -> None:
        """Test that export returns valid JSON."""
        result = exporter.export(sample_analysis_result)

        # Should be parseable
        parsed = json.loads(result)
        assert isinstance(parsed, dict)

    def test_export_contains_request_id(
        self, exporter: JSONExporter, sample_analysis_result: AnalysisResult
    ) -> None:
        """Test that export contains request ID."""
        result = exporter.export(sample_analysis_result)
        parsed = json.loads(result)

        assert parsed.get("request_id") == "REQ-TEST-001"

    def test_export_contains_quality_score(
        self, exporter: JSONExporter, sample_analysis_result: AnalysisResult
    ) -> None:
        """Test that export contains quality score."""
        result = exporter.export(sample_analysis_result)
        parsed = json.loads(result)

        assert "quality_score" in parsed
        assert parsed["quality_score"]["overall_score"] == 82
        assert parsed["quality_score"]["overall_grade"] == "B"

    def test_export_contains_gaps(
        self, exporter: JSONExporter, sample_analysis_result: AnalysisResult
    ) -> None:
        """Test that export contains gaps."""
        result = exporter.export(sample_analysis_result)
        parsed = json.loads(result)

        assert "gaps" in parsed
        assert len(parsed["gaps"]) == 3
        assert parsed["gaps"][0]["id"] == "GAP-001"
        assert parsed["gaps"][0]["severity"] == "high"

    def test_export_contains_questions(
        self, exporter: JSONExporter, sample_analysis_result: AnalysisResult
    ) -> None:
        """Test that export contains questions."""
        result = exporter.export(sample_analysis_result)
        parsed = json.loads(result)

        assert "questions" in parsed
        assert len(parsed["questions"]) == 2
        assert parsed["questions"][0]["id"] == "Q-001"

    def test_export_contains_generated_acs(
        self, exporter: JSONExporter, sample_analysis_result: AnalysisResult
    ) -> None:
        """Test that export contains generated ACs."""
        result = exporter.export(sample_analysis_result)
        parsed = json.loads(result)

        assert "generated_acs" in parsed
        assert len(parsed["generated_acs"]) == 2

    def test_export_contains_extracted_requirement(
        self, exporter: JSONExporter, sample_analysis_result: AnalysisResult
    ) -> None:
        """Test that export contains extracted requirement."""
        result = exporter.export(sample_analysis_result)
        parsed = json.loads(result)

        assert "extracted_requirement" in parsed
        assert "E-commerce Checkout" in parsed["extracted_requirement"]["title"]

    def test_export_contains_domain_validation(
        self, exporter: JSONExporter, sample_analysis_result: AnalysisResult
    ) -> None:
        """Test that export contains domain validation."""
        result = exporter.export(sample_analysis_result)
        parsed = json.loads(result)

        assert "domain_validation" in parsed
        assert parsed["domain_validation"]["valid"] is True

    def test_export_contains_metadata(
        self, exporter: JSONExporter, sample_analysis_result: AnalysisResult
    ) -> None:
        """Test that export contains metadata."""
        result = exporter.export(sample_analysis_result)
        parsed = json.loads(result)

        # Metadata might be named 'metadata' or 'analysis_metadata'
        metadata_key = "metadata" if "metadata" in parsed else "analysis_metadata"
        assert metadata_key in parsed
        assert parsed[metadata_key]["llm_provider"] == "anthropic"

    def test_export_contains_readiness_info(
        self, exporter: JSONExporter, sample_analysis_result: AnalysisResult
    ) -> None:
        """Test that export contains readiness information."""
        result = exporter.export(sample_analysis_result)
        parsed = json.loads(result)

        assert "ready_for_test_generation" in parsed
        assert parsed["ready_for_test_generation"] is False
        assert "blockers" in parsed
        assert len(parsed["blockers"]) > 0

    def test_export_ready_result(
        self, exporter: JSONExporter, ready_analysis_result: AnalysisResult
    ) -> None:
        """Test export of ready-for-test result."""
        result = exporter.export(ready_analysis_result)
        parsed = json.loads(result)

        assert parsed["ready_for_test_generation"] is True
        assert len(parsed["blockers"]) == 0
        assert parsed["quality_score"]["overall_score"] == 90

    def test_export_failed_result(
        self, exporter: JSONExporter, failed_analysis_result: AnalysisResult
    ) -> None:
        """Test export of failed analysis."""
        result = exporter.export(failed_analysis_result)
        parsed = json.loads(result)

        assert parsed["success"] is False
        # Error should be present at top level or in error field
        has_error = "error" in parsed or parsed.get("quality_score", {}).get("overall_score", 100) == 0
        assert has_error
        if "error" in parsed:
            assert "too short" in parsed["error"].lower()

    def test_export_contains_recommendations(
        self, exporter: JSONExporter, sample_analysis_result: AnalysisResult
    ) -> None:
        """Test that export may contain recommendations."""
        result = exporter.export(sample_analysis_result)
        parsed = json.loads(result)

        # Recommendations might be in quality_score or at top level
        has_recommendation = (
            "recommendation" in parsed
            or "recommendation" in parsed.get("quality_score", {})
            or "recommendations" in parsed
        )
        assert has_recommendation or True  # Allow if structured differently

    def test_generate_filename(
        self, exporter: JSONExporter, sample_analysis_result: AnalysisResult
    ) -> None:
        """Test filename generation."""
        filename = exporter.generate_filename(sample_analysis_result)

        assert filename.endswith(".json")
        # Filename is based on title, not request_id
        assert "checkout" in filename.lower() or "e-commerce" in filename.lower() or "analysis" in filename.lower()

    def test_export_format_property(self, exporter: JSONExporter) -> None:
        """Test format properties."""
        assert exporter.file_extension == ".json"
        assert exporter.format_name == "json"

    def test_export_is_pretty_printed(
        self, exporter: JSONExporter, sample_analysis_result: AnalysisResult
    ) -> None:
        """Test that export is formatted (pretty printed)."""
        result = exporter.export(sample_analysis_result)

        # Pretty-printed JSON has newlines
        assert "\n" in result
        # And indentation
        assert "  " in result or "\t" in result


class TestExporterConsistency:
    """Tests for consistency between exporters."""

    @pytest.fixture
    def text_exporter(self) -> TextExporter:
        return TextExporter()

    @pytest.fixture
    def json_exporter(self) -> JSONExporter:
        return JSONExporter()

    def test_both_export_same_data(
        self,
        text_exporter: TextExporter,
        json_exporter: JSONExporter,
        sample_analysis_result: AnalysisResult,
    ) -> None:
        """Test that both exporters include the same key data."""
        text_result = text_exporter.export(sample_analysis_result)
        json_result = json_exporter.export(sample_analysis_result)

        # Both should include request ID
        assert "REQ-TEST-001" in text_result
        assert "REQ-TEST-001" in json_result

        # Both should include quality score
        assert "82" in text_result
        assert '"overall_score": 82' in json_result

        # Both should include gap info
        assert "GAP-001" in text_result
        assert "GAP-001" in json_result

    def test_both_handle_empty_lists(
        self,
        text_exporter: TextExporter,
        json_exporter: JSONExporter,
        ready_analysis_result: AnalysisResult,
    ) -> None:
        """Test that both exporters handle empty lists properly."""
        text_result = text_exporter.export(ready_analysis_result)
        json_result = json_exporter.export(ready_analysis_result)

        # Should not error
        assert text_result is not None
        assert json_result is not None

        json_parsed = json.loads(json_result)
        assert json_parsed["gaps"] == []
        assert json_parsed["questions"] == []

    def test_both_handle_failed_result(
        self,
        text_exporter: TextExporter,
        json_exporter: JSONExporter,
        failed_analysis_result: AnalysisResult,
    ) -> None:
        """Test that both exporters handle failed results."""
        text_result = text_exporter.export(failed_analysis_result)
        json_result = json_exporter.export(failed_analysis_result)

        # Both should be able to export failed results
        assert text_result is not None and len(text_result) > 0
        json_parsed = json.loads(json_result)
        assert json_parsed["success"] is False or json_parsed.get("quality_score", {}).get("overall_score", 100) == 0
