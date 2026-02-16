# Detailed Setup Guide

This guide provides step-by-step instructions for setting up the Phishing Email Analyzer.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Getting Groq API Key](#getting-groq-api-key)
3. [Backend Setup](#backend-setup)
4. [Frontend Setup](#frontend-setup)
5. [Running the Application](#running-the-application)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

1. **Python 3.10 or higher**
   ```bash
   python --version
   # Should output: Python 3.10.x or higher
   ```
   Download from: https://www.python.org/downloads/

2. **Node.js 18 or higher**
   ```bash
   node --version
   # Should output: v18.x.x or higher
   ```
   Download from: https://nodejs.org/

3. **Git** (for cloning)
   ```bash
   git --version
   ```

## Getting Groq API Key

Groq provides **free** access to Llama 3.1 70B with generous rate limits:

1. Visit [console.groq.com](https://console.groq.com)
2. Click "Sign Up" (no credit card required)
3. Verify your email
4. Go to "API Keys" section
5. Click "Create API Key"
6. Copy the key (you'll need it later)

**Free Tier Limits:**
- 30 requests per minute
- 14,400 requests per day
- Perfect for personal/small team use

## Backend Setup

### Step 1: Navigate to Backend Directory

```bash
cd C:\code\agentic-ai\phishing-analyzer\backend
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- FastAPI (web framework)
- Groq (AI client)
- Email parsing libraries
- DNS validation tools
- Threat intelligence clients

### Step 4: Configure Environment

Create `.env` file:
```bash
# Windows
copy ..\.env.example .env

# Linux/Mac
cp ../.env.example .env
```

Edit `.env` with a text editor and add your Groq API key:
```bash
GROQ_API_KEY=gsk_your_actual_api_key_here

API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
```

**Optional:** Add Google Safe Browsing API key for enhanced threat detection:
```bash
GOOGLE_SAFE_BROWSING_API_KEY=your_google_api_key
```

Get free Google Safe Browsing key:
1. Visit: https://developers.google.com/safe-browsing/v4/get-started
2. Create a project
3. Enable Safe Browsing API
4. Create credentials (API key)

### Step 5: Verify Backend Setup

```bash
python run.py
```

You should see:
```
Starting Phishing Email Analyzer API on 0.0.0.0:8000
DEBUG mode: True
API Documentation: http://0.0.0.0:8000/docs
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Visit http://localhost:8000/docs to see the API documentation.

Stop the server with `Ctrl+C`.

## Frontend Setup

### Step 1: Navigate to Frontend Directory

Open a **new terminal** and:
```bash
cd C:\code\agentic-ai\phishing-analyzer\frontend
```

### Step 2: Install Dependencies

```bash
npm install
```

This installs:
- React (UI framework)
- Vite (build tool)
- Tailwind CSS (styling)
- Axios (API client)

### Step 3: Verify Frontend Setup

```bash
npm run dev
```

You should see:
```
  VITE v5.0.11  ready in 500 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

Visit http://localhost:3000 to see the frontend (it won't work yet without the backend).

Stop the server with `Ctrl+C`.

## Running the Application

You need **two terminals** running simultaneously:

### Terminal 1: Backend

```bash
cd C:\code\agentic-ai\phishing-analyzer\backend
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
python run.py
```

Leave this running. Backend API is now available at http://localhost:8000

### Terminal 2: Frontend

```bash
cd C:\code\agentic-ai\phishing-analyzer\frontend
npm run dev
```

Leave this running. Frontend is now available at http://localhost:3000

### Access the Application

Open your browser and go to: **http://localhost:3000**

## Testing

### Test 1: Load Example Email

1. Click "Load Example" button
2. Review the pre-filled phishing email example
3. Click "Analyze Email"
4. Wait 10-20 seconds for analysis
5. Review the results showing risk level and agent findings

### Test 2: Custom Email

**Simple Mode:**
1. Enter a from address: `test@example.com`
2. Enter a subject: `Test Email`
3. Enter body text: `This is a test email with a link: http://example.com`
4. Click "Analyze Email"

**Raw Email Mode:**
1. Switch to "Raw Email" tab
2. Paste a complete email with headers
3. Click "Analyze Email"

### Test 3: API Testing

Visit http://localhost:8000/docs and try the API directly:

1. Expand POST `/api/v1/analyze`
2. Click "Try it out"
3. Enter test data:
```json
{
  "from_address": "test@example.com",
  "subject": "Test",
  "body_text": "Test email"
}
```
4. Click "Execute"
5. See the JSON response

## Troubleshooting

### Backend Issues

**Issue: "GROQ_API_KEY not set"**
```
Solution: Check your .env file has GROQ_API_KEY=your_key
Make sure .env is in the backend directory
```

**Issue: "Module not found"**
```bash
Solution: Activate virtual environment and reinstall
venv\Scripts\activate
pip install -r requirements.txt
```

**Issue: "Port 8000 already in use"**
```bash
Solution: Change port in .env file
API_PORT=8001
```

**Issue: DNS resolution errors**
```
Solution: This is normal if email has invalid domains
The analyzer will note this in findings
```

### Frontend Issues

**Issue: "Cannot connect to backend"**
```
Solution: Ensure backend is running on port 8000
Check browser console for CORS errors
```

**Issue: npm install fails**
```bash
Solution: Clear npm cache and retry
npm cache clean --force
npm install
```

**Issue: Page is blank**
```bash
Solution: Check browser console for errors
Try: npm run build && npm run preview
```

### Analysis Issues

**Issue: "Analysis takes too long"**
```
Cause: Groq API rate limiting or network latency
Solution: Wait and retry. Free tier has rate limits.
```

**Issue: "Low confidence scores"**
```
Cause: Ambiguous emails are hard to classify
This is expected - the AI is being cautious
```

**Issue: "Threat intel not working"**
```
Cause: Free APIs may be rate limited or down
Solution: This is optional - analysis continues without it
```

## Next Steps

### Enhance Threat Intelligence

Add Google Safe Browsing API key to `.env`:
```bash
GOOGLE_SAFE_BROWSING_API_KEY=your_key_here
```

This adds real-time malicious URL detection.

### Deploy to Production

See [README.md](README.md) deployment section for:
- Deploying backend to Render/Railway
- Deploying frontend to Vercel/Netlify
- Setting up custom domain

### Customize Agents

Edit agent prompt files in `backend/app/agents/` to:
- Adjust sensitivity
- Add brand-specific checks
- Modify risk scoring

## Support

If you encounter issues:

1. Check logs in terminal for error messages
2. Verify all prerequisites are installed
3. Ensure .env file is configured correctly
4. Try the example email first
5. Check Groq API status: https://status.groq.com

For more help, open an issue on GitHub with:
- Error message
- Steps to reproduce
- Your environment (OS, Python version, Node version)

## Security Best Practices

1. **Never commit `.env` file** - it's in .gitignore
2. **Rotate API keys** periodically
3. **Use environment variables** in production
4. **Enable HTTPS** in production deployment
5. **Rate limit** your API endpoints in production

## Development Tips

### Backend Development

```bash
# Auto-reload on changes (DEBUG=True in .env)
python run.py

# Run specific agent test
python -c "from app.agents.header_agent import HeaderAnalysisAgent; print('OK')"

# Check code style
pip install black
black app/
```

### Frontend Development

```bash
# Development with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

---

Congratulations! Your Phishing Email Analyzer is now set up and running. 🎉
