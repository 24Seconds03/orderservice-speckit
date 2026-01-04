# Research: Draft Order Microservice

This document resolves all design decisions required to proceed with Phase 1 design/contracts.

## SQLAlchemy + FastAPI integration

- **Decision**: Use synchronous SQLAlchemy 2.x (`Engine` + `Session`) with a request-scoped session dependency in FastAPI (one session + one transaction per request).
- **Rationale**: Lowest complexity for an MVP, strong library compatibility, and predictable correctness when following “one request = one session = one transaction”. Avoids common async ORM pitfalls (implicit IO / lazy loading surprises).
- **Alternatives considered**:
  - Async SQLAlchemy (`AsyncSession`): higher complexity; more strict rules around IO and relationship loading.
  - Commit-at-service-layer instead of request dependency: acceptable, but more boilerplate; MVP will standardize on a single pattern.

## One DRAFT per customer (enforcement)

- **Decision**: Enforce “at most one `DRAFT` order per customer” with a SQLite partial unique index on `customer_id` where `status = 'DRAFT'`, plus application-level logic that returns the existing draft.
- **Rationale**: DB-level constraint is the only robust protection against races (two concurrent create requests). Application-level pre-check enables the required behavior (“return existing draft”) and clearer errors, but the unique index is the correctness backstop.
- **Alternatives considered**:
  - App-level check only: not safe under concurrency.
  - Separate `draft_orders` table or `customer.current_draft_order_id`: stronger by construction but introduces additional domain concepts not required for MVP.

## Outbox pattern (no message broker)

- **Decision**: Implement a transactional outbox table `outbox_events` in SQLite and insert outbox rows in the same DB transaction as the order state change. For MVP, events are recorded durably and can be polled/inspected; optional publisher/relay can be added later.
- **Rationale**: Meets FR-011a durability requirement without introducing a broker. Transactional write guarantees “state + event” atomicity and prevents event loss on crashes.
- **Alternatives considered**:
  - Publish/log event after commit without outbox: risks event loss and violates FR-011a.
  - Full relay worker with locking/backoff: useful operationally, but can be postponed until a delivery mechanism is specified.

**Minimal outbox schema (MVP)**
- `id` (UUID, PK)
- `event_type` (e.g., `OrderSubmitted`, `PaymentConfirmed`)
- `aggregate_id` (order id)
- `payload` (JSON)
- `occurred_at` (timestamp)
- `created_at` (timestamp)
- `published_at` (nullable timestamp)
- `attempts` (int, default 0)
- `last_error` (nullable text)

## Payment confirmation idempotency

- **Decision**: Make `ConfirmPayment` idempotent by persisting a stable `payment_reference` and transitioning `SUBMITTED → PAID` exactly once; emit `PaymentConfirmed` only on the first successful transition. Use outbox deduplication via a unique `dedup_key` (e.g., `PaymentConfirmed:{order_id}` or `PaymentConfirmed:{payment_reference}`).
- **Rationale**: Prevents duplicate `PaymentConfirmed` events even with retries or concurrent callbacks by ensuring only one transaction can create the outbox event for the same order/payment.
- **Alternatives considered**:
  - Idempotency only in application memory: unsafe with concurrency and restarts.
  - Provider delivery-id (“webhook event id”) dedupe only: useful but not always stable across retries; keep optional.

## Event payload shape (minimum)

- **Decision**: Keep domain event payloads minimal and stable:
  - `OrderSubmitted`: `{ "order_id": ..., "customer_id": ... }`
  - `PaymentConfirmed`: `{ "order_id": ..., "payment_reference": ... }`
- **Rationale**: Aligns with spec minimums while keeping contracts stable; additional fields can be versioned later via `schema_version` if needed.
- **Alternatives considered**:
  - Include full order snapshot in event: higher coupling and larger payloads; unnecessary for MVP.
