from __future__ import annotations

from enum import StrEnum
from uuid import UUID


class OrderStatus(StrEnum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    PAID = "PAID"


OrderId = UUID
