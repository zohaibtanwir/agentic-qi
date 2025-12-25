"""gRPC Server entry point for Requirement Analysis Agent."""

import asyncio
import signal
import sys
from concurrent import futures
from typing import Optional

import grpc

from requirement_analysis_agent.clients import DomainAgentClient, TestCasesAgentClient
from requirement_analysis_agent.config import Settings, get_settings
from requirement_analysis_agent.llm.anthropic_client import AnthropicClient
from requirement_analysis_agent.proto import requirement_analysis_pb2_grpc as pb2_grpc
from requirement_analysis_agent.server.servicer import RequirementAnalysisServicer
from requirement_analysis_agent.storage import WeaviateClient
from requirement_analysis_agent.utils.logging import get_logger


logger = get_logger(__name__)


class GRPCServer:
    """gRPC server manager for Requirement Analysis Agent."""

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize server.

        Args:
            settings: Application settings (uses defaults if not provided)
        """
        self.settings = settings or get_settings()
        self.server: Optional[grpc.aio.Server] = None
        self.servicer: Optional[RequirementAnalysisServicer] = None
        self._shutdown_event = asyncio.Event()

    async def start(self) -> None:
        """Start the gRPC server."""
        logger.info(
            "starting_grpc_server",
            port=self.settings.grpc_port,
            environment=self.settings.environment.value,
        )

        # Initialize clients
        llm_client = None
        domain_client = None
        weaviate_client = None

        # Initialize LLM client if API key is available
        if self.settings.has_anthropic:
            llm_client = AnthropicClient(
                api_key=self.settings.anthropic_api_key,
                default_model=self.settings.default_model,
            )
            await llm_client.initialize()
            logger.info("llm_client_initialized", provider="anthropic")

        # Initialize Domain Agent client
        try:
            domain_client = DomainAgentClient(
                host=self.settings.domain_agent_host,
                port=self.settings.domain_agent_port,
                timeout=self.settings.agent_timeout,
            )
            await domain_client.connect()
            logger.info(
                "domain_client_connected",
                address=self.settings.domain_agent_address,
            )
        except Exception as e:
            logger.warning(
                "domain_client_unavailable",
                error=str(e),
                message="Domain validation will be disabled",
            )
            domain_client = None

        # Initialize Weaviate client
        try:
            weaviate_client = WeaviateClient(self.settings)
            await weaviate_client.connect()
            logger.info("weaviate_client_connected", url=self.settings.weaviate_url)
        except Exception as e:
            logger.warning(
                "weaviate_client_unavailable",
                error=str(e),
                message="History storage will be disabled",
            )
            weaviate_client = None

        # Initialize Test Cases Agent client
        test_cases_client = None
        try:
            test_cases_client = TestCasesAgentClient(
                host=self.settings.test_cases_agent_host,
                port=self.settings.test_cases_agent_port,
                timeout=self.settings.agent_timeout,
            )
            await test_cases_client.connect()
            logger.info(
                "test_cases_client_connected",
                address=self.settings.test_cases_agent_address,
            )
        except Exception as e:
            logger.warning(
                "test_cases_client_unavailable",
                error=str(e),
                message="Test case forwarding will be disabled",
            )
            test_cases_client = None

        # Create servicer
        self.servicer = RequirementAnalysisServicer(
            settings=self.settings,
            llm_client=llm_client,
            domain_client=domain_client,
            weaviate_client=weaviate_client,
            test_cases_client=test_cases_client,
        )
        await self.servicer.initialize()

        # Create gRPC server
        self.server = grpc.aio.server(
            futures.ThreadPoolExecutor(max_workers=self.settings.max_workers),
            options=[
                ("grpc.max_send_message_length", 50 * 1024 * 1024),  # 50MB
                ("grpc.max_receive_message_length", 50 * 1024 * 1024),  # 50MB
                ("grpc.keepalive_time_ms", 30000),
                ("grpc.keepalive_timeout_ms", 10000),
                ("grpc.keepalive_permit_without_calls", True),
            ],
        )

        # Add servicer
        pb2_grpc.add_RequirementAnalysisServiceServicer_to_server(
            self.servicer, self.server
        )

        # Bind to port
        listen_addr = f"[::]:{self.settings.grpc_port}"
        self.server.add_insecure_port(listen_addr)

        # Start server
        await self.server.start()
        logger.info(
            "grpc_server_started",
            address=listen_addr,
            service="RequirementAnalysisService",
        )

    async def stop(self) -> None:
        """Stop the gRPC server gracefully."""
        logger.info("stopping_grpc_server")

        if self.server:
            # Give clients time to finish
            await self.server.stop(grace=5.0)
            logger.info("grpc_server_stopped")

        if self.servicer:
            await self.servicer.shutdown()

    async def wait_for_termination(self) -> None:
        """Wait for server termination signal."""
        await self._shutdown_event.wait()

    def request_shutdown(self) -> None:
        """Request server shutdown."""
        self._shutdown_event.set()


async def serve(settings: Optional[Settings] = None) -> None:
    """Run the gRPC server.

    Args:
        settings: Optional application settings
    """
    server = GRPCServer(settings)

    # Setup signal handlers
    loop = asyncio.get_running_loop()

    def signal_handler(sig: signal.Signals) -> None:
        logger.info("shutdown_signal_received", signal=sig.name)
        server.request_shutdown()

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda s=sig: signal_handler(s))

    try:
        await server.start()
        logger.info(
            "server_ready",
            port=server.settings.grpc_port,
            message="Requirement Analysis Agent is ready to accept requests",
        )
        await server.wait_for_termination()
    except Exception as e:
        logger.error("server_error", error=str(e))
        raise
    finally:
        await server.stop()


def main() -> None:
    """Main entry point."""
    logger.info("requirement_analysis_agent_starting")

    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        logger.info("keyboard_interrupt_received")
    except Exception as e:
        logger.error("fatal_error", error=str(e))
        sys.exit(1)

    logger.info("requirement_analysis_agent_stopped")


if __name__ == "__main__":
    main()
