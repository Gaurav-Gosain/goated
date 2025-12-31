"""Go-style concurrency primitives for Python.

Provides goroutine-like spawning, WaitGroups, and channels with
Go's simple, elegant API.

This module now uses the optimized M:N runtime backend, which provides:
- Work-stealing for load balancing across workers
- Optimized for free-threaded Python (3.13t+)
- Better performance for CPU-bound workloads

Example:
    from goated.std.goroutine import go, WaitGroup, Chan

    # Simple goroutine spawning
    def worker(id):
        print(f"Worker {id} running")

    wg = WaitGroup()
    for i in range(5):
        wg.Add(1)
        go(worker, i, done=wg)
    wg.Wait()

    # With channels
    ch = Chan[int](buffer=10)

    def producer():
        for i in range(10):
            ch.Send(i)
        ch.Close()

    go(producer)
    for val in ch:
        print(val)

"""

# Re-export everything from the optimized runtime
# This maintains backward compatibility while using the new backend
from goated.runtime import (
    After,
    AfterFunc,
    Await,
    Chan,
    ErrGroup,
    # Optimized channels (new)
    FastChan,
    # Group helpers
    GoGroup,
    # Sync primitives
    Mutex,
    Once,
    Pool,
    RWMutex,
    Select,
    SelectCase,
    Ticker,
    WaitGroup,
    # Runtime management (new)
    get_runtime,
    # Core API
    go,
    # Decorators and utilities
    goroutine,
    is_free_threaded,
    # Parallel helpers
    parallel_for,
    parallel_map,
    runtime_stats,
    shutdown_runtime,
)

__all__ = [
    # Core API
    "go",
    "WaitGroup",
    "Chan",
    "Select",
    "SelectCase",
    # Sync primitives
    "Mutex",
    "RWMutex",
    "Once",
    "Pool",
    # Group helpers
    "GoGroup",
    "ErrGroup",
    # Decorators and utilities
    "goroutine",
    "Await",
    "AfterFunc",
    "Ticker",
    "After",
    # Parallel helpers
    "parallel_for",
    "parallel_map",
    # Optimized channels (new)
    "FastChan",
    # Runtime management (new)
    "get_runtime",
    "shutdown_runtime",
    "runtime_stats",
    "is_free_threaded",
]
