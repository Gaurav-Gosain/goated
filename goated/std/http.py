from __future__ import annotations

import contextlib
import http.client as _http_client
import http.server as _http_server
import ssl
import urllib.parse
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass, field
from io import BytesIO
from typing import IO, Any

from goated.result import Err, GoError, Ok, Result

__all__ = [
    "Get",
    "Post",
    "PostForm",
    "Head",
    "NewRequest",
    "DefaultClient",
    "Client",
    "Request",
    "Response",
    "Header",
    "Cookie",
    "Server",
    "ListenAndServe",
    "HandleFunc",
    "Handle",
    "Handler",
    "HandlerFunc",
    "ServeMux",
    "FileServer",
    "NotFound",
    "Redirect",
    "Error",
    "StatusOK",
    "StatusCreated",
    "StatusAccepted",
    "StatusNoContent",
    "StatusMovedPermanently",
    "StatusFound",
    "StatusNotModified",
    "StatusBadRequest",
    "StatusUnauthorized",
    "StatusForbidden",
    "StatusNotFound",
    "StatusMethodNotAllowed",
    "StatusInternalServerError",
    "StatusBadGateway",
    "StatusServiceUnavailable",
    "MethodGet",
    "MethodPost",
    "MethodPut",
    "MethodDelete",
    "MethodHead",
    "MethodOptions",
    "MethodPatch",
]

StatusOK = 200
StatusCreated = 201
StatusAccepted = 202
StatusNoContent = 204
StatusMovedPermanently = 301
StatusFound = 302
StatusNotModified = 304
StatusBadRequest = 400
StatusUnauthorized = 401
StatusForbidden = 403
StatusNotFound = 404
StatusMethodNotAllowed = 405
StatusInternalServerError = 500
StatusBadGateway = 502
StatusServiceUnavailable = 503

MethodGet = "GET"
MethodPost = "POST"
MethodPut = "PUT"
MethodDelete = "DELETE"
MethodHead = "HEAD"
MethodOptions = "OPTIONS"
MethodPatch = "PATCH"


class Header(dict[str, Any]):
    """HTTP header map."""

    def Add(self, key: str, value: str) -> None:
        """Add adds the key, value pair to the header."""
        key = key.title()
        if key in self:
            if isinstance(self[key], list):
                self[key].append(value)
            else:
                self[key] = [self[key], value]
        else:
            self[key] = value

    def Set(self, key: str, value: str) -> None:
        """Set sets the header entry associated with key to value."""
        self[key.title()] = value

    def Get(self, key: str) -> str:
        """Get gets the first value associated with the given key."""
        val = self.get(key.title(), "")
        if isinstance(val, list):
            return str(val[0]) if val else ""
        return str(val)

    def Del(self, key: str) -> None:
        """Del deletes the values associated with key."""
        self.pop(key.title(), None)

    def Clone(self) -> Header:
        """Clone returns a copy of the header."""
        h = Header()
        h.update(self)
        return h


@dataclass
class Cookie:
    """HTTP cookie."""

    Name: str = ""
    Value: str = ""
    Path: str = ""
    Domain: str = ""
    Expires: float | None = None
    MaxAge: int = 0
    Secure: bool = False
    HttpOnly: bool = False
    SameSite: str = ""

    def String(self) -> str:
        """String returns the serialization of the cookie."""
        parts = [f"{self.Name}={self.Value}"]
        if self.Path:
            parts.append(f"Path={self.Path}")
        if self.Domain:
            parts.append(f"Domain={self.Domain}")
        if self.MaxAge > 0:
            parts.append(f"Max-Age={self.MaxAge}")
        if self.Secure:
            parts.append("Secure")
        if self.HttpOnly:
            parts.append("HttpOnly")
        if self.SameSite:
            parts.append(f"SameSite={self.SameSite}")
        return "; ".join(parts)


@dataclass
class Request:
    """HTTP request."""

    Method: str = "GET"
    URL: str = ""
    Header: Header = field(default_factory=Header)
    Body: bytes | None = None
    ContentLength: int = 0
    Host: str = ""
    Form: dict[str, list[str]] = field(default_factory=dict)
    PostForm: dict[str, list[str]] = field(default_factory=dict)

    def AddCookie(self, c: Cookie) -> None:
        """AddCookie adds a cookie to the request."""
        existing = self.Header.Get("Cookie")
        if existing:
            self.Header.Set("Cookie", f"{existing}; {c.Name}={c.Value}")
        else:
            self.Header.Set("Cookie", f"{c.Name}={c.Value}")

    def Cookie(self, name: str) -> Result[Cookie, GoError]:
        """Cookie returns the named cookie."""
        cookie_header = self.Header.Get("Cookie")
        if not cookie_header:
            return Err(GoError("http: named cookie not present", "http.ErrNoCookie"))

        for part in cookie_header.split(";"):
            part = part.strip()
            if "=" in part:
                n, v = part.split("=", 1)
                if n.strip() == name:
                    return Ok(Cookie(Name=n.strip(), Value=v.strip()))

        return Err(GoError("http: named cookie not present", "http.ErrNoCookie"))

    def FormValue(self, key: str) -> str:
        """FormValue returns the first value for the named component of the query."""
        if key in self.Form:
            vals = self.Form[key]
            return vals[0] if vals else ""
        return ""

    def PostFormValue(self, key: str) -> str:
        """PostFormValue returns the first value for the named component of the POST form."""
        if key in self.PostForm:
            vals = self.PostForm[key]
            return vals[0] if vals else ""
        return ""


@dataclass
class Response:
    """HTTP response."""

    Status: str = ""
    StatusCode: int = 0
    Header: Header = field(default_factory=Header)
    Body: IO[bytes] | None = None
    ContentLength: int = -1
    Request: Request | None = None

    def Read(self) -> Result[bytes, GoError]:
        """Read reads the response body."""
        if self.Body is None:
            return Ok(b"")
        try:
            return Ok(self.Body.read())
        except Exception as e:
            return Err(GoError(str(e), "http.Error"))

    def Close(self) -> Result[None, GoError]:
        """Close closes the response body."""
        if self.Body is not None:
            with contextlib.suppress(Exception):
                self.Body.close()
        return Ok(None)


class Client:
    """HTTP client."""

    def __init__(self, timeout: float = 30.0):
        self.Timeout = timeout
        self.Transport = None
        self.CheckRedirect = None
        self.Jar = None

    def Do(self, req: Request) -> Result[Response, GoError]:
        """Do sends an HTTP request and returns an HTTP response."""
        try:
            parsed = urllib.parse.urlparse(req.URL)

            conn: _http_client.HTTPConnection | _http_client.HTTPSConnection
            if parsed.scheme == "https":
                context = ssl.create_default_context()
                conn = _http_client.HTTPSConnection(
                    parsed.netloc, timeout=self.Timeout, context=context
                )
            else:
                conn = _http_client.HTTPConnection(parsed.netloc, timeout=self.Timeout)

            path = parsed.path or "/"
            if parsed.query:
                path = f"{path}?{parsed.query}"

            headers = dict(req.Header)

            conn.request(req.Method, path, body=req.Body, headers=headers)
            resp = conn.getresponse()

            response = Response(
                Status=f"{resp.status} {resp.reason}",
                StatusCode=resp.status,
                Header=Header(resp.getheaders()),
                Body=BytesIO(resp.read()),
                ContentLength=int(resp.getheader("Content-Length", -1)),
                Request=req,
            )

            conn.close()
            return Ok(response)
        except TimeoutError:
            return Err(GoError("request timeout", "http.ErrTimeout"))
        except Exception as e:
            return Err(GoError(str(e), "http.Error"))

    def Get(self, url: str) -> Result[Response, GoError]:
        """Get issues a GET to the specified URL."""
        req = Request(Method="GET", URL=url)
        return self.Do(req)

    def Post(self, url: str, contentType: str, body: bytes) -> Result[Response, GoError]:
        """Post issues a POST to the specified URL."""
        req = Request(
            Method="POST",
            URL=url,
            Body=body,
            Header=Header({"Content-Type": contentType}),
        )
        return self.Do(req)

    def PostForm(self, url: str, data: dict[str, list[str]]) -> Result[Response, GoError]:
        """PostForm issues a POST with form data."""
        encoded = urllib.parse.urlencode(data, doseq=True)
        return self.Post(url, "application/x-www-form-urlencoded", encoded.encode())

    def Head(self, url: str) -> Result[Response, GoError]:
        """Head issues a HEAD to the specified URL."""
        req = Request(Method="HEAD", URL=url)
        return self.Do(req)


DefaultClient = Client()


def Get(url: str) -> Result[Response, GoError]:
    """Get issues a GET to the specified URL."""
    return DefaultClient.Get(url)


def Post(url: str, contentType: str, body: bytes) -> Result[Response, GoError]:
    """Post issues a POST to the specified URL."""
    return DefaultClient.Post(url, contentType, body)


def PostForm(url: str, data: dict[str, list[str]]) -> Result[Response, GoError]:
    """PostForm issues a POST with form data."""
    return DefaultClient.PostForm(url, data)


def Head(url: str) -> Result[Response, GoError]:
    """Head issues a HEAD to the specified URL."""
    return DefaultClient.Head(url)


def NewRequest(method: str, url: str, body: bytes | None = None) -> Result[Request, GoError]:
    """NewRequest returns a new Request given a method, URL, and optional body."""
    try:
        req = Request(
            Method=method.upper(),
            URL=url,
            Body=body,
            ContentLength=len(body) if body else 0,
        )
        parsed = urllib.parse.urlparse(url)
        req.Host = parsed.netloc
        return Ok(req)
    except Exception as e:
        return Err(GoError(str(e), "http.Error"))


# Handler takes ResponseWriter (not Response) - this is the HTTP server handler
Handler = Callable[["ResponseWriter", Request], None]
HandlerFunc = Handler


class ResponseWriter:
    """ResponseWriter interface for writing HTTP responses."""

    def __init__(self, handler: _http_server.BaseHTTPRequestHandler):
        self._handler = handler
        self._headers: Header = Header()
        self._status_code = 200
        self._headers_written = False

    def Header(self) -> Header:
        """Header returns the header map."""
        return self._headers

    def Write(self, data: bytes) -> int:
        """Write writes the data to the connection."""
        if not self._headers_written:
            self.WriteHeader(self._status_code)
        self._handler.wfile.write(data)
        return len(data)

    def WriteHeader(self, statusCode: int) -> None:
        """WriteHeader sends an HTTP response header."""
        if self._headers_written:
            return
        self._status_code = statusCode
        self._handler.send_response(statusCode)
        for key, value in self._headers.items():
            if isinstance(value, list):
                for v in value:
                    self._handler.send_header(key, v)
            else:
                self._handler.send_header(key, value)
        self._handler.end_headers()
        self._headers_written = True


_handlers: dict[str, Handler] = {}


class _HTTPHandler(_http_server.BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        self._handle_request()

    def do_POST(self) -> None:
        self._handle_request()

    def do_PUT(self) -> None:
        self._handle_request()

    def do_DELETE(self) -> None:
        self._handle_request()

    def do_HEAD(self) -> None:
        self._handle_request()

    def do_OPTIONS(self) -> None:
        self._handle_request()

    def do_PATCH(self) -> None:
        self._handle_request()

    def _handle_request(self) -> None:
        path = urllib.parse.urlparse(self.path).path

        handler = None
        for pattern, h in _handlers.items():
            if path == pattern or path.startswith(pattern.rstrip("/") + "/"):
                handler = h
                break

        if handler is None:
            self.send_error(404, "Not Found")
            return

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else None

        req = Request(
            Method=self.command,
            URL=self.path,
            Header=Header(self.headers.items()),
            Body=body,
            Host=self.headers.get("Host", ""),
        )

        w = ResponseWriter(self)
        try:
            handler(w, req)
        except Exception as e:
            if not w._headers_written:
                self.send_error(500, str(e))

    def log_message(self, format: str, *args: Any) -> None:
        pass


class ServeMux:
    """ServeMux is an HTTP request multiplexer."""

    def __init__(self) -> None:
        self._handlers: dict[str, Handler] = {}

    def Handle(self, pattern: str, handler: Handler) -> None:
        """Handle registers the handler for the given pattern."""
        self._handlers[pattern] = handler

    def HandleFunc(self, pattern: str, handler: HandlerFunc) -> None:
        """HandleFunc registers the handler function for the given pattern."""
        self._handlers[pattern] = handler

    def ServeHTTP(self, w: ResponseWriter, r: Request) -> None:
        """ServeHTTP dispatches the request to the handler."""
        path = urllib.parse.urlparse(r.URL).path

        handler = None
        for pattern, h in self._handlers.items():
            if path == pattern or path.startswith(pattern.rstrip("/") + "/"):
                handler = h
                break

        if handler is None:
            NotFound(w, r)
            return

        handler(w, r)


class Server:
    """HTTP server."""

    def __init__(self, addr: str = ":8080", handler: ServeMux | None = None):
        self.Addr = addr
        self.Handler = handler or ServeMux()
        self._server: _http_server.HTTPServer | None = None

    def ListenAndServe(self) -> Result[None, GoError]:
        """ListenAndServe listens and serves HTTP requests."""
        try:
            host, port = self._parse_addr()
            self._server = _http_server.HTTPServer((host, port), _HTTPHandler)
            self._server.serve_forever()
            return Ok(None)
        except Exception as e:
            return Err(GoError(str(e), "http.Error"))

    def Shutdown(self) -> Result[None, GoError]:
        """Shutdown gracefully shuts down the server."""
        if self._server:
            self._server.shutdown()
        return Ok(None)

    def _parse_addr(self) -> tuple[str, int]:
        if ":" in self.Addr:
            parts = self.Addr.rsplit(":", 1)
            host = parts[0] if parts[0] else ""
            port = int(parts[1])
        else:
            host = ""
            port = int(self.Addr)
        return host, port


def HandleFunc(pattern: str, handler: HandlerFunc) -> None:
    """HandleFunc registers the handler function for the given pattern."""
    _handlers[pattern] = handler


def Handle(pattern: str, handler: Handler) -> None:
    """Handle registers the handler for the given pattern."""
    _handlers[pattern] = handler


def ListenAndServe(addr: str, handler: ServeMux | None = None) -> Result[None, GoError]:
    """ListenAndServe listens and serves HTTP requests."""
    server = Server(addr, handler)
    return server.ListenAndServe()


def FileServer(root: str) -> Handler:
    """FileServer returns a handler that serves HTTP requests with files from root."""
    import mimetypes
    import os

    def handler(w: ResponseWriter, r: Request) -> None:
        path = urllib.parse.urlparse(r.URL).path.lstrip("/")
        filepath = os.path.join(root, path)

        if os.path.isdir(filepath):
            filepath = os.path.join(filepath, "index.html")

        if not os.path.exists(filepath):
            NotFound(w, r)
            return

        content_type, _ = mimetypes.guess_type(filepath)
        if content_type:
            w.Header().Set("Content-Type", content_type)

        with open(filepath, "rb") as f:
            w.Write(f.read())

    return handler


def NotFound(w: ResponseWriter, r: Request) -> None:
    """NotFound replies with an HTTP 404 not found error."""
    Error(w, "404 page not found", StatusNotFound)


def Redirect(w: ResponseWriter, r: Request, url: str, code: int) -> None:
    """Redirect replies with a redirect to url."""
    w.Header().Set("Location", url)
    w.WriteHeader(code)


def Error(w: ResponseWriter, error: str, code: int) -> None:
    """Error replies with the specified error message and HTTP code."""
    w.Header().Set("Content-Type", "text/plain; charset=utf-8")
    w.Header().Set("X-Content-Type-Options", "nosniff")
    w.WriteHeader(code)
    w.Write(error.encode())
