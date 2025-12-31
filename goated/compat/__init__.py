"""Drop-in replacements for Python standard library modules.

These modules provide the same API as Python's stdlib but use Go implementations
under the hood when available for potentially better performance.

Usage:
    # Replace stdlib imports
    from goated.compat import json  # instead of: import json
    from goated.compat import re    # instead of: import re
    from goated.compat import hashlib
    from goated.compat import base64

    # Or use as a namespace
    from goated import compat
    compat.json.dumps({"key": "value"})

The modules will automatically use Go implementations when the shared library
is available, and fall back to Python's stdlib when it's not.
"""

from goated.compat import base64, hashlib, json, re

__all__ = [
    "json",
    "re",
    "hashlib",
    "base64",
]
