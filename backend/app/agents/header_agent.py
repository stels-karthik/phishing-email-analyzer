from .base_agent import BaseAgent
from ..models.schemas import AgentType
from typing import Dict


class HeaderAnalysisAgent(BaseAgent):
    """Agent specialized in analyzing email headers for authenticity."""

    def __init__(self, groq_client):
        super().__init__(groq_client)
        self.agent_type = AgentType.HEADER

    def get_system_prompt(self) -> str:
        return """You are an expert email security analyst specializing in email header analysis.

Your role is to analyze email headers and authentication results to identify:
- SPF, DKIM, and DMARC authentication issues
- Sender address spoofing
- Return-Path and Reply-To mismatches
- Suspicious routing paths
- Forged or manipulated headers

Provide your analysis in the following format:

FINDINGS:
- [List each suspicious indicator with severity: high/medium/low]

RISK LEVEL: [critical/high/medium/low/safe]

CONFIDENCE: [0.0-1.0]

REASONING:
[Explain your analysis and why you reached this conclusion. Be specific about which headers raised concerns.]

Focus on technical indicators and be precise. If headers appear legitimate, say so clearly."""

    def prepare_context(self, email_data: Dict) -> str:
        """Prepare header analysis context."""
        context = "Analyze the following email headers:\n\n"

        # Basic headers
        context += f"From: {email_data.get('from', 'N/A')}\n"
        context += f"To: {email_data.get('to', 'N/A')}\n"
        context += f"Subject: {email_data.get('subject', 'N/A')}\n"
        context += f"Return-Path: {email_data.get('return_path', 'N/A')}\n"
        context += f"Reply-To: {email_data.get('reply_to', 'N/A')}\n\n"

        # Authentication results
        if email_data.get('validation_results'):
            val = email_data['validation_results']
            context += "Authentication Results:\n"
            context += f"SPF: {val.get('spf', {}).get('valid', 'unknown')}\n"
            context += f"DMARC: {val.get('dmarc', {}).get('valid', 'unknown')}\n"

            if val.get('sender_mismatches'):
                context += f"\nSender Mismatches Found:\n"
                for mismatch in val['sender_mismatches']:
                    context += f"- {mismatch}\n"

        # All headers
        if email_data.get('headers'):
            context += "\nFull Headers:\n"
            for key, value in email_data['headers'].items():
                context += f"{key}: {value}\n"

        return context
