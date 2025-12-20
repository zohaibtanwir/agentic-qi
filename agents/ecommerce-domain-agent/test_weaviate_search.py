#!/usr/bin/env python
"""Test Weaviate search functionality to verify knowledge base indexing."""

import sys
import os
import json

# Add path for imports
sys.path.insert(0, '/Users/zohaibtanwir/projects/ecommerce-agent/service/src')

# Set Weaviate URL for local testing
os.environ['WEAVIATE_URL'] = 'http://localhost:8090'

from ecommerce_agent.clients.weaviate_client import get_weaviate_client
from ecommerce_agent.utils.logging import get_logger

logger = get_logger(__name__)


def test_weaviate_search():
    """Test various search queries against the indexed knowledge base."""
    print("\n🔍 Testing Weaviate Knowledge Base Search\n")
    print("=" * 50)

    try:
        # Get client
        client = get_weaviate_client()

        # Check connection
        print("\n1. Checking connection...")
        if not client.is_connected():
            print("   ❌ Not connected to Weaviate")
            return False
        print("   ✅ Connected to Weaviate")

        # Get schema to see what's indexed
        print("\n2. Checking indexed collections...")
        schema = client.get_schema()
        collections = schema.get("classes", [])
        print(f"   Found {len(collections)} collections:")
        for col in collections:
            print(f"     - {col['class']}")

        # Test BM25 search on business rules
        print("\n3. Testing BM25 search on Business Rules...")
        print("   Query: 'minimum order value cart'")
        results = client.search_bm25(
            class_name="EcommerceRule",
            query="minimum order value cart",
            limit=5
        )
        print(f"   Found {len(results)} results")
        if results:
            for i, result in enumerate(results[:3], 1):
                print(f"\n   Result {i}:")
                print(f"     Rule: {result.get('rule_id', 'N/A')} - {result.get('name', 'N/A')}")
                print(f"     Description: {result.get('description', 'N/A')[:100]}...")

        # Test search on edge cases
        print("\n4. Testing BM25 search on Edge Cases...")
        print("   Query: 'concurrent cart payment'")
        results = client.search_bm25(
            class_name="EcommerceEdgeCase",
            query="concurrent cart payment",
            limit=5
        )
        print(f"   Found {len(results)} results")
        if results:
            for i, result in enumerate(results[:3], 1):
                print(f"\n   Result {i}:")
                print(f"     Case: {result.get('edge_case_id', 'N/A')} - {result.get('name', 'N/A')}")
                print(f"     Description: {result.get('description', 'N/A')[:100]}...")

        # Try semantic search (near_text)
        print("\n5. Testing semantic search...")
        print("   Query: 'product inventory stock management'")
        try:
            results = client.search_similar(
                class_name="EcommerceEntity",
                query="product inventory stock management",
                limit=5
            )
            print(f"   Found {len(results)} results")
            if results:
                for i, result in enumerate(results[:3], 1):
                    print(f"\n   Result {i}:")
                    print(f"     Entity: {result.get('entity_name', 'N/A')}")
                    print(f"     Description: {result.get('description', 'N/A')[:100]}...")
        except Exception as e:
            print(f"   ⚠️  Semantic search failed: {str(e)}")
            print("   Note: Semantic search requires text vectorization module")

        # Check actual object counts
        print("\n6. Checking object counts per collection...")
        for col_name in ["EcommerceRule", "EcommerceEdgeCase", "EcommerceEntity", "EcommerceWorkflow"]:
            try:
                # Get all objects to count
                results = client.search_bm25(
                    class_name=col_name,
                    query="*",  # Match all
                    limit=100
                )
                print(f"   {col_name}: {len(results)} objects")
            except Exception as e:
                print(f"   {col_name}: Error counting - {str(e)}")

        # Test a specific known rule
        print("\n7. Testing specific business rule search...")
        print("   Query: 'BR001'")
        results = client.search_bm25(
            class_name="EcommerceRule",
            query="BR001",
            limit=1
        )
        if results:
            result = results[0]
            print(f"   ✅ Found: {result.get('rule_id')} - {result.get('name')}")
            print(f"   Description: {result.get('description')}")
            print(f"   Constraint: {result.get('constraint')}")
        else:
            print("   ❌ BR001 not found!")

        # Close connection
        client.close()

        print("\n" + "=" * 50)
        print("\n✅ Search test completed!")

        return True

    except Exception as e:
        print(f"\n❌ Error testing search: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_weaviate_search()
    sys.exit(0 if success else 1)