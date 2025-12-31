"""Go channel integration with Python asyncio.

This module provides Channel[T] - a Go channel exposed to Python's async/await.
Channels enable communication between goroutines (spawned via go()) and
Python async coroutines.

Key features:
- Buffered and unbuffered channels
- Async iteration with `async for`
- Select statement for multiplexing
- Seamless asyncio integration

Example:
    >>> import asyncio
    >>> from goated import Channel, go
    >>>
    >>> async def producer(ch: Channel[int]):
    ...     for i in range(5):
    ...         await ch.send(i)
    ...     ch.close()
    >>>
    >>> async def consumer(ch: Channel[int]):
    ...     async for value in ch:
    ...         print(f"Got: {value}")
    >>>
    >>> async def main():
    ...     ch = Channel[int](buffer_size=2)
    ...     await asyncio.gather(producer(ch), consumer(ch))
    >>>
    >>> asyncio.run(main())
    Got: 0
    Got: 1
    Got: 2
    Got: 3
    Got: 4

"""

from __future__ import annotations

import asyncio
from collections import deque
from collections.abc import AsyncIterator, Callable
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Generic, TypeVar, cast

__all__ = ["Channel", "ChannelClosed", "select", "go", "SelectCase", "SelectOp"]

T = TypeVar("T")


class ChannelClosed(Exception):
    """Exception raised when operating on a closed channel.

    Raised when:
    - Sending to a closed channel
    - Receiving from a closed, empty channel
    """

    pass


class SelectOp(Enum):
    """Operation type for select cases."""

    SEND = auto()
    RECV = auto()


@dataclass
class SelectCase(Generic[T]):
    """A case for the select statement.

    Attributes:
        channel: The channel to operate on
        op: The operation (SEND or RECV)
        value: Value to send (for SEND ops)

    """

    channel: Channel[T]
    op: SelectOp
    value: T | None = None


class Channel(Generic[T]):
    """Go-style channel with Python asyncio integration.

    Channels provide a way for concurrent tasks to communicate. They can be
    buffered (with a capacity > 0) or unbuffered (synchronous, capacity = 0).

    Unbuffered channels block the sender until a receiver is ready, and vice versa.
    Buffered channels only block when the buffer is full (send) or empty (recv).

    Attributes:
        buffer_size: Channel buffer capacity (0 = unbuffered)

    Example:
        >>> ch = Channel[int](buffer_size=3)
        >>> await ch.send(42)
        >>> value = await ch.recv()
        >>> print(value)
        42

        >>> # Async iteration
        >>> async for item in ch:
        ...     print(item)

        >>> # Close when done
        >>> ch.close()

    """

    __slots__ = (
        "_buffer_size",
        "_buffer",
        "_closed",
        "_send_event",
        "_recv_event",
        "_lock",
    )

    def __init__(self, buffer_size: int = 0) -> None:
        """Create a new channel.

        Args:
            buffer_size: Buffer capacity. 0 means unbuffered (synchronous).
                        -1 means unlimited buffer.

        Example:
            >>> unbuffered = Channel[int]()  # Synchronous
            >>> buffered = Channel[str](buffer_size=10)
            >>> unlimited = Channel[bytes](buffer_size=-1)

        """
        self._buffer_size = buffer_size
        self._buffer: deque[T] = deque()
        self._closed = False
        self._send_event = asyncio.Event()
        self._recv_event = asyncio.Event()
        self._lock = asyncio.Lock()

    async def send(self, value: T) -> None:
        """Send a value to the channel.

        Blocks until a receiver is ready (unbuffered) or buffer has space.

        Args:
            value: Value to send

        Raises:
            ChannelClosed: If channel is closed

        Example:
            >>> ch = Channel[int](buffer_size=1)
            >>> await ch.send(42)

        """
        while True:
            async with self._lock:
                if self._closed:
                    raise ChannelClosed("send on closed channel")

                # Check if we can send
                can_send = (
                    self._buffer_size == -1  # Unlimited
                    or len(self._buffer) < max(1, self._buffer_size)  # Has space
                )

                if can_send:
                    self._buffer.append(value)
                    self._recv_event.set()  # Signal receivers
                    return

                # Buffer full - clear send event and wait
                self._send_event.clear()

            # Wait for space (outside lock)
            await self._send_event.wait()

    async def recv(self) -> T:
        """Receive a value from the channel.

        Blocks until a value is available.

        Returns:
            The received value

        Raises:
            ChannelClosed: If channel is closed and empty

        Example:
            >>> ch = Channel[int](buffer_size=1)
            >>> await ch.send(42)
            >>> value = await ch.recv()
            >>> print(value)
            42

        """
        while True:
            async with self._lock:
                # Check if we can receive
                if self._buffer:
                    value = self._buffer.popleft()
                    self._send_event.set()  # Signal senders
                    return value

                if self._closed:
                    raise ChannelClosed("recv on closed channel")

                # Buffer empty - clear recv event and wait
                self._recv_event.clear()

            # Wait for data (outside lock)
            await self._recv_event.wait()

    def send_nowait(self, value: T) -> bool:
        """Try to send without blocking.

        Args:
            value: Value to send

        Returns:
            True if sent, False if would block

        Raises:
            ChannelClosed: If channel is closed

        """
        if self._closed:
            raise ChannelClosed("send on closed channel")

        can_send = self._buffer_size == -1 or len(self._buffer) < max(1, self._buffer_size)

        if can_send:
            self._buffer.append(value)
            self._recv_event.set()
            return True
        return False

    def recv_nowait(self) -> T | None:
        """Try to receive without blocking.

        Returns:
            The value if available, None if would block

        Raises:
            ChannelClosed: If channel is closed and empty

        """
        if self._buffer:
            value = self._buffer.popleft()
            self._send_event.set()
            return value

        if self._closed:
            raise ChannelClosed("recv on closed channel")
        return None

    def close(self) -> None:
        """Close the channel.

        After closing:
        - send() will raise ChannelClosed
        - recv() will return remaining buffered items, then raise ChannelClosed

        Example:
            >>> ch = Channel[int]()
            >>> ch.close()
            >>> await ch.send(1)  # Raises ChannelClosed

        """
        self._closed = True
        # Wake up all waiters so they can check closed state
        self._send_event.set()
        self._recv_event.set()

    @property
    def closed(self) -> bool:
        """Return True if channel is closed."""
        return self._closed

    def __len__(self) -> int:
        """Return number of items in buffer."""
        return len(self._buffer)

    async def __aiter__(self) -> AsyncIterator[T]:
        """Async iterate over channel values.

        Yields values until channel is closed.

        Example:
            >>> async for value in ch:
            ...     print(value)

        """
        while True:
            try:
                yield await self.recv()
            except ChannelClosed:
                break

    def __repr__(self) -> str:
        status = "closed" if self._closed else "open"
        return f"Channel[{status}, buf={self._buffer_size}, len={len(self)}]"


async def select(*cases: SelectCase[Any]) -> tuple[int, Any]:
    """Select on multiple channel operations.

    Similar to Go's select statement. Waits until one of the cases is ready,
    then executes it and returns the index and result.

    Args:
        *cases: SelectCase objects describing the operations

    Returns:
        Tuple of (case_index, result). Result is the received value for RECV,
        None for SEND.

    Example:
        >>> ch1 = Channel[int]()
        >>> ch2 = Channel[str]()
        >>>
        >>> idx, value = await select(
        ...     SelectCase(ch1, SelectOp.RECV),
        ...     SelectCase(ch2, SelectOp.SEND, "hello"),
        ... )
        >>> print(f"Case {idx} completed with {value}")

    """
    if not cases:
        raise ValueError("select requires at least one case")

    # Create tasks for each case
    async def try_case(idx: int, case: SelectCase[Any]) -> tuple[int, Any]:
        if case.op == SelectOp.RECV:
            value = await case.channel.recv()
            return (idx, value)
        else:  # SEND
            await case.channel.send(case.value)
            return (idx, None)

    tasks = [asyncio.create_task(try_case(i, c)) for i, c in enumerate(cases)]

    try:
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

        # Cancel pending tasks
        for task in pending:
            task.cancel()

        # Return first completed result
        for task in done:
            return task.result()

        raise RuntimeError("select completed with no results")
    except Exception:
        # Cancel all tasks on error
        for task in tasks:
            task.cancel()
        raise


# Thread pool for running Go functions
_executor: ThreadPoolExecutor | None = None


def _get_executor() -> ThreadPoolExecutor:
    """Get or create the thread pool executor."""
    global _executor
    if _executor is None:
        _executor = ThreadPoolExecutor(max_workers=32, thread_name_prefix="goated-")
    return _executor


def go(func: Callable[..., T], *args: Any, **kwargs: Any) -> Future[T]:
    """Spawn a function like a goroutine.

    Runs the function in a thread pool, returning a Future that can be awaited.
    This is useful for running blocking Go operations without blocking the
    asyncio event loop.

    Args:
        func: Function to run (can be sync or async)
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Future that resolves to the function's return value

    Example:
        >>> def heavy_computation(n: int) -> int:
        ...     return sum(range(n))
        >>>
        >>> future = go(heavy_computation, 1000000)
        >>> result = future.result()  # Blocking wait
        >>> # Or in async context:
        >>> result = await asyncio.wrap_future(future)

    """
    executor = _get_executor()

    if asyncio.iscoroutinefunction(func):

        def run_async() -> T:
            loop = asyncio.new_event_loop()
            try:
                return cast(T, loop.run_until_complete(func(*args, **kwargs)))
            finally:
                loop.close()

        return executor.submit(run_async)
    else:
        return executor.submit(func, *args, **kwargs)
