#!/usr/bin/env python3
"""Text templating examples using goated.std.template.

Demonstrates:
- Basic template parsing and execution
- Variable substitution
- Custom functions
- Pipelines
- HTML/JS escaping
"""

from io import StringIO

from goated.std import template


def demo_basic_template():
    """Demonstrate basic template creation and execution."""
    print("=== Basic Templates ===\n")

    # Create a simple template
    t = template.New("greeting")
    t.Parse("Hello, {{.}}!")

    buf = StringIO()
    t.Execute(buf, "World")
    print(f"Simple: {buf.getvalue()}")

    # Template with dict data
    t = template.New("user")
    t.Parse("Name: {{.Name}}, Email: {{.Email}}")

    buf = StringIO()
    t.Execute(buf, {"Name": "Alice", "Email": "alice@example.com"})
    print(f"Dict: {buf.getvalue()}")

    # Template with object data
    class User:
        def __init__(self, name, age):
            self.Name = name
            self.Age = age

    t = template.New("user_obj")
    t.Parse("{{.Name}} is {{.Age}} years old")

    buf = StringIO()
    t.Execute(buf, User("Bob", 30))
    print(f"Object: {buf.getvalue()}")
    print()


def demo_nested_fields():
    """Demonstrate nested field access."""
    print("=== Nested Fields ===\n")

    t = template.New("nested")
    t.Parse(
        """
User: {{.User.Name}}
Address: {{.User.Address.City}}, {{.User.Address.Country}}
""".strip()
    )

    data = {
        "User": {
            "Name": "Charlie",
            "Address": {
                "City": "New York",
                "Country": "USA",
            },
        }
    }

    buf = StringIO()
    t.Execute(buf, data)
    print(buf.getvalue())
    print()


def demo_custom_functions():
    """Demonstrate custom functions in templates."""
    print("=== Custom Functions ===\n")

    t = template.New("funcs")

    # Add custom functions
    t.Funcs(
        {
            "upper": lambda s: str(s).upper(),
            "lower": lambda s: str(s).lower(),
            "repeat": lambda s, n: str(s) * int(n),
            "add": lambda a, b: int(a) + int(b),
            "greet": lambda name: f"Hello, {name}!",
        }
    )

    # Use functions in template
    t.Parse("{{upper .Name}} - {{greet .Name}}")

    buf = StringIO()
    t.Execute(buf, {"Name": "alice"})
    print(f"Functions: {buf.getvalue()}")

    # Function with multiple args
    t2 = template.New("multi_args")
    t2.Funcs({"repeat": lambda s, n: str(s) * int(n)})
    t2.Parse('{{repeat "Go" 3}}')

    buf = StringIO()
    t2.Execute(buf, None)
    print(f"Repeat: {buf.getvalue()}")
    print()


def demo_pipelines():
    """Demonstrate template pipelines."""
    print("=== Pipelines ===\n")

    t = template.New("pipeline")
    t.Funcs(
        {
            "upper": lambda s: str(s).upper(),
            "trim": lambda s: str(s).strip(),
            "quote": lambda s: f'"{s}"',
        }
    )

    # Pipeline: value | function | function
    t.Parse("{{.Name | upper}}")

    buf = StringIO()
    t.Execute(buf, {"Name": "alice"})
    print(f"Pipeline (upper): {buf.getvalue()}")
    print()


def demo_must():
    """Demonstrate Must helper function."""
    print("=== Must Helper ===\n")

    # Must panics on error, useful for initialization
    t = template.Must(template.New("must_test").Parse("Hello, {{.}}!"))

    buf = StringIO()
    t.Execute(buf, "Must")
    print(f"Must result: {buf.getvalue()}")

    # Using Must with chained calls
    t = template.Must(
        template.New("chained")
        .Funcs({"double": lambda x: int(x) * 2})
        .Parse("Double: {{double .}}")
    )

    buf = StringIO()
    t.Execute(buf, 21)
    print(f"Chained Must: {buf.getvalue()}")
    print()


def demo_associated_templates():
    """Demonstrate associated templates."""
    print("=== Associated Templates ===\n")

    # Main template
    main = template.New("main")

    # Create associated templates
    header = main.New("header")
    header.Parse("=== HEADER ===")

    footer = main.New("footer")
    footer.Parse("=== FOOTER ===")

    content = main.New("content")
    content.Parse("Content: {{.}}")

    # List templates
    templates = main.Templates()
    print(f"Associated templates: {[t.Name() for t in templates]}")
    print(f"DefinedTemplates: {main.DefinedTemplates()}")

    # Execute specific template
    buf = StringIO()
    main.ExecuteTemplate(buf, "content", "Hello!")
    print(f"Execute 'content': {buf.getvalue()}")

    # Lookup template
    found = main.Lookup("header")
    if found:
        buf = StringIO()
        found.Execute(buf, None)
        print(f"Execute 'header': {buf.getvalue()}")
    print()


def demo_define_blocks():
    """Demonstrate define blocks."""
    print("=== Define Blocks ===\n")

    t = template.New("main")
    t.Parse(
        """
{{define "greeting"}}Hello, {{.}}!{{end}}
{{define "farewell"}}Goodbye, {{.}}!{{end}}
Main template
""".strip()
    )

    # Check defined templates
    print(f"Defined: {t.DefinedTemplates()}")

    # Execute defined template
    buf = StringIO()
    t.ExecuteTemplate(buf, "greeting", "World")
    print(f"Greeting: {buf.getvalue()}")

    buf = StringIO()
    t.ExecuteTemplate(buf, "farewell", "Friend")
    print(f"Farewell: {buf.getvalue()}")
    print()


def demo_clone():
    """Demonstrate template cloning."""
    print("=== Template Cloning ===\n")

    # Create original template with functions
    original = template.New("original")
    original.Funcs({"format": lambda x: f"[{x}]"})
    original.Parse("Original: {{format .}}")

    # Clone the template
    result = original.Clone()
    if result.is_ok():
        clone = result.unwrap()

        # Modify clone's functions without affecting original
        clone.Funcs({"format": lambda x: f"<{x}>"})

        buf1 = StringIO()
        original.Execute(buf1, "test")

        buf2 = StringIO()
        clone.Execute(buf2, "test")

        print(f"Original: {buf1.getvalue()}")
        print(f"Clone: {buf2.getvalue()}")
    print()


def demo_html_escaping():
    """Demonstrate HTML escaping functions."""
    print("=== HTML Escaping ===\n")

    dangerous = '<script>alert("XSS")</script>'
    safe = template.HTMLEscapeString(dangerous)
    print(f"Original: {dangerous}")
    print(f"Escaped: {safe}")

    # HTMLEscaper with multiple args
    result = template.HTMLEscaper("<b>", "bold", "</b>")
    print(f"HTMLEscaper: {result}")
    print()


def demo_js_escaping():
    """Demonstrate JavaScript escaping functions."""
    print("=== JavaScript Escaping ===\n")

    js_string = 'Hello\nWorld\t"quoted"'
    escaped = template.JSEscapeString(js_string)
    print(f"Original: {js_string!r}")
    print(f"Escaped: {escaped}")

    # HTML in JS
    html_in_js = '<script>alert("xss")</script>'
    escaped = template.JSEscapeString(html_in_js)
    print(f"HTML in JS escaped: {escaped}")

    # JSEscaper with multiple args
    result = template.JSEscaper("line1", "line2")
    print(f"JSEscaper: {result}")
    print()


def demo_url_escaping():
    """Demonstrate URL escaping."""
    print("=== URL Escaping ===\n")

    query = "search term with spaces & special=chars"
    escaped = template.URLQueryEscaper(query)
    print(f"Original: {query}")
    print(f"Escaped: {escaped}")

    # Multiple args
    result = template.URLQueryEscaper("hello", "world")
    print(f"URLQueryEscaper: {result}")
    print()


def demo_real_world_example():
    """Demonstrate a real-world template example."""
    print("=== Real-World Example: Email Template ===\n")

    email_template = template.New("email")
    email_template.Funcs(
        {
            "upper": lambda s: str(s).upper(),
        }
    )

    email_template.Parse(
        """
Subject: Welcome to {{.CompanyName}}!

Dear {{.User.Name}},

Thank you for joining {{.CompanyName}}. Your account has been created with:
- Username: {{.User.Username}}
- Email: {{.User.Email}}

Your plan: {{.Plan | upper}}

Best regards,
The {{.CompanyName}} Team
""".strip()
    )

    data = {
        "CompanyName": "Acme Inc",
        "User": {
            "Name": "John Doe",
            "Username": "johnd",
            "Email": "john@example.com",
        },
        "Plan": "premium",
    }

    buf = StringIO()
    email_template.Execute(buf, data)
    print(buf.getvalue())
    print()


def main():
    print("=" * 60)
    print("  goated.std.template - Go's text/template for Python")
    print("=" * 60)
    print()

    demo_basic_template()
    demo_nested_fields()
    demo_custom_functions()
    demo_pipelines()
    demo_must()
    demo_associated_templates()
    demo_define_blocks()
    demo_clone()
    demo_html_escaping()
    demo_js_escaping()
    demo_url_escaping()
    demo_real_world_example()

    print("=" * 60)
    print("  Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
