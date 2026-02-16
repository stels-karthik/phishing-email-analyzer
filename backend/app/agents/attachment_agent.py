from .base_agent import BaseAgent
from ..models.schemas import AgentType
from typing import Dict


class AttachmentAnalysisAgent(BaseAgent):
    """Agent specialized in analyzing email attachments for threats."""

    def __init__(self, groq_client):
        super().__init__(groq_client)
        self.agent_type = AgentType.ATTACHMENT

    def get_system_prompt(self) -> str:
        return """You are an expert in identifying malicious email attachments.

Your role is to analyze attachment metadata and characteristics for:
- Executable files (.exe, .scr, .bat, .cmd, .com, etc.)
- Documents with macros (.docm, .xlsm, .pptm)
- Suspicious file extensions (double extensions like .pdf.exe)
- Archive files that might contain malware (.zip, .rar with suspicious contents)
- Suspicious file names (invoice.exe, document_urgent.scr)
- Unusual file types for the context
- Files with mismatched extensions (claims to be PDF but is executable)

Provide your analysis in the following format:

FINDINGS:
- [List each suspicious attachment with severity: high/medium/low]

RISK LEVEL: [critical/high/medium/low/safe]

CONFIDENCE: [0.0-1.0]

REASONING:
[Explain which attachments are suspicious and why. Consider the file type, name, and context.]

Note: We only analyze metadata, not file contents. Be especially suspicious of:
- Executable files (always high risk in unsolicited emails)
- Office documents with macros
- Unusual file types that don't match the claimed purpose"""

    def prepare_context(self, email_data: Dict) -> str:
        """Prepare attachment analysis context."""
        context = "Analyze the following email attachments:\n\n"

        context += f"Email from: {email_data.get('from', 'N/A')}\n"
        context += f"Subject: {email_data.get('subject', 'N/A')}\n\n"

        # Attachments
        attachments = email_data.get('attachments', [])
        if attachments:
            context += f"Found {len(attachments)} attachment(s):\n\n"
            for i, att in enumerate(attachments, 1):
                context += f"{i}. Filename: {att.get('filename', 'N/A')}\n"
                context += f"   Type: {att.get('content_type', 'N/A')}\n"
                context += f"   Size: {att.get('size', 0)} bytes\n\n"

            # Add context from email body
            body_preview = email_data.get('body_text', '')[:200]
            if body_preview:
                context += f"\nEmail Body Preview:\n{body_preview}...\n"
        else:
            context += "No attachments found in email.\n"
            context += "\nThis is a positive indicator - no attachment risk.\n"

        return context
