"""Universal Activity Events Bus and Timeline Projector."""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.events import ActivityEvent

# In-memory broadcast listeners (used by SSE/WebSockets for connected clients during dev or when Supabase Realtime is local)
_subscribers: list[Any] = []


class ActivityBus:
    """Dispatches canonical activity events to the database and realtime broadcast."""

    @staticmethod
    async def record_activity(
        session: AsyncSession,
        user_id: str,
        event_type: str,
        entity_type: str,
        entity_id: str,
        source: str = "tracking_engine",
        metadata: dict[str, Any] | None = None,
        occurred_at: datetime | None = None,
    ) -> ActivityEvent:
        """Persists a canonical event to activity_events and broadcasts it to realtime listeners."""
        if occurred_at is None:
            occurred_at = datetime.now(UTC)

        activity = ActivityEvent(
            user_id=user_id,
            event_type=event_type,
            source=source,
            entity_type=entity_type,
            entity_id=entity_id,
            occurred_at=occurred_at,
            metadata_json=metadata or {},
        )
        session.add(activity)
        await session.flush()

        # Broadcast event to in-memory listeners if any
        event_payload = {
            "id": activity.id,
            "user_id": user_id,
            "event_type": event_type,
            "source": source,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "occurred_at": activity.occurred_at.isoformat(),
            "metadata": activity.metadata_json,
        }
        for sub in _subscribers:
            try:
                await sub(event_payload)
            except Exception:
                pass

        return activity

    @staticmethod
    def subscribe(callback):
        """Registers a listener for live activity broadcasts."""
        _subscribers.append(callback)

    @staticmethod
    def unsubscribe(callback):
        """Unregisters a listener."""
        if callback in _subscribers:
            _subscribers.remove(callback)

    @staticmethod
    async def get_recent_activity(
        session: AsyncSession,
        user_id: str,
        limit: int = 50,
        since_id: str | None = None,
    ) -> list[ActivityEvent]:
        """Reconciliation API: fetches chronological activity events for dashboard or extension."""
        stmt = (
            select(ActivityEvent)
            .where(ActivityEvent.user_id == user_id)
            .order_by(desc(ActivityEvent.occurred_at))
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())


activity_bus = ActivityBus()
