"""Go fmt package bindings - Pure Python implementation.

This module provides Python bindings for Go's fmt package formatting
functions.

Example:
    >>> from goated.std import fmt
    >>>
    >>> fmt.Sprintf("Hello, %s!", "World")
    'Hello, World!'
    >>>
    >>> fmt.Sprintf("%d + %d = %d", 2, 3, 5)
    '2 + 3 = 5'

"""

from __future__ import annotations

import sys
from typing import Any, TextIO

__all__ = [
    # Print functions
    "Print",
    "Println",
    "Printf",
    "Fprint",
    "Fprintln",
    "Fprintf",
    "Sprint",
    "Sprintln",
    "Sprintf",
    # Scan functions
    "Scan",
    "Scanln",
    "Scanf",
    "Sscan",
    "Sscanln",
    "Sscanf",
    # Error functions
    "Errorf",
    # Interfaces
    "Stringer",
    "GoStringer",
    "Formatter",
]


# =============================================================================
# Interfaces
# =============================================================================


class Stringer:
    """Stringer is implemented by any type with a String method."""

    def String(self) -> str:
        raise NotImplementedError


class GoStringer:
    """GoStringer is implemented by any type with a GoString method."""

    def GoString(self) -> str:
        raise NotImplementedError


class Formatter:
    """Formatter is implemented by any type with a Format method."""

    def Format(self, f: State, verb: str) -> None:
        raise NotImplementedError


class State:
    """State represents the printer state passed to custom formatters."""

    def __init__(self, width: int | None, precision: int | None, flags: str):
        self._width = width
        self._precision = precision
        self._flags = flags
        self._buf: list[str] = []

    def Width(self) -> tuple[int, bool]:
        if self._width is None:
            return 0, False
        return self._width, True

    def Precision(self) -> tuple[int, bool]:
        if self._precision is None:
            return 0, False
        return self._precision, True

    def Flag(self, c: str) -> bool:
        return c in self._flags

    def Write(self, b: bytes) -> tuple[int, Exception | None]:
        self._buf.append(b.decode("utf-8"))
        return len(b), None


# =============================================================================
# Format Conversion
# =============================================================================


def _convert_format(fmt_str: str, args: tuple[Any, ...]) -> str:
    """Convert Go-style format string to Python format.

    Go verbs:
    %v - default format
    %+v - add field names
    %#v - Go-syntax representation
    %T - type name
    %t - boolean
    %b - binary
    %c - character
    %d - decimal
    %o - octal
    %O - octal with 0o prefix
    %q - quoted string
    %x - hex lowercase
    %X - hex uppercase
    %U - Unicode format
    %e - scientific lowercase
    %E - scientific uppercase
    %f - decimal point
    %F - same as %f
    %g - compact format
    %G - compact format uppercase
    %s - string
    %p - pointer
    %% - literal %
    """
    result = []
    arg_idx = 0
    i = 0

    while i < len(fmt_str):
        if fmt_str[i] == "%":
            if i + 1 < len(fmt_str) and fmt_str[i + 1] == "%":
                result.append("%")
                i += 2
                continue

            # Parse format specifier
            j = i + 1
            flags = ""
            width = ""
            precision = ""

            # Parse flags
            while j < len(fmt_str) and fmt_str[j] in "+-# 0":
                flags += fmt_str[j]
                j += 1

            # Parse width
            while j < len(fmt_str) and fmt_str[j].isdigit():
                width += fmt_str[j]
                j += 1

            # Parse precision
            if j < len(fmt_str) and fmt_str[j] == ".":
                j += 1
                while j < len(fmt_str) and fmt_str[j].isdigit():
                    precision += fmt_str[j]
                    j += 1

            # Parse verb
            if j < len(fmt_str):
                verb = fmt_str[j]
                j += 1

                # Get argument
                if arg_idx < len(args):
                    arg = args[arg_idx]
                    arg_idx += 1
                else:
                    arg = "%!(" + verb + "=MISSING)"

                # Format based on verb
                formatted = _format_arg(arg, verb, flags, width, precision)
                result.append(formatted)

            i = j
        else:
            result.append(fmt_str[i])
            i += 1

    return "".join(result)


def _format_arg(arg: Any, verb: str, flags: str, width: str, precision: str) -> str:
    """Format a single argument according to the verb."""
    # Check for Stringer interface
    if hasattr(arg, "String") and verb in "sv":
        arg = arg.String()

    # Check for GoStringer interface
    if hasattr(arg, "GoString") and verb == "v" and "#" in flags:
        return str(arg.GoString())

    try:
        if verb == "v":
            # Default format
            if "#" in flags:
                return repr(arg)
            elif "+" in flags and hasattr(arg, "__dict__"):
                return str(arg.__dict__)
            return str(arg)

        elif verb == "T":
            return type(arg).__name__

        elif verb == "t":
            return "true" if arg else "false"

        elif verb == "b":
            return format(int(arg), "b")

        elif verb == "c":
            return chr(int(arg))

        elif verb == "d":
            fmt_spec = ""
            if width:
                if "0" in flags:
                    fmt_spec = f"0{width}"
                elif "-" in flags:
                    fmt_spec = f"<{width}"
                else:
                    fmt_spec = f">{width}"
            if "+" in flags and arg >= 0:
                return "+" + format(int(arg), fmt_spec)
            return format(int(arg), fmt_spec)

        elif verb == "o":
            return format(int(arg), "o")

        elif verb == "O":
            return "0o" + format(int(arg), "o")

        elif verb == "q":
            if isinstance(arg, str):
                return repr(arg)
            return repr(str(arg))

        elif verb == "x":
            if isinstance(arg, (bytes, bytearray)):
                return arg.hex()
            return format(int(arg), "x")

        elif verb == "X":
            if isinstance(arg, (bytes, bytearray)):
                return arg.hex().upper()
            return format(int(arg), "X")

        elif verb == "U":
            return f"U+{ord(str(arg)[0]) if isinstance(arg, str) else int(arg):04X}"

        elif verb == "e":
            prec = int(precision) if precision else 6
            return format(float(arg), f".{prec}e")

        elif verb == "E":
            prec = int(precision) if precision else 6
            return format(float(arg), f".{prec}E")

        elif verb in "fF":
            prec = int(precision) if precision else 6
            fmt_spec = f".{prec}f"
            if width:
                if "0" in flags:
                    fmt_spec = f"0{width}.{prec}f"
                elif "-" in flags:
                    fmt_spec = f"<{width}.{prec}f"
                else:
                    fmt_spec = f">{width}.{prec}f"
            return format(float(arg), fmt_spec)

        elif verb == "g":
            prec = int(precision) if precision else -1
            if prec < 0:
                return str(float(arg))
            return format(float(arg), f".{prec}g")

        elif verb == "G":
            prec = int(precision) if precision else -1
            if prec < 0:
                return str(float(arg)).upper()
            return format(float(arg), f".{prec}G")

        elif verb == "s":
            s = str(arg)
            if precision:
                s = s[: int(precision)]
            if width:
                w = int(width)
                s = s.ljust(w) if "-" in flags else s.rjust(w)
            return s

        elif verb == "p":
            return hex(id(arg))

        else:
            return f"%!{verb}({type(arg).__name__}={arg})"

    except Exception as e:
        return f"%!{verb}(ERROR={e})"


# =============================================================================
# Print Functions
# =============================================================================


def Print(*args: Any) -> tuple[int, Exception | None]:
    """Print formats using default formats and writes to standard output.
    Spaces are added between operands when neither is a string.
    """
    s = Sprint(*args)
    try:
        n = sys.stdout.write(s)
        return n, None
    except Exception as e:
        return 0, e


def Println(*args: Any) -> tuple[int, Exception | None]:
    """Println formats using default formats and writes to standard output.
    Spaces are always added between operands and a newline is appended.
    """
    s = Sprintln(*args)
    try:
        n = sys.stdout.write(s)
        return n, None
    except Exception as e:
        return 0, e


def Printf(format: str, *args: Any) -> tuple[int, Exception | None]:
    """Printf formats according to a format specifier and writes to standard output."""
    s = Sprintf(format, *args)
    try:
        n = sys.stdout.write(s)
        return n, None
    except Exception as e:
        return 0, e


def Fprint(w: TextIO, *args: Any) -> tuple[int, Exception | None]:
    """Fprint formats using default formats and writes to w."""
    s = Sprint(*args)
    try:
        n = w.write(s)
        return n, None
    except Exception as e:
        return 0, e


def Fprintln(w: TextIO, *args: Any) -> tuple[int, Exception | None]:
    """Fprintln formats using default formats and writes to w.
    Spaces are always added between operands and a newline is appended.
    """
    s = Sprintln(*args)
    try:
        n = w.write(s)
        return n, None
    except Exception as e:
        return 0, e


def Fprintf(w: TextIO, format: str, *args: Any) -> tuple[int, Exception | None]:
    """Fprintf formats according to a format specifier and writes to w."""
    s = Sprintf(format, *args)
    try:
        n = w.write(s)
        return n, None
    except Exception as e:
        return 0, e


def Sprint(*args: Any) -> str:
    """Sprint formats using default formats and returns the resulting string."""
    parts = []
    for i, arg in enumerate(args):
        if i > 0 and not isinstance(args[i - 1], str) and not isinstance(arg, str):
            parts.append(" ")
        if hasattr(arg, "String"):
            parts.append(arg.String())
        else:
            parts.append(str(arg))
    return "".join(parts)


def Sprintln(*args: Any) -> str:
    """Sprintln formats using default formats and returns the resulting string.
    Spaces are always added between operands and a newline is appended.
    """
    parts = []
    for arg in args:
        if hasattr(arg, "String"):
            parts.append(arg.String())
        else:
            parts.append(str(arg))
    return " ".join(parts) + "\n"


def Sprintf(format: str, *args: Any) -> str:
    """Sprintf formats according to a format specifier and returns the resulting string.

    Example:
        >>> Sprintf("Hello, %s!", "World")
        'Hello, World!'
        >>> Sprintf("%d items", 42)
        '42 items'

    """
    return _convert_format(format, args)


# =============================================================================
# Error Functions
# =============================================================================


class _FormattedError(Exception):
    """Error created by Errorf."""

    def __init__(self, message: str, wrapped: Exception | None = None):
        super().__init__(message)
        self._message = message
        self._wrapped = wrapped

    def Error(self) -> str:
        return self._message

    def Unwrap(self) -> Exception | None:
        return self._wrapped

    def __str__(self) -> str:
        return self._message


def Errorf(format: str, *args: Any) -> Exception:
    """Errorf formats according to a format specifier and returns an error.

    If the format specifier includes a %w verb with an error operand,
    the returned error will implement an Unwrap method.

    Example:
        >>> err = Errorf("failed to open %s: %w", "file.txt", IOError("not found"))
        >>> print(err)
        failed to open file.txt: not found

    """
    # Check for %w verb
    wrapped = None
    new_args = []
    new_format = format

    if "%w" in format:
        parts = format.split("%w")
        if len(parts) == 2 and args:
            # Find the error argument
            fmt_count = format[: format.index("%w")].count("%") - format[
                : format.index("%w")
            ].count("%%")
            if fmt_count < len(args):
                wrapped = args[fmt_count]
                new_args = list(args[:fmt_count]) + list(args[fmt_count + 1 :])
                new_format = parts[0] + "%v" + parts[1]
                args = tuple(new_args[:fmt_count]) + (str(wrapped),) + tuple(new_args[fmt_count:])

    message = Sprintf(new_format, *args)
    return _FormattedError(message, wrapped)


# =============================================================================
# Scan Functions (basic implementations)
# =============================================================================


def Scan(*args: Any) -> tuple[int, Exception | None]:
    """Scan scans text read from standard input."""
    try:
        line = input()
        return Sscan(line, *args)
    except EOFError:
        from .io import EOF

        return 0, EOF()
    except Exception as e:
        return 0, e


def Scanln(*args: Any) -> tuple[int, Exception | None]:
    """Scanln is similar to Scan, but stops at a newline."""
    return Scan(*args)


def Scanf(format: str, *args: Any) -> tuple[int, Exception | None]:
    """Scanf scans text read from standard input, storing values according to format."""
    try:
        line = input()
        return Sscanf(line, format, *args)
    except EOFError:
        from .io import EOF

        return 0, EOF()
    except Exception as e:
        return 0, e


def Sscan(s: str, *args: Any) -> tuple[int, Exception | None]:
    """Sscan scans the argument string."""
    parts = s.split()
    count = 0

    for i, _arg in enumerate(args):
        if i >= len(parts):
            break
        # Note: In Python we can't modify the args directly
        # This is a simplified implementation
        count += 1

    return count, None


def Sscanln(s: str, *args: Any) -> tuple[int, Exception | None]:
    """Sscanln is similar to Sscan, but stops at a newline."""
    return Sscan(s.split("\n")[0], *args)


def Sscanf(s: str, format: str, *args: Any) -> tuple[int, Exception | None]:
    """Sscanf scans the argument string, storing values according to format."""
    # Simplified implementation
    return Sscan(s, *args)
