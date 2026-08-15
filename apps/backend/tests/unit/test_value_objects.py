"""Unit tests for domain value objects."""

import pytest
from app.domain.value_objects.email import Email


class TestEmail:
    def test_valid_email(self):
        e = Email("user@example.com")
        assert str(e) == "user@example.com"

    def test_domain_extraction(self):
        e = Email("jane@company.org")
        assert e.domain() == "company.org"

    def test_invalid_email_raises(self):
        with pytest.raises(ValueError):
            Email("not-an-email")

    def test_missing_tld_raises(self):
        with pytest.raises(ValueError):
            Email("user@domain")

    def test_email_is_immutable(self):
        e = Email("test@test.com")
        with pytest.raises(Exception):
            e.value = "other@test.com"  # frozen dataclass

    def test_equality(self):
        assert Email("a@b.com") == Email("a@b.com")

    def test_inequality(self):
        assert Email("a@b.com") != Email("c@d.com")
