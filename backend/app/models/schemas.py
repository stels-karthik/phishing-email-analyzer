from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime


class RiskLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    SAFE = "safe"


class AgentType(str, Enum):
    HEADER = "header"
    CONTENT = "content"
    LINK = "link"
    ATTACHMENT = "attachment"
    SYNTHESIS = "synthesis"


class Finding(BaseModel):
    indicator: str
    description: str
    severity: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: Optional[str] = None


class AgentAnalysis(BaseModel):
    agent_type: AgentType
    findings: List[Finding]
    risk_level: RiskLevel
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    execution_time: float


class EmailInput(BaseModel):
    raw_email: Optional[str] = None
    from_address: Optional[str] = None
    to_address: Optional[str] = None
    subject: Optional[str] = None
    body_html: Optional[str] = None
    body_text: Optional[str] = None
    headers: Optional[Dict[str, str]] = None


class AnalysisResult(BaseModel):
    email_id: str
    timestamp: datetime
    overall_risk: RiskLevel
    confidence: float
    agent_analyses: List[AgentAnalysis]
    summary: str
    recommendations: List[str]
    threat_intel_hits: List[Dict[str, Any]]
    execution_time: float


class HealthResponse(BaseModel):
    status: str
    version: str
    groq_configured: bool
