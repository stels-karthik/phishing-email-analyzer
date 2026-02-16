from abc import ABC, abstractmethod
from typing import Dict, Any
import time
from groq import Groq
import os
from ..models.schemas import AgentAnalysis, AgentType, Finding, RiskLevel
import json


class BaseAgent(ABC):
    """Base class for all analysis agents."""

    def __init__(self, groq_client: Groq):
        self.client = groq_client
        self.model = "llama-3.1-70b-versatile"  # Groq's free tier model
        self.agent_type = None

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent."""
        pass

    @abstractmethod
    def prepare_context(self, email_data: Dict) -> str:
        """Prepare the context/input for this agent."""
        pass

    async def analyze(self, email_data: Dict, additional_context: Dict = None) -> AgentAnalysis:
        """Run the agent analysis."""
        start_time = time.time()

        try:
            # Prepare the analysis context
            context = self.prepare_context(email_data)

            if additional_context:
                context += f"\n\nAdditional Context:\n{json.dumps(additional_context, indent=2)}"

            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.get_system_prompt()},
                    {"role": "user", "content": context}
                ],
                temperature=0.3,
                max_tokens=2000
            )

            # Parse the response
            analysis_text = response.choices[0].message.content
            result = self._parse_response(analysis_text)

            execution_time = time.time() - start_time

            return AgentAnalysis(
                agent_type=self.agent_type,
                findings=result["findings"],
                risk_level=result["risk_level"],
                confidence=result["confidence"],
                reasoning=result["reasoning"],
                execution_time=execution_time
            )

        except Exception as e:
            execution_time = time.time() - start_time
            return AgentAnalysis(
                agent_type=self.agent_type,
                findings=[Finding(
                    indicator="Analysis Error",
                    description=f"Agent failed: {str(e)}",
                    severity="error",
                    confidence=1.0
                )],
                risk_level=RiskLevel.MEDIUM,
                confidence=0.0,
                reasoning=f"Analysis failed due to error: {str(e)}",
                execution_time=execution_time
            )

    def _parse_response(self, response_text: str) -> Dict:
        """Parse the LLM response into structured format."""
        try:
            # Try to parse as JSON first (if model returns JSON)
            if response_text.strip().startswith("{"):
                return json.loads(response_text)

            # Otherwise, use structured parsing
            findings = []
            risk_level = RiskLevel.LOW
            confidence = 0.7
            reasoning = response_text

            # Extract findings using simple parsing
            lines = response_text.split("\n")
            for line in lines:
                line = line.strip()
                if line.startswith("- ") or line.startswith("* "):
                    finding_text = line[2:].strip()
                    if finding_text:
                        # Determine severity based on keywords
                        severity = "medium"
                        if any(word in finding_text.lower() for word in ["critical", "dangerous", "malicious", "confirmed"]):
                            severity = "high"
                        elif any(word in finding_text.lower() for word in ["suspicious", "warning", "unusual"]):
                            severity = "medium"
                        else:
                            severity = "low"

                        findings.append(Finding(
                            indicator=finding_text[:50],
                            description=finding_text,
                            severity=severity,
                            confidence=0.7
                        ))

            # Determine risk level from response
            response_lower = response_text.lower()
            if "critical" in response_lower or "definitely phishing" in response_lower:
                risk_level = RiskLevel.CRITICAL
                confidence = 0.9
            elif "high risk" in response_lower or "likely phishing" in response_lower:
                risk_level = RiskLevel.HIGH
                confidence = 0.8
            elif "suspicious" in response_lower or "medium risk" in response_lower:
                risk_level = RiskLevel.MEDIUM
                confidence = 0.7
            elif "low risk" in response_lower:
                risk_level = RiskLevel.LOW
                confidence = 0.8
            else:
                risk_level = RiskLevel.SAFE
                confidence = 0.6

            return {
                "findings": findings if findings else [Finding(
                    indicator="General Analysis",
                    description="See reasoning for details",
                    severity="info",
                    confidence=confidence
                )],
                "risk_level": risk_level,
                "confidence": confidence,
                "reasoning": reasoning
            }

        except Exception as e:
            # Fallback parsing
            return {
                "findings": [Finding(
                    indicator="Parse Error",
                    description=f"Could not parse response: {str(e)}",
                    severity="info",
                    confidence=0.5
                )],
                "risk_level": RiskLevel.MEDIUM,
                "confidence": 0.5,
                "reasoning": response_text
            }
