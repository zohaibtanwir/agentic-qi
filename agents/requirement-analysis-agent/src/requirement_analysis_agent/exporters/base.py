"""Base exporter class for analysis results."""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Optional

from requirement_analysis_agent.models import AnalysisResult, ExportConfig
from requirement_analysis_agent.utils.logging import get_logger


logger = get_logger(__name__)


class BaseExporter(ABC):
    """Abstract base class for analysis result exporters."""

    def __init__(self, config: Optional[ExportConfig] = None):
        """Initialize exporter.

        Args:
            config: Export configuration
        """
        self.config = config or ExportConfig()
        self.logger = get_logger(self.__class__.__name__)

    @property
    @abstractmethod
    def format_name(self) -> str:
        """Return the format name (e.g., 'text', 'json')."""
        pass

    @property
    @abstractmethod
    def file_extension(self) -> str:
        """Return the file extension (e.g., '.txt', '.json')."""
        pass

    @abstractmethod
    def export(self, result: AnalysisResult) -> str:
        """Export analysis result to string.

        Args:
            result: Analysis result to export

        Returns:
            Exported content as string
        """
        pass

    def generate_filename(self, result: AnalysisResult) -> str:
        """Generate a filename for the export.

        Args:
            result: Analysis result

        Returns:
            Suggested filename
        """
        # Sanitize title for filename
        title = result.extracted_requirement.title[:50]
        safe_title = "".join(c if c.isalnum() or c in "-_ " else "" for c in title)
        safe_title = safe_title.strip().replace(" ", "_").lower()

        if not safe_title:
            safe_title = "analysis"

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        return f"{safe_title}_{timestamp}{self.file_extension}"

    def _format_grade_emoji(self, grade: str) -> str:
        """Get emoji for grade.

        Args:
            grade: Letter grade (A-F)

        Returns:
            Corresponding emoji
        """
        grade_emojis = {
            "A": "✅",
            "B": "👍",
            "C": "⚠️",
            "D": "⚠️",
            "F": "❌",
        }
        return grade_emojis.get(grade, "❓")

    def _format_severity_emoji(self, severity: str) -> str:
        """Get emoji for severity.

        Args:
            severity: Severity level

        Returns:
            Corresponding emoji
        """
        severity_emojis = {
            "high": "🔴",
            "medium": "🟡",
            "low": "🟢",
        }
        return severity_emojis.get(severity, "⚪")
