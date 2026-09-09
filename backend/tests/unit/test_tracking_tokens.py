"""Unit tests for HMAC tracking tokens with key rotation."""

from app.security.tracking_tokens import TokenManager


def test_open_token_roundtrip():
    manager = TokenManager(active_key="secret-key-1234567890-test-key")
    token = manager.generate_open_token("recip-1", "email-1")
    assert token is not None

    payload = manager.verify_open_token(token)
    assert payload is not None
    assert payload["rid"] == "recip-1"
    assert payload["eid"] == "email-1"


def test_tampered_token_fails():
    manager = TokenManager(active_key="secret-key-1234567890-test-key")
    token = manager.generate_open_token("recip-1", "email-1")
    tampered = token[:-4] + "abcd"
    assert manager.verify_open_token(tampered) is None


def test_malformed_token_fails():
    manager = TokenManager(active_key="secret-key-1234567890-test-key")
    assert manager.verify_open_token("not-a-token") is None
    assert manager.verify_open_token("") is None
    assert manager.verify_open_token("a.b") is None


def test_click_token_binding():
    manager = TokenManager(active_key="secret-key-1234567890-test-key")
    dest_url = "https://example.com/pricing"
    token = manager.generate_click_token("recip-1", dest_url)

    # Valid check
    rid = manager.verify_click_token(token, dest_url)
    assert rid == "recip-1"

    # Forged destination URL should be rejected
    rid_tampered = manager.verify_click_token(token, "https://evil.com")
    assert rid_tampered is None


def test_key_rotation():
    old_key = "old-secret-key-1234567890"
    new_key = "new-secret-key-0987654321"

    # Token issued before rotation
    old_manager = TokenManager(active_key=old_key, key_id="v1")
    token = old_manager.generate_open_token("recip-old", "email-old")

    # System rotated to new active key, retaining old key in previous keys
    new_manager = TokenManager(active_key=new_key, previous_keys=[old_key], key_id="v2")
    # Add v1 alias for old key
    new_manager.all_keys["v1"] = old_key.encode("utf-8")

    payload = new_manager.verify_open_token(token)
    assert payload is not None
    assert payload["rid"] == "recip-old"
