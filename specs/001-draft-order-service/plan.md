# Implementation Plan: Draft Order Microservice

**Branch**: `001-draft-order-service` | **Date**: 2026-01-04 | **Spec**: `specs/001-draft-order-service/spec.md`
**Input**: Feature specification from `specs/001-draft-order-service/spec.md`

## Summary

Implement a single Python 3.12 `order-service` FastAPI microservice with one DDD aggregate (`Order`) supporting the lifecycle `DRAFT → SUBMITTED → PAID`. Persist orders in SQLite via SQLAlchemy, enforce all invariants inside the `Order` aggregate, and record `OrderSubmitted` / `PaymentConfirmed` domain events in an outbox table for durable, brokerless event capture.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: FastAPI (HTTP API), Pydantic v2 (schemas), SQLAlchemy 2.x (ORM), Uvicorn (ASGI server)  
**Storage**: SQLite (file-based; persisted as a Docker volume) via SQLAlchemy  
**Testing**: pytest (+ FastAPI `TestClient` for API smoke tests)  
**Target Platform**: Linux container runtime (Docker) and local dev (Windows/macOS/Linux)  
**Project Type**: Single service (one deployable microservice)  
**Performance Goals**: MVP correctness > performance; target <200ms p95 locally for simple reads/writes; satisfy spec success criteria (read within 5s, paid visible within 10s)  
**Constraints**: Exactly one aggregate (`Order`); strict lifecycle state machine; no message broker; outbox must durably record domain events; auth handled upstream; SQLite file DB in Docker  
**Scale/Scope**: MVP / single bounded context; low-to-moderate traffic; single-instance deployment assumed (SQLite)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Confirm change stays within the single `Order` aggregate boundary
- Confirm lifecycle rules remain `DRAFT` → `SUBMITTED` → `PAID` (no illegal transitions)
- Confirm domain invariants are covered by `pytest` unit tests
- Confirm affected endpoints have at least an API smoke test (e.g., FastAPI `TestClient`)
- Confirm any contract changes are documented in `specs/.../contracts/`
- Confirm logs include `order_id` + command/context

## Project Structure

### Documentation (this feature)

```text
specs/001-draft-order-service/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
order_service/
├── api/                 # FastAPI routes + request/response DTOs
├── application/         # Use-cases (command handlers), unit-of-work
├── adapters/            # DB/outbox implementations and repositories
└── domain/              # Aggregate + value objects + domain events

tests/
├── api/                 # 1-2 HTTP smoke tests
└── domain/              # Domain invariants + transitions
```

**Structure Decision**: Use a classic clean/layered DDD layout (`domain` / `application` / `adapters` / `api`) inside a single Python package `order_service` to keep boundaries explicit while remaining lightweight for an MVP microservice.

## Complexity Tracking

> No constitution violations are required for this feature.
