from __future__ import annotations


def test_us1_cart_flow_smoke(client):
    create_resp = client.post("/customers/cust-1/orders/draft")
    assert create_resp.status_code == 200

    created = create_resp.json()
    order_id = created["order_id"]
    assert created["customer_id"] == "cust-1"
    assert created["status"] == "DRAFT"
    assert created["items"] == []

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
    assert add_resp.json()["items"][0]["quantity"] == 1

    add_again_resp = client.post(
        f"/customers/cust-1/orders/{order_id}/items",
        json={
            "product_id": "P1",
            "product_name": "Chair",
            "quantity": 2,
            "unit_price_cents": 19999,
            "currency": "EUR",
        },
    )
    assert add_again_resp.status_code == 200
    assert add_again_resp.json()["items"][0]["quantity"] == 3

    get_resp = client.get(f"/customers/cust-1/orders/{order_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["items"][0]["quantity"] == 3

    delete_resp = client.delete(f"/customers/cust-1/orders/{order_id}/items/P1")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["items"] == []
