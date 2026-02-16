import asyncio
from typing import Dict, List
from groq import Groq
import time
from datetime import datetime
import hashlib

from .header_agent import HeaderAnalysisAgent
from .content_agent import ContentAnalysisAgent
from .link_agent import LinkAnalysisAgent
from .attachment_agent import AttachmentAnalysisAgent
from .synthesis_agent import SynthesisAgent
from ..services.threat_intel import ThreatIntelService
from ..utils.validators import EmailValidator, URLValidator
from ..models.schemas import AnalysisResult, RiskLevel


class AnalysisOrchestrator:
    """Orchestrates the multi-agent phishing analysis."""

    def __init__(self, groq_api_key: str):
        self.groq_client = Groq(api_key=groq_api_key)
        self.threat_intel = ThreatIntelService()

        # Initialize agents
        self.header_agent = HeaderAnalysisAgent(self.groq_client)
        self.content_agent = ContentAnalysisAgent(self.groq_client)
        self.link_agent = LinkAnalysisAgent(self.groq_client)
        self.attachment_agent = AttachmentAnalysisAgent(self.groq_client)
        self.synthesis_agent = SynthesisAgent(self.groq_client)

    async def analyze_email(self, email_data: Dict) -> AnalysisResult:
        """Run complete multi-agent analysis on an email."""
        start_time = time.time()

        # Generate email ID
        email_id = hashlib.md5(
            f"{email_data.get('from', '')}{email_data.get('subject', '')}{time.time()}".encode()
        ).hexdigest()[:12]

        try:
            # Step 1: Enrich email data with validation and threat intel
            enriched_data = await self._enrich_email_data(email_data)

            # Step 2: Run specialized agents in parallel
            agent_analyses = await self._run_agent_analyses(enriched_data)

            # Step 3: Synthesize findings
            synthesis = await self.synthesis_agent.synthesize(enriched_data, agent_analyses)

            # Step 4: Compile final result
            execution_time = time.time() - start_time

            result = AnalysisResult(
                email_id=email_id,
                timestamp=datetime.now(),
                overall_risk=synthesis["overall_risk"],
                confidence=synthesis["confidence"],
                agent_analyses=agent_analyses,
                summary=synthesis["summary"],
                recommendations=synthesis["recommendations"],
                threat_intel_hits=[
                    hit for hit in enriched_data.get('threat_intel_results', [])
                    if hit.get('malicious')
                ],
                execution_time=execution_time
            )

            return result

        except Exception as e:
            # Return error result
            execution_time = time.time() - start_time
            return AnalysisResult(
                email_id=email_id,
                timestamp=datetime.now(),
                overall_risk=RiskLevel.MEDIUM,
                confidence=0.0,
                agent_analyses=[],
                summary=f"Analysis failed: {str(e)}",
                recommendations=["Manual review required", "Contact security team"],
                threat_intel_hits=[],
                execution_time=execution_time
            )

    async def _enrich_email_data(self, email_data: Dict) -> Dict:
        """Enrich email data with validation and threat intelligence."""
        enriched = email_data.copy()

        # Email validation
        from_email = email_data.get('from', '')
        domain = EmailValidator.extract_domain_from_email(from_email)

        validation_results = {}

        if domain:
            # Check SPF and DMARC
            spf_result = EmailValidator.check_spf(domain)
            dmarc_result = EmailValidator.check_dmarc(domain)

            validation_results['spf'] = spf_result
            validation_results['dmarc'] = dmarc_result

            # Check for sender mismatches
            sender_mismatches = EmailValidator.check_sender_mismatch(
                from_email,
                email_data.get('return_path', ''),
                email_data.get('reply_to', '')
            )
            validation_results['sender_mismatches'] = sender_mismatches

        enriched['validation_results'] = validation_results

        # Analyze links
        links = email_data.get('links', [])
        if links:
            # Enrich each link with analysis
            enriched_links = []
            threat_intel_results = []

            for link in links:
                url = link.get('url', '')
                link_text = link.get('text', '')

                # URL analysis
                link_analysis = {
                    'is_shortener': URLValidator.is_url_shortener(url),
                    'mismatch': URLValidator.check_url_mismatch(link_text, url),
                }

                # Check for typosquatting (common brands)
                common_brands = ['paypal.com', 'amazon.com', 'microsoft.com', 'apple.com',
                               'google.com', 'facebook.com', 'netflix.com', 'chase.com']
                typosquat = URLValidator.check_typosquatting(url, common_brands)
                if typosquat:
                    link_analysis['typosquatting'] = typosquat

                link['analysis'] = link_analysis
                enriched_links.append(link)

                # Threat intelligence check
                threat_results = await self.threat_intel.check_url(url)
                threat_intel_results.extend(threat_results)

            enriched['links'] = enriched_links
            enriched['threat_intel_results'] = threat_intel_results

        return enriched

    async def _run_agent_analyses(self, email_data: Dict) -> List:
        """Run all specialized agents in parallel."""
        # Create analysis tasks
        tasks = [
            self.header_agent.analyze(email_data),
            self.content_agent.analyze(email_data),
            self.link_agent.analyze(email_data),
            self.attachment_agent.analyze(email_data),
        ]

        # Run in parallel
        analyses = await asyncio.gather(*tasks)

        return analyses
