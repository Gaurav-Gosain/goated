"""Go-powered HTTP server for Python.

Go's net/http server handles 100K+ req/s - orders of magnitude faster than
Python's http.server. This module provides a simple Pythonic API to start
a Go HTTP server from Python.

Usage:
    from goated.server import GoServer

    # Simple static server
    with GoServer(":8080") as app:
        app.json("/api/health", '{"status": "ok"}')
        app.static("/hello", "Hello, World!")
        input("Server running, press Enter to stop...")

    # File server
    from goated.server import FileServer
    with FileServer(":8080", "./static") as srv:
        input("Serving files...")

    # Benchmark server (maximum throughput)
    from goated.server import BenchServer
    with BenchServer(":8080", '{"ok": true}') as srv:
        print(f"Benchmark server at {srv.addr}")

    # Standalone functions
    from goated.server import bench_server, stop_server
    sid = bench_server(":9090", '{"bench": true}')
    stop_server(sid)
"""

from __future__ import annotations

import contextlib
import ctypes
from typing import Any

from goated._core import _USE_GO_LIB, get_cffi_lib, get_lib

_lib_setup = False
_use_cffi = False


class GoServerError(Exception):
    """Raised when a Go HTTP server operation fails."""

    pass


def _setup() -> None:
    global _lib_setup, _use_cffi
    if _lib_setup:
        return

    cffi_lib = get_cffi_lib()
    if cffi_lib is not None:
        _use_cffi = True
        _lib_setup = True
        return

    if not _USE_GO_LIB:
        return
    try:
        lib = get_lib().lib
        lib.goated_http_server_new.argtypes = [ctypes.c_char_p]
        lib.goated_http_server_new.restype = ctypes.c_uint64
        lib.goated_http_server_route.argtypes = [
            ctypes.c_uint64,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
        ]
        lib.goated_http_server_route.restype = None
        lib.goated_http_server_start.argtypes = [
            ctypes.c_uint64,
            ctypes.POINTER(ctypes.c_char_p),
        ]
        lib.goated_http_server_start.restype = None
        lib.goated_http_server_stop.argtypes = [ctypes.c_uint64]
        lib.goated_http_server_stop.restype = None
        lib.goated_http_server_addr.argtypes = [ctypes.c_uint64]
        lib.goated_http_server_addr.restype = ctypes.c_char_p
        lib.goated_http_bench_server.argtypes = [
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.c_char_p),
        ]
        lib.goated_http_bench_server.restype = ctypes.c_uint64
        lib.goated_http_fileserver_new.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        lib.goated_http_fileserver_new.restype = ctypes.c_uint64
        _lib_setup = True
    except Exception:
        pass


def _get_lib() -> Any:
    _setup()
    if _use_cffi:
        return get_cffi_lib()
    return get_lib().lib if _lib_setup else None


class GoServer:
    """A Go-powered HTTP server.

    Handles 100K+ requests/second - orders of magnitude faster than
    Python's http.server or even WSGI servers.

    Args:
        addr: Address to listen on (e.g. ":8080", "127.0.0.1:3000").

    Example:
        with GoServer(":8080") as app:
            app.json("/api/health", '{"status": "ok"}')
            app.static("/hello", "Hello, World!")
            input("Press Enter to stop...")

    """

    def __init__(self, addr: str = ":8080") -> None:
        _setup()
        lib = _get_lib()
        if lib is None:
            raise GoServerError("Go library not available. Run 'make build' to compile.")

        addr_b = addr.encode("utf-8") if isinstance(addr, str) else addr
        self._id = lib.goated_http_server_new(addr_b)
        if not self._id:
            raise GoServerError("Failed to create Go HTTP server.")
        self._addr = addr
        self._started = False
        self._routes: list[tuple[str, str, str]] = []

    def route(self, path: str, body: str, content_type: str = "text/plain") -> GoServer:
        """Add a route that returns a static response.

        Args:
            path: URL path (e.g. "/api/health").
            body: Response body string.
            content_type: Content-Type header value.

        Returns:
            Self for chaining.

        """
        lib = _get_lib()
        lib.goated_http_server_route(
            self._id,
            path.encode("utf-8"),
            body.encode("utf-8"),
            content_type.encode("utf-8"),
        )
        self._routes.append((path, body, content_type))
        return self

    def json(self, path: str, body: str) -> GoServer:
        """Add a JSON route (convenience method)."""
        return self.route(path, body, "application/json")

    def static(self, path: str, body: str) -> GoServer:
        """Add a plain text route (convenience method)."""
        return self.route(path, body, "text/plain")

    def start(self) -> GoServer:
        """Start the server (non-blocking).

        The Go HTTP server runs in a separate goroutine.

        Returns:
            Self for chaining.

        Raises:
            GoServerError: If the server fails to start.

        """
        if self._started:
            return self

        lib = _get_lib()
        if _use_cffi:
            from goated._core import _cffi_ffi

            err = _cffi_ffi.new("char**")
            lib.goated_http_server_start(self._id, err)
            if err[0]:
                raise GoServerError(f"Failed to start server: {_cffi_ffi.string(err[0]).decode()}")
        else:
            err = ctypes.c_char_p()
            lib.goated_http_server_start(self._id, ctypes.byref(err))
            if err.value:
                raise GoServerError(f"Failed to start server: {err.value.decode()}")
        self._started = True
        return self

    def stop(self) -> None:
        """Stop the server gracefully.

        Waits up to 5 seconds for in-flight requests to complete.
        """
        if self._started:
            try:
                lib = _get_lib()
                lib.goated_http_server_stop(self._id)
            except Exception:
                pass
            finally:
                self._started = False

    @property
    def addr(self) -> str:
        """Get the server's listen address."""
        if _lib_setup:
            try:
                lib = _get_lib()
                if _use_cffi:
                    from goated._core import _cffi_ffi

                    result = lib.goated_http_server_addr(self._id)
                    if result:
                        return _cffi_ffi.string(result).decode("utf-8")
                else:
                    result = lib.goated_http_server_addr(self._id)
                    if result:
                        return result.decode("utf-8")
            except Exception:
                pass
        return self._addr

    @property
    def running(self) -> bool:
        """Check if the server is currently running."""
        return self._started

    @property
    def routes(self) -> list[tuple[str, str, str]]:
        """Get registered routes as (path, body, content_type) tuples."""
        return list(self._routes)

    def __enter__(self) -> GoServer:
        self.start()
        return self

    def __exit__(self, *args: object) -> None:
        self.stop()

    def __del__(self) -> None:
        with contextlib.suppress(Exception):
            self.stop()

    def __repr__(self) -> str:
        status = "running" if self._started else "stopped"
        return f"GoServer(addr={self._addr!r}, status={status}, routes={len(self._routes)})"


class FileServer:
    """A Go-powered static file server.

    Serves files from a directory with Go's high-performance HTTP stack.

    Args:
        addr: Address to listen on.
        directory: Path to the directory to serve.

    Example:
        with FileServer(":8080", "./static") as srv:
            print(f"Serving files at {srv.addr}")

    """

    def __init__(self, addr: str, directory: str) -> None:
        _setup()
        lib = _get_lib()
        if lib is None:
            raise GoServerError("Go library not available. Run 'make build' to compile.")
        self._id = lib.goated_http_fileserver_new(
            addr.encode("utf-8"),
            directory.encode("utf-8"),
        )
        if not self._id:
            raise GoServerError("Failed to create Go file server.")
        self._addr = addr
        self._directory = directory
        self._started = False

    def start(self) -> FileServer:
        """Start the file server in the background."""
        if self._started:
            return self

        lib = _get_lib()
        if _use_cffi:
            from goated._core import _cffi_ffi

            err = _cffi_ffi.new("char**")
            lib.goated_http_server_start(self._id, err)
            if err[0]:
                raise GoServerError(
                    f"Failed to start file server: {_cffi_ffi.string(err[0]).decode()}"
                )
        else:
            err = ctypes.c_char_p()
            lib.goated_http_server_start(self._id, ctypes.byref(err))
            if err.value:
                raise GoServerError(f"Failed to start file server: {err.value.decode()}")
        self._started = True
        return self

    def stop(self) -> None:
        """Stop the file server gracefully."""
        if self._started:
            try:
                lib = _get_lib()
                lib.goated_http_server_stop(self._id)
            except Exception:
                pass
            finally:
                self._started = False

    @property
    def addr(self) -> str:
        """Get the server's listen address."""
        return self._addr

    @property
    def directory(self) -> str:
        """Get the directory being served."""
        return self._directory

    @property
    def running(self) -> bool:
        """Check if the server is currently running."""
        return self._started

    def __enter__(self) -> FileServer:
        self.start()
        return self

    def __exit__(self, *args: object) -> None:
        self.stop()

    def __del__(self) -> None:
        with contextlib.suppress(Exception):
            self.stop()

    def __repr__(self) -> str:
        status = "running" if self._started else "stopped"
        return f"FileServer(addr={self._addr!r}, dir={self._directory!r}, status={status})"


# Alias for compatibility with spec naming
GoFileServer = FileServer


class BenchServer:
    """Ultra-fast benchmark server that returns a fixed JSON response.

    Optimized for maximum throughput benchmarking.

    Example:
        with BenchServer(":8080", '{"ok": true}') as srv:
            # Use wrk or ab to benchmark: wrk -t4 -c100 http://localhost:8080/
            input("Benchmarking...")

    """

    def __init__(self, addr: str, json_response: str) -> None:
        _setup()
        lib = _get_lib()
        if lib is None:
            raise GoServerError("Go library not available. Run 'make build' to compile.")

        if _use_cffi:
            from goated._core import _cffi_ffi

            err = _cffi_ffi.new("char**")
            self._id = lib.goated_http_bench_server(
                addr.encode("utf-8"),
                json_response.encode("utf-8"),
                err,
            )
            if err[0]:
                raise GoServerError(
                    f"Failed to start bench server: {_cffi_ffi.string(err[0]).decode()}"
                )
        else:
            err = ctypes.c_char_p()
            self._id = lib.goated_http_bench_server(
                addr.encode("utf-8"),
                json_response.encode("utf-8"),
                ctypes.byref(err),
            )
            if err.value:
                raise GoServerError(f"Failed to start bench server: {err.value.decode()}")
        self._addr = addr
        self._started = True

    def stop(self) -> None:
        """Stop the benchmark server."""
        if self._started:
            try:
                lib = _get_lib()
                lib.goated_http_server_stop(self._id)
            except Exception:
                pass
            finally:
                self._started = False

    @property
    def addr(self) -> str:
        """Get the server's listen address."""
        return self._addr

    @property
    def running(self) -> bool:
        """Check if the server is currently running."""
        return self._started

    def __enter__(self) -> BenchServer:
        return self

    def __exit__(self, *args: object) -> None:
        self.stop()

    def __del__(self) -> None:
        with contextlib.suppress(Exception):
            self.stop()

    def __repr__(self) -> str:
        status = "running" if self._started else "stopped"
        return f"BenchServer(addr={self._addr!r}, status={status})"


def bench_server(addr: str, json_response: str) -> int:
    """Create and start a benchmark server that responds with static JSON.

    This is a standalone function alternative to BenchServer class.

    Args:
        addr: Address to listen on.
        json_response: JSON string to respond with on every request.

    Returns:
        Server ID that can be used with stop_server().

    Raises:
        GoServerError: If the server fails to start.

    """
    _setup()
    lib = _get_lib()
    if lib is None:
        raise GoServerError("Go library not available. Run 'make build' to compile.")

    if _use_cffi:
        from goated._core import _cffi_ffi

        err = _cffi_ffi.new("char**")
        server_id = lib.goated_http_bench_server(
            addr.encode("utf-8"),
            json_response.encode("utf-8"),
            err,
        )
        if err[0]:
            raise GoServerError(
                f"Failed to start bench server: {_cffi_ffi.string(err[0]).decode()}"
            )
    else:
        err = ctypes.c_char_p()
        server_id = lib.goated_http_bench_server(
            addr.encode("utf-8"),
            json_response.encode("utf-8"),
            ctypes.byref(err),
        )
        if err.value:
            raise GoServerError(f"Failed to start bench server: {err.value.decode()}")

    return int(server_id)


def stop_server(server_id: int) -> None:
    """Stop a server by its ID (returned by bench_server).

    Args:
        server_id: The server ID to stop.

    """
    lib = _get_lib()
    if lib is not None:
        with contextlib.suppress(Exception):
            lib.goated_http_server_stop(server_id)


__all__ = [
    "GoServer",
    "GoServerError",
    "GoFileServer",
    "FileServer",
    "BenchServer",
    "bench_server",
    "stop_server",
]
