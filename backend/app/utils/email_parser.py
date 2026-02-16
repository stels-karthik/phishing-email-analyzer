import email
from email import policy
from email.parser import BytesParser
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup
import re


class EmailParser:
    """Parse and extract components from email messages."""

    @staticmethod
    def parse_raw_email(raw_email: str) -> Dict:
        """Parse a raw email string and extract all components."""
        try:
            # Parse the email
            msg = email.message_from_string(raw_email, policy=policy.default)

            # Extract headers
            headers = {key: value for key, value in msg.items()}

            # Extract body
            body_text = ""
            body_html = ""

            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/plain":
                        body_text = part.get_content()
                    elif content_type == "text/html":
                        body_html = part.get_content()
            else:
                content_type = msg.get_content_type()
                if content_type == "text/plain":
                    body_text = msg.get_content()
                elif content_type == "text/html":
                    body_html = msg.get_content()

            # Extract links from HTML body
            links = EmailParser.extract_links(body_html if body_html else body_text)

            # Extract attachments info
            attachments = EmailParser.extract_attachment_info(msg)

            return {
                "from": msg.get("From", ""),
                "to": msg.get("To", ""),
                "subject": msg.get("Subject", ""),
                "date": msg.get("Date", ""),
                "headers": headers,
                "body_text": body_text,
                "body_html": body_html,
                "links": links,
                "attachments": attachments,
                "return_path": msg.get("Return-Path", ""),
                "reply_to": msg.get("Reply-To", ""),
            }
        except Exception as e:
            raise ValueError(f"Failed to parse email: {str(e)}")

    @staticmethod
    def extract_links(content: str) -> List[Dict[str, str]]:
        """Extract all URLs from email content."""
        links = []

        # Try HTML parsing first
        if "<" in content and ">" in content:
            try:
                soup = BeautifulSoup(content, 'html.parser')
                for a_tag in soup.find_all('a', href=True):
                    links.append({
                        "url": a_tag['href'],
                        "text": a_tag.get_text(strip=True),
                        "type": "html"
                    })
            except:
                pass

        # Also extract plain URLs using regex
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        plain_urls = re.findall(url_pattern, content)
        for url in plain_urls:
            if not any(link["url"] == url for link in links):
                links.append({
                    "url": url,
                    "text": url,
                    "type": "plain"
                })

        return links

    @staticmethod
    def extract_attachment_info(msg) -> List[Dict[str, str]]:
        """Extract attachment information without downloading content."""
        attachments = []

        if msg.is_multipart():
            for part in msg.walk():
                content_disposition = part.get("Content-Disposition", "")
                if "attachment" in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        attachments.append({
                            "filename": filename,
                            "content_type": part.get_content_type(),
                            "size": len(part.get_payload(decode=True) or b"")
                        })

        return attachments

    @staticmethod
    def extract_display_name_and_email(from_field: str) -> Tuple[str, str]:
        """Extract display name and email from 'From' field."""
        # Format: "Display Name <email@example.com>" or just "email@example.com"
        match = re.match(r'^"?([^"<]+)"?\s*<([^>]+)>$', from_field.strip())
        if match:
            return match.group(1).strip(), match.group(2).strip()
        else:
            # Just an email address
            return "", from_field.strip()
