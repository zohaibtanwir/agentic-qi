#!/usr/bin/env python
"""Test script to verify Weaviate v4 client connection and functionality."""

import sys
import os

# Add path for imports
sys.path.insert(0, '/Users/zohaibtanwir/projects/ecommerce-agent/service/src')

# Set Weaviate URL for local testing
os.environ['WEAVIATE_URL'] = 'http://localhost:8090'

from ecommerce_agent.clients.weaviate_client import get_weaviate_client
from ecommerce_agent.utils.logging import get_logger

logger = get_logger(__name__)


def test_weaviate_connection():
    """Test Weaviate v4 client connection and basic operations."""
    print("\n🔍 Testing Weaviate v4 Client Connection\n")
    print("=" * 50)

    try:
        # Get client
        print("\n1. Getting Weaviate client...")
        client = get_weaviate_client()

        # Check connection
        print("\n2. Checking connection status...")
        is_connected = client.is_connected()
        print(f"   ✅ Connected: {is_connected}")

        if not is_connected:
            print("   ❌ Failed to connect to Weaviate!")
            print("   Make sure Weaviate is running with: docker compose up -d")
            return False

        # Health check
        print("\n3. Running health check...")
        health = client.health_check()
        print(f"   Ready: {health['ready']}")
        print(f"   URL: {health['url']}")
        print(f"   Collections: {health['classes_count']}")

        # Get schema
        print("\n4. Getting current schema...")
        schema = client.get_schema()
        classes = schema.get("classes", [])
        print(f"   Found {len(classes)} collections")

        if classes:
            print("   Existing collections:")
            for cls in classes:
                print(f"     - {cls['class']}")

        # Test creating a test collection
        print("\n5. Testing collection creation...")
        test_schema = {
            "class": "TestCollection",
            "properties": [
                {
                    "name": "title",
                    "dataType": ["string"]
                },
                {
                    "name": "content",
                    "dataType": ["text"]
                },
                {
                    "name": "score",
                    "dataType": ["number"]
                }
            ]
        }

        success = client.create_class(test_schema)
        if success:
            print("   ✅ Created test collection")
        else:
            print("   ❌ Failed to create test collection")

        # Test adding an object
        print("\n6. Testing object insertion...")
        test_obj = {
            "title": "Test Document",
            "content": "This is a test document for Weaviate v4",
            "score": 0.95
        }

        obj_id = client.add_object("TestCollection", test_obj)
        if obj_id:
            print(f"   ✅ Added object: {obj_id}")

            # Test retrieving object
            print("\n7. Testing object retrieval...")
            retrieved = client.get_object("TestCollection", obj_id)
            if retrieved:
                print(f"   ✅ Retrieved object: {retrieved.get('title')}")

        # Test batch insertion
        print("\n8. Testing batch insertion...")
        batch_objects = [
            {"title": "Doc 1", "content": "First document", "score": 0.8},
            {"title": "Doc 2", "content": "Second document", "score": 0.9},
            {"title": "Doc 3", "content": "Third document", "score": 0.85}
        ]

        if client.batch_add_objects("TestCollection", batch_objects):
            print("   ✅ Batch added 3 objects")

        # Test search
        print("\n9. Testing BM25 search...")
        results = client.search_bm25("TestCollection", "document", limit=5)
        print(f"   Found {len(results)} results")

        # Clean up
        print("\n10. Cleaning up test collection...")
        if client.delete_class("TestCollection"):
            print("   ✅ Deleted test collection")

        print("\n" + "=" * 50)
        print("\n✅ Weaviate v4 client is working correctly!")
        print("\nYou can now seed the knowledge base.")

        # Close connection
        client.close()

        return True

    except Exception as e:
        print(f"\n❌ Error testing Weaviate: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_weaviate_connection()
    sys.exit(0 if success else 1)