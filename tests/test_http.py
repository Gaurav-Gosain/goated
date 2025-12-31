"""Tests for goated.std.http module (net/http)."""

from io import BytesIO

from goated.std import http


class TestStatusCodes:
    """Test HTTP status code constants."""

    def test_status_ok(self):
        assert http.StatusOK == 200

    def test_status_created(self):
        assert http.StatusCreated == 201

    def test_status_accepted(self):
        assert http.StatusAccepted == 202

    def test_status_no_content(self):
        assert http.StatusNoContent == 204

    def test_status_moved_permanently(self):
        assert http.StatusMovedPermanently == 301

    def test_status_found(self):
        assert http.StatusFound == 302

    def test_status_not_modified(self):
        assert http.StatusNotModified == 304

    def test_status_bad_request(self):
        assert http.StatusBadRequest == 400

    def test_status_unauthorized(self):
        assert http.StatusUnauthorized == 401

    def test_status_forbidden(self):
        assert http.StatusForbidden == 403

    def test_status_not_found(self):
        assert http.StatusNotFound == 404

    def test_status_method_not_allowed(self):
        assert http.StatusMethodNotAllowed == 405

    def test_status_internal_server_error(self):
        assert http.StatusInternalServerError == 500

    def test_status_bad_gateway(self):
        assert http.StatusBadGateway == 502

    def test_status_service_unavailable(self):
        assert http.StatusServiceUnavailable == 503


class TestMethods:
    """Test HTTP method constants."""

    def test_method_get(self):
        assert http.MethodGet == "GET"

    def test_method_post(self):
        assert http.MethodPost == "POST"

    def test_method_put(self):
        assert http.MethodPut == "PUT"

    def test_method_delete(self):
        assert http.MethodDelete == "DELETE"

    def test_method_head(self):
        assert http.MethodHead == "HEAD"

    def test_method_options(self):
        assert http.MethodOptions == "OPTIONS"

    def test_method_patch(self):
        assert http.MethodPatch == "PATCH"


class TestHeader:
    """Test Header class."""

    def test_set_and_get(self):
        h = http.Header()
        h.Set("Content-Type", "application/json")
        assert h.Get("Content-Type") == "application/json"

    def test_case_insensitive(self):
        h = http.Header()
        h.Set("content-type", "text/plain")
        assert h.Get("Content-Type") == "text/plain"

    def test_add_creates_list(self):
        h = http.Header()
        h.Add("Accept", "text/html")
        h.Add("Accept", "application/json")
        assert h.Get("Accept") == "text/html"

    def test_del(self):
        h = http.Header()
        h.Set("X-Custom", "value")
        h.Del("X-Custom")
        assert h.Get("X-Custom") == ""

    def test_clone(self):
        h = http.Header()
        h.Set("Key", "Value")
        h2 = h.Clone()
        assert h2.Get("Key") == "Value"
        h2.Set("Key", "NewValue")
        assert h.Get("Key") == "Value"


class TestCookie:
    """Test Cookie class."""

    def test_basic_cookie(self):
        c = http.Cookie(Name="session", Value="abc123")
        assert c.Name == "session"
        assert c.Value == "abc123"

    def test_cookie_string_simple(self):
        c = http.Cookie(Name="id", Value="42")
        assert c.String() == "id=42"

    def test_cookie_string_with_path(self):
        c = http.Cookie(Name="id", Value="42", Path="/")
        assert "Path=/" in c.String()

    def test_cookie_string_with_domain(self):
        c = http.Cookie(Name="id", Value="42", Domain="example.com")
        assert "Domain=example.com" in c.String()

    def test_cookie_string_secure(self):
        c = http.Cookie(Name="id", Value="42", Secure=True)
        assert "Secure" in c.String()

    def test_cookie_string_httponly(self):
        c = http.Cookie(Name="id", Value="42", HttpOnly=True)
        assert "HttpOnly" in c.String()

    def test_cookie_string_max_age(self):
        c = http.Cookie(Name="id", Value="42", MaxAge=3600)
        assert "Max-Age=3600" in c.String()


class TestRequest:
    """Test Request class."""

    def test_default_method(self):
        req = http.Request()
        assert req.Method == "GET"

    def test_set_method(self):
        req = http.Request(Method="POST", URL="http://example.com")
        assert req.Method == "POST"
        assert req.URL == "http://example.com"

    def test_add_cookie(self):
        req = http.Request()
        c = http.Cookie(Name="session", Value="xyz")
        req.AddCookie(c)
        assert "session=xyz" in req.Header.Get("Cookie")

    def test_get_cookie(self):
        req = http.Request()
        req.Header.Set("Cookie", "session=abc123")
        result = req.Cookie("session")
        assert result.is_ok()
        assert result.unwrap().Value == "abc123"

    def test_get_cookie_not_found(self):
        req = http.Request()
        result = req.Cookie("nonexistent")
        assert result.is_err()
        assert result.err().go_type == "http.ErrNoCookie"

    def test_form_value(self):
        req = http.Request()
        req.Form = {"name": ["John"]}
        assert req.FormValue("name") == "John"

    def test_form_value_missing(self):
        req = http.Request()
        assert req.FormValue("missing") == ""

    def test_post_form_value(self):
        req = http.Request()
        req.PostForm = {"data": ["test"]}
        assert req.PostFormValue("data") == "test"


class TestResponse:
    """Test Response class."""

    def test_response_fields(self):
        resp = http.Response(
            Status="200 OK",
            StatusCode=200,
        )
        assert resp.Status == "200 OK"
        assert resp.StatusCode == 200

    def test_read_body(self):
        body = BytesIO(b"Hello, World!")
        resp = http.Response(Body=body)
        result = resp.Read()
        assert result.is_ok()
        assert result.unwrap() == b"Hello, World!"

    def test_read_empty_body(self):
        resp = http.Response(Body=None)
        result = resp.Read()
        assert result.is_ok()
        assert result.unwrap() == b""

    def test_close(self):
        body = BytesIO(b"data")
        resp = http.Response(Body=body)
        result = resp.Close()
        assert result.is_ok()


class TestNewRequest:
    """Test NewRequest function."""

    def test_new_request_get(self):
        result = http.NewRequest("GET", "http://example.com/path")
        assert result.is_ok()
        req = result.unwrap()
        assert req.Method == "GET"
        assert req.URL == "http://example.com/path"
        assert req.Host == "example.com"

    def test_new_request_post_with_body(self):
        body = b'{"key": "value"}'
        result = http.NewRequest("POST", "http://api.example.com/data", body)
        assert result.is_ok()
        req = result.unwrap()
        assert req.Method == "POST"
        assert req.Body == body
        assert req.ContentLength == len(body)

    def test_new_request_uppercase_method(self):
        result = http.NewRequest("post", "http://example.com")
        assert result.is_ok()
        assert result.unwrap().Method == "POST"


class TestClient:
    """Test Client class."""

    def test_client_default_timeout(self):
        client = http.Client()
        assert client.Timeout == 30.0

    def test_client_custom_timeout(self):
        client = http.Client(timeout=60.0)
        assert client.Timeout == 60.0


class TestDefaultClient:
    """Test DefaultClient."""

    def test_default_client_exists(self):
        assert http.DefaultClient is not None
        assert isinstance(http.DefaultClient, http.Client)


class TestServeMux:
    """Test ServeMux class."""

    def test_create_mux(self):
        mux = http.ServeMux()
        assert mux is not None

    def test_handle_func(self):
        mux = http.ServeMux()

        def handler(w, r):
            w.Write(b"Hello")

        mux.HandleFunc("/test", handler)
        assert "/test" in mux._handlers


class TestServer:
    """Test Server class."""

    def test_server_default_addr(self):
        server = http.Server()
        assert server.Addr == ":8080"

    def test_server_custom_addr(self):
        server = http.Server(addr=":9000")
        assert server.Addr == ":9000"

    def test_parse_addr_with_host(self):
        server = http.Server(addr="localhost:8080")
        host, port = server._parse_addr()
        assert host == "localhost"
        assert port == 8080

    def test_parse_addr_without_host(self):
        server = http.Server(addr=":3000")
        host, port = server._parse_addr()
        assert host == ""
        assert port == 3000


class TestHandleFunc:
    """Test HandleFunc function."""

    def test_register_handler(self):
        http._handlers.clear()

        def my_handler(w, r):
            pass

        http.HandleFunc("/api", my_handler)
        assert "/api" in http._handlers


class TestModuleExports:
    """Test that all expected exports are available."""

    def test_exports(self):
        assert hasattr(http, "Get")
        assert hasattr(http, "Post")
        assert hasattr(http, "PostForm")
        assert hasattr(http, "Head")
        assert hasattr(http, "NewRequest")
        assert hasattr(http, "DefaultClient")
        assert hasattr(http, "Client")
        assert hasattr(http, "Request")
        assert hasattr(http, "Response")
        assert hasattr(http, "Header")
        assert hasattr(http, "Cookie")
        assert hasattr(http, "Server")
        assert hasattr(http, "ListenAndServe")
        assert hasattr(http, "HandleFunc")
        assert hasattr(http, "Handle")
        assert hasattr(http, "ServeMux")
        assert hasattr(http, "FileServer")
        assert hasattr(http, "NotFound")
        assert hasattr(http, "Redirect")
        assert hasattr(http, "Error")
