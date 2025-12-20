import asyncio
import signal
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn

from ecommerce_agent.config import get_settings
from ecommerce_agent.server.grpc_server import create_server
from ecommerce_agent.server.health import create_health_app
from ecommerce_agent.utils.logging import setup_logging, get_logger

logger = get_logger(__name__)


async def run_grpc_server(port: int) -> None:
    """Run the gRPC server."""
    server = await create_server(port)
    await server.start()
    logger.info("gRPC server started", port=port)

    # Wait for termination
    await server.wait_for_termination()


async def run_http_server(port: int) -> None:
    """Run the HTTP server for health endpoints."""
    app = create_health_app()
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=port,
        log_level="warning",
    )
    server = uvicorn.Server(config)
    await server.serve()


async def main() -> None:
    """Main entry point."""
    setup_logging()
    settings = get_settings()

    logger.info(
        "Starting eCommerce Domain Agent",
        service=settings.service_name,
        grpc_port=settings.grpc_port,
        http_port=settings.http_port,
    )

    # Handle shutdown signals
    shutdown_event = asyncio.Event()

    def handle_shutdown(sig: signal.Signals) -> None:
        logger.info("Received shutdown signal", signal=sig.name)
        shutdown_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, handle_shutdown, sig)

    # Run servers concurrently
    try:
        await asyncio.gather(
            run_grpc_server(settings.grpc_port),
            run_http_server(settings.http_port),
        )
    except asyncio.CancelledError:
        logger.info("Servers cancelled")

    logger.info("eCommerce Domain Agent stopped")


if __name__ == "__main__":
    asyncio.run(main())