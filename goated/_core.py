"""Core FFI binding loader for Goated.

This module handles loading the Go shared library and provides the low-level
interface for calling Go functions from Python.

The library is loaded lazily on first use, and the path is determined by:
1. GOATED_LIB environment variable
2. Platform-specific library in the package directory

Example:
    >>> from goated._core import get_lib
    >>> lib = get_lib()
    >>> # Now use lib to call Go functions

"""

from __future__ import annotations

import ctypes
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ctypes import CDLL

__all__ = ["get_lib", "GoatedLibrary", "LibraryNotFoundError"]


class LibraryNotFoundError(Exception):
    """Raised when the Go shared library cannot be found or loaded."""

    pass


def _get_lib_extension() -> str:
    """Get the platform-specific shared library extension."""
    if sys.platform == "win32":
        return "dll"
    elif sys.platform == "darwin":
        return "dylib"
    else:
        return "so"


def _get_lib_name() -> str:
    """Get the platform-specific library filename."""
    ext = _get_lib_extension()
    return f"libgoated.{ext}"


def _find_library_path() -> Path:
    """Find the path to the Go shared library.

    Search order:
    1. GOATED_LIB environment variable
    2. Package directory (goated/)
    3. Current working directory

    Returns:
        Path to the library file

    Raises:
        LibraryNotFoundError: If library cannot be found

    """
    # Check environment variable first
    env_path = os.environ.get("GOATED_LIB")
    if env_path:
        path = Path(env_path)
        if path.exists():
            return path
        raise LibraryNotFoundError(f"GOATED_LIB points to non-existent file: {env_path}")

    lib_name = _get_lib_name()

    # Check package directory
    package_dir = Path(__file__).parent
    package_lib = package_dir / lib_name
    if package_lib.exists():
        return package_lib

    # Check current directory
    cwd_lib = Path.cwd() / lib_name
    if cwd_lib.exists():
        return cwd_lib

    # Not found
    raise LibraryNotFoundError(
        f"Could not find {lib_name}. "
        f"Searched: {package_dir}, {Path.cwd()}. "
        f"Set GOATED_LIB environment variable to the library path, "
        f"or run 'make build' to compile it."
    )


class GoatedLibrary:
    """Wrapper around the Go shared library.

    Provides a clean interface for calling Go functions with proper
    type conversions and error handling.

    Attributes:
        _lib: The underlying ctypes CDLL
        _loaded: Whether the library has been loaded

    """

    __slots__ = ("_lib", "_loaded", "_path")

    def __init__(self) -> None:
        self._lib: CDLL | None = None
        self._loaded = False
        self._path: Path | None = None

    def _ensure_loaded(self) -> CDLL:
        """Ensure the library is loaded, loading it if necessary."""
        if not self._loaded:
            self._load()
        assert self._lib is not None
        return self._lib

    def _load(self) -> None:
        """Load the Go shared library."""
        if self._loaded:
            return

        try:
            self._path = _find_library_path()
            self._lib = ctypes.CDLL(str(self._path))
            self._loaded = True
            self._setup_functions()
        except OSError as e:
            raise LibraryNotFoundError(f"Failed to load library: {e}") from e

    def _setup_functions(self) -> None:
        """Set up function signatures for type safety."""
        if self._lib is None:
            return

        # Handle management functions
        self._try_setup(
            "goated_handle_delete",
            argtypes=[ctypes.c_uint64],
            restype=None,
        )

        # String functions
        self._try_setup(
            "goated_strings_Contains",
            argtypes=[ctypes.c_char_p, ctypes.c_char_p],
            restype=ctypes.c_bool,
        )

        self._try_setup(
            "goated_strings_Count",
            argtypes=[ctypes.c_char_p, ctypes.c_char_p],
            restype=ctypes.c_int64,
        )

        self._try_setup(
            "goated_strings_HasPrefix",
            argtypes=[ctypes.c_char_p, ctypes.c_char_p],
            restype=ctypes.c_bool,
        )

        self._try_setup(
            "goated_strings_HasSuffix",
            argtypes=[ctypes.c_char_p, ctypes.c_char_p],
            restype=ctypes.c_bool,
        )

        self._try_setup(
            "goated_strings_Index",
            argtypes=[ctypes.c_char_p, ctypes.c_char_p],
            restype=ctypes.c_int64,
        )

        self._try_setup(
            "goated_strings_Join",
            argtypes=[ctypes.c_void_p, ctypes.c_int64, ctypes.c_char_p],
            restype=ctypes.c_char_p,
        )

        self._try_setup(
            "goated_strings_Repeat",
            argtypes=[ctypes.c_char_p, ctypes.c_int64],
            restype=ctypes.c_char_p,
        )

        self._try_setup(
            "goated_strings_Replace",
            argtypes=[ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int64],
            restype=ctypes.c_char_p,
        )

        self._try_setup(
            "goated_strings_Split",
            argtypes=[ctypes.c_char_p, ctypes.c_char_p],
            restype=ctypes.c_uint64,  # Returns handle
        )

        self._try_setup(
            "goated_strings_ToLower",
            argtypes=[ctypes.c_char_p],
            restype=ctypes.c_char_p,
        )

        self._try_setup(
            "goated_strings_ToUpper",
            argtypes=[ctypes.c_char_p],
            restype=ctypes.c_char_p,
        )

        self._try_setup(
            "goated_strings_ToTitle",
            argtypes=[ctypes.c_char_p],
            restype=ctypes.c_char_p,
        )

        self._try_setup(
            "goated_strings_Title",
            argtypes=[ctypes.c_char_p],
            restype=ctypes.c_char_p,
        )

        self._try_setup(
            "goated_strings_ReplaceAll",
            argtypes=[ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p],
            restype=ctypes.c_char_p,
        )

        self._try_setup(
            "goated_strings_Trim",
            argtypes=[ctypes.c_char_p, ctypes.c_char_p],
            restype=ctypes.c_char_p,
        )

        self._try_setup(
            "goated_strings_TrimLeft",
            argtypes=[ctypes.c_char_p, ctypes.c_char_p],
            restype=ctypes.c_char_p,
        )

        self._try_setup(
            "goated_strings_TrimRight",
            argtypes=[ctypes.c_char_p, ctypes.c_char_p],
            restype=ctypes.c_char_p,
        )

        self._try_setup(
            "goated_strings_TrimSpace",
            argtypes=[ctypes.c_char_p],
            restype=ctypes.c_char_p,
        )

        self._try_setup(
            "goated_strings_TrimPrefix",
            argtypes=[ctypes.c_char_p, ctypes.c_char_p],
            restype=ctypes.c_char_p,
        )

        self._try_setup(
            "goated_strings_TrimSuffix",
            argtypes=[ctypes.c_char_p, ctypes.c_char_p],
            restype=ctypes.c_char_p,
        )

        # Slice helper functions
        self._try_setup(
            "goated_slice_string_len",
            argtypes=[ctypes.c_uint64],
            restype=ctypes.c_int64,
        )

        self._try_setup(
            "goated_slice_string_get",
            argtypes=[ctypes.c_uint64, ctypes.c_int64],
            restype=ctypes.c_char_p,
        )

        self._try_setup(
            "goated_free_string",
            argtypes=[ctypes.c_char_p],
            restype=None,
        )

    def _try_setup(
        self,
        name: str,
        argtypes: list[Any],
        restype: Any,
    ) -> None:
        """Try to set up a function, ignoring if not found."""
        if self._lib is None:
            return
        try:
            func = getattr(self._lib, name)
            func.argtypes = argtypes
            func.restype = restype
        except AttributeError:
            # Function not in library - might be added later
            pass

    @property
    def lib(self) -> CDLL:
        """Get the underlying ctypes library."""
        return self._ensure_loaded()

    @property
    def loaded(self) -> bool:
        """Check if the library is loaded."""
        return self._loaded

    @property
    def path(self) -> Path | None:
        """Get the path to the loaded library."""
        return self._path

    def __getattr__(self, name: str) -> Any:
        """Forward attribute access to the underlying library."""
        lib = self._ensure_loaded()
        return getattr(lib, name)


# Global library instance (lazy singleton)
_library: GoatedLibrary | None = None


def get_lib() -> GoatedLibrary:
    """Get the global Goated library instance.

    The library is loaded lazily on first access.

    Returns:
        The GoatedLibrary instance

    Raises:
        LibraryNotFoundError: If the library cannot be found or loaded

    Example:
        >>> lib = get_lib()
        >>> result = lib.goated_strings_Contains(b"hello", b"ell")
        >>> print(result)
        True

    """
    global _library
    if _library is None:
        _library = GoatedLibrary()
    return _library


_library_available_cache: bool | None = None


def is_library_available() -> bool:
    """Check if the Go library is available without loading it.

    Returns:
        True if the library file exists and can be found

    """
    global _library_available_cache
    if _library_available_cache is not None:
        return _library_available_cache
    try:
        _find_library_path()
        _library_available_cache = True
    except LibraryNotFoundError:
        _library_available_cache = False
    return _library_available_cache


# Pre-compute at module load time for zero-overhead checks
_USE_GO_LIB: bool = is_library_available()
