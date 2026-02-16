from .base_agent import BaseAgent
from ..models.schemas import AgentType, AgentAnalysis, RiskLevel
from typing import Dict, List
import json


class SynthesisAgent(BaseAgent):
    """Agent that synthesizes findings from all other agents."""

    def __init__(self, groq_client):
        super().__init__(groq_client)
        self.agent_type = AgentType.SYNTHESIS

    def get_system_prompt(self) -> str:
        return """You are a senior email security analyst synthesizing findings from multiple specialized agents.

Your role is to:
1. Review all agent findings (header, content, link, attachment analyses)
2. Weigh the evidence from each agent
3. Identify corroborating indicators (multiple agents flagging related issues)
4. Make a final risk determination
5. Provide actionable recommendations

Provide your analysis in the following format:

OVERALL RISK: [critical/high/medium/low/safe]

CONFIDENCE: [0.0-1.0]

KEY FINDINGS:
- [List the most important findings from all agents]

SUMMARY:
[2-3 sentence executive summary of the threat assessment]

RECOMMENDATIONS:
- [List 3-5 specific actions the user should take]

REASONING:
[Explain how you weighed the different agent findings and why you reached this conclusion.
Consider that multiple weak indicators can add up to high risk, while strong legitimate
indicators can overcome minor suspicious elements.]

Be balanced and consider the full context. Not every suspicious element means phishing,
but multiple red flags warrant serious caution."""

    def prepare_context(self, email_data: Dict) -> str:
        """Prepare synthesis context from all agent analyses."""
        agent_analyses = email_data.get('agent_analyses', [])

        context = "Review the following analyses from specialized agents:\n\n"

        context += f"Email Summary:\n"
        context += f"From: {email_data.get('from', 'N/A')}\n"
        context += f"Subject: {email_data.get('subject', 'N/A')}\n"
        context += f"Links: {len(email_data.get('links', []))} found\n"
        context += f"Attachments: {len(email_data.get('attachments', []))} found\n\n"

        # Add each agent's analysis
        for analysis in agent_analyses:
            context += f"--- {analysis['agent_type'].upper()} AGENT ---\n"
            context += f"Risk Level: {analysis['risk_level']}\n"
            context += f"Confidence: {analysis['confidence']}\n\n"

            context += "Findings:\n"
            for finding in analysis['findings']:
                context += f"- [{finding['severity']}] {finding['description']}\n"

            context += f"\nReasoning:\n{analysis['reasoning']}\n\n"

        # Add threat intelligence summary
        threat_intel = email_data.get('threat_intel_results', [])
        if threat_intel:
            malicious_hits = [t for t in threat_intel if t.get('malicious')]
            if malicious_hits:
                context += "THREAT INTELLIGENCE ALERTS:\n"
                for hit in malicious_hits:
                    context += f"- {hit['source']}: {hit.get('details', 'Malicious URL detected')}\n"
                context += "\n"

        context += "Based on all evidence above, provide your final synthesis and recommendations."

        return context

    async def synthesize(self, email_data: Dict, agent_analyses: List[AgentAnalysis]) -> Dict:
        """Synthesize all agent findings into final assessment."""
        # Add analyses to email data for context preparation
        email_data['agent_analyses'] = [analysis.dict() for analysis in agent_analyses]

        # Run synthesis analysis
        synthesis = await self.analyze(email_data)

        # Parse recommendations from reasoning
        recommendations = self._extract_recommendations(synthesis.reasoning)

        # Generate summary
        summary = self._extract_summary(synthesis.reasoning)

        return {
            "overall_risk": synthesis.risk_level,
            "confidence": synthesis.confidence,
            "summary": summary,
            "recommendations": recommendations,
            "detailed_reasoning": synthesis.reasoning,
            "key_findings": [f.description for f in synthesis.findings[:5]]  # Top 5
        }

    def _extract_recommendations(self, reasoning: str) -> List[str]:
        """Extract recommendations from the synthesis reasoning."""
        recommendations = []
        in_recommendations = False

        for line in reasoning.split('\n'):
            line = line.strip()
            if 'RECOMMENDATION' in line.upper():
                in_recommendations = True
                continue
            if in_recommendations and (line.startswith('-') or line.startswith('•')):
                rec = line[1:].strip()
                if rec:
                    recommendations.append(rec)
            elif in_recommendations and line and not line.startswith('-'):
                # End of recommendations section
                if recommendations:
                    break

        # Default recommendations if none found
        if not recommendations:
            recommendations = [
                "Review the detailed analysis above",
                "Verify sender identity through known channels",
                "Do not click any links or download attachments if suspicious",
                "Report to your IT security team if applicable"
            ]

        return recommendations[:5]  # Limit to 5

    def _extract_summary(self, reasoning: str) -> str:
        """Extract summary from the synthesis reasoning."""
        # Look for SUMMARY section
        lines = reasoning.split('\n')
        in_summary = False
        summary_lines = []

        for line in lines:
            if 'SUMMARY' in line.upper():
                in_summary = True
                continue
            if in_summary:
                line = line.strip()
                if line and not line.startswith('RECOMMENDATION') and not line.startswith('REASONING'):
                    summary_lines.append(line)
                elif line.startswith('RECOMMENDATION') or line.startswith('REASONING'):
                    break

        if summary_lines:
            return ' '.join(summary_lines)

        # Fallback: use first few lines of reasoning
        return ' '.join(reasoning.split('\n')[:3])
