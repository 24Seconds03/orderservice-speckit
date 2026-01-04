from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from order_service.adapters.db import get_session
from order_service.api.dependencies import require_callback_token
from order_service.api.routes.orders import OrderReadModelDto
from order_service.application.unit_of_work import UnitOfWork
from order_service.application.use_cases.confirm_payment import confirm_payment


class ConfirmPaymentRequestDto(BaseModel):
    order_id: str
    payment_reference: str


router = APIRouter(tags=["payments"])


@router.post(
    "/payments/confirmations",
    response_model=OrderReadModelDto,
    dependencies=[Depends(require_callback_token)],
)
def confirm_payment_route(
    body: ConfirmPaymentRequestDto,
    session: Session = Depends(get_session),  # noqa: B008
) -> dict:
    uow = UnitOfWork(session)
    return confirm_payment(
        uow=uow, order_id=body.order_id, payment_reference=body.payment_reference
    )
