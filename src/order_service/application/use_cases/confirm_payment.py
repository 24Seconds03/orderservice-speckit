from __future__ import annotations

from order_service.adapters.outbox import record_event
from order_service.application.unit_of_work import UnitOfWork
from order_service.domain.errors import NotFoundError

from ._mapping import apply_domain_to_order_table, order_table_to_domain, order_table_to_read_model


def confirm_payment(*, uow: UnitOfWork, order_id: str, payment_reference: str) -> dict:
    order_table = uow.orders.get(order_id)
    if order_table is None:
        raise NotFoundError(error_code="ORDER_NOT_FOUND", message="Order not found")

    domain = order_table_to_domain(order_table)
    event = domain.confirm_payment(payment_reference=payment_reference)

    apply_domain_to_order_table(domain, order_table)

    if event is not None:
        record_event(
            session=uow.session,
            event_type=event.event_type,
            aggregate_id=order_table.id,
            payload=event.payload,
            dedup_key=f"{event.event_type}:{order_table.id}",
        )

    uow.session.flush()
    return order_table_to_read_model(order_table)
