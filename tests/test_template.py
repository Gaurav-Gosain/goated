"""Tests for goated.std.template module (text/template)."""

from io import StringIO

from goated.std import template


class TestNew:
    """Test New function."""

    def test_new_creates_template(self):
        t = template.New("test")
        assert t is not None
        assert t.Name() == "test"

    def test_new_empty_name(self):
        t = template.New("")
        assert t.Name() == ""


class TestParse:
    """Test Parse method."""

    def test_parse_simple_text(self):
        t = template.New("test")
        result = t.Parse("Hello, World!")
        assert result.is_ok()

    def test_parse_with_variable(self):
        t = template.New("test")
        result = t.Parse("Hello, {{.Name}}!")
        assert result.is_ok()

    def test_parse_returns_template(self):
        t = template.New("test")
        result = t.Parse("template")
        assert result.unwrap() is t


class TestExecute:
    """Test Execute method."""

    def test_execute_plain_text(self):
        t = template.New("test")
        t.Parse("Hello, World!")

        buf = StringIO()
        result = t.Execute(buf, None)
        assert result.is_ok()
        assert buf.getvalue() == "Hello, World!"

    def test_execute_with_dot(self):
        t = template.New("test")
        t.Parse("Value: {{.}}")

        buf = StringIO()
        result = t.Execute(buf, "test data")
        assert result.is_ok()
        assert buf.getvalue() == "Value: test data"

    def test_execute_with_dict_field(self):
        t = template.New("test")
        t.Parse("Hello, {{.Name}}!")

        buf = StringIO()
        result = t.Execute(buf, {"Name": "John"})
        assert result.is_ok()
        assert buf.getvalue() == "Hello, John!"

    def test_execute_with_nested_dict(self):
        t = template.New("test")
        t.Parse("City: {{.Address.City}}")

        buf = StringIO()
        data = {"Address": {"City": "New York"}}
        result = t.Execute(buf, data)
        assert result.is_ok()
        assert buf.getvalue() == "City: New York"

    def test_execute_with_object(self):
        class Person:
            def __init__(self, name):
                self.Name = name

        t = template.New("test")
        t.Parse("Name: {{.Name}}")

        buf = StringIO()
        result = t.Execute(buf, Person("Alice"))
        assert result.is_ok()
        assert buf.getvalue() == "Name: Alice"

    def test_execute_missing_field(self):
        t = template.New("test")
        t.Parse("Value: {{.Missing}}")

        buf = StringIO()
        result = t.Execute(buf, {})
        assert result.is_ok()
        assert buf.getvalue() == "Value: "


class TestFuncs:
    """Test Funcs method."""

    def test_add_function(self):
        t = template.New("test")
        t.Funcs({"upper": lambda s: s.upper()})
        t.Parse("{{upper .}}")

        buf = StringIO()
        result = t.Execute(buf, "hello")
        assert result.is_ok()
        assert buf.getvalue() == "HELLO"

    def test_multiple_functions(self):
        t = template.New("test")
        t.Funcs(
            {
                "double": lambda x: int(x) * 2,
                "add": lambda x, y: x + y,
            }
        )
        t.Parse("{{double .}}")

        buf = StringIO()
        result = t.Execute(buf, 5)
        assert result.is_ok()
        assert buf.getvalue() == "10"

    def test_funcs_chaining(self):
        t = template.New("test")
        t2 = t.Funcs({"test": lambda: "test"})
        assert t2 is t


class TestPipelines:
    """Test template pipelines."""

    def test_simple_pipeline(self):
        t = template.New("test")
        t.Funcs({"upper": lambda s: s.upper()})
        t.Parse("{{.Name | upper}}")

        buf = StringIO()
        result = t.Execute(buf, {"Name": "john"})
        assert result.is_ok()
        assert buf.getvalue() == "JOHN"


class TestHTMLEscaping:
    """Test HTML escaping functions."""

    def test_html_escape_string(self):
        result = template.HTMLEscapeString("<script>alert('xss')</script>")
        assert "&lt;" in result
        assert "&gt;" in result
        assert "&#x27;" in result or "'" not in result or "&apos;" in result

    def test_html_escape_string_ampersand(self):
        result = template.HTMLEscapeString("Tom & Jerry")
        assert "&amp;" in result

    def test_html_escaper(self):
        result = template.HTMLEscaper("<b>", "bold", "</b>")
        assert "&lt;b&gt;" in result


class TestJSEscaping:
    """Test JavaScript escaping functions."""

    def test_js_escape_string_quotes(self):
        result = template.JSEscapeString('He said "hello"')
        assert '\\"' in result

    def test_js_escape_string_newline(self):
        result = template.JSEscapeString("line1\nline2")
        assert "\\n" in result

    def test_js_escape_string_backslash(self):
        result = template.JSEscapeString("path\\to\\file")
        assert "\\\\" in result

    def test_js_escape_string_html(self):
        result = template.JSEscapeString("<script>")
        assert "\\u003c" in result

    def test_js_escaper(self):
        result = template.JSEscaper("a", "b")
        assert result == "a b"


class TestURLQueryEscaper:
    """Test URL query escaping."""

    def test_url_query_escaper_spaces(self):
        result = template.URLQueryEscaper("hello world")
        assert "%20" in result or "+" in result

    def test_url_query_escaper_special(self):
        result = template.URLQueryEscaper("a=b&c=d")
        assert "=" not in result or "%3D" in result


class TestMust:
    """Test Must function."""

    def test_must_success(self):
        t = template.New("test")
        result = t.Parse("valid template")
        t2 = template.Must(result)
        assert t2 is t

    def test_must_returns_template(self):
        t = template.New("test")
        result = t.Parse("{{.Value}}")
        t2 = template.Must(result)
        assert t2.Name() == "test"


class TestClone:
    """Test Clone method."""

    def test_clone_creates_copy(self):
        t = template.New("original")
        t.Parse("{{.Value}}")

        result = t.Clone()
        assert result.is_ok()

        clone = result.unwrap()
        assert clone.Name() == "original"

    def test_clone_independent(self):
        t = template.New("test")
        t.Funcs({"fn": lambda: "original"})

        clone = t.Clone().unwrap()
        clone.Funcs({"fn": lambda: "cloned"})

        assert t._funcs["fn"]() == "original"


class TestNew_Method:
    """Test New method on Template."""

    def test_new_creates_associated_template(self):
        t = template.New("main")
        sub = t.New("sub")

        assert sub.Name() == "sub"
        assert "sub" in t._templates


class TestLookup:
    """Test Lookup method."""

    def test_lookup_existing(self):
        t = template.New("main")
        sub = t.New("sub")

        found = t.Lookup("sub")
        assert found is sub

    def test_lookup_nonexistent(self):
        t = template.New("main")
        found = t.Lookup("nonexistent")
        assert found is None


class TestTemplates:
    """Test Templates method."""

    def test_templates_empty(self):
        t = template.New("main")
        templates = t.Templates()
        assert templates == []

    def test_templates_with_associated(self):
        t = template.New("main")
        t.New("sub1")
        t.New("sub2")

        templates = t.Templates()
        assert len(templates) == 2


class TestDefinedTemplates:
    """Test DefinedTemplates method."""

    def test_defined_templates_empty(self):
        t = template.New("main")
        result = t.DefinedTemplates()
        assert result == ""

    def test_defined_templates_with_associated(self):
        t = template.New("main")
        t.New("sub")

        result = t.DefinedTemplates()
        assert "sub" in result
        assert "defined templates are" in result


class TestDefineBlocks:
    """Test define blocks in templates."""

    def test_parse_define(self):
        t = template.New("main")
        t.Parse('{{define "header"}}Header{{end}}')

        assert "header" in t._templates


class TestExecuteTemplate:
    """Test ExecuteTemplate method."""

    def test_execute_template(self):
        t = template.New("main")
        sub = t.New("sub")
        sub.Parse("Sub template: {{.}}")

        buf = StringIO()
        result = t.ExecuteTemplate(buf, "sub", "data")
        assert result.is_ok()
        assert buf.getvalue() == "Sub template: data"

    def test_execute_template_not_found(self):
        t = template.New("main")

        buf = StringIO()
        result = t.ExecuteTemplate(buf, "nonexistent", None)
        assert result.is_err()


class TestOption:
    """Test Option method."""

    def test_option_returns_template(self):
        t = template.New("test")
        t2 = t.Option("missingkey=zero")
        assert t2 is t


class TestModuleExports:
    """Test module exports."""

    def test_exports(self):
        assert hasattr(template, "New")
        assert hasattr(template, "Must")
        assert hasattr(template, "ParseFiles")
        assert hasattr(template, "ParseGlob")
        assert hasattr(template, "Template")
        assert hasattr(template, "FuncMap")
        assert hasattr(template, "HTMLEscapeString")
        assert hasattr(template, "HTMLEscaper")
        assert hasattr(template, "JSEscapeString")
        assert hasattr(template, "JSEscaper")
        assert hasattr(template, "URLQueryEscaper")
