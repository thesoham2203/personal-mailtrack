"""Bot, Scanner, and Prefetch Event Classifier for open and click tracking.
Complies with PRD Section 23: Bot/Prefetch Classification.
"""

from datetime import UTC, datetime
import ipaddress

# Known image proxy user agent signatures
IMAGE_PROXY_SIGNATURES = [
    "googleimageproxy",
    "yahoo! slurp",
    "yahoocache",
    "apple mail privacy protection",
    "apple-mpp",
    "cloudflare-always-online",
]

# Automated enterprise security scanner and email security gateway signatures
SECURITY_SCANNER_SIGNATURES = [
    "barracuda",
    "mimecast",
    "proofpoint",
    "trend micro",
    "symantec",
    "virustotal",
    "zscaler",
    "cisco",
    "sophos",
    "fireeye",
    "palo alto",
    "paloalto",
    "fortinet",
    "spamassassin",
    "mailguard",
    "forcepoint",
    "hornetsecurity",
    "mcafee",
    "kaspersky",
    "avast",
    "eset",
    "cyren",
    "safelinks",
    "bingpreview",
]

# Automated HTTP clients, crawlers, and headless browser signatures
AUTOMATION_SIGNATURES = [
    "bot",
    "spider",
    "crawler",
    "headless",
    "phantomjs",
    "puppeteer",
    "playwright",
    "selenium",
    "python-requests",
    "aiohttp",
    "httpx",
    "curl",
    "wget",
    "go-http-client",
    "apache-httpclient",
    "okhttp",
    "java/",
    "winhttp",
    "urllib",
    "libwww",
    "scrapy",
    "node-fetch",
    "axios",
    "postman",
]

# Known CIDR blocks for cloud email image proxies
GOOGLE_PROXY_NETWORKS = [
    ipaddress.ip_network("66.249.64.0/19"),
    ipaddress.ip_network("72.14.192.0/18"),
    ipaddress.ip_network("209.85.128.0/17"),
]

# Known CIDR blocks for Microsoft Defender / Exchange Online scanners
MICROSOFT_SCANNER_NETWORKS = [
    ipaddress.ip_network("40.76.0.0/14"),
    ipaddress.ip_network("40.92.0.0/15"),
    ipaddress.ip_network("40.107.0.0/16"),
    ipaddress.ip_network("52.100.0.0/14"),
]


def _match_network(ip_str: str | None, networks: list[ipaddress.IPv4Network | ipaddress.IPv6Network]) -> bool:
    if not ip_str:
        return False
    try:
        ip = ipaddress.ip_address(ip_str.strip())
        return any(ip in net for net in networks)
    except ValueError:
        return False


class EventClassifier:
    """Classifies tracking requests into human vs proxy/scanner categories."""

    @staticmethod
    def classify_open(
        sent_at: datetime | None,
        occurred_at: datetime,
        user_agent: str | None,
        ip_address: str | None,
        last_open_at: datetime | None = None,
        raw_open_count: int = 0,
    ) -> tuple[str, float, str]:
        """
        Evaluates open event characteristics across User-Agent, IP/network,
        send timing, and request repetition patterns.
        
        Returns: (classification, confidence, reason)
        Valid classifications (PRD Section 23):
          - human_likely
          - proxy_likely
          - security_scanner_likely
          - automation_likely
          - unknown
        """
        ua_lower = (user_agent or "").lower().strip()

        # 0. Missing or empty User-Agent
        if not ua_lower:
            return "automation_likely", 0.90, "Missing or empty User-Agent header"

        # 1. Image Proxy Detection (User-Agent or Google proxy IP)
        if "googleimageproxy" in ua_lower:
            return "proxy_likely", 0.95, "Google Image Proxy prefetch/cache"

        if _match_network(ip_address, GOOGLE_PROXY_NETWORKS) or (ip_address and ip_address.startswith("66.249.")):
            return "proxy_likely", 0.92, f"Google Image Proxy egress IP ({ip_address})"

        for sig in IMAGE_PROXY_SIGNATURES:
            if sig in ua_lower:
                return "proxy_likely", 0.88, f"Known mail proxy signature: {sig}"

        # 2. Automated Security Scanner Detection (Signatures & Gateway Networks)
        for sig in SECURITY_SCANNER_SIGNATURES:
            if sig in ua_lower:
                return "security_scanner_likely", 0.95, f"Automated security scanner signature: {sig}"

        if _match_network(ip_address, MICROSOFT_SCANNER_NETWORKS):
            return "security_scanner_likely", 0.85, f"Microsoft Defender/Exchange scanner subnet ({ip_address})"

        # 3. Automation / Bot / Headless Scripts
        for sig in AUTOMATION_SIGNATURES:
            if sig in ua_lower:
                return "automation_likely", 0.95, f"Automated client signature: {sig}"

        # 4. Timing Evaluation (instant open after send)
        if sent_at:
            if sent_at.tzinfo is None:
                sent_at = sent_at.replace(tzinfo=UTC)
            if occurred_at.tzinfo is None:
                occurred_at = occurred_at.replace(tzinfo=UTC)

            delta_seconds = (occurred_at - sent_at).total_seconds()
            # If opened in under 1.5 seconds from send, inbound SMTP gateway scanner
            if 0 <= delta_seconds < 1.5:
                return "security_scanner_likely", 0.85, f"Instant open ({delta_seconds:.1f}s after send)"

        # 5. Rapid repeated-fetch / burst probe pattern (< 3.0s from previous open)
        if last_open_at:
            if last_open_at.tzinfo is None:
                last_open_at = last_open_at.replace(tzinfo=UTC)
            if occurred_at.tzinfo is None:
                occurred_at = occurred_at.replace(tzinfo=UTC)

            burst_delta = (occurred_at - last_open_at).total_seconds()
            if 0 <= burst_delta < 3.0 and raw_open_count >= 1:
                return "automation_likely", 0.80, f"Rapid repeated burst ({burst_delta:.1f}s after prior request)"

        # 6. Standard Interactive Browser User-Agent check
        # Must contain legitimate browser vendor tokens and have plausible desktop/mobile UA structure
        browser_tokens = ("mozilla", "applewebkit", "chrome", "safari", "firefox", "edge")
        if any(b in ua_lower for b in browser_tokens) and len(ua_lower) > 35:
            return "human_likely", 0.85, "Standard interactive browser user-agent"

        return "unknown", 0.50, "Unclassified user-agent pattern"

    @staticmethod
    def classify_click(
        user_agent: str | None,
        ip_address: str | None,
    ) -> tuple[str, float, str]:
        """
        Classifies link click requests.
        Unlike image pixel opens (which are routinely loaded by proxies),
        link clicks represent intentional navigation unless originating from
        known automated URL scanners or security gateways.
        """
        ua_lower = (user_agent or "").lower().strip()

        # 1. Explicit security scanner or safe-link inspection crawler
        for sig in SECURITY_SCANNER_SIGNATURES:
            if sig in ua_lower:
                return "security_scanner_likely", 0.95, f"Automated link scanner signature: {sig}"

        if _match_network(ip_address, MICROSOFT_SCANNER_NETWORKS):
            return "security_scanner_likely", 0.85, f"Microsoft SafeLinks scanner subnet ({ip_address})"

        # 2. Explicit automated crawler/spider
        for sig in ["spider", "crawler", "headless", "phantomjs", "puppeteer", "playwright", "selenium"]:
            if sig in ua_lower:
                return "automation_likely", 0.90, f"Automated crawler signature: {sig}"

        return "human_likely", 0.95, "Interactive link click navigation"
