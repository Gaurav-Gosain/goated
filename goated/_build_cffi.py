"""Build cffi API-mode extension for goated.

This generates a compiled C extension module (_goated_cffi) that calls
the Go shared library directly via C function calls, bypassing libffi.
This reduces per-call overhead from ~300ns (ctypes) to ~70ns.

Usage:
    python goated/_build_cffi.py

The extension is optional - goated falls back to ctypes if unavailable.
"""

from __future__ import annotations

import os
import sys

import cffi


def extract_declarations(header_path: str) -> str:
    """Extract C function declarations from the Go-generated header."""
    with open(header_path) as f:
        content = f.read()

    # Find all extern declarations (but not the C++ wrapper or Go internal ones)
    lines = []
    for line in content.splitlines():
        if line.startswith("extern") and "goated_" in line:
            # Clean up the declaration for cffi
            decl = line.rstrip(";").strip() + ";"
            # Remove 'extern' prefix
            decl = decl.replace("extern ", "")
            # cffi doesn't understand _Bool, use bool
            decl = decl.replace("_Bool", "bool")
            lines.append(decl)

    return "\n".join(lines)


def build():
    # Find the header
    base_dir = os.path.dirname(os.path.abspath(__file__))
    header_path = os.path.join(base_dir, "libgoated.h")

    if not os.path.exists(header_path):
        print(f"Header not found at {header_path}", file=sys.stderr)
        sys.exit(1)

    # Find the shared library
    if sys.platform == "darwin":
        lib_name = "libgoated.dylib"
    elif sys.platform == "win32":
        lib_name = "libgoated.dll"
    else:
        lib_name = "libgoated.so"

    lib_path = os.path.join(base_dir, lib_name)
    if not os.path.exists(lib_path):
        print(f"Shared library not found at {lib_path}", file=sys.stderr)
        sys.exit(1)

    # Extract declarations
    declarations = extract_declarations(header_path)
    print(f"Extracted {declarations.count(';')} function declarations")

    # Build the cffi extension
    ffibuilder = cffi.FFI()
    ffibuilder.cdef(declarations)

    ffibuilder.set_source(
        "_goated_cffi",
        f'#include "{header_path}"',
        libraries=[],
        extra_link_args=[lib_path, f"-Wl,-rpath,{base_dir}"],
    )

    ffibuilder.compile(tmpdir=base_dir, verbose=True)
    print("cffi API-mode extension built successfully!")


if __name__ == "__main__":
    build()
