#!/usr/bin/env python
"""Test client for Test Cases Agent."""

import sys
sys.path.insert(0, 'src')

import grpc
import asyncio
from test_cases_agent.proto import test_cases_pb2, test_cases_pb2_grpc


async def test_health_check():
    """Test the HealthCheck method."""
    async with grpc.aio.insecure_channel('localhost:9003') as channel:
        stub = test_cases_pb2_grpc.TestCasesServiceStub(channel)

        # Test HealthCheck
        print("Testing HealthCheck...")
        request = test_cases_pb2.HealthCheckRequest()
        response = await stub.HealthCheck(request)
        print(f"Health Status: {response.status}")
        print(f"Version: {response.version}")
        print()


async def test_generate_test_cases():
    """Test the GenerateTestCases method."""
    async with grpc.aio.insecure_channel('localhost:9003') as channel:
        stub = test_cases_pb2_grpc.TestCasesServiceStub(channel)

        # Create a test request
        print("Testing GenerateTestCases...")
        request = test_cases_pb2.GenerateTestCasesRequest(
            request_id="test_123",
            free_form=test_cases_pb2.FreeFormRequirement(
                requirement_text="Test user login functionality with email and password",
                context_info={
                    "entity_type": "user",
                    "workflow": "authentication"
                }
            ),
            generation_config=test_cases_pb2.GenerationConfig(
                test_types=[test_cases_pb2.TestType.FUNCTIONAL],
                count=2,
                include_edge_cases=True,
                include_negative_tests=True,
                detail_level="medium"
            )
        )

        try:
            response = await stub.GenerateTestCases(request)
            print(f"Success: {response.success}")
            print(f"Request ID: {response.request_id}")
            print(f"Generated {len(response.test_cases)} test cases:")

            for i, tc in enumerate(response.test_cases, 1):
                print(f"\n  Test Case {i}:")
                print(f"    ID: {tc.id}")
                print(f"    Title: {tc.title}")
                print(f"    Description: {tc.description}")
                print(f"    Type: {tc.test_type}")
                print(f"    Priority: {tc.priority}")
                print(f"    Steps: {len(tc.steps)}")
                for j, step in enumerate(tc.steps, 1):
                    print(f"      Step {j}: {step.action}")
                    print(f"        Expected: {step.expected_result}")

            if response.metadata:
                print(f"\nGeneration Metadata:")
                print(f"  Time: {response.metadata.generation_time_ms}ms")
                print(f"  Provider: {response.metadata.llm_provider}")
        except grpc.RpcError as e:
            print(f"Error: {e.code()}: {e.details()}")


async def main():
    """Run tests."""
    print("=" * 60)
    print("Test Cases Agent - Client Test")
    print("=" * 60)
    print()

    # Test health check
    await test_health_check()

    # Test generation
    await test_generate_test_cases()


if __name__ == "__main__":
    asyncio.run(main())