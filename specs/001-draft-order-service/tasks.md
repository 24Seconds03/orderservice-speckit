---

description: "Tasks for implementing the Draft Order Microservice"
---

# Tasks: Draft Order Microservice

**Input**: Design documents from `specs/001-draft-order-service/`
**Prerequisites**: `specs/001-draft-order-service/plan.md`, `specs/001-draft-order-service/spec.md`, `specs/001-draft-order-service/research.md`, `specs/001-draft-order-service/data-model.md`, `specs/001-draft-order-service/contracts/openapi.yaml`

**Tests**: REQUIRED (constitution). Include domain unit tests for invariants/transitions and API smoke tests covering the endpoints.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] T### [P?] [US?] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[US#]**: Which user story this task belongs to (`US1`, `US2`, `US3`)
- Every task includes an explicit file path.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and repository structure

- [ ] T001 Create package directories and markers in `src/order_service/__init__.py`
- [ ] T002 [P] Define runtime dependencies in `requirements.txt`
- [ ] T003 [P] Define dev tooling config in `pyproject.toml` (pytest + ruff)
- [ ] T004 [P] Add Docker build configuration in `Dockerfile` and `.dockerignore`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Implement settings/env loading in `src/order_service/config.py` (DATABASE_URL, CALLBACK_TOKEN)
- [ ] T006 [P] Add domain primitives in `src/order_service/domain/types.py` (UUID type alias, `OrderStatus` enum)
- [ ] T007 [P] Add domain exceptions in `src/order_service/domain/errors.py` (NotFound, Conflict, ValidationError)
- [ ] T008 Implement SQLAlchemy engine + session dependency in `src/order_service/adapters/db.py`
- [ ] T009 Define SQLAlchemy ORM tables in `src/order_service/adapters/models.py` (`orders`, `order_items`, `outbox_events`, indexes)
- [ ] T010 Implement repository interface + concrete SQLAlchemy repo in `src/order_service/adapters/order_repository.py`
- [ ] T011 Implement unit-of-work (transaction boundary) in `src/order_service/application/unit_of_work.py`
- [ ] T012 Implement API error mapping + handlers in `src/order_service/api/error_handlers.py` (404/409/422 shapes)
- [ ] T013 Create FastAPI app + router wiring in `src/order_service/api/main.py` (startup creates tables, registers handlers)
- [ ] T014 [P] Add shared test fixtures in `tests/conftest.py` (temporary SQLite DB, FastAPI `TestClient`)
- [ ] T015 [P] Add structured logging setup in `src/order_service/logging.py` (include `order_id` context)

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Build a shopping cart as a draft order (Priority: P1) MVP

**Goal**: Create/get a `DRAFT` order and add/remove items with price snapshot.

**Independent Test**: Create draft → add item → add same product increases qty → remove item → get order shows correct status/items.

### Tests for User Story 1

- [ ] T016 [P] [US1] Add domain tests for draft cart behavior in `tests/domain/test_order_cart.py`
- [ ] T017 [P] [US1] Add API smoke test for cart flow in `tests/api/test_us1_cart_smoke.py`

### Implementation for User Story 1

- [ ] T018 [US1] Implement value objects `PriceSnapshot` + `OrderItem` in `src/order_service/domain/value_objects.py`
- [ ] T019 [US1] Implement `Order` aggregate draft + item mutations in `src/order_service/domain/order.py` (add/remove/increase qty)
- [ ] T020 [US1] Implement create/get draft use-case in `src/order_service/application/use_cases/create_or_get_draft_order.py`
- [ ] T021 [US1] Implement add-item use-case in `src/order_service/application/use_cases/add_item_to_order.py`
- [ ] T022 [US1] Implement remove-item use-case in `src/order_service/application/use_cases/remove_item_from_order.py`
- [ ] T023 [US1] Implement get-order read-model use-case in `src/order_service/application/use_cases/get_order.py`
- [ ] T024 [US1] Implement order routes in `src/order_service/api/routes/orders.py` (`POST /customers/{customer_id}/orders/draft`, `GET /customers/{customer_id}/orders/{order_id}`)
- [ ] T025 [US1] Implement item routes + DTOs in `src/order_service/api/routes/order_items.py` (`POST /.../items`, `DELETE /.../items/{product_id}`)
- [ ] T026 [US1] Enforce “one DRAFT per customer” constraint in `src/order_service/adapters/models.py` (partial unique index) and handle conflicts in `src/order_service/application/use_cases/create_or_get_draft_order.py`

**Checkpoint**: US1 endpoints work and smoke test passes.

---

## Phase 4: User Story 2 - Provide shipping address and submit the order (Priority: P2)

**Goal**: Set a shipping address on a draft order and submit it (`DRAFT → SUBMITTED`), recording `OrderSubmitted` in the outbox.

**Independent Test**: Create draft → add item → set shipping address → submit → get order shows `SUBMITTED` and outbox contains `OrderSubmitted`.

### Tests for User Story 2

- [ ] T027 [P] [US2] Add domain tests for submit validation and transition in `tests/domain/test_order_submit.py`
- [ ] T028 [P] [US2] Add API smoke test for submit flow in `tests/api/test_us2_submit_smoke.py`

### Implementation for User Story 2

- [ ] T029 [US2] Implement `ShippingAddress` value object in `src/order_service/domain/value_objects.py`
- [ ] T030 [US2] Implement `submit()` transition + validation in `src/order_service/domain/order.py` (requires items + complete address)
- [ ] T031 [US2] Implement `OrderSubmitted` event in `src/order_service/domain/events.py`
- [ ] T032 [US2] Implement outbox recording helper in `src/order_service/adapters/outbox.py` (insert outbox row within transaction)
- [ ] T033 [US2] Implement set-address use-case in `src/order_service/application/use_cases/set_shipping_address.py`
- [ ] T034 [US2] Implement submit-order use-case in `src/order_service/application/use_cases/submit_order.py` (records outbox)
- [ ] T035 [US2] Implement shipping + submit routes in `src/order_service/api/routes/order_checkout.py` (`PUT /.../shipping-address`, `POST /.../submit`)
- [ ] T036 [US2] Enforce “no mutations after SUBMITTED” in `src/order_service/domain/order.py` and validate in `src/order_service/application/use_cases/add_item_to_order.py`

**Checkpoint**: US2 submit flow works and emits one `OrderSubmitted` outbox event.

---

## Phase 5: User Story 3 - Confirm payment via external callback (Priority: P3)

**Goal**: Accept external payment confirmation callback and transition `SUBMITTED → PAID` idempotently, recording `PaymentConfirmed` in the outbox.

**Independent Test**: Submit an order → confirm payment → order becomes `PAID` → repeat confirm payment with same reference does not create a second outbox event.

### Tests for User Story 3

- [ ] T037 [P] [US3] Add domain tests for confirm payment idempotency in `tests/domain/test_order_payment.py`
- [ ] T038 [P] [US3] Add API smoke test for payment callback in `tests/api/test_us3_payment_smoke.py`

### Implementation for User Story 3

- [ ] T039 [US3] Implement `PaymentConfirmed` event in `src/order_service/domain/events.py`
- [ ] T040 [US3] Implement `confirm_payment()` transition in `src/order_service/domain/order.py` (only SUBMITTED; idempotent on same reference)
- [ ] T041 [US3] Implement confirm-payment use-case in `src/order_service/application/use_cases/confirm_payment.py` (records outbox with unique `dedup_key`)
- [ ] T042 [US3] Add callback auth simulation in `src/order_service/api/dependencies.py` (validate `X-Callback-Token`)
- [ ] T043 [US3] Implement payment callback route in `src/order_service/api/routes/payments.py` (`POST /payments/confirmations`)
- [ ] T044 [US3] Add outbox dedup constraint in `src/order_service/adapters/models.py` (`outbox_events.dedup_key` unique) and enforce consistent `dedup_key` generation in `src/order_service/adapters/outbox.py`
- [ ] T045 [US3] Handle unknown order / invalid status errors in `src/order_service/api/error_handlers.py` for payment confirmations

**Checkpoint**: US3 callback is idempotent and emits exactly one `PaymentConfirmed` outbox event.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T046 [P] Ensure OpenAPI examples align with implementation in `specs/001-draft-order-service/contracts/openapi.yaml`
- [ ] T047 Add Docker run docs verification and env var notes in `specs/001-draft-order-service/quickstart.md`
- [ ] T048 Add repository-level smoke validation instructions in `doku.md` (link to `specs/001-draft-order-service/quickstart.md`)
- [ ] T049 [P] Add additional domain edge-case tests in `tests/domain/test_order_edge_cases.py` (wrong customer, remove missing item, submit empty)
- [ ] T050 Run formatting and lint configuration checks in `pyproject.toml` (ruff, pytest options)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies
- **Foundational (Phase 2)**: depends on Setup; BLOCKS all user stories
- **User Stories (Phase 3–5)**: depend on Foundational
- **Polish (Phase 6)**: depends on the desired user stories being complete

### User Story Dependencies

- **US1 (P1)**: depends only on Foundational
- **US2 (P2)**: depends on US1 (submission requires items and the order read model)
- **US3 (P3)**: depends on US2 (payment requires `SUBMITTED` order)

## Parallel Execution Examples

### Parallel Example: US1

```text
In parallel (different files):
- T016 tests/domain/test_order_cart.py
- T017 tests/api/test_us1_cart_smoke.py
- T018 src/order_service/domain/value_objects.py
```

### Parallel Example: US2

```text
In parallel (different files):
- T027 tests/domain/test_order_submit.py
- T028 tests/api/test_us2_submit_smoke.py
- T032 src/order_service/adapters/outbox.py
```

### Parallel Example: US3

```text
In parallel (different files):
- T037 tests/domain/test_order_payment.py
- T038 tests/api/test_us3_payment_smoke.py
- T042 src/order_service/api/dependencies.py
```

---

## Implementation Strategy

### MVP First (US1 only)

1. Complete Phase 1 (Setup) and Phase 2 (Foundational)
2. Complete Phase 3 (US1)
3. Validate US1 using `tests/domain/test_order_cart.py` and `tests/api/test_us1_cart_smoke.py`

### Incremental Delivery (US1 → US2 → US3)

- Add US2 and validate submit + outbox `OrderSubmitted`
- Add US3 and validate payment idempotency + outbox `PaymentConfirmed`

## Notes

- All domain invariants must live inside `src/order_service/domain/order.py` (single aggregate rule).
- API must return structured errors per constitution: `404` not found, `409` conflicts, `422` validation.
- Outbox must be written in the same transaction as state changes (`src/order_service/adapters/outbox.py`).
