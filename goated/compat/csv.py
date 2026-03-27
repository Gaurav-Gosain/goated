"""Drop-in replacement for Python's csv module, backed by Go's encoding/csv.

Uses Go FFI for reading/parsing complete CSV strings.
Falls back to Python for streaming and custom dialects.

Usage:
    from goated.compat import csv
    reader = csv.reader(open("data.csv"))
    for row in reader:
        print(row)
"""

from __future__ import annotations

import csv as _csv
import ctypes

# Re-export everything from Python's csv
from csv import (  # noqa: F401
    QUOTE_ALL,
    QUOTE_MINIMAL,
    QUOTE_NONE,
    QUOTE_NONNUMERIC,
    Dialect,
    DictReader,
    DictWriter,
    Error,
    Sniffer,
    excel,
    excel_tab,
    field_size_limit,
    get_dialect,
    list_dialects,
    reader,
    register_dialect,
    unix_dialect,
    unregister_dialect,
    writer,
)

from goated._core import _USE_GO_LIB, get_lib

_lib_setup = False


def _setup_lib() -> None:
    global _lib_setup
    if _lib_setup or not _USE_GO_LIB:
        return
    try:
        lib = get_lib().lib
        lib.goated_csv_read_all.argtypes = [
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_char_p),
        ]
        lib.goated_csv_read_all.restype = ctypes.c_uint64
        lib.goated_csv_records_len.argtypes = [ctypes.c_uint64]
        lib.goated_csv_records_len.restype = ctypes.c_int
        lib.goated_csv_record_len.argtypes = [ctypes.c_uint64, ctypes.c_int]
        lib.goated_csv_record_len.restype = ctypes.c_int
        lib.goated_csv_get_field.argtypes = [ctypes.c_uint64, ctypes.c_int, ctypes.c_int]
        lib.goated_csv_get_field.restype = ctypes.c_char_p
        lib.goated_handle_delete.argtypes = [ctypes.c_uint64]
        lib.goated_handle_delete.restype = None
        _lib_setup = True
    except Exception:
        pass


def read_all(data: str) -> list[list[str]]:
    """Parse entire CSV string at once. Go-accelerated.

    This is a goated extension for bulk CSV parsing.
    """
    if _USE_GO_LIB:
        _setup_lib()
        if _lib_setup:
            try:
                lib = get_lib().lib
                encoded = data.encode("utf-8")
                err_out = ctypes.c_char_p()
                handle = lib.goated_csv_read_all(encoded, len(encoded), ctypes.byref(err_out))
                if handle and not err_out.value:
                    try:
                        nrows = lib.goated_csv_records_len(handle)
                        result = []
                        for i in range(nrows):
                            ncols = lib.goated_csv_record_len(handle, i)
                            row = []
                            for j in range(ncols):
                                field = lib.goated_csv_get_field(handle, i, j)
                                row.append(field.decode("utf-8") if field else "")
                            result.append(row)
                        return result
                    finally:
                        lib.goated_handle_delete(handle)
            except Exception:
                pass
    # Fallback
    import io

    rdr = _csv.reader(io.StringIO(data))
    return list(rdr)


__all__ = [
    "reader",
    "writer",
    "DictReader",
    "DictWriter",
    "Dialect",
    "Error",
    "Sniffer",
    "excel",
    "excel_tab",
    "unix_dialect",
    "field_size_limit",
    "get_dialect",
    "list_dialects",
    "register_dialect",
    "unregister_dialect",
    "read_all",
    "QUOTE_ALL",
    "QUOTE_MINIMAL",
    "QUOTE_NONE",
    "QUOTE_NONNUMERIC",
]
