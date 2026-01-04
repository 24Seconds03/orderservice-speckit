# Data Model: Draft Order Microservice

This feature uses exactly one aggregate: `Order`.

## Aggregate: Order

### Order (domain)

**Identity**
- `order_id` (UUID)

**Ownership**
- `customer_id` (string; treated as opaque identifier provided upstream)

**Lifecycle**
- `status` (enum): `DRAFT` → `SUBMITTED` → `PAID` (strict state machine)
- `submitted_at` (timestamp, nullable)
- `paid_at` (timestamp, nullable)

**Shipping address (value object; editable only in `DRAFT`)**
- `shipping_recipient_name` (string, nullable)
- `shipping_street` (string, nullable)
- `shipping_postal_code` (string, nullable)
- `shipping_city` (string, nullable)
- `shipping_country` (string, nullable)

**Payment confirmation (external callback)**
- `payment_reference` (string, nullable; stable provider reference persisted on first confirmation)

**Audit**
- `created_at` (timestamp)
- `updated_at` (timestamp)

### OrderItem (entity inside Order aggregate)

Represents one product line in an order. `Order` is the aggregate root.

- `order_item_id` (UUID) OR surrogate integer (implementation choice)
- `order_id` (FK to orders)
- `product_id` (string)
- `product_name` (string, nullable; optional display snapshot)
- `quantity` (int, > 0)

**Price snapshot (captured at add-time; never recomputed)**
- `unit_price_cents` (int)
- `currency` (string, ISO-4217-like; e.g., `EUR`)

**Constraints**
- Unique: (`order_id`, `product_id`) to prevent duplicate lines.

## Domain Events (recorded via outbox)

### OrderSubmitted

Emitted when an order transitions `DRAFT → SUBMITTED`.

Minimum payload:
- `order_id`
- `customer_id`

### PaymentConfirmed

Emitted when an order transitions `SUBMITTED → PAID`.

Minimum payload:
- `order_id`
- `payment_reference`

## Persistence Tables (SQLite via SQLAlchemy)

### `orders`

- `id` (PK, UUID as string)
- `customer_id`
- `status`
- shipping address columns (nullable)
- `payment_reference` (nullable)
- `created_at`, `updated_at`, `submitted_at`, `paid_at`

**Indexes/Constraints**
- Partial unique index: `UNIQUE(customer_id) WHERE status = 'DRAFT'` (enforces at most one draft per customer)

### `order_items`

- `id` (PK)
- `order_id` (FK)
- `product_id`
- `product_name` (nullable)
- `quantity`
- `unit_price_cents`
- `currency`

**Indexes/Constraints**
- Unique index: (`order_id`, `product_id`)

### `outbox_events`

Transactional outbox for durable domain event recording.

- `id` (PK, UUID)
- `event_type` (string)
- `aggregate_id` (string; order id)
- `dedup_key` (string; unique)
- `payload` (JSON/text)
- `occurred_at` (timestamp)
- `created_at` (timestamp)
- `published_at` (nullable timestamp)
- `attempts` (int)
- `last_error` (nullable text)

**Indexes/Constraints**
- Unique: `dedup_key` (prevents duplicate emissions for idempotent commands)
- Index: `published_at` (or `(published_at, created_at)`)

## Validation Rules (from spec)

- Only `DRAFT` orders can be modified (items, shipping address).
- Submit requires:
  - `status == DRAFT`
  - at least one item exists
  - shipping address is complete (recipient name, street, postal code, city, country)
- Confirm payment requires:
  - `status == SUBMITTED`
  - idempotent behavior:
    - if already `PAID` with same `payment_reference`, return success and do not emit a new outbox event
    - if already `PAID` with different `payment_reference`, treat as conflict (HTTP 409)
