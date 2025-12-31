"""Go encoding/xml package bindings - XML encoding and decoding.

This module provides Python bindings for Go's encoding/xml package.

Example:
    >>> from goated.std import xml
    >>>
    >>> xml.Marshal({"name": "Go", "version": "1.21"})
    Ok('<root><name>Go</name><version>1.21</version></root>')

"""

from __future__ import annotations

import html
import xml.etree.ElementTree as ET
from typing import Any
from xml.dom import minidom

from goated.result import Err, GoError, Ok, Result

__all__ = [
    "Marshal",
    "MarshalIndent",
    "Unmarshal",
    "Escape",
    "EscapeText",
    "HTMLEscape",
    "Decoder",
    "Encoder",
    "Token",
    "StartElement",
    "EndElement",
    "CharData",
    "Comment",
    "ProcInst",
    "Directive",
]


# Token types
class Token:
    """Base class for XML tokens."""

    pass


class StartElement(Token):
    """Represents an XML start element."""

    def __init__(self, name: str, attr: dict[str, str] | None = None):
        self.Name = name
        self.Attr = attr or {}

    def __repr__(self) -> str:
        return f"StartElement({self.Name!r}, {self.Attr!r})"


class EndElement(Token):
    """Represents an XML end element."""

    def __init__(self, name: str) -> None:
        self.Name = name

    def __repr__(self) -> str:
        return f"EndElement({self.Name!r})"


class CharData(Token):
    """Represents XML character data (text content)."""

    def __init__(self, data: str) -> None:
        self.Data = data

    def __repr__(self) -> str:
        return f"CharData({self.Data!r})"


class Comment(Token):
    """Represents an XML comment."""

    def __init__(self, data: str) -> None:
        self.Data = data

    def __repr__(self) -> str:
        return f"Comment({self.Data!r})"


class ProcInst(Token):
    """Represents an XML processing instruction."""

    def __init__(self, target: str, inst: str) -> None:
        self.Target = target
        self.Inst = inst

    def __repr__(self) -> str:
        return f"ProcInst({self.Target!r}, {self.Inst!r})"


class Directive(Token):
    """Represents an XML directive."""

    def __init__(self, data: str) -> None:
        self.Data = data

    def __repr__(self) -> str:
        return f"Directive({self.Data!r})"


def _dict_to_xml(d: Any, root_name: str = "root") -> ET.Element:
    """Convert a dictionary to an XML Element."""
    root = ET.Element(root_name)

    if isinstance(d, dict):
        for key, value in d.items():
            child = _dict_to_xml(value, str(key))
            root.append(child)
    elif isinstance(d, (list, tuple)):
        for _i, item in enumerate(d):
            child = _dict_to_xml(item, "item")
            root.append(child)
    else:
        root.text = str(d) if d is not None else ""

    return root


def _xml_to_dict(element: ET.Element) -> Any:
    """Convert an XML Element to a dictionary."""
    result: dict[str, Any] = {}

    # Handle attributes
    if element.attrib:
        result["@attributes"] = dict(element.attrib)

    # Handle child elements
    children = list(element)
    if children:
        child_dict: dict[str, list[Any]] = {}
        for child in children:
            child_data = _xml_to_dict(child)
            if child.tag in child_dict:
                child_dict[child.tag].append(child_data)
            else:
                child_dict[child.tag] = [child_data]

        # Simplify single-item lists
        for key, value in child_dict.items():
            if len(value) == 1:
                result[key] = value[0]
            else:
                result[key] = value
    elif element.text and element.text.strip():
        # If no children but has text, return just the text
        if not result:
            return element.text.strip()
        result["#text"] = element.text.strip()

    return result if result else ""


def Marshal(v: Any) -> Result[str, GoError]:
    """Returns the XML encoding of v."""
    try:
        if isinstance(v, str):
            return Ok(Escape(v))

        root = _dict_to_xml(v)
        return Ok(ET.tostring(root, encoding="unicode"))
    except Exception as e:
        return Err(GoError(str(e), "xml.MarshalError"))


def MarshalIndent(v: Any, prefix: str = "", indent: str = "  ") -> Result[str, GoError]:
    """Returns the indented XML encoding of v."""
    try:
        if isinstance(v, str):
            return Ok(Escape(v))

        root = _dict_to_xml(v)
        rough_string = ET.tostring(root, encoding="unicode")

        # Parse and re-format with minidom for pretty printing
        dom = minidom.parseString(rough_string)
        pretty = dom.toprettyxml(indent=indent)

        # Remove the XML declaration
        lines = pretty.split("\n")
        if lines[0].startswith("<?xml"):
            lines = lines[1:]

        # Add prefix to each line
        if prefix:
            lines = [prefix + line for line in lines]

        # Remove empty lines
        lines = [line for line in lines if line.strip()]

        return Ok("\n".join(lines))
    except Exception as e:
        return Err(GoError(str(e), "xml.MarshalError"))


def Unmarshal(data: str | bytes) -> Result[Any, GoError]:
    """Parses the XML-encoded data and returns the result."""
    try:
        if isinstance(data, bytes):
            data = data.decode("utf-8")

        root = ET.fromstring(data)
        result = _xml_to_dict(root)

        # Wrap in root element name
        return Ok({root.tag: result})
    except ET.ParseError as e:
        return Err(GoError(str(e), "xml.SyntaxError"))
    except Exception as e:
        return Err(GoError(str(e), "xml.UnmarshalError"))


def Escape(s: str) -> str:
    """Escapes special XML characters."""
    return html.escape(s, quote=True)


def EscapeText(s: str) -> bytes:
    """Escapes special XML characters and returns bytes."""
    return Escape(s).encode("utf-8")


def HTMLEscape(s: str) -> str:
    """Escapes special characters for use in HTML."""
    return html.escape(s, quote=True)


class Decoder:
    """A Decoder reads and decodes XML from an input stream."""

    def __init__(self, data: str | bytes) -> None:
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        self._data = data
        self._iter: Any = None
        self._root: Any = None

    def Decode(self) -> Result[Any, GoError]:
        """Reads the next XML-encoded value and decodes it."""
        return Unmarshal(self._data)

    def Token(self) -> Result[Token | None, GoError]:
        """Returns the next XML token in the input stream."""
        try:
            if self._iter is None:
                self._iter = ET.iterparse(
                    __import__("io").StringIO(self._data), events=("start", "end")
                )

            try:
                event, elem = next(self._iter)
                if event == "start":
                    return Ok(StartElement(elem.tag, dict(elem.attrib)))
                else:
                    return Ok(EndElement(elem.tag))
            except StopIteration:
                return Ok(None)
        except Exception as e:
            return Err(GoError(str(e), "xml.SyntaxError"))


class Encoder:
    """An Encoder writes XML to an output stream."""

    def __init__(self) -> None:
        self._output: list[str] = []
        self.Indent = ""

    def Encode(self, v: Any) -> Result[None, GoError]:
        """Writes the XML encoding of v."""
        result = MarshalIndent(v, indent=self.Indent) if self.Indent else Marshal(v)

        if result.is_err():
            err = result.err()
            assert err is not None
            return Err(err)

        self._output.append(result.unwrap())
        return Ok(None)

    def Flush(self) -> Result[str, GoError]:
        """Returns the accumulated output."""
        return Ok("".join(self._output))
