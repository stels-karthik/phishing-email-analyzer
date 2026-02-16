export default function AnalysisResults({ analysis }) {
  const getRiskColor = (risk) => {
    const colors = {
      critical: 'bg-red-100 text-red-800 border-red-300',
      high: 'bg-orange-100 text-orange-800 border-orange-300',
      medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      low: 'bg-blue-100 text-blue-800 border-blue-300',
      safe: 'bg-green-100 text-green-800 border-green-300'
    }
    return colors[risk] || colors.medium
  }

  const getRiskIcon = (risk) => {
    if (risk === 'critical' || risk === 'high') {
      return (
        <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
        </svg>
      )
    } else if (risk === 'safe') {
      return (
        <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
        </svg>
      )
    }
    return (
      <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
      </svg>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Analysis Results</h2>

      {/* Overall Risk */}
      <div className={`border-2 rounded-lg p-4 mb-6 ${getRiskColor(analysis.overall_risk)}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {getRiskIcon(analysis.overall_risk)}
            <div>
              <h3 className="font-bold text-lg uppercase">{analysis.overall_risk} RISK</h3>
              <p className="text-sm">Confidence: {(analysis.confidence * 100).toFixed(0)}%</p>
            </div>
          </div>
          <div className="text-sm text-right">
            <div>Analyzed in {analysis.execution_time.toFixed(2)}s</div>
          </div>
        </div>
      </div>

      {/* Summary */}
      <div className="mb-6">
        <h3 className="font-semibold text-gray-900 mb-2">Summary</h3>
        <p className="text-gray-700">{analysis.summary}</p>
      </div>

      {/* Recommendations */}
      <div className="mb-6">
        <h3 className="font-semibold text-gray-900 mb-2">Recommendations</h3>
        <ul className="space-y-2">
          {analysis.recommendations.map((rec, index) => (
            <li key={index} className="flex items-start">
              <svg className="w-5 h-5 text-indigo-600 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span className="text-gray-700">{rec}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Threat Intel Hits */}
      {analysis.threat_intel_hits && analysis.threat_intel_hits.length > 0 && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="font-semibold text-red-900 mb-2 flex items-center">
            <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            Threat Intelligence Alerts
          </h3>
          <ul className="space-y-2">
            {analysis.threat_intel_hits.map((hit, index) => (
              <li key={index} className="text-sm text-red-800">
                <strong>{hit.source}:</strong> {hit.details || 'Malicious content detected'}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Agent Analyses */}
      <div>
        <h3 className="font-semibold text-gray-900 mb-3">Detailed Agent Analyses</h3>
        <div className="space-y-3">
          {analysis.agent_analyses.map((agent, index) => (
            <details key={index} className="border border-gray-200 rounded-lg">
              <summary className="cursor-pointer p-3 hover:bg-gray-50 flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <span className={`px-2 py-1 text-xs font-semibold rounded ${getRiskColor(agent.risk_level)}`}>
                    {agent.agent_type}
                  </span>
                  <span className="text-sm text-gray-600">
                    {agent.findings.length} finding(s)
                  </span>
                </div>
                <span className="text-sm text-gray-500">
                  {(agent.confidence * 100).toFixed(0)}% confidence
                </span>
              </summary>
              <div className="p-4 bg-gray-50 border-t border-gray-200">
                {agent.findings.length > 0 && (
                  <div className="mb-3">
                    <h4 className="text-sm font-semibold text-gray-700 mb-2">Findings:</h4>
                    <ul className="space-y-1">
                      {agent.findings.map((finding, fIndex) => (
                        <li key={fIndex} className="text-sm text-gray-600 flex items-start">
                          <span className={`inline-block w-16 px-2 py-0.5 text-xs rounded mr-2 flex-shrink-0 ${
                            finding.severity === 'high' ? 'bg-red-100 text-red-800' :
                            finding.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-blue-100 text-blue-800'
                          }`}>
                            {finding.severity}
                          </span>
                          {finding.description}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 mb-2">Reasoning:</h4>
                  <p className="text-sm text-gray-600 whitespace-pre-wrap">{agent.reasoning}</p>
                </div>
              </div>
            </details>
          ))}
        </div>
      </div>
    </div>
  )
}
