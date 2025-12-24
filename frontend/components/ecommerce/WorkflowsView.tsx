'use client';

import { useEcommerceStore } from '@/lib/stores/ecommerce-store';

export function WorkflowsView() {
  const workflows = useEcommerceStore((state) => state.workflows);
  const selectedWorkflow = useEcommerceStore((state) => state.selectedWorkflow);
  const selectedWorkflowName = useEcommerceStore((state) => state.selectedWorkflowName);
  const selectWorkflow = useEcommerceStore((state) => state.selectWorkflow);
  const clearSelectedWorkflow = useEcommerceStore((state) => state.clearSelectedWorkflow);
  const isLoadingWorkflows = useEcommerceStore((state) => state.isLoadingWorkflows);
  const isLoadingWorkflowDetails = useEcommerceStore((state) => state.isLoadingWorkflowDetails);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Workflow List */}
        <div className="bg-[var(--surface-primary)] border border-[var(--border-default)] rounded-xl overflow-hidden">
          <div className="p-4 border-b border-[var(--border-default)]">
            <h3 className="font-semibold text-[var(--text-primary)]">
              Business Workflows ({workflows.length})
            </h3>
          </div>
          <div className="max-h-[600px] overflow-y-auto">
            {isLoadingWorkflows ? (
              <div className="p-8 text-center text-[var(--text-muted)]">
                Loading workflows...
              </div>
            ) : workflows.length === 0 ? (
              <div className="p-8 text-center text-[var(--text-muted)]">
                No workflows found
              </div>
            ) : (
              <div className="divide-y divide-[var(--border-default)]">
                {workflows.map((workflow) => (
                  <button
                    key={workflow.name}
                    onClick={() => selectWorkflow(workflow.name)}
                    className={`w-full p-4 text-left hover:bg-[var(--surface-secondary)] transition-colors ${
                      selectedWorkflowName === workflow.name ? 'bg-[var(--surface-secondary)]' : ''
                    }`}
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <h4 className="font-medium text-[var(--text-primary)] capitalize">{workflow.name}</h4>
                        <p className="text-sm text-[var(--text-muted)] mt-0.5">{workflow.description}</p>
                        <div className="flex flex-wrap gap-1.5 mt-2">
                          {workflow.involvedEntities.map((entity) => (
                            <span
                              key={entity}
                              className="text-xs px-2 py-0.5 bg-[var(--accent-default)]/10 text-[var(--accent-default)] rounded capitalize"
                            >
                              {entity}
                            </span>
                          ))}
                        </div>
                      </div>
                      <div className="flex-shrink-0">
                        <span className="text-xs px-2 py-1 bg-[var(--surface-tertiary)] rounded text-[var(--text-muted)]">
                          {workflow.stepCount} steps
                        </span>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Workflow Details */}
        <div className="bg-[var(--surface-primary)] border border-[var(--border-default)] rounded-xl overflow-hidden">
          <div className="p-4 border-b border-[var(--border-default)] flex items-center justify-between">
            <h3 className="font-semibold text-[var(--text-primary)]">
              {selectedWorkflow ? (
                <span className="capitalize">{selectedWorkflow.name} Flow</span>
              ) : (
                'Select a Workflow'
              )}
            </h3>
            {selectedWorkflow && (
              <button
                onClick={clearSelectedWorkflow}
                className="text-[var(--text-muted)] hover:text-[var(--text-primary)]"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
          </div>
          <div className="max-h-[600px] overflow-y-auto p-4">
            {isLoadingWorkflowDetails ? (
              <div className="text-center text-[var(--text-muted)] py-8">
                Loading workflow details...
              </div>
            ) : !selectedWorkflow ? (
              <div className="text-center text-[var(--text-muted)] py-8">
                Click on a workflow to view its details
              </div>
            ) : (
              <div className="space-y-6">
                {/* Description */}
                <div>
                  <p className="text-[var(--text-secondary)]">{selectedWorkflow.description}</p>
                </div>

                {/* Involved Entities */}
                <div>
                  <h4 className="text-sm font-semibold text-[var(--text-primary)] mb-2">Involved Entities</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedWorkflow.involvedEntities.map((entity) => (
                      <span
                        key={entity}
                        className="px-3 py-1.5 bg-[var(--accent-default)]/10 text-[var(--accent-default)] rounded-lg text-sm capitalize"
                      >
                        {entity}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Workflow Steps */}
                {selectedWorkflow.steps.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-[var(--text-primary)] mb-3">Workflow Steps</h4>
                    <div className="relative">
                      {/* Vertical Line */}
                      <div className="absolute left-4 top-6 bottom-6 w-0.5 bg-[var(--border-default)]"></div>

                      <div className="space-y-4">
                        {selectedWorkflow.steps.map((step, idx) => (
                          <div key={idx} className="relative pl-10">
                            {/* Step Number Circle */}
                            <div className="absolute left-0 w-8 h-8 bg-[var(--accent-default)] rounded-full flex items-center justify-center text-white text-sm font-bold">
                              {step.order}
                            </div>

                            <div className="p-4 bg-[var(--surface-secondary)] rounded-lg">
                              <div className="flex items-center justify-between mb-2">
                                <h5 className="font-medium text-[var(--text-primary)]">{step.name}</h5>
                                <span className="text-xs px-2 py-0.5 bg-[var(--surface-tertiary)] rounded text-[var(--text-muted)] capitalize">
                                  {step.entity}
                                </span>
                              </div>
                              <p className="text-sm text-[var(--text-muted)] mb-2">{step.description}</p>

                              {step.validations.length > 0 && (
                                <div className="mt-2">
                                  <span className="text-xs text-[var(--text-muted)]">Validations:</span>
                                  <div className="flex flex-wrap gap-1 mt-1">
                                    {step.validations.map((val, vidx) => (
                                      <span key={vidx} className="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 rounded">
                                        {val}
                                      </span>
                                    ))}
                                  </div>
                                </div>
                              )}

                              {step.possibleOutcomes.length > 0 && (
                                <div className="mt-2">
                                  <span className="text-xs text-[var(--text-muted)]">Possible Outcomes:</span>
                                  <div className="flex flex-wrap gap-1 mt-1">
                                    {step.possibleOutcomes.map((outcome, oidx) => (
                                      <span key={oidx} className="text-xs px-2 py-0.5 bg-green-100 text-green-700 rounded">
                                        {outcome}
                                      </span>
                                    ))}
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {/* Business Rules */}
                {selectedWorkflow.rules.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-[var(--text-primary)] mb-3">Business Rules</h4>
                    <div className="space-y-2">
                      {selectedWorkflow.rules.map((rule) => (
                        <div key={rule.id} className="p-3 bg-[var(--surface-secondary)] rounded-lg">
                          <div className="flex items-center justify-between">
                            <span className="font-medium text-[var(--text-primary)]">{rule.name}</span>
                            <span className={`text-xs px-2 py-0.5 rounded ${
                              rule.severity === 'error' ? 'bg-red-100 text-red-700' :
                              rule.severity === 'warning' ? 'bg-yellow-100 text-yellow-700' :
                              'bg-blue-100 text-blue-700'
                            }`}>
                              {rule.severity}
                            </span>
                          </div>
                          <p className="text-sm text-[var(--text-muted)] mt-1">{rule.description}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Edge Cases */}
                {selectedWorkflow.edgeCases.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-[var(--text-primary)] mb-3">Edge Cases</h4>
                    <ul className="space-y-1">
                      {selectedWorkflow.edgeCases.map((edgeCase, idx) => (
                        <li key={idx} className="text-sm text-[var(--text-secondary)] flex items-start gap-2">
                          <svg className="w-4 h-4 text-[var(--accent-default)] mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                          </svg>
                          {edgeCase}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Test Scenarios */}
                {selectedWorkflow.testScenarios.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-[var(--text-primary)] mb-3">Test Scenarios</h4>
                    <ul className="space-y-1">
                      {selectedWorkflow.testScenarios.map((scenario, idx) => (
                        <li key={idx} className="text-sm text-[var(--text-secondary)] flex items-start gap-2">
                          <svg className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          {scenario}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
