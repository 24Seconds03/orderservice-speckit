# Order Service (Speckit/Opencode) – Projektdoku

## Schritt 0 – MVP Scope & Entscheidungen (DDD / Microservice)

### 0. Ziel
Wir implementieren einen **Order Service** für einen Möbel-Webshop.  
Der Warenkorb wird als **Draft Order** modelliert.  
Wir bauen **1 Microservice** und darin **1 Aggregate**.
Diese Dokumentation wird auf deutsch geschrieben, die Implementierung soll auf 
englisch erfolgen.

### 0.1 Bounded Context / Microservice
- Service: `order-service`
- Verantwortlich für: Erstellung/Änderung/Checkout von Bestellungen
- Nicht enthalten (explizit out-of-scope im MVP):
  - Produktkatalog, Lagerbestand, Benutzerverwaltung/Auth
  - Versand/Shipment, Retouren, Support-Tickets
  - echte Payment-Integration (nur Stub/Simulation)

### 0.2 Aggregate (DDD)
**Aggregate:** `Order`

**Wichtige Felder (Domain):**
- `order_id` (UUID)
- `status` ∈ {`DRAFT`, `SUBMITTED`, `PAID`} (MVP)
- `items[]` (product_id, unit_price_cents, qty)
- `shipping_address` (für Submit erforderlich)

Hinweis: OrderItems speichern unit_price_cents als Snapshot zum Zeitpunkt des AddItem.

### 0.3 Commands (MVP)
- `CreateDraftOrder`
- `AddItem(order_id, product_id, unit_price_cents, qty)` (Preis wird vom Client übergeben (MVP-Annahme))
- `RemoveItem(order_id, product_id)`
- `SetShippingAddress(order_id, address)`
- `SubmitOrder(order_id)`  → Checkout
- `ConfirmPayment(order_id, payment_ref)` → callback/extern

### 0.4 Domain Events 
Wir fokussieren 2 Events aus dem EventStorming.

- Event A: `OrderSubmitted`  
  Bedeutung: Kunde ist zur Kasse gegangen / Bestellung wurde aufgegeben.

- Event B: `PaymentConfirmed`  
  Bedeutung: Zahlung wurde bestätigt (External System Callback/Simulation).

### 0.5 Policies (Reaktionen auf Events)
- Policy 1 (bei `OrderSubmitted`): Payment anfordern (External System Stub)
- Policy 2 (bei `PaymentConfirmed`): Order auf `PAID` setzen + Bestätigung (Stub)

### 0.6 Read Model (Query)
- `GetOrder(order_id)` → Status + Items + Address (für Demo)
- Optional später: `ListOrders()` (nicht nötig für MVP)

### 0.7 Invarianten / Geschäftsregeln (Domain)
- `SubmitOrder` ist nur erlaubt, wenn:
  - mindestens 1 Item vorhanden ist
  - shipping_address gesetzt ist
  - status == `DRAFT`
- Nach `SUBMITTED` dürfen Items nicht mehr verändert werden (Add/Remove verboten)
- `ConfirmPayment` ist nur erlaubt, wenn status == `SUBMITTED`

### 0.8 Persistenz / Datenbank (nur MVP)
- DB: SQLite (file-based in Docker)
- Tabellen:
  - `orders`
  - `order_items`
- Optional: `outbox_events` (für Event-Log / spätere Veröffentlichung)

### 0.9 API (HTTP Endpoints – grob)
- `POST /orders` → CreateDraftOrder
- `POST /orders/{id}/items` → AddItem
- `DELETE /orders/{id}/items/{product_id}` → RemoveItem
- `PUT /orders/{id}/shipping-address` → SetShippingAddress
- `POST /orders/{id}/submit` → SubmitOrder
- `POST /payments/confirm` → ConfirmPayment (Stub Callback)
- `GET /orders/{id}` → Read Model

### 0.10 Definition of Done (MVP)
- Service startet lokal + im Docker
- Commands funktionieren + Regeln enforced (Tests!)
- pytest:
  - Domain-Unit-Tests für Invarianten
  - 1–2 API Smoke Tests (FastAPI TestClient)
- SQLite Schema wird automatisch erzeugt (SQLAlchemy)

## Schritt 1 – Constitution (speckit.constitution)

### Prompt (Input)
```text
/speckit.constitution We build a single Python 3.12 microservice called "order-service" for a furniture webshop. We follow Domain-Driven Design and implement exactly one aggregate: Order (cart as draft order with statuses DRAFT -> SUBMITTED -> PAID).
```

### Output
- .specify/memory/constitution.md wurde aus Template befüllt (v1.0.0)
- Sync Impact Report wurde hinzugefügt
- Speckit hat zusätzlich Templates angepasst:
  - .specify/templates/plan-template.md
  - .specify/templates/tasks-template.md

### Manuelle Verbesserungen an der Constitution (Review)
**Probleme im initialen Output**
- Ubiquitous Language als DDD-Kernprinzip fehlte
- Event-/External-System-Abgrenzung (Payment) war nicht explizit genug
- API-Fehlerfälle waren zu unkonkret (Statuscodes nicht festgelegt)
- Event-Verarbeitung war nicht klar (Outbox vs. Event-Bus)

**Änderungen / Fixes**
- Added new principle **Ubiquitous Language (Consistent Terms)**: englische Identifiers im Code, deutsche Doku erlaubt, aber gleiche Begriffe
- Klarstellung: `PaymentConfirmed` ist **externer Callback** (Payment Stub), kein Payment-Aggregate
- Festgelegt: Domain Events werden über **Outbox Table** persistiert (kein Kafka/Broker im MVP)
- API-Contract-Regel vereinfacht: Dokumentation direkt in Spec (OpenAPI/Contracts Section)
- Fehlercodes konkretisiert: `404` (not found), `409` (domain conflict), `422` (validation)
- Governance bereinigt: `Ratified` gesetzt; Constitution-Version auf **1.1.0** erhöht (neues Principle)


## Schritt 2 – Specification (speckit.specify)

### Prompt (Input)
```text
/speckit.specify Create an Order microservice for a furniture webshop where the shopping cart is modeled as a draft Order 
(DRAFT -> SUBMITTED -> PAID); customers can create a draft order, add/remove items (with price snapshot), 
set a shipping address, submit the order (emitting OrderSubmitted), and later confirm payment via an external callback 
(emitting PaymentConfirmed). The service exposes HTTP endpoints for commands and a read model to retrieve an order with 
status and items. Stop after writing the spec files; do not run plan/tasks/implement.

```

### Output
- Speckit hat Feature-Branch `001-draft-order-service` erstellt.
- Erzeugte Artefakte:
  - `specs/001-draft-order-service/spec.md`
  - `specs/001-draft-order-service/checklists/requirements.md` (ohne NEEDS-CLARIFICATION Marker)

