from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from order_service.domain.errors import ConflictError, DomainValidationError
from order_service.domain.types import OrderStatus
from order_service.domain.value_objects import OrderItem, PriceSnapshot


@dataclass(slots=True)
class Order:
    order_id: UUID
    customer_id: str
    status: OrderStatus
    items: list[OrderItem] = field(default_factory=list)

    @classmethod
    def create_draft(cls, *, order_id: UUID, customer_id: str) -> "Order":
        if not customer_id:
            raise DomainValidationError(
                error_code="INVALID_CUSTOMER_ID",
                message="customer_id is required",
            )

        return cls(order_id=order_id, customer_id=customer_id, status=OrderStatus.DRAFT)

    def add_item(
        self,
        *,
        product_id: str,
        quantity: int,
        price: PriceSnapshot,
        product_name: str | None,
    ) -> None:
        self._require_draft("add_item")

        if not product_id:
            raise DomainValidationError(
                error_code="INVALID_PRODUCT_ID",
                message="product_id is required",
            )
        if quantity <= 0:
            raise DomainValidationError(
                error_code="INVALID_QUANTITY",
                message="quantity must be >= 1",
            )

        for item in self.items:
            if item.product_id == product_id:
                # Preserve the original price snapshot for this line item.
                item.increase_quantity(quantity)
                return

        self.items.append(
            OrderItem(
                product_id=product_id,
                product_name=product_name,
                quantity=quantity,
                price=price,
            )
        )

    def remove_item(self, *, product_id: str) -> None:
        self._require_draft("remove_item")

        for index, item in enumerate(self.items):
            if item.product_id == product_id:
                self.items.pop(index)
                return

        raise DomainValidationError(
            error_code="ITEM_NOT_FOUND",
            message="Order does not contain requested product",
            details={"product_id": product_id},
        )

    def _require_draft(self, command: str) -> None:
        if self.status != OrderStatus.DRAFT:
            raise ConflictError(
                error_code="INVALID_STATUS",
                message=f"{command} allowed only for DRAFT orders",
                details={"status": self.status.value},
            )
