from __future__ import annotations

import datetime as dt
import json
from uuid import uuid4

from sqlalchemy.orm import Session

from order_service.adapters.models import OutboxEventTable


def record_event(
    *,
    session: Session,
    event_type: str,
    aggregate_id: str,
    payload: dict,
    dedup_key: str | None = None,
    occurred_at: dt.datetime | None = None,
) -> None:
    resolved_dedup_key = dedup_key or f"{event_type}:{aggregate_id}"

    session.add(
        OutboxEventTable(
            id=str(uuid4()),
            event_type=event_type,
            aggregate_id=aggregate_id,
            dedup_key=resolved_dedup_key,
            payload=json.dumps(payload),
            occurred_at=occurred_at or dt.datetime.utcnow(),
        )
    )
