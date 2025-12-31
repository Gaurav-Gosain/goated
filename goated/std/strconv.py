"""Go strconv package bindings - string conversions."""

from __future__ import annotations

from goated.result import Err, GoError, Ok, Result

__all__ = [
    "Atoi",
    "Itoa",
    "ParseInt",
    "ParseUint",
    "ParseFloat",
    "ParseBool",
    "FormatInt",
    "FormatUint",
    "FormatFloat",
    "FormatBool",
    "Quote",
    "QuoteToASCII",
    "QuoteRune",
    "QuoteRuneToASCII",
    "Unquote",
    "UnquoteChar",
    "AppendInt",
    "AppendUint",
    "AppendFloat",
    "AppendBool",
    "AppendQuote",
    "CanBackquote",
    "IsPrint",
    "IsGraphic",
    "IntSize",
]

IntSize = 64


def Atoi(s: str) -> Result[int, GoError]:
    """Converts string to int."""
    try:
        return Ok(int(s))
    except ValueError as e:
        return Err(GoError(str(e), "strconv.NumError"))


def Itoa(i: int) -> str:
    """Converts int to string."""
    return str(i)


def ParseInt(s: str, base: int = 10, bit_size: int = 64) -> Result[int, GoError]:
    """Interprets string s in the given base and returns the corresponding int."""
    try:
        return Ok(int(s, base))
    except ValueError as e:
        return Err(GoError(str(e), "strconv.NumError"))


def ParseUint(s: str, base: int = 10, bit_size: int = 64) -> Result[int, GoError]:
    """Like ParseInt but for unsigned integers."""
    try:
        value = int(s, base)
        if value < 0:
            return Err(GoError("invalid syntax", "strconv.NumError"))
        return Ok(value)
    except ValueError as e:
        return Err(GoError(str(e), "strconv.NumError"))


def ParseFloat(s: str, bit_size: int = 64) -> Result[float, GoError]:
    """Converts the string s to a floating-point number."""
    try:
        return Ok(float(s))
    except ValueError as e:
        return Err(GoError(str(e), "strconv.NumError"))


def ParseBool(s: str) -> Result[bool, GoError]:
    """Returns the boolean value represented by the string."""
    s_lower = s.lower()
    if s_lower in ("1", "t", "true"):
        return Ok(True)
    elif s_lower in ("0", "f", "false"):
        return Ok(False)
    return Err(GoError(f"strconv.ParseBool: parsing {s!r}: invalid syntax", "strconv.NumError"))


def FormatInt(i: int, base: int) -> str:
    """Returns the string representation of i in the given base (2-36)."""
    if base == 10:
        return str(i)
    elif base == 16:
        return format(i, "x") if i >= 0 else "-" + format(-i, "x")
    elif base == 8:
        return format(i, "o") if i >= 0 else "-" + format(-i, "o")
    elif base == 2:
        return format(i, "b") if i >= 0 else "-" + format(-i, "b")
    else:
        if base < 2 or base > 36:
            raise ValueError(f"base must be 2-36, got {base}")
        digits = "0123456789abcdefghijklmnopqrstuvwxyz"
        if i == 0:
            return "0"
        negative = i < 0
        i = abs(i)
        result = []
        while i:
            result.append(digits[i % base])
            i //= base
        if negative:
            result.append("-")
        return "".join(reversed(result))


def FormatUint(i: int, base: int) -> str:
    """Returns the string representation of unsigned i in the given base."""
    if i < 0:
        raise ValueError("FormatUint requires non-negative integer")
    return FormatInt(i, base)


def FormatFloat(f: float, fmt: str = "g", prec: int = -1, bit_size: int = 64) -> str:
    """Converts the floating-point number f to a string."""
    if fmt == "g" or fmt == "G":
        if prec < 0:
            return str(f)
        return f"{f:.{prec}g}"
    elif fmt == "f" or fmt == "F":
        if prec < 0:
            prec = 6
        return f"{f:.{prec}f}"
    elif fmt == "e" or fmt == "E":
        if prec < 0:
            prec = 6
        return f"{f:.{prec}e}"
    return str(f)


def FormatBool(b: bool) -> str:
    """Returns 'true' or 'false' according to the value of b."""
    return "true" if b else "false"


def Quote(s: str) -> str:
    """Returns a double-quoted Go string literal representing s."""
    result = ['"']
    for c in s:
        if c == '"':
            result.append('\\"')
        elif c == "\\":
            result.append("\\\\")
        elif c == "\n":
            result.append("\\n")
        elif c == "\r":
            result.append("\\r")
        elif c == "\t":
            result.append("\\t")
        elif ord(c) < 32 or ord(c) >= 127:
            if ord(c) < 256:
                result.append(f"\\x{ord(c):02x}")
            else:
                result.append(f"\\u{ord(c):04x}")
        else:
            result.append(c)
    result.append('"')
    return "".join(result)


def QuoteToASCII(s: str) -> str:
    """Returns a double-quoted Go string literal, with non-ASCII escaped."""
    result = ['"']
    for c in s:
        if c == '"':
            result.append('\\"')
        elif c == "\\":
            result.append("\\\\")
        elif c == "\n":
            result.append("\\n")
        elif c == "\r":
            result.append("\\r")
        elif c == "\t":
            result.append("\\t")
        elif ord(c) < 32 or ord(c) >= 127:
            if ord(c) < 0x10000:
                result.append(f"\\u{ord(c):04x}")
            else:
                result.append(f"\\U{ord(c):08x}")
        else:
            result.append(c)
    result.append('"')
    return "".join(result)


def QuoteRune(r: str | int) -> str:
    """Returns a single-quoted Go character literal representing the rune."""
    if isinstance(r, int):
        try:
            r = chr(r)
        except (ValueError, OverflowError):
            return "'\ufffd'"
    if len(r) == 0:
        return "''"
    c = r[0]
    if c == "'":
        return "'\\''"
    elif c == "\\":
        return "'\\\\'"
    elif c == "\n":
        return "'\\n'"
    elif c == "\r":
        return "'\\r'"
    elif c == "\t":
        return "'\\t'"
    elif ord(c) < 32 or (ord(c) >= 127 and ord(c) < 256):
        return f"'\\x{ord(c):02x}'"
    elif ord(c) >= 256:
        if ord(c) < 0x10000:
            return f"'\\u{ord(c):04x}'"
        return f"'\\U{ord(c):08x}'"
    return f"'{c}'"


def QuoteRuneToASCII(r: str | int) -> str:
    """Returns a single-quoted Go character literal, with non-ASCII escaped."""
    if isinstance(r, int):
        try:
            r = chr(r)
        except (ValueError, OverflowError):
            return "'\\ufffd'"
    if len(r) == 0:
        return "''"
    c = r[0]
    if c == "'":
        return "'\\''"
    elif c == "\\":
        return "'\\\\'"
    elif c == "\n":
        return "'\\n'"
    elif c == "\r":
        return "'\\r'"
    elif c == "\t":
        return "'\\t'"
    elif ord(c) < 32 or ord(c) >= 127:
        if ord(c) < 0x10000:
            return f"'\\u{ord(c):04x}'"
        return f"'\\U{ord(c):08x}'"
    return f"'{c}'"


def Unquote(s: str) -> Result[str, GoError]:
    """Interprets s as a quoted Go string literal and returns the unquoted value."""
    if len(s) < 2:
        return Err(GoError("invalid syntax", "strconv.ErrSyntax"))
    if s[0] == s[-1] and s[0] in ('"', "'", "`"):
        inner = s[1:-1]
        if s[0] == "`":
            return Ok(inner)
        try:
            return Ok(inner.encode("utf-8").decode("unicode_escape"))
        except Exception:
            return Ok(inner)
    return Err(GoError("invalid syntax", "strconv.ErrSyntax"))


def UnquoteChar(s: str, quote: str) -> Result[tuple[str, bool, str], GoError]:
    """Decodes the first character or byte in s. Returns (value, multibyte, tail)."""
    if not s:
        return Err(GoError("empty string", "strconv.ErrSyntax"))
    c = s[0]
    if c == quote:
        return Err(GoError("invalid syntax", "strconv.ErrSyntax"))
    if c != "\\":
        return Ok((c, ord(c) >= 128, s[1:]))
    if len(s) < 2:
        return Err(GoError("invalid syntax", "strconv.ErrSyntax"))
    c = s[1]
    escape_map = {
        "a": "\a",
        "b": "\b",
        "f": "\f",
        "n": "\n",
        "r": "\r",
        "t": "\t",
        "v": "\v",
        "\\": "\\",
        "'": "'",
        '"': '"',
    }
    if c in escape_map:
        return Ok((escape_map[c], False, s[2:]))
    elif c == "x":
        if len(s) < 4:
            return Err(GoError("invalid syntax", "strconv.ErrSyntax"))
        try:
            val = int(s[2:4], 16)
            return Ok((chr(val), False, s[4:]))
        except ValueError:
            return Err(GoError("invalid syntax", "strconv.ErrSyntax"))
    elif c == "u":
        if len(s) < 6:
            return Err(GoError("invalid syntax", "strconv.ErrSyntax"))
        try:
            val = int(s[2:6], 16)
            return Ok((chr(val), val >= 128, s[6:]))
        except ValueError:
            return Err(GoError("invalid syntax", "strconv.ErrSyntax"))
    elif c == "U":
        if len(s) < 10:
            return Err(GoError("invalid syntax", "strconv.ErrSyntax"))
        try:
            val = int(s[2:10], 16)
            return Ok((chr(val), val >= 128, s[10:]))
        except ValueError:
            return Err(GoError("invalid syntax", "strconv.ErrSyntax"))
    elif c.isdigit():
        if len(s) < 4:
            return Err(GoError("invalid syntax", "strconv.ErrSyntax"))
        try:
            val = int(s[1:4], 8)
            return Ok((chr(val), False, s[4:]))
        except ValueError:
            return Err(GoError("invalid syntax", "strconv.ErrSyntax"))
    return Err(GoError("invalid syntax", "strconv.ErrSyntax"))


def AppendInt(dst: bytes, i: int, base: int) -> bytes:
    """Appends the string form of the integer i to dst."""
    return dst + FormatInt(i, base).encode("utf-8")


def AppendUint(dst: bytes, i: int, base: int) -> bytes:
    """Appends the string form of the unsigned integer i to dst."""
    return dst + FormatUint(i, base).encode("utf-8")


def AppendFloat(dst: bytes, f: float, fmt: str, prec: int, bit_size: int) -> bytes:
    """Appends the string form of the floating-point number f to dst."""
    return dst + FormatFloat(f, fmt, prec, bit_size).encode("utf-8")


def AppendBool(dst: bytes, b: bool) -> bytes:
    """Appends 'true' or 'false' to dst."""
    return dst + (b"true" if b else b"false")


def AppendQuote(dst: bytes, s: str) -> bytes:
    """Appends a double-quoted Go string literal to dst."""
    return dst + Quote(s).encode("utf-8")


def CanBackquote(s: str) -> bool:
    """Reports whether s can be represented as a single-line backquoted string."""
    return all(not (c == "`" or ord(c) < 32 and c != "\t" or c == "\ufeff") for c in s)


def IsPrint(r: str | int) -> bool:
    """Reports whether the rune is printable."""
    if isinstance(r, str):
        if not r:
            return False
        r = ord(r[0])
    return not (r < 32 or (127 <= r < 160))


def IsGraphic(r: str | int) -> bool:
    """Reports whether the rune is a graphic character."""
    if isinstance(r, str):
        if not r:
            return False
        r = ord(r[0])
    import unicodedata

    try:
        cat = unicodedata.category(chr(r))
        return cat[0] in ("L", "M", "N", "P", "S") or cat == "Zs"
    except (ValueError, OverflowError):
        return False
