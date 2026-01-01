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
