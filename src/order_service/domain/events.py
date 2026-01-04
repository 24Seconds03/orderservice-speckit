from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class OrderSubmitted:
    order_id: UUID
    customer_id: str

    @property
    def event_type(self) -> str:
        return "OrderSubmitted"

    @property
    def payload(self) -> dict[str, str]:
        return {
            "order_id": str(self.order_id),
            "customer_id": self.customer_id,
        }


@dataclass(frozen=True, slots=True)
class PaymentConfirmed:
    order_id: UUID
    payment_reference: str

    @property
    def event_type(self) -> str:
        return "PaymentConfirmed"

    @property
    def payload(self) -> dict[str, str]:
        return {
            "order_id": str(self.order_id),
            "payment_reference": self.payment_reference,
        }
