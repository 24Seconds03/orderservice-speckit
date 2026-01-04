from __future__ import annotations

from uuid import uuid4

from sqlalchemy.exc import IntegrityError

from order_service.adapters.models import OrderTable
from order_service.application.unit_of_work import UnitOfWork
from order_service.domain.order import Order

from ._mapping import apply_domain_to_order_table, order_table_to_read_model


def create_or_get_draft_order(*, uow: UnitOfWork, customer_id: str) -> dict:
    existing = uow.orders.get_draft_for_customer(customer_id)
    if existing is not None:
        return order_table_to_read_model(existing)

    domain = Order.create_draft(order_id=uuid4(), customer_id=customer_id)

    order_table = OrderTable(
        id=str(domain.order_id), customer_id=domain.customer_id, status=domain.status.value
    )
    apply_domain_to_order_table(domain, order_table)
    uow.orders.add(order_table)

    try:
        # Flush so uniqueness violations surface now (not at request end).
        uow.session.flush()
    except IntegrityError:
        uow.session.rollback()
        existing_after_race = uow.orders.get_draft_for_customer(customer_id)
        if existing_after_race is None:
            raise
        return order_table_to_read_model(existing_after_race)

    return order_table_to_read_model(order_table)
