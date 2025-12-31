"""Go errors package bindings - Pure Python implementation.

This module provides Python bindings for Go's errors package.

Example:
    >>> from goated.std import errors
    >>>
    >>> err = errors.New("something went wrong")
    >>> print(err)
    something went wrong
    >>>
    >>> wrapped = errors.New("operation failed: %w", err)
    >>> errors.Is(wrapped, err)
    True

"""

from __future__ import annotations

import traceback
from typing import TypeVar, cast

__all__ = [
    "New",
    "Is",
    "As",
    "Unwrap",
    "Join",
    # Error interface
    "Error",
]

T = TypeVar("T", bound=Exception)


# =============================================================================
# Error Interface
# =============================================================================


class Error(Exception):
    """Error is the interface that wraps the basic Error method.

    This is the base class for Go-style errors.
    """

    def __init__(self, message: str):
        super().__init__(message)
        self._message = message

    def Error(self) -> str:
        """Return the error message."""
        return self._message

    def __str__(self) -> str:
        return self._message

    def __repr__(self) -> str:
        return f"Error({self._message!r})"


class _WrappedError(Error):
    """An error that wraps another error."""

    def __init__(self, message: str, wrapped: Exception | None = None):
        super().__init__(message)
        self._wrapped = wrapped

    def Unwrap(self) -> Exception | None:
        """Return the wrapped error."""
        return self._wrapped


class _JoinedError(Error):
    """An error that joins multiple errors."""

    def __init__(self, errs: list[Exception]):
        self._errors = [e for e in errs if e is not None]
        messages = [str(e) for e in self._errors]
        super().__init__("\n".join(messages))

    def Unwrap(self) -> list[Exception]:
        """Return the list of wrapped errors."""
        return self._errors


# =============================================================================
# Functions
# =============================================================================


def New(text: str) -> Error:
    """New returns an error that formats as the given text.

    Each call to New returns a distinct error value even if the text is identical.

    Example:
        >>> err1 = New("error")
        >>> err2 = New("error")
        >>> err1 == err2
        False

    """
    return Error(text)


def Is(err: Exception | None, target: Exception | None) -> bool:
    """Is reports whether any error in err's tree matches target.

    The tree consists of err itself, followed by the errors obtained by
    repeatedly calling Unwrap. An error is considered to match a target
    if it is equal to that target or if it implements an Is method
    such that Is(target) returns true.

    Example:
        >>> base = New("base error")
        >>> wrapped = _WrappedError("wrapped: base error", base)
        >>> Is(wrapped, base)
        True

    """
    if err is None or target is None:
        return err == target

    # Direct comparison
    if err == target:
        return True

    # Check if error has Is method
    if hasattr(err, "Is") and callable(err.Is) and err.Is(target):
        return True

    # Check type match
    if type(err) is type(target) and str(err) == str(target):
        return True

    # Unwrap and recurse
    unwrapped = Unwrap(err)
    if unwrapped is not None:
        if isinstance(unwrapped, list):
            return any(Is(e, target) for e in unwrapped)
        return Is(unwrapped, target)

    return False


def As(err: Exception | None, target: type[T]) -> T | None:
    """As finds the first error in err's tree that matches target type,
    and if so, returns that error.

    The tree consists of err itself, followed by the errors obtained by
    repeatedly calling Unwrap.

    Example:
        >>> class MyError(Error):
        ...     pass
        >>> err = MyError("my error")
        >>> As(err, MyError)
        MyError('my error')

    """
    if err is None:
        return None

    # Check if err is of target type
    if isinstance(err, target):
        return err

    # Check if error has As method
    if hasattr(err, "As") and callable(err.As):
        result = err.As(target)
        if result is not None:
            return cast(T, result)

    # Unwrap and recurse
    unwrapped = Unwrap(err)
    if unwrapped is not None:
        if isinstance(unwrapped, list):
            for e in unwrapped:
                result = As(e, target)
                if result is not None:
                    return cast(T, result)
        else:
            return As(unwrapped, target)

    return None


def Unwrap(err: Exception | None) -> Exception | list[Exception] | None:
    """Unwrap returns the result of calling the Unwrap method on err,
    if err's type contains an Unwrap method returning error.
    Otherwise, Unwrap returns nil.

    Example:
        >>> base = New("base")
        >>> wrapped = _WrappedError("wrapped", base)
        >>> Unwrap(wrapped) == base
        True

    """
    if err is None:
        return None

    if hasattr(err, "Unwrap") and callable(err.Unwrap):
        result: Exception | list[Exception] | None = err.Unwrap()
        return result

    # Check for Python's __cause__ (from `raise X from Y`)
    if hasattr(err, "__cause__") and err.__cause__ is not None:
        cause = err.__cause__
        if isinstance(cause, Exception):
            return cause

    return None


def Join(*errs: Exception | None) -> Exception | None:
    """Join returns an error that wraps the given errors.
    Any nil error values are discarded.
    Join returns nil if errs contains no non-nil values.

    The error formats as the concatenation of the strings obtained
    by calling the Error method of each element of errs, with a newline
    between each string.

    Example:
        >>> err1 = New("error 1")
        >>> err2 = New("error 2")
        >>> joined = Join(err1, err2)
        >>> print(joined)
        error 1
        error 2

    """
    non_nil = [e for e in errs if e is not None]

    if not non_nil:
        return None

    if len(non_nil) == 1:
        return non_nil[0]

    return _JoinedError(non_nil)


# =============================================================================
# Helper Functions
# =============================================================================


def Wrap(err: Exception, message: str) -> Error:
    """Wrap returns an error annotating err with a message.

    This is a convenience function similar to fmt.Errorf("%s: %w", message, err).

    Example:
        >>> base = New("file not found")
        >>> wrapped = Wrap(base, "failed to open config")
        >>> print(wrapped)
        failed to open config: file not found

    """
    return _WrappedError(f"{message}: {err}", err)


def Cause(err: Exception | None) -> Exception | None:
    """Cause returns the underlying cause of the error, if possible.

    This unwraps the error chain to find the root cause.
    """
    if err is None:
        return None

    for _ in range(100):  # Prevent infinite loops
        unwrapped = Unwrap(err)
        if unwrapped is None:
            return err
        if isinstance(unwrapped, list):
            return err
        err = unwrapped

    return err


def WithStack(err: Exception) -> Exception:
    """WithStack annotates err with a stack trace."""
    setattr(err, "_stack", traceback.format_stack())  # noqa: B010
    return err


def Stack(err: Exception) -> str | None:
    """Stack returns the stack trace from an error created with WithStack."""
    stack = getattr(err, "_stack", None)
    if stack is not None:
        return "".join(stack)
    return None
