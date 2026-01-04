from __future__ import annotations

from order_service.application.unit_of_work import UnitOfWork
from order_service.domain.errors import ConflictError, NotFoundError
from order_service.domain.value_objects import ShippingAddress

from ._mapping import apply_domain_to_order_table, order_table_to_domain, order_table_to_read_model


def set_shipping_address(
    *,
    uow: UnitOfWork,
    customer_id: str,
    order_id: str,
    recipient_name: str,
    street: str,
    postal_code: str,
    city: str,
    country: str,
) -> dict:
    order_table = uow.orders.get(order_id)
    if order_table is None:
        raise NotFoundError(error_code="ORDER_NOT_FOUND", message="Order not found")

    if order_table.customer_id != customer_id:
        raise ConflictError(
            error_code="CUSTOMER_MISMATCH",
            message="customer_id does not match order owner",
        )

    domain = order_table_to_domain(order_table)
    domain.set_shipping_address(
        ShippingAddress(
            recipient_name=recipient_name,
            street=street,
            postal_code=postal_code,
            city=city,
            country=country,
        )
    )

    apply_domain_to_order_table(domain, order_table)
    uow.session.flush()
    return order_table_to_read_model(order_table)
