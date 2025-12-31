"""Optimized channel implementations.

Provides multiple channel implementations:
- Chan: Standard thread-safe channel (works everywhere)
- FastChan: Optimized for free-threaded Python with reduced contention
- MPMCQueue: Multi-producer multi-consumer queue using ring buffer
"""

from __future__ import annotations

import threading
import time
from collections import deque
from collections.abc import Iterator
from typing import Any, Generic, TypeVar

__all__ = ["FastChan", "MPMCQueue", "chan"]

T = TypeVar("T")


class FastChan(Generic[T]):
    """High-performance channel optimized for free-threaded Python.

    Streamlined implementation using condition variables for blocking.
    Equivalent to Chan but kept for API compatibility.

    Features:
    - Efficient condition variables for blocking
    - Bounded buffer with backpressure
    - Local variable caching in hot paths

    Example:
        ch = FastChan[int](buffer=100)

        # Producer
        for i in range(100):
            ch.Send(i)
        ch.Close()

        # Consumer
        for val in ch:
            process(val)

    """

    __slots__ = (
        "_buffer",
        "_buffer_size",
        "_closed",
        "_lock",
        "_not_empty",
        "_not_full",
    )

    def __init__(self, buffer: int = 0):
        """Create a fast channel.

        Args:
            buffer: Buffer size. 0 = unbuffered

        """
        self._buffer_size = max(1, buffer)
        self._buffer: deque[T] = deque(maxlen=self._buffer_size if buffer > 0 else None)
        self._closed = False

        # Main lock and conditions
        self._lock = threading.Lock()
        self._not_empty = threading.Condition(self._lock)
        self._not_full = threading.Condition(self._lock)

    def Send(self, value: T, timeout: float | None = None) -> bool:
        """Send a value to the channel.

        Blocks if buffer is full until space is available or timeout.

        Args:
            value: Value to send
            timeout: Max time to wait (None = forever)

        Returns:
            True if sent, False on timeout

        Raises:
            ValueError: If channel is closed

        """
        deadline = time.monotonic() + timeout if timeout else None

        with self._not_full:
            while True:
                if self._closed:
                    raise ValueError("send on closed channel")

                if len(self._buffer) < self._buffer_size:
                    self._buffer.append(value)
                    self._not_empty.notify()
                    return True

                # Buffer full - wait
                remaining = None
                if deadline:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        return False

                if not self._not_full.wait(remaining):
                    return False

    def Recv(self, timeout: float | None = None) -> tuple[T | None, bool]:
        """Receive a value from the channel.

        Blocks if buffer is empty until value is available or timeout.

        Args:
            timeout: Max time to wait (None = forever)

        Returns:
            (value, True) on success, (None, False) if closed and empty

        """
        deadline = time.monotonic() + timeout if timeout else None

        with self._not_empty:
            while True:
                if self._buffer:
                    value = self._buffer.popleft()
                    self._not_full.notify()
                    return value, True

                if self._closed:
                    return None, False

                # Buffer empty - wait
                remaining = None
                if deadline:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        return None, False

                if not self._not_empty.wait(remaining):
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

    def TryRecv(self) -> tuple[T | None, bool]:
        """Non-blocking receive. Returns (None, False) if empty."""
        with self._lock:
            if self._buffer:
                value = self._buffer.popleft()
                self._not_full.notify()
                return value, True
            return None, False

    def Close(self) -> None:
        """Close the channel."""
        with self._lock:
            if self._closed:
                raise ValueError("close of closed channel")
            self._closed = True
            self._not_empty.notify_all()
            self._not_full.notify_all()

    @property
    def closed(self) -> bool:
        return self._closed

    def __len__(self) -> int:
        with self._lock:
            return len(self._buffer)

    def __iter__(self) -> Iterator[T]:
        """Iterate over channel values until closed."""
        while True:
            value, ok = self.Recv(timeout=0.1)
            if not ok:
                # Check if truly closed or just timeout
                with self._lock:
                    if self._closed and not self._buffer:
                        break
                continue
            if value is not None:
                yield value


class MPMCQueue(Generic[T]):
    """Multi-producer multi-consumer bounded queue.

    Uses a ring buffer with separate head/tail locks for better
    concurrency on free-threaded Python.

    This is a lower-level primitive - use FastChan for channel semantics.
    """

    __slots__ = (
        "_buffer",
        "_capacity",
        "_head",
        "_tail",
        "_size",
        "_head_lock",
        "_tail_lock",
        "_size_lock",
        "_not_empty",
        "_not_full",
    )

    def __init__(self, capacity: int):
        if capacity < 1:
            raise ValueError("capacity must be positive")

        self._capacity = capacity
        self._buffer: list[T | None] = [None] * capacity
        self._head = 0  # Consumer index
        self._tail = 0  # Producer index
        self._size = 0

        # Separate locks for head and tail
        self._head_lock = threading.Lock()
        self._tail_lock = threading.Lock()
        self._size_lock = threading.Lock()

        # Conditions for blocking
        self._not_empty = threading.Condition(self._size_lock)
        self._not_full = threading.Condition(self._size_lock)

    def put(self, item: T, timeout: float | None = None) -> bool:
        """Add an item to the queue.

        Returns:
            True if added, False on timeout

        """
        deadline = time.monotonic() + timeout if timeout else None

        with self._not_full:
            while self._size >= self._capacity:
                remaining = None
                if deadline:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        return False
                if not self._not_full.wait(remaining):
                    return False

            # Got space - acquire tail lock
            with self._tail_lock:
                self._buffer[self._tail] = item
                self._tail = (self._tail + 1) % self._capacity

            self._size += 1
            self._not_empty.notify()
            return True

    def get(self, timeout: float | None = None) -> tuple[T | None, bool]:
        """Remove and return an item.

        Returns:
            (item, True) on success, (None, False) on timeout

        """
        deadline = time.monotonic() + timeout if timeout else None

        with self._not_empty:
            while self._size == 0:
                remaining = None
                if deadline:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        return None, False
                if not self._not_empty.wait(remaining):
                    return None, False

            # Got item - acquire head lock
            with self._head_lock:
                item = self._buffer[self._head]
                self._buffer[self._head] = None  # Help GC
                self._head = (self._head + 1) % self._capacity

            self._size -= 1
            self._not_full.notify()
            return item, True

    def try_put(self, item: T) -> bool:
        """Non-blocking put."""
        with self._size_lock:
            if self._size >= self._capacity:
                return False

            with self._tail_lock:
                self._buffer[self._tail] = item
                self._tail = (self._tail + 1) % self._capacity

            self._size += 1
            self._not_empty.notify()
            return True

    def try_get(self) -> tuple[T | None, bool]:
        """Non-blocking get."""
        with self._size_lock:
            if self._size == 0:
                return None, False

            with self._head_lock:
                item = self._buffer[self._head]
                self._buffer[self._head] = None
                self._head = (self._head + 1) % self._capacity

            self._size -= 1
            self._not_full.notify()
            return item, True

    def __len__(self) -> int:
        return self._size


def chan(buffer: int = 0) -> FastChan[Any]:
    """Create a channel (factory function for Go-like syntax).

    Example:
        ch = chan(10)  # buffered channel with capacity 10
        ch = chan()    # unbuffered channel

    """
    return FastChan(buffer=buffer)
