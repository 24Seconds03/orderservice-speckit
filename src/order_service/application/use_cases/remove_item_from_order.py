from __future__ import annotations

from order_service.application.unit_of_work import UnitOfWork
from order_service.domain.errors import ConflictError, NotFoundError

from ._mapping import apply_domain_to_order_table, order_table_to_domain, order_table_to_read_model


def remove_item_from_order(
    *, uow: UnitOfWork, customer_id: str, order_id: str, product_id: str
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
    domain.remove_item(product_id=product_id)

    apply_domain_to_order_table(domain, order_table)
    uow.session.flush()
    return order_table_to_read_model(order_table)
