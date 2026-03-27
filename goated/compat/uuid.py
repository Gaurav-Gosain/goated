"""Drop-in replacement for Python's uuid module, backed by Go's crypto/rand.

Uses Go FFI for uuid4 generation (Go's crypto/rand is fast).
Falls back to Python for uuid1, uuid3, uuid5, and UUID class operations.

Usage:
    from goated.compat import uuid
    u = uuid.uuid4()
    batch = uuid.batch_uuid4(1000)
"""

from __future__ import annotations

import ctypes
import uuid as _uuid

# Re-export everything from Python's uuid
from uuid import (  # noqa: F401
    NAMESPACE_DNS,
    NAMESPACE_OID,
    NAMESPACE_URL,
    NAMESPACE_X500,
    RESERVED_FUTURE,
    RESERVED_MICROSOFT,
    RESERVED_NCS,
    RFC_4122,
    UUID,
    getnode,
    uuid1,
    uuid3,
    uuid5,
)

from goated._core import _USE_GO_LIB, get_lib

_lib_setup = False


def _setup_lib() -> None:
    global _lib_setup
    if _lib_setup or not _USE_GO_LIB:
        return
    try:
        lib = get_lib().lib
        lib.goated_uuid4.argtypes = []
        lib.goated_uuid4.restype = ctypes.c_char_p
        lib.goated_batch_uuid4.argtypes = [
            ctypes.c_int,  # count
            ctypes.POINTER(ctypes.c_char_p),  # results
        ]
        lib.goated_batch_uuid4.restype = None
        _lib_setup = True
    except Exception:
        pass


def uuid4() -> _uuid.UUID:
    """Generate a random UUID (version 4). Go-accelerated."""
    if _USE_GO_LIB:
        # Prefer cffi
        from goated._core import get_cffi_lib

        cffi_lib = get_cffi_lib()
        if cffi_lib is not None:
            try:
                from goated._core import _cffi_ffi

                result = cffi_lib.goated_uuid4()
                if result:
                    return _uuid.UUID(_cffi_ffi.string(result).decode("utf-8"))
            except Exception:
                pass

        # Fallback to ctypes
        _setup_lib()
        if _lib_setup:
            try:
                lib = get_lib().lib
                result = lib.goated_uuid4()
                if result:
                    return _uuid.UUID(result.decode("utf-8"))
            except Exception:
                pass

    return _uuid.uuid4()


def batch_uuid4(n: int) -> list[_uuid.UUID]:
    """Generate n random UUIDs (version 4). Go-accelerated batch.

    This is a goated extension -- not part of Python's uuid module.
    """
    if n <= 0:
        return []

    if _USE_GO_LIB:
        # Prefer cffi
        from goated._core import get_cffi_lib

        cffi_lib = get_cffi_lib()
        if cffi_lib is not None:
            try:
                from goated._core import _cffi_ffi

                results = _cffi_ffi.new("char*[]", n)
                cffi_lib.goated_batch_uuid4(n, results)
                uuids = []
                for i in range(n):
                    if results[i]:
                        uuids.append(_uuid.UUID(_cffi_ffi.string(results[i]).decode("utf-8")))
                    else:
                        uuids.append(_uuid.uuid4())
                return uuids
            except Exception:
                pass

        # Fallback to ctypes
        _setup_lib()
        if _lib_setup:
            try:
                lib = get_lib().lib
                results = (ctypes.c_char_p * n)()
                lib.goated_batch_uuid4(n, results)
                uuids = []
                for i in range(n):
                    if results[i]:
                        uuids.append(_uuid.UUID(results[i].decode("utf-8")))
                    else:
                        uuids.append(_uuid.uuid4())
                return uuids
            except Exception:
                pass

    return [_uuid.uuid4() for _ in range(n)]


__all__ = [
    "UUID",
    "uuid1",
    "uuid3",
    "uuid4",
    "uuid5",
    "batch_uuid4",
    "getnode",
    "NAMESPACE_DNS",
    "NAMESPACE_URL",
    "NAMESPACE_OID",
    "NAMESPACE_X500",
    "RESERVED_NCS",
    "RFC_4122",
    "RESERVED_MICROSOFT",
    "RESERVED_FUTURE",
]
