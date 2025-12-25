"""Unit tests for input parsers."""

import pytest

from requirement_analysis_agent.models import (
    InputType,
    JiraStoryInput,
    FreeFormInput,
    TranscriptInput,
)
from requirement_analysis_agent.parsers import (
    ParsedInput,
    JiraStoryParser,
    FreeFormParser,
    TranscriptParser,
)


class TestJiraStoryParser:
    """Tests for JiraStoryParser."""

    @pytest.fixture
    def parser(self) -> JiraStoryParser:
        """Create parser instance."""
        return JiraStoryParser()

    def test_input_type(self, parser: JiraStoryParser) -> None:
        """Test that input type is correct."""
        assert parser.input_type == InputType.JIRA

    def test_validate_valid_input(self, parser: JiraStoryParser) -> None:
        """Test validation passes for valid input."""
        input_data = JiraStoryInput(
            key="ECOM-1234",
            summary="Add wishlist feature",
            description="As a customer, I want to save products to a wishlist",
        )
        errors = parser.validate(input_data)
        assert errors == []

    def test_validate_missing_key(self, parser: JiraStoryParser) -> None:
        """Test validation fails for missing key."""
        input_data = JiraStoryInput(
            key="",
            summary="Test",
            description="Description",
        )
        errors = parser.validate(input_data)
        assert len(errors) == 1
        assert "key is required" in errors[0].lower()

    def test_validate_invalid_key_format(self, parser: JiraStoryParser) -> None:
        """Test validation fails for invalid key format."""
        input_data = JiraStoryInput(
            key="invalid",
            summary="Test",
            description="Description",
        )
        errors = parser.validate(input_data)
        assert len(errors) == 1
        assert "invalid jira key format" in errors[0].lower()

    def test_validate_missing_summary(self, parser: JiraStoryParser) -> None:
        """Test validation fails for missing summary."""
        input_data = JiraStoryInput(
            key="ECOM-123",
            summary="",
            description="Description",
        )
        errors = parser.validate(input_data)
        assert len(errors) == 1
        assert "summary is required" in errors[0].lower()

    def test_validate_missing_description(self, parser: JiraStoryParser) -> None:
        """Test validation fails for missing description."""
        input_data = JiraStoryInput(
            key="ECOM-123",
            summary="Test summary",
            description="",
        )
        errors = parser.validate(input_data)
        assert len(errors) == 1
        assert "description is required" in errors[0].lower()

    def test_parse_basic_story(self, parser: JiraStoryParser) -> None:
        """Test parsing a basic Jira story."""
        input_data = JiraStoryInput(
            key="ECOM-1234",
            summary="Add wishlist feature",
            description="As a customer, I want to save products to a wishlist so that I can purchase them later.",
            acceptance_criteria=["User can add product", "User can remove product"],
        )
        result = parser.parse(input_data)

        assert result.input_type == InputType.JIRA
        assert "[ECOM-1234]" in result.title
        assert "wishlist" in result.title.lower()
        assert len(result.acceptance_criteria) >= 2
        assert result.metadata["jira_key"] == "ECOM-1234"

    def test_parse_with_metadata(self, parser: JiraStoryParser) -> None:
        """Test parsing story with full metadata."""
        input_data = JiraStoryInput(
            key="ECOM-5678",
            summary="Checkout enhancement",
            description="Improve the checkout flow",
            labels=["checkout", "enhancement"],
            components=["frontend", "payment"],
            priority="High",
            story_points=8,
        )
        result = parser.parse(input_data)

        assert "Labels" in result.context
        assert "Components" in result.context
        assert "Priority" in result.context
        assert result.metadata["story_points"] == 8

    def test_parse_extracts_acs_from_description(self, parser: JiraStoryParser) -> None:
        """Test that ACs are extracted from description."""
        input_data = JiraStoryInput(
            key="ECOM-999",
            summary="Test feature",
            description="""
            Feature description here.

            Acceptance Criteria:
            - User can do action A
            - User can do action B
            - System validates input
            """,
            acceptance_criteria=[],
        )
        result = parser.parse(input_data)

        assert len(result.acceptance_criteria) >= 3

    def test_parse_extracts_gherkin_from_description(self, parser: JiraStoryParser) -> None:
        """Test that Gherkin scenarios are extracted."""
        input_data = JiraStoryInput(
            key="ECOM-100",
            summary="Login feature",
            description="""
            User login functionality.

            Given the user is on the login page
            When they enter valid credentials
            Then they should be logged in
            """,
            acceptance_criteria=[],
        )
        result = parser.parse(input_data)

        # Should find the Gherkin scenario
        assert len(result.acceptance_criteria) >= 1
        found_gherkin = any("given" in ac.lower() for ac in result.acceptance_criteria)
        assert found_gherkin

    def test_parse_if_valid_returns_errors_on_invalid(self, parser: JiraStoryParser) -> None:
        """Test parse_if_valid returns errors for invalid input."""
        input_data = JiraStoryInput(
            key="",
            summary="",
            description="",
        )
        result, errors = parser.parse_if_valid(input_data)

        assert result is None
        assert len(errors) >= 3  # key, summary, description


class TestFreeFormParser:
    """Tests for FreeFormParser."""

    @pytest.fixture
    def parser(self) -> FreeFormParser:
        """Create parser instance."""
        return FreeFormParser()

    def test_input_type(self, parser: FreeFormParser) -> None:
        """Test that input type is correct."""
        assert parser.input_type == InputType.FREE_FORM

    def test_validate_valid_input(self, parser: FreeFormParser) -> None:
        """Test validation passes for valid input."""
        input_data = FreeFormInput(
            text="As a user, I want to be able to search for products by name so I can find what I need.",
        )
        errors = parser.validate(input_data)
        assert errors == []

    def test_validate_missing_text(self, parser: FreeFormParser) -> None:
        """Test validation fails for missing text."""
        input_data = FreeFormInput(text="")
        errors = parser.validate(input_data)
        assert len(errors) == 1
        assert "required" in errors[0].lower()

    def test_validate_short_text(self, parser: FreeFormParser) -> None:
        """Test validation fails for too short text."""
        input_data = FreeFormInput(text="Short")
        errors = parser.validate(input_data)
        assert len(errors) == 1
        assert "too short" in errors[0].lower()

    def test_parse_user_story_format(self, parser: FreeFormParser) -> None:
        """Test parsing user story format text."""
        input_data = FreeFormInput(
            text="As a customer, I want to add items to my cart so that I can purchase multiple products.",
        )
        result = parser.parse(input_data)

        assert result.input_type == InputType.FREE_FORM
        assert result.title  # Should have extracted a title
        assert result.metadata.get("format") == "user_story"

    def test_parse_with_provided_title(self, parser: FreeFormParser) -> None:
        """Test parsing with explicitly provided title."""
        input_data = FreeFormInput(
            text="Users should be able to search for products",
            title="Product Search Feature",
        )
        result = parser.parse(input_data)

        assert result.title == "Product Search Feature"

    def test_parse_extracts_criteria_from_list(self, parser: FreeFormParser) -> None:
        """Test extracting criteria from bulleted list."""
        input_data = FreeFormInput(
            text="""
            Product search feature

            Acceptance Criteria:
            - User can search by product name
            - Results are displayed in a grid
            - User can filter results by category
            """,
        )
        result = parser.parse(input_data)

        assert len(result.acceptance_criteria) >= 3

    def test_parse_extracts_gherkin(self, parser: FreeFormParser) -> None:
        """Test extracting Gherkin scenarios."""
        input_data = FreeFormInput(
            text="""
            Search feature requirements

            Given the user is on the search page
            When they enter a search term
            Then they should see matching results
            """,
        )
        result = parser.parse(input_data)

        assert result.metadata.get("has_gherkin") is True

    def test_parse_extracts_should_statements(self, parser: FreeFormParser) -> None:
        """Test extracting 'should' statements."""
        input_data = FreeFormInput(
            text="""
            The system should display search results within 2 seconds.
            The system should support fuzzy matching.
            Users should be able to save search queries.
            """,
        )
        result = parser.parse(input_data)

        # Should extract some criteria
        assert len(result.acceptance_criteria) >= 1

    def test_parse_with_context(self, parser: FreeFormParser) -> None:
        """Test parsing with additional context."""
        input_data = FreeFormInput(
            text="Users need to be able to checkout their shopping cart",
            context="This is for the e-commerce checkout flow",
        )
        result = parser.parse(input_data)

        assert "e-commerce" in result.context


class TestTranscriptParser:
    """Tests for TranscriptParser."""

    @pytest.fixture
    def parser(self) -> TranscriptParser:
        """Create parser instance."""
        return TranscriptParser()

    def test_input_type(self, parser: TranscriptParser) -> None:
        """Test that input type is correct."""
        assert parser.input_type == InputType.TRANSCRIPT

    def test_validate_valid_input(self, parser: TranscriptParser) -> None:
        """Test validation passes for valid input."""
        input_data = TranscriptInput(
            transcript="PM: We need a new checkout feature.\nDev: What about error handling?",
        )
        errors = parser.validate(input_data)
        assert errors == []

    def test_validate_missing_transcript(self, parser: TranscriptParser) -> None:
        """Test validation fails for missing transcript."""
        input_data = TranscriptInput(transcript="")
        errors = parser.validate(input_data)
        assert len(errors) == 1
        assert "required" in errors[0].lower()

    def test_validate_short_transcript(self, parser: TranscriptParser) -> None:
        """Test validation fails for too short transcript."""
        input_data = TranscriptInput(transcript="Too short")
        errors = parser.validate(input_data)
        assert len(errors) == 1
        assert "too short" in errors[0].lower()

    def test_parse_basic_transcript(self, parser: TranscriptParser) -> None:
        """Test parsing a basic transcript."""
        input_data = TranscriptInput(
            transcript="""
            PM: We need to implement a new checkout feature.
            Dev: What functionality should it have?
            PM: Users must be able to pay with credit cards.
            Dev: Agreed, we will do that.
            """,
            meeting_title="Sprint Planning",
        )
        result = parser.parse(input_data)

        assert result.input_type == InputType.TRANSCRIPT
        assert "Sprint Planning" in result.title
        assert result.description  # Should have extracted something
        assert result.metadata["meeting_title"] == "Sprint Planning"

    def test_parse_identifies_speakers(self, parser: TranscriptParser) -> None:
        """Test that speakers are identified."""
        input_data = TranscriptInput(
            transcript="""
            John: We need this feature.
            Sarah: I agree.
            Mike: Let's plan it out.
            """,
        )
        result = parser.parse(input_data)

        speakers = result.metadata.get("speakers_identified", [])
        assert "John" in speakers
        assert "Sarah" in speakers
        assert "Mike" in speakers

    def test_parse_extracts_requirements(self, parser: TranscriptParser) -> None:
        """Test that requirement statements are extracted."""
        input_data = TranscriptInput(
            transcript="""
            PM: The system should allow users to checkout.
            PM: Users must be able to save their cart.
            Dev: We need error handling for payment failures.
            """,
        )
        result = parser.parse(input_data)

        # Should have extracted requirement statements
        assert result.metadata["requirement_statements_count"] >= 3

    def test_parse_extracts_decisions(self, parser: TranscriptParser) -> None:
        """Test that decisions become acceptance criteria."""
        input_data = TranscriptInput(
            transcript="""
            PM: We need a cart feature.
            Team: We agreed to implement guest checkout.
            Lead: We decided to use Stripe for payments.
            """,
        )
        result = parser.parse(input_data)

        # Decisions should become ACs
        assert len(result.acceptance_criteria) >= 1

    def test_parse_with_meeting_metadata(self, parser: TranscriptParser) -> None:
        """Test parsing with full meeting metadata."""
        input_data = TranscriptInput(
            transcript="PM: We need this feature to be done by next sprint.",
            meeting_title="Feature Planning Meeting",
            meeting_date="2025-01-15",
            participants=["PM", "Dev", "QA"],
        )
        result = parser.parse(input_data)

        assert "Feature Planning Meeting" in result.context
        assert "2025-01-15" in result.context
        assert result.metadata["participants"] == ["PM", "Dev", "QA"]

    def test_parse_different_speaker_formats(self, parser: TranscriptParser) -> None:
        """Test parsing different speaker format patterns."""
        input_data = TranscriptInput(
            transcript="""
            [Alice]: We need this feature.
            Bob: I can implement it.
            (Charlie) Let me help with that.
            Dave> Sure thing.
            """,
        )
        result = parser.parse(input_data)

        speakers = result.metadata.get("speakers_identified", [])
        assert len(speakers) >= 3  # Should identify at least Alice, Bob, Charlie

    def test_requirement_density(self, parser: TranscriptParser) -> None:
        """Test requirement density calculation."""
        # High density transcript
        high_density = TranscriptInput(
            transcript="""
            PM: We need feature A.
            PM: Users must have feature B.
            PM: The system should do C.
            PM: We require functionality D.
            """,
        )
        high_score = parser.get_requirement_density(high_density)

        # Low density transcript
        low_density = TranscriptInput(
            transcript="""
            PM: How are you today?
            Dev: I'm good, thanks.
            PM: Great weather.
            Dev: Indeed.
            """,
        )
        low_score = parser.get_requirement_density(low_density)

        assert high_score > low_score


class TestParsedInput:
    """Tests for ParsedInput model."""

    def test_to_dict(self) -> None:
        """Test converting ParsedInput to dictionary."""
        parsed = ParsedInput(
            input_type=InputType.JIRA,
            title="Test Feature",
            description="Feature description",
            acceptance_criteria=["AC1", "AC2"],
            context="Test context",
            metadata={"key": "value"},
        )
        result = parsed.to_dict()

        assert result["input_type"] == "jira"
        assert result["title"] == "Test Feature"
        assert result["description"] == "Feature description"
        assert len(result["acceptance_criteria"]) == 2
        assert result["context"] == "Test context"
        assert result["metadata"]["key"] == "value"

    def test_default_values(self) -> None:
        """Test ParsedInput with default values."""
        parsed = ParsedInput(
            input_type=InputType.FREE_FORM,
            title="Title",
            description="Description",
            acceptance_criteria=[],
        )

        assert parsed.context == ""
        assert parsed.metadata == {}
