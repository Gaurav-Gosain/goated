"""Drop-in replacement for Python's json module, backed by Go's encoding/json.

Uses Go FFI for JSON validation (valid function).
dumps/loads use Python's _json C accelerator which is already very fast.

Usage:
    from goated.compat import json
    data = json.loads('{"key": "value"}')
    text = json.dumps({"key": "value"})
"""

from __future__ import annotations

import ctypes
import json as _json

# Re-export types and classes unchanged
from json import (  # noqa: F401
    JSONDecodeError,
    JSONDecoder,
    JSONEncoder,
)
from typing import Any

from goated._core import _USE_GO_LIB, get_lib

_GO_THRESHOLD = 1024
_lib_setup = False


def _setup_lib() -> None:
    global _lib_setup
    if _lib_setup or not _USE_GO_LIB:
        return
    try:
        lib = get_lib().lib
        lib.goated_json_Valid.argtypes = [ctypes.c_char_p, ctypes.c_longlong]
        lib.goated_json_Valid.restype = ctypes.c_bool
        _lib_setup = True
    except Exception:
        pass


def dumps(obj: Any, **kwargs: Any) -> str:
    """Serialize obj to a JSON formatted string."""
    return _json.dumps(obj, **kwargs)


def loads(s: str | bytes, **kwargs: Any) -> Any:
    """Deserialize s to a Python object."""
    return _json.loads(s, **kwargs)


def dump(obj: Any, fp: Any, **kwargs: Any) -> None:
    """Serialize obj as JSON to fp (file-like object)."""
    _json.dump(obj, fp, **kwargs)


def load(fp: Any, **kwargs: Any) -> Any:
    """Deserialize fp (file-like object) to Python object."""
    return _json.load(fp, **kwargs)


def valid(s: str | bytes) -> bool:
    """Check if s is valid JSON. Go-accelerated for large inputs.

    This is a goated extension -- not part of Python's json module.
    """
    if _USE_GO_LIB:
        _setup_lib()
        if _lib_setup:
            try:
                lib = get_lib().lib
                if isinstance(s, str):
                    s = s.encode("utf-8")
                return bool(lib.goated_json_Valid(s, ctypes.c_longlong(len(s))))
            except Exception:
                pass
    try:
        _json.loads(s)
        return True
    except (ValueError, TypeError):
        return False


__all__ = [
    "dump",
    "dumps",
    "load",
    "loads",
    "valid",
    "JSONDecodeError",
    "JSONEncoder",
    "JSONDecoder",
]
