'use client';

import { useRequirementAnalysisStore, type RequirementAnalysisStore } from '@/lib/stores/requirement-analysis-store';

function GradeIcon({ grade }: { grade: string }) {
  // Macy's-themed grade colors with high contrast
  const colors: Record<string, string> = {
    A: 'bg-green-600 text-white border-green-700',
    B: 'bg-blue-600 text-white border-blue-700',
    C: 'bg-amber-500 text-white border-amber-600',
    D: 'bg-orange-500 text-white border-orange-600',
    F: 'bg-red-600 text-white border-red-700',
  };
  return (
    <span className={`inline-flex items-center justify-center w-8 h-8 rounded-lg border text-lg font-bold ${colors[grade] || colors.C}`}>
      {grade}
    </span>
  );
}

function SeverityBadge({ severity }: { severity: string }) {
  const colors: Record<string, string> = {
    high: 'bg-red-100 text-red-700',
    medium: 'bg-yellow-100 text-yellow-700',
    low: 'bg-green-100 text-green-700',
  };
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${colors[severity] || colors.medium}`}>
      {severity}
    </span>
  );
}

function ScoreLegend() {
  const grades = [
    { grade: 'A', range: '90-100', label: 'Excellent', color: 'bg-green-600' },
    { grade: 'B', range: '80-89', label: 'Good', color: 'bg-blue-600' },
    { grade: 'C', range: '70-79', label: 'Fair', color: 'bg-amber-500' },
    { grade: 'D', range: '60-69', label: 'Needs Work', color: 'bg-orange-500' },
    { grade: 'F', range: '0-59', label: 'Poor', color: 'bg-red-600' },
  ];

  return (
    <div className="flex items-center gap-4 text-xs">
      <span className="text-[var(--text-muted)] font-medium">Score Legend:</span>
      {grades.map(({ grade, range, color }) => (
        <div key={grade} className="flex items-center gap-1.5">
          <span className={`w-5 h-5 ${color} text-white rounded flex items-center justify-center font-bold text-[10px]`}>
            {grade}
          </span>
          <span className="text-[var(--text-muted)]">{range}</span>
        </div>
      ))}
    </div>
  );
}

export function AnalysisResults() {
  const analysisResult = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.analysisResult);
  const qualityScore = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.qualityScore);
  const gaps = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.gaps);
  const questions = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.questions);
  const generatedACs = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.generatedACs);
  const extractedRequirement = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.extractedRequirement);
  const clearAnalysis = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.clearAnalysis);
  const answerQuestion = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.answerQuestion);
  const answeredQuestions = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.answeredQuestions);
  const acceptedACs = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.acceptedACs);
  const toggleACAcceptance = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.toggleACAcceptance);
  const reanalyzeRequirement = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.reanalyzeRequirement);
  const isReanalyzing = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.isReanalyzing);
  const exportAnalysis = useRequirementAnalysisStore((state: RequirementAnalysisStore) => state.exportAnalysis);

  if (!analysisResult) return null;

  const handleExport = async (format: 'json' | 'text') => {
    const content = await exportAnalysis(format);
    if (content) {
      const blob = new Blob([content], { type: format === 'json' ? 'application/json' : 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analysis_${Date.now()}.${format === 'json' ? 'json' : 'txt'}`;
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header with Actions */}
      <div className="flex items-center justify-between">
        <button
          onClick={clearAnalysis}
          className="flex items-center gap-2 text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          New Analysis
        </button>
        <div className="flex items-center gap-2">
          <button
            onClick={() => handleExport('json')}
            className="px-3 py-1.5 text-sm border border-[var(--border-default)] rounded-lg hover:bg-[var(--surface-secondary)]"
          >
            Export JSON
          </button>
          <button
            onClick={() => handleExport('text')}
            className="px-3 py-1.5 text-sm border border-[var(--border-default)] rounded-lg hover:bg-[var(--surface-secondary)]"
          >
            Export Text
          </button>
        </div>
      </div>

      {/* Quality Score Card */}
      {qualityScore && (
        <div className="bg-[var(--surface-primary)] rounded-xl border border-[var(--border-default)] p-6">
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-lg font-semibold text-[var(--text-primary)]">Quality Score</h2>
            <div className="flex items-center gap-3">
              <span className="text-3xl font-bold text-[var(--text-primary)]">{qualityScore.overallScore}</span>
              <GradeIcon grade={qualityScore.overallGrade} />
            </div>
          </div>
          <div className="mb-4">
            <ScoreLegend />
          </div>

          {/* Dimension Scores */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            {[
              { label: 'Clarity', data: qualityScore.clarity },
              { label: 'Completeness', data: qualityScore.completeness },
              { label: 'Testability', data: qualityScore.testability },
              { label: 'Consistency', data: qualityScore.consistency },
            ].map((dim) => (
              <div key={dim.label} className="bg-[var(--surface-secondary)] rounded-lg p-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm text-[var(--text-secondary)]">{dim.label}</span>
                  <GradeIcon grade={dim.data?.grade || 'C'} />
                </div>
                <div className="text-xl font-semibold text-[var(--text-primary)]">{dim.data?.score || 0}</div>
                <div className="mt-1 w-full bg-gray-200 rounded-full h-1.5">
                  <div
                    className="bg-red-600 h-1.5 rounded-full"
                    style={{ width: `${dim.data?.score || 0}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          <p className="text-sm text-[var(--text-secondary)] italic">{qualityScore.recommendation}</p>

          {/* Ready Status */}
          <div className="mt-4 pt-4 border-t border-[var(--border-default)]">
            {analysisResult.readyForTestGeneration ? (
              <div className="flex items-center gap-2 text-green-600">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="font-medium">Ready for Test Case Generation</span>
              </div>
            ) : (
              <div className="text-amber-600">
                <div className="flex items-center gap-2 mb-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <span className="font-medium">Blockers to Address</span>
                </div>
                <ul className="list-disc list-inside text-sm space-y-1">
                  {analysisResult.blockers.map((blocker, i) => (
                    <li key={i}>{blocker}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Extracted Structure */}
      {extractedRequirement && (
        <div className="bg-[var(--surface-primary)] rounded-xl border border-[var(--border-default)] p-6">
          <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-4">Extracted Structure</h2>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-[var(--text-muted)]">Actor:</span>
              <span className="ml-2 text-[var(--text-primary)]">{extractedRequirement.structure?.actor || 'N/A'}</span>
            </div>
            <div>
              <span className="text-[var(--text-muted)]">Action:</span>
              <span className="ml-2 text-[var(--text-primary)]">{extractedRequirement.structure?.action || 'N/A'}</span>
            </div>
            <div>
              <span className="text-[var(--text-muted)]">Object:</span>
              <span className="ml-2 text-[var(--text-primary)]">{extractedRequirement.structure?.object || 'N/A'}</span>
            </div>
            <div>
              <span className="text-[var(--text-muted)]">Outcome:</span>
              <span className="ml-2 text-[var(--text-primary)]">{extractedRequirement.structure?.outcome || 'N/A'}</span>
            </div>
          </div>
          {extractedRequirement.structure?.entities && extractedRequirement.structure.entities.length > 0 && (
            <div className="mt-4">
              <span className="text-[var(--text-muted)] text-sm">Domain Entities:</span>
              <div className="flex flex-wrap gap-2 mt-1">
                {extractedRequirement.structure.entities.map((entity, i) => (
                  <span key={i} className="px-2 py-1 bg-red-100 text-red-700 rounded text-xs font-medium">
                    {entity}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Gaps */}
      {gaps.length > 0 && (
        <div className="bg-[var(--surface-primary)] rounded-xl border border-[var(--border-default)] p-6">
          <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-4">
            Detected Gaps ({gaps.length})
          </h2>
          <div className="space-y-3">
            {gaps.map((gap) => (
              <div key={gap.id} className="border border-[var(--border-default)] rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-mono text-[var(--text-muted)]">{gap.id}</span>
                    <SeverityBadge severity={gap.severity} />
                    <span className="text-xs text-[var(--text-muted)]">{gap.category.replace(/_/g, ' ')}</span>
                  </div>
                  <span className="text-xs text-[var(--text-muted)]">{gap.location}</span>
                </div>
                <p className="text-sm text-[var(--text-primary)] mb-2">{gap.description}</p>
                <p className="text-sm text-red-600">
                  <span className="font-medium">Suggestion:</span> {gap.suggestion}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Clarifying Questions */}
      {questions.length > 0 && (
        <div className="bg-[var(--surface-primary)] rounded-xl border border-[var(--border-default)] p-6">
          <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-4">
            Clarifying Questions ({questions.length})
          </h2>
          <div className="space-y-4">
            {questions.map((q) => {
              const answered = answeredQuestions.find(aq => aq.questionId === q.id);
              return (
                <div key={q.id} className="border border-[var(--border-default)] rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-sm font-mono text-[var(--text-muted)]">{q.id}</span>
                    <SeverityBadge severity={q.priority} />
                    <span className="text-xs px-2 py-0.5 bg-gray-100 rounded">{q.category.replace(/_/g, ' ')}</span>
                  </div>
                  <p className="text-sm font-medium text-[var(--text-primary)] mb-2">{q.question}</p>
                  <p className="text-xs text-[var(--text-muted)] mb-3">{q.context}</p>

                  {q.suggestedAnswers.length > 0 && (
                    <div className="mb-3">
                      <span className="text-xs text-[var(--text-muted)]">Suggested answers:</span>
                      <div className="flex flex-wrap gap-2 mt-1">
                        {q.suggestedAnswers.map((ans, i) => (
                          <button
                            key={i}
                            onClick={() => answerQuestion(q.id, ans)}
                            className={`text-xs px-2 py-1 rounded border transition-colors ${
                              answered?.answer === ans
                                ? 'bg-red-100 border-red-300 text-red-700'
                                : 'border-[var(--border-default)] hover:border-red-300'
                            }`}
                          >
                            {ans}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  <input
                    type="text"
                    value={answered?.answer || ''}
                    onChange={(e) => answerQuestion(q.id, e.target.value)}
                    placeholder="Type your answer..."
                    className="w-full px-3 py-2 text-sm border border-[var(--border-default)] rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                  />
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Generated ACs */}
      {generatedACs.length > 0 && (
        <div className="bg-[var(--surface-primary)] rounded-xl border border-[var(--border-default)] p-6">
          <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-4">
            Generated Acceptance Criteria ({generatedACs.length})
          </h2>
          <div className="space-y-3">
            {generatedACs.map((ac) => (
              <div
                key={ac.id}
                className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                  acceptedACs.includes(ac.id)
                    ? 'border-green-300 bg-green-50'
                    : 'border-[var(--border-default)] hover:border-red-300'
                }`}
                onClick={() => toggleACAcceptance(ac.id)}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={acceptedACs.includes(ac.id)}
                      onChange={() => toggleACAcceptance(ac.id)}
                      className="w-4 h-4 text-green-600 rounded border-gray-300"
                      onClick={(e) => e.stopPropagation()}
                    />
                    <span className="text-sm font-mono text-[var(--text-muted)]">{ac.id}</span>
                    <span className="text-xs px-2 py-0.5 bg-red-100 text-red-700 rounded">
                      {ac.source.replace(/_/g, ' ')}
                    </span>
                  </div>
                  <span className="text-xs text-[var(--text-muted)]">
                    {Math.round(ac.confidence * 100)}% confidence
                  </span>
                </div>
                <p className="text-sm text-[var(--text-primary)] mb-2">{ac.text}</p>
                {ac.gherkin && (
                  <details className="mt-2">
                    <summary className="text-xs text-red-600 cursor-pointer">Show Gherkin</summary>
                    <pre className="mt-2 p-2 bg-gray-50 rounded text-xs font-mono whitespace-pre-wrap">
                      {ac.gherkin}
                    </pre>
                  </details>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Reanalyze Button */}
      {(answeredQuestions.length > 0 || acceptedACs.length > 0) && (
        <button
          onClick={reanalyzeRequirement}
          disabled={isReanalyzing}
          className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${
            isReanalyzing
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-red-600 text-white hover:bg-red-700'
          }`}
        >
          {isReanalyzing ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Reanalyzing...
            </span>
          ) : (
            `Reanalyze with ${answeredQuestions.length} answers and ${acceptedACs.length} accepted ACs`
          )}
        </button>
      )}

      {/* Metadata */}
      {analysisResult.metadata && (
        <div className="text-xs text-[var(--text-muted)] flex items-center gap-4">
          <span>Model: {analysisResult.metadata.llmModel}</span>
          <span>Tokens: {analysisResult.metadata.tokensUsed.toLocaleString()}</span>
          <span>Time: {(analysisResult.metadata.analysisTimeMs / 1000).toFixed(3)}s</span>
        </div>
      )}
    </div>
  );
}
