import { useState } from 'react'

export default function EmailForm({ onAnalyze, loading, onReset }) {
  const [inputMode, setInputMode] = useState('simple') // 'simple' or 'raw'
  const [formData, setFormData] = useState({
    from_address: '',
    subject: '',
    body_text: '',
    raw_email: ''
  })

  const handleSubmit = (e) => {
    e.preventDefault()

    if (inputMode === 'raw') {
      onAnalyze({ raw_email: formData.raw_email })
    } else {
      onAnalyze({
        from_address: formData.from_address,
        subject: formData.subject,
        body_text: formData.body_text
      })
    }
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleModeChange = (mode) => {
    setInputMode(mode)
    onReset()
  }

  const loadExample = () => {
    if (inputMode === 'simple') {
      setFormData({
        ...formData,
        from_address: 'security@paypa1-verify.com',
        subject: 'Urgent: Your PayPal Account Has Been Limited',
        body_text: `Dear Valued Customer,

We have detected unusual activity on your PayPal account. For your security, we have temporarily limited your account access.

To restore full access, please verify your information immediately by clicking the link below:

http://paypal-secure-verify.tk/restore-account

You must complete this verification within 24 hours or your account will be permanently suspended.

If you do not complete this process, we will be unable to secure your account and may have to close it permanently.

Thank you for your immediate attention to this matter.

PayPal Security Team`
      })
    } else {
      setFormData({
        ...formData,
        raw_email: `From: security@paypa1-verify.com
To: customer@example.com
Subject: Urgent: Your PayPal Account Has Been Limited
Date: Mon, 15 Jan 2024 10:30:00 +0000
Return-Path: bounce@suspicious-mailer.xyz

Dear Valued Customer,

We have detected unusual activity on your PayPal account. For your security, we have temporarily limited your account access.

To restore full access, please verify your information immediately by clicking the link below:

http://paypal-secure-verify.tk/restore-account

You must complete this verification within 24 hours or your account will be permanently suspended.

Thank you for your immediate attention to this matter.

PayPal Security Team`
      })
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold text-gray-900">Email Input</h2>
        <button
          type="button"
          onClick={loadExample}
          className="text-sm text-indigo-600 hover:text-indigo-800"
        >
          Load Example
        </button>
      </div>

      {/* Mode Toggle */}
      <div className="flex space-x-2 mb-4">
        <button
          onClick={() => handleModeChange('simple')}
          className={`px-4 py-2 rounded-md text-sm font-medium ${
            inputMode === 'simple'
              ? 'bg-indigo-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Simple Mode
        </button>
        <button
          onClick={() => handleModeChange('raw')}
          className={`px-4 py-2 rounded-md text-sm font-medium ${
            inputMode === 'raw'
              ? 'bg-indigo-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Raw Email
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {inputMode === 'simple' ? (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                From Address *
              </label>
              <input
                type="text"
                name="from_address"
                value={formData.from_address}
                onChange={handleChange}
                required
                placeholder="sender@example.com"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Subject *
              </label>
              <input
                type="text"
                name="subject"
                value={formData.subject}
                onChange={handleChange}
                required
                placeholder="Email subject line"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email Body *
              </label>
              <textarea
                name="body_text"
                value={formData.body_text}
                onChange={handleChange}
                required
                rows={8}
                placeholder="Paste the email content here..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 font-mono text-sm"
              />
            </div>
          </>
        ) : (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Raw Email (RFC822 format) *
            </label>
            <textarea
              name="raw_email"
              value={formData.raw_email}
              onChange={handleChange}
              required
              rows={12}
              placeholder="Paste the complete raw email including headers..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 font-mono text-sm"
            />
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className={`w-full py-3 px-4 rounded-md font-medium text-white ${
            loading
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-indigo-600 hover:bg-indigo-700'
          }`}
        >
          {loading ? 'Analyzing...' : 'Analyze Email'}
        </button>
      </form>
    </div>
  )
}
