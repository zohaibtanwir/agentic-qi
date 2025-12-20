#!/usr/bin/env python
"""Seed the knowledge base into Weaviate vector database."""

import sys
import os

# Add path for imports
sys.path.insert(0, '/Users/zohaibtanwir/projects/ecommerce-agent/service/src')

# Set Weaviate URL for local testing
os.environ['WEAVIATE_URL'] = 'http://localhost:8090'

from ecommerce_agent.knowledge.indexer import get_indexer
from ecommerce_agent.utils.logging import get_logger

logger = get_logger(__name__)


def seed_knowledge_base():
    """Seed all knowledge documents into Weaviate."""
    print("\n🚀 Seeding Knowledge Base into Weaviate\n")
    print("=" * 50)

    try:
        # Get indexer
        print("\n1. Initializing indexer...")
        indexer = get_indexer()

        # Check connection
        print("\n2. Checking Weaviate connection...")
        stats = indexer.get_stats()
        if stats.get("connected"):
            print(f"   ✅ Connected to Weaviate")
            print(f"   Collections: {stats.get('collections', 0)}")
        else:
            print("   ❌ Failed to connect to Weaviate!")
            print("   Make sure Weaviate is running with: docker compose up -d weaviate")
            return False

        # Initialize collections (recreate if needed)
        print("\n3. Initializing collections...")
        if indexer.initialize_collections(force_recreate=True):
            print("   ✅ Collections initialized")
        else:
            print("   ❌ Failed to initialize collections")
            return False

        # Index all knowledge
        print("\n4. Indexing knowledge documents...")
        results = indexer.index_all(force_recreate=False)

        print("\n📊 Indexing Results:")
        print(f"   Entities: {results['entities']}")
        print(f"   Workflows: {results['workflows']}")
        print(f"   Business Rules: {results['business_rules']}")
        print(f"   Edge Cases: {results['edge_cases']}")
        print(f"   Total: {sum(results.values())}")

        # Verify by getting stats again
        print("\n5. Verifying indexed data...")
        final_stats = indexer.get_stats()
        print(f"   Collections: {final_stats.get('collections', 0)}")
        print(f"   Connection: {final_stats.get('connected', False)}")

        print("\n" + "=" * 50)
        print("\n✅ Knowledge base successfully seeded into Weaviate!")
        print(f"\n📚 Total documents indexed: {sum(results.values())}")
        print("\nThe eCommerce Domain Agent now has access to:")
        print("  - Business rules for validation")
        print("  - Edge cases for robust testing")
        print("  - Test scenarios for comprehensive coverage")
        print("  - Domain entities for context")

        return True

    except Exception as e:
        print(f"\n❌ Error seeding knowledge base: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = seed_knowledge_base()
    sys.exit(0 if success else 1)