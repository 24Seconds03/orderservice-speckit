from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from order_service.adapters.models import OrderTable
from order_service.domain.types import OrderStatus


class SqlAlchemyOrderRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, order_id: str) -> OrderTable | None:
        return self._session.get(OrderTable, order_id)

    def get_draft_for_customer(self, customer_id: str) -> OrderTable | None:
        stmt = select(OrderTable).where(
            OrderTable.customer_id == customer_id,
            OrderTable.status == OrderStatus.DRAFT.value,
        )
        return self._session.execute(stmt).scalar_one_or_none()

    def add(self, order: OrderTable) -> None:
        self._session.add(order)
