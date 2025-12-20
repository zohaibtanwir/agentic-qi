#!/usr/bin/env python
"""Simple test to check Weaviate v4 connection."""

import weaviate
from weaviate import WeaviateClient

# Try direct connection with v4 API
print("Testing Weaviate v4 connection...")

try:
    # Connect to local Weaviate
    client = weaviate.connect_to_local(
        host="localhost",
        port=8090,
        grpc_port=50051,
    )

    print(f"Connected: {client.is_ready()}")

    # Try to get collections
    collections = client.collections.list_all()
    print(f"Collections: {list(collections.keys())}")

    # Create a test collection
    from weaviate.classes import config

    client.collections.create(
        name="TestCollection",
        properties=[
            config.Property(
                name="title",
                data_type=config.DataType.TEXT,
            ),
            config.Property(
                name="content",
                data_type=config.DataType.TEXT,
            )
        ]
    )
    print("Created TestCollection")

    # Add a test object
    collection = client.collections.get("TestCollection")
    uuid = collection.data.insert(
        properties={
            "title": "Test Document",
            "content": "This is a test"
        }
    )
    print(f"Added object: {uuid}")

    # Query the collection
    response = collection.query.bm25(
        query="test",
        limit=5
    )
    print(f"Found {len(response.objects)} objects")

    # Clean up
    client.collections.delete("TestCollection")
    print("Deleted TestCollection")

    # Close connection
    client.close()
    print("\n✅ Weaviate v4 is working!")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()