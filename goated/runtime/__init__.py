"""M:N Goroutine-style runtime for Python.

A work-stealing scheduler that multiplexes M lightweight goroutines
onto N OS threads. Optimized for free-threaded Python (3.13t+) but
works on any Python version.

Key Features:
- Work-stealing for load balancing across workers
- Per-worker task queues for cache locality
- Adaptive to free-threaded Python (no GIL)
- Same API as goated.std.goroutine

Example:
    from goated.runtime import go, WaitGroup, Chan, GoGroup

    # Fire and forget
    go(lambda: print("Hello from goroutine!"))

    # With WaitGroup
    wg = WaitGroup()
    for i in range(10):
        wg.Add(1)
        go(worker, i, done=wg)
    wg.Wait()

    # With GoGroup (automatic tracking)
    with GoGroup() as g:
        for url in urls:
            g.go(fetch, url)
    # Automatically waits here

"""

from goated.runtime.api import (
    After,
    AfterFunc,
    Await,
    Chan,
    ErrGroup,
    GoGroup,
    Mutex,
    Once,
    Pool,
    RWMutex,
    Select,
    SelectCase,
    Ticker,
    WaitGroup,
    go,
    goroutine,
    parallel_for,
    parallel_map,
)
from goated.runtime.channel import (
    FastChan,
    MPMCQueue,
    chan,
)
from goated.runtime.scheduler import (
    Runtime,
    get_runtime,
    is_free_threaded,
    runtime_stats,
    shutdown_runtime,
)

__all__ = [
    # Runtime management
    "Runtime",
    "get_runtime",
    "shutdown_runtime",
    "runtime_stats",
    "is_free_threaded",
    # Go-style API
    "go",
    "WaitGroup",
    "Chan",
    "Select",
    "SelectCase",
    "Mutex",
    "RWMutex",
    "Once",
    "Pool",
    "GoGroup",
    "ErrGroup",
    "goroutine",
    "Await",
    "AfterFunc",
    "Ticker",
    "After",
    "parallel_for",
    "parallel_map",
    # Optimized channels
    "FastChan",
    "MPMCQueue",
    "chan",
]
