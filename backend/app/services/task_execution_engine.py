"""
Task Execution Engine with enterprise event-driven architecture.
Built for MVP simplicity, designed for enterprise orchestration scale.
"""

import asyncio
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from app.core.interfaces import AgentConfig, TaskResult, TaskStatus

logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """Task execution priority levels"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class TaskType(Enum):
    """Types of tasks the engine can execute"""

    COMPLETION = "completion"  # AI text completion
    ANALYSIS = "analysis"  # Data analysis
    WORKFLOW = "workflow"  # Multi-step workflow
    INTEGRATION = "integration"  # External system integration
    CUSTOM = "custom"  # Custom task type


@dataclass
class TaskDefinition:
    """
    Complete task definition for execution.

    Current: Basic task parameters
    Future: Complex workflow definitions, dependencies
    """

    task_id: str
    task_type: TaskType
    priority: TaskPriority

    # Task execution parameters
    agent_config: AgentConfig
    input_data: Dict[str, Any]

    # Enterprise features
    tenant_id: Optional[str] = None
    user_id: Optional[str] = None

    # Execution constraints
    timeout_seconds: int = 300
    max_retries: int = 3

    # Dependencies and workflow
    depends_on: Optional[List[str]] = None  # Task IDs this task depends on
    callback_url: Optional[str] = None

    # Metadata
    created_at: Optional[datetime] = None
    scheduled_for: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.depends_on is None:
            self.depends_on = []


@dataclass
class TaskExecution:
    """
    Task execution state and history.

    Current: Basic execution tracking
    Future: Detailed performance metrics, cost tracking
    """

    task_id: str
    definition: TaskDefinition

    # Execution state
    status: TaskStatus
    current_attempt: int = 0

    # Timing
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Results and errors
    result: Optional[TaskResult] = None
    error_history: Optional[List[str]] = None

    # Enterprise metrics
    execution_node: Optional[str] = None  # Which worker executed
    cost_estimate: float = 0.0
    token_usage: Optional[Dict[str, int]] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.error_history is None:
            self.error_history = []
        if self.token_usage is None:
            self.token_usage = {}


class TaskQueue:
    """
    Enterprise task queue with priority scheduling.

    Current: In-memory priority queue
    Future: Redis/RabbitMQ with persistence, scaling
    """

    def __init__(self):
        self._queues = {
            TaskPriority.URGENT: asyncio.Queue(),
            TaskPriority.HIGH: asyncio.Queue(),
            TaskPriority.NORMAL: asyncio.Queue(),
            TaskPriority.LOW: asyncio.Queue(),
        }
        self._pending_tasks: Dict[str, TaskExecution] = {}
        self._running_tasks: Dict[str, TaskExecution] = {}
        self._completed_tasks: Dict[str, TaskExecution] = {}

    async def enqueue(self, task_definition: TaskDefinition):
        """Add task to appropriate priority queue"""
        task_execution = TaskExecution(
            task_id=task_definition.task_id,
            definition=task_definition,
            status=TaskStatus.PENDING,
        )

        self._pending_tasks[task_definition.task_id] = task_execution
        await self._queues[task_definition.priority].put(task_execution)

        logger.info(
            f"Task enqueued: {task_definition.task_id} (priority: {task_definition.priority.value})"
        )

    async def dequeue(self) -> Optional[TaskExecution]:
        """Dequeue highest priority task"""
        # Check queues in priority order
        for priority in [
            TaskPriority.URGENT,
            TaskPriority.HIGH,
            TaskPriority.NORMAL,
            TaskPriority.LOW,
        ]:
            queue = self._queues[priority]
            if not queue.empty():
                task_execution: TaskExecution = await queue.get()

                # Move from pending to running
                if task_execution.task_id in self._pending_tasks:
                    del self._pending_tasks[task_execution.task_id]

                self._running_tasks[task_execution.task_id] = task_execution
                task_execution.status = TaskStatus.RUNNING
                task_execution.started_at = datetime.utcnow()

                return task_execution

        return None

    def complete_task(self, task_id: str, result: TaskResult):
        """Mark task as completed"""
        if task_id in self._running_tasks:
            task_execution = self._running_tasks.pop(task_id)
            task_execution.status = result.status
            task_execution.result = result
            task_execution.completed_at = datetime.utcnow()

            # Track enterprise metrics
            if result.cost_estimate:
                task_execution.cost_estimate = result.cost_estimate
            if result.token_usage:
                task_execution.token_usage = result.token_usage

            self._completed_tasks[task_id] = task_execution

    def get_task_status(self, task_id: str) -> Optional[TaskExecution]:
        """Get current task status"""
        for task_dict in [
            self._pending_tasks,
            self._running_tasks,
            self._completed_tasks,
        ]:
            if task_id in task_dict:
                return task_dict[task_id]
        return None

    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics for monitoring"""
        return {
            "pending": {
                priority.value: queue.qsize()
                for priority, queue in self._queues.items()
            },
            "running": len(self._running_tasks),
            "completed": len(self._completed_tasks),
            "total_pending": len(self._pending_tasks),
        }


class TaskExecutionEngine:
    """
    Enterprise Task Execution Engine with event-driven architecture.

    Current: Single-node execution with basic monitoring
    Future: Distributed execution, advanced scheduling, ML optimization
    """

    def __init__(self, event_service=None, max_concurrent_tasks: int = 10):
        self.event_service = event_service
        self.max_concurrent_tasks = max_concurrent_tasks

        # Task management
        self.task_queue = TaskQueue()
        self.task_handlers: Dict[TaskType, Callable] = {}

        # Worker management
        self._worker_tasks: List[asyncio.Task] = []
        self._running = False

        # Enterprise monitoring
        self._metrics = {
            "tasks_executed": 0,
            "tasks_failed": 0,
            "total_execution_time": 0,
            "total_cost": 0.0,
        }

        # Register default task handlers
        self._register_default_handlers()

    async def start(self):
        """Start the execution engine workers"""
        if self._running:
            return

        self._running = True

        # Start worker tasks
        for i in range(self.max_concurrent_tasks):
            worker_task = asyncio.create_task(self._worker_loop(f"worker-{i}"))
            self._worker_tasks.append(worker_task)

        logger.info(
            f"Task execution engine started with {self.max_concurrent_tasks} workers"
        )

        if self.event_service:
            await self.event_service.publish_event(
                {
                    "type": "engine.started",
                    "timestamp": datetime.utcnow().isoformat(),
                    "workers": self.max_concurrent_tasks,
                }
            )

    async def stop(self):
        """Stop the execution engine"""
        self._running = False

        # Cancel worker tasks
        for task in self._worker_tasks:
            task.cancel()

        # Wait for workers to finish
        await asyncio.gather(*self._worker_tasks, return_exceptions=True)
        self._worker_tasks.clear()

        logger.info("Task execution engine stopped")

        if self.event_service:
            await self.event_service.publish_event(
                {"type": "engine.stopped", "timestamp": datetime.utcnow().isoformat()}
            )

    async def submit_task(self, task_definition: TaskDefinition) -> str:
        """
        Submit task for execution.

        Current: Simple task submission
        Future: Dependency resolution, smart scheduling
        """
        try:
            # Validate task definition
            if not await self._validate_task_definition(task_definition):
                raise ValueError(f"Invalid task definition: {task_definition.task_id}")

            # Check dependencies (future: complex dependency resolution)
            if task_definition.depends_on:
                logger.info(
                    f"Task {task_definition.task_id} has dependencies: {task_definition.depends_on}"
                )
                # For now, just log dependencies. Future: wait for completion

            # Enqueue task
            await self.task_queue.enqueue(task_definition)

            # Publish event
            if self.event_service:
                await self.event_service.publish_event(
                    {
                        "type": "task.submitted",
                        "task_id": task_definition.task_id,
                        "task_type": task_definition.task_type.value,
                        "priority": task_definition.priority.value,
                        "tenant_id": task_definition.tenant_id,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )

            return task_definition.task_id

        except Exception as e:
            logger.error(f"Failed to submit task {task_definition.task_id}: {str(e)}")
            raise

    async def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """Get task execution result"""
        task_execution = self.task_queue.get_task_status(task_id)
        return task_execution.result if task_execution else None

    async def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get current task status"""
        task_execution = self.task_queue.get_task_status(task_id)
        return task_execution.status if task_execution else None

    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancel task execution.

        Current: Basic cancellation
        Future: Graceful cancellation, cleanup, rollback
        """
        try:
            task_execution = self.task_queue.get_task_status(task_id)
            if not task_execution:
                return False

            if task_execution.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
                task_execution.status = TaskStatus.CANCELLED
                task_execution.completed_at = datetime.utcnow()

                # Publish event
                if self.event_service:
                    await self.event_service.publish_event(
                        {
                            "type": "task.cancelled",
                            "task_id": task_id,
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    )

                logger.info(f"Task cancelled: {task_id}")
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to cancel task {task_id}: {str(e)}")
            return False

    def register_task_handler(self, task_type: TaskType, handler: Callable):
        """Register custom task handler"""
        self.task_handlers[task_type] = handler
        logger.info(f"Registered handler for task type: {task_type.value}")

    def get_engine_stats(self) -> Dict[str, Any]:
        """Get execution engine statistics"""
        queue_stats = self.task_queue.get_queue_stats()

        return {
            "engine": {
                "running": self._running,
                "workers": len(self._worker_tasks),
                "max_concurrent": self.max_concurrent_tasks,
            },
            "queue": queue_stats,
            "metrics": self._metrics.copy(),
        }

    # Private methods for engine implementation

    async def _worker_loop(self, worker_id: str):
        """Main worker loop for task execution"""
        logger.info(f"Worker started: {worker_id}")

        while self._running:
            try:
                # Get next task
                task_execution = await self.task_queue.dequeue()
                if not task_execution:
                    # No tasks available, wait briefly
                    await asyncio.sleep(0.1)
                    continue

                # Execute task
                await self._execute_task(task_execution, worker_id)

            except asyncio.CancelledError:
                logger.info(f"Worker cancelled: {worker_id}")
                break
            except Exception as e:
                logger.error(f"Worker error in {worker_id}: {str(e)}")
                await asyncio.sleep(1)  # Brief pause on error

        logger.info(f"Worker stopped: {worker_id}")

    async def _execute_task(self, task_execution: TaskExecution, worker_id: str):
        """Execute a single task"""
        task_id = task_execution.task_id
        task_definition = task_execution.definition

        logger.info(f"Executing task: {task_id} on {worker_id}")

        # Check timeout
        timeout = (
            task_definition.timeout_seconds
            if task_definition.timeout_seconds > 0
            else 300
        )  # Default 5 minutes

        try:
            # Set execution node for tracking
            task_execution.execution_node = worker_id

            # Get task handler
            handler = self.task_handlers.get(task_definition.task_type)
            if not handler:
                raise ValueError(
                    f"No handler registered for task type: {task_definition.task_type}"
                )

            # Execute with timeout
            result = await asyncio.wait_for(handler(task_definition), timeout=timeout)

            # Complete task
            self.task_queue.complete_task(task_id, result)

            # Update metrics
            self._update_metrics(task_execution, result)

            # Publish completion event
            if self.event_service:
                await self.event_service.publish_event(
                    {
                        "type": "task.completed",
                        "task_id": task_id,
                        "status": result.status.value,
                        "execution_time_ms": result.execution_time_ms,
                        "worker_id": worker_id,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )

            logger.info(f"Task completed: {task_id} ({result.status.value})")

        except asyncio.TimeoutError:
            error_msg = f"Task timeout after {timeout} seconds"
            await self._handle_task_error(task_execution, error_msg, worker_id)

        except Exception as e:
            error_msg = f"Task execution error: {str(e)}"
            await self._handle_task_error(task_execution, error_msg, worker_id)

    async def _handle_task_error(
        self, task_execution: TaskExecution, error_msg: str, worker_id: str
    ):
        """Handle task execution errors with retry logic"""
        task_id = task_execution.task_id
        task_definition = task_execution.definition

        task_execution.current_attempt += 1
        if task_execution.error_history is None:
            task_execution.error_history = []
        task_execution.error_history.append(error_msg)

        logger.error(
            f"Task error: {task_id} - {error_msg} (attempt {task_execution.current_attempt})"
        )

        # Check if we should retry
        if task_execution.current_attempt < task_definition.max_retries:
            logger.info(
                f"Retrying task: {task_id} (attempt {task_execution.current_attempt + 1})"
            )

            # Reset execution state for retry
            task_execution.status = TaskStatus.PENDING
            task_execution.started_at = None

            # Re-enqueue for retry (with delay)
            await asyncio.sleep(
                min(2**task_execution.current_attempt, 30)
            )  # Exponential backoff
            await self.task_queue.enqueue(task_definition)

            return

        # Max retries exceeded - mark as failed
        failed_result = TaskResult(
            task_id=task_id,
            status=TaskStatus.FAILED,
            error_message=error_msg,
            started_at=task_execution.started_at or datetime.utcnow(),
            completed_at=datetime.utcnow(),
        )

        self.task_queue.complete_task(task_id, failed_result)
        self._metrics["tasks_failed"] += 1

        # Publish failure event
        if self.event_service:
            await self.event_service.publish_event(
                {
                    "type": "task.failed",
                    "task_id": task_id,
                    "error": error_msg,
                    "attempts": task_execution.current_attempt,
                    "worker_id": worker_id,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

    def _register_default_handlers(self):
        """Register default task handlers"""
        self.task_handlers[TaskType.COMPLETION] = self._handle_completion_task
        self.task_handlers[TaskType.ANALYSIS] = self._handle_analysis_task
        # Future: Add more default handlers

    async def _handle_completion_task(
        self, task_definition: TaskDefinition
    ) -> TaskResult:
        """Handle AI completion tasks (placeholder)"""
        # Future: Integrate with AI provider service
        await asyncio.sleep(0.1)  # Simulate processing

        return TaskResult(
            task_id=task_definition.task_id,
            status=TaskStatus.COMPLETED,
            result={"message": "Completion task placeholder"},
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            execution_time_ms=100,
        )

    async def _handle_analysis_task(
        self, task_definition: TaskDefinition
    ) -> TaskResult:
        """Handle analysis tasks (placeholder)"""
        # Future: Integrate with analytics service
        await asyncio.sleep(0.1)  # Simulate processing

        return TaskResult(
            task_id=task_definition.task_id,
            status=TaskStatus.COMPLETED,
            result={"analysis": "Analysis task placeholder"},
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            execution_time_ms=100,
        )

    async def _validate_task_definition(self, task_definition: TaskDefinition) -> bool:
        """Validate task definition"""
        if not task_definition.task_id:
            return False

        if not task_definition.agent_config:
            return False

        if task_definition.timeout_seconds < 0:
            return False

        return True

    def _update_metrics(self, task_execution: TaskExecution, result: TaskResult):
        """Update execution metrics"""
        self._metrics["tasks_executed"] += 1

        if result.execution_time_ms:
            self._metrics["total_execution_time"] += result.execution_time_ms

        if result.cost_estimate:
            self._metrics["total_cost"] += result.cost_estimate


# Utility functions for task creation
def create_completion_task(
    prompt: str,
    agent_config: AgentConfig,
    priority: TaskPriority = TaskPriority.NORMAL,
    tenant_id: Optional[str] = None,
) -> TaskDefinition:
    """Create a completion task definition"""
    return TaskDefinition(
        task_id=str(uuid.uuid4()),
        task_type=TaskType.COMPLETION,
        priority=priority,
        agent_config=agent_config,
        input_data={"prompt": prompt},
        tenant_id=tenant_id,
    )


def create_analysis_task(
    data: Dict[str, Any],
    analysis_type: str,
    agent_config: AgentConfig,
    priority: TaskPriority = TaskPriority.NORMAL,
    tenant_id: Optional[str] = None,
) -> TaskDefinition:
    """Create an analysis task definition"""
    return TaskDefinition(
        task_id=str(uuid.uuid4()),
        task_type=TaskType.ANALYSIS,
        priority=priority,
        agent_config=agent_config,
        input_data={"data": data, "analysis_type": analysis_type},
        tenant_id=tenant_id,
    )
