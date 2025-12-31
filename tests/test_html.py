from goated.std import html


class TestEscapeString:
    def test_escape_less_than(self):
        result = html.EscapeString("<div>")
        assert "&lt;" in result

    def test_escape_greater_than(self):
        result = html.EscapeString(">test")
        assert "&gt;" in result

    def test_escape_ampersand(self):
        result = html.EscapeString("a & b")
        assert "&amp;" in result

    def test_escape_quotes(self):
        result = html.EscapeString('"test"')
        assert "&quot;" in result or "&#34;" in result

    def test_escape_single_quote(self):
        result = html.EscapeString("it's")
        assert "&#x27;" in result or "&#39;" in result or "&apos;" in result

    def test_escape_combined(self):
        result = html.EscapeString('<a href="test">')
        assert "<" not in result
        assert ">" not in result

    def test_escape_no_change(self):
        text = "Hello World"
        assert html.EscapeString(text) == text


class TestUnescapeString:
    def test_unescape_less_than(self):
        result = html.UnescapeString("&lt;div&gt;")
        assert result == "<div>"

    def test_unescape_ampersand(self):
        result = html.UnescapeString("a &amp; b")
        assert result == "a & b"

    def test_unescape_quotes(self):
        result = html.UnescapeString("&quot;test&quot;")
        assert result == '"test"'

    def test_unescape_numeric(self):
        result = html.UnescapeString("&#60;test&#62;")
        assert result == "<test>"

    def test_unescape_hex(self):
        result = html.UnescapeString("&#x3C;test&#x3E;")
        assert result == "<test>"

    def test_unescape_no_change(self):
        text = "Hello World"
        assert html.UnescapeString(text) == text


class TestRoundTrip:
    def test_roundtrip(self):
        original = '<script>alert("XSS")</script>'
        escaped = html.EscapeString(original)
        unescaped = html.UnescapeString(escaped)
        assert unescaped == original

    def test_roundtrip_complex(self):
        original = 'Tom & Jerry\'s "Adventure" <Episode 1>'
        escaped = html.EscapeString(original)
        unescaped = html.UnescapeString(escaped)
        assert unescaped == original


class TestSecurity:
    def test_xss_prevention(self):
        malicious = '<script>alert("XSS")</script>'
        escaped = html.EscapeString(malicious)
        assert "<script>" not in escaped
        assert "</script>" not in escaped

    def test_attribute_injection(self):
        malicious = '" onclick="evil()"'
        escaped = html.EscapeString(malicious)
        assert '"' not in escaped or "&quot;" in escaped


class TestEdgeCases:
    def test_empty_string(self):
        assert html.EscapeString("") == ""
        assert html.UnescapeString("") == ""

    def test_only_special_chars(self):
        result = html.EscapeString("<>&\"'")
        assert "<" not in result
        assert ">" not in result
        assert "&" in result  # will be &amp; or similar

    def test_unicode(self):
        text = "日本語 <test>"
        escaped = html.EscapeString(text)
        assert "日本語" in escaped
        assert "&lt;" in escaped
