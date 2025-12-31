from __future__ import annotations

import html as _html

__all__ = [
    "EscapeString",
    "UnescapeString",
]


def EscapeString(s: str) -> str:
    """EscapeString escapes special characters like "<" to become "&lt;".
    It escapes only five such characters: <, >, &, ' and ".
    """
    return _html.escape(s, quote=True)


def UnescapeString(s: str) -> str:
    """UnescapeString unescapes entities like "&lt;" to become "<".
    It unescapes a larger range of entities than EscapeString escapes.
    """
    return _html.unescape(s)
