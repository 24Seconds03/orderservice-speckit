from __future__ import annotations

from order_service.adapters.outbox import record_event
from order_service.application.unit_of_work import UnitOfWork
from order_service.domain.errors import ConflictError, NotFoundError

from ._mapping import apply_domain_to_order_table, order_table_to_domain, order_table_to_read_model


def submit_order(*, uow: UnitOfWork, customer_id: str, order_id: str) -> dict:
    order_table = uow.orders.get(order_id)
    if order_table is None:
        raise NotFoundError(error_code="ORDER_NOT_FOUND", message="Order not found")

    if order_table.customer_id != customer_id:
        raise ConflictError(
            error_code="CUSTOMER_MISMATCH",
            message="customer_id does not match order owner",
        )

    domain = order_table_to_domain(order_table)
    event = domain.submit()

    apply_domain_to_order_table(domain, order_table)
    record_event(
        session=uow.session,
        event_type=event.event_type,
        aggregate_id=order_table.id,
        payload=event.payload,
    )

    uow.session.flush()
    return order_table_to_read_model(order_table)
