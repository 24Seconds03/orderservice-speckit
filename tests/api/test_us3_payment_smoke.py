from __future__ import annotations

import json

from sqlalchemy import select

from order_service.adapters.models import OutboxEventTable


def test_us3_payment_callback_smoke(client, db_session):
    create_resp = client.post("/customers/cust-1/orders/draft")
    assert create_resp.status_code == 200
    order_id = create_resp.json()["order_id"]

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

    submit_resp = client.post(f"/customers/cust-1/orders/{order_id}/submit")
    assert submit_resp.status_code == 200
    assert submit_resp.json()["status"] == "SUBMITTED"

    confirm_resp = client.post(
        "/payments/confirmations",
        headers={"X-Callback-Token": "dev-token"},
        json={"order_id": order_id, "payment_reference": "pay-123"},
    )
    assert confirm_resp.status_code == 200
    assert confirm_resp.json()["status"] == "PAID"
    assert confirm_resp.json()["payment_reference"] == "pay-123"

    confirm_again_resp = client.post(
        "/payments/confirmations",
        headers={"X-Callback-Token": "dev-token"},
        json={"order_id": order_id, "payment_reference": "pay-123"},
    )
    assert confirm_again_resp.status_code == 200
    assert confirm_again_resp.json()["status"] == "PAID"

    events = db_session.execute(select(OutboxEventTable)).scalars().all()
    assert len(events) == 2
    assert len([evt for evt in events if evt.event_type == "PaymentConfirmed"]) == 1

    payment_event = [evt for evt in events if evt.event_type == "PaymentConfirmed"][0]
    payload = json.loads(payment_event.payload)
    assert payload["order_id"] == order_id
    assert payload["payment_reference"] == "pay-123"


def test_us3_payment_unknown_order_returns_404(client):
    resp = client.post(
        "/payments/confirmations",
        headers={"X-Callback-Token": "dev-token"},
        json={"order_id": "missing", "payment_reference": "pay-123"},
    )

    assert resp.status_code == 404
