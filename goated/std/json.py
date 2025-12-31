"""Go encoding/json package bindings - Direct mapping style.

This module provides Python bindings for Go's encoding/json package.

Example:
    >>> from goated.std import json as gojson
    >>>
    >>> data = {"name": "Go", "version": 1.21}
    >>> gojson.Marshal(data)
    Ok('{"name":"Go","version":1.21}')
    >>> gojson.Valid('{"valid": true}')
    True

"""

from __future__ import annotations

import json
from typing import Any

from goated.result import Err, GoError, Ok, Result

__all__ = [
    "Marshal",
    "MarshalIndent",
    "Unmarshal",
    "Valid",
    "Compact",
]


def Marshal(v: Any) -> Result[str, GoError]:
    """Returns the JSON encoding of v."""
    try:
        return Ok(json.dumps(v, separators=(",", ":")))
    except (TypeError, ValueError) as e:
        return Err(GoError(str(e), "json.MarshalerError"))


def MarshalIndent(v: Any, prefix: str = "", indent: str = "  ") -> Result[str, GoError]:
    """Returns the indented JSON encoding of v."""
    try:
        result = json.dumps(v, indent=len(indent) if indent else None, separators=(",", ": "))
        if prefix:
            lines = result.split("\n")
            result = "\n".join(prefix + line for line in lines)
        return Ok(result)
    except (TypeError, ValueError) as e:
        return Err(GoError(str(e), "json.MarshalerError"))


def Unmarshal(data: str | bytes) -> Result[Any, GoError]:
    """Parses the JSON-encoded data and returns the result."""
    try:
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        return Ok(json.loads(data))
    except json.JSONDecodeError as e:
        return Err(GoError(str(e), "json.SyntaxError"))


def Valid(data: str | bytes) -> bool:
    """Reports whether data is a valid JSON encoding."""
    try:
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        json.loads(data)
        return True
    except (json.JSONDecodeError, UnicodeDecodeError):
        return False


def Compact(src: str | bytes) -> Result[str, GoError]:
    """Appends to dst the JSON-encoded src with insignificant space characters elided."""
    try:
        if isinstance(src, bytes):
            src = src.decode("utf-8")
        parsed = json.loads(src)
        return Ok(json.dumps(parsed, separators=(",", ":")))
    except json.JSONDecodeError as e:
        return Err(GoError(str(e), "json.SyntaxError"))
