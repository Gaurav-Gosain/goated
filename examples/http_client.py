#!/usr/bin/env python3
"""HTTP client examples using goated.std.http (net/http).

Demonstrates:
- Making GET/POST requests
- Custom headers and cookies
- Creating requests with NewRequest
- Response handling
"""

from goated.std import http


def demo_basic_concepts():
    """Demonstrate HTTP constants and basic types."""
    print("=== HTTP Constants and Types ===\n")

    # Status codes (like Go's http.StatusOK, etc.)
    print("Status Codes:")
    print(f"  http.StatusOK = {http.StatusOK}")
    print(f"  http.StatusCreated = {http.StatusCreated}")
    print(f"  http.StatusNotFound = {http.StatusNotFound}")
    print(f"  http.StatusInternalServerError = {http.StatusInternalServerError}")

    # HTTP methods
    print("\nHTTP Methods:")
    print(f"  http.MethodGet = {http.MethodGet!r}")
    print(f"  http.MethodPost = {http.MethodPost!r}")
    print(f"  http.MethodPut = {http.MethodPut!r}")
    print(f"  http.MethodDelete = {http.MethodDelete!r}")
    print()


def demo_headers():
    """Demonstrate Header operations."""
    print("=== HTTP Headers ===\n")

    # Create and manipulate headers
    h = http.Header()

    # Set headers (case-insensitive)
    h.Set("Content-Type", "application/json")
    h.Set("authorization", "Bearer token123")  # Will be normalized to "Authorization"

    print(f"Content-Type: {h.Get('content-type')}")  # Case-insensitive get
    print(f"Authorization: {h.Get('Authorization')}")

    # Add multiple values for same header
    h.Add("Accept", "text/html")
    h.Add("Accept", "application/json")
    print(f"Accept (first): {h.Get('Accept')}")

    # Delete a header
    h.Del("Authorization")
    print(f"After Del - Authorization: {h.Get('Authorization')!r}")

    # Clone headers
    h2 = h.Clone()
    h2.Set("X-Custom", "value")
    print(f"Original has X-Custom: {h.Get('X-Custom')!r}")
    print(f"Clone has X-Custom: {h2.Get('X-Custom')!r}")
    print()


def demo_cookies():
    """Demonstrate Cookie handling."""
    print("=== HTTP Cookies ===\n")

    # Create a cookie
    cookie = http.Cookie(
        Name="session_id",
        Value="abc123xyz",
        Path="/",
        Domain="example.com",
        MaxAge=3600,
        Secure=True,
        HttpOnly=True,
        SameSite="Strict",
    )

    print(f"Cookie string: {cookie.String()}")

    # Simple cookie
    simple = http.Cookie(Name="user", Value="john")
    print(f"Simple cookie: {simple.String()}")
    print()


def demo_request_creation():
    """Demonstrate creating HTTP requests."""
    print("=== Creating Requests ===\n")

    # Create a GET request
    result = http.NewRequest("GET", "https://api.example.com/users")
    if result.is_ok():
        req = result.unwrap()
        print("GET Request:")
        print(f"  Method: {req.Method}")
        print(f"  URL: {req.URL}")
        print(f"  Host: {req.Host}")

    # Create a POST request with body
    body = b'{"name": "John", "email": "john@example.com"}'
    result = http.NewRequest("POST", "https://api.example.com/users", body)
    if result.is_ok():
        req = result.unwrap()
        req.Header.Set("Content-Type", "application/json")
        print("\nPOST Request:")
        print(f"  Method: {req.Method}")
        print(f"  URL: {req.URL}")
        print(f"  Content-Length: {req.ContentLength}")
        print(f"  Content-Type: {req.Header.Get('Content-Type')}")

    # Add cookies to request
    req = http.Request(Method="GET", URL="https://example.com")
    req.AddCookie(http.Cookie(Name="session", Value="xyz789"))
    print("\nRequest with cookie:")
    print(f"  Cookie header: {req.Header.Get('Cookie')}")
    print()


def demo_request_with_form():
    """Demonstrate form data handling."""
    print("=== Form Data ===\n")

    # Request with form data
    req = http.Request()
    req.Form = {
        "username": ["john"],
        "tags": ["python", "go", "rust"],
    }
    req.PostForm = {
        "password": ["secret123"],
    }

    print(f"FormValue('username'): {req.FormValue('username')}")
    print(f"FormValue('tags'): {req.FormValue('tags')}")  # Returns first value
    print(f"PostFormValue('password'): {req.PostFormValue('password')}")
    print(f"FormValue('missing'): {req.FormValue('missing')!r}")
    print()


def demo_response_handling():
    """Demonstrate Response handling."""
    print("=== Response Handling ===\n")

    from io import BytesIO

    # Simulate a response
    body_content = b'{"status": "success", "data": {"id": 123}}'
    response = http.Response(
        Status="200 OK",
        StatusCode=http.StatusOK,
        Body=BytesIO(body_content),
        ContentLength=len(body_content),
    )
    response.Header.Set("Content-Type", "application/json")

    print(f"Status: {response.Status}")
    print(f"StatusCode: {response.StatusCode}")
    print(f"Content-Type: {response.Header.Get('Content-Type')}")
    print(f"Content-Length: {response.ContentLength}")

    # Read body
    result = response.Read()
    if result.is_ok():
        body = result.unwrap()
        print(f"Body: {body.decode()}")

    # Close response
    response.Close()
    print()


def demo_client():
    """Demonstrate HTTP Client."""
    print("=== HTTP Client ===\n")

    # Create client with custom timeout
    client = http.Client(timeout=30.0)
    print(f"Client timeout: {client.Timeout}s")

    # Default client is also available
    print(f"DefaultClient timeout: {http.DefaultClient.Timeout}s")

    # Note: Actual HTTP calls would look like:
    # result = http.Get("https://api.example.com/data")
    # result = http.Post("https://api.example.com/data", "application/json", b'{}')
    # result = http.PostForm("https://api.example.com/form", {"key": ["value"]})
    # result = http.Head("https://api.example.com/data")

    print("\nAvailable methods:")
    print("  http.Get(url) -> Result[Response, GoError]")
    print("  http.Post(url, contentType, body) -> Result[Response, GoError]")
    print("  http.PostForm(url, data) -> Result[Response, GoError]")
    print("  http.Head(url) -> Result[Response, GoError]")
    print("  client.Do(request) -> Result[Response, GoError]")
    print()


def demo_server_components():
    """Demonstrate server-side components."""
    print("=== Server Components ===\n")

    # ServeMux - request multiplexer
    mux = http.ServeMux()

    # Register handlers
    def hello_handler(w, r):
        w.Header().Set("Content-Type", "text/plain")
        w.Write(b"Hello, World!")

    def api_handler(w, r):
        w.Header().Set("Content-Type", "application/json")
        w.WriteHeader(http.StatusOK)
        w.Write(b'{"message": "API response"}')

    mux.HandleFunc("/hello", hello_handler)
    mux.HandleFunc("/api/", api_handler)

    print("Registered routes:")
    print("  /hello -> hello_handler")
    print("  /api/  -> api_handler")

    # Server configuration
    server = http.Server(addr=":8080")
    print(f"\nServer configured on {server.Addr}")

    # Global handlers (using default mux)
    http._handlers.clear()  # Clear any existing
    http.HandleFunc("/", lambda w, r: w.Write(b"Root handler"))
    http.Handle("/static", lambda w, r: w.Write(b"Static handler"))

    print("\nNote: To start server, use:")
    print('  http.ListenAndServe(":8080", mux)')
    print("  # or")
    print("  server.ListenAndServe()")
    print()


def demo_file_server():
    """Demonstrate FileServer."""
    print("=== File Server ===\n")

    # Create a file server handler
    # In real use: handler = http.FileServer("/path/to/static/files")

    print("FileServer usage:")
    print('  handler = http.FileServer("./static")')
    print('  http.Handle("/static/", handler)')
    print()

    print("This serves files from ./static directory")
    print("Request to /static/css/style.css serves ./static/css/style.css")
    print()


def demo_redirects_and_errors():
    """Demonstrate redirect and error responses."""
    print("=== Redirects and Error Responses ===\n")

    print("Error response helpers:")
    print("  http.Error(w, 'Not Found', http.StatusNotFound)")
    print("  http.NotFound(w, r)  # Sends 404")
    print()

    print("Redirect helpers:")
    print("  http.Redirect(w, r, '/new-url', http.StatusMovedPermanently)  # 301")
    print("  http.Redirect(w, r, '/new-url', http.StatusFound)  # 302")
    print()


def main():
    print("=" * 60)
    print("  goated.std.http - Go's net/http for Python")
    print("=" * 60)
    print()

    demo_basic_concepts()
    demo_headers()
    demo_cookies()
    demo_request_creation()
    demo_request_with_form()
    demo_response_handling()
    demo_client()
    demo_server_components()
    demo_file_server()
    demo_redirects_and_errors()

    print("=" * 60)
    print("  Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
