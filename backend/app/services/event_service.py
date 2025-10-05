"""
Enterprise Event Service with scalable event-driven architecture.
Built for MVP simplicity, designed for billion-dollar platform scale.
"""

import asyncio
import json
import logging
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Standard event types for enterprise observability"""

    # Agent lifecycle events
    AGENT_CREATED = "agent.created"
    AGENT_UPDATED = "agent.updated"
    AGENT_DELETED = "agent.deleted"
    AGENT_STARTED = "agent.started"
    AGENT_STOPPED = "agent.stopped"

    # Task execution events
    TASK_SUBMITTED = "task.submitted"
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    TASK_CANCELLED = "task.cancelled"

    # Engine events
    ENGINE_STARTED = "engine.started"
    ENGINE_STOPPED = "engine.stopped"
    ENGINE_ERROR = "engine.error"

    # Provider events
    PROVIDER_HEALTH_CHECK = "provider.health_check"
    PROVIDER_ERROR = "provider.error"
    PROVIDER_RATE_LIMITED = "provider.rate_limited"

    # Security events
    AUTH_SUCCESS = "auth.success"
    AUTH_FAILED = "auth.failed"
    ACCESS_DENIED = "access.denied"

    # Business events
    COST_THRESHOLD_EXCEEDED = "cost.threshold_exceeded"
    QUOTA_EXCEEDED = "quota.exceeded"
    SLA_VIOLATION = "sla.violation"

    # Custom events
    CUSTOM = "custom"


@dataclass
class Event:
    """
    Enterprise event with full traceability.

    Current: Basic event structure
    Future: Event schemas, validation, encryption
    """

    event_id: str
    event_type: EventType
    timestamp: datetime

    # Event payload
    data: Dict[str, Any]

    # Enterprise context
    tenant_id: Optional[str] = None
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    task_id: Optional[str] = None

    # Tracing and correlation
    correlation_id: Optional[str] = None
    parent_event_id: Optional[str] = None
    trace_id: Optional[str] = None

    # Event metadata
    source: str = "agentcores"
    version: str = "1.0"
    priority: str = "normal"

    # Delivery tracking
    delivery_attempts: int = 0
    last_delivery_attempt: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization"""
        event_dict = asdict(self)
        event_dict["event_type"] = self.event_type.value
        event_dict["timestamp"] = self.timestamp.isoformat()
        if self.last_delivery_attempt:
            event_dict["last_delivery_attempt"] = self.last_delivery_attempt.isoformat()
        return event_dict

    def to_json(self) -> str:
        """Convert event to JSON string"""
        return json.dumps(self.to_dict())


class EventHandler:
    """
    Event handler registration and execution.

    Current: Simple callback-based handlers
    Future: Complex event processing, filters, transformations
    """

    def __init__(
        self, handler_id: str, event_types: List[EventType], callback: Callable
    ):
        self.handler_id = handler_id
        self.event_types = set(event_types)
        self.callback = callback
        self.enabled = True

        # Enterprise features
        self.filter_conditions: Dict[str, Any] = {}
        self.retry_config = {"max_retries": 3, "backoff_multiplier": 2}

        # Metrics
        self.events_processed = 0
        self.events_failed = 0
        self.last_processed: Optional[datetime] = None

    def matches_event(self, event: Event) -> bool:
        """Check if handler should process this event"""
        if not self.enabled:
            return False

        if event.event_type not in self.event_types:
            return False

        # Apply filter conditions (future: complex filtering)
        for field, expected_value in self.filter_conditions.items():
            if hasattr(event, field):
                if getattr(event, field) != expected_value:
                    return False
            elif field in event.data:
                if event.data[field] != expected_value:
                    return False

        return True

    async def handle_event(self, event: Event) -> bool:
        """Execute handler for event"""
        try:
            if asyncio.iscoroutinefunction(self.callback):
                await self.callback(event)
            else:
                self.callback(event)

            self.events_processed += 1
            self.last_processed = datetime.utcnow()
            return True

        except Exception as e:
            self.events_failed += 1
            logger.error(f"Event handler {self.handler_id} failed: {str(e)}")
            return False


class EventStore:
    """
    Enterprise event store with persistence.

    Current: In-memory storage with limited retention
    Future: Database persistence, partitioning, archival
    """

    def __init__(self, max_events: int = 10000, retention_hours: int = 24):
        self._events: Dict[str, Event] = {}
        self._events_by_type: Dict[EventType, List[str]] = {}
        self._events_by_tenant: Dict[str, List[str]] = {}

        self.max_events = max_events
        self.retention_hours = retention_hours

        # Start cleanup task
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def store_event(self, event: Event):
        """Store event with automatic cleanup"""
        self._events[event.event_id] = event

        # Index by type
        if event.event_type not in self._events_by_type:
            self._events_by_type[event.event_type] = []
        self._events_by_type[event.event_type].append(event.event_id)

        # Index by tenant
        if event.tenant_id:
            if event.tenant_id not in self._events_by_tenant:
                self._events_by_tenant[event.tenant_id] = []
            self._events_by_tenant[event.tenant_id].append(event.event_id)

        # Trigger cleanup if needed
        if len(self._events) > self.max_events:
            await self._cleanup_old_events()

    async def get_event(self, event_id: str) -> Optional[Event]:
        """Retrieve event by ID"""
        return self._events.get(event_id)

    async def get_events_by_type(
        self, event_type: EventType, limit: int = 100, since: Optional[datetime] = None
    ) -> List[Event]:
        """Get events by type with filtering"""
        event_ids = self._events_by_type.get(event_type, [])
        events = []

        for event_id in reversed(event_ids[-limit:]):  # Latest first
            event = self._events.get(event_id)
            if event and (not since or event.timestamp >= since):
                events.append(event)

        return events

    async def get_events_by_tenant(
        self, tenant_id: str, limit: int = 100, since: Optional[datetime] = None
    ) -> List[Event]:
        """Get events by tenant with filtering"""
        event_ids = self._events_by_tenant.get(tenant_id, [])
        events = []

        for event_id in reversed(event_ids[-limit:]):  # Latest first
            event = self._events.get(event_id)
            if event and (not since or event.timestamp >= since):
                events.append(event)

        return events

    async def get_event_stats(self) -> Dict[str, Any]:
        """Get event store statistics"""
        stats = {
            "total_events": len(self._events),
            "events_by_type": {
                event_type.value: len(event_ids)
                for event_type, event_ids in self._events_by_type.items()
            },
            "tenants": len(self._events_by_tenant),
            "oldest_event": None,
            "newest_event": None,
        }

        if self._events:
            timestamps = [event.timestamp for event in self._events.values()]
            stats["oldest_event"] = min(timestamps).isoformat()
            stats["newest_event"] = max(timestamps).isoformat()

        return stats

    async def _cleanup_loop(self):
        """Background cleanup of old events"""
        while True:
            try:
                await asyncio.sleep(3600)  # Check every hour
                await self._cleanup_old_events()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Event cleanup error: {str(e)}")

    async def _cleanup_old_events(self):
        """Remove old events based on retention policy"""
        cutoff_time = datetime.utcnow() - timedelta(hours=self.retention_hours)

        events_to_remove = []
        for event_id, event in self._events.items():
            if event.timestamp < cutoff_time:
                events_to_remove.append(event_id)

        for event_id in events_to_remove:
            event = self._events.pop(event_id, None)
            if event:
                # Remove from indexes
                if event.event_type in self._events_by_type:
                    try:
                        self._events_by_type[event.event_type].remove(event_id)
                    except ValueError:
                        pass

                if event.tenant_id and event.tenant_id in self._events_by_tenant:
                    try:
                        self._events_by_tenant[event.tenant_id].remove(event_id)
                    except ValueError:
                        pass

        if events_to_remove:
            logger.info(f"Cleaned up {len(events_to_remove)} old events")


class EventService:
    """
    Enterprise Event Service with scalable architecture.

    Current: In-memory event bus with basic handlers
    Future: Distributed event streaming, complex event processing
    """

    def __init__(self, enable_store: bool = True):
        self.event_store = EventStore() if enable_store else None
        self.handlers: Dict[str, EventHandler] = {}

        # Event processing
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._processor_task = None
        self._running = False

        # Enterprise features
        self._dead_letter_queue: asyncio.Queue = asyncio.Queue()
        self._webhook_subscriptions: Dict[str, Dict[str, Any]] = {}

        # Metrics
        self._metrics = {
            "events_published": 0,
            "events_processed": 0,
            "events_failed": 0,
            "handlers_registered": 0,
        }

    async def start(self):
        """Start the event service"""
        if self._running:
            return

        self._running = True
        self._processor_task = asyncio.create_task(self._event_processor())

        logger.info("Event service started")

        # Publish startup event
        await self.publish_event(
            {
                "type": "event_service.started",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    async def stop(self):
        """Stop the event service"""
        self._running = False

        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass

        if self.event_store and hasattr(self.event_store, "_cleanup_task"):
            self.event_store._cleanup_task.cancel()

        logger.info("Event service stopped")

    async def publish_event(
        self,
        event_data: Dict[str, Any],
        event_type: Optional[EventType] = None,
        tenant_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> str:
        """
        Publish event to the event bus.

        Current: Simple event publishing
        Future: Event validation, schema enforcement, routing
        """
        try:
            # Determine event type
            if event_type is None:
                type_str = event_data.get("type", "custom")
                try:
                    event_type = EventType(type_str)
                except ValueError:
                    event_type = EventType.CUSTOM

            # Create event
            event = Event(
                event_id=str(uuid.uuid4()),
                event_type=event_type,
                timestamp=datetime.utcnow(),
                data=event_data,
                tenant_id=tenant_id,
                correlation_id=correlation_id or str(uuid.uuid4()),
            )

            # Add to processing queue
            await self._event_queue.put(event)

            self._metrics["events_published"] += 1

            return event.event_id

        except Exception as e:
            logger.error(f"Failed to publish event: {str(e)}")
            raise

    def register_handler(
        self,
        handler_id: str,
        event_types: List[EventType],
        callback: Callable,
        filter_conditions: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Register event handler.

        Current: Simple callback registration
        Future: Handler discovery, dependency injection, load balancing
        """
        try:
            if handler_id in self.handlers:
                logger.warning(f"Handler {handler_id} already registered, replacing")

            handler = EventHandler(handler_id, event_types, callback)
            if filter_conditions:
                handler.filter_conditions = filter_conditions

            self.handlers[handler_id] = handler
            self._metrics["handlers_registered"] = len(self.handlers)

            logger.info(
                f"Registered event handler: {handler_id} for types: {[t.value for t in event_types]}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to register handler {handler_id}: {str(e)}")
            return False

    def unregister_handler(self, handler_id: str) -> bool:
        """Unregister event handler"""
        if handler_id in self.handlers:
            del self.handlers[handler_id]
            self._metrics["handlers_registered"] = len(self.handlers)
            logger.info(f"Unregistered event handler: {handler_id}")
            return True
        return False

    async def get_events(
        self,
        event_type: Optional[EventType] = None,
        tenant_id: Optional[str] = None,
        limit: int = 100,
        since: Optional[datetime] = None,
    ) -> List[Event]:
        """Get events from store with filtering"""
        if not self.event_store:
            return []

        if event_type:
            return await self.event_store.get_events_by_type(event_type, limit, since)
        elif tenant_id:
            return await self.event_store.get_events_by_tenant(tenant_id, limit, since)
        else:
            # Return recent events across all types (limited implementation)
            all_events = []
            for event in self.event_store._events.values():
                if not since or event.timestamp >= since:
                    all_events.append(event)

            # Sort by timestamp and limit
            all_events.sort(key=lambda e: e.timestamp, reverse=True)
            return all_events[:limit]

    async def get_service_stats(self) -> Dict[str, Any]:
        """Get service statistics for monitoring"""
        stats = {
            "service": {
                "running": self._running,
                "queue_size": self._event_queue.qsize(),
                "dead_letter_queue_size": self._dead_letter_queue.qsize(),
                "handlers_count": len(self.handlers),
            },
            "metrics": self._metrics.copy(),
            "handlers": {
                handler_id: {
                    "event_types": [t.value for t in handler.event_types],
                    "enabled": handler.enabled,
                    "events_processed": handler.events_processed,
                    "events_failed": handler.events_failed,
                    "last_processed": (
                        handler.last_processed.isoformat()
                        if handler.last_processed
                        else None
                    ),
                }
                for handler_id, handler in self.handlers.items()
            },
        }

        if self.event_store:
            stats["store"] = await self.event_store.get_event_stats()

        return stats

    # Private methods for event processing

    async def _event_processor(self):
        """Main event processing loop"""
        logger.info("Event processor started")

        while self._running:
            try:
                # Get next event with timeout
                event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)

                # Store event if store is enabled
                if self.event_store:
                    await self.event_store.store_event(event)

                # Process event with handlers
                await self._process_event_with_handlers(event)

                self._metrics["events_processed"] += 1

            except asyncio.TimeoutError:
                # No events to process, continue
                continue
            except asyncio.CancelledError:
                logger.info("Event processor cancelled")
                break
            except Exception as e:
                logger.error(f"Event processor error: {str(e)}")
                self._metrics["events_failed"] += 1

        logger.info("Event processor stopped")

    async def _process_event_with_handlers(self, event: Event):
        """Process event with all matching handlers"""
        matching_handlers = []

        for handler in self.handlers.values():
            if handler.matches_event(event):
                matching_handlers.append(handler)

        if not matching_handlers:
            logger.debug(f"No handlers for event: {event.event_type.value}")
            return

        # Execute handlers concurrently (future: sequential for ordered processing)
        handler_tasks = []
        for handler in matching_handlers:
            task = asyncio.create_task(self._execute_handler_with_retry(handler, event))
            handler_tasks.append(task)

        # Wait for all handlers to complete
        results = await asyncio.gather(*handler_tasks, return_exceptions=True)

        # Log handler failures
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                handler = matching_handlers[i]
                logger.error(f"Handler {handler.handler_id} failed: {str(result)}")

    async def _execute_handler_with_retry(self, handler: EventHandler, event: Event):
        """Execute handler with retry logic"""
        max_retries = handler.retry_config.get("max_retries", 3)
        backoff_multiplier = handler.retry_config.get("backoff_multiplier", 2)

        for attempt in range(max_retries + 1):
            try:
                success = await handler.handle_event(event)
                if success:
                    return

                if attempt < max_retries:
                    wait_time = backoff_multiplier**attempt
                    await asyncio.sleep(wait_time)

            except Exception as e:
                if attempt == max_retries:
                    # Send to dead letter queue
                    await self._dead_letter_queue.put(
                        {
                            "event": event,
                            "handler_id": handler.handler_id,
                            "error": str(e),
                            "attempts": attempt + 1,
                        }
                    )
                    raise

                # Wait before retry
                wait_time = backoff_multiplier**attempt
                await asyncio.sleep(wait_time)


# Enterprise Event Analytics
class EventAnalytics:
    """
    Event analytics for enterprise observability.
    Future: Real-time dashboards, ML-powered insights
    """

    def __init__(self, event_service: EventService):
        self.event_service = event_service

    async def get_event_volume_by_type(self, hours: int = 24) -> Dict[str, int]:
        """Get event volume by type over time period"""
        since = datetime.utcnow() - timedelta(hours=hours)
        volume = {}

        for event_type in EventType:
            events = await self.event_service.get_events(
                event_type=event_type, since=since
            )
            volume[event_type.value] = len(events)

        return volume

    async def get_error_rate(self, hours: int = 24) -> float:
        """Calculate error rate over time period"""
        since = datetime.utcnow() - timedelta(hours=hours)

        total_events = 0
        error_events = 0

        for event_type in [
            EventType.TASK_FAILED,
            EventType.ENGINE_ERROR,
            EventType.PROVIDER_ERROR,
        ]:
            events = await self.event_service.get_events(
                event_type=event_type, since=since
            )
            error_events += len(events)

        # Get total task events for comparison
        for event_type in [
            EventType.TASK_SUBMITTED,
            EventType.TASK_COMPLETED,
            EventType.TASK_FAILED,
        ]:
            events = await self.event_service.get_events(
                event_type=event_type, since=since
            )
            total_events += len(events)

        return (error_events / total_events * 100) if total_events > 0 else 0.0
