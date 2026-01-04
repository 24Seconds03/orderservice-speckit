from __future__ import annotations

from uuid import uuid4

import pytest

from order_service.application.unit_of_work import UnitOfWork
from order_service.application.use_cases.add_item_to_order import add_item_to_order
from order_service.application.use_cases.create_or_get_draft_order import create_or_get_draft_order
from order_service.domain.errors import ConflictError, DomainValidationError
from order_service.domain.order import Order
from order_service.domain.value_objects import ShippingAddress


def test_wrong_customer_id_is_rejected(db_session) -> None:
    uow = UnitOfWork(db_session)
    created = create_or_get_draft_order(uow=uow, customer_id="cust-1")

    with pytest.raises(ConflictError) as exc:
        add_item_to_order(
            uow=uow,
            customer_id="cust-2",
            order_id=created["order_id"],
            product_id="P1",
            product_name=None,
            quantity=1,
            unit_price_cents=19999,
            currency="EUR",
        )

    assert exc.value.error_code == "CUSTOMER_MISMATCH"


def test_remove_missing_item_is_rejected() -> None:
    order = Order.create_draft(order_id=uuid4(), customer_id="cust-1")

    with pytest.raises(DomainValidationError) as exc:
        order.remove_item(product_id="missing")

    assert exc.value.error_code == "ITEM_NOT_FOUND"


def test_submit_empty_order_is_rejected() -> None:
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

    with pytest.raises(DomainValidationError) as exc:
        order.submit()

    assert exc.value.error_code == "EMPTY_ORDER"
