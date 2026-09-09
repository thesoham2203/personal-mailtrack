"""HMAC-signed opaque tracking capability tokens with key rotation support."""

import base64
import hashlib
import hmac
import json
import time
from typing import Any

from app.config import settings


def _urlsafe_b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _urlsafe_b64decode(data: str) -> bytes:
    padding = 4 - (len(data) % 4)
    if padding != 4:
        data += "=" * padding
    return base64.urlsafe_b64decode(data.encode("ascii"))


class TokenManager:
    """Manages creation and constant-time verification of signed capability tokens."""

    def __init__(self, active_key: str, previous_keys: list[str] | None = None, key_id: str = "v1"):
        self.active_key = active_key.encode("utf-8")
        self.key_id = key_id
        self.all_keys: dict[str, bytes] = {key_id: self.active_key}
        if previous_keys:
            for idx, k in enumerate(previous_keys):
                self.all_keys[f"prev_{idx}"] = k.encode("utf-8")

    def _sign(self, message: bytes, key: bytes) -> str:
        sig = hmac.new(key, message, hashlib.sha256).digest()
        return _urlsafe_b64encode(sig)

    def generate_token(self, payload: dict[str, Any]) -> str:
        """Serializes payload and creates signed capability token in form: kid.payload_b64.signature."""
        payload_bytes = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
        payload_b64 = _urlsafe_b64encode(payload_bytes)
        message = f"{self.key_id}.{payload_b64}".encode()
        sig = self._sign(message, self.active_key)
        return f"{self.key_id}.{payload_b64}.{sig}"

    def verify_token(self, token: str) -> dict[str, Any] | None:
        """Verifies signature against active or previous keys, returning decoded payload or None."""
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return None
            kid, payload_b64, signature = parts
            key = self.all_keys.get(kid)
            if not key:
                return None

            message = f"{kid}.{payload_b64}".encode()
            expected_sig = self._sign(message, key)
            if not hmac.compare_digest(signature, expected_sig):
                return None

            payload_bytes = _urlsafe_b64decode(payload_b64)
            payload = json.loads(payload_bytes.decode("utf-8"))
            return payload
        except Exception:
            return None

    def generate_open_token(self, recipient_id: str, tracked_email_id: str) -> str:
        """Generates capability token for 1x1 open pixel."""
        payload = {
            "type": "open",
            "rid": recipient_id,
            "eid": tracked_email_id,
            "iat": int(time.time()),
        }
        return self.generate_token(payload)

    def verify_open_token(self, token: str) -> dict[str, Any] | None:
        """Verifies open tracking token."""
        payload = self.verify_token(token)
        if payload and payload.get("type") == "open" and "rid" in payload and "eid" in payload:
            return payload
        return None

    def generate_click_token(self, recipient_id: str, destination_url: str) -> str:
        """Generates capability token cryptographically binding recipient to destination URL."""
        # Hash destination URL to bind it without bloating token length
        url_hash = hashlib.sha256(destination_url.encode("utf-8")).hexdigest()[:16]
        payload = {
            "type": "click",
            "rid": recipient_id,
            "uh": url_hash,
            "iat": int(time.time()),
        }
        return self.generate_token(payload)

    def verify_click_token(self, token: str, destination_url: str) -> str | None:
        """Verifies click token and binds it to the exact destination URL. Returns recipient_id or None."""
        payload = self.verify_token(token)
        if not payload or payload.get("type") != "click":
            return None
        expected_hash = hashlib.sha256(destination_url.encode("utf-8")).hexdigest()[:16]
        if not hmac.compare_digest(payload.get("uh", ""), expected_hash):
            return None
        return payload.get("rid")

    def generate_unsubscribe_token(self, email: str, user_id: str) -> str:
        """Generates token for 1-click unsubscribe."""
        payload = {
            "type": "unsub",
            "em": email,
            "uid": user_id,
            "iat": int(time.time()),
        }
        return self.generate_token(payload)

    def verify_unsubscribe_token(self, token: str) -> dict[str, Any] | None:
        """Verifies unsubscribe token."""
        payload = self.verify_token(token)
        if payload and payload.get("type") == "unsub":
            return payload
        return None


token_manager = TokenManager(
    active_key=settings.tracking_signing_key,
    previous_keys=settings.tracking_previous_keys,
)
