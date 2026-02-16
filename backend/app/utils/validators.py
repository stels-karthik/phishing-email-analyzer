import dns.resolver
import re
from typing import Dict, List, Optional
import tldextract


class EmailValidator:
    """Validate email headers and perform DNS checks."""

    @staticmethod
    def check_spf(domain: str, sender_ip: Optional[str] = None) -> Dict:
        """Check SPF record for domain."""
        try:
            answers = dns.resolver.resolve(domain, 'TXT')
            spf_record = None

            for rdata in answers:
                txt = str(rdata).strip('"')
                if txt.startswith('v=spf1'):
                    spf_record = txt
                    break

            return {
                "has_spf": spf_record is not None,
                "record": spf_record,
                "valid": spf_record is not None
            }
        except Exception as e:
            return {
                "has_spf": False,
                "record": None,
                "valid": False,
                "error": str(e)
            }

    @staticmethod
    def check_dmarc(domain: str) -> Dict:
        """Check DMARC record for domain."""
        try:
            dmarc_domain = f"_dmarc.{domain}"
            answers = dns.resolver.resolve(dmarc_domain, 'TXT')

            for rdata in answers:
                txt = str(rdata).strip('"')
                if txt.startswith('v=DMARC1'):
                    return {
                        "has_dmarc": True,
                        "record": txt,
                        "valid": True
                    }

            return {"has_dmarc": False, "record": None, "valid": False}
        except Exception as e:
            return {
                "has_dmarc": False,
                "record": None,
                "valid": False,
                "error": str(e)
            }

    @staticmethod
    def check_domain_age(domain: str) -> Optional[int]:
        """Check domain age (simplified - would need WHOIS API for real implementation)."""
        # This is a placeholder - real implementation would use WHOIS lookup
        # For free implementation, we skip this or use a free WHOIS API
        return None

    @staticmethod
    def extract_domain_from_email(email: str) -> str:
        """Extract domain from email address."""
        match = re.search(r'@([\w\.-]+)', email)
        return match.group(1) if match else ""

    @staticmethod
    def check_sender_mismatch(from_email: str, return_path: str, reply_to: str) -> List[str]:
        """Check for mismatches between sender addresses."""
        issues = []

        from_domain = EmailValidator.extract_domain_from_email(from_email)

        if return_path:
            return_domain = EmailValidator.extract_domain_from_email(return_path)
            if return_domain and from_domain != return_domain:
                issues.append(f"Return-Path domain ({return_domain}) differs from From domain ({from_domain})")

        if reply_to and reply_to != from_email:
            reply_domain = EmailValidator.extract_domain_from_email(reply_to)
            if reply_domain and from_domain != reply_domain:
                issues.append(f"Reply-To domain ({reply_domain}) differs from From domain ({from_domain})")

        return issues


class URLValidator:
    """Validate and analyze URLs."""

    @staticmethod
    def extract_domain(url: str) -> str:
        """Extract domain from URL."""
        extracted = tldextract.extract(url)
        return f"{extracted.domain}.{extracted.suffix}"

    @staticmethod
    def check_typosquatting(url: str, legitimate_domains: List[str]) -> Optional[str]:
        """Check if URL might be typosquatting a legitimate domain."""
        url_domain = URLValidator.extract_domain(url).lower()

        for legit in legitimate_domains:
            legit_lower = legit.lower()
            # Simple similarity check
            if url_domain != legit_lower:
                # Check for common typosquatting patterns
                if (url_domain.replace('1', 'l').replace('0', 'o') == legit_lower or
                    url_domain.replace('rn', 'm') == legit_lower or
                    url_domain.replace('vv', 'w') == legit_lower):
                    return f"Possible typosquatting of {legit}"

        return None

    @staticmethod
    def check_url_mismatch(link_text: str, link_url: str) -> bool:
        """Check if link text and URL domain mismatch (common phishing tactic)."""
        # Extract domain-like text from link text
        domain_pattern = r'(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,})'
        text_domains = re.findall(domain_pattern, link_text.lower())

        if text_domains:
            url_domain = URLValidator.extract_domain(link_url).lower()
            for text_domain in text_domains:
                if text_domain not in url_domain and url_domain not in text_domain:
                    return True

        return False

    @staticmethod
    def is_url_shortener(url: str) -> bool:
        """Check if URL is from a known URL shortener."""
        shorteners = [
            'bit.ly', 'goo.gl', 'tinyurl.com', 't.co', 'ow.ly',
            'is.gd', 'buff.ly', 'adf.ly', 'bit.do', 'short.to'
        ]
        domain = URLValidator.extract_domain(url).lower()
        return any(shortener in domain for shortener in shorteners)
