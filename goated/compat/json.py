"""Drop-in replacement for Python's json module.

This module provides the same API as Python's json module.
Future versions may use Go's encoding/json for performance when available.

Usage:
    from goated.compat import json

    # Same API as stdlib json
    data = json.loads('{"key": "value"}')
    text = json.dumps({"key": "value"})
"""

from __future__ import annotations

# Re-export everything from Python's json module
from json import (
    JSONDecodeError,
    JSONDecoder,
    JSONEncoder,
    dump,
    dumps,
    load,
    loads,
)

__all__ = [
    "dump",
    "dumps",
    "load",
    "loads",
    "JSONDecodeError",
    "JSONEncoder",
    "JSONDecoder",
]
