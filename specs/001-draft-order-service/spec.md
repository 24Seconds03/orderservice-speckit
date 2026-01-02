# Feature Specification: Draft Order Microservice

**Feature Branch**: `001-draft-order-service`  
**Created**: 2026-01-02  
**Status**: Draft  
**Input**: User description: "Create an Order microservice for a furniture webshop where the shopping cart is modeled as a draft Order (DRAFT -> SUBMITTED -> PAID); customers can create a draft order, add/remove items (with price snapshot), set a shipping address, submit the order (emitting OrderSubmitted), and later confirm payment via an external callback (emitting PaymentConfirmed). The service exposes HTTP endpoints for commands and a read model to retreive an order with status and items. Stop after writing the spec files; do not run plan / tasks / impelement"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Build a shopping cart as a draft order (Priority: P1)

As a customer, I can create a draft order and add/remove items so that my shopping cart is persisted and can be reviewed later.

**Why this priority**: This is the core cart experience and is required before checkout.

**Independent Test**: Can be fully tested by creating a draft order, adding/removing items, and retrieving the order read model to verify status and item details.

**Acceptance Scenarios**:

1. **Given** a customer with no current draft order, **When** they create a draft order, **Then** a new order exists with status `DRAFT` and no items.
2. **Given** a `DRAFT` order, **When** the customer adds an item with quantity and price snapshot, **Then** the order contains the item and the stored price snapshot matches what was provided at the time of adding.
3. **Given** a `DRAFT` order with an item, **When** the customer removes that item, **Then** the order no longer contains it.

---

### User Story 2 - Provide shipping address and submit the order (Priority: P2)

As a customer, I can set a shipping address on my draft order and submit it so that checkout can begin and the webshop can start fulfillment and payment processing.

**Why this priority**: Submission is the boundary between an editable cart and a committed order.

**Independent Test**: Can be fully tested by setting an address on a `DRAFT` order, submitting it, verifying status becomes `SUBMITTED`, and verifying an `OrderSubmitted` event is emitted.

**Acceptance Scenarios**:

1. **Given** a `DRAFT` order with at least one item and no shipping address, **When** the customer submits the order, **Then** submission is rejected with a clear validation error.
2. **Given** a `DRAFT` order with at least one item and a complete shipping address, **When** the customer submits the order, **Then** the order status becomes `SUBMITTED` and an `OrderSubmitted` event is emitted.
3. **Given** a `SUBMITTED` order, **When** the customer attempts to add/remove items or change the shipping address, **Then** the change is rejected and the order remains unchanged.

---

### User Story 3 - Confirm payment via external callback (Priority: P3)

As the webshop, we can accept a payment confirmation callback from an external payment provider so that a submitted order becomes paid and downstream systems are notified.

**Why this priority**: Paid status is required to complete the order lifecycle and unlock fulfillment.

**Independent Test**: Can be fully tested by submitting an order, calling the payment confirmation callback, verifying status becomes `PAID`, and verifying a `PaymentConfirmed` event is emitted.

**Acceptance Scenarios**:

1. **Given** a `SUBMITTED` order, **When** a valid payment confirmation callback is received, **Then** the order status becomes `PAID` and a `PaymentConfirmed` event is emitted.
2. **Given** a `PAID` order, **When** a duplicate payment confirmation callback is received for the same payment, **Then** the request succeeds without changing the order and no duplicate `PaymentConfirmed` event is emitted.

---

### Edge Cases

- A customer tries to add items to a non-existent order.
- A customer tries to remove an item that is not present in the order.
- A customer tries to submit a draft order with zero items.
- A customer tries to access or modify another customer’s order.
- Payment confirmation is received for an unknown order.
- Payment confirmation is received for an order that is still `DRAFT`.
- Payment confirmation arrives multiple times or out of order.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow a customer to create a new order in status `DRAFT`.
- **FR-002**: System MUST allow a customer to retrieve an order read model that includes at minimum: `orderId`, `customerId`, `status` (`DRAFT`, `SUBMITTED`, `PAID`), items, and shipping address (if set).
- **FR-003**: System MUST allow a customer to add an item to a `DRAFT` order.
- **FR-004**: When an item is added, System MUST store a price snapshot provided at the time of adding (e.g., unit price and currency) and MUST NOT retroactively change that snapshot due to later catalog price changes.
- **FR-005**: System MUST allow a customer to remove an item from a `DRAFT` order.
- **FR-006**: System MUST reject item additions/removals for orders not in `DRAFT`.
- **FR-007**: System MUST allow a customer to set or replace a shipping address on a `DRAFT` order.
- **FR-008**: System MUST reject shipping address changes for orders not in `DRAFT`.
- **FR-009**: System MUST allow a customer to submit a `DRAFT` order, transitioning it to `SUBMITTED`.
- **FR-010**: System MUST reject submission unless the order has at least one item and a complete shipping address (recipient name, street, postal code, city, and country).
- **FR-011**: Upon successful submission, System MUST emit an `OrderSubmitted` event containing enough information for downstream consumers to start payment/fulfillment workflows (at minimum: order identifier and customer identifier).
- **FR-012**: System MUST accept an external payment confirmation callback to confirm payment for a `SUBMITTED` order.
- **FR-013**: Upon successful payment confirmation, System MUST transition the order to `PAID` and emit a `PaymentConfirmed` event (at minimum: order identifier and a payment reference).
- **FR-014**: System MUST treat payment confirmation callbacks as idempotent (retries must not create duplicate state transitions or duplicate `PaymentConfirmed` emissions).
- **FR-015**: System MUST protect all customer-facing command endpoints so only the owning customer can create, view, and modify their own orders.
- **FR-016**: System MUST protect the payment confirmation callback so only authorized payment systems can confirm payment.
- **FR-017**: System MUST provide clear, user-safe error responses for invalid transitions (e.g., submitting a `PAID` order).

### Assumptions

- The furniture webshop has a separate product/catalog source; this service receives product identifiers and the price snapshot to store, but does not calculate pricing from scratch.
- Taxes, discounts, and shipping cost calculation are out of scope unless explicitly added later; the order stores item price snapshots only.
- Inventory reservation and fulfillment execution are handled by other systems; this service emits events and tracks order state.

### Out of Scope

- Capturing payment details directly from customers (payment UI/workflows are handled elsewhere).
- Refunds, cancellations, returns, partial payments, and multiple shipments.
- Promotions/discount application, tax calculation, and shipping rate selection.

### Key Entities *(include if feature involves data)*

- **Order**: A customer-owned purchase intent with an immutable identifier, a status (`DRAFT` → `SUBMITTED` → `PAID`), a list of items, and an optional shipping address until submission.
- **OrderItem**: A line item representing a product being purchased; includes product identifier, display name/description (if provided), quantity, and a price snapshot captured when added.
- **PriceSnapshot**: The monetary values stored at the time the item is added (e.g., unit price and currency) used for later review and payment reconciliation.
- **ShippingAddress**: The destination address for delivery; includes recipient name, street, postal code, city, and country.
- **OrderSubmitted (Event)**: A domain event emitted when an order transitions to `SUBMITTED`.
- **PaymentConfirmed (Event)**: A domain event emitted when an order transitions to `PAID`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A customer can create a draft order and see it in the read model within 5 seconds.
- **SC-002**: A customer can add/remove items and observe the updated order (status and items) within 5 seconds.
- **SC-003**: At least 95% of customers can submit an order on the first attempt when providing a valid address and at least one item.
- **SC-004**: Payment confirmation updates an order to `PAID` and makes that status visible in the read model within 10 seconds.
- **SC-005**: Duplicate payment confirmations do not result in duplicate paid transitions or duplicate `PaymentConfirmed` notifications (0 observed duplicates in acceptance testing).
