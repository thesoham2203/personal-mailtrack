"""Bot and Prefetch Event Classifier for open and click tracking."""

from datetime import UTC, datetime

# Known image proxy user agents
PROXY_SIGNATURES = [
    "googleimageproxy",
    "yahoo! slurp",
    "barracuda",
    "mimecast",
    "proofpoint",
    "trend micro",
    "symantec",
]

# Automated scanner signatures
SCANNER_SIGNATURES = [
    "bot",
    "spider",
    "crawler",
    "headless",
    "python-requests",
    "curl",
    "wget",
    "go-http-client",
]


class EventClassifier:
    """Classifies tracking requests into human vs proxy/scanner categories."""

    @staticmethod
    def classify_open(
        sent_at: datetime | None,
        occurred_at: datetime,
        user_agent: str | None,
        ip_address: str | None,
    ) -> tuple[str, float, str]:
        """
        Evaluates open event characteristics.
        Returns: (classification, confidence, reason)
        """
        ua_lower = (user_agent or "").lower()

        # 1. Image Proxy Detection
        if "googleimageproxy" in ua_lower:
            return "proxy_likely", 0.90, "Google Image Proxy prefetch/cache"

        for sig in PROXY_SIGNATURES:
            if sig in ua_lower:
                return "proxy_likely", 0.85, f"Known mail proxy signature: {sig}"

        # 2. Automated Scanner Detection
        for sig in SCANNER_SIGNATURES:
            if sig in ua_lower:
                return "security_scanner_likely", 0.95, f"Automated scanner signature: {sig}"

        # 3. Timing Evaluation
        if sent_at:
            if sent_at.tzinfo is None:
                sent_at = sent_at.replace(tzinfo=UTC)
            if occurred_at.tzinfo is None:
                occurred_at = occurred_at.replace(tzinfo=UTC)

            delta_seconds = (occurred_at - sent_at).total_seconds()
            # If opened in under 1.5 seconds from exact send, likely automated inbound security scanner
            if 0 <= delta_seconds < 1.5:
                return "security_scanner_likely", 0.80, f"Instant open ({delta_seconds:.1f}s after send)"

        # 4. Standard Browser User-Agent check
        if any(b in ua_lower for b in ("mozilla", "applewebkit", "chrome", "safari", "firefox", "edge")):
            return "human_likely", 0.85, "Standard interactive browser user-agent"

        return "unknown", 0.50, "Unclassified user-agent pattern"
