"""Go standard library bindings - Pythonic style.

This module provides Python-friendly wrappers around Go's standard library.
All functions use snake_case naming and return native Python types where possible.

Available packages:
- strings: String manipulation functions

Example:
    >>> from goated.pythonic import strings
    >>>
    >>> strings.split("a,b,c", ",")
    ['a', 'b', 'c']
    >>>
    >>> strings.contains("hello", "ell")
    True

"""

__all__ = ["strings"]


from types import ModuleType


def __getattr__(name: str) -> ModuleType:
    if name == "strings":
        import importlib

        return importlib.import_module("goated.pythonic.strings")
    raise AttributeError(f"module 'goated.pythonic' has no attribute {name!r}")
