"""Result types for Go error handling in Python.

This module provides Rust-inspired Result[T, E] types that elegantly map
Go's (value, error) return pattern to Python. Supports pattern matching
with Python 3.10+ match/case statements.

Example:
    >>> from goated import Ok, Err, Result
    >>>
    >>> def divide(a: int, b: int) -> Result[float, str]:
    ...     if b == 0:
    ...         return Err("division by zero")
    ...     return Ok(a / b)
    >>>
    >>> match divide(10, 2):
    ...     case Ok(value): print(f"Result: {value}")
    ...     case Err(error): print(f"Error: {error}")
    Result: 5.0
    >>>
    >>> # Fluent API
    >>> divide(10, 2).map(lambda x: x * 2).unwrap()
    10.0
    >>> divide(10, 0).unwrap_or(0.0)
    0.0

"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Generic,
    NoReturn,
    TypeVar,
)

if TYPE_CHECKING:
    from typing import TypeGuard

__all__ = ["Ok", "Err", "Result", "GoError", "is_ok", "is_err"]

T = TypeVar("T")  # Success type
E = TypeVar("E", bound=Exception)  # Error type
U = TypeVar("U")  # Mapped type
F = TypeVar("F", bound=Exception)  # Mapped error type


class GoError(Exception):
    r"""Exception wrapper for Go errors.

    Wraps error strings returned from Go functions into Python exceptions.
    Preserves the original Go error message and provides useful context.

    Attributes:
        message: The original Go error message
        go_type: The Go error type name (if available)

    Example:
        >>> err = GoError("strconv.ParseInt: parsing \"abc\": invalid syntax")
        >>> raise err
        GoError: strconv.ParseInt: parsing "abc": invalid syntax

    """

    __slots__ = ("message", "go_type")

    def __init__(self, message: str, go_type: str = "error") -> None:
        self.message = message
        self.go_type = go_type
        super().__init__(message)

    def __repr__(self) -> str:
        return f"GoError({self.message!r})"

    def __str__(self) -> str:
        return self.message

    def __eq__(self, other: object) -> bool:
        if isinstance(other, GoError):
            return self.message == other.message
        return False

    def __hash__(self) -> int:
        return hash(self.message)


@dataclass(frozen=True, slots=True)
class Ok(Generic[T]):
    """Represents a successful result containing a value.

    This is the success variant of Result[T, E]. It wraps a value of type T
    and provides methods for transforming and extracting the value.

    Attributes:
        value: The success value

    Example:
        >>> ok = Ok(42)
        >>> ok.unwrap()
        42
        >>> ok.map(lambda x: x * 2).unwrap()
        84
        >>> ok.is_ok()
        True

    """

    value: T

    # For pattern matching: match result: case Ok(v): ...
    __match_args__ = ("value",)

    def is_ok(self) -> bool:
        """Returns True if this is an Ok value."""
        return True

    def is_err(self) -> bool:
        """Returns False since this is an Ok value."""
        return False

    def unwrap(self) -> T:
        """Returns the contained value.

        Since this is Ok, always succeeds.

        Returns:
            The wrapped value

        Example:
            >>> Ok(42).unwrap()
            42

        """
        return self.value

    def unwrap_or(self, default: T) -> T:
        """Returns the contained value, ignoring the default.

        Args:
            default: Ignored for Ok values

        Returns:
            The wrapped value

        Example:
            >>> Ok(42).unwrap_or(0)
            42

        """
        return self.value

    def unwrap_or_else(self, f: Callable[[E], T]) -> T:
        """Returns the contained value, ignoring the fallback function.

        Args:
            f: Ignored for Ok values

        Returns:
            The wrapped value

        """
        return self.value

    def expect(self, msg: str) -> T:
        """Returns the contained value.

        Args:
            msg: Ignored for Ok values

        Returns:
            The wrapped value

        """
        return self.value

    def map(self, f: Callable[[T], U]) -> Ok[U]:
        """Applies a function to the contained value.

        Args:
            f: Function to apply to the value

        Returns:
            Ok containing the transformed value

        Example:
            >>> Ok(21).map(lambda x: x * 2)
            Ok(value=42)

        """
        return Ok(f(self.value))

    def map_err(self, f: Callable[[E], F]) -> Ok[T]:
        """Returns self unchanged since there's no error to map.

        Args:
            f: Ignored for Ok values

        Returns:
            Self unchanged

        """
        return self

    def and_then(self, f: Callable[[T], Result[U, E]]) -> Result[U, E]:
        """Applies a function that returns a Result to the contained value.

        Useful for chaining operations that may fail.

        Args:
            f: Function returning a Result

        Returns:
            The Result from applying f

        Example:
            >>> def double_if_positive(x: int) -> Result[int, str]:
            ...     if x > 0:
            ...         return Ok(x * 2)
            ...     return Err("not positive")
            >>> Ok(21).and_then(double_if_positive)
            Ok(value=42)

        """
        return f(self.value)

    def or_else(self, f: Callable[[E], Result[T, F]]) -> Ok[T]:
        """Returns self unchanged since there's no error.

        Args:
            f: Ignored for Ok values

        Returns:
            Self unchanged

        """
        return self

    def ok(self) -> T:
        """Returns the contained value.

        Alias for unwrap() for compatibility with other Result implementations.
        """
        return self.value

    def err(self) -> None:
        """Returns None since this is not an error."""
        return None

    def __bool__(self) -> bool:
        """Ok is truthy."""
        return True

    def __repr__(self) -> str:
        return f"Ok({self.value!r})"


@dataclass(frozen=True, slots=True)
class Err(Generic[E]):
    """Represents a failed result containing an error.

    This is the error variant of Result[T, E]. It wraps an error of type E
    and provides methods for handling the error case.

    Attributes:
        error: The error value

    Example:
        >>> err = Err(GoError("something went wrong"))
        >>> err.is_err()
        True
        >>> err.unwrap_or(42)
        42

    """

    error: E

    # For pattern matching: match result: case Err(e): ...
    __match_args__ = ("error",)

    def is_ok(self) -> bool:
        """Returns False since this is an Err value."""
        return False

    def is_err(self) -> bool:
        """Returns True if this is an Err value."""
        return True

    def unwrap(self) -> NoReturn:
        """Raises the contained error.

        Raises:
            The wrapped error

        Example:
            >>> Err(GoError("oops")).unwrap()
            Traceback (most recent call last):
                ...
            GoError: oops

        """
        raise self.error

    def unwrap_or(self, default: T) -> T:
        """Returns the default value since this is an error.

        Args:
            default: Value to return

        Returns:
            The default value

        Example:
            >>> Err(GoError("oops")).unwrap_or(42)
            42

        """
        return default

    def unwrap_or_else(self, f: Callable[[E], T]) -> T:
        """Computes a value from the error using the provided function.

        Args:
            f: Function to compute fallback value from error

        Returns:
            The computed value

        """
        return f(self.error)

    def expect(self, msg: str) -> NoReturn:
        """Raises the error with a custom message.

        Args:
            msg: Custom error message prefix

        Raises:
            RuntimeError with the custom message and original error

        """
        raise RuntimeError(f"{msg}: {self.error}") from self.error

    def map(self, f: Callable[[T], U]) -> Err[E]:
        """Returns self unchanged since there's no value to map.

        Args:
            f: Ignored for Err values

        Returns:
            Self unchanged

        """
        return self

    def map_err(self, f: Callable[[E], F]) -> Err[F]:
        """Applies a function to the contained error.

        Args:
            f: Function to apply to the error

        Returns:
            Err containing the transformed error

        """
        return Err(f(self.error))

    def and_then(self, f: Callable[[T], Result[U, E]]) -> Err[E]:
        """Returns self unchanged since there's no value.

        Args:
            f: Ignored for Err values

        Returns:
            Self unchanged

        """
        return self

    def or_else(self, f: Callable[[E], Result[T, F]]) -> Result[T, F]:
        """Applies a function that returns a Result to the error.

        Useful for error recovery.

        Args:
            f: Function returning a Result

        Returns:
            The Result from applying f

        """
        return f(self.error)

    def ok(self) -> None:
        """Returns None since this is an error."""
        return None

    def err(self) -> E:
        """Returns the contained error."""
        return self.error

    def __bool__(self) -> bool:
        """Err is falsy."""
        return False

    def __repr__(self) -> str:
        return f"Err({self.error!r})"


# Type alias for Result
Result = Ok[T] | Err[E]


def is_ok(result: Result[T, E]) -> TypeGuard[Ok[T]]:
    """Type guard that checks if a Result is Ok.

    Useful for type narrowing in if statements.

    Args:
        result: The Result to check

    Returns:
        True if result is Ok

    Example:
        >>> r: Result[int, str] = Ok(42)
        >>> if is_ok(r):
        ...     print(r.value)  # type checker knows r is Ok[int]
        42

    """
    return isinstance(result, Ok)


def is_err(result: Result[T, E]) -> TypeGuard[Err[E]]:
    """Type guard that checks if a Result is Err.

    Useful for type narrowing in if statements.

    Args:
        result: The Result to check

    Returns:
        True if result is Err

    Example:
        >>> r: Result[int, GoError] = Err(GoError("oops"))
        >>> if is_err(r):
        ...     print(r.error)  # type checker knows r is Err[GoError]
        oops

    """
    return isinstance(result, Err)
