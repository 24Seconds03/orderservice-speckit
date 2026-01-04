from __future__ import annotations

from uuid import uuid4

import pytest

from order_service.domain.errors import ConflictError
from order_service.domain.order import Order
from order_service.domain.types import OrderStatus
from order_service.domain.value_objects import PriceSnapshot, ShippingAddress


def _submitted_order() -> Order:
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
    return order


def test_confirm_payment_transitions_to_paid() -> None:
    order = _submitted_order()

    event = order.confirm_payment(payment_reference="pay-123")

    assert order.status == OrderStatus.PAID
    assert order.payment_reference == "pay-123"
    assert event is not None
    assert event.event_type == "PaymentConfirmed"


def test_confirm_payment_is_idempotent_for_same_reference() -> None:
    order = _submitted_order()
    order.confirm_payment(payment_reference="pay-123")

    event = order.confirm_payment(payment_reference="pay-123")

    assert order.status == OrderStatus.PAID
    assert event is None


def test_confirm_payment_rejects_different_reference_after_paid() -> None:
    order = _submitted_order()
    order.confirm_payment(payment_reference="pay-123")

    with pytest.raises(ConflictError):
        order.confirm_payment(payment_reference="pay-999")


def test_confirm_payment_requires_submitted() -> None:
    order = Order.create_draft(order_id=uuid4(), customer_id="cust-1")

    with pytest.raises(ConflictError):
        order.confirm_payment(payment_reference="pay-123")
