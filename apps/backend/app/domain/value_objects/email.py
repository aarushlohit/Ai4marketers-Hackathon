"""Email value object — immutable, self-validating."""

import re
from dataclasses import dataclass

_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        if not _EMAIL_RE.match(self.value):
            raise ValueError(f"Invalid email address: {self.value!r}")

    def domain(self) -> str:
        return self.value.split("@")[1]

    def __str__(self) -> str:
        return self.value
