"""Go unicode package bindings.

This module provides Python bindings for Go's unicode package.
"""

from __future__ import annotations

import ctypes
import unicodedata

from goated._core import get_lib, is_library_available

__all__ = [
    "IsControl",
    "IsDigit",
    "IsGraphic",
    "IsLetter",
    "IsLower",
    "IsMark",
    "IsNumber",
    "IsPrint",
    "IsPunct",
    "IsSpace",
    "IsSymbol",
    "IsTitle",
    "IsUpper",
    "SimpleFold",
    "To",
    "ToLower",
    "ToTitle",
    "ToUpper",
    # Case constants
    "UpperCase",
    "LowerCase",
    "TitleCase",
    "MaxRune",
    "ReplacementChar",
]

# Case constants
UpperCase = 0
LowerCase = 1
TitleCase = 2

# Unicode constants
MaxRune = 0x10FFFF  # Maximum valid Unicode code point
ReplacementChar = "\ufffd"  # Unicode replacement character

_fn_configured: set[str] = set()


def _configure_fn(lib: object, name: str, argtypes: list[type], restype: type) -> None:
    if name in _fn_configured:
        return
    fn = getattr(lib, name)
    fn.argtypes = argtypes
    fn.restype = restype
    _fn_configured.add(name)


def _get_rune(r: str | int) -> int:
    """Convert a string character to its code point (rune)."""
    if isinstance(r, int):
        return r
    if isinstance(r, str) and len(r) > 0:
        return ord(r[0])
    return 0


def _from_rune(r: int) -> str:
    """Convert a code point (rune) to a string character."""
    try:
        return chr(r)
    except (ValueError, OverflowError):
        return ReplacementChar


def IsControl(r: str | int) -> bool:
    """IsControl reports whether the rune is a control character."""
    rune = _get_rune(r)

    if is_library_available():
        try:
            lib = get_lib()
            _configure_fn(lib, "goated_unicode_IsControl", [ctypes.c_int], ctypes.c_bool)
            return bool(lib.goated_unicode_IsControl(rune))
        except Exception:
            pass

    # Pure Python fallback
    if rune < 0 or rune > MaxRune:
        return False
    try:
        char = chr(rune)
        cat = unicodedata.category(char)
        return cat.startswith("C") and cat != "Co"
    except (ValueError, OverflowError):
        return False


def IsDigit(r: str | int) -> bool:
    """IsDigit reports whether the rune is a decimal digit."""
    rune = _get_rune(r)

    if is_library_available():
        try:
            lib = get_lib()
            _configure_fn(lib, "goated_unicode_IsDigit", [ctypes.c_int], ctypes.c_bool)
            return bool(lib.goated_unicode_IsDigit(rune))
        except Exception:
            pass

    # Pure Python fallback
    if rune < 0 or rune > MaxRune:
        return False
    try:
        char = chr(rune)
        cat = unicodedata.category(char)
        return cat == "Nd"
    except (ValueError, OverflowError):
        return False


def IsGraphic(r: str | int) -> bool:
    """IsGraphic reports whether the rune is defined as a Graphic by Unicode."""
    rune = _get_rune(r)

    if is_library_available():
        try:
            lib = get_lib()
            _configure_fn(lib, "goated_unicode_IsGraphic", [ctypes.c_int], ctypes.c_bool)
            return bool(lib.goated_unicode_IsGraphic(rune))
        except Exception:
            pass

    # Pure Python fallback
    if rune < 0 or rune > MaxRune:
        return False
    try:
        char = chr(rune)
        cat = unicodedata.category(char)
        return cat[0] in ("L", "M", "N", "P", "S") or cat == "Zs"
    except (ValueError, OverflowError):
        return False


def IsLetter(r: str | int) -> bool:
    """IsLetter reports whether the rune is a letter (category [L])."""
    rune = _get_rune(r)

    if is_library_available():
        try:
            lib = get_lib()
            _configure_fn(lib, "goated_unicode_IsLetter", [ctypes.c_int], ctypes.c_bool)
            return bool(lib.goated_unicode_IsLetter(rune))
        except Exception:
            pass

    # Pure Python fallback
    if rune < 0 or rune > MaxRune:
        return False
    try:
        char = chr(rune)
        cat = unicodedata.category(char)
        return cat.startswith("L")
    except (ValueError, OverflowError):
        return False


def IsLower(r: str | int) -> bool:
    """IsLower reports whether the rune is a lower case letter."""
    rune = _get_rune(r)

    if is_library_available():
        try:
            lib = get_lib()
            _configure_fn(lib, "goated_unicode_IsLower", [ctypes.c_int], ctypes.c_bool)
            return bool(lib.goated_unicode_IsLower(rune))
        except Exception:
            pass

    # Pure Python fallback
    if rune < 0 or rune > MaxRune:
        return False
    try:
        char = chr(rune)
        cat = unicodedata.category(char)
        return cat == "Ll"
    except (ValueError, OverflowError):
        return False


def IsMark(r: str | int) -> bool:
    """IsMark reports whether the rune is a mark character (category [M])."""
    rune = _get_rune(r)

    if is_library_available():
        try:
            lib = get_lib()
            _configure_fn(lib, "goated_unicode_IsMark", [ctypes.c_int], ctypes.c_bool)
            return bool(lib.goated_unicode_IsMark(rune))
        except Exception:
            pass

    # Pure Python fallback
    if rune < 0 or rune > MaxRune:
        return False
    try:
        char = chr(rune)
        cat = unicodedata.category(char)
        return cat.startswith("M")
    except (ValueError, OverflowError):
        return False


def IsNumber(r: str | int) -> bool:
    """IsNumber reports whether the rune is a number (category [N])."""
    rune = _get_rune(r)

    if is_library_available():
        try:
            lib = get_lib()
            _configure_fn(lib, "goated_unicode_IsNumber", [ctypes.c_int], ctypes.c_bool)
            return bool(lib.goated_unicode_IsNumber(rune))
        except Exception:
            pass

    # Pure Python fallback
    if rune < 0 or rune > MaxRune:
        return False
    try:
        char = chr(rune)
        cat = unicodedata.category(char)
        return cat.startswith("N")
    except (ValueError, OverflowError):
        return False


def IsPrint(r: str | int) -> bool:
    """IsPrint reports whether the rune is defined as printable by Go."""
    rune = _get_rune(r)

    if is_library_available():
        try:
            lib = get_lib()
            _configure_fn(lib, "goated_unicode_IsPrint", [ctypes.c_int], ctypes.c_bool)
            return bool(lib.goated_unicode_IsPrint(rune))
        except Exception:
            pass

    # Pure Python fallback
    if rune < 0 or rune > MaxRune:
        return False
    try:
        char = chr(rune)
        if rune == 0x20:
            return True
        cat = unicodedata.category(char)
        return cat[0] in ("L", "M", "N", "P", "S")
    except (ValueError, OverflowError):
        return False


def IsPunct(r: str | int) -> bool:
    """IsPunct reports whether the rune is a Unicode punctuation character."""
    rune = _get_rune(r)

    if is_library_available():
        try:
            lib = get_lib()
            _configure_fn(lib, "goated_unicode_IsPunct", [ctypes.c_int], ctypes.c_bool)
            return bool(lib.goated_unicode_IsPunct(rune))
        except Exception:
            pass

    # Pure Python fallback
    if rune < 0 or rune > MaxRune:
        return False
    try:
        char = chr(rune)
        cat = unicodedata.category(char)
        return cat.startswith("P")
    except (ValueError, OverflowError):
        return False


def IsSpace(r: str | int) -> bool:
    """IsSpace reports whether the rune is a space character."""
    rune = _get_rune(r)

    if is_library_available():
        try:
            lib = get_lib()
            _configure_fn(lib, "goated_unicode_IsSpace", [ctypes.c_int], ctypes.c_bool)
            return bool(lib.goated_unicode_IsSpace(rune))
        except Exception:
            pass

    # Pure Python fallback - Go's whitespace definition
    whitespace = {
        0x09,
        0x0A,
        0x0B,
        0x0C,
        0x0D,
        0x20,
        0x85,
        0xA0,
        0x1680,
        0x2000,
        0x2001,
        0x2002,
        0x2003,
        0x2004,
        0x2005,
        0x2006,
        0x2007,
        0x2008,
        0x2009,
        0x200A,
        0x2028,
        0x2029,
        0x202F,
        0x205F,
        0x3000,
    }
    return rune in whitespace


def IsSymbol(r: str | int) -> bool:
    """IsSymbol reports whether the rune is a symbolic character."""
    rune = _get_rune(r)

    if is_library_available():
        try:
            lib = get_lib()
            _configure_fn(lib, "goated_unicode_IsSymbol", [ctypes.c_int], ctypes.c_bool)
            return bool(lib.goated_unicode_IsSymbol(rune))
        except Exception:
            pass

    # Pure Python fallback
    if rune < 0 or rune > MaxRune:
        return False
    try:
        char = chr(rune)
        cat = unicodedata.category(char)
        return cat.startswith("S")
    except (ValueError, OverflowError):
        return False


def IsTitle(r: str | int) -> bool:
    """IsTitle reports whether the rune is a title case letter."""
    rune = _get_rune(r)

    if is_library_available():
        try:
            lib = get_lib()
            _configure_fn(lib, "goated_unicode_IsTitle", [ctypes.c_int], ctypes.c_bool)
            return bool(lib.goated_unicode_IsTitle(rune))
        except Exception:
            pass

    # Pure Python fallback
    if rune < 0 or rune > MaxRune:
        return False
    try:
        char = chr(rune)
        cat = unicodedata.category(char)
        return cat == "Lt"
    except (ValueError, OverflowError):
        return False


def IsUpper(r: str | int) -> bool:
    """IsUpper reports whether the rune is an upper case letter."""
    rune = _get_rune(r)

    if is_library_available():
        try:
            lib = get_lib()
            _configure_fn(lib, "goated_unicode_IsUpper", [ctypes.c_int], ctypes.c_bool)
            return bool(lib.goated_unicode_IsUpper(rune))
        except Exception:
            pass

    # Pure Python fallback
    if rune < 0 or rune > MaxRune:
        return False
    try:
        char = chr(rune)
        cat = unicodedata.category(char)
        return cat == "Lu"
    except (ValueError, OverflowError):
        return False


def SimpleFold(r: str | int) -> str:
    """SimpleFold iterates over Unicode code points equivalent under simple case folding."""
    rune = _get_rune(r)

    if is_library_available():
        try:
            lib = get_lib()
            _configure_fn(lib, "goated_unicode_SimpleFold", [ctypes.c_int], ctypes.c_int)
            result = lib.goated_unicode_SimpleFold(rune)
            return _from_rune(result)
        except Exception:
            pass

    # Pure Python fallback
    if rune < 0 or rune > MaxRune:
        return _from_rune(rune)

    try:
        char = chr(rune)
        lower = char.lower()
        upper = char.upper()

        variants = sorted({ord(lower[0]) if lower else rune, ord(upper[0]) if upper else rune})

        for v in variants:
            if v > rune:
                return chr(v)
        return chr(variants[0]) if variants else char
    except (ValueError, OverflowError):
        return _from_rune(rune)


def To(_case: int, r: str | int) -> str:
    """To maps the rune to the specified case: UpperCase, LowerCase, or TitleCase."""
    rune = _get_rune(r)

    if is_library_available():
        try:
            lib = get_lib()
            _configure_fn(lib, "goated_unicode_To", [ctypes.c_longlong, ctypes.c_int], ctypes.c_int)
            result = lib.goated_unicode_To(_case, rune)
            return _from_rune(result)
        except Exception:
            pass

    # Pure Python fallback
    if rune < 0 or rune > MaxRune:
        return _from_rune(rune)

    try:
        char = chr(rune)
        if _case == UpperCase:
            return char.upper()
        elif _case == LowerCase:
            return char.lower()
        elif _case == TitleCase:
            return char.upper()
        return char
    except (ValueError, OverflowError):
        return _from_rune(rune)


def ToLower(r: str | int) -> str:
    """ToLower maps the rune to lower case."""
    rune = _get_rune(r)

    if is_library_available():
        try:
            lib = get_lib()
            _configure_fn(lib, "goated_unicode_ToLower", [ctypes.c_int], ctypes.c_int)
            result = lib.goated_unicode_ToLower(rune)
            return _from_rune(result)
        except Exception:
            pass

    # Pure Python fallback
    try:
        return chr(rune).lower()
    except (ValueError, OverflowError):
        return _from_rune(rune)


def ToTitle(r: str | int) -> str:
    """ToTitle maps the rune to title case."""
    rune = _get_rune(r)

    if is_library_available():
        try:
            lib = get_lib()
            _configure_fn(lib, "goated_unicode_ToTitle", [ctypes.c_int], ctypes.c_int)
            result = lib.goated_unicode_ToTitle(rune)
            return _from_rune(result)
        except Exception:
            pass

    # Pure Python fallback
    try:
        return chr(rune).upper()
    except (ValueError, OverflowError):
        return _from_rune(rune)


def ToUpper(r: str | int) -> str:
    """ToUpper maps the rune to upper case."""
    rune = _get_rune(r)

    if is_library_available():
        try:
            lib = get_lib()
            _configure_fn(lib, "goated_unicode_ToUpper", [ctypes.c_int], ctypes.c_int)
            result = lib.goated_unicode_ToUpper(rune)
            return _from_rune(result)
        except Exception:
            pass

    # Pure Python fallback
    try:
        return chr(rune).upper()
    except (ValueError, OverflowError):
        return _from_rune(rune)
