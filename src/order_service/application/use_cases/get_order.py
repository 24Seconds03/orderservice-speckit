from __future__ import annotations

from order_service.application.unit_of_work import UnitOfWork
from order_service.domain.errors import ConflictError, NotFoundError

from ._mapping import order_table_to_read_model


def get_order(*, uow: UnitOfWork, customer_id: str, order_id: str) -> dict:
    order_table = uow.orders.get(order_id)
    if order_table is None:
        raise NotFoundError(error_code="ORDER_NOT_FOUND", message="Order not found")

    if order_table.customer_id != customer_id:
        raise ConflictError(
            error_code="CUSTOMER_MISMATCH",
            message="customer_id does not match order owner",
        )

    return order_table_to_read_model(order_table)
