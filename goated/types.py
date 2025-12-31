"""Go type wrappers for Python.

This module provides Python classes that wrap Go types, enabling efficient
data exchange between Python and Go without unnecessary copying.

The key types are:
- GoSlice: Wraps Go slices ([]T)
- GoString: Wraps Go strings
- GoMap: Wraps Go maps (map[K]V)

These types integrate with ctypes for FFI and provide Pythonic interfaces.

Example:
    >>> from goated.types import GoSlice
    >>>
    >>> # From Python list
    >>> s = GoSlice.from_list([1, 2, 3, 4, 5])
    >>> print(s.to_list())
    [1, 2, 3, 4, 5]
    >>>
    >>> # Efficient iteration without copying
    >>> for item in s:
    ...     print(item)

"""

from __future__ import annotations

import ctypes
from collections.abc import ItemsView, Iterator, KeysView, Mapping, Sequence, ValuesView
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    TypeVar,
)

if TYPE_CHECKING:
    pass

__all__ = ["GoSlice", "GoString", "GoMap", "GoInt", "GoFloat64"]

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")

# Go's integer type (platform dependent, but we use int64 for safety)
GoInt = ctypes.c_int64
GoUint = ctypes.c_uint64
GoFloat64 = ctypes.c_double
GoFloat32 = ctypes.c_float
GoBool = ctypes.c_bool
GoByte = ctypes.c_uint8


class _GoSliceStruct(ctypes.Structure):
    """C struct representation of Go slice header.

    Matches: struct { void *data; GoInt len; GoInt cap; }
    """

    _fields_ = [
        ("data", ctypes.c_void_p),
        ("len", ctypes.c_int64),
        ("cap", ctypes.c_int64),
    ]


class _GoStringStruct(ctypes.Structure):
    """C struct representation of Go string header.

    Matches: struct { const char *p; GoInt n; }
    """

    _fields_ = [
        ("p", ctypes.c_char_p),
        ("n", ctypes.c_int64),
    ]


class GoSlice(Generic[T]):
    """Python wrapper for Go slices.

    Provides a Pythonic interface to Go slices with efficient memory handling.
    Supports iteration, indexing, and conversion to/from Python lists.

    The underlying data is managed by Go's runtime. This class holds a handle
    to the Go slice, not a copy of the data.

    Attributes:
        _handle: Internal handle to the Go slice
        _len: Length of the slice
        _cap: Capacity of the slice
        _elem_type: Type of elements (for ctypes)

    Example:
        >>> s = GoSlice.from_list([1, 2, 3])
        >>> len(s)
        3
        >>> s[0]
        1
        >>> list(s)
        [1, 2, 3]

    """

    __slots__ = ("_handle", "_len", "_cap", "_elem_type", "_data")

    def __init__(
        self,
        handle: int = 0,
        length: int = 0,
        capacity: int = 0,
        elem_type: type = ctypes.c_int64,
        data: Any = None,
    ) -> None:
        """Initialize a GoSlice.

        Usually created via from_list() or returned from Go functions.

        Args:
            handle: Go handle to the slice (0 for empty/local)
            length: Number of elements
            capacity: Capacity of the slice
            elem_type: ctypes type of elements
            data: Raw ctypes array (for locally created slices)

        """
        self._handle = handle
        self._len = length
        self._cap = capacity if capacity > 0 else length
        self._elem_type = elem_type
        self._data = data

    @classmethod
    def from_list(
        cls,
        items: Sequence[T],
        elem_type: type = ctypes.c_int64,
    ) -> GoSlice[T]:
        """Create a GoSlice from a Python sequence.

        Args:
            items: Python sequence to convert
            elem_type: ctypes type for elements (default: int64)

        Returns:
            A new GoSlice containing the items

        Example:
            >>> s = GoSlice.from_list([1, 2, 3, 4, 5])
            >>> s.to_list()
            [1, 2, 3, 4, 5]
            >>>
            >>> # With specific type
            >>> s = GoSlice.from_list([1.5, 2.5], elem_type=ctypes.c_double)

        """
        n = len(items)
        if n == 0:
            return cls(handle=0, length=0, capacity=0, elem_type=elem_type)

        # Create ctypes array (type: ignore for ctypes dynamic array creation)
        ArrayType = elem_type * n  # type: ignore[operator]
        data = ArrayType(*items)  # type: ignore[operator]

        return cls(
            handle=0,
            length=n,
            capacity=n,
            elem_type=elem_type,
            data=data,
        )

    @staticmethod
    def from_bytes(data: bytes) -> GoSlice[int]:
        """Create a GoSlice[byte] from Python bytes.

        Args:
            data: Python bytes object

        Returns:
            A GoSlice containing the bytes

        """
        n = len(data)
        ArrayType = ctypes.c_uint8 * n
        arr = ArrayType(*data)
        return GoSlice[int](
            handle=0,
            length=n,
            capacity=n,
            elem_type=ctypes.c_uint8,
            data=arr,
        )

    def to_list(self) -> list[T]:
        """Convert the GoSlice to a Python list.

        Returns:
            A new Python list containing copies of all elements

        Example:
            >>> s = GoSlice.from_list([1, 2, 3])
            >>> s.to_list()
            [1, 2, 3]

        """
        if self._len == 0:
            return []

        if self._data is not None:
            return list(self._data[: self._len])

        # For Go-managed slices, we need to fetch through FFI
        # This will be implemented when we have the Go library loaded
        raise NotImplementedError("Go-managed slice conversion not yet implemented")

    def to_bytes(self) -> bytes:
        """Convert a byte slice to Python bytes.

        Returns:
            Python bytes object

        Raises:
            TypeError: If slice is not a byte slice

        """
        if self._elem_type != ctypes.c_uint8:
            raise TypeError("to_bytes() only works on byte slices")

        if self._len == 0:
            return b""

        if self._data is not None:
            return bytes(self._data[: self._len])

        raise NotImplementedError("Go-managed slice conversion not yet implemented")

    def to_struct(self) -> _GoSliceStruct:
        """Get the ctypes struct representation for FFI calls.

        Returns:
            _GoSliceStruct ready for passing to Go

        """
        struct = _GoSliceStruct()
        if self._data is not None:
            struct.data = ctypes.cast(self._data, ctypes.c_void_p)
        else:
            struct.data = ctypes.c_void_p(0)
        struct.len = self._len
        struct.cap = self._cap
        return struct

    def __len__(self) -> int:
        """Return the length of the slice."""
        return self._len

    def __getitem__(self, index: int) -> T:
        """Get an element by index.

        Args:
            index: Index (supports negative indexing)

        Returns:
            The element at the given index

        Raises:
            IndexError: If index is out of bounds

        """
        if index < 0:
            index = self._len + index
        if index < 0 or index >= self._len:
            raise IndexError(f"index {index} out of range for slice of length {self._len}")

        if self._data is not None:
            return self._data[index]  # type: ignore[no-any-return]

        raise NotImplementedError("Go-managed slice access not yet implemented")

    def __iter__(self) -> Iterator[T]:
        """Iterate over slice elements."""
        for i in range(self._len):
            yield self[i]

    def __contains__(self, item: T) -> bool:
        """Check if item is in the slice."""
        return any(x == item for x in self)

    def __repr__(self) -> str:
        if self._len <= 10:
            items = self.to_list()
            return f"GoSlice({items})"
        else:
            first_items = [self[i] for i in range(5)]
            return f"GoSlice([{', '.join(map(str, first_items))}, ... ({self._len} items)])"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, GoSlice):
            return self.to_list() == other.to_list()
        if isinstance(other, (list, tuple)):
            return self.to_list() == list(other)
        return False

    @property
    def capacity(self) -> int:
        """Return the capacity of the slice."""
        return self._cap


class GoString:
    """Python wrapper for Go strings.

    Go strings are immutable sequences of bytes (usually UTF-8). This class
    provides efficient conversion between Python strings and Go strings.

    Attributes:
        _data: The string data
        _len: Length in bytes

    Example:
        >>> s = GoString.from_str("Hello, World!")
        >>> str(s)
        'Hello, World!'
        >>> len(s)
        13

    """

    __slots__ = ("_data", "_len", "_bytes")

    def __init__(self, data: bytes = b"", length: int | None = None) -> None:
        """Initialize a GoString.

        Args:
            data: UTF-8 encoded bytes
            length: Length in bytes (computed if not provided)

        """
        self._bytes = data
        self._len = length if length is not None else len(data)
        # Keep reference to prevent garbage collection
        self._data = ctypes.c_char_p(data)

    @classmethod
    def from_str(cls, s: str) -> GoString:
        """Create a GoString from a Python string.

        Args:
            s: Python string

        Returns:
            A new GoString

        Example:
            >>> gs = GoString.from_str("hello")
            >>> str(gs)
            'hello'

        """
        encoded = s.encode("utf-8")
        return cls(encoded, len(encoded))

    def to_str(self) -> str:
        """Convert to a Python string.

        Returns:
            Python string (decoded from UTF-8)

        """
        return self._bytes.decode("utf-8")

    def to_bytes(self) -> bytes:
        """Get the raw bytes.

        Returns:
            The underlying bytes

        """
        return self._bytes

    def to_struct(self) -> _GoStringStruct:
        """Get the ctypes struct representation for FFI calls.

        Returns:
            _GoStringStruct ready for passing to Go

        """
        struct = _GoStringStruct()
        struct.p = self._data
        struct.n = self._len
        return struct

    def __str__(self) -> str:
        return self.to_str()

    def __repr__(self) -> str:
        return f"GoString({self._bytes!r})"

    def __len__(self) -> int:
        """Return length in bytes."""
        return self._len

    def __eq__(self, other: object) -> bool:
        if isinstance(other, GoString):
            return self._bytes == other._bytes
        if isinstance(other, str):
            return self.to_str() == other
        if isinstance(other, bytes):
            return self._bytes == other
        return False

    def __hash__(self) -> int:
        return hash(self._bytes)


class GoMap(Generic[K, V]):
    """Python wrapper for Go maps.

    Provides a dict-like interface to Go maps. Supports iteration,
    membership testing, and conversion to Python dicts.

    Note: Go maps are not ordered (until Go 1.12+), so iteration order
    may differ from Python dicts.

    Attributes:
        _handle: Internal handle to the Go map

    Example:
        >>> m = GoMap.from_dict({"a": 1, "b": 2})
        >>> m["a"]
        1
        >>> dict(m)
        {'a': 1, 'b': 2}

    """

    __slots__ = ("_handle", "_dict", "_key_type", "_value_type")

    def __init__(
        self,
        handle: int = 0,
        data: dict[K, V] | None = None,
        key_type: type = str,
        value_type: type = int,
    ) -> None:
        """Initialize a GoMap.

        Args:
            handle: Go handle to the map (0 for local)
            data: Python dict for locally created maps
            key_type: Type of keys
            value_type: Type of values

        """
        self._handle = handle
        self._dict = data if data is not None else {}
        self._key_type = key_type
        self._value_type = value_type

    @classmethod
    def from_dict(
        cls,
        d: Mapping[K, V],
        key_type: type = str,
        value_type: type = int,
    ) -> GoMap[K, V]:
        """Create a GoMap from a Python dict.

        Args:
            d: Python dict to convert
            key_type: Type of keys
            value_type: Type of values

        Returns:
            A new GoMap

        """
        return cls(handle=0, data=dict(d), key_type=key_type, value_type=value_type)

    def to_dict(self) -> dict[K, V]:
        """Convert to a Python dict.

        Returns:
            A new Python dict with copies of all items

        """
        return dict(self._dict)

    def __getitem__(self, key: K) -> V:
        """Get value by key."""
        return self._dict[key]

    def __setitem__(self, key: K, value: V) -> None:
        """Set value for key."""
        self._dict[key] = value

    def __delitem__(self, key: K) -> None:
        """Delete key."""
        del self._dict[key]

    def __contains__(self, key: object) -> bool:
        """Check if key exists."""
        return key in self._dict

    def __len__(self) -> int:
        """Return number of items."""
        return len(self._dict)

    def __iter__(self) -> Iterator[K]:
        """Iterate over keys."""
        return iter(self._dict)

    def keys(self) -> KeysView[K]:
        """Return keys view."""
        return self._dict.keys()

    def values(self) -> ValuesView[V]:
        """Return values view."""
        return self._dict.values()

    def items(self) -> ItemsView[K, V]:
        """Return items view."""
        return self._dict.items()

    def get(self, key: K, default: V | None = None) -> V | None:
        """Get value with default."""
        return self._dict.get(key, default)

    def __repr__(self) -> str:
        return f"GoMap({self._dict!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, GoMap):
            return self._dict == other._dict
        if isinstance(other, dict):
            return self._dict == other
        return False
