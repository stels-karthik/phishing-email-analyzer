import asyncio
import aiohttp
import hashlib
from typing import Dict, List, Optional
import os
from datetime import datetime, timedelta


class ThreatIntelService:
    """Free threat intelligence service integrations."""

    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY")
        self.cache = {}
        self.cache_ttl = timedelta(hours=int(os.getenv("CACHE_TTL_HOURS", 24)))

    async def check_url(self, url: str) -> List[Dict]:
        """Check URL against multiple free threat intelligence sources."""
        hits = []

        # Check cache first
        cache_key = f"url:{hashlib.md5(url.encode()).hexdigest()}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_ttl:
                return cached_data

        # Run checks in parallel
        tasks = [
            self._check_phishtank(url),
            self._check_urlhaus(url),
        ]

        if self.google_api_key:
            tasks.append(self._check_google_safe_browsing(url))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, dict) and result.get("malicious"):
                hits.append(result)

        # Cache results
        self.cache[cache_key] = (hits, datetime.now())

        return hits

    async def _check_phishtank(self, url: str) -> Dict:
        """Check URL against PhishTank (free, no API key needed for checking)."""
        try:
            # PhishTank provides a downloadable database
            # For real-time checking, you'd download their database periodically
            # This is a simplified placeholder
            return {
                "source": "PhishTank",
                "malicious": False,
                "details": "Database check not implemented (download PhishTank DB for offline checks)"
            }
        except Exception as e:
            return {"source": "PhishTank", "error": str(e)}

    async def _check_urlhaus(self, url: str) -> Dict:
        """Check URL against URLhaus abuse.ch (free, no API key)."""
        try:
            async with aiohttp.ClientSession() as session:
                api_url = "https://urlhaus-api.abuse.ch/v1/url/"
                data = {"url": url}

                async with session.post(api_url, data=data, timeout=5) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("query_status") == "ok":
                            return {
                                "source": "URLhaus",
                                "malicious": True,
                                "threat_type": result.get("threat", "unknown"),
                                "details": f"Listed on URLhaus: {result.get('url_status', 'active')}"
                            }

            return {"source": "URLhaus", "malicious": False}
        except Exception as e:
            return {"source": "URLhaus", "error": str(e)}

    async def _check_google_safe_browsing(self, url: str) -> Dict:
        """Check URL against Google Safe Browsing API (free tier: 10k lookups/day)."""
        if not self.google_api_key:
            return {"source": "Google Safe Browsing", "skipped": "No API key"}

        try:
            async with aiohttp.ClientSession() as session:
                api_url = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={self.google_api_key}"

                payload = {
                    "client": {
                        "clientId": "phishing-analyzer",
                        "clientVersion": "1.0.0"
                    },
                    "threatInfo": {
                        "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
                        "platformTypes": ["ANY_PLATFORM"],
                        "threatEntryTypes": ["URL"],
                        "threatEntries": [{"url": url}]
                    }
                }

                async with session.post(api_url, json=payload, timeout=5) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("matches"):
                            match = result["matches"][0]
                            return {
                                "source": "Google Safe Browsing",
                                "malicious": True,
                                "threat_type": match.get("threatType"),
                                "platform": match.get("platformType"),
                                "details": "Listed in Google Safe Browsing"
                            }

            return {"source": "Google Safe Browsing", "malicious": False}
        except Exception as e:
            return {"source": "Google Safe Browsing", "error": str(e)}

    async def check_domain_reputation(self, domain: str) -> Dict:
        """Check domain reputation using free sources."""
        # Placeholder for domain reputation checks
        # Could integrate with free sources like:
        # - DNS-based blacklists (DNSBL)
        # - Domain age checks via WHOIS (rate-limited)
        return {
            "domain": domain,
            "reputation": "unknown",
            "note": "Extended reputation checking requires additional free APIs"
        }
