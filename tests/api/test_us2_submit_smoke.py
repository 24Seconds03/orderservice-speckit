from __future__ import annotations

import json

from sqlalchemy import select

from order_service.adapters.models import OutboxEventTable


def test_us2_submit_flow_smoke(client, db_session):
    create_resp = client.post("/customers/cust-1/orders/draft")
    assert create_resp.status_code == 200

    created = create_resp.json()
    order_id = created["order_id"]

    add_resp = client.post(
        f"/customers/cust-1/orders/{order_id}/items",
        json={
            "product_id": "P1",
            "product_name": "Chair",
            "quantity": 1,
            "unit_price_cents": 19999,
            "currency": "EUR",
        },
    )
    assert add_resp.status_code == 200

    set_shipping_resp = client.put(
        f"/customers/cust-1/orders/{order_id}/shipping-address",
        json={
            "recipient_name": "Ada Lovelace",
            "street": "Main St 1",
            "postal_code": "12345",
            "city": "Berlin",
            "country": "DE",
        },
    )
    assert set_shipping_resp.status_code == 200
    assert set_shipping_resp.json()["shipping_address"]["city"] == "Berlin"

    submit_resp = client.post(f"/customers/cust-1/orders/{order_id}/submit")
    assert submit_resp.status_code == 200
    assert submit_resp.json()["status"] == "SUBMITTED"

    get_resp = client.get(f"/customers/cust-1/orders/{order_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["status"] == "SUBMITTED"
    assert get_resp.json()["shipping_address"]["postal_code"] == "12345"

    events = db_session.execute(select(OutboxEventTable)).scalars().all()
    assert len(events) == 1
    assert events[0].event_type == "OrderSubmitted"

    payload = json.loads(events[0].payload)
    assert payload["order_id"] == order_id
    assert payload["customer_id"] == "cust-1"
