"""Go-style concurrency API using the M:N runtime - Optimized.

This module provides the same API as goated.std.goroutine but backed
by the work-stealing M:N scheduler for better performance, especially
on free-threaded Python.

Key optimizations over standard implementation:
- Future callbacks instead of wrapper functions (zero allocation hot path)
- Atomic-like operations for WaitGroup on free-threaded Python
- Minimized function creation overhead
- Direct executor access in hot paths
- Proper condition-variable-based Select (no spin-wait)
- True unbuffered channel rendezvous semantics
- Correct reader-writer lock with writer preference
"""

from __future__ import annotations

import functools
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
    "Semaphore",
    "pipe",
    "merge",
    "fan_out",
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

# Global registry for Select notification: channels notify waiting Selects
_select_waiters_lock = threading.Lock()
_select_waiters: list[threading.Condition] = []


def _notify_select_waiters() -> None:
    """Wake any Select statements waiting on channel activity."""
    with _select_waiters_lock:
        for cond in _select_waiters:
            with cond:
                cond.notify_all()


class Chan(Generic[T]):
    """A typed channel for goroutine communication.

    Supports both buffered and true unbuffered (rendezvous) channels.
    Unbuffered channels (buffer=0) require sender and receiver to meet:
    the sender blocks until a receiver is ready, and vice versa.

    Optimized: uses deque + Condition (3x faster than queue.Queue).
    Iterators block properly on condition variables (no polling).

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

    __slots__ = (
        "_buffer",
        "_buffer_size",
        "_unbuffered",
        "_closed",
        "_lock",
        "_not_empty",
        "_not_full",
        "_rendezvous",
        "_rendezvous_value",
        "_rendezvous_taken",
    )

    def __init__(self, buffer: int = 0) -> None:
        """Create a channel.

        Args:
            buffer: Buffer size. 0 = unbuffered (synchronous rendezvous)

        """
        self._unbuffered = buffer <= 0
        self._buffer_size = max(buffer, 0)
        self._buffer: deque[T] = deque()
        self._closed = False
        self._lock = threading.Lock()
        self._not_empty = threading.Condition(self._lock)
        self._not_full = threading.Condition(self._lock)
        # Rendezvous state for unbuffered channels
        self._rendezvous: threading.Condition = threading.Condition(self._lock)
        self._rendezvous_value: T | _ChannelClosed = _CHAN_CLOSED  # sentinel = no value
        self._rendezvous_taken = False

    def Send(self, value: T, timeout: float | None = None) -> bool:
        """Send a value to the channel.

        For unbuffered channels, blocks until a receiver takes the value.
        For buffered channels, blocks only when the buffer is full.
        """
        monotonic = time.monotonic
        deadline = monotonic() + timeout if timeout is not None else None

        if self._unbuffered:
            return self._send_unbuffered(value, deadline, monotonic)
        return self._send_buffered(value, deadline, monotonic)

    def _send_buffered(
        self, value: T, deadline: float | None, monotonic: Callable[[], float]
    ) -> bool:
        buffer = self._buffer
        buffer_size = self._buffer_size
        not_full = self._not_full

        with not_full:
            if self._closed:
                raise ValueError("send on closed channel")
            while len(buffer) >= buffer_size:
                if self._closed:
                    raise ValueError("send on closed channel")
                remaining = None
                if deadline is not None:
                    remaining = deadline - monotonic()
                    if remaining <= 0:
                        return False
                if not not_full.wait(remaining):
                    return False
            buffer.append(value)
            self._not_empty.notify()
            _notify_select_waiters()
            return True

    def _send_unbuffered(
        self, value: T, deadline: float | None, monotonic: Callable[[], float]
    ) -> bool:
        """True unbuffered send: block until a receiver takes the value."""
        with self._lock:
            if self._closed:
                raise ValueError("send on closed channel")
            # Wait for any previous rendezvous to complete
            while self._rendezvous_value is not _CHAN_CLOSED and not self._rendezvous_taken:
                self._rendezvous.wait(0.01)
            # Place value and wait for receiver to take it
            self._rendezvous_value = value
            self._rendezvous_taken = False
            self._not_empty.notify()
            _notify_select_waiters()
            # Wait until receiver picks up the value
            while not self._rendezvous_taken:
                if self._closed:
                    raise ValueError("send on closed channel")
                remaining = None
                if deadline is not None:
                    remaining = deadline - monotonic()
                    if remaining <= 0:
                        self._rendezvous_value = _CHAN_CLOSED
                        return False
                self._rendezvous.wait(remaining)
            return True

    def Recv(self, timeout: float | None = None) -> tuple[T | None, bool]:
        """Receive a value from the channel.

        For unbuffered channels, completes the rendezvous with the sender.
        """
        monotonic = time.monotonic
        deadline = monotonic() + timeout if timeout is not None else None

        if self._unbuffered:
            return self._recv_unbuffered(deadline, monotonic)
        return self._recv_buffered(deadline, monotonic)

    def _recv_buffered(
        self, deadline: float | None, monotonic: Callable[[], float]
    ) -> tuple[T | None, bool]:
        buffer = self._buffer
        not_empty = self._not_empty

        with not_empty:
            while not buffer:
                if self._closed:
                    return None, False
                remaining = None
                if deadline is not None:
                    remaining = deadline - monotonic()
                    if remaining <= 0:
                        return None, False
                if not not_empty.wait(remaining):
                    if self._closed:
                        return None, False
                    return None, False
            value = buffer.popleft()
            self._not_full.notify()
            _notify_select_waiters()
            return value, True

    def _recv_unbuffered(
        self, deadline: float | None, monotonic: Callable[[], float]
    ) -> tuple[T | None, bool]:
        """True unbuffered recv: wait for sender, then take the value."""
        with self._lock:
            # Wait for a sender to place a value (not sentinel AND not yet taken)
            while True:
                if self._rendezvous_value is not _CHAN_CLOSED and not self._rendezvous_taken:
                    break  # A sender has placed a value, take it
                if self._closed:
                    return None, False
                remaining = None
                if deadline is not None:
                    remaining = deadline - monotonic()
                    if remaining <= 0:
                        return None, False
                self._not_empty.wait(remaining)
            # Take the value and notify sender
            value = cast(T, self._rendezvous_value)
            self._rendezvous_value = _CHAN_CLOSED
            self._rendezvous_taken = True
            self._rendezvous.notify()
            _notify_select_waiters()
            return value, True

    def TryRecv(self) -> tuple[T | None, bool]:
        """Non-blocking receive. Returns (None, False) if nothing available."""
        with self._lock:
            if self._unbuffered:
                if self._rendezvous_value is not _CHAN_CLOSED and not self._rendezvous_taken:
                    value = cast(T, self._rendezvous_value)
                    self._rendezvous_value = _CHAN_CLOSED
                    self._rendezvous_taken = True
                    self._rendezvous.notify()
                    _notify_select_waiters()
                    return value, True
                return None, False
            if self._buffer:
                value = self._buffer.popleft()
                self._not_full.notify()
                _notify_select_waiters()
                return value, True
            return None, False

    def TrySend(self, value: T) -> bool:
        """Non-blocking send. Returns False if buffer full or closed."""
        with self._lock:
            if self._closed:
                return False
            if self._unbuffered:
                # Can only succeed if a receiver is already waiting
                # For TrySend on unbuffered, we use the buffer as a handoff slot
                # This is inherently racy; return False (Go semantics: TrySend on
                # unbuffered only succeeds if a goroutine is blocked in Recv)
                return False
            if len(self._buffer) < self._buffer_size:
                self._buffer.append(value)
                self._not_empty.notify()
                _notify_select_waiters()
                return True
            return False

    def Close(self) -> None:
        """Close the channel. Sends will panic, receives drain then return (nil, false)."""
        with self._lock:
            if self._closed:
                raise ValueError("close of closed channel")
            self._closed = True
            self._not_empty.notify_all()
            self._not_full.notify_all()
            self._rendezvous.notify_all()
            _notify_select_waiters()

    @property
    def closed(self) -> bool:
        return self._closed

    def __iter__(self) -> Iterator[T]:
        """Iterate over channel values until closed and drained.

        Blocks properly on condition variables - no polling.
        """
        while True:
            val, ok = self.Recv()
            if not ok:
                break
            yield cast(T, val)

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

    Uses condition-variable notification instead of spin-wait for zero
    CPU waste and minimal latency.

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

    # Blocking path: register a condition variable and wait for notification
    # from any channel involved in this Select.
    cond = threading.Condition()
    with _select_waiters_lock:
        _select_waiters.append(cond)

    try:
        with cond:
            while True:
                # Try all cases (randomized for fairness)
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
                # Wait for any channel to notify us
                cond.wait(timeout=0.1)
    finally:
        with _select_waiters_lock:
            if cond in _select_waiters:
                _select_waiters.remove(cond)


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
    """A reader/writer mutual exclusion lock (like sync.RWMutex in Go).

    Supports concurrent reads but exclusive writes. Uses writer-preference
    to prevent writer starvation: when a writer is waiting, new readers
    block until the writer completes.
    """

    __slots__ = ("_state_lock", "_readers", "_writer_waiting", "_no_readers", "_write_lock")

    def __init__(self) -> None:
        self._state_lock = threading.Lock()
        self._readers = 0
        self._writer_waiting = False
        self._no_readers = threading.Event()
        self._no_readers.set()  # Initially no readers
        self._write_lock = threading.Lock()

    def Lock(self) -> None:
        """Acquire write lock. Blocks new readers and waits for existing ones."""
        self._write_lock.acquire()
        with self._state_lock:
            self._writer_waiting = True
        # Wait for all current readers to finish
        self._no_readers.wait()

    def Unlock(self) -> None:
        """Release write lock."""
        with self._state_lock:
            self._writer_waiting = False
        self._write_lock.release()

    def RLock(self) -> None:
        """Acquire read lock. Blocks if a writer is waiting or holding the lock."""
        # If a writer is waiting/holding, we must wait for it
        self._write_lock.acquire()
        with self._state_lock:
            self._readers += 1
            self._no_readers.clear()
        self._write_lock.release()

    def RUnlock(self) -> None:
        """Release read lock."""
        with self._state_lock:
            self._readers -= 1
            if self._readers == 0:
                self._no_readers.set()

    def TryLock(self) -> bool:
        """Try to acquire write lock without blocking."""
        if not self._write_lock.acquire(blocking=False):
            return False
        with self._state_lock:
            if self._readers > 0:
                self._write_lock.release()
                return False
            self._writer_waiting = True
        return True

    def TryRLock(self) -> bool:
        """Try to acquire read lock without blocking."""
        if not self._write_lock.acquire(blocking=False):
            return False
        with self._state_lock:
            self._readers += 1
            self._no_readers.clear()
        self._write_lock.release()
        return True

    def __enter__(self) -> RWMutex:
        self.Lock()
        return self

    def __exit__(self, *args: object) -> None:
        self.Unlock()

    def RLocker(self) -> _RLocker:
        """Return a context manager for read locking."""
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
    """A pool of reusable objects (like sync.Pool in Go).

    Uses thread-local storage for a fast path: each thread keeps one
    cached object that can be Get/Put without locking. Overflow goes
    to a shared pool protected by a lock.
    """

    __slots__ = ("_new", "_shared", "_lock", "_local")

    def __init__(self, new: Callable[[], T] | None = None):
        self._new = new
        self._shared: list[T] = []
        self._lock = threading.Lock()
        self._local = threading.local()

    def Get(self) -> T | None:
        """Get an object from the pool. Thread-local fast path first."""
        # Fast path: check thread-local cache (no lock)
        local = self._local
        obj = getattr(local, "cached", None)
        if obj is not None:
            local.cached = None
            return obj
        # Slow path: shared pool
        with self._lock:
            if self._shared:
                return self._shared.pop()
        if self._new:
            return self._new()
        return None

    def Put(self, x: T) -> None:
        """Put an object back in the pool. Thread-local fast path first."""
        # Fast path: store in thread-local if empty
        local = self._local
        if getattr(local, "cached", None) is None:
            local.cached = x
            return
        # Slow path: shared pool
        with self._lock:
            self._shared.append(x)


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

    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Future[T]:
        return go(fn, *args, **kwargs)

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


class Semaphore:
    """A counting semaphore for limiting concurrent access (like a weighted sync primitive).

    Useful for rate limiting or bounding concurrency to N simultaneous operations.

    Example:
        sem = Semaphore(3)  # Allow 3 concurrent operations

        def worker(id):
            with sem:
                do_work(id)

        with GoGroup() as g:
            for i in range(100):
                g.go(worker, i)  # Only 3 run at a time

    """

    __slots__ = ("_value", "_lock", "_condition")

    def __init__(self, value: int = 1) -> None:
        if value < 0:
            raise ValueError("semaphore initial value must be >= 0")
        self._value = value
        self._lock = threading.Lock()
        self._condition = threading.Condition(self._lock)

    def Acquire(self, n: int = 1, timeout: float | None = None) -> bool:
        """Acquire n permits. Blocks until available or timeout."""
        monotonic = time.monotonic
        deadline = monotonic() + timeout if timeout is not None else None
        with self._condition:
            while self._value < n:
                remaining = None
                if deadline is not None:
                    remaining = deadline - monotonic()
                    if remaining <= 0:
                        return False
                if not self._condition.wait(remaining):
                    return False
            self._value -= n
            return True

    def Release(self, n: int = 1) -> None:
        """Release n permits."""
        with self._condition:
            self._value += n
            self._condition.notify_all()

    def TryAcquire(self, n: int = 1) -> bool:
        """Try to acquire n permits without blocking."""
        with self._lock:
            if self._value >= n:
                self._value -= n
                return True
            return False

    def __enter__(self) -> Semaphore:
        self.Acquire()
        return self

    def __exit__(self, *args: object) -> None:
        self.Release()


def pipe(
    src: Chan[T],
    fn: Callable[[T], Any],
    dst: Chan[Any] | None = None,
    buffer: int = 0,
    workers: int = 1,
) -> Chan[Any]:
    """Pipe values from src through fn into dst (created if not provided).

    Creates a processing pipeline stage. Each value from src is transformed
    by fn and sent to dst. Closes dst when src is drained.

    Args:
        src: Source channel
        fn: Transform function
        dst: Destination channel (created if None)
        buffer: Buffer size for created dst channel
        workers: Number of concurrent workers processing the pipe

    Returns:
        The destination channel

    Example:
        ch1 = Chan[int](buffer=10)
        ch2 = pipe(ch1, lambda x: x * 2)
        ch3 = pipe(ch2, lambda x: str(x))

        # Producer
        for i in range(10):
            ch1.Send(i)
        ch1.Close()

        # Consumer
        for val in ch3:
            print(val)  # "0", "2", "4", ...

    """
    if dst is None:
        dst = Chan[Any](buffer=buffer)

    out = dst

    def _worker() -> None:
        for val in src:
            result = fn(val)
            out.Send(result)

    def _run() -> None:
        if workers <= 1:
            _worker()
        else:
            wg = WaitGroup()
            for _ in range(workers):
                wg.Add(1)
                go(_worker, done=wg)
            wg.Wait()
        out.Close()

    go(_run)
    return out


def merge(*channels: Chan[T], buffer: int = 0) -> Chan[T]:
    """Fan-in: merge multiple channels into one.

    Values from all source channels are forwarded to the output channel.
    Output is closed when all sources are closed.

    Args:
        *channels: Source channels to merge
        buffer: Buffer size for the output channel

    Returns:
        Merged output channel

    Example:
        ch1 = Chan[int](buffer=5)
        ch2 = Chan[int](buffer=5)

        merged = merge(ch1, ch2)

        # Producers write to ch1 and ch2
        # Consumer reads from merged
        for val in merged:
            print(val)

    """
    out: Chan[T] = Chan[T](buffer=buffer)

    def _forward(src: Chan[T]) -> None:
        for val in src:
            out.Send(val)

    def _run() -> None:
        wg = WaitGroup()
        for ch in channels:
            wg.Add(1)
            go(_forward, ch, done=wg)
        wg.Wait()
        out.Close()

    go(_run)
    return out


def fan_out(
    src: Chan[T],
    n: int,
    buffer: int = 0,
) -> list[Chan[T]]:
    """Fan-out: distribute values from one channel to N output channels.

    Values are distributed round-robin across output channels.
    All outputs are closed when the source is drained.

    Args:
        src: Source channel
        n: Number of output channels
        buffer: Buffer size for each output channel

    Returns:
        List of output channels

    Example:
        jobs = Chan[int](buffer=100)
        worker_chans = fan_out(jobs, 4, buffer=10)

        # Each worker_chan gets ~1/4 of the jobs
        for i, ch in enumerate(worker_chans):
            go(worker, i, ch)

    """
    outputs: list[Chan[T]] = [Chan[T](buffer=buffer) for _ in range(n)]

    def _distribute() -> None:
        idx = 0
        for val in src:
            outputs[idx % n].Send(val)
            idx += 1
        for ch in outputs:
            ch.Close()

    go(_distribute)
    return outputs


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
