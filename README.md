# Phishing Email Analyzer

A **zero-cost** multi-agent AI system for analyzing emails and detecting phishing attempts. Built with FastAPI, Groq AI, and React.

## Features

- **Multi-Agent AI Analysis**: Specialized AI agents analyze different aspects of emails
  - Header Analysis Agent: SPF/DKIM/DMARC validation, sender spoofing detection
  - Content Analysis Agent: Phishing tactics, urgency language, social engineering
  - Link Analysis Agent: URL typosquatting, malicious links, domain reputation
  - Attachment Analysis Agent: Suspicious file types and naming patterns
  - Synthesis Agent: Combines all findings for final risk assessment

- **Free Threat Intelligence**: Integrates with free APIs (URLhaus, Google Safe Browsing, PhishTank)
- **Zero Cost**: Uses Groq's free tier (14,400 requests/day) with Llama 3.1 70B
- **Modern UI**: Clean React interface with real-time analysis
- **Detailed Reports**: Natural language explanations and actionable recommendations

## Architecture

```
┌─────────────────────────────────────────┐
│  Frontend (React + Vite)                │
│  - Email input forms                    │
│  - Real-time analysis display           │
└──────────────┬──────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────┐
│  Backend API (FastAPI)                  │
│  - Email parsing & validation           │
│  - Orchestration layer                  │
└──────────────┬──────────────────────────┘
               │
     ┌─────────┴─────────┬─────────────┐
     ↓                   ↓             ↓
┌──────────┐    ┌────────────────┐  ┌──────────┐
│ Free     │    │ Multi-Agent AI │  │ SQLite   │
│ Threat   │    │ (Groq API)     │  │ Cache    │
│ Intel    │    │ - Header Agent │  │          │
│ APIs     │    │ - Content Agent│  │          │
│          │    │ - Link Agent   │  │          │
│          │    │ - Attach Agent │  │          │
│          │    │ - Synthesis    │  │          │
└──────────┘    └────────────────┘  └──────────┘
```

## Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- Groq API key (free tier: [console.groq.com](https://console.groq.com))

## Quick Start

### 1. Clone and Setup

```bash
cd C:\code\agentic-ai\phishing-analyzer
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp ..\.env.example .env
# Edit .env and add your GROQ_API_KEY
```

Get your free Groq API key:
1. Visit [console.groq.com](https://console.groq.com)
2. Sign up (no credit card required)
3. Create an API key
4. Add it to `.env`: `GROQ_API_KEY=your_key_here`

### 3. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install
```

### 4. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
python run.py
```
Backend runs on: http://localhost:8000

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
Frontend runs on: http://localhost:3000

### 5. Open and Test

Open http://localhost:3000 in your browser and:
1. Click "Load Example" to load a sample phishing email
2. Click "Analyze Email" to see the multi-agent analysis
3. Review detailed findings from each AI agent

## Usage

### Simple Mode
Enter email details directly:
- From address
- Subject
- Body content

### Raw Email Mode
Paste complete raw email (RFC822 format) including headers.

### Analysis Results

The system provides:
- **Overall Risk Score**: Critical/High/Medium/Low/Safe
- **Summary**: Executive summary of the threat
- **Recommendations**: Specific actions to take
- **Threat Intel Alerts**: Known malicious URLs/domains
- **Agent Findings**: Detailed analysis from each specialized agent

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

**POST /api/v1/analyze**
```json
{
  "from_address": "sender@example.com",
  "subject": "Email subject",
  "body_text": "Email content..."
}
```

**POST /api/v1/analyze/file**
Upload .eml or .msg file for analysis.

**GET /api/v1/health**
Health check endpoint.

## Cost Analysis

### Current Setup (Zero Cost)
- **Groq API**: Free tier (14,400 requests/day)
- **Threat Intel APIs**: Free tiers only
- **Hosting**: Run locally or use free tiers (Render/Vercel)
- **Database**: SQLite (file-based)

**Daily Capacity**: ~14,000 email analyses/day (more than enough for personal/small team use)

### Scaling (Low Cost)
If you exceed free tier:
- Groq: $0.05-0.27 per 1M tokens
- Typical email analysis: ~1000 tokens
- Cost: ~$0.0001 per email

## Configuration

### Environment Variables

Edit [.env](.env.example):

```bash
# Required
GROQ_API_KEY=your_groq_api_key

# Optional
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
GOOGLE_SAFE_BROWSING_API_KEY=optional_but_recommended
CACHE_TTL_HOURS=24
```

### Threat Intelligence APIs

All are free:
- **URLhaus**: No API key needed
- **Google Safe Browsing**: 10k lookups/day (optional, recommended)
- **PhishTank**: Database-based (download periodically)

## Project Structure

```
phishing-analyzer/
├── backend/
│   ├── app/
│   │   ├── agents/          # AI agents
│   │   │   ├── base_agent.py
│   │   │   ├── header_agent.py
│   │   │   ├── content_agent.py
│   │   │   ├── link_agent.py
│   │   │   ├── attachment_agent.py
│   │   │   ├── synthesis_agent.py
│   │   │   └── orchestrator.py
│   │   ├── api/             # FastAPI routes
│   │   ├── models/          # Pydantic models
│   │   ├── services/        # Threat intel services
│   │   ├── utils/           # Email parsing, validation
│   │   └── main.py          # FastAPI app
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── .env.example
└── README.md
```

## How It Works

1. **Email Parsing**: Extract headers, links, attachments, and content
2. **Pre-Processing**: Validate SPF/DKIM/DMARC, check URLs against threat intel
3. **Agent Analysis**: Run 4 specialized AI agents in parallel
   - Each agent uses Groq's Llama 3.1 70B model
   - Agents analyze their specific domain with detailed prompts
   - Returns structured findings with confidence scores
4. **Synthesis**: Synthesis agent reviews all findings and makes final determination
5. **Results**: Return comprehensive report with risk level and recommendations

## Deployment

### Backend (Free Options)

**Render.com**:
```bash
# Deploy to Render free tier
# Add GROQ_API_KEY in environment variables
```

**Railway.app**:
```bash
# Deploy to Railway
railway up
```

### Frontend (Free Options)

**Vercel**:
```bash
cd frontend
npm run build
vercel --prod
```

**Netlify**:
```bash
cd frontend
npm run build
netlify deploy --prod
```

## Limitations

- Free tier rate limits (14,400/day on Groq)
- No malware scanning (only metadata analysis)
- LLM-based detection (not signature-based)
- Response time: 10-20 seconds per email

## Security Notes

- This tool analyzes email metadata and content using AI
- It does NOT execute or open attachments
- It does NOT click on links (only analyzes URLs)
- All processing happens server-side
- No email data is stored (beyond cache)

## Contributing

Contributions welcome! Areas for improvement:
- Additional AI agents (e.g., image analysis)
- More threat intelligence integrations
- Improved caching strategies
- Batch analysis support
- User authentication

## License

MIT License - feel free to use and modify

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

## Acknowledgments

- **Groq**: Fast, free LLM inference
- **URLhaus**: Free malicious URL database
- **FastAPI**: Modern Python web framework
- **React + Vite**: Fast frontend development

---

Built with ❤️ for cybersecurity education and awareness
