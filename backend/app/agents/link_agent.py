from .base_agent import BaseAgent
from ..models.schemas import AgentType
from typing import Dict


class LinkAnalysisAgent(BaseAgent):
    """Agent specialized in analyzing links for phishing indicators."""

    def __init__(self, groq_client):
        super().__init__(groq_client)
        self.agent_type = AgentType.LINK

    def get_system_prompt(self) -> str:
        return """You are an expert in identifying malicious URLs and phishing links.

Your role is to analyze links in emails for:
- Link text vs actual URL mismatches (hovering shows different domain)
- Suspicious domains that mimic legitimate sites (typosquatting)
- URL shorteners that hide the real destination
- Unusual or suspicious TLDs (.tk, .ml, etc.)
- Domains with excessive subdomains
- IP addresses instead of domain names
- Homograph attacks (using similar-looking characters)
- Known malicious domains (from threat intel)

Provide your analysis in the following format:

FINDINGS:
- [List each suspicious link with severity: high/medium/low]

RISK LEVEL: [critical/high/medium/low/safe]

CONFIDENCE: [0.0-1.0]

REASONING:
[Explain which links are suspicious and why. Be specific about what makes each URL concerning.]

If threat intelligence indicates known malicious URLs, flag them as critical.
Consider that some URL patterns are more common in phishing (e.g., long random strings, misspelled brand names)."""

    def prepare_context(self, email_data: Dict) -> str:
        """Prepare link analysis context."""
        context = "Analyze the following URLs found in the email:\n\n"

        context += f"Email claims to be from: {email_data.get('from', 'N/A')}\n"
        context += f"Subject: {email_data.get('subject', 'N/A')}\n\n"

        # Links
        links = email_data.get('links', [])
        if links:
            context += f"Found {len(links)} link(s):\n\n"
            for i, link in enumerate(links, 1):
                context += f"{i}. Text: \"{link.get('text', 'N/A')}\"\n"
                context += f"   URL: {link.get('url', 'N/A')}\n"

                # Add analysis results if available
                if link.get('analysis'):
                    analysis = link['analysis']
                    if analysis.get('is_shortener'):
                        context += "   [URL Shortener detected]\n"
                    if analysis.get('mismatch'):
                        context += "   [Link text/URL mismatch detected]\n"
                    if analysis.get('typosquatting'):
                        context += f"   [Possible typosquatting: {analysis['typosquatting']}]\n"

                context += "\n"
        else:
            context += "No links found in email.\n"

        # Threat intelligence results
        if email_data.get('threat_intel_results'):
            context += "\nThreat Intelligence Results:\n"
            for result in email_data['threat_intel_results']:
                if result.get('malicious'):
                    context += f"- {result['source']}: MALICIOUS - {result.get('details', 'No details')}\n"

        return context
