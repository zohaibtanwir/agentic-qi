"""Structured logging configuration using structlog."""

import logging
import sys
from typing import Any, Optional

import structlog
from structlog.contextvars import merge_contextvars

from requirement_analysis_agent.config import LogLevel, get_settings


def setup_logging(log_level: Optional[LogLevel] = None) -> None:
    """
    Configure structured logging for the application.

    Args:
        log_level: Optional log level override
    """
    settings = get_settings()
    level = log_level or settings.log_level

    # Configure Python's logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.value),
    )

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.CallsiteParameterAdder(
                parameters=[
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.LINENO,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                ]
            ),
            structlog.processors.dict_tracebacks,
            structlog.dev.ConsoleRenderer() if settings.environment.value != "production"
            else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: Optional[str] = None) -> Any:
    """
    Get a structured logger instance.

    Args:
        name: Optional logger name

    Returns:
        Structured logger instance
    """
    return structlog.get_logger(name)


def log_context(**kwargs: Any) -> None:
    """
    Add context variables that will be included in all subsequent log messages.

    Args:
        **kwargs: Context variables to add
    """
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(**kwargs)


def log_grpc_request(method: str, request: Any) -> None:
    """
    Log a gRPC request.

    Args:
        method: gRPC method name
        request: Request object
    """
    logger = get_logger("grpc.request")
    logger.info(
        "gRPC request received",
        method=method,
        request_type=type(request).__name__,
    )


def log_grpc_response(method: str, response: Any, duration_ms: float) -> None:
    """
    Log a gRPC response.

    Args:
        method: gRPC method name
        response: Response object
        duration_ms: Request duration in milliseconds
    """
    logger = get_logger("grpc.response")
    logger.info(
        "gRPC response sent",
        method=method,
        response_type=type(response).__name__,
        duration_ms=duration_ms,
    )


def log_grpc_error(method: str, error: Exception, duration_ms: float) -> None:
    """
    Log a gRPC error.

    Args:
        method: gRPC method name
        error: Exception that occurred
        duration_ms: Request duration in milliseconds
    """
    logger = get_logger("grpc.error")
    logger.error(
        "gRPC error occurred",
        method=method,
        error=str(error),
        error_type=type(error).__name__,
        duration_ms=duration_ms,
    )


def log_llm_request(provider: str, model: str, prompt_tokens: int) -> None:
    """
    Log an LLM request.

    Args:
        provider: LLM provider name
        model: Model name
        prompt_tokens: Number of tokens in prompt
    """
    logger = get_logger("llm.request")
    logger.info(
        "LLM request sent",
        provider=provider,
        model=model,
        prompt_tokens=prompt_tokens,
    )


def log_llm_response(
    provider: str, model: str, completion_tokens: int, duration_ms: float
) -> None:
    """
    Log an LLM response.

    Args:
        provider: LLM provider name
        model: Model name
        completion_tokens: Number of tokens in completion
        duration_ms: Request duration in milliseconds
    """
    logger = get_logger("llm.response")
    logger.info(
        "LLM response received",
        provider=provider,
        model=model,
        completion_tokens=completion_tokens,
        duration_ms=duration_ms,
    )


def log_llm_error(provider: str, model: str, error: Exception) -> None:
    """
    Log an LLM error.

    Args:
        provider: LLM provider name
        model: Model name
        error: Exception that occurred
    """
    logger = get_logger("llm.error")
    logger.error(
        "LLM error occurred",
        provider=provider,
        model=model,
        error=str(error),
        error_type=type(error).__name__,
    )


def log_analysis_start(request_id: str, input_type: str) -> None:
    """
    Log the start of a requirement analysis.

    Args:
        request_id: Unique request identifier
        input_type: Type of input (jira, free_form, transcript)
    """
    logger = get_logger("analysis.start")
    logger.info(
        "Requirement analysis started",
        request_id=request_id,
        input_type=input_type,
    )


def log_analysis_complete(
    request_id: str, quality_score: int, gaps_found: int, duration_ms: float
) -> None:
    """
    Log the completion of a requirement analysis.

    Args:
        request_id: Unique request identifier
        quality_score: Overall quality score (0-100)
        gaps_found: Number of gaps detected
        duration_ms: Analysis duration in milliseconds
    """
    logger = get_logger("analysis.complete")
    logger.info(
        "Requirement analysis completed",
        request_id=request_id,
        quality_score=quality_score,
        gaps_found=gaps_found,
        duration_ms=duration_ms,
    )


def log_domain_validation(request_id: str, valid: bool, entities_found: int) -> None:
    """
    Log domain validation results.

    Args:
        request_id: Unique request identifier
        valid: Whether the requirement is valid against domain rules
        entities_found: Number of domain entities found
    """
    logger = get_logger("domain.validation")
    logger.info(
        "Domain validation completed",
        request_id=request_id,
        valid=valid,
        entities_found=entities_found,
    )


__all__ = [
    "setup_logging",
    "get_logger",
    "log_context",
    "log_grpc_request",
    "log_grpc_response",
    "log_grpc_error",
    "log_llm_request",
    "log_llm_response",
    "log_llm_error",
    "log_analysis_start",
    "log_analysis_complete",
    "log_domain_validation",
]
