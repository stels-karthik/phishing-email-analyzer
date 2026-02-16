export default function Header() {
  return (
    <header className="bg-white shadow-sm">
      <div className="container mx-auto px-4 py-4 max-w-7xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <svg className="w-8 h-8 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Phishing Email Analyzer</h1>
              <p className="text-sm text-gray-600">AI-Powered Email Security Analysis</p>
            </div>
          </div>

          <div className="hidden md:flex items-center space-x-4">
            <span className="px-3 py-1 bg-green-100 text-green-800 text-xs font-semibold rounded-full">
              FREE
            </span>
            <span className="px-3 py-1 bg-indigo-100 text-indigo-800 text-xs font-semibold rounded-full">
              Multi-Agent AI
            </span>
          </div>
        </div>
      </div>
    </header>
  )
}
