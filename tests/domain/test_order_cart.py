from __future__ import annotations

from uuid import uuid4

import pytest

from order_service.domain.errors import ConflictError, DomainValidationError
from order_service.domain.order import Order
from order_service.domain.types import OrderStatus
from order_service.domain.value_objects import PriceSnapshot


def test_create_draft_starts_empty() -> None:
    order = Order.create_draft(order_id=uuid4(), customer_id="cust-1")

    assert order.status == OrderStatus.DRAFT
    assert order.items == []


def test_add_item_stores_price_snapshot() -> None:
    order = Order.create_draft(order_id=uuid4(), customer_id="cust-1")

    order.add_item(
        product_id="P1",
        quantity=2,
        product_name="Chair",
        price=PriceSnapshot(unit_price_cents=19999, currency="EUR"),
    )

    assert len(order.items) == 1
    assert order.items[0].product_id == "P1"
    assert order.items[0].quantity == 2
    assert order.items[0].price.unit_price_cents == 19999
    assert order.items[0].price.currency == "EUR"


def test_add_same_product_increases_quantity() -> None:
    order = Order.create_draft(order_id=uuid4(), customer_id="cust-1")

    order.add_item(
        product_id="P1",
        quantity=1,
        product_name=None,
        price=PriceSnapshot(unit_price_cents=19999, currency="EUR"),
    )
    order.add_item(
        product_id="P1",
        quantity=3,
        product_name=None,
        price=PriceSnapshot(unit_price_cents=19999, currency="EUR"),
    )

    assert len(order.items) == 1
    assert order.items[0].quantity == 4


def test_remove_item_removes_from_order() -> None:
    order = Order.create_draft(order_id=uuid4(), customer_id="cust-1")

    order.add_item(
        product_id="P1",
        quantity=1,
        product_name=None,
        price=PriceSnapshot(unit_price_cents=19999, currency="EUR"),
    )
    order.remove_item(product_id="P1")

    assert order.items == []


def test_cannot_mutate_items_after_submission() -> None:
    order = Order.create_draft(order_id=uuid4(), customer_id="cust-1")
    order.status = OrderStatus.SUBMITTED

    with pytest.raises(ConflictError):
        order.add_item(
            product_id="P1",
            quantity=1,
            product_name=None,
            price=PriceSnapshot(unit_price_cents=19999, currency="EUR"),
        )


def test_remove_missing_item_is_rejected() -> None:
    order = Order.create_draft(order_id=uuid4(), customer_id="cust-1")

    with pytest.raises(DomainValidationError):
        order.remove_item(product_id="missing")
