from __future__ import annotations

import datetime as dt

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from order_service.domain.types import OrderStatus


class Base(DeclarativeBase):
    pass


class OrderTable(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    customer_id: Mapped[str] = mapped_column(String, index=True)
    status: Mapped[str] = mapped_column(String, index=True, default=OrderStatus.DRAFT.value)

    shipping_recipient_name: Mapped[str | None] = mapped_column(String, nullable=True)
    shipping_street: Mapped[str | None] = mapped_column(String, nullable=True)
    shipping_postal_code: Mapped[str | None] = mapped_column(String, nullable=True)
    shipping_city: Mapped[str | None] = mapped_column(String, nullable=True)
    shipping_country: Mapped[str | None] = mapped_column(String, nullable=True)

    payment_reference: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=lambda: dt.datetime.utcnow())
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime,
        default=lambda: dt.datetime.utcnow(),
        onupdate=lambda: dt.datetime.utcnow(),
    )
    submitted_at: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)
    paid_at: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)

    items: Mapped[list[OrderItemTable]] = relationship(
        "OrderItemTable",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


Index(
    "uq_orders_customer_draft",
    OrderTable.customer_id,
    unique=True,
    sqlite_where=(OrderTable.status == OrderStatus.DRAFT.value),
)


class OrderItemTable(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), index=True)

    product_id: Mapped[str] = mapped_column(String)
    product_name: Mapped[str | None] = mapped_column(String, nullable=True)

    quantity: Mapped[int] = mapped_column(Integer)
    unit_price_cents: Mapped[int] = mapped_column(Integer)
    currency: Mapped[str] = mapped_column(String)

    order: Mapped[OrderTable] = relationship("OrderTable", back_populates="items")


Index(
    "uq_order_items_order_product", OrderItemTable.order_id, OrderItemTable.product_id, unique=True
)


class OutboxEventTable(Base):
    __tablename__ = "outbox_events"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    event_type: Mapped[str] = mapped_column(String, index=True)
    aggregate_id: Mapped[str] = mapped_column(String, index=True)
    dedup_key: Mapped[str] = mapped_column(String, unique=True)

    payload: Mapped[str] = mapped_column(Text)

    occurred_at: Mapped[dt.datetime] = mapped_column(DateTime, default=lambda: dt.datetime.utcnow())
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=lambda: dt.datetime.utcnow())
    published_at: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)

    attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
