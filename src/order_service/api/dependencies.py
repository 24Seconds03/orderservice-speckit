from __future__ import annotations

from fastapi import Header

from order_service.config import get_settings
from order_service.domain.errors import ConflictError


def require_callback_token(
    x_callback_token: str = Header(..., alias="X-Callback-Token"),
) -> None:
    settings = get_settings()
    if x_callback_token != settings.callback_token:
        raise ConflictError(
            error_code="INVALID_CALLBACK_TOKEN",
            message="Invalid callback token",
        )
