from __future__ import annotations

from uuid import uuid4

import pytest

from order_service.domain.errors import DomainValidationError
from order_service.domain.order import Order
from order_service.domain.types import OrderStatus
from order_service.domain.value_objects import PriceSnapshot, ShippingAddress


def test_submit_requires_items() -> None:
    order = Order.create_draft(order_id=uuid4(), customer_id="cust-1")
    order.set_shipping_address(
        ShippingAddress(
            recipient_name="Ada Lovelace",
            street="Main St 1",
            postal_code="12345",
            city="Berlin",
            country="DE",
        )
    )

    with pytest.raises(DomainValidationError):
        order.submit()


def test_submit_requires_complete_shipping_address() -> None:
    order = Order.create_draft(order_id=uuid4(), customer_id="cust-1")
    order.add_item(
        product_id="P1",
        quantity=1,
        product_name=None,
        price=PriceSnapshot(unit_price_cents=19999, currency="EUR"),
    )

    with pytest.raises(DomainValidationError):
        order.submit()


def test_submit_transitions_to_submitted() -> None:
    order = Order.create_draft(order_id=uuid4(), customer_id="cust-1")
    order.add_item(
        product_id="P1",
        quantity=1,
        product_name=None,
        price=PriceSnapshot(unit_price_cents=19999, currency="EUR"),
    )
    order.set_shipping_address(
        ShippingAddress(
            recipient_name="Ada Lovelace",
            street="Main St 1",
            postal_code="12345",
            city="Berlin",
            country="DE",
        )
    )

    order.submit()

    assert order.status == OrderStatus.SUBMITTED
