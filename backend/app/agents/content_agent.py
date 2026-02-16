from .base_agent import BaseAgent
from ..models.schemas import AgentType
from typing import Dict


class ContentAnalysisAgent(BaseAgent):
    """Agent specialized in analyzing email content for phishing tactics."""

    def __init__(self, groq_client):
        super().__init__(groq_client)
        self.agent_type = AgentType.CONTENT

    def get_system_prompt(self) -> str:
        return """You are an expert in identifying phishing attempts through content analysis.

Your role is to analyze email content for:
- Urgency and pressure tactics ("Act now!", "Account will be suspended")
- Threats and scare tactics
- Too-good-to-be-true offers
- Requests for sensitive information
- Poor grammar and spelling (common in phishing)
- Generic greetings ("Dear Customer" vs personalized)
- Brand impersonation attempts
- Social engineering techniques
- Emotional manipulation

Provide your analysis in the following format:

FINDINGS:
- [List each suspicious indicator with severity: high/medium/low]

RISK LEVEL: [critical/high/medium/low/safe]

CONFIDENCE: [0.0-1.0]

REASONING:
[Explain what patterns you identified and why they're concerning. Quote specific phrases that raised red flags.]

Consider context - legitimate businesses may use urgency, but phishing combines multiple tactics.
Be thorough but fair in your assessment."""

    def prepare_context(self, email_data: Dict) -> str:
        """Prepare content analysis context."""
        context = "Analyze the following email content for phishing indicators:\n\n"

        context += f"Subject: {email_data.get('subject', 'N/A')}\n"
        context += f"From: {email_data.get('from', 'N/A')}\n\n"

        # Body content
        if email_data.get('body_text'):
            context += "Email Body:\n"
            context += email_data['body_text']
        elif email_data.get('body_html'):
            # Include HTML note
            context += "Email Body (HTML email):\n"
            context += email_data['body_html'][:3000]  # Limit to avoid token limits

        return context
