# Order Service

Ein FastAPI-basierter Order Service für die Verwaltung von Bestellungen (Draft Orders) mit Domain-Driven Design (DDD) Architektur.

## Technologie-Stack

- **Python 3.12**
- **FastAPI** - HTTP API Framework
- **Pydantic v2** - Datenvalidierung und Schemas
- **SQLAlchemy 2.x** - ORM für Datenbankzugriff
- **Uvicorn** - ASGI Server
- **SQLite** - Datenbank (Standard: `orders.db`)

## Voraussetzungen

### Lokale Entwicklung
- Python 3.12 oder höher
- pip (Python Package Manager)

### Docker (Alternative)
- Docker Engine 20.10 oder höher
- Docker Compose (optional, für docker-compose.yml)

## Installation

### 1. Repository klonen

```bash
git clone <repository-url>
cd orderservice-speckit
```

### 2. Virtuelle Umgebung erstellen

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Dependencies installieren

```bash
pip install -r requirements.txt
```

## Konfiguration

Die Anwendung verwendet Umgebungsvariablen oder eine `.env` Datei für die Konfiguration. Standardwerte:

- `DATABASE_URL`: `sqlite:///./orders.db`
- `CALLBACK_TOKEN`: `dev-token`

Optional können Sie eine `.env` Datei erstellen:

```env
DATABASE_URL=sqlite:///./orders.db
CALLBACK_TOKEN=dev-token
```

## Server starten

### Entwicklungsserver

**Windows (PowerShell):**
```powershell
cd src
uvicorn order_service.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Linux/macOS:**
```bash
cd src
uvicorn order_service.api.main:app --reload --host 0.0.0.0 --port 8000
```

Der Server läuft dann auf: `http://localhost:8000`

## Docker

### Docker Image bauen

**Windows (PowerShell):**
```powershell
docker build -t order-service .
```

**Linux/macOS:**
```bash
docker build -t order-service .
```

### Container starten

**Windows (PowerShell):**
```powershell
# Container mit Volume für persistente Datenbank starten
docker run -d --name order-service -p 8000:8000 -v ${PWD}/data:/data -e CALLBACK_TOKEN=dev-token order-service
```

**Linux/macOS:**
```bash
# Container mit Volume für persistente Datenbank starten
docker run -d \
  --name order-service \
  -p 8000:8000 \
  -v $(pwd)/data:/data \
  -e CALLBACK_TOKEN=dev-token \
  order-service
```

### Container verwalten

**Container stoppen:**
```bash
docker stop order-service
```

**Container starten:**
```bash
docker start order-service
```

**Container entfernen:**
```bash
docker rm -f order-service
```

**Logs anzeigen:**
```bash
docker logs -f order-service
```

**In laufenden Container einsteigen:**
```bash
docker exec -it order-service /bin/bash
```

**Hinweis:** Die Datenbank wird im Container unter `/data/orders.db` gespeichert. Durch das Volume-Mapping (`-v`) wird die Datenbank auf dem Host-System im `data/` Verzeichnis persistiert. Falls das Verzeichnis nicht existiert, wird es automatisch erstellt.

### Docker Compose (Optional)

Falls Sie `docker-compose` verwenden möchten, können Sie eine `docker-compose.yml` Datei erstellen:

```yaml
version: '3.8'

services:
  order-service:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/data
    environment:
      - DATABASE_URL=sqlite:////data/orders.db
      - CALLBACK_TOKEN=dev-token
    restart: unless-stopped
```

Dann können Sie den Service starten mit:

```bash
docker-compose up -d
```

### API Dokumentation

Nach dem Starten des Servers ist die interaktive API-Dokumentation verfügbar:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpunkte

### 1. Draft Order erstellen oder abrufen

**POST** `/customers/{customer_id}/orders/draft`

**Windows (PowerShell):**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/customers/customer-123/orders/draft" -Method POST -ContentType "application/json"
```

**Linux/macOS (curl):**
```bash
curl -X POST "http://localhost:8000/customers/customer-123/orders/draft" \
  -H "Content-Type: application/json"
```

**Beispiel Response:**
```json
{
  "order_id": "order-abc-123",
  "customer_id": "customer-123",
  "status": "DRAFT",
  "items": [],
  "shipping_address": null,
  "payment_reference": null
}
```

### 2. Order abrufen

**GET** `/customers/{customer_id}/orders/{order_id}`

**Windows (PowerShell):**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/customers/customer-123/orders/order-abc-123" -Method GET
```

**Linux/macOS (curl):**
```bash
curl -X GET "http://localhost:8000/customers/customer-123/orders/order-abc-123"
```

### 3. Item zu Order hinzufügen

**POST** `/customers/{customer_id}/orders/{order_id}/items`

**Windows (PowerShell):**
```powershell
$body = @{
    product_id = "prod-001"
    product_name = "Test Product"
    quantity = 2
    unit_price_cents = 1999
    currency = "EUR"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/customers/customer-123/orders/order-abc-123/items" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

**Linux/macOS (curl):**
```bash
curl -X POST "http://localhost:8000/customers/customer-123/orders/order-abc-123/items" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "prod-001",
    "product_name": "Test Product",
    "quantity": 2,
    "unit_price_cents": 1999,
    "currency": "EUR"
  }'
```

### 4. Item aus Order entfernen

**DELETE** `/customers/{customer_id}/orders/{order_id}/items/{product_id}`

**Windows (PowerShell):**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/customers/customer-123/orders/order-abc-123/items/prod-001" -Method DELETE
```

**Linux/macOS (curl):**
```bash
curl -X DELETE "http://localhost:8000/customers/customer-123/orders/order-abc-123/items/prod-001"
```

### 5. Versandadresse setzen

**PUT** `/customers/{customer_id}/orders/{order_id}/shipping-address`

**Windows (PowerShell):**
```powershell
$body = @{
    recipient_name = "Max Mustermann"
    street = "Musterstraße 123"
    postal_code = "12345"
    city = "Berlin"
    country = "Deutschland"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/customers/customer-123/orders/order-abc-123/shipping-address" `
  -Method PUT `
  -ContentType "application/json" `
  -Body $body
```

**Linux/macOS (curl):**
```bash
curl -X PUT "http://localhost:8000/customers/customer-123/orders/order-abc-123/shipping-address" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_name": "Max Mustermann",
    "street": "Musterstraße 123",
    "postal_code": "12345",
    "city": "Berlin",
    "country": "Deutschland"
  }'
```

### 6. Order einreichen (Submit)

**POST** `/customers/{customer_id}/orders/{order_id}/submit`

**Windows (PowerShell):**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/customers/customer-123/orders/order-abc-123/submit" -Method POST
```

**Linux/macOS (curl):**
```bash
curl -X POST "http://localhost:8000/customers/customer-123/orders/order-abc-123/submit"
```

### 7. Zahlung bestätigen (Payment Callback)

**POST** `/payments/confirmations`

**Hinweis:** Dieser Endpunkt erfordert den Header `X-Callback-Token` (Standard: `dev-token`)

**Windows (PowerShell):**
```powershell
$body = @{
    order_id = "order-abc-123"
    payment_reference = "pay-ref-456"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/payments/confirmations" `
  -Method POST `
  -ContentType "application/json" `
  -Headers @{"X-Callback-Token"="dev-token"} `
  -Body $body
```

**Linux/macOS (curl):**
```bash
curl -X POST "http://localhost:8000/payments/confirmations" \
  -H "Content-Type: application/json" \
  -H "X-Callback-Token: dev-token" \
  -d '{
    "order_id": "order-abc-123",
    "payment_reference": "pay-ref-456"
  }'
```

## Vollständiger Workflow Beispiel

Hier ist ein vollständiges Beispiel für einen typischen Bestellablauf:

**Windows (PowerShell):**
```powershell
# 1. Draft Order erstellen
$order = Invoke-RestMethod -Uri "http://localhost:8000/customers/customer-123/orders/draft" -Method POST
$orderId = $order.order_id
Write-Host "Order erstellt: $orderId"

# 2. Item hinzufügen
$itemBody = @{
    product_id = "prod-001"
    product_name = "Laptop"
    quantity = 1
    unit_price_cents = 99999
    currency = "EUR"
} | ConvertTo-Json

$order = Invoke-RestMethod -Uri "http://localhost:8000/customers/customer-123/orders/$orderId/items" `
  -Method POST -ContentType "application/json" -Body $itemBody
Write-Host "Item hinzugefügt"

# 3. Versandadresse setzen
$addressBody = @{
    recipient_name = "Max Mustermann"
    street = "Musterstraße 123"
    postal_code = "12345"
    city = "Berlin"
    country = "Deutschland"
} | ConvertTo-Json

$order = Invoke-RestMethod -Uri "http://localhost:8000/customers/customer-123/orders/$orderId/shipping-address" `
  -Method PUT -ContentType "application/json" -Body $addressBody
Write-Host "Versandadresse gesetzt"

# 4. Order einreichen
$order = Invoke-RestMethod -Uri "http://localhost:8000/customers/customer-123/orders/$orderId/submit" -Method POST
Write-Host "Order eingereicht, Status: $($order.status)"

# 5. Zahlung bestätigen
$paymentBody = @{
    order_id = $orderId
    payment_reference = "pay-ref-456"
} | ConvertTo-Json

$order = Invoke-RestMethod -Uri "http://localhost:8000/payments/confirmations" `
  -Method POST -ContentType "application/json" `
  -Headers @{"X-Callback-Token"="dev-token"} -Body $paymentBody
Write-Host "Zahlung bestätigt, Status: $($order.status)"
```

**Linux/macOS (Bash):**
```bash
#!/bin/bash

# 1. Draft Order erstellen
ORDER=$(curl -s -X POST "http://localhost:8000/customers/customer-123/orders/draft")
ORDER_ID=$(echo $ORDER | grep -o '"order_id":"[^"]*' | cut -d'"' -f4)
echo "Order erstellt: $ORDER_ID"

# 2. Item hinzufügen
curl -s -X POST "http://localhost:8000/customers/customer-123/orders/$ORDER_ID/items" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "prod-001",
    "product_name": "Laptop",
    "quantity": 1,
    "unit_price_cents": 99999,
    "currency": "EUR"
  }'
echo "Item hinzugefügt"

# 3. Versandadresse setzen
curl -s -X PUT "http://localhost:8000/customers/customer-123/orders/$ORDER_ID/shipping-address" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_name": "Max Mustermann",
    "street": "Musterstraße 123",
    "postal_code": "12345",
    "city": "Berlin",
    "country": "Deutschland"
  }'
echo "Versandadresse gesetzt"

# 4. Order einreichen
ORDER=$(curl -s -X POST "http://localhost:8000/customers/customer-123/orders/$ORDER_ID/submit")
echo "Order eingereicht"

# 5. Zahlung bestätigen
curl -s -X POST "http://localhost:8000/payments/confirmations" \
  -H "Content-Type: application/json" \
  -H "X-Callback-Token: dev-token" \
  -d "{
    \"order_id\": \"$ORDER_ID\",
    \"payment_reference\": \"pay-ref-456\"
  }"
echo "Zahlung bestätigt"
```

## Testing

### Unit Tests ausführen

**Windows (PowerShell):**
```powershell
cd src
pytest
```

**Linux/macOS:**
```bash
cd src
pytest
```

### Linting

**Windows (PowerShell):**
```powershell
cd src
ruff check .
```

**Linux/macOS:**
```bash
cd src
ruff check .
```

## Order Status

Die Order durchläuft folgende Status:

- **DRAFT** - Entwurf, kann bearbeitet werden
- **SUBMITTED** - Eingereicht, wartet auf Zahlung
- **PAID** - Bezahlt, Bestellung abgeschlossen

## Projektstruktur

```
src/
├── order_service/
│   ├── adapters/          # Datenbank-Adapter und Repository
│   ├── api/               # FastAPI Routes und Endpunkte
│   ├── application/       # Use Cases und Unit of Work
│   ├── domain/            # Domain-Modelle und Business-Logik
│   ├── config.py          # Konfiguration
│   └── logging.py         # Logging-Konfiguration
tests/                     # Test-Dateien
specs/                     # Spezifikationen und OpenAPI Contracts
```

## Weitere Informationen

- OpenAPI Spezifikation: `specs/001-draft-order-service/contracts/openapi.yaml`
- Die Datenbank wird automatisch beim ersten Start erstellt (`orders.db`)


