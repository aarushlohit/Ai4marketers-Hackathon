"""Unit tests for JWT token creation and password hashing."""

import pytest
from uuid import uuid4
from jose import JWTError

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_is_not_plaintext(self):
        hashed = hash_password("mysecret")
        assert hashed != "mysecret"

    def test_verify_correct_password(self):
        hashed = hash_password("correct")
        assert verify_password("correct", hashed) is True

    def test_verify_wrong_password(self):
        hashed = hash_password("correct")
        assert verify_password("wrong", hashed) is False

    def test_two_hashes_differ(self):
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2  # bcrypt uses random salt


class TestJWTTokens:
    def setup_method(self):
        self.user_id = uuid4()
        self.tenant_id = uuid4()

    def test_access_token_roundtrip(self):
        token = create_access_token(self.user_id, self.tenant_id, "admin")
        payload = decode_token(token)
        assert payload["sub"] == str(self.user_id)
        assert payload["tenant_id"] == str(self.tenant_id)
        assert payload["role"] == "admin"
        assert payload["type"] == "access"

    def test_refresh_token_type(self):
        token = create_refresh_token(self.user_id, self.tenant_id)
        payload = decode_token(token)
        assert payload["type"] == "refresh"

    def test_tampered_token_raises(self):
        token = create_access_token(self.user_id, self.tenant_id, "user")
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(JWTError):
            decode_token(tampered)

    def test_access_token_contains_tenant(self):
        token = create_access_token(self.user_id, self.tenant_id, "viewer")
        payload = decode_token(token)
        assert payload["tenant_id"] == str(self.tenant_id)
