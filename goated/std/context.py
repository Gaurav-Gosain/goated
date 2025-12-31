"""Go context package bindings - Pure Python implementation.

This module provides Python bindings for Go's context package for
carrying deadlines, cancellation signals, and request-scoped values.

Example:
    >>> from goated.std import context
    >>> import asyncio
    >>>
    >>> async def main():
    ...     ctx, cancel = context.WithTimeout(context.Background(), 5.0)
    ...     try:
    ...         # Use ctx for operations
    ...         await do_work(ctx)
    ...     finally:
    ...         cancel()

"""

from __future__ import annotations

import asyncio
import contextlib
import threading
import time
from abc import abstractmethod
from collections.abc import Callable
from typing import Any

__all__ = [
    # Context types
    "Context",
    # Functions
    "Background",
    "TODO",
    "WithCancel",
    "WithTimeout",
    "WithDeadline",
    "WithValue",
    # Errors
    "Canceled",
    "DeadlineExceeded",
]


# =============================================================================
# Errors
# =============================================================================


class Canceled(Exception):
    """Canceled is the error returned when a context is canceled."""

    def __init__(self) -> None:
        super().__init__("context canceled")

    def Error(self) -> str:
        return "context canceled"


class DeadlineExceeded(Exception):
    """DeadlineExceeded is the error returned when a context's deadline passes."""

    def __init__(self) -> None:
        super().__init__("context deadline exceeded")

    def Error(self) -> str:
        return "context deadline exceeded"


# =============================================================================
# Context Interface
# =============================================================================


class Context:
    """Context carries deadlines, cancellation signals, and request-scoped values.

    A Context's methods may be called by multiple goroutines simultaneously.
    """

    @abstractmethod
    def Deadline(self) -> tuple[float | None, bool]:
        """Return the time when work done on behalf of this context should be canceled.

        Returns (deadline, ok) where ok is False when no deadline is set.
        """
        ...

    @abstractmethod
    def Done(self) -> asyncio.Event | None:
        """Return a channel that's closed when work done on behalf of this context
        should be canceled.
        """
        ...

    @abstractmethod
    def Err(self) -> Exception | None:
        """Return Canceled if the context was canceled or DeadlineExceeded if
        the context's deadline passed.
        """
        ...

    @abstractmethod
    def Value(self, key: Any) -> Any:
        """Return the value associated with this context for key, or None."""
        ...


# =============================================================================
# Implementations
# =============================================================================


class _BackgroundContext(Context):
    """An empty context that is never canceled."""

    def Deadline(self) -> tuple[float | None, bool]:
        return None, False

    def Done(self) -> asyncio.Event | None:
        return None

    def Err(self) -> Exception | None:
        return None

    def Value(self, key: Any) -> Any:
        return None

    def __str__(self) -> str:
        return "context.Background"

    def __repr__(self) -> str:
        return "context.Background"


class _TODOContext(_BackgroundContext):
    """A context for when it's unclear which Context to use."""

    def __str__(self) -> str:
        return "context.TODO"

    def __repr__(self) -> str:
        return "context.TODO"


_background = _BackgroundContext()
_todo = _TODOContext()


def Background() -> Context:
    """Return a non-nil, empty Context.

    It is never canceled, has no values, and has no deadline.
    It is typically used by the main function, initialization, and tests.
    """
    return _background


def TODO() -> Context:
    """Return a non-nil, empty Context.

    Code should use TODO when it's unclear which Context to use or it is
    not yet available.
    """
    return _todo


class _CancelContext(Context):
    """A context that can be canceled."""

    def __init__(self, parent: Context):
        self._parent = parent
        self._done = asyncio.Event()
        self._err: Exception | None = None
        self._lock = threading.Lock()
        self._children: list[_CancelContext] = []

        # Register with parent if it's cancellable
        if isinstance(parent, _CancelContext):
            with parent._lock:
                parent._children.append(self)

    def Deadline(self) -> tuple[float | None, bool]:
        return self._parent.Deadline()

    def Done(self) -> asyncio.Event | None:
        return self._done

    def Err(self) -> Exception | None:
        with self._lock:
            return self._err

    def Value(self, key: Any) -> Any:
        return self._parent.Value(key)

    def _cancel(self, err: Exception) -> None:
        with self._lock:
            if self._err is not None:
                return  # Already canceled
            self._err = err

        self._done.set()

        # Cancel children
        for child in self._children:
            child._cancel(err)

    def __str__(self) -> str:
        return f"context.WithCancel({self._parent})"


class _DeadlineContext(_CancelContext):
    """A context with a deadline."""

    def __init__(self, parent: Context, deadline: float):
        super().__init__(parent)
        self._deadline = deadline
        self._timer: asyncio.TimerHandle | None = None

        # Schedule cancellation
        delay = deadline - time.time()
        if delay <= 0:
            self._cancel(DeadlineExceeded())
        else:
            try:
                loop = asyncio.get_event_loop()
                self._timer = loop.call_later(delay, self._timeout)
            except RuntimeError:
                # No event loop running
                pass

    def Deadline(self) -> tuple[float | None, bool]:
        return self._deadline, True

    def _timeout(self) -> None:
        self._cancel(DeadlineExceeded())

    def _cancel(self, err: Exception) -> None:
        super()._cancel(err)
        if self._timer:
            self._timer.cancel()
            self._timer = None

    def __str__(self) -> str:
        return f"context.WithDeadline({self._parent}, {self._deadline})"


class _ValueContext(Context):
    """A context that carries a key-value pair."""

    def __init__(self, parent: Context, key: Any, val: Any):
        self._parent = parent
        self._key = key
        self._val = val

    def Deadline(self) -> tuple[float | None, bool]:
        return self._parent.Deadline()

    def Done(self) -> asyncio.Event | None:
        return self._parent.Done()

    def Err(self) -> Exception | None:
        return self._parent.Err()

    def Value(self, key: Any) -> Any:
        if key == self._key:
            return self._val
        return self._parent.Value(key)

    def __str__(self) -> str:
        return f"context.WithValue({self._parent}, {self._key!r})"


# =============================================================================
# Factory Functions
# =============================================================================


def WithCancel(parent: Context) -> tuple[Context, Callable[[], None]]:
    """Return a copy of parent with a new Done channel.

    The returned context's Done channel is closed when the returned cancel
    function is called or when the parent context's Done channel is closed.

    Example:
        >>> ctx, cancel = WithCancel(Background())
        >>> # ... use ctx ...
        >>> cancel()  # Cancel the context

    """
    ctx = _CancelContext(parent)

    def cancel() -> None:
        ctx._cancel(Canceled())

    # Propagate parent cancellation
    parent_done = parent.Done()
    if parent_done is not None:

        async def _watch_parent() -> None:
            await parent_done.wait()
            ctx._cancel(parent.Err() or Canceled())

        with contextlib.suppress(RuntimeError):
            asyncio.get_event_loop().create_task(_watch_parent())

    return ctx, cancel


def WithTimeout(parent: Context, timeout: float) -> tuple[Context, Callable[[], None]]:
    """Return WithDeadline(parent, time.Now().Add(timeout)).

    Example:
        >>> ctx, cancel = WithTimeout(Background(), 5.0)  # 5 second timeout
        >>> try:
        ...     await do_work(ctx)
        ... finally:
        ...     cancel()

    """
    return WithDeadline(parent, time.time() + timeout)


def WithDeadline(parent: Context, deadline: float) -> tuple[Context, Callable[[], None]]:
    """Return a copy of the parent context with the deadline adjusted to be
    no later than d.

    Example:
        >>> deadline = time.time() + 10  # 10 seconds from now
        >>> ctx, cancel = WithDeadline(Background(), deadline)

    """
    # Check if parent has earlier deadline
    parent_deadline, ok = parent.Deadline()
    if ok and parent_deadline is not None and parent_deadline < deadline:
        # Parent deadline is earlier, just use cancel context
        return WithCancel(parent)

    ctx = _DeadlineContext(parent, deadline)

    def cancel() -> None:
        ctx._cancel(Canceled())

    return ctx, cancel


def WithValue(parent: Context, key: Any, val: Any) -> Context:
    """Return a copy of parent in which the value associated with key is val.

    Use context Values only for request-scoped data that transits processes
    and API boundaries, not for passing optional parameters to functions.

    Example:
        >>> ctx = WithValue(Background(), "user_id", 12345)
        >>> ctx.Value("user_id")
        12345

    """
    return _ValueContext(parent, key, val)


# =============================================================================
# Utility Functions
# =============================================================================


async def Sleep(ctx: Context, duration: float) -> Exception | None:
    """Sleep pauses the current task for at least duration seconds.

    Returns the context's error if the context is canceled before duration.

    Example:
        >>> err = await Sleep(ctx, 1.0)
        >>> if err:
        ...     print("Context canceled:", err)

    """
    done = ctx.Done()
    if done is None:
        await asyncio.sleep(duration)
        return None

    try:
        await asyncio.wait_for(done.wait(), timeout=duration)
        return ctx.Err()
    except asyncio.TimeoutError:
        return None


def AfterFunc(ctx: Context, f: Callable[[], None]) -> Callable[[], bool]:
    """Arrange to call f in its own goroutine after ctx is done.

    Returns a function that can be called to stop f from being called.
    """
    stopped = [False]

    async def _wait() -> None:
        done = ctx.Done()
        if done:
            await done.wait()
            if not stopped[0]:
                f()

    with contextlib.suppress(RuntimeError):
        asyncio.get_event_loop().create_task(_wait())

    def stop() -> bool:
        was_stopped = stopped[0]
        stopped[0] = True
        return not was_stopped

    return stop
