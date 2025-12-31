from goated.std import mime


class TestTypeByExtension:
    def test_html(self):
        result = mime.TypeByExtension(".html")
        assert "text/html" in result.lower()

    def test_json(self):
        result = mime.TypeByExtension(".json")
        assert "application/json" in result.lower()

    def test_css(self):
        result = mime.TypeByExtension(".css")
        assert "text/css" in result.lower()

    def test_js(self):
        result = mime.TypeByExtension(".js")
        assert "javascript" in result.lower()

    def test_png(self):
        result = mime.TypeByExtension(".png")
        assert "image/png" in result.lower()

    def test_jpg(self):
        result = mime.TypeByExtension(".jpg")
        assert "image/jpeg" in result.lower()

    def test_jpeg(self):
        result = mime.TypeByExtension(".jpeg")
        assert "image/jpeg" in result.lower()

    def test_pdf(self):
        result = mime.TypeByExtension(".pdf")
        assert "application/pdf" in result.lower()

    def test_unknown(self):
        result = mime.TypeByExtension(".unknownext12345")
        assert result == ""


class TestExtensionsByType:
    def test_text_html(self):
        result = mime.ExtensionsByType("text/html")
        assert result is not None
        assert any(".htm" in ext for ext in result)

    def test_application_json(self):
        result = mime.ExtensionsByType("application/json")
        assert result is not None
        assert any(".json" in ext for ext in result)

    def test_unknown_type(self):
        result = mime.ExtensionsByType("application/x-unknown-type-12345")
        assert result is None


class TestAddExtensionType:
    def test_add_custom_type(self):
        err = mime.AddExtensionType(".custom", "application/x-custom")
        assert err is None

        result = mime.TypeByExtension(".custom")
        assert result == "application/x-custom"

    def test_add_and_retrieve(self):
        mime.AddExtensionType(".mytype", "application/x-mytype")

        result = mime.TypeByExtension(".mytype")
        assert result == "application/x-mytype"

        exts = mime.ExtensionsByType("application/x-mytype")
        assert exts is not None
        assert ".mytype" in exts


class TestFormatMediaType:
    def test_simple(self):
        result = mime.FormatMediaType("text/html", None)
        assert result == "text/html"

    def test_with_charset(self):
        result = mime.FormatMediaType("text/html", {"charset": "utf-8"})
        assert "text/html" in result
        assert "charset=utf-8" in result

    def test_with_multiple_params(self):
        result = mime.FormatMediaType("multipart/form-data", {"boundary": "----boundary"})
        assert "multipart/form-data" in result
        assert "boundary=----boundary" in result

    def test_param_quoting(self):
        result = mime.FormatMediaType("text/plain", {"filename": "my file.txt"})
        assert "text/plain" in result


class TestParseMediaType:
    def test_simple(self):
        mediatype, params, err = mime.ParseMediaType("text/html")
        assert err is None
        assert mediatype == "text/html"
        assert params == {}

    def test_with_charset(self):
        mediatype, params, err = mime.ParseMediaType("text/html; charset=utf-8")
        assert err is None
        assert mediatype == "text/html"
        assert params.get("charset") == "utf-8"

    def test_with_multiple_params(self):
        mediatype, params, err = mime.ParseMediaType("multipart/form-data; boundary=abc123")
        assert err is None
        assert mediatype == "multipart/form-data"
        assert params.get("boundary") == "abc123"

    def test_quoted_param(self):
        mediatype, params, err = mime.ParseMediaType('text/plain; filename="my file.txt"')
        assert err is None
        assert params.get("filename") == "my file.txt"

    def test_case_insensitive(self):
        mediatype, params, err = mime.ParseMediaType("TEXT/HTML; CHARSET=UTF-8")
        assert err is None
        assert mediatype == "text/html"
        assert params.get("charset") == "UTF-8"


class TestRoundTrip:
    def test_format_parse_roundtrip(self):
        original_type = "application/json"
        original_params = {"charset": "utf-8"}

        formatted = mime.FormatMediaType(original_type, original_params)
        mediatype, params, err = mime.ParseMediaType(formatted)

        assert err is None
        assert mediatype == original_type
        assert params.get("charset") == "utf-8"


class TestEdgeCases:
    def test_empty_extension(self):
        result = mime.TypeByExtension("")
        assert result == ""

    def test_no_dot_extension(self):
        result = mime.TypeByExtension("html")
        assert result == ""

    def test_parse_empty(self):
        mediatype, params, err = mime.ParseMediaType("")
        assert mediatype == ""

    def test_parse_whitespace(self):
        mediatype, params, err = mime.ParseMediaType("  text/html  ;  charset=utf-8  ")
        assert err is None
        assert mediatype == "text/html"
