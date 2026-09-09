"""Unit tests for SSRF prevention and destination URL validation."""

from app.security.url_safety import normalize_url, validate_destination_url


def test_valid_public_urls():
    assert validate_destination_url("https://google.com") is True
    assert validate_destination_url("http://example.com/page?ref=mail#pricing") is True
    assert validate_destination_url("https://subdomain.domain.co.uk/test") is True


def test_dangerous_schemes_rejected():
    assert validate_destination_url("javascript:alert(1)") is False
    assert validate_destination_url("data:text/html,<html>alert</html>") is False
    assert validate_destination_url("file:///etc/passwd") is False
    assert validate_destination_url("vbscript:msgbox(1)") is False
    assert validate_destination_url("//evil.com/path") is False


def test_loopback_and_private_ips_rejected():
    assert validate_destination_url("http://127.0.0.1:8000") is False
    assert validate_destination_url("http://localhost:3000") is False
    assert validate_destination_url("http://[::1]/secret") is False
    assert validate_destination_url("http://10.0.0.1") is False
    assert validate_destination_url("http://192.168.1.1/admin") is False
    assert validate_destination_url("http://172.16.0.1") is False
    assert validate_destination_url("http://169.254.169.254/latest/meta-data") is False


def test_userinfo_rejected():
    assert validate_destination_url("http://user:password@example.com") is False


def test_url_normalization():
    assert normalize_url("HTTPS://Example.Com/Path?A=1") == "https://example.com/Path?A=1"
    assert normalize_url("http://domain.com") == "http://domain.com/"
