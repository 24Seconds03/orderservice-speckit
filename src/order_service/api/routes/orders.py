from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from order_service.adapters.db import get_session
from order_service.application.unit_of_work import UnitOfWork
from order_service.application.use_cases.create_or_get_draft_order import create_or_get_draft_order
from order_service.application.use_cases.get_order import get_order


class MoneySnapshotDto(BaseModel):
    unit_price_cents: int
    currency: str


class OrderItemDto(BaseModel):
    product_id: str
    product_name: str | None = None
    quantity: int
    price: MoneySnapshotDto


class ShippingAddressDto(BaseModel):
    recipient_name: str
    street: str
    postal_code: str
    city: str
    country: str


class OrderReadModelDto(BaseModel):
    order_id: str
    customer_id: str
    status: str
    items: list[OrderItemDto]
    shipping_address: ShippingAddressDto | None = None
    payment_reference: str | None = None


router = APIRouter(tags=["orders"])


@router.post("/customers/{customer_id}/orders/draft", response_model=OrderReadModelDto)
def create_or_get_draft(customer_id: str, session: Session = Depends(get_session)) -> dict:
    uow = UnitOfWork(session)
    return create_or_get_draft_order(uow=uow, customer_id=customer_id)


@router.get("/customers/{customer_id}/orders/{order_id}", response_model=OrderReadModelDto)
def get_order_route(
    customer_id: str, order_id: str, session: Session = Depends(get_session)
) -> dict:
    uow = UnitOfWork(session)
    return get_order(uow=uow, customer_id=customer_id, order_id=order_id)
