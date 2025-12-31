"""Go sync package bindings - Pure Python implementation.

This module provides Python bindings for Go's sync package synchronization
primitives.

Example:
    >>> from goated.std import sync
    >>>
    >>> # Mutex
    >>> mu = sync.Mutex()
    >>> mu.Lock()
    >>> # critical section
    >>> mu.Unlock()
    >>>
    >>> # WaitGroup
    >>> wg = sync.WaitGroup()
    >>> wg.Add(2)
    >>> # ... spawn workers that call wg.Done() ...
    >>> wg.Wait()

"""

from __future__ import annotations

import asyncio
import threading
from collections.abc import Callable
from typing import Any, Generic, TypeVar

__all__ = [
    "Mutex",
    "RWMutex",
    "WaitGroup",
    "Once",
    "Cond",
    "Pool",
    "Map",
]

T = TypeVar("T")


# =============================================================================
# Mutex
# =============================================================================


class Mutex:
    """A Mutex is a mutual exclusion lock.

    A Mutex must not be copied after first use.

    Example:
        >>> mu = Mutex()
        >>> mu.Lock()
        >>> try:
        ...     # critical section
        ...     pass
        ... finally:
        ...     mu.Unlock()

    """

    __slots__ = ("_lock",)

    def __init__(self) -> None:
        self._lock = threading.Lock()

    def Lock(self) -> None:
        """Lock locks the mutex."""
        self._lock.acquire()

    def Unlock(self) -> None:
        """Unlock unlocks the mutex."""
        self._lock.release()

    def TryLock(self) -> bool:
        """TryLock tries to lock the mutex and returns whether it succeeded."""
        return self._lock.acquire(blocking=False)

    def __enter__(self) -> Mutex:
        self.Lock()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        self.Unlock()


class RWMutex:
    """A RWMutex is a reader/writer mutual exclusion lock.

    The lock can be held by an arbitrary number of readers or a single writer.

    Example:
        >>> rw = RWMutex()
        >>>
        >>> # For reading
        >>> rw.RLock()
        >>> try:
        ...     # read data
        ...     pass
        ... finally:
        ...     rw.RUnlock()
        >>>
        >>> # For writing
        >>> rw.Lock()
        >>> try:
        ...     # write data
        ...     pass
        ... finally:
        ...     rw.Unlock()

    """

    __slots__ = ("_lock",)

    def __init__(self) -> None:
        self._lock = threading.RLock()

    def Lock(self) -> None:
        """Lock locks rw for writing."""
        self._lock.acquire()

    def Unlock(self) -> None:
        """Unlock unlocks rw for writing."""
        self._lock.release()

    def TryLock(self) -> bool:
        """TryLock tries to lock rw for writing and returns whether it succeeded."""
        return self._lock.acquire(blocking=False)

    def RLock(self) -> None:
        """RLock locks rw for reading."""
        self._lock.acquire()

    def RUnlock(self) -> None:
        """RUnlock undoes a single RLock call."""
        self._lock.release()

    def TryRLock(self) -> bool:
        """TryRLock tries to lock rw for reading and returns whether it succeeded."""
        return self._lock.acquire(blocking=False)


# =============================================================================
# WaitGroup
# =============================================================================


class WaitGroup:
    """A WaitGroup waits for a collection of goroutines to finish.

    Example:
        >>> wg = WaitGroup()
        >>>
        >>> def worker(id):
        ...     print(f"Worker {id} done")
        ...     wg.Done()
        >>>
        >>> for i in range(3):
        ...     wg.Add(1)
        ...     threading.Thread(target=worker, args=(i,)).start()
        >>>
        >>> wg.Wait()
        >>> print("All workers done")

    """

    __slots__ = ("_counter", "_lock", "_event")

    def __init__(self) -> None:
        self._counter = 0
        self._lock = threading.Lock()
        self._event = threading.Event()
        self._event.set()  # Initially no waiters

    def Add(self, delta: int) -> None:
        """Add adds delta to the WaitGroup counter.

        If the counter becomes zero, all goroutines blocked on Wait are released.
        If the counter goes negative, Add panics.
        """
        with self._lock:
            self._counter += delta
            if self._counter < 0:
                raise ValueError("sync: negative WaitGroup counter")
            if self._counter == 0:
                self._event.set()
            else:
                self._event.clear()

    def Done(self) -> None:
        """Done decrements the WaitGroup counter by one."""
        self.Add(-1)

    def Wait(self) -> None:
        """Wait blocks until the WaitGroup counter is zero."""
        self._event.wait()

    async def WaitAsync(self) -> None:
        """Async version of Wait."""
        while True:
            with self._lock:
                if self._counter == 0:
                    return
            await asyncio.sleep(0.001)


# =============================================================================
# Once
# =============================================================================


class Once:
    """Once is an object that will perform exactly one action.

    Example:
        >>> once = Once()
        >>>
        >>> def initialize():
        ...     print("Initializing...")
        >>>
        >>> once.Do(initialize)  # Prints "Initializing..."
        >>> once.Do(initialize)  # Does nothing
        >>> once.Do(initialize)  # Does nothing

    """

    __slots__ = ("_done", "_lock")

    def __init__(self) -> None:
        self._done = False
        self._lock = threading.Lock()

    def Do(self, f: Callable[[], None]) -> None:
        """Do calls the function f if and only if Do is being called for
        the first time for this instance of Once.
        """
        if self._done:
            return

        with self._lock:
            if self._done:
                return
            try:
                f()
            finally:
                self._done = True


# =============================================================================
# Cond
# =============================================================================


class Cond:
    """Cond implements a condition variable, a rendezvous point for goroutines
    waiting for or announcing the occurrence of an event.

    Example:
        >>> mu = Mutex()
        >>> cond = Cond(mu)
        >>>
        >>> # Waiter
        >>> def waiter():
        ...     cond.L.Lock()
        ...     while not ready:
        ...         cond.Wait()
        ...     cond.L.Unlock()
        >>>
        >>> # Signaler
        >>> def signaler():
        ...     cond.L.Lock()
        ...     ready = True
        ...     cond.Signal()
        ...     cond.L.Unlock()

    """

    __slots__ = ("L", "_cond")

    def __init__(self, lock: Mutex):
        self.L = lock
        self._cond = threading.Condition(lock._lock)

    def Wait(self) -> None:
        """Wait atomically unlocks c.L and suspends execution of the calling
        goroutine. After later resuming execution, Wait locks c.L before
        returning.
        """
        self._cond.wait()

    def Signal(self) -> None:
        """Signal wakes one goroutine waiting on c, if there is any."""
        self._cond.notify()

    def Broadcast(self) -> None:
        """Broadcast wakes all goroutines waiting on c."""
        self._cond.notify_all()


# =============================================================================
# Pool
# =============================================================================


class Pool(Generic[T]):
    """A Pool is a set of temporary objects that may be individually saved and
    retrieved.

    Pool's purpose is to cache allocated but unused items for later reuse,
    relieving pressure on the garbage collector.

    Example:
        >>> pool = Pool(lambda: [0] * 1024)  # Create a pool of 1KB buffers
        >>>
        >>> buf = pool.Get()
        >>> # ... use buf ...
        >>> pool.Put(buf)

    """

    __slots__ = ("_new", "_items", "_lock")

    def __init__(self, new: Callable[[], T] | None = None):
        self._new = new
        self._items: list[T] = []
        self._lock = threading.Lock()

    def Get(self) -> T | None:
        """Get selects an arbitrary item from the Pool, removes it from the Pool,
        and returns it to the caller.
        """
        with self._lock:
            if self._items:
                return self._items.pop()

        if self._new:
            return self._new()

        return None

    def Put(self, x: T) -> None:
        """Put adds x to the pool."""
        if x is None:
            return

        with self._lock:
            self._items.append(x)


# =============================================================================
# Map
# =============================================================================


class Map(Generic[T]):
    """Map is like a Go map[any]any but is safe for concurrent use.

    Example:
        >>> m = Map()
        >>> m.Store("key", "value")
        >>> val, ok = m.Load("key")
        >>> print(val, ok)
        value True

    """

    __slots__ = ("_data", "_lock")

    def __init__(self) -> None:
        self._data: dict[Any, T] = {}
        self._lock = threading.RLock()

    def Load(self, key: Any) -> tuple[T | None, bool]:
        """Load returns the value stored in the map for a key, or None if no
        value is present.

        The ok result indicates whether value was found in the map.
        """
        with self._lock:
            if key in self._data:
                return self._data[key], True
            return None, False

    def Store(self, key: Any, value: T) -> None:
        """Store sets the value for a key."""
        with self._lock:
            self._data[key] = value

    def LoadOrStore(self, key: Any, value: T) -> tuple[T, bool]:
        """LoadOrStore returns the existing value for the key if present.
        Otherwise, it stores and returns the given value.

        The loaded result is true if the value was loaded, false if stored.
        """
        with self._lock:
            if key in self._data:
                return self._data[key], True
            self._data[key] = value
            return value, False

    def LoadAndDelete(self, key: Any) -> tuple[T | None, bool]:
        """LoadAndDelete deletes the value for a key, returning the previous
        value if any.

        The loaded result reports whether the key was present.
        """
        with self._lock:
            if key in self._data:
                value = self._data.pop(key)
                return value, True
            return None, False

    def Delete(self, key: Any) -> None:
        """Delete deletes the value for a key."""
        with self._lock:
            self._data.pop(key, None)

    def Swap(self, key: Any, value: T) -> tuple[T | None, bool]:
        """Swap swaps the value for a key and returns the previous value if any.

        The loaded result reports whether the key was present.
        """
        with self._lock:
            previous = self._data.get(key)
            loaded = key in self._data
            self._data[key] = value
            return previous, loaded

    def CompareAndSwap(self, key: Any, old: T, new: T) -> bool:
        """CompareAndSwap swaps the old and new values for key if the value
        stored in the map is equal to old.

        Returns true if the swap was performed.
        """
        with self._lock:
            if key in self._data and self._data[key] == old:
                self._data[key] = new
                return True
            return False

    def CompareAndDelete(self, key: Any, old: T) -> bool:
        """CompareAndDelete deletes the entry for key if its value is equal to old.

        Returns true if the entry was deleted.
        """
        with self._lock:
            if key in self._data and self._data[key] == old:
                del self._data[key]
                return True
            return False

    def Range(self, f: Callable[[Any, T], bool]) -> None:
        """Range calls f sequentially for each key and value present in the map.

        If f returns false, range stops the iteration.
        """
        with self._lock:
            items = list(self._data.items())

        for key, value in items:
            if not f(key, value):
                break

    def Clear(self) -> None:
        """Clear deletes all entries from the map."""
        with self._lock:
            self._data.clear()

    def Len(self) -> int:
        """Return the number of items in the map."""
        with self._lock:
            return len(self._data)
