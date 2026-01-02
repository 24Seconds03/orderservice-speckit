<!--
Sync Impact Report
- Version change: template → 1.0.0
- Modified principles:
  - Template placeholder principle 1 → Domain-First DDD (Single Aggregate: Order)
  - Template placeholder principle 2 → Explicit Order Lifecycle State Machine
  - Template placeholder principle 3 → Tested Domain Rules (NON-NEGOTIABLE)
  - Template placeholder principle 4 → Stable HTTP Contract + Clear Errors
  - Template placeholder principle 5 → Operational Simplicity & Observability
- Added sections:
  - Architecture & Technology Constraints
  - Development Workflow & Quality Gates
- Removed sections: None
- Templates requiring updates:
  - ✅ .specify/templates/plan-template.md
  - ✅ .specify/templates/spec-template.md (no changes required)
  - ✅ .specify/templates/tasks-template.md
  - ⚠ .specify/templates/commands/*.md (directory missing; plan-template references it)
- Deferred TODOs:
  - TODO(RATIFICATION_DATE): original adoption date unknown
-->

# order-service Constitution

## Core Principles

### Domain-First DDD (Single Aggregate: Order)
The `order-service` MUST implement exactly one aggregate: `Order`.

Non-negotiable rules:
- All business invariants MUST be enforced inside the `Order` aggregate boundary.
- No other aggregates (e.g., `Customer`, `Product`, `Payment`) may be introduced in this service.
- Other concerns (API, persistence, payment stub, event publishing) MUST adapt to the domain model,
  not the other way around.

Rationale: A single bounded context with one aggregate keeps the MVP focused and maintainable.

### Ubiquitous Language (Consistent Terms)
- Code identifiers MUST be in English (commands/events/entities).
- Documentation MAY be German, but MUST reference the exact English identifiers.
- Terms like `Order`, `OrderItem`, `DRAFT`, `SUBMITTED`, `PAID`, `OrderSubmitted`, `PaymentConfirmed` MUST be used consistently across specs, code, tests.

### Explicit Order Lifecycle State Machine
The `Order.status` lifecycle is a strict state machine: `DRAFT` → `SUBMITTED` → `PAID`.

Non-negotiable rules:
- Only the allowed transitions MAY occur; skipping or reversing states is forbidden.
- Mutations to cart contents and shipping address MUST only be allowed while `status == DRAFT`.
- `SubmitOrder` MUST validate:
  - at least one item exists
  - `shipping_address` is set
  - `status == DRAFT`
- `ConfirmPayment` MUST only be allowed when `status == SUBMITTED`.

Rationale: A strict lifecycle prevents inconsistent orders and makes the API predictable.

### Tested Domain Rules (NON-NEGOTIABLE)
Changes to domain behavior MUST be accompanied by automated tests.

Non-negotiable rules:
- All invariants and state transitions MUST have `pytest` unit tests at the domain layer.
- Any new/changed HTTP endpoint MUST have at least an API smoke test (e.g., FastAPI `TestClient`).
- If a test is intentionally omitted, the feature spec MUST explicitly waive it and explain why.

Rationale: The order lifecycle is the business core; tests protect correctness while iterating quickly.

### Stable HTTP Contract + Clear Errors
The service MUST expose a stable, well-defined HTTP contract.

Non-negotiable rules:
- Input validation MUST be explicit and return consistent, structured error responses.
- The API MUST use appropriate HTTP status codes; internal exceptions MUST NOT leak to clients.
- Contracts that clients depend on (endpoints, request/response shapes) MUST be documented in the spec (e.g. OpenAPI examples in spec.md or a dedicated contracts section)

Cases:
- `404` when order not found
- `409` when lifecycle/invariant violation (e.g. add item after SUBMITTED)
- `422` for validation errors (schema)

Rationale: A microservice boundary lives or dies by its external contract.

### Operational Simplicity & Observability
The MVP MUST prioritize simple operations and debuggability.

Non-negotiable rules:
- The baseline stack is Python 3.12, FastAPI, SQLAlchemy, SQLite (file-based in Docker) for MVP.
- Logging MUST be structured and include enough context to trace an order through its lifecycle
  (e.g., `order_id`, command name, resulting status).
- Prefer the simplest design that satisfies requirements (YAGNI). Introduce async/event-bus
  complexity only with explicit requirements.
- Payment is modeled as an external system stub; `PaymentConfirmed` is an incoming external callback/event and does not introduce a `Payment` aggregate.
- Domain events MUST be persisted (outbox table) before being published/logged (no broker required).

Rationale: Simple, observable systems ship faster and are easier to support.

## Architecture & Technology Constraints

- **Language**: Python 3.12.
- **Service type**: Single microservice named `order-service`.
- **Domain model**: DDD with exactly one aggregate (`Order`).
- **Persistence (MVP)**: SQLite via SQLAlchemy.
- **API (MVP)**: FastAPI HTTP endpoints.
- **External dependencies**: Payment integration is a stub/simulation unless explicitly expanded.
- **Out of scope for MVP**: product catalog, inventory, user/auth, shipping, returns.

## Development Workflow & Quality Gates

- Work is spec-driven: feature changes MUST be captured in `specs/<feature>/spec.md`, planned in
  `specs/<feature>/plan.md`, and executed via `specs/<feature>/tasks.md`.
- Every plan MUST include a “Constitution Check” section that verifies compliance with these
  principles before implementation begins.
- Code review MUST include a brief checklist-style confirmation that:
  - the single-aggregate rule is preserved
  - lifecycle invariants remain enforced
  - relevant tests were added/updated
  - API contract changes are documented

## Governance

- This constitution supersedes other practices and templates.
- Amendments MUST be made via a documented change (e.g., PR) that includes rationale and scope.
- Constitution versioning follows semantic versioning:
  - MAJOR: incompatible governance or principle removals/redefinitions
  - MINOR: new principles/sections or materially expanded obligations
  - PATCH: clarifications and wording with no semantic change
- Compliance MUST be re-checked whenever the constitution changes and during feature planning.

**Version**: 1.1.0 | **Ratified**: 2026-01-02: original adoption date unknown | **Last Amended**: 2026-01-02
