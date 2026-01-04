from __future__ import annotations

from sqlalchemy.orm import Session

from order_service.adapters.order_repository import SqlAlchemyOrderRepository


class UnitOfWork:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.orders = SqlAlchemyOrderRepository(session)

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
