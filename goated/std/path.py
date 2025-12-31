"""Go path package bindings - Auto-generated.

This module provides Python bindings for Go's path package.
Implements POSIX-style path operations (always uses forward slashes).
"""

from __future__ import annotations

import fnmatch
import posixpath

from goated._core import get_lib, is_library_available
from goated.result import Err, GoError, Ok, Result

__all__ = [
    "Base",
    "Clean",
    "Dir",
    "Ext",
    "IsAbs",
    "Join",
    "Match",
    "Split",
]


def _encode(s: str) -> bytes:
    return s.encode("utf-8")


def _decode(b: bytes | None) -> str:
    if b is None:
        return ""
    return b.decode("utf-8")


import ctypes

_fn_configured: set[str] = set()


def _configure_fn(lib: object, name: str, argtypes: list[type], restype: type) -> None:
    if name in _fn_configured:
        return
    fn = getattr(lib, name)
    fn.argtypes = argtypes
    fn.restype = restype
    _fn_configured.add(name)


# Pure Python fallback implementations


def _clean_path(path_: str) -> str:
    """Clean returns the shortest path name equivalent to path.

    Pure Python implementation of Go's path.Clean.
    """
    if not path_:
        return "."

    rooted = path_.startswith("/")
    n = len(path_)

    # Invariants:
    #   reading from path; r is index of next byte to process.
    #   writing to buf; w is index of next byte to write.

    # Process the path
    out = []
    r = 0

    if rooted:
        out.append("/")
        r = 1

    while r < n:
        if path_[r] == "/":
            # Empty path element
            r += 1
        elif path_[r] == "." and (r + 1 == n or path_[r + 1] == "/"):
            # . element
            r += 1
        elif path_[r] == "." and path_[r + 1] == "." and (r + 2 == n or path_[r + 2] == "/"):
            # .. element: remove last element
            r += 2
            if out and out[-1] != "/":
                # Can back up
                # Find last /
                i = len(out) - 1
                while i >= 0 and (
                    len(out) <= i
                    or (
                        i < len(out)
                        and (
                            out[i]
                            if isinstance(out[i], str) and len(out[i]) == 1
                            else out[i][-1]
                            if out[i]
                            else ""
                        )
                        != "/"
                    )
                ):
                    i -= 1
                if i >= 0:
                    out = out[: i + 1] if i >= 0 else []
                elif not rooted:
                    out = []
            elif not rooted:
                if out:
                    out.append("/")
                out.append("..")
        else:
            # Real path element
            if (rooted and len(out) > 1) or (not rooted and out):
                out.append("/")
            while r < n and path_[r] != "/":
                out.append(path_[r])
                r += 1

    result = "".join(out)
    if not result:
        return "."
    return result


def _py_clean(path_: str) -> str:
    """Pure Python Clean implementation using posixpath."""
    if not path_:
        return "."

    # Use posixpath.normpath which does most of what we need
    result = posixpath.normpath(path_)

    # Go's Clean returns "." for empty result
    if not result or result == ".":
        return "."

    return result


def Base(path_: str) -> str:
    """Base returns the last element of path.
    Trailing slashes are removed before extracting the last element.
    If the path is empty, Base returns ".".
    If the path consists entirely of slashes, Base returns "/".
    """
    if not is_library_available():
        # Pure Python fallback
        if not path_:
            return "."
        # Strip trailing slashes
        path_ = path_.rstrip("/")
        if not path_:
            return "/"
        # Find last slash
        i = path_.rfind("/")
        if i >= 0:
            return path_[i + 1 :]
        return path_

    lib = get_lib()
    _configure_fn(lib, "goated_path_Base", [ctypes.c_char_p], ctypes.c_char_p)
    result = lib.goated_path_Base(_encode(path_))
    return _decode(result)


def Clean(path_: str) -> str:
    """Clean returns the shortest path name equivalent to path
    by purely lexical processing. It applies the following rules
    iteratively until no further processing can be done:

     1. Replace multiple slashes with a single slash.
     2. Eliminate each . path name element (the current directory).
     3. Eliminate each inner .. path name element (the parent directory)
        along with the non-.. element that precedes it.
     4. Eliminate .. elements that begin a rooted path:
        that is, replace "/.." by "/" at the beginning of a path.

    The returned path ends in a slash only if it is the root "/".

    If the result of this process is an empty string, Clean
    returns the string ".".
    """
    if not is_library_available():
        return _py_clean(path_)

    lib = get_lib()
    _configure_fn(lib, "goated_path_Clean", [ctypes.c_char_p], ctypes.c_char_p)
    result = lib.goated_path_Clean(_encode(path_))
    return _decode(result)


def Dir(path_: str) -> str:
    """Dir returns all but the last element of path, typically the path's directory.
    After dropping the final element using [Split], the path is Cleaned and trailing
    slashes are removed.
    If the path is empty, Dir returns ".".
    If the path consists entirely of slashes followed by non-slash bytes, Dir
    returns a single slash. In any other case, the returned path does not end in a
    slash.
    """
    if not is_library_available():
        # Pure Python fallback
        if not path_:
            return "."
        # If path ends with slash, return path without trailing slash
        if path_.endswith("/") and len(path_) > 1:
            return path_.rstrip("/")
        # Find last slash
        i = path_.rfind("/")
        if i < 0:
            return "."
        # Clean the directory part
        dir_part = path_[:i]
        if not dir_part:
            return "/"
        return _py_clean(dir_part)

    lib = get_lib()
    _configure_fn(lib, "goated_path_Dir", [ctypes.c_char_p], ctypes.c_char_p)
    result = lib.goated_path_Dir(_encode(path_))
    return _decode(result)


def Ext(path_: str) -> str:
    """Ext returns the file name extension used by path.
    The extension is the suffix beginning at the final dot
    in the final slash-separated element of path;
    it is empty if there is no dot.
    """
    if not is_library_available():
        # Pure Python fallback
        # Get the base name first
        i = path_.rfind("/")
        if i >= 0:
            path_ = path_[i + 1 :]
        # Find extension
        i = path_.rfind(".")
        if i < 0:
            return ""
        return path_[i:]

    lib = get_lib()
    _configure_fn(lib, "goated_path_Ext", [ctypes.c_char_p], ctypes.c_char_p)
    result = lib.goated_path_Ext(_encode(path_))
    return _decode(result)


def IsAbs(path_: str) -> bool:
    """IsAbs reports whether the path is absolute."""
    if not is_library_available():
        # Pure Python fallback - POSIX style, so absolute = starts with /
        return path_.startswith("/")

    lib = get_lib()
    _configure_fn(lib, "goated_path_IsAbs", [ctypes.c_char_p], ctypes.c_bool)
    result = lib.goated_path_IsAbs(_encode(path_))
    return bool(result)


def Join(*elem: str) -> str:
    """Join joins any number of path elements into a single path,
    separating them with slashes. Empty elements are ignored.
    The result is Cleaned. However, if the argument list is
    empty or all its elements are empty, Join returns
    an empty string.
    """
    # Pure Python implementation (no FFI for this one usually)
    # Filter out empty strings
    parts = [e for e in elem if e]
    if not parts:
        return ""
    return _py_clean("/".join(parts))


def Split(path_: str) -> tuple[str, str]:
    """Split splits path immediately following the final slash,
    separating it into a directory and file name component.
    If there is no slash in path, Split returns an empty dir and
    file set to path.
    The returned values have the property that path = dir+file.
    """
    # Pure Python implementation
    i = path_.rfind("/")
    if i < 0:
        return "", path_
    return path_[: i + 1], path_[i + 1 :]


def Match(pattern: str, name: str) -> Result[bool, GoError]:
    r"""Match reports whether name matches the shell pattern.
    The pattern syntax is:

        pattern:
                { term }
        term:
                '*'         matches any sequence of non-/ characters
                '?'         matches any single non-/ character
                '[' [ '^' ] { character-range } ']'
                                character class (must be non-empty)
                c           matches character c (c != '*', '?', '\\', '[')
                '\\' c      matches character c

        character-range:
                c           matches character c (c != '\\', '-', ']')
                '\\' c      matches character c
                lo '-' hi   matches character c for lo <= c <= hi

    Match requires pattern to match all of name, not just a substring.
    The only possible returned error is [ErrBadPattern], when pattern
    is malformed.
    """
    if not is_library_available():
        # Pure Python fallback using fnmatch
        try:
            # Check for bad pattern - unclosed bracket
            bracket_depth = 0
            i = 0
            while i < len(pattern):
                c = pattern[i]
                if c == "\\" and i + 1 < len(pattern):
                    i += 2
                    continue
                if c == "[":
                    bracket_depth += 1
                    # Check for empty bracket expression
                    if i + 1 < len(pattern) and pattern[i + 1] == "]":
                        return Err(GoError("syntax error in pattern"))
                elif c == "]":
                    if bracket_depth > 0:
                        bracket_depth -= 1
                i += 1

            if bracket_depth > 0:
                return Err(GoError("syntax error in pattern"))

            # Use fnmatch for matching
            matched = fnmatch.fnmatch(name, pattern)
            return Ok(matched)
        except Exception:
            return Err(GoError("syntax error in pattern"))

    lib = get_lib()
    _configure_fn(
        lib,
        "goated_path_Match",
        [ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_char_p)],
        ctypes.c_bool,
    )
    err_out = ctypes.c_char_p()
    result = lib.goated_path_Match(_encode(pattern), _encode(name), ctypes.byref(err_out))

    if err_out.value:
        return Err(GoError(_decode(err_out.value)))
    return Ok(result)
