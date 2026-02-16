import { useState } from 'react'
import axios from 'axios'
import EmailForm from './components/EmailForm'
import AnalysisResults from './components/AnalysisResults'
import Header from './components/Header'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleAnalyze = async (emailData) => {
    setLoading(true)
    setError(null)
    setAnalysis(null)

    try {
      const response = await axios.post(`${API_BASE_URL}/api/v1/analyze`, emailData)
      setAnalysis(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to analyze email. Please try again.')
      console.error('Analysis error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setAnalysis(null)
    setError(null)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Header />

      <main className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Info Banner */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <div className="flex items-start">
            <svg className="w-5 h-5 text-blue-600 mt-0.5 mr-3" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
            <div>
              <h3 className="text-sm font-medium text-blue-900">Multi-Agent AI Analysis</h3>
              <p className="text-sm text-blue-700 mt-1">
                This tool uses specialized AI agents to analyze email headers, content, links, and attachments for phishing indicators.
              </p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Email Input */}
          <div>
            <EmailForm
              onAnalyze={handleAnalyze}
              loading={loading}
              onReset={handleReset}
            />

            {error && (
              <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex">
                  <svg className="w-5 h-5 text-red-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                  <div>
                    <h3 className="text-sm font-medium text-red-900">Error</h3>
                    <p className="text-sm text-red-700 mt-1">{error}</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Analysis Results */}
          <div>
            {loading && (
              <div className="bg-white rounded-lg shadow-md p-8 text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
                <p className="mt-4 text-gray-600">Analyzing email with AI agents...</p>
                <p className="mt-2 text-sm text-gray-500">This may take 10-20 seconds</p>
              </div>
            )}

            {analysis && !loading && (
              <AnalysisResults analysis={analysis} />
            )}

            {!analysis && !loading && !error && (
              <div className="bg-white rounded-lg shadow-md p-8 text-center text-gray-500">
                <svg className="w-16 h-16 mx-auto text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p>Enter email details and click "Analyze" to get started</p>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-12 py-6 text-center text-sm text-gray-600">
        <p>Built with FastAPI, Groq AI, and React • Free & Open Source</p>
        <p className="mt-1">Uses multiple AI agents for comprehensive phishing detection</p>
      </footer>
    </div>
  )
}

export default App
