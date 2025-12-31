from goated.std import url


class TestURLParse:
    def test_parse_simple_url(self):
        result = url.Parse("https://example.com/path")
        assert result.is_ok()
        u = result.unwrap()
        assert u.Scheme == "https"
        assert u.Host == "example.com"
        assert u.Path == "/path"

    def test_parse_url_with_query(self):
        result = url.Parse("https://example.com/search?q=test&page=1")
        assert result.is_ok()
        u = result.unwrap()
        assert u.Scheme == "https"
        assert u.Host == "example.com"
        assert u.Path == "/search"
        assert u.RawQuery == "q=test&page=1"

    def test_parse_url_with_fragment(self):
        result = url.Parse("https://example.com/page#section")
        assert result.is_ok()
        u = result.unwrap()
        assert u.Fragment == "section"

    def test_parse_url_with_port(self):
        result = url.Parse("https://example.com:8080/path")
        assert result.is_ok()
        u = result.unwrap()
        assert u.Host == "example.com:8080"
        assert u.Hostname() == "example.com"
        assert u.Port() == "8080"

    def test_parse_url_with_userinfo(self):
        result = url.Parse("https://user:pass@example.com/path")
        assert result.is_ok()
        u = result.unwrap()
        assert u.User is not None
        assert u.User.Username() == "user"
        password, has_password = u.User.Password()
        assert has_password
        assert password == "pass"

    def test_parse_empty_scheme_url(self):
        result = url.Parse("://invalid")
        assert result.is_ok()
        u = result.unwrap()
        assert u.Scheme == ""


class TestURLString:
    def test_string_simple(self):
        result = url.Parse("https://example.com/path")
        u = result.unwrap()
        assert u.String() == "https://example.com/path"

    def test_string_with_query(self):
        result = url.Parse("https://example.com/search?q=test")
        u = result.unwrap()
        assert "q=test" in u.String()


class TestQueryEscape:
    def test_escape_spaces(self):
        assert url.QueryEscape("hello world") == "hello+world"

    def test_escape_special_chars(self):
        escaped = url.QueryEscape("a=b&c=d")
        assert "=" not in escaped or escaped == "a%3Db%26c%3Dd"

    def test_escape_unicode(self):
        escaped = url.QueryEscape("日本語")
        assert "%" in escaped


class TestQueryUnescape:
    def test_unescape_plus(self):
        result = url.QueryUnescape("hello+world")
        assert result.is_ok()
        assert result.unwrap() == "hello world"

    def test_unescape_percent(self):
        result = url.QueryUnescape("hello%20world")
        assert result.is_ok()
        assert result.unwrap() == "hello world"

    def test_unescape_percent_gg(self):
        result = url.QueryUnescape("%GG")
        assert result.is_ok()


class TestPathEscape:
    def test_escape_spaces(self):
        assert url.PathEscape("hello world") == "hello%20world"

    def test_escape_slash(self):
        escaped = url.PathEscape("a/b")
        assert escaped == "a%2Fb"


class TestPathUnescape:
    def test_unescape_percent(self):
        result = url.PathUnescape("hello%20world")
        assert result.is_ok()
        assert result.unwrap() == "hello world"


class TestValues:
    def test_get_set(self):
        v = url.Values()
        v.Set("key", "value")
        assert v.Get("key") == "value"

    def test_add_multiple(self):
        v = url.Values()
        v.Add("key", "value1")
        v.Add("key", "value2")
        values = v.get("key", [])
        assert len(values) == 2
        assert "value1" in values
        assert "value2" in values

    def test_del(self):
        v = url.Values()
        v.Set("key", "value")
        v.Del("key")
        assert v.Get("key") == ""

    def test_has(self):
        v = url.Values()
        assert not v.Has("key")
        v.Set("key", "value")
        assert v.Has("key")

    def test_encode(self):
        v = url.Values()
        v.Set("a", "1")
        v.Set("b", "2")
        encoded = v.Encode()
        assert "a=1" in encoded
        assert "b=2" in encoded


class TestParseQuery:
    def test_parse_simple(self):
        result = url.ParseQuery("a=1&b=2")
        assert result.is_ok()
        v = result.unwrap()
        assert v.Get("a") == "1"
        assert v.Get("b") == "2"

    def test_parse_multiple_values(self):
        result = url.ParseQuery("a=1&a=2")
        assert result.is_ok()
        v = result.unwrap()
        values = v.get("a", [])
        assert len(values) == 2

    def test_parse_empty(self):
        result = url.ParseQuery("")
        assert result.is_ok()


class TestJoinPath:
    def test_join_simple(self):
        result = url.JoinPath("https://example.com", "a", "b")
        assert result.is_ok()
        assert result.unwrap() == "https://example.com/a/b"

    def test_join_with_slashes(self):
        result = url.JoinPath("https://example.com/", "/a/", "/b")
        assert result.is_ok()
        assert "//" not in result.unwrap().split("://")[1]


class TestUserinfo:
    def test_user_only(self):
        u = url.User("username")
        assert u.Username() == "username"
        _, has_password = u.Password()
        assert not has_password

    def test_user_password(self):
        u = url.UserPassword("username", "secret")
        assert u.Username() == "username"
        password, has_password = u.Password()
        assert has_password
        assert password == "secret"

    def test_string(self):
        u = url.UserPassword("user", "pass")
        assert u.String() == "user:pass"
