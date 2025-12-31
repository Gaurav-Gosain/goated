from __future__ import annotations

import html as _html
import re
from collections.abc import Callable
from typing import Any, TextIO

from goated.result import Err, GoError, Ok, Result

__all__ = [
    "New",
    "Must",
    "ParseFiles",
    "ParseGlob",
    "Template",
    "FuncMap",
    "HTMLEscapeString",
    "HTMLEscaper",
    "JSEscapeString",
    "JSEscaper",
    "URLQueryEscaper",
]

FuncMap = dict[str, Callable[..., object]]

_ACTION_PATTERN = re.compile(r"\{\{(.+?)\}\}", re.DOTALL)
_VARIABLE_PATTERN = re.compile(r"^\.(\w+)$")
_FIELD_PATTERN = re.compile(r"^\.(\w+(?:\.\w+)*)$")
_RANGE_PATTERN = re.compile(r"^range\s+(.+)$")
_IF_PATTERN = re.compile(r"^if\s+(.+)$")
_ELSE_PATTERN = re.compile(r"^else$")
_END_PATTERN = re.compile(r"^end$")
_WITH_PATTERN = re.compile(r"^with\s+(.+)$")
_TEMPLATE_PATTERN = re.compile(r'^template\s+"([^"]+)"(?:\s+(.+))?$')
_DEFINE_PATTERN = re.compile(r'^define\s+"([^"]+)"$')
_BLOCK_PATTERN = re.compile(r'^block\s+"([^"]+)"(?:\s+(.+))?$')


def HTMLEscapeString(s: str) -> str:
    """HTMLEscapeString escapes special HTML characters."""
    return _html.escape(s, quote=True)


def HTMLEscaper(*args: object) -> str:
    """Returns the escaped HTML equivalent of its arguments' textual representation."""
    return HTMLEscapeString(" ".join(str(a) for a in args))


def JSEscapeString(s: str) -> str:
    """JSEscapeString escapes special JavaScript characters."""
    result = []
    for c in s:
        if c == "\\":
            result.append("\\\\")
        elif c == '"':
            result.append('\\"')
        elif c == "'":
            result.append("\\'")
        elif c == "\n":
            result.append("\\n")
        elif c == "\r":
            result.append("\\r")
        elif c == "\t":
            result.append("\\t")
        elif c == "<":
            result.append("\\u003c")
        elif c == ">":
            result.append("\\u003e")
        elif c == "&":
            result.append("\\u0026")
        else:
            result.append(c)
    return "".join(result)


def JSEscaper(*args: object) -> str:
    """Returns the escaped JavaScript equivalent of its arguments' textual representation."""
    return JSEscapeString(" ".join(str(a) for a in args))


def URLQueryEscaper(*args: object) -> str:
    """Returns the escaped URL query equivalent of its arguments' textual representation."""
    import urllib.parse

    return urllib.parse.quote(" ".join(str(a) for a in args))


class Template:
    """Template represents a parsed template."""

    def __init__(self, name: str = ""):
        self._name = name
        self._text = ""
        self._funcs: FuncMap = {}
        self._templates: dict[str, Template] = {}
        self._parsed = False

    def Name(self) -> str:
        """Name returns the name of the template."""
        return self._name

    def Funcs(self, funcMap: FuncMap) -> Template:
        """Funcs adds the functions to the template's function map."""
        self._funcs.update(funcMap)
        return self

    def Parse(self, text: str) -> Result[Template, GoError]:
        """Parse parses the template definition string."""
        try:
            self._text = text
            self._parsed = True
            self._parse_defines(text)
            return Ok(self)
        except Exception as e:
            return Err(GoError(str(e), "template.ParseError"))

    def _parse_defines(self, text: str) -> None:
        """Parse define blocks and add them as associated templates."""
        define_pattern = re.compile(r'\{\{define\s+"([^"]+)"\}\}(.*?)\{\{end\}\}', re.DOTALL)
        for match in define_pattern.finditer(text):
            name = match.group(1)
            content = match.group(2)
            t = Template(name)
            t._text = content
            t._funcs = self._funcs
            t._parsed = True
            self._templates[name] = t

    def ParseFiles(self, *filenames: str) -> Result[Template, GoError]:
        """ParseFiles parses the named files and associates them with the template."""
        try:
            for filename in filenames:
                with open(filename) as f:
                    content = f.read()
                name = filename.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
                t = Template(name)
                t._text = content
                t._funcs = self._funcs
                t._parsed = True
                self._templates[name] = t
                if not self._parsed:
                    self._text = content
                    self._parsed = True
            return Ok(self)
        except Exception as e:
            return Err(GoError(str(e), "template.ParseError"))

    def Execute(self, wr: TextIO, data: Any) -> Result[None, GoError]:
        """Execute applies the template to the data and writes the result to wr."""
        try:
            result = self._execute(self._text, data, data)
            wr.write(result)
            return Ok(None)
        except Exception as e:
            return Err(GoError(str(e), "template.ExecError"))

    def ExecuteTemplate(self, wr: TextIO, name: str, data: Any) -> Result[None, GoError]:
        """ExecuteTemplate applies the named template to the data and writes the result to wr."""
        if name not in self._templates:
            return Err(GoError(f"template {name!r} not found", "template.ExecError"))
        try:
            result = self._templates[name]._execute(self._templates[name]._text, data, data)
            wr.write(result)
            return Ok(None)
        except Exception as e:
            return Err(GoError(str(e), "template.ExecError"))

    def _execute(self, text: str, data: Any, root: Any) -> str:
        """Execute the template with the given data."""
        result = []
        pos = 0

        for match in _ACTION_PATTERN.finditer(text):
            result.append(text[pos : match.start()])
            action = match.group(1).strip()
            output = self._execute_action(action, data, root)
            result.append(output)
            pos = match.end()

        result.append(text[pos:])
        return "".join(result)

    def _execute_action(self, action: str, data: Any, root: Any) -> str:
        """Execute a single action."""
        if action == ".":
            return self._format_value(data)

        if action.startswith("."):
            field_match = _FIELD_PATTERN.match(action)
            if field_match:
                fields = field_match.group(1).split(".")
                value = data
                for field in fields:
                    value = self._get_field(value, field)
                return self._format_value(value)

        if action.startswith("$"):
            return self._format_value(root)

        parts = action.split("|")
        if len(parts) > 1:
            value = self._execute_action(parts[0].strip(), data, root)
            for pipe in parts[1:]:
                pipe = pipe.strip()
                if pipe in self._funcs:
                    value = self._format_value(self._funcs[pipe](value))
            return value

        if " " in action:
            parts = action.split(None, 1)
            func_name = parts[0]
            if func_name in self._funcs:
                args = self._parse_args(parts[1] if len(parts) > 1 else "", data, root)
                return self._format_value(self._funcs[func_name](*args))

        if action in self._funcs:
            return self._format_value(self._funcs[action]())

        return ""

    def _get_field(self, obj: Any, field: str) -> Any:
        """Get a field from an object."""
        if isinstance(obj, dict):
            return obj.get(field, "")
        if hasattr(obj, field):
            val = getattr(obj, field)
            if callable(val):
                return val()
            return val
        return ""

    def _format_value(self, value: Any) -> str:
        """Format a value for output."""
        if value is None:
            return ""
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value)

    def _parse_args(self, args_str: str, data: Any, root: Any) -> list[Any]:
        """Parse arguments from a string."""
        args = []
        for arg in args_str.split():
            arg = arg.strip()
            if arg.startswith('"') and arg.endswith('"'):
                args.append(arg[1:-1])
            elif arg.startswith("."):
                args.append(self._execute_action(arg, data, root))
            elif arg == "$":
                args.append(root)
            else:
                try:
                    args.append(str(int(arg)))
                except ValueError:
                    try:
                        args.append(str(float(arg)))
                    except ValueError:
                        args.append(arg)
        return args

    def Lookup(self, name: str) -> Template | None:
        """Lookup returns the template with the given name."""
        return self._templates.get(name)

    def Templates(self) -> list[Template]:
        """Templates returns the list of templates associated with this template."""
        return list(self._templates.values())

    def Clone(self) -> Result[Template, GoError]:
        """Clone returns a duplicate of the template."""
        try:
            t = Template(self._name)
            t._text = self._text
            t._funcs = self._funcs.copy()
            t._templates = dict(self._templates.items())
            t._parsed = self._parsed
            return Ok(t)
        except Exception as e:
            return Err(GoError(str(e), "template.Error"))

    def DefinedTemplates(self) -> str:
        """DefinedTemplates returns a string listing the defined templates."""
        names = [f'"{name}"' for name in self._templates]
        if names:
            return "; defined templates are: " + ", ".join(names)
        return ""

    def New(self, name: str) -> Template:
        """New creates a new template with the given name."""
        t = Template(name)
        t._funcs = self._funcs
        self._templates[name] = t
        return t

    def Option(self, *opts: str) -> Template:
        """Option sets options for the template."""
        return self


def New(name: str) -> Template:
    """New allocates a new template with the given name."""
    return Template(name)


def Must(t: Result[Template, GoError]) -> Template:
    """Must panics if err is non-nil."""
    if t.is_err():
        raise RuntimeError(str(t.err()))
    return t.unwrap()


def ParseFiles(*filenames: str) -> Result[Template, GoError]:
    """Creates a new Template and parses template definitions from the named files."""
    if not filenames:
        return Err(GoError("no files named", "template.ParseError"))

    name = filenames[0].rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
    t = Template(name)
    return t.ParseFiles(*filenames)


def ParseGlob(pattern: str) -> Result[Template, GoError]:
    """Creates a new Template and parses template definitions from files matching the pattern."""
    import glob

    files = glob.glob(pattern)
    if not files:
        return Err(GoError(f"pattern matches no files: {pattern}", "template.ParseError"))
    return ParseFiles(*files)
