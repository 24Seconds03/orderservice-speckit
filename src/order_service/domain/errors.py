from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(eq=False)
class DomainError(Exception):
    error_code: str
    message: str
    details: dict[str, Any] | None = None

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.error_code}: {self.message}"


class NotFoundError(DomainError):
    pass


class ConflictError(DomainError):
    pass


class DomainValidationError(DomainError):
    pass
