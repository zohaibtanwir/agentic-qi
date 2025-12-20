#!/usr/bin/env python
"""Quick test to verify the server can be imported and initialized."""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_server():
    """Test server initialization."""
    try:
        from ecommerce_agent.config import get_settings
        from ecommerce_agent.server.grpc_server import EcommerceDomainServicer
        from ecommerce_agent.server.health import create_health_app
        from ecommerce_agent.utils.logging import setup_logging

        # Test logging setup
        setup_logging()
        print("✓ Logging configured successfully")

        # Test settings
        settings = get_settings()
        print(f"✓ Settings loaded: {settings.service_name}")

        # Test gRPC server creation
        servicer = EcommerceDomainServicer()
        print("✓ gRPC servicer created successfully")

        # Test health app creation
        app = create_health_app()
        print("✓ Health app created successfully")

        # Test domain models
        from ecommerce_agent.domain.entities import get_entity
        cart = get_entity("cart")
        print(f"✓ Domain model loaded: {cart.name if cart else 'None'}")

        print("\n✅ All components initialized successfully!")
        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_server())
    sys.exit(0 if success else 1)