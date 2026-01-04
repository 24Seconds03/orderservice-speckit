# Quickstart: order-service (MVP)

This quickstart describes how the implemented service is expected to be run and tested once the tasks in this feature are executed.

## Local dev (Python)

### Prereqs
- Python 3.12

### Install

```bash
python -m venv .venv
# activate venv (platform-specific)
pip install -r requirements.txt
```

### Run

```bash
# Uses SQLite file DB by default
uvicorn order_service.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Run tests

```bash
pytest -q
```

## Docker

### Build image

```bash
docker build -t order-service:dev .
```

### Run container (SQLite file persisted)

```bash
docker run --rm -p 8000:8000 \
  -e DATABASE_URL="sqlite:////data/orders.db" \
  -e CALLBACK_TOKEN="dev-token" \
  -v order_service_data:/data \
  order-service:dev
```

- The SQLite DB file is stored at `/data/orders.db`.
- `CALLBACK_TOKEN` simulates a trusted upstream for `POST /payments/confirmations` via the `X-Callback-Token` header.

### Smoke test (manual)

1) Create draft:
```bash
curl -X POST http://localhost:8000/customers/cust-1/orders/draft
```

2) Add item:
```bash
curl -X POST http://localhost:8000/customers/cust-1/orders/<order_id>/items \
  -H "Content-Type: application/json" \
  -d '{"product_id":"P1","quantity":1,"unit_price":"199.99","currency":"EUR"}'
```

3) Set shipping address:
```bash
curl -X PUT http://localhost:8000/customers/cust-1/orders/<order_id>/shipping-address \
  -H "Content-Type: application/json" \
  -d '{"recipient_name":"Ada Lovelace","street":"Main St 1","postal_code":"12345","city":"Berlin","country":"DE"}'
```

4) Submit:
```bash
curl -X POST http://localhost:8000/customers/cust-1/orders/<order_id>/submit
```

5) Confirm payment (idempotent):
```bash
curl -X POST http://localhost:8000/payments/confirmations \
  -H "Content-Type: application/json" \
  -H "X-Callback-Token: dev-token" \
  -d '{"order_id":"<order_id>","payment_reference":"pay-123"}'
```
