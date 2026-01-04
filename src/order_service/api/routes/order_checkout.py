from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from order_service.adapters.db import get_session
from order_service.api.routes.orders import OrderReadModelDto, ShippingAddressDto
from order_service.application.unit_of_work import UnitOfWork
from order_service.application.use_cases.set_shipping_address import set_shipping_address
from order_service.application.use_cases.submit_order import submit_order

router = APIRouter(tags=["order-checkout"])


@router.put(
    "/customers/{customer_id}/orders/{order_id}/shipping-address",
    response_model=OrderReadModelDto,
)
def set_shipping_address_route(
    customer_id: str,
    order_id: str,
    body: ShippingAddressDto,
    session: Session = Depends(get_session),  # noqa: B008
) -> dict:
    uow = UnitOfWork(session)
    return set_shipping_address(
        uow=uow,
        customer_id=customer_id,
        order_id=order_id,
        recipient_name=body.recipient_name,
        street=body.street,
        postal_code=body.postal_code,
        city=body.city,
        country=body.country,
    )


@router.post(
    "/customers/{customer_id}/orders/{order_id}/submit",
    response_model=OrderReadModelDto,
)
def submit_order_route(
    customer_id: str,
    order_id: str,
    session: Session = Depends(get_session),  # noqa: B008
) -> dict:
    uow = UnitOfWork(session)
    return submit_order(uow=uow, customer_id=customer_id, order_id=order_id)
