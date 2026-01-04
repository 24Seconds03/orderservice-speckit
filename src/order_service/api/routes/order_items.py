from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from order_service.adapters.db import get_session
from order_service.application.unit_of_work import UnitOfWork
from order_service.application.use_cases.add_item_to_order import add_item_to_order
from order_service.application.use_cases.remove_item_from_order import remove_item_from_order

from .orders import OrderReadModelDto


class AddItemRequestDto(BaseModel):
    product_id: str
    product_name: str | None = None
    quantity: int
    unit_price_cents: int
    currency: str


router = APIRouter(tags=["order-items"])


@router.post(
    "/customers/{customer_id}/orders/{order_id}/items",
    response_model=OrderReadModelDto,
)
def add_item_route(
    customer_id: str,
    order_id: str,
    body: AddItemRequestDto,
    session: Session = Depends(get_session),
) -> dict:
    uow = UnitOfWork(session)
    return add_item_to_order(
        uow=uow,
        customer_id=customer_id,
        order_id=order_id,
        product_id=body.product_id,
        product_name=body.product_name,
        quantity=body.quantity,
        unit_price_cents=body.unit_price_cents,
        currency=body.currency,
    )


@router.delete(
    "/customers/{customer_id}/orders/{order_id}/items/{product_id}",
    response_model=OrderReadModelDto,
)
def remove_item_route(
    customer_id: str,
    order_id: str,
    product_id: str,
    session: Session = Depends(get_session),
) -> dict:
    uow = UnitOfWork(session)
    return remove_item_from_order(
        uow=uow,
        customer_id=customer_id,
        order_id=order_id,
        product_id=product_id,
    )
