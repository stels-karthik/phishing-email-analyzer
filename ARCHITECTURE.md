# Architecture Documentation

This document describes the technical architecture of the Phishing Email Analyzer.

## Overview

The system uses a **multi-agent architecture** where specialized AI agents analyze different aspects of emails in parallel, then a synthesis agent combines findings for a final assessment.

## System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        Frontend Layer                         │
│  ┌────────────┐  ┌─────────────┐  ┌──────────────────────┐  │
│  │ Email Form │  │ Results UI  │  │ Agent Visualizations │  │
│  └─────┬──────┘  └──────▲──────┘  └──────────────────────┘  │
│        │                 │                                     │
└────────┼─────────────────┼─────────────────────────────────────┘
         │ POST            │ JSON Response
         │                 │
┌────────▼─────────────────┴─────────────────────────────────────┐
│                      API Gateway (FastAPI)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────┐ │
│  │ /analyze     │  │ /analyze/file│  │ /health             │ │
│  └──────┬───────┘  └──────┬───────┘  └─────────────────────┘ │
│         │                  │                                    │
└─────────┼──────────────────┼────────────────────────────────────┘
          │                  │
┌─────────▼──────────────────▼────────────────────────────────────┐
│                    Orchestration Layer                          │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Analysis Orchestrator                        │  │
│  │  1. Parse & Enrich Email                                 │  │
│  │  2. Run Agents in Parallel                               │  │
│  │  3. Synthesize Results                                   │  │
│  └────┬─────────────────────────────────────────────────┬───┘  │
│       │                                                  │       │
└───────┼──────────────────────────────────────────────────┼───────┘
        │                                                  │
        ├──────────────┬────────────────┬─────────────────┤
        │              │                │                 │
┌───────▼────┐  ┌──────▼──────┐  ┌─────▼──────┐  ┌──────▼────────┐
│  Header    │  │  Content    │  │  Link      │  │  Attachment   │
│  Agent     │  │  Agent      │  │  Agent     │  │  Agent        │
│            │  │             │  │            │  │               │
│ • SPF/DKIM │  │ • Urgency   │  │ • Typo-    │  │ • File Types  │
│ • Spoofing │  │ • Threats   │  │   squatting│  │ • Extensions  │
│ • Routing  │  │ • Grammar   │  │ • Mismatch │  │ • Naming      │
└───────┬────┘  └──────┬──────┘  └─────┬──────┘  └──────┬────────┘
        │              │                │                 │
        └──────────────┴────────────────┴─────────────────┘
                       │
                ┌──────▼──────────┐
                │  Synthesis Agent│
                │                 │
                │ • Weighs all    │
                │   findings      │
                │ • Final risk    │
                │ • Recommends    │
                └────────┬────────┘
                         │
                   Final Report

Supporting Services:
┌────────────────┐  ┌──────────────┐  ┌────────────────┐
│ Email Parser   │  │ Threat Intel │  │ Validators     │
│ • RFC822       │  │ • URLhaus    │  │ • DNS/SPF      │
│ • Links        │  │ • Google SB  │  │ • URL Analysis │
│ • Attachments  │  │ • PhishTank  │  │ • Domain Check │
└────────────────┘  └──────────────┘  └────────────────┘
```

## Component Details

### 1. Frontend Layer

**Technology:** React 18 + Vite + Tailwind CSS

**Components:**
- `EmailForm`: Input interface (simple mode & raw email mode)
- `AnalysisResults`: Display risk scores and findings
- `Header`: Application branding and info

**Features:**
- Real-time validation
- Example email loading
- Progress indicators
- Responsive design

### 2. API Gateway

**Technology:** FastAPI

**Endpoints:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/analyze` | POST | Analyze email from fields |
| `/api/v1/analyze/file` | POST | Analyze uploaded .eml/.msg file |
| `/api/v1/health` | GET | Health check |
| `/api/v1/stats` | GET | Usage statistics (future) |

**Responsibilities:**
- Request validation (Pydantic)
- Error handling
- CORS management
- API documentation (Swagger/ReDoc)

### 3. Orchestration Layer

**Class:** `AnalysisOrchestrator`

**Workflow:**

```python
async def analyze_email(email_data):
    1. Generate unique email_id
    2. Enrich email data:
       - Parse headers
       - Extract links & attachments
       - Validate DNS (SPF/DMARC)
       - Check threat intelligence
    3. Run agents in parallel:
       - header_agent.analyze()
       - content_agent.analyze()
       - link_agent.analyze()
       - attachment_agent.analyze()
    4. Synthesis:
       - synthesis_agent.synthesize(all_findings)
    5. Compile final result
    6. Return AnalysisResult
```

**Key Features:**
- Parallel agent execution (asyncio)
- Error handling per agent
- Result caching
- Execution time tracking

### 4. Agent System

#### Base Agent Architecture

```python
class BaseAgent(ABC):
    - groq_client: Groq
    - model: str = "llama-3.1-70b-versatile"

    @abstractmethod
    def get_system_prompt() -> str

    @abstractmethod
    def prepare_context(email_data) -> str

    async def analyze(email_data) -> AgentAnalysis

    def _parse_response(response) -> Dict
```

#### Specialized Agents

**1. Header Analysis Agent**
- Focuses on: Email authentication, routing, sender verification
- Input: Headers, SPF/DKIM/DMARC results, sender addresses
- Output: Findings about header manipulation, spoofing, mismatches

**2. Content Analysis Agent**
- Focuses on: Psychological tactics, language patterns, social engineering
- Input: Subject, body text/HTML
- Output: Urgency indicators, threats, grammar issues, impersonation

**3. Link Analysis Agent**
- Focuses on: URL safety, domain reputation, typosquatting
- Input: Extracted URLs, threat intel results, link text
- Output: Suspicious domains, shorteners, text/URL mismatches

**4. Attachment Analysis Agent**
- Focuses on: File type risks, naming patterns
- Input: Attachment metadata (name, type, size)
- Output: Risky file types, double extensions, suspicious names

**5. Synthesis Agent**
- Focuses on: Holistic assessment, correlation, final decision
- Input: All agent findings + threat intel
- Output: Overall risk, summary, recommendations

### 5. Supporting Services

#### Email Parser
```python
class EmailParser:
    - parse_raw_email(raw: str) -> Dict
    - extract_links(content: str) -> List[Dict]
    - extract_attachment_info(msg) -> List[Dict]
    - extract_display_name_and_email(from_field: str) -> Tuple
```

#### Validators
```python
class EmailValidator:
    - check_spf(domain: str) -> Dict
    - check_dmarc(domain: str) -> Dict
    - check_sender_mismatch(...) -> List[str]
    - extract_domain_from_email(email: str) -> str

class URLValidator:
    - extract_domain(url: str) -> str
    - check_typosquatting(url: str, legit_domains: List) -> Optional[str]
    - check_url_mismatch(text: str, url: str) -> bool
    - is_url_shortener(url: str) -> bool
```

#### Threat Intelligence Service
```python
class ThreatIntelService:
    - check_url(url: str) -> List[Dict]
    - _check_phishtank(url: str) -> Dict
    - _check_urlhaus(url: str) -> Dict
    - _check_google_safe_browsing(url: str) -> Dict
    - check_domain_reputation(domain: str) -> Dict
```

**Free APIs Used:**
- URLhaus (abuse.ch) - No key required
- Google Safe Browsing - 10k lookups/day
- PhishTank - Database download

## Data Models

### Input Model
```python
class EmailInput(BaseModel):
    raw_email: Optional[str]
    from_address: Optional[str]
    to_address: Optional[str]
    subject: Optional[str]
    body_html: Optional[str]
    body_text: Optional[str]
    headers: Optional[Dict[str, str]]
```

### Output Model
```python
class AnalysisResult(BaseModel):
    email_id: str
    timestamp: datetime
    overall_risk: RiskLevel  # critical/high/medium/low/safe
    confidence: float  # 0.0-1.0
    agent_analyses: List[AgentAnalysis]
    summary: str
    recommendations: List[str]
    threat_intel_hits: List[Dict]
    execution_time: float
```

### Agent Analysis Model
```python
class AgentAnalysis(BaseModel):
    agent_type: AgentType
    findings: List[Finding]
    risk_level: RiskLevel
    confidence: float
    reasoning: str
    execution_time: float

class Finding(BaseModel):
    indicator: str
    description: str
    severity: str  # high/medium/low
    confidence: float
    evidence: Optional[str]
```

## AI/LLM Integration

### Groq API Usage

**Model:** `llama-3.1-70b-versatile`

**Configuration:**
- Temperature: 0.3 (consistent, factual responses)
- Max tokens: 2000 per agent
- Async calls for parallel execution

**Prompt Engineering:**
Each agent has a specialized system prompt:
```python
system_prompt = """
You are an expert email security analyst specializing in [domain].

Your role is to analyze [aspect] for:
- [specific indicators]
- [specific patterns]

Provide your analysis in the following format:
FINDINGS: [structured list]
RISK LEVEL: [level]
CONFIDENCE: [0.0-1.0]
REASONING: [explanation]
"""
```

**Response Parsing:**
- Attempts JSON parsing first
- Falls back to text parsing with keyword extraction
- Extracts risk level, findings, confidence from structured text

### Cost Optimization

1. **Prompt Caching**: System prompts are reused
2. **Parallel Execution**: Minimize total wall time
3. **Pre-filtering**: Use heuristics before LLM calls
4. **Caching**: Store threat intel results
5. **Efficient Prompts**: Concise, focused context

**Token Usage per Email:**
- Header Agent: ~200 tokens
- Content Agent: ~500 tokens
- Link Agent: ~300 tokens
- Attachment Agent: ~200 tokens
- Synthesis Agent: ~400 tokens
- **Total: ~1600 tokens per email**

**Daily Capacity (Free Tier):**
- Rate limit: 30 req/min → 5 agents = 6 emails/min
- Daily limit: 14,400 req/day → ~2,880 emails/day

## Security Considerations

### Input Validation
- Pydantic models validate all inputs
- Email parsing uses safe libraries
- No code execution from email content

### Output Sanitization
- HTML content is parsed, not rendered
- URLs are analyzed but not visited
- Attachments are metadata-only

### API Security
- CORS configuration
- Rate limiting (recommended for production)
- No sensitive data logging
- Environment variable configuration

### Privacy
- No email storage (except cache)
- Cache TTL: 24 hours
- No user tracking
- All processing server-side

## Performance

### Benchmarks
- Average analysis time: 10-15 seconds
- Parallel agent execution: ~5-8 seconds
- Synthesis: ~3-5 seconds
- Network latency: ~2-3 seconds

### Bottlenecks
1. LLM API latency (Groq)
2. Threat intel API calls
3. DNS lookups

### Optimization Strategies
1. Parallel agent execution
2. Async I/O throughout
3. Result caching
4. Connection pooling

## Scalability

### Current Architecture
- Stateless API (scales horizontally)
- SQLite for caching (single instance)
- No session management

### Scaling Path
1. **Stage 1** (0-100 emails/day): Current setup
2. **Stage 2** (100-1000/day):
   - Add Redis cache
   - Implement rate limiting
3. **Stage 3** (1000+/day):
   - PostgreSQL for caching
   - Load balancer
   - Multiple API instances
   - Queue system (Celery/RQ)

## Error Handling

### Agent Failures
- Individual agent failures don't stop analysis
- Failed agents return error findings
- Synthesis continues with available data

### API Failures
- Threat intel timeouts (5s) don't block
- Graceful degradation
- Error responses with details

### Logging
- Structured logging (JSON)
- Error tracking
- Performance metrics

## Future Enhancements

### Planned Features
1. **Image Analysis Agent**: Logo verification, visual phishing
2. **Historical Analysis**: Track sender reputation over time
3. **Batch Processing**: Analyze multiple emails
4. **User Feedback**: Learn from corrections
5. **Custom Rules**: User-defined detection rules

### Architecture Improvements
1. **Microservices**: Split agents into separate services
2. **Event Streaming**: Kafka for real-time processing
3. **ML Pipeline**: Fine-tune models on feedback
4. **Admin Dashboard**: Monitoring and analytics

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | React 18 | UI framework |
| | Vite | Build tool |
| | Tailwind CSS | Styling |
| | Axios | HTTP client |
| Backend | FastAPI | API framework |
| | Uvicorn | ASGI server |
| | Pydantic | Data validation |
| AI/LLM | Groq | LLM API provider |
| | Llama 3.1 70B | Language model |
| Email | python-email | RFC822 parsing |
| | BeautifulSoup4 | HTML parsing |
| Network | dnspython | DNS queries |
| | requests/aiohttp | HTTP client |
| | tldextract | Domain parsing |
| Storage | SQLite | Caching |
| Threat Intel | URLhaus | Free API |
| | Google Safe Browsing | Free API |
| | PhishTank | Database |

---

This architecture provides a solid foundation for phishing detection while remaining cost-effective and scalable.
