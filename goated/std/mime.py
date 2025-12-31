from __future__ import annotations

import mimetypes as _mimetypes

__all__ = [
    "TypeByExtension",
    "ExtensionsByType",
    "AddExtensionType",
    "FormatMediaType",
    "ParseMediaType",
]

_mimetypes.init()

_custom_types: dict[str, str] = {}
_custom_extensions: dict[str, list[str]] = {}


def TypeByExtension(ext: str) -> str:
    """TypeByExtension returns the MIME type associated with the file extension ext.
    The extension ext should begin with a leading dot, as in ".html".
    Returns empty string if extension is unknown.
    """
    if ext in _custom_types:
        return _custom_types[ext]

    mime_type, _ = _mimetypes.guess_type("file" + ext)
    return mime_type or ""


def ExtensionsByType(typ: str) -> list[str] | None:
    """ExtensionsByType returns the extensions known to be associated with the MIME type typ.
    Returns None if typ is not known.
    """
    base_type = typ.split(";")[0].strip().lower()

    if base_type in _custom_extensions:
        return _custom_extensions[base_type].copy()

    extensions = _mimetypes.guess_all_extensions(base_type)
    if extensions:
        return extensions
    return None


def AddExtensionType(ext: str, typ: str) -> Exception | None:
    """AddExtensionType sets the MIME type associated with the extension ext to typ.
    The extension should begin with a leading dot, as in ".html".
    """
    try:
        _custom_types[ext] = typ

        base_type = typ.split(";")[0].strip().lower()
        if base_type not in _custom_extensions:
            _custom_extensions[base_type] = []
        if ext not in _custom_extensions[base_type]:
            _custom_extensions[base_type].append(ext)

        return None
    except Exception as e:
        return e


def FormatMediaType(mediatype: str, params: dict[str, str] | None = None) -> str:
    """FormatMediaType serializes mediatype and the optional params into a media type string."""
    if not params:
        return mediatype

    result = mediatype
    for key, value in sorted(params.items()):
        if _needs_quoting(value):
            value = f'"{_escape_quotes(value)}"'
        result += f"; {key}={value}"

    return result


def ParseMediaType(v: str) -> tuple[str, dict[str, str], Exception | None]:
    """ParseMediaType parses a media type value and any optional parameters.
    Returns (mediatype, params, error).
    """
    try:
        parts = v.split(";")
        mediatype = parts[0].strip().lower()

        params: dict[str, str] = {}
        for part in parts[1:]:
            part = part.strip()
            if not part:
                continue

            if "=" not in part:
                continue

            key, value = part.split("=", 1)
            key = key.strip().lower()
            value = value.strip()

            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
                value = _unescape_quotes(value)

            params[key] = value

        return mediatype, params, None
    except Exception as e:
        return "", {}, e


def _needs_quoting(s: str) -> bool:
    """Check if a string needs quoting in a media type parameter."""
    for c in s:
        if c in ' \t"();/<=>?@[\\]':
            return True
        if ord(c) < 32 or ord(c) > 126:
            return True
    return False


def _escape_quotes(s: str) -> str:
    """Escape quotes and backslashes in a string."""
    return s.replace("\\", "\\\\").replace('"', '\\"')


def _unescape_quotes(s: str) -> str:
    """Unescape quotes and backslashes in a string."""
    result = []
    i = 0
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s):
            result.append(s[i + 1])
            i += 2
        else:
            result.append(s[i])
            i += 1
    return "".join(result)
