from __future__ import annotations

from uuid import UUID

from order_service.adapters.models import OrderItemTable, OrderTable
from order_service.domain.order import Order
from order_service.domain.types import OrderStatus
from order_service.domain.value_objects import OrderItem, PriceSnapshot


def order_table_to_domain(order: OrderTable) -> Order:
    return Order(
        order_id=UUID(order.id),
        customer_id=order.customer_id,
        status=OrderStatus(order.status),
        items=[
            OrderItem(
                product_id=item.product_id,
                product_name=item.product_name,
                quantity=item.quantity,
                price=PriceSnapshot(unit_price_cents=item.unit_price_cents, currency=item.currency),
            )
            for item in order.items
        ],
    )


def apply_domain_to_order_table(domain: Order, table: OrderTable) -> None:
    table.status = domain.status.value

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
        "shipping_address": None,
        "payment_reference": order.payment_reference,
    }
