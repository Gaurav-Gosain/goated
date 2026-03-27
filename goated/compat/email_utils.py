"""Accelerated email address parsing and validation, backed by Go's net/mail.

Uses Go FFI for email parsing and validation. Falls back to Python's
email.utils for other utility functions.

Usage:
    from goated.compat import email_utils
    name, addr = email_utils.parseaddr("John Doe <john@example.com>")
    valid = email_utils.validate_email("user@example.com")
    results = email_utils.batch_parse(["a@b.com", "Name <c@d.com>"])
"""

from __future__ import annotations

import ctypes
import email.utils as _email_utils
from collections.abc import Sequence

# Re-export common email.utils functions
from email.utils import (  # noqa: F401
    decode_rfc2231,
    encode_rfc2231,
    format_datetime,
    formataddr,
    formatdate,
    getaddresses,
    make_msgid,
    mktime_tz,
    parsedate,
    parsedate_to_datetime,
    parsedate_tz,
)

from goated._core import _USE_GO_LIB, get_lib

_lib_setup = False


def _setup_lib() -> None:
    global _lib_setup
    if _lib_setup or not _USE_GO_LIB:
        return
    try:
        lib = get_lib().lib
        lib.goated_email_parse_address.argtypes = [
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.c_char_p),  # nameOut
            ctypes.POINTER(ctypes.c_char_p),  # emailOut
        ]
        lib.goated_email_parse_address.restype = ctypes.c_bool
        lib.goated_email_validate.argtypes = [ctypes.c_char_p]
        lib.goated_email_validate.restype = ctypes.c_bool
        _lib_setup = True
    except Exception:
        pass


def parseaddr(addr: str) -> tuple[str, str]:
    """Parse an email address. Go-accelerated.

    Returns a (name, email) tuple. Falls back to Python on failure.
    """
    if not _USE_GO_LIB:
        return _email_utils.parseaddr(addr)

    # Prefer cffi
    from goated._core import get_cffi_lib

    cffi_lib = get_cffi_lib()
    if cffi_lib is not None:
        try:
            from goated._core import _cffi_ffi

            name_out = _cffi_ffi.new("char**")
            email_out = _cffi_ffi.new("char**")
            ok = cffi_lib.goated_email_parse_address(
                addr.encode("utf-8"), name_out, email_out,
            )
            if ok:
                name = _cffi_ffi.string(name_out[0]).decode("utf-8") if name_out[0] else ""
                email = _cffi_ffi.string(email_out[0]).decode("utf-8") if email_out[0] else ""
                return (name, email)
        except Exception:
            pass

    # Fallback to ctypes
    _setup_lib()
    if _lib_setup:
        try:
            lib = get_lib().lib
            name_out = ctypes.c_char_p()
            email_out = ctypes.c_char_p()
            ok = lib.goated_email_parse_address(
                addr.encode("utf-8"),
                ctypes.byref(name_out),
                ctypes.byref(email_out),
            )
            if ok:
                name = name_out.value.decode("utf-8") if name_out.value else ""
                email = email_out.value.decode("utf-8") if email_out.value else ""
                return (name, email)
        except Exception:
            pass

    return _email_utils.parseaddr(addr)


def validate_email(addr: str) -> bool:
    """Validate an email address format. Go-accelerated.

    This is a goated extension -- uses Go's net/mail.ParseAddress for validation.
    """
    if _USE_GO_LIB:
        from goated._core import get_cffi_lib

        cffi_lib = get_cffi_lib()
        if cffi_lib is not None:
            try:
                return bool(cffi_lib.goated_email_validate(addr.encode("utf-8")))
            except Exception:
                pass

        _setup_lib()
        if _lib_setup:
            try:
                lib = get_lib().lib
                return bool(lib.goated_email_validate(addr.encode("utf-8")))
            except Exception:
                pass

    # Python fallback: basic validation via parseaddr
    _, email = _email_utils.parseaddr(addr)
    return bool(email and "@" in email)


def batch_parse(
    addresses: Sequence[str],
) -> list[tuple[str, str]]:
    """Parse multiple email addresses. Go-accelerated.

    This is a goated extension for bulk email parsing.

    Returns:
        List of (name, email) tuples.

    """
    if _USE_GO_LIB:
        # Use individual Go calls (still faster than Python for large batches)
        from goated._core import get_cffi_lib

        cffi_lib = get_cffi_lib()
        if cffi_lib is not None:
            try:
                from goated._core import _cffi_ffi

                results = []
                for addr in addresses:
                    name_out = _cffi_ffi.new("char**")
                    email_out = _cffi_ffi.new("char**")
                    ok = cffi_lib.goated_email_parse_address(
                        addr.encode("utf-8"), name_out, email_out,
                    )
                    if ok:
                        name = _cffi_ffi.string(name_out[0]).decode("utf-8") if name_out[0] else ""
                        eout = email_out[0]
                        email = _cffi_ffi.string(eout).decode("utf-8") if eout else ""
                        results.append((name, email))
                    else:
                        results.append(("", ""))
                return results
            except Exception:
                pass

        _setup_lib()
        if _lib_setup:
            try:
                lib = get_lib().lib
                results = []
                for addr in addresses:
                    name_out = ctypes.c_char_p()
                    email_out = ctypes.c_char_p()
                    ok = lib.goated_email_parse_address(
                        addr.encode("utf-8"),
                        ctypes.byref(name_out),
                        ctypes.byref(email_out),
                    )
                    if ok:
                        name = name_out.value.decode("utf-8") if name_out.value else ""
                        email = email_out.value.decode("utf-8") if email_out.value else ""
                        results.append((name, email))
                    else:
                        results.append(("", ""))
                return results
            except Exception:
                pass

    # Python fallback
    return [_email_utils.parseaddr(addr) for addr in addresses]


__all__ = [
    "parseaddr",
    "formataddr",
    "validate_email",
    "batch_parse",
    "parsedate",
    "parsedate_tz",
    "parsedate_to_datetime",
    "formatdate",
    "format_datetime",
    "make_msgid",
    "mktime_tz",
    "getaddresses",
    "decode_rfc2231",
    "encode_rfc2231",
]
