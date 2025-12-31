#!/usr/bin/env python3
"""Task queue with worker pool pattern using goated channels.

Demonstrates:
- Worker pool pattern with channels
- Graceful shutdown
- Task prioritization
- Result aggregation
- Error handling in workers
"""

import random
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any

from goated.std import fmt
from goated.std.goroutine import Chan, Mutex, go


class Priority(IntEnum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class Task:
    id: int
    name: str
    payload: Any
    priority: Priority = Priority.NORMAL
    created_at: float = field(default_factory=time.time)


@dataclass
class TaskResult:
    task_id: int
    success: bool
    result: Any = None
    error: str | None = None
    duration_ms: int = 0


class WorkerPool:
    """A pool of workers processing tasks from a channel."""

    def __init__(self, num_workers: int, task_handler: Callable[[Task], Any]):
        self.num_workers = num_workers
        self.task_handler = task_handler
        self.tasks: Chan[Task] = Chan[Task](buffer=100)
        self.results: Chan[TaskResult] = Chan[TaskResult](buffer=100)
        self._running = False
        self._stats_lock = Mutex()
        self._processed = 0
        self._errors = 0

    def _worker(self, worker_id: int) -> None:
        """Worker goroutine that processes tasks."""
        for task in self.tasks:
            start = time.perf_counter_ns()
            try:
                result = self.task_handler(task)
                duration_ms = int((time.perf_counter_ns() - start) / 1_000_000)

                self.results.Send(
                    TaskResult(
                        task_id=task.id,
                        success=True,
                        result=result,
                        duration_ms=duration_ms,
                    )
                )

                with self._stats_lock:
                    self._processed += 1

            except Exception as e:
                duration_ms = int((time.perf_counter_ns() - start) / 1_000_000)

                self.results.Send(
                    TaskResult(
                        task_id=task.id,
                        success=False,
                        error=str(e),
                        duration_ms=duration_ms,
                    )
                )

                with self._stats_lock:
                    self._processed += 1
                    self._errors += 1

    def start(self) -> None:
        """Start the worker pool."""
        self._running = True
        for i in range(self.num_workers):
            go(self._worker, i)

    def submit(self, task: Task) -> None:
        """Submit a task to the pool."""
        self.tasks.Send(task)

    def submit_batch(self, tasks: list[Task]) -> None:
        """Submit multiple tasks."""
        for task in tasks:
            self.tasks.Send(task)

    def shutdown(self, wait_for_results: bool = True) -> list[TaskResult]:
        """Shutdown the pool and optionally wait for all results."""
        self.tasks.Close()

        if wait_for_results:
            time.sleep(0.1)
            self.results.Close()

            results = []
            for r in self.results:
                results.append(r)
            return results

        return []

    @property
    def stats(self) -> tuple[int, int]:
        """Return (processed, errors) counts."""
        with self._stats_lock:
            return self._processed, self._errors


class PriorityTaskQueue:
    """Task queue with priority support using multiple channels."""

    def __init__(self, num_workers: int, task_handler: Callable[[Task], Any]):
        self.num_workers = num_workers
        self.task_handler = task_handler

        self.critical_tasks: Chan[Task] = Chan[Task](buffer=10)
        self.high_tasks: Chan[Task] = Chan[Task](buffer=50)
        self.normal_tasks: Chan[Task] = Chan[Task](buffer=100)
        self.low_tasks: Chan[Task] = Chan[Task](buffer=200)

        self.results: Chan[TaskResult] = Chan[TaskResult](buffer=500)
        self._stop = False

    def _get_next_task(self) -> Task | None:
        """Get next task by priority (non-blocking check of each queue)."""
        for ch in [self.critical_tasks, self.high_tasks, self.normal_tasks, self.low_tasks]:
            val, ok = ch.TryRecv()
            if ok:
                return val
        return None

    def _worker(self, worker_id: int) -> None:
        """Priority-aware worker."""
        while not self._stop:
            task = self._get_next_task()
            if task is None:
                time.sleep(0.001)
                continue

            start = time.perf_counter_ns()
            try:
                result = self.task_handler(task)
                duration_ms = int((time.perf_counter_ns() - start) / 1_000_000)

                self.results.TrySend(
                    TaskResult(
                        task_id=task.id,
                        success=True,
                        result=result,
                        duration_ms=duration_ms,
                    )
                )
            except Exception as e:
                duration_ms = int((time.perf_counter_ns() - start) / 1_000_000)
                self.results.TrySend(
                    TaskResult(
                        task_id=task.id,
                        success=False,
                        error=str(e),
                        duration_ms=duration_ms,
                    )
                )

    def start(self) -> None:
        """Start workers."""
        for i in range(self.num_workers):
            go(self._worker, i)

    def submit(self, task: Task) -> None:
        """Submit task to appropriate priority queue."""
        if task.priority == Priority.CRITICAL:
            self.critical_tasks.TrySend(task)
        elif task.priority == Priority.HIGH:
            self.high_tasks.TrySend(task)
        elif task.priority == Priority.LOW:
            self.low_tasks.TrySend(task)
        else:
            self.normal_tasks.TrySend(task)

    def shutdown(self) -> None:
        """Signal workers to stop."""
        self._stop = True
        time.sleep(0.1)


def example_basic_worker_pool():
    """Basic worker pool example."""
    print("=" * 60)
    print("  BASIC WORKER POOL")
    print("=" * 60)

    def process_task(task: Task) -> str:
        time.sleep(random.uniform(0.01, 0.05))
        if random.random() < 0.1:
            raise ValueError(f"Random failure for task {task.id}")
        return fmt.Sprintf("Processed: %s", task.name)

    pool = WorkerPool(num_workers=4, task_handler=process_task)
    pool.start()

    tasks = [Task(id=i, name=fmt.Sprintf("task-%d", i), payload={"data": i}) for i in range(20)]

    print(fmt.Sprintf("\n  Submitting %d tasks to 4 workers...", len(tasks)))
    start = time.perf_counter()

    pool.submit_batch(tasks)
    results = pool.shutdown(wait_for_results=True)

    elapsed = time.perf_counter() - start

    success = sum(1 for r in results if r.success)
    failed = sum(1 for r in results if not r.success)
    avg_duration = sum(r.duration_ms for r in results) / len(results) if results else 0

    print(fmt.Sprintf("\n  Results:"))
    print(fmt.Sprintf("    Total:    %d tasks", len(results)))
    print(fmt.Sprintf("    Success:  %d", success))
    print(fmt.Sprintf("    Failed:   %d", failed))
    print(fmt.Sprintf("    Avg time: %.1fms", avg_duration))
    print(fmt.Sprintf("    Elapsed:  %.2fs", elapsed))
    print(fmt.Sprintf("    Rate:     %.1f tasks/sec", len(tasks) / elapsed))


def example_priority_queue():
    """Priority task queue example."""
    print("\n" + "=" * 60)
    print("  PRIORITY TASK QUEUE")
    print("=" * 60)

    processed_order: list[tuple[int, str]] = []
    lock = Mutex()

    def process_task(task: Task) -> str:
        time.sleep(0.01)
        with lock:
            processed_order.append((task.id, task.priority.name))
        return fmt.Sprintf("Done: %s (priority=%s)", task.name, task.priority.name)

    queue = PriorityTaskQueue(num_workers=2, task_handler=process_task)
    queue.start()

    tasks = [
        Task(id=1, name="low-1", payload=None, priority=Priority.LOW),
        Task(id=2, name="low-2", payload=None, priority=Priority.LOW),
        Task(id=3, name="normal-1", payload=None, priority=Priority.NORMAL),
        Task(id=4, name="high-1", payload=None, priority=Priority.HIGH),
        Task(id=5, name="critical-1", payload=None, priority=Priority.CRITICAL),
        Task(id=6, name="normal-2", payload=None, priority=Priority.NORMAL),
        Task(id=7, name="critical-2", payload=None, priority=Priority.CRITICAL),
        Task(id=8, name="high-2", payload=None, priority=Priority.HIGH),
    ]

    print("\n  Submitting tasks with mixed priorities...")
    random.shuffle(tasks)

    for task in tasks:
        queue.submit(task)

    time.sleep(0.2)
    queue.shutdown()

    print("\n  Processing order (higher priority first):")
    for task_id, priority in processed_order:
        print(fmt.Sprintf("    Task %d: %s", task_id, priority))


def example_batch_processing():
    """Batch processing with worker pool."""
    print("\n" + "=" * 60)
    print("  BATCH DATA PROCESSING")
    print("=" * 60)

    data_items = list(range(100))

    def process_batch(task: Task) -> dict:
        items = task.payload
        time.sleep(0.02)
        return {
            "batch_id": task.id,
            "sum": sum(items),
            "count": len(items),
            "avg": sum(items) / len(items) if items else 0,
        }

    pool = WorkerPool(num_workers=8, task_handler=process_batch)
    pool.start()

    batch_size = 10
    batches = [data_items[i : i + batch_size] for i in range(0, len(data_items), batch_size)]

    tasks = [
        Task(id=i, name=fmt.Sprintf("batch-%d", i), payload=batch)
        for i, batch in enumerate(batches)
    ]

    print(
        fmt.Sprintf(
            "\n  Processing %d items in %d batches with 8 workers...", len(data_items), len(batches)
        )
    )

    start = time.perf_counter()
    pool.submit_batch(tasks)
    results = pool.shutdown(wait_for_results=True)
    elapsed = time.perf_counter() - start

    total_sum = sum(r.result["sum"] for r in results if r.success)
    total_count = sum(r.result["count"] for r in results if r.success)

    print(fmt.Sprintf("\n  Results:"))
    print(fmt.Sprintf("    Total items: %d", total_count))
    print(fmt.Sprintf("    Total sum:   %d", total_sum))
    print(fmt.Sprintf("    Expected:    %d", sum(data_items)))
    print(fmt.Sprintf("    Elapsed:     %.3fs", elapsed))


def main():
    print("\n" + "=" * 60)
    print("  TASK QUEUE EXAMPLES")
    print("  Worker pool patterns with goated")
    print("=" * 60 + "\n")

    example_basic_worker_pool()
    example_priority_queue()
    example_batch_processing()

    print("\n" + "=" * 60)
    print("  ALL EXAMPLES COMPLETED")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
