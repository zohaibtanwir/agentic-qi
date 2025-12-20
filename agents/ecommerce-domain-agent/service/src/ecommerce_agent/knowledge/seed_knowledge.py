#!/usr/bin/env python
"""Script to seed domain knowledge into Weaviate."""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ecommerce_agent.knowledge.indexer import get_indexer
from ecommerce_agent.clients.weaviate_client import get_weaviate_client
from ecommerce_agent.utils.logging import setup_logging, get_logger

logger = get_logger(__name__)


def seed_knowledge(force_recreate: bool = False):
    """
    Seed all domain knowledge into Weaviate.

    Args:
        force_recreate: If True, recreate collections (deletes existing data)
    """
    setup_logging()
    logger.info("Starting knowledge seeding", force_recreate=force_recreate)

    # Check Weaviate connection
    client = get_weaviate_client()
    health = client.health_check()

    if not health.get("ready"):
        logger.error("Weaviate is not ready", health=health)
        return False

    logger.info("Weaviate connection established", url=health.get("url"))

    # Initialize indexer and seed data
    indexer = get_indexer()
    results = indexer.index_all(force_recreate=force_recreate)

    # Print results
    total = sum(results.values())
    if total > 0:
        logger.info("Successfully seeded knowledge", results=results, total=total)
        print("\n✅ Knowledge Seeding Complete!")
        print(f"   Entities: {results['entities']}")
        print(f"   Workflows: {results['workflows']}")
        print(f"   Business Rules: {results['business_rules']}")
        print(f"   Edge Cases: {results['edge_cases']}")
        print(f"   Total: {total} items")
        return True
    else:
        logger.error("No knowledge was indexed")
        print("\n❌ Knowledge seeding failed - no items indexed")
        return False


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Seed domain knowledge into Weaviate")
    parser.add_argument(
        "--force-recreate",
        action="store_true",
        help="Force recreate collections (deletes existing data)",
    )
    args = parser.parse_args()

    try:
        success = seed_knowledge(force_recreate=args.force_recreate)
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error("Seeding failed", error=str(e))
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()