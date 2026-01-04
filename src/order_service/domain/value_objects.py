from __future__ import annotations

from dataclasses import dataclass

from order_service.domain.errors import DomainValidationError


@dataclass(frozen=True, slots=True)
class PriceSnapshot:
    unit_price_cents: int
    currency: str

    def __post_init__(self) -> None:
        if self.unit_price_cents < 0:
            raise DomainValidationError(
                error_code="INVALID_PRICE",
                message="unit_price_cents must be >= 0",
            )
        if not self.currency:
            raise DomainValidationError(
                error_code="INVALID_CURRENCY",
                message="currency is required",
            )


@dataclass(slots=True)
class OrderItem:
    product_id: str
    quantity: int
    price: PriceSnapshot
    product_name: str | None = None

    def __post_init__(self) -> None:
        if not self.product_id:
            raise DomainValidationError(
                error_code="INVALID_PRODUCT_ID",
                message="product_id is required",
            )
        if self.quantity <= 0:
            raise DomainValidationError(
                error_code="INVALID_QUANTITY",
                message="quantity must be >= 1",
            )

    def increase_quantity(self, by: int) -> None:
        if by <= 0:
            raise DomainValidationError(
                error_code="INVALID_QUANTITY",
                message="quantity increment must be >= 1",
            )
        self.quantity += by


@dataclass(frozen=True, slots=True)
class ShippingAddress:
    recipient_name: str
    street: str
    postal_code: str
    city: str
    country: str

    def __post_init__(self) -> None:
        fields = {
            "recipient_name": self.recipient_name,
            "street": self.street,
            "postal_code": self.postal_code,
            "city": self.city,
            "country": self.country,
        }

        missing = [name for name, value in fields.items() if not value]
        if missing:
            raise DomainValidationError(
                error_code="INVALID_SHIPPING_ADDRESS",
                message="shipping address is incomplete",
                details={"missing": missing},
            )
