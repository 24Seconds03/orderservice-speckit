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
