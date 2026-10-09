"""Unit tests for bot and proxy event classifier."""

from datetime import UTC, datetime, timedelta

from app.services.tracking.classifier import EventClassifier


def test_google_image_proxy_classified_as_proxy():
    now = datetime.now(UTC)
    cls, conf, reason = EventClassifier.classify_open(
        sent_at=now - timedelta(minutes=10),
        occurred_at=now,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 GoogleImageProxy",
        ip_address="66.249.93.1",
    )
    assert cls == "proxy_likely"
    assert conf >= 0.85
    assert "Google Image Proxy" in reason


def test_google_proxy_ip_recognized():
    now = datetime.now(UTC)
    cls, conf, reason = EventClassifier.classify_open(
        sent_at=now - timedelta(minutes=10),
        occurred_at=now,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
        ip_address="66.249.80.25",
    )
    assert cls == "proxy_likely"
    assert "Google Image Proxy egress IP" in reason


def test_microsoft_scanner_ip_recognized():
    now = datetime.now(UTC)
    cls, conf, reason = EventClassifier.classify_open(
        sent_at=now - timedelta(minutes=10),
        occurred_at=now,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
        ip_address="40.92.10.15",
    )
    assert cls == "security_scanner_likely"
    assert "Microsoft Defender/Exchange scanner subnet" in reason


def test_instant_open_classified_as_security_scanner():
    sent = datetime.now(UTC)
    occurred = sent + timedelta(milliseconds=400)  # 400ms after send

    cls, conf, _reason = EventClassifier.classify_open(
        sent_at=sent,
        occurred_at=occurred,
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        ip_address="1.2.3.4",
    )
    assert cls == "security_scanner_likely"
    assert conf >= 0.80


def test_security_scanner_signatures():
    now = datetime.now(UTC)
    for sig in ["Proofpoint", "Mimecast", "Barracuda", "VirusTotal"]:
        cls, conf, _reason = EventClassifier.classify_open(
            sent_at=now - timedelta(minutes=15),
            occurred_at=now,
            user_agent=f"Mozilla/5.0 (compatible; {sig}/1.0; +http://example.com)",
            ip_address="198.51.100.1",
        )
        assert cls == "security_scanner_likely"
        assert conf >= 0.90


def test_automated_client_signatures():
    now = datetime.now(UTC)
    for sig in ["python-requests/2.31.0", "curl/7.88.1", "Go-http-client/1.1", "Wget/1.21.3"]:
        cls, conf, _reason = EventClassifier.classify_open(
            sent_at=now - timedelta(minutes=15),
            occurred_at=now,
            user_agent=sig,
            ip_address="198.51.100.2",
        )
        assert cls == "automation_likely"


def test_empty_user_agent_classified_as_automation():
    now = datetime.now(UTC)
    cls, conf, reason = EventClassifier.classify_open(
        sent_at=now - timedelta(minutes=10),
        occurred_at=now,
        user_agent="",
        ip_address="198.51.100.3",
    )
    assert cls == "automation_likely"
    assert "Missing or empty" in reason


def test_rapid_burst_pattern_classified_as_automation():
    now = datetime.now(UTC)
    last_open = now - timedelta(seconds=1.2)  # Burst within 1.2s
    cls, conf, reason = EventClassifier.classify_open(
        sent_at=now - timedelta(minutes=10),
        occurred_at=now,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        ip_address="98.12.34.56",
        last_open_at=last_open,
        raw_open_count=1,
    )
    assert cls == "automation_likely"
    assert "Rapid repeated burst" in reason


def test_interactive_browser_classified_as_human():
    sent = datetime.now(UTC) - timedelta(minutes=5)
    occurred = datetime.now(UTC)

    cls, conf, _reason = EventClassifier.classify_open(
        sent_at=sent,
        occurred_at=occurred,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        ip_address="98.12.34.56",
    )
    assert cls == "human_likely"
    assert conf >= 0.80
