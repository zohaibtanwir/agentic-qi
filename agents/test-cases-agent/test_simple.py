#!/usr/bin/env python
"""Simple test without enums."""

import sys
sys.path.insert(0, 'src')

import grpc
import asyncio
from test_cases_agent.proto import test_cases_pb2, test_cases_pb2_grpc


async def test_simple():
    """Simple test without problematic enums."""
    async with grpc.aio.insecure_channel('localhost:9003') as channel:
        stub = test_cases_pb2_grpc.TestCasesServiceStub(channel)

        # Create a minimal test request
        print("Testing GenerateTestCases with minimal request...")
        request = test_cases_pb2.GenerateTestCasesRequest(
            request_id="simple_test",
            free_form=test_cases_pb2.FreeFormInput(
                requirement="Create a simple test for user login",
                context={"entity_type": "user"}
            ),
            generation_config=test_cases_pb2.GenerationConfig(
                count=1,
                detail_level="low"
            )
        )

        try:
            print("Sending request...")
            response = await stub.GenerateTestCases(request)
            print(f"\nResponse received!")
            print(f"Success: {response.success}")
            print(f"Request ID: {response.request_id}")

            if response.success:
                print(f"Generated {len(response.test_cases)} test case(s)")

                if response.test_cases:
                    tc = response.test_cases[0]
                    print(f"\nTest Case:")
                    print(f"  ID: {tc.id}")
                    print(f"  Title: {tc.title}")
                    print(f"  Description: {tc.description}")
                    print(f"  Steps: {len(tc.steps)}")
            else:
                print(f"Error: {response.error_message}")

        except grpc.RpcError as e:
            print(f"\nRPC Error: {e.code()}")
            print(f"Details: {e.details()}")
        except Exception as e:
            print(f"\nUnexpected error: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("Test Cases Agent - Simple Test")
    print("=" * 60)
    print()
    asyncio.run(test_simple())