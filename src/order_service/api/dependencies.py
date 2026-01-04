from __future__ import annotations

from fastapi import Header, HTTPException, status

from order_service.config import get_settings


def require_callback_token(
    x_callback_token: str = Header(..., alias="X-Callback-Token"),
) -> None:
    settings = get_settings()
    if x_callback_token != settings.callback_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid callback token",
        )
