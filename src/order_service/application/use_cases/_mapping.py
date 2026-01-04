from __future__ import annotations

import datetime as dt
from uuid import UUID

from order_service.adapters.models import OrderItemTable, OrderTable
from order_service.domain.order import Order
from order_service.domain.types import OrderStatus
from order_service.domain.value_objects import OrderItem, PriceSnapshot, ShippingAddress


def order_table_to_domain(order: OrderTable) -> Order:
    shipping_address = None
    if (
        order.shipping_recipient_name is not None
        and order.shipping_street is not None
        and order.shipping_postal_code is not None
        and order.shipping_city is not None
        and order.shipping_country is not None
    ):
        shipping_address = ShippingAddress(
            recipient_name=order.shipping_recipient_name,
            street=order.shipping_street,
            postal_code=order.shipping_postal_code,
            city=order.shipping_city,
            country=order.shipping_country,
        )

    return Order(
        order_id=UUID(order.id),
        customer_id=order.customer_id,
        status=OrderStatus(order.status),
        payment_reference=order.payment_reference,
        items=[
            OrderItem(
                product_id=item.product_id,
                product_name=item.product_name,
                quantity=item.quantity,
                price=PriceSnapshot(unit_price_cents=item.unit_price_cents, currency=item.currency),
            )
            for item in order.items
        ],
        shipping_address=shipping_address,
    )


def apply_domain_to_order_table(domain: Order, table: OrderTable) -> None:
    previous_status = table.status
    table.status = domain.status.value

    if (
        previous_status != table.status
        and table.status == OrderStatus.SUBMITTED.value
        and table.submitted_at is None
    ):
        table.submitted_at = dt.datetime.utcnow()

    if (
        previous_status != table.status
        and table.status == OrderStatus.PAID.value
        and table.paid_at is None
    ):
        table.paid_at = dt.datetime.utcnow()

    table.payment_reference = domain.payment_reference

    if domain.shipping_address is None:
        table.shipping_recipient_name = None
        table.shipping_street = None
        table.shipping_postal_code = None
        table.shipping_city = None
        table.shipping_country = None
    else:
        table.shipping_recipient_name = domain.shipping_address.recipient_name
        table.shipping_street = domain.shipping_address.street
        table.shipping_postal_code = domain.shipping_address.postal_code
        table.shipping_city = domain.shipping_address.city
        table.shipping_country = domain.shipping_address.country

    by_product_id = {item.product_id: item for item in domain.items}

    # Update existing
    for existing in list(table.items):
        domain_item = by_product_id.pop(existing.product_id, None)
        if domain_item is None:
            table.items.remove(existing)
            continue

        existing.quantity = domain_item.quantity
        existing.product_name = domain_item.product_name
        existing.unit_price_cents = domain_item.price.unit_price_cents
        existing.currency = domain_item.price.currency

    # Add new
    for domain_item in by_product_id.values():
        table.items.append(
            OrderItemTable(
                product_id=domain_item.product_id,
                product_name=domain_item.product_name,
                quantity=domain_item.quantity,
                unit_price_cents=domain_item.price.unit_price_cents,
                currency=domain_item.price.currency,
            )
        )


def order_table_to_read_model(order: OrderTable) -> dict:
    shipping_address = None
    if (
        order.shipping_recipient_name is not None
        and order.shipping_street is not None
        and order.shipping_postal_code is not None
        and order.shipping_city is not None
        and order.shipping_country is not None
    ):
        shipping_address = {
            "recipient_name": order.shipping_recipient_name,
            "street": order.shipping_street,
            "postal_code": order.shipping_postal_code,
            "city": order.shipping_city,
            "country": order.shipping_country,
        }

    return {
        "order_id": order.id,
        "customer_id": order.customer_id,
        "status": order.status,
        "items": [
            {
                "product_id": item.product_id,
                "product_name": item.product_name,
                "quantity": item.quantity,
                "price": {
                    "unit_price_cents": item.unit_price_cents,
                    "currency": item.currency,
                },
            }
            for item in order.items
        ],
        "shipping_address": shipping_address,
        "payment_reference": order.payment_reference,
    }
