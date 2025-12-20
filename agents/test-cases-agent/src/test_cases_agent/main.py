"""Main entry point for Test Cases Agent."""

import asyncio
import signal
import sys
from concurrent import futures
from typing import Optional

import grpc
from grpc_health.v1 import health, health_pb2, health_pb2_grpc
from grpc_reflection.v1alpha import reflection

from test_cases_agent.config import get_settings
from test_cases_agent.utils.logging import get_logger, setup_logging


class TestCasesAgent:
    """Test Cases Agent application."""

    def __init__(self) -> None:
        """Initialize the agent."""
        self.settings = get_settings()
        setup_logging()
        self.logger = get_logger(__name__)
        self.server: Optional[grpc.aio.Server] = None
        self.health_servicer: Optional[health.HealthServicer] = None

    async def start_grpc_server(self) -> None:
        """Start the gRPC server."""
        self.logger.info(
            "Starting gRPC server",
            port=self.settings.grpc_port,
            max_workers=self.settings.max_workers,
        )

        # Create gRPC server
        self.server = grpc.aio.server(
            futures.ThreadPoolExecutor(max_workers=self.settings.max_workers),
            options=[
                ("grpc.max_send_message_length", -1),
                ("grpc.max_receive_message_length", -1),
                ("grpc.max_concurrent_rpcs", self.settings.max_concurrent_requests),
            ],
        )

        # Add health check service
        self.health_servicer = health.HealthServicer()
        health_pb2_grpc.add_HealthServicer_to_server(
            self.health_servicer, self.server
        )

        # Set service status to SERVING
        self.health_servicer.set(
            "test_cases.TestCasesService",
            health_pb2.HealthCheckResponse.SERVING,
        )

        # Add reflection for debugging
        service_names = [
            "test_cases.TestCasesService",
            health_pb2.DESCRIPTOR.services_by_name["Health"].full_name,
            reflection.SERVICE_NAME,
        ]
        reflection.enable_server_reflection(service_names, self.server)

        # Add TestCasesService implementation
        from test_cases_agent.server.service import TestCasesService
        from test_cases_agent.proto import test_cases_pb2_grpc

        test_cases_pb2_grpc.add_TestCasesServiceServicer_to_server(
            TestCasesService(), self.server
        )

        # Bind to port
        address = f"[::]:{self.settings.grpc_port}"
        self.server.add_insecure_port(address)

        # Start server
        await self.server.start()
        self.logger.info(
            "gRPC server started",
            address=address,
            services=service_names,
        )

        # Wait for termination
        await self.server.wait_for_termination()

    async def start_http_health_server(self) -> None:
        """Start HTTP health check endpoint."""
        from aiohttp import web

        async def health_check(request: web.Request) -> web.Response:
            """Health check handler."""
            return web.json_response(
                {
                    "status": "healthy",
                    "service": self.settings.service_name,
                    "environment": self.settings.environment.value,
                    "grpc_port": self.settings.grpc_port,
                }
            )

        app = web.Application()
        app.router.add_get("/health", health_check)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", self.settings.http_port)
        await site.start()

        self.logger.info(
            "HTTP health server started",
            port=self.settings.http_port,
            endpoint="/health",
        )

    async def shutdown(self) -> None:
        """Gracefully shutdown the server."""
        self.logger.info("Shutting down server...")

        if self.health_servicer:
            # Mark service as NOT_SERVING
            self.health_servicer.set(
                "test_cases.TestCasesService",
                health_pb2.HealthCheckResponse.NOT_SERVING,
            )

        if self.server:
            # Grace period for ongoing requests
            await self.server.stop(grace=5)

        self.logger.info("Server shutdown complete")

    async def run(self) -> None:
        """Run the agent."""
        try:
            # Start both servers concurrently
            await asyncio.gather(
                self.start_grpc_server(),
                self.start_http_health_server(),
            )
        except Exception as e:
            self.logger.error("Server error", error=str(e))
            raise
        finally:
            await self.shutdown()


def handle_signal(agent: TestCasesAgent, sig: signal.Signals) -> None:
    """Handle shutdown signals."""
    agent.logger.info(f"Received signal {sig.name}, initiating shutdown...")
    asyncio.create_task(agent.shutdown())


def main() -> None:
    """Main entry point."""
    # Print startup banner
    print("=" * 60)
    print("  Test Cases Agent - v1.0.0")
    print("  Generates comprehensive test case specifications")
    print("=" * 60)

    # Create and run agent
    agent = TestCasesAgent()

    # Setup signal handlers
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, lambda s, f: handle_signal(agent, s))

    # Run the agent
    try:
        asyncio.run(agent.run())
    except KeyboardInterrupt:
        agent.logger.info("Received keyboard interrupt")
    except Exception as e:
        agent.logger.error("Fatal error", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()