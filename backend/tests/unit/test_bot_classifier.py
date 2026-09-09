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
