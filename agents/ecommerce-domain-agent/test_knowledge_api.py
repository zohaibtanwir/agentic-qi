#!/usr/bin/env python
"""Test the knowledge search API directly."""

import os
import sys

# Add path for imports
sys.path.insert(0, '/Users/zohaibtanwir/projects/ecommerce-agent/service/src')

# Set Weaviate URL for local testing
os.environ['WEAVIATE_URL'] = 'http://localhost:8090'

# Clear any cached settings
import functools
from ecommerce_agent import config
config.get_settings.cache_clear()

import asyncio
import json
from ecommerce_agent.clients.weaviate_client import get_weaviate_client

async def test_search():
    print("\n🔍 Testing Knowledge Search Directly\n")
    print("=" * 50)

    # Get client
    client = get_weaviate_client()

    # Check connection
    print("\n1. Checking connection...")
    connected = client.is_connected()
    print(f"   Connected: {connected}")

    if not connected:
        print("   ❌ Not connected to Weaviate")
        print(f"   URL: {client.settings.weaviate_url}")
        return

    print("   ✅ Connected to Weaviate")

    # Test search
    print("\n2. Searching for 'payment timeout'...")

    try:
        # Search in business rules
        results = client.search_bm25(
            class_name="EcommerceRule",
            query="payment timeout",
            limit=5
        )

        print(f"   Found {len(results)} results in Business Rules")

        if results:
            for i, result in enumerate(results[:3], 1):
                print(f"\n   Result {i}:")
                print(f"     Rule: {result.get('rule_id', 'N/A')} - {result.get('name', 'N/A')}")
                print(f"     Description: {result.get('description', 'N/A')[:100]}...")

        # Search in edge cases
        print("\n3. Searching in Edge Cases...")
        results = client.search_bm25(
            class_name="EcommerceEdgeCase",
            query="payment timeout",
            limit=5
        )

        print(f"   Found {len(results)} results in Edge Cases")

        if results:
            for i, result in enumerate(results[:3], 1):
                print(f"\n   Result {i}:")
                print(f"     Case: {result.get('edge_case_id', 'N/A')} - {result.get('name', 'N/A')}")
                print(f"     Description: {result.get('description', 'N/A')[:100]}...")

        print("\n" + "=" * 50)
        print("\n✅ Search test completed!")

        # Close connection
        client.close()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_search())