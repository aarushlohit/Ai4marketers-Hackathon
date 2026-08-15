"""User domain entity."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass
class UserEntity:
    id: UUID = field(default_factory=uuid4)
    tenant_id: UUID = field(default_factory=uuid4)
    email: str = ""
    first_name: str = ""
    last_name: str = ""
    role: str = "user"
    is_active: bool = True
    is_verified: bool = False
    mfa_enabled: bool = False
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    VALID_ROLES = ("super_admin", "admin", "manager", "user", "viewer")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def has_permission(self, required_role: str) -> bool:
        """Check if user role meets or exceeds required role level."""
        hierarchy = {r: i for i, r in enumerate(reversed(self.VALID_ROLES))}
        return hierarchy.get(self.role, 0) >= hierarchy.get(required_role, 0)

    def promote(self, new_role: str) -> None:
        if new_role not in self.VALID_ROLES:
            raise ValueError(f"Invalid role: {new_role}")
        self.role = new_role

    def deactivate(self) -> None:
        self.is_active = False

    def verify_email(self) -> None:
        self.is_verified = True
