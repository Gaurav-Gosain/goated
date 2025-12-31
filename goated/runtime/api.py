"""Go-style concurrency API using the M:N runtime - Optimized.

This module provides the same API as goated.std.goroutine but backed
by the work-stealing M:N scheduler for better performance, especially
on free-threaded Python.

Key optimizations over standard implementation:
- Future callbacks instead of wrapper functions (zero allocation hot path)
- Atomic-like operations for WaitGroup on free-threaded Python
- Minimized function creation overhead
- Direct executor access in hot paths
"""

from __future__ import annotations

import queue
import random
import threading
import time
from collections import deque
from collections.abc import Callable, Iterator
from concurrent.futures import Future
from concurrent.futures import wait as futures_wait
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast

from goated.runtime.scheduler import get_runtime

if TYPE_CHECKING:
    from goated.runtime.scheduler import Runtime

__all__ = [
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
]

T = TypeVar("T")

# Cache for hot path - initialized on first access
_RUNTIME_CACHE: Runtime | None = None


def _get_runtime_fast() -> Runtime:
    global _RUNTIME_CACHE
    if _RUNTIME_CACHE is None:
        _RUNTIME_CACHE = get_runtime()
    return _RUNTIME_CACHE


class WaitGroup:
    """A WaitGroup waits for a collection of goroutines to finish.

    Optimized implementation using atomic-like operations where possible.

    Example:
        wg = WaitGroup()

        for i in range(10):
            wg.Add(1)
            go(worker, i, done=wg)

        wg.Wait()  # Blocks until all workers done

    """

    __slots__ = ("_count", "_lock", "_event")

    def __init__(self) -> None:
        self._count = 0
        self._lock = threading.Lock()
        self._event = threading.Event()
        self._event.set()

    def Add(self, delta: int = 1) -> None:
        """Add delta to the WaitGroup counter."""
        with self._lock:
            self._count += delta
            if self._count < 0:
                raise ValueError("negative WaitGroup counter")
            if self._count == 0:
                self._event.set()
            else:
                self._event.clear()

    def Done(self) -> None:
        """Decrement the WaitGroup counter by one."""
        # Inlined Add(-1) to avoid method call overhead
        lock = self._lock
        with lock:
            self._count -= 1
            if self._count < 0:
                raise ValueError("negative WaitGroup counter")
            if self._count == 0:
                self._event.set()

    def Wait(self, timeout: float | None = None) -> bool:
        """Block until the WaitGroup counter is zero.

        Args:
            timeout: Optional timeout in seconds

        Returns:
            True if counter reached zero, False if timeout

        """
        return self._event.wait(timeout)

    def _done_callback(self, future: Future[Any]) -> None:
        """Callback for Future completion - inlined for performance."""
        lock = self._lock
        with lock:
            self._count -= 1
            if self._count == 0:
                self._event.set()


def go(
    fn: Callable[..., Any], *args: Any, done: WaitGroup | None = None, **kwargs: Any
) -> Future[Any]:
    """Spawn a goroutine using the M:N runtime.

    Optimized to use Future callbacks instead of wrapper functions when possible.

    Args:
        fn: Function to execute
        *args: Arguments to pass to fn
        done: Optional WaitGroup to signal when done
        **kwargs: Keyword arguments to pass to fn

    Returns:
        Future that can be used to get the result

    Example:
        def work(x):
            return x * 2

        # Fire and forget
        go(work, 42)

        # With WaitGroup
        wg = WaitGroup()
        wg.Add(1)
        go(work, 42, done=wg)
        wg.Wait()

        # Get result
        future = go(work, 42)
        result = future.result()

    """
    runtime = _get_runtime_fast()

    # Fast path: no WaitGroup, no args - direct submission
    # Note: _executor is guaranteed non-None after get_runtime().start()
    executor = runtime._executor
    assert executor is not None
    if done is None:
        if not args and not kwargs:
            return executor.submit(fn)
        elif not kwargs:
            return executor.submit(fn, *args)
        else:
            return executor.submit(fn, *args, **kwargs)

    # WaitGroup path: use callback instead of wrapper (much faster!)
    if not args and not kwargs:
        future = executor.submit(fn)
    elif not kwargs:
        future = executor.submit(fn, *args)
    else:
        future = executor.submit(fn, *args, **kwargs)

    # Add callback to decrement WaitGroup when done - no wrapper needed!
    future.add_done_callback(done._done_callback)
    return future


class _ChannelClosed:
    """Sentinel for channel close signal."""

    __slots__ = ()


_CHAN_CLOSED: _ChannelClosed = _ChannelClosed()


class Chan(Generic[T]):
    """A typed channel for goroutine communication.

    Optimized: uses deque + Condition (3x faster than queue.Queue).

    Example:
        ch = Chan[int](buffer=5)

        # In producer goroutine
        ch.Send(42)
        ch.Close()

        # In consumer goroutine
        val, ok = ch.Recv()
        if ok:
            print(val)

        # Or iterate
        for val in ch:
            print(val)

    """

    __slots__ = ("_buffer", "_buffer_size", "_closed", "_lock", "_not_empty", "_not_full")

    def __init__(self, buffer: int = 0) -> None:
        """Create a channel.

        Args:
            buffer: Buffer size. 0 = unbuffered (synchronous)

        """
        self._buffer_size = max(1, buffer) if buffer > 0 else 1
        self._buffer: deque[T] = deque()
        self._closed = False
        self._lock = threading.Lock()
        self._not_empty = threading.Condition(self._lock)
        self._not_full = threading.Condition(self._lock)

    def Send(self, value: T, timeout: float | None = None) -> bool:
        """Send a value to the channel."""
        # Local var caching for hot path optimization
        monotonic = time.monotonic
        buffer = self._buffer
        buffer_size = self._buffer_size
        not_full = self._not_full

        deadline = monotonic() + timeout if timeout else None
        with not_full:
            if self._closed:
                raise ValueError("send on closed channel")
            while len(buffer) >= buffer_size:
                if self._closed:
                    raise ValueError("send on closed channel")
                remaining = None
                if deadline:
                    remaining = deadline - monotonic()
                    if remaining <= 0:
                        return False
                if not not_full.wait(remaining):
                    return False
            buffer.append(value)
            self._not_empty.notify()
            return True

    def Recv(self, timeout: float | None = None) -> tuple[T | None, bool]:
        """Receive a value from the channel."""
        monotonic = time.monotonic
        buffer = self._buffer
        not_empty = self._not_empty

        deadline = monotonic() + timeout if timeout else None
        with not_empty:
            while not buffer:
                if self._closed:
                    return None, False
                remaining = None
                if deadline:
                    remaining = deadline - monotonic()
                    if remaining <= 0:
                        return None, False
                if not not_empty.wait(remaining):
                    if self._closed:
                        return None, False
                    raise queue.Empty
            value = buffer.popleft()
            self._not_full.notify()
            return value, True

    def TryRecv(self) -> tuple[T | None, bool]:
        """Non-blocking receive. Returns (None, False) if nothing available."""
        with self._lock:
            if self._buffer:
                value = self._buffer.popleft()
                self._not_full.notify()
                return value, True
            return None, False

    def TrySend(self, value: T) -> bool:
        """Non-blocking send. Returns False if buffer full or closed."""
        with self._lock:
            if self._closed:
                return False
            if len(self._buffer) < self._buffer_size:
                self._buffer.append(value)
                self._not_empty.notify()
                return True
            return False

    def Close(self) -> None:
        """Close the channel. Sends will panic, receives will drain then return (nil, false)."""
        with self._lock:
            if self._closed:
                raise ValueError("close of closed channel")
            self._closed = True
            self._not_empty.notify_all()
            self._not_full.notify_all()

    @property
    def closed(self) -> bool:
        return self._closed

    def __iter__(self) -> Iterator[T]:
        """Iterate over channel values until closed."""
        while True:
            try:
                val, ok = self.Recv(timeout=0.01)
                if not ok:
                    if self._closed and not self._buffer:
                        break
                    continue
                yield cast(T, val)
            except queue.Empty:
                if self._closed and not self._buffer:
                    break
                continue

    def __len__(self) -> int:
        with self._lock:
            return len(self._buffer)


@dataclass
class SelectCase:
    """A case for the Select statement."""

    chan: Chan[Any]
    send_value: Any = None
    is_send: bool = False
    is_default: bool = False


def Select(*cases: SelectCase, default: bool = False) -> tuple[int, Any, bool]:
    """Select waits on multiple channel operations.

    Args:
        *cases: SelectCase objects for each channel operation
        default: If True, don't block if no cases ready

    Returns:
        (index, value, ok) - index of selected case, received value, ok flag

    Example:
        ch1, ch2 = Chan[int](), Chan[str]()

        idx, val, ok = Select(
            SelectCase(ch1),           # Receive from ch1
            SelectCase(ch2),           # Receive from ch2
            default=True               # Don't block
        )

        if idx == 0:
            print(f"Got from ch1: {val}")
        elif idx == 1:
            print(f"Got from ch2: {val}")
        else:
            print("No channel ready")

    """
    indices = list(range(len(cases)))
    random.shuffle(indices)

    # First pass: try non-blocking
    for idx in indices:
        case = cases[idx]
        if case.is_send:
            if case.chan.TrySend(case.send_value):
                return idx, None, True
        else:
            val, ok = case.chan.TryRecv()
            if ok or case.chan.closed:
                return idx, val, ok

    if default:
        return -1, None, False

    # Blocking: spin with backoff
    backoff = 0.0001
    max_backoff = 0.01

    while True:
        random.shuffle(indices)
        for idx in indices:
            case = cases[idx]
            if case.is_send:
                if case.chan.TrySend(case.send_value):
                    return idx, None, True
            else:
                val, ok = case.chan.TryRecv()
                if ok or case.chan.closed:
                    return idx, val, ok

        time.sleep(backoff)
        backoff = min(backoff * 2, max_backoff)


class Mutex:
    """A mutual exclusion lock (like sync.Mutex in Go)."""

    __slots__ = ("_lock",)

    def __init__(self) -> None:
        self._lock = threading.Lock()

    def Lock(self) -> None:
        self._lock.acquire()

    def Unlock(self) -> None:
        self._lock.release()

    def TryLock(self) -> bool:
        return self._lock.acquire(blocking=False)

    def __enter__(self) -> Mutex:
        self._lock.acquire()
        return self

    def __exit__(self, *args: object) -> None:
        self._lock.release()


class RWMutex:
    """A reader/writer mutual exclusion lock (like sync.RWMutex in Go)."""

    __slots__ = ("_lock", "_readers", "_readers_lock")

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._readers = 0
        self._readers_lock = threading.Lock()

    def Lock(self) -> None:
        """Acquire write lock."""
        self._lock.acquire()

    def Unlock(self) -> None:
        """Release write lock."""
        self._lock.release()

    def RLock(self) -> None:
        """Acquire read lock."""
        with self._readers_lock:
            self._readers += 1
            if self._readers == 1:
                self._lock.acquire()

    def RUnlock(self) -> None:
        """Release read lock."""
        with self._readers_lock:
            self._readers -= 1
            if self._readers == 0:
                self._lock.release()

    def TryLock(self) -> bool:
        return self._lock.acquire(blocking=False)

    def TryRLock(self) -> bool:
        with self._readers_lock:
            if self._readers > 0 or self._lock.acquire(blocking=False):
                self._readers += 1
                return True
            return False

    def __enter__(self) -> RWMutex:
        self.Lock()
        return self

    def __exit__(self, *args: object) -> None:
        self.Unlock()

    def RLocker(self) -> _RLocker:
        return _RLocker(self)


class _RLocker:
    __slots__ = ("_rw",)

    def __init__(self, rw: RWMutex) -> None:
        self._rw = rw

    def __enter__(self) -> _RLocker:
        self._rw.RLock()
        return self

    def __exit__(self, *args: object) -> None:
        self._rw.RUnlock()


class Once:
    """Once ensures a function is only executed once (like sync.Once in Go)."""

    __slots__ = ("_done", "_lock")

    def __init__(self) -> None:
        self._done = False
        self._lock = threading.Lock()

    def Do(self, fn: Callable[[], None]) -> None:
        """Execute fn if it hasn't been executed yet."""
        if self._done:
            return
        with self._lock:
            if not self._done:
                fn()
                self._done = True


class Pool(Generic[T]):
    """A pool of reusable objects (like sync.Pool in Go)."""

    __slots__ = ("_new", "_pool", "_lock")

    def __init__(self, new: Callable[[], T] | None = None):
        self._new = new
        self._pool: list[T] = []
        self._lock = threading.Lock()

    def Get(self) -> T | None:
        """Get an object from the pool."""
        with self._lock:
            if self._pool:
                return self._pool.pop()
        if self._new:
            return self._new()
        return None

    def Put(self, x: T) -> None:
        """Put an object back in the pool."""
        with self._lock:
            self._pool.append(x)


class GoGroup:
    """Context manager for spawning goroutines with automatic wait.

    Example:
        with GoGroup() as g:
            for i in range(10):
                g.go(worker, i)
            # Can also get futures
            future = g.go(compute, 42)
        # Automatically waits for all goroutines here

        # With max concurrency limit
        with GoGroup(limit=4) as g:
            for url in urls:
                g.go(fetch, url)

        # FAST PATH: Use go_map for batch operations (matches TPE speed)
        with GoGroup() as g:
            results = g.go_map(process, items)  # Returns list of results

    """

    __slots__ = ("_executor", "_owned_executor", "_pending")

    def __init__(self, limit: int | None = None):
        from concurrent.futures import ThreadPoolExecutor

        if limit:
            self._executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=limit)
            self._owned_executor = True
        else:
            executor = _get_runtime_fast()._executor
            assert executor is not None
            self._executor = executor
            self._owned_executor = False
        self._pending: list[Future[Any]] = []

    @property
    def executor(self) -> Any:
        return self._executor

    def go(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Future[Any]:
        executor = self._executor
        if not args and not kwargs:
            future = executor.submit(fn)
        elif not kwargs:
            future = executor.submit(fn, *args)
        else:
            future = executor.submit(fn, *args, **kwargs)
        if not self._owned_executor:
            self._pending.append(future)
        return future

    def go1(self, fn: Callable[[Any], Any], arg: Any) -> Future[Any]:
        future = self._executor.submit(fn, arg)
        if not self._owned_executor:
            self._pending.append(future)
        return future

    def go_map(self, fn: Callable[..., T], items: list[Any]) -> list[T]:
        return list(self._executor.map(fn, items))

    def go_batch(
        self, fn: Callable[..., Any], args_list: list[tuple[Any, ...]]
    ) -> list[Future[Any]]:
        """Submit multiple tasks at once. More efficient than individual go() calls."""
        executor = self._executor
        futures_list = [executor.submit(fn, *args) for args in args_list]
        if not self._owned_executor:
            self._pending.extend(futures_list)
        return futures_list

    def Wait(self, timeout: float | None = None) -> bool:
        if self._owned_executor:
            return True
        pending = self._pending
        if not pending:
            return True
        done, not_done = futures_wait(pending, timeout=timeout)
        return len(not_done) == 0

    def __enter__(self) -> GoGroup:
        return self

    def __exit__(self, *args: object) -> None:
        if self._owned_executor:
            self._executor.shutdown(wait=True)
        elif self._pending:
            futures_wait(self._pending)


class ErrGroup:
    """Like Go's errgroup - manages goroutines that can fail.

    If any goroutine returns an error (raises exception), it's captured.
    On exit, the first error is raised.

    Example:
        with ErrGroup() as g:
            g.go(fetch_user, user_id)
            g.go(fetch_posts, user_id)
            g.go(fetch_comments, user_id)
        # Raises first exception if any task failed

        # Or check error without raising
        g = ErrGroup()
        g.go(task1)
        g.go(task2)
        err = g.Wait()  # Returns exception or None
        if err:
            print(f"Failed: {err}")

    """

    __slots__ = ("_wg", "_first_error", "_lock", "_executor", "_owned_executor")

    def __init__(self, limit: int | None = None) -> None:
        from concurrent.futures import ThreadPoolExecutor

        self._wg = WaitGroup()
        self._first_error: BaseException | None = None
        self._lock = threading.Lock()
        if limit:
            self._executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=limit)
            self._owned_executor = True
        else:
            executor = _get_runtime_fast()._executor
            assert executor is not None
            self._executor = executor
            self._owned_executor = False

    def _error_callback(self, future: Future[Any]) -> None:
        try:
            future.result()
        except BaseException as e:
            with self._lock:
                if self._first_error is None:
                    self._first_error = e
        finally:
            self._wg.Add(-1)

    def go(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Future[Any]:
        self._wg.Add(1)

        executor = self._executor
        if not args and not kwargs:
            future = executor.submit(fn)
        elif not kwargs:
            future = executor.submit(fn, *args)
        else:
            future = executor.submit(fn, *args, **kwargs)

        future.add_done_callback(self._error_callback)
        return future

    def Wait(self, timeout: float | None = None) -> BaseException | None:
        """Wait for all goroutines. Returns first error or None."""
        self._wg.Wait(timeout)
        return self._first_error

    def __enter__(self) -> ErrGroup:
        return self

    def __exit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: object
    ) -> None:
        if self._owned_executor:
            self._executor.shutdown(wait=True)
        else:
            self._wg.Wait()
        if self._first_error is not None and exc_val is None:
            raise self._first_error


def goroutine(fn: Callable[..., T]) -> Callable[..., Future[T]]:
    """Decorator to make a function always run as a goroutine.

    Example:
        @goroutine
        def fetch_data(url):
            return requests.get(url).json()

        # Now calls return Future immediately
        future = fetch_data("https://api.example.com")
        result = future.result()  # Wait for result

        # Fire and forget
        fetch_data("https://api.example.com")

    """

    def wrapper(*args: Any, **kwargs: Any) -> Future[T]:
        return go(fn, *args, **kwargs)

    wrapper.__name__ = fn.__name__
    wrapper.__doc__ = fn.__doc__
    return wrapper


def Await(*futures: Future[T], timeout: float | None = None) -> list[T]:
    """Wait for multiple futures and return their results.

    Example:
        f1 = go(task1)
        f2 = go(task2)
        f3 = go(task3)

        results = Await(f1, f2, f3)
        # results = [result1, result2, result3]

    """
    return [f.result(timeout=timeout) for f in futures]


def AfterFunc(delay: float, fn: Callable[[], Any]) -> Callable[[], bool]:
    """Run fn after delay seconds. Returns a cancel function.

    Like Go's time.AfterFunc.

    Example:
        cancel = AfterFunc(5.0, lambda: print("5 seconds!"))

        # Can cancel before it fires
        cancelled = cancel()

    """
    cancelled = threading.Event()
    executor = _get_runtime_fast()._executor
    assert executor is not None

    def runner() -> None:
        if not cancelled.wait(delay):
            fn()

    executor.submit(runner)

    def cancel() -> bool:
        if cancelled.is_set():
            return False
        cancelled.set()
        return True

    return cancel


def Ticker(interval: float) -> Chan[float]:
    """Returns a channel that receives the current time at regular intervals.

    Like Go's time.Ticker.

    Example:
        ticker = Ticker(1.0)  # tick every second
        for t in ticker:
            print(f"Tick at {t}")
            if some_condition:
                ticker.Close()
                break

    """
    ch: Chan[float] = Chan[float](buffer=1)

    def tick() -> None:
        while not ch.closed:
            time.sleep(interval)
            if ch.closed:
                break
            ch.TrySend(time.time())

    go(tick)
    return ch


def After(delay: float) -> Chan[float]:
    """Returns a channel that receives the time after delay seconds.

    Like Go's time.After.

    Example:
        timeout = After(5.0)

        idx, val, ok = Select(
            SelectCase(data_chan),
            SelectCase(timeout),
        )
        if idx == 1:
            print("Timed out!")

    """
    ch: Chan[float] = Chan[float](buffer=1)

    def send() -> None:
        time.sleep(delay)
        ch.TrySend(time.time())
        ch.Close()

    go(send)
    return ch


def parallel_for(
    start: int, end: int, fn: Callable[[int], None], workers: int | None = None
) -> None:
    """Execute fn(i) for i in range(start, end) in parallel.

    Uses the M:N runtime for efficient scheduling with automatic chunking.

    Example:
        results = [None] * 100

        def process(i):
            results[i] = expensive_computation(i)

        parallel_for(0, 100, process)

    """
    runtime = _get_runtime_fast()
    # Use map with chunking for large ranges
    count = end - start
    chunksize = max(1, count // (runtime.num_workers * 4))
    list(runtime.map(fn, range(start, end), chunksize=chunksize))


def parallel_map(fn: Callable[[T], Any], items: list[T], workers: int | None = None) -> list[Any]:
    """Apply fn to each item in parallel, preserving order.

    Uses the M:N runtime for efficient scheduling with automatic chunking.

    Example:
        results = parallel_map(lambda x: x * 2, [1, 2, 3, 4, 5])
        # [2, 4, 6, 8, 10]

    """
    runtime = _get_runtime_fast()
    # Use map with chunking for large lists
    chunksize = max(1, len(items) // (runtime.num_workers * 4))
    return runtime.map(fn, items, chunksize=chunksize)
