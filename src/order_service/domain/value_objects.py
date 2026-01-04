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
