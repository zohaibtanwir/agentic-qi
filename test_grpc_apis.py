#!/usr/bin/env python3
"""Test gRPC APIs with actual LLM endpoints."""

import asyncio
import grpc
import sys
import os

# Add the protos to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agents/test-data-agent/src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agents/test-cases-agent/src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agents/ecommerce-domain-agent/service/src'))

from test_data_agent.proto import test_data_pb2, test_data_pb2_grpc
from test_cases_agent.proto import test_cases_pb2, test_cases_pb2_grpc
from ecommerce_agent.proto import ecommerce_domain_pb2, ecommerce_domain_pb2_grpc


async def test_test_data_agent():
    """Test Test Data Agent with real LLM call."""
    print("\n" + "="*80)
    print("TESTING: Test Data Agent - Generate Data with LLM")
    print("="*80)

    try:
        async with grpc.aio.insecure_channel('localhost:9091') as channel:
            stub = test_data_pb2_grpc.TestDataServiceStub(channel)

            # Test health check first
            print("\n1. Testing health check...")
            health_request = test_data_pb2.HealthCheckRequest()
            health_response = await stub.HealthCheck(health_request, timeout=5.0)
            print(f"   ✓ Health Status: {health_response.status}")

            # Test data generation with LLM
            print("\n2. Testing data generation with LLM...")
            request = test_data_pb2.GenerateRequest(
                request_id="test-001",
                domain="ecommerce",
                entity="customer",
                count=2,
                context="Generate realistic customer data for testing",
                output_format=test_data_pb2.JSON,  # Use enum instead of string
                hints=["realistic"],
            )

            response = await stub.GenerateData(request, timeout=30.0)

            if response.success:
                print(f"   ✓ Generation successful!")
                print(f"   ✓ Records generated: {response.record_count}")
                print(f"   ✓ Generation path: {response.metadata.generation_path}")
                print(f"   ✓ Tokens used: {response.metadata.llm_tokens_used}")
                print(f"   ✓ Sample data (first 200 chars): {response.data[:200]}...")
                return True
            else:
                print(f"   ✗ Generation failed: {response.error}")
                return False

    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_ecommerce_domain_agent():
    """Test eCommerce Domain Agent."""
    print("\n" + "="*80)
    print("TESTING: eCommerce Domain Agent")
    print("="*80)

    try:
        async with grpc.aio.insecure_channel('localhost:9002') as channel:
            stub = ecommerce_domain_pb2_grpc.EcommerceDomainServiceStub(channel)

            # Test health check
            print("\n1. Testing health check...")
            health_request = ecommerce_domain_pb2.HealthCheckRequest()
            health_response = await stub.HealthCheck(health_request, timeout=5.0)
            print(f"   ✓ Health Status: {health_response.status}")

            # Test get domain context
            print("\n2. Testing get domain context...")
            request = ecommerce_domain_pb2.DomainContextRequest(
                entity="order",
                scenario="checkout",
            )

            response = await stub.GetDomainContext(request, timeout=10.0)
            print(f"   ✓ Got domain context")
            print(f"   ✓ Context length: {len(response.context)} chars")
            print(f"   ✓ Business rules: {len(response.rules)}")
            print(f"   ✓ Edge cases: {len(response.edge_cases)}")
            return True

    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_test_cases_agent():
    """Test Test Cases Agent with real LLM call."""
    print("\n" + "="*80)
    print("TESTING: Test Cases Agent - Generate Test Cases with LLM")
    print("="*80)

    try:
        async with grpc.aio.insecure_channel('localhost:9003') as channel:
            stub = test_cases_pb2_grpc.TestCasesServiceStub(channel)

            # Test health check
            print("\n1. Testing health check...")
            health_request = test_cases_pb2.HealthCheckRequest()
            health_response = await stub.HealthCheck(health_request, timeout=5.0)
            print(f"   ✓ Health Status: {health_response.status}")

            # Test generate test cases
            print("\n2. Testing test case generation with LLM...")
            free_form = test_cases_pb2.FreeFormInput(
                requirement="User should be able to add items to cart and checkout"
            )
            request = test_cases_pb2.GenerateTestCasesRequest(
                request_id="test-tc-001",
                free_form=free_form,
            )

            response = await stub.GenerateTestCases(request, timeout=120.0)

            if response.success:
                print(f"   ✓ Generation successful!")
                print(f"   ✓ Test cases generated: {len(response.test_cases)}")
                for i, tc in enumerate(response.test_cases[:2], 1):
                    print(f"   ✓ Test Case {i}: {tc.title}")
                    print(f"      Type: {test_cases_pb2.TestType.Name(tc.type)}, Priority: {test_cases_pb2.Priority.Name(tc.priority)}")
                return True
            else:
                print(f"   ✗ Generation failed: {response.error_message}")
                return False

    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("gRPC API Tests with Real LLM Endpoints")
    print("="*80)

    results = {}

    # Test each agent
    results['test-data-agent'] = await test_test_data_agent()
    results['ecommerce-domain-agent'] = await test_ecommerce_domain_agent()
    results['test-cases-agent'] = await test_test_cases_agent()

    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    for agent, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{agent:30} {status}")

    print("="*80)

    # Return exit code
    all_passed = all(results.values())
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
