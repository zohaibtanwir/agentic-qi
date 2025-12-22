'use client';

import { useState, useCallback } from 'react';
import testCasesClient from '@/lib/grpc/testCasesClient';
import {
  TestType,
  type GenerateTestCasesRequest,
  type GenerateTestCasesResponse,
  type TestCase,
  type GenerationMetadata,
  type OutputFormat,
  type CoverageLevel,
} from '@/lib/grpc/generated/test_cases';

export type InputType = 'user_story' | 'api_spec' | 'free_form';

export interface GenerateFormData {
  inputType: InputType;
  // User Story fields
  story?: string;
  acceptanceCriteria?: string[];
  additionalContext?: string;
  // API Spec fields
  apiSpec?: string;
  specFormat?: 'openapi' | 'graphql';
  endpoints?: string[];
  // Free Form fields
  freeFormText?: string;
  freeFormContext?: Record<string, string>;
  // Generation config
  outputFormat: OutputFormat;
  coverageLevel: CoverageLevel;
  testTypes: TestType[];
  maxTestCases?: number;
  priorityFocus?: string;
  detailLevel?: 'low' | 'medium' | 'high';
}

export interface UseGenerateTestCasesReturn {
  generateTestCases: (formData: GenerateFormData) => Promise<void>;
  loading: boolean;
  error: string | null;
  testCases: TestCase[];
  metadata: GenerationMetadata | null;
  reset: () => void;
}

export function useGenerateTestCases(): UseGenerateTestCasesReturn {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [testCases, setTestCases] = useState<TestCase[]>([]);
  const [metadata, setMetadata] = useState<GenerationMetadata | null>(null);

  const reset = useCallback(() => {
    setError(null);
    setTestCases([]);
    setMetadata(null);
  }, []);

  const generateTestCases = useCallback(async (formData: GenerateFormData) => {
    setLoading(true);
    setError(null);
    setTestCases([]);
    setMetadata(null);

    try {
      // Build proto request
      const request: GenerateTestCasesRequest = {
        requestId: `req-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
        generationConfig: {
          outputFormat: formData.outputFormat,
          coverageLevel: formData.coverageLevel,
          testTypes: formData.testTypes,
          llmProvider: 'anthropic',
          checkDuplicates: false,
          maxTestCases: formData.maxTestCases || 10,
          priorityFocus: formData.priorityFocus || '',
          count: formData.maxTestCases || 10,
          includeEdgeCases: formData.testTypes.includes(TestType.EDGE_CASE),
          includeNegativeTests: formData.testTypes.includes(TestType.NEGATIVE),
          detailLevel: formData.detailLevel || 'medium',
        },
        domainConfig: undefined,
        testDataConfig: undefined,
      };

      // Set input based on type
      if (formData.inputType === 'user_story') {
        request.userStory = {
          story: formData.story || '',
          acceptanceCriteria: formData.acceptanceCriteria?.filter(ac => ac.trim()) || [],
          additionalContext: formData.additionalContext || '',
        };
      } else if (formData.inputType === 'api_spec') {
        request.apiSpec = {
          spec: formData.apiSpec || '',
          specFormat: formData.specFormat || 'openapi',
          endpoints: formData.endpoints?.filter(ep => ep.trim()) || [],
        };
      } else if (formData.inputType === 'free_form') {
        request.freeForm = {
          requirement: formData.freeFormText || '',
          context: formData.freeFormContext || {},
        };
      }

      // Call gRPC-Web service
      const response: GenerateTestCasesResponse = await testCasesClient.generateTestCases(request);

      if (!response.success && response.errorMessage) {
        throw new Error(response.errorMessage);
      }

      setTestCases(response.testCases || []);
      setMetadata(response.metadata || null);
    } catch (err: unknown) {
      console.error('Generation Error:', err);

      let errorMessage = 'Failed to generate test cases';

      if (err instanceof Error) {
        // Handle specific error types
        if (err.message.includes('UNAVAILABLE') || err.message.includes('fetch')) {
          errorMessage = 'Service unavailable. Please ensure the Test Cases Agent and Envoy proxy are running.';
        } else if (err.message.includes('DEADLINE_EXCEEDED') || err.message.includes('timeout')) {
          errorMessage = 'Request timed out. Test case generation may take up to 60 seconds.';
        } else if (err.message.includes('INVALID_ARGUMENT')) {
          errorMessage = 'Invalid input. Please check your form data.';
        } else {
          errorMessage = err.message;
        }
      }

      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    generateTestCases,
    loading,
    error,
    testCases,
    metadata,
    reset,
  };
}

export default useGenerateTestCases;
