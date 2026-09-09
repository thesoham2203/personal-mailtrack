"""SSRF and Destination URL Validation for Click Tracking."""

import ipaddress
import re
from urllib.parse import urlparse

# Prohibited URL schemes
BANNED_SCHEMES = {"javascript", "data", "vbscript", "file", "blob", "about"}

# Localhost names
LOCAL_HOSTS = {"localhost", "localhost.localdomain", "ip6-localhost", "ip6-loopback"}

MAX_URL_LENGTH = 2048


def is_ip_private_or_reserved(ip_str: str) -> bool:
    """Checks if an IP address string belongs to private, loopback, link-local, or reserved ranges."""
    try:
        ip = ipaddress.ip_address(ip_str)
        return (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        )
    except ValueError:
        return False


def validate_destination_url(url: str) -> bool:
    """Strictly validates that a destination URL is safe to redirect to, preventing SSRF and open redirects."""
    if not url or len(url) > MAX_URL_LENGTH:
        return False

    # Prevent protocol-relative URLs
    if url.startswith("//"):
        return False

    # Prevent whitespace or control characters
    if re.search(r"[\s\r\n\t]", url):
        return False

    try:
        parsed = urlparse(url)
    except Exception:
        return False

    # Scheme must be http or https
    if parsed.scheme.lower() not in ("http", "https"):
        return False

    # Hostname must be present
    hostname = parsed.hostname
    if not hostname:
        return False

    hostname_lower = hostname.lower().strip(".")

    # Reject user credentials in URL (user:pass@domain)
    if parsed.username or parsed.password:
        return False

    # Reject localhost
    if hostname_lower in LOCAL_HOSTS or hostname_lower.endswith(".localhost"):
        return False

    # If hostname is an IP address literal, check if it is private/reserved
    if is_ip_private_or_reserved(hostname_lower):
        return False

    # Reject common internal hostname patterns
    return hostname_lower not in ("internal", "lan", "local", "intranet")


def normalize_url(url: str) -> str:
    """Standardizes destination URL format."""
    parsed = urlparse(url.strip())
    # Rebuild with lowercased scheme and hostname
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path or "/"
    query = f"?{parsed.query}" if parsed.query else ""
    fragment = f"#{parsed.fragment}" if parsed.fragment else ""
    return f"{scheme}://{netloc}{path}{query}{fragment}"
