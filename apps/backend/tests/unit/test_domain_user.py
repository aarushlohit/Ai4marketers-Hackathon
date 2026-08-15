"""Unit tests for the User domain entity."""

import pytest
from app.domain.entities.user import UserEntity


class TestUserEntity:
    def test_full_name(self):
        u = UserEntity(first_name="John", last_name="Doe")
        assert u.full_name == "John Doe"

    def test_has_permission_same_role(self):
        u = UserEntity(role="manager")
        assert u.has_permission("manager") is True

    def test_has_permission_lower_role(self):
        u = UserEntity(role="admin")
        assert u.has_permission("user") is True

    def test_has_permission_higher_role_denied(self):
        u = UserEntity(role="user")
        assert u.has_permission("admin") is False

    def test_super_admin_has_all_permissions(self):
        u = UserEntity(role="super_admin")
        for role in UserEntity.VALID_ROLES:
            assert u.has_permission(role) is True

    def test_promote_valid_role(self):
        u = UserEntity(role="user")
        u.promote("manager")
        assert u.role == "manager"

    def test_promote_invalid_role_raises(self):
        u = UserEntity(role="user")
        with pytest.raises(ValueError):
            u.promote("god_mode")

    def test_deactivate(self):
        u = UserEntity(is_active=True)
        u.deactivate()
        assert u.is_active is False

    def test_verify_email(self):
        u = UserEntity(is_verified=False)
        u.verify_email()
        assert u.is_verified is True
