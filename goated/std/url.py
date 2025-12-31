"""Go net/url package bindings - URL parsing and manipulation.

This module provides Python bindings for Go's net/url package.

Example:
    >>> from goated.std import url
    >>>
    >>> u = url.Parse("https://user:pass@example.com:8080/path?q=1#frag")
    >>> u.unwrap().Host
    'example.com:8080'
    >>> url.QueryEscape("hello world")
    'hello+world'

"""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import (
    parse_qs,
    quote,
    quote_plus,
    unquote,
    unquote_plus,
    urlencode,
    urlparse,
)

from goated.result import Err, GoError, Ok, Result

__all__ = [
    "URL",
    "Values",
    "Parse",
    "ParseRequestURI",
    "QueryEscape",
    "QueryUnescape",
    "PathEscape",
    "PathUnescape",
    "JoinPath",
]


@dataclass
class Userinfo:
    """Userinfo contains username and password information."""

    _username: str = ""
    _password: str = ""
    _password_set: bool = False

    def Username(self) -> str:
        """Returns the username."""
        return self._username

    def Password(self) -> tuple[str, bool]:
        """Returns the password and whether it is set."""
        return self._password, self._password_set

    def String(self) -> str:
        """Returns the encoded userinfo."""
        if self._password_set:
            return f"{quote(self._username, safe='')}:{quote(self._password, safe='')}"
        return quote(self._username, safe="")


def User(username: str) -> Userinfo:
    """Returns a Userinfo with the provided username."""
    return Userinfo(_username=username)


def UserPassword(username: str, password: str) -> Userinfo:
    """Returns a Userinfo with the provided username and password."""
    return Userinfo(_username=username, _password=password, _password_set=True)


class Values(dict[str, list[str]]):
    """Values maps a string key to a list of values.
    It is typically used for query parameters and form values.
    """

    def Get(self, key: str) -> str:
        """Gets the first value associated with the given key."""
        values = self.get(key, [])
        if values:
            return str(values[0])
        return ""

    def Set(self, key: str, value: str) -> None:
        """Sets the key to value. It replaces any existing values."""
        self[key] = [value]

    def Add(self, key: str, value: str) -> None:
        """Adds the value to key. It appends to any existing values."""
        if key in self:
            self[key].append(value)
        else:
            self[key] = [value]

    def Del(self, key: str) -> None:
        """Deletes the values associated with key."""
        self.pop(key, None)

    def Has(self, key: str) -> bool:
        """Checks whether a given key is set."""
        return key in self

    def Encode(self) -> str:
        """Encodes the values into URL encoded form."""
        items = []
        for key in sorted(self.keys()):
            for value in self[key]:
                items.append((key, value))
        return urlencode(items)


def ParseQuery(query: str) -> Result[Values, GoError]:
    """Parses a URL query string into a Values dict."""
    try:
        parsed = parse_qs(query, keep_blank_values=True)
        values = Values()
        for key, val_list in parsed.items():
            values[key] = val_list
        return Ok(values)
    except Exception as e:
        return Err(GoError(str(e), "url.ParseError"))


@dataclass
class URL:
    """A URL represents a parsed URL.

    The general form is:
        [scheme:][//[userinfo@]host][/path][?query][#fragment]
    """

    Scheme: str = ""
    Opaque: str = ""  # encoded opaque data
    User: Userinfo | None = None  # username and password information
    Host: str = ""  # host or host:port
    Path: str = ""  # path (relative paths may omit leading slash)
    RawPath: str = ""  # encoded path hint
    RawQuery: str = ""  # encoded query values, without '?'
    Fragment: str = ""  # fragment for references, without '#'
    RawFragment: str = ""  # encoded fragment hint

    def EscapedPath(self) -> str:
        """Returns the escaped form of Path."""
        if self.RawPath:
            return self.RawPath
        return quote(self.Path, safe="/:@")

    def EscapedFragment(self) -> str:
        """Returns the escaped form of Fragment."""
        if self.RawFragment:
            return self.RawFragment
        return quote(self.Fragment, safe="/:@")

    def Hostname(self) -> str:
        """Returns the host without port."""
        host = self.Host
        if ":" in host:
            # Handle IPv6
            if host.startswith("["):
                bracket_idx = host.find("]")
                if bracket_idx != -1:
                    return host[1:bracket_idx]
            return host.rsplit(":", 1)[0]
        return host

    def Port(self) -> str:
        """Returns the port part of Host, without the leading colon."""
        host = self.Host
        if ":" in host:
            # Handle IPv6
            if host.startswith("["):
                bracket_idx = host.find("]")
                if bracket_idx != -1 and len(host) > bracket_idx + 2:
                    return host[bracket_idx + 2 :]
                return ""
            return host.rsplit(":", 1)[1]
        return ""

    def Query(self) -> Values:
        """Parses RawQuery and returns the corresponding values."""
        result = ParseQuery(self.RawQuery)
        if result.is_ok():
            return result.unwrap()
        return Values()

    def RequestURI(self) -> str:
        """Returns the encoded path?query or opaque?query string."""
        result = self.EscapedPath()
        if self.RawQuery:
            result += "?" + self.RawQuery
        return result

    def String(self) -> str:
        """Reassembles the URL into a valid URL string."""
        result = ""

        if self.Scheme:
            result += self.Scheme + ":"

        if self.Opaque:
            result += self.Opaque
        else:
            if self.Scheme or self.Host or self.User:
                result += "//"
                if self.User:
                    result += self.User.String() + "@"
                result += self.Host
            result += self.EscapedPath()

        if self.RawQuery:
            result += "?" + self.RawQuery

        if self.Fragment:
            result += "#" + self.EscapedFragment()

        return result

    def ResolveReference(self, ref: URL) -> URL:
        """Resolves a URI reference to an absolute URI."""
        # Simplified implementation
        if ref.Scheme:
            return URL(
                Scheme=ref.Scheme,
                Host=ref.Host,
                Path=ref.Path,
                RawQuery=ref.RawQuery,
                Fragment=ref.Fragment,
            )

        if ref.Host:
            return URL(
                Scheme=self.Scheme,
                Host=ref.Host,
                Path=ref.Path,
                RawQuery=ref.RawQuery,
                Fragment=ref.Fragment,
            )

        if not ref.Path:
            return URL(
                Scheme=self.Scheme,
                Host=self.Host,
                Path=self.Path,
                RawQuery=ref.RawQuery if ref.RawQuery else self.RawQuery,
                Fragment=ref.Fragment,
            )

        path = ref.Path
        if not path.startswith("/"):
            # Relative path
            base_path = self.Path
            base_path = base_path.rsplit("/", 1)[0] + "/" if "/" in base_path else "/"
            path = base_path + path

        return URL(
            Scheme=self.Scheme,
            Host=self.Host,
            Path=path,
            RawQuery=ref.RawQuery,
            Fragment=ref.Fragment,
        )

    def IsAbs(self) -> bool:
        """Reports whether the URL is absolute."""
        return self.Scheme != ""

    def Redacted(self) -> str:
        """Returns the URL string with password redacted."""
        if self.User and self.User._password_set:
            u = URL(
                Scheme=self.Scheme,
                User=Userinfo(_username=self.User._username, _password="xxxxx", _password_set=True),
                Host=self.Host,
                Path=self.Path,
                RawPath=self.RawPath,
                RawQuery=self.RawQuery,
                Fragment=self.Fragment,
            )
            return u.String()
        return self.String()


def Parse(rawurl: str) -> Result[URL, GoError]:
    """Parses a raw url into a URL structure."""
    try:
        parsed = urlparse(rawurl)

        user = None
        if parsed.username:
            if parsed.password:
                user = UserPassword(parsed.username, parsed.password)
            else:
                user = User(parsed.username)

        return Ok(
            URL(
                Scheme=parsed.scheme,
                User=user,
                Host=parsed.netloc.split("@")[-1] if parsed.netloc else "",
                Path=parsed.path,
                RawQuery=parsed.query,
                Fragment=parsed.fragment,
            )
        )
    except Exception as e:
        return Err(GoError(str(e), "url.ParseError"))


def ParseRequestURI(rawurl: str) -> Result[URL, GoError]:
    """Parses a raw url into a URL structure, for request URIs."""
    result = Parse(rawurl)
    if result.is_err():
        return result

    url = result.unwrap()
    if url.Fragment:
        return Err(GoError("invalid URL: fragment not allowed", "url.ParseError"))

    return Ok(url)


def QueryEscape(s: str) -> str:
    """Escapes the string so it can be safely placed inside a URL query."""
    return quote_plus(s)


def QueryUnescape(s: str) -> Result[str, GoError]:
    """Performs the inverse transformation of QueryEscape."""
    try:
        return Ok(unquote_plus(s))
    except Exception as e:
        return Err(GoError(str(e), "url.EscapeError"))


def PathEscape(s: str) -> str:
    """Escapes the string so it can be safely placed inside a URL path segment."""
    return quote(s, safe="")


def PathUnescape(s: str) -> Result[str, GoError]:
    """Performs the inverse transformation of PathEscape."""
    try:
        return Ok(unquote(s))
    except Exception as e:
        return Err(GoError(str(e), "url.EscapeError"))


def JoinPath(base: str, *elem: str) -> Result[str, GoError]:
    """Joins base URL with path elements."""
    try:
        result = Parse(base)
        if result.is_err():
            err = result.err()
            assert err is not None
            return Err(err)

        url = result.unwrap()
        path = url.Path
        for e in elem:
            path = path + e.lstrip("/") if path.endswith("/") else path + "/" + e.lstrip("/")

        url.Path = path
        return Ok(url.String())
    except Exception as e:
        return Err(GoError(str(e), "url.ParseError"))
