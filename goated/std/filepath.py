"""Go filepath package bindings - Auto-generated.

This module provides Python bindings for Go's path/filepath package.
OS-aware path operations (uses os.sep for separators).
"""

from __future__ import annotations

import fnmatch
import os
import os.path as _ospath
from collections.abc import Callable

from goated._core import get_lib, is_library_available
from goated.result import Err, GoError, Ok, Result

__all__ = [
    "Abs",
    "Base",
    "Clean",
    "Dir",
    "EvalSymlinks",
    "Ext",
    "FromSlash",
    "Glob",
    "HasPrefix",
    "IsAbs",
    "IsLocal",
    "Join",
    "Localize",
    "Match",
    "Rel",
    "Split",
    "SplitList",
    "ToSlash",
    "VolumeName",
    "Walk",
    "WalkDir",
    # Constants
    "Separator",
    "ListSeparator",
]

# OS-specific separators
Separator = os.sep
ListSeparator = os.pathsep


def _encode(s: str) -> bytes:
    return s.encode("utf-8")


def _decode(b: bytes | None) -> str:
    if b is None:
        return ""
    return b.decode("utf-8")


import ctypes

_fn_configured: set[str] = set()


def _configure_fn(lib: object, name: str, argtypes: list[type], restype: type) -> None:
    if name in _fn_configured:
        return
    fn = getattr(lib, name)
    fn.argtypes = argtypes
    fn.restype = restype
    _fn_configured.add(name)


def Abs(path_: str) -> Result[str, GoError]:
    """Abs returns an absolute representation of path.
    If the path is not absolute it will be joined with the current
    working directory to turn it into an absolute path. The absolute
    path name for a given file is not guaranteed to be unique.
    Abs calls [Clean] on the result.
    """
    if not is_library_available():
        # Pure Python fallback
        try:
            return Ok(_ospath.abspath(path_))
        except Exception as e:
            return Err(GoError(str(e)))

    lib = get_lib()
    _configure_fn(
        lib,
        "goated_filepath_Abs",
        [ctypes.c_char_p, ctypes.POINTER(ctypes.c_char_p)],
        ctypes.c_char_p,
    )
    err_out = ctypes.c_char_p()
    result = lib.goated_filepath_Abs(_encode(path_), ctypes.byref(err_out))

    if err_out.value:
        return Err(GoError(_decode(err_out.value)))
    return Ok(_decode(result))


def Base(path_: str) -> str:
    """Base returns the last element of path.
    Trailing path separators are removed before extracting the last element.
    If the path is empty, Base returns ".".
    If the path consists entirely of separators, Base returns a single separator.
    """
    if not is_library_available():
        # Pure Python fallback
        if not path_:
            return "."
        # Use os.path.basename but handle edge cases
        result = _ospath.basename(path_.rstrip(os.sep))
        if not result:
            return os.sep
        return result

    lib = get_lib()
    _configure_fn(lib, "goated_filepath_Base", [ctypes.c_char_p], ctypes.c_char_p)
    result = lib.goated_filepath_Base(_encode(path_))
    return _decode(result)


def Clean(path_: str) -> str:
    """Clean returns the shortest path name equivalent to path
    by purely lexical processing.
    """
    if not is_library_available():
        # Pure Python fallback
        if not path_:
            return "."
        result = _ospath.normpath(path_)
        return result if result else "."

    lib = get_lib()
    _configure_fn(lib, "goated_filepath_Clean", [ctypes.c_char_p], ctypes.c_char_p)
    result = lib.goated_filepath_Clean(_encode(path_))
    return _decode(result)


def Dir(path_: str) -> str:
    """Dir returns all but the last element of path, typically the path's directory.
    After dropping the final element, Dir calls [Clean] on the path and trailing
    slashes are removed.
    If the path is empty, Dir returns ".".
    If the path consists entirely of separators, Dir returns a single separator.
    The returned path does not end in a separator unless it is the root directory.
    """
    if not is_library_available():
        # Pure Python fallback
        if not path_:
            return "."
        result = _ospath.dirname(path_.rstrip(os.sep))
        if not result:
            if path_.startswith(os.sep):
                return os.sep
            return "."
        return Clean(result)

    lib = get_lib()
    _configure_fn(lib, "goated_filepath_Dir", [ctypes.c_char_p], ctypes.c_char_p)
    result = lib.goated_filepath_Dir(_encode(path_))
    return _decode(result)


def EvalSymlinks(path_: str) -> Result[str, GoError]:
    """EvalSymlinks returns the path name after the evaluation of any symbolic
    links.
    If path is relative the result will be relative to the current directory,
    unless one of the components is an absolute symbolic link.
    EvalSymlinks calls [Clean] on the result.
    """
    if not is_library_available():
        # Pure Python fallback
        try:
            resolved = _ospath.realpath(path_)
            # Check if path exists (Go returns error for non-existent paths)
            if not _ospath.exists(resolved):
                return Err(GoError(f"lstat {path_}: no such file or directory"))
            return Ok(resolved)
        except Exception as e:
            return Err(GoError(str(e)))

    lib = get_lib()
    _configure_fn(
        lib,
        "goated_filepath_EvalSymlinks",
        [ctypes.c_char_p, ctypes.POINTER(ctypes.c_char_p)],
        ctypes.c_char_p,
    )
    err_out = ctypes.c_char_p()
    result = lib.goated_filepath_EvalSymlinks(_encode(path_), ctypes.byref(err_out))

    if err_out.value:
        return Err(GoError(_decode(err_out.value)))
    return Ok(_decode(result))


def Ext(path_: str) -> str:
    """Ext returns the file name extension used by path.
    The extension is the suffix beginning at the final dot
    in the final element of path; it is empty if there is
    no dot.
    """
    if not is_library_available():
        # Pure Python fallback
        # Get the base name first
        base = Base(path_)
        i = base.rfind(".")
        if i < 0:
            return ""
        return base[i:]

    lib = get_lib()
    _configure_fn(lib, "goated_filepath_Ext", [ctypes.c_char_p], ctypes.c_char_p)
    result = lib.goated_filepath_Ext(_encode(path_))
    return _decode(result)


def FromSlash(path_: str) -> str:
    """FromSlash returns the result of replacing each slash ('/') character
    in path with a separator character. Multiple slashes are replaced
    by multiple separators.
    """
    if not is_library_available():
        # Pure Python fallback
        if os.sep == "/":
            return path_
        return path_.replace("/", os.sep)

    lib = get_lib()
    _configure_fn(lib, "goated_filepath_FromSlash", [ctypes.c_char_p], ctypes.c_char_p)
    result = lib.goated_filepath_FromSlash(_encode(path_))
    return _decode(result)


def Glob(pattern: str) -> Result[list[str] | None, GoError]:
    """Glob returns the names of all files matching pattern or nil
    if there is no matching file.
    """
    # Pure Python implementation using glob module
    import glob as _glob

    try:
        matches = _glob.glob(pattern)
        return Ok(matches if matches else None)
    except Exception as e:
        return Err(GoError(str(e)))


def HasPrefix(p: str, prefix: str) -> bool:
    """HasPrefix exists for historical compatibility and should not be used.

    Deprecated: HasPrefix does not respect path boundaries and
    does not ignore case when required.
    """
    if not is_library_available():
        # Pure Python fallback
        return p.startswith(prefix)

    lib = get_lib()
    _configure_fn(
        lib, "goated_filepath_HasPrefix", [ctypes.c_char_p, ctypes.c_char_p], ctypes.c_bool
    )
    result = lib.goated_filepath_HasPrefix(_encode(p), _encode(prefix))
    return bool(result)


def IsAbs(path_: str) -> bool:
    """IsAbs reports whether the path is absolute."""
    if not is_library_available():
        # Pure Python fallback
        return _ospath.isabs(path_)

    lib = get_lib()
    _configure_fn(lib, "goated_filepath_IsAbs", [ctypes.c_char_p], ctypes.c_bool)
    result = lib.goated_filepath_IsAbs(_encode(path_))
    return bool(result)


def IsLocal(path_: str) -> bool:
    """IsLocal reports whether path, using lexical analysis only, has all of these properties:

      - is within the subtree rooted at the directory in which path is evaluated
      - is not an absolute path
      - is not empty
      - on Windows, is not a reserved name such as "NUL"

    If IsLocal(path) returns true, then
    Join(base, path) will always produce a path contained within base and
    Clean(path) will always produce an unrooted path with no ".." path elements.
    """
    if not is_library_available():
        # Pure Python fallback
        if not path_:
            return False
        if _ospath.isabs(path_):
            return False

        # Check for .. that would escape
        cleaned = Clean(path_)
        if cleaned.startswith(".."):
            return False

        # Windows reserved names
        if os.name == "nt":
            reserved = {
                "CON",
                "PRN",
                "AUX",
                "NUL",
                "COM1",
                "COM2",
                "COM3",
                "COM4",
                "COM5",
                "COM6",
                "COM7",
                "COM8",
                "COM9",
                "LPT1",
                "LPT2",
                "LPT3",
                "LPT4",
                "LPT5",
                "LPT6",
                "LPT7",
                "LPT8",
                "LPT9",
            }
            base = Base(path_).upper()
            # Remove extension for check
            if "." in base:
                base = base.split(".")[0]
            if base in reserved:
                return False

        return True

    lib = get_lib()
    _configure_fn(lib, "goated_filepath_IsLocal", [ctypes.c_char_p], ctypes.c_bool)
    result = lib.goated_filepath_IsLocal(_encode(path_))
    return bool(result)


def Join(*elem: str) -> str:
    """Join joins any number of path elements into a single path,
    separating them with an OS specific Separator. Empty elements
    are ignored. The result is Cleaned. However, if the argument
    list is empty or all its elements are empty, Join returns
    an empty string.
    """
    # Pure Python implementation
    parts = [e for e in elem if e]
    if not parts:
        return ""
    return Clean(_ospath.join(*parts))


def Localize(path_: str) -> Result[str, GoError]:
    """Localize converts a slash-separated path into an operating system path.
    The input path must be a valid path as reported by [io/fs.ValidPath].
    """
    if not is_library_available():
        # Pure Python fallback
        # Check for invalid patterns
        if not path_:
            return Err(GoError("invalid path"))
        if path_.startswith("/"):
            return Err(GoError("path is absolute"))

        # Check for .. elements
        parts = path_.split("/")
        for part in parts:
            if part == "..":
                return Err(GoError("path contains '..'"))
            if not part and parts.index(part) != len(parts) - 1:
                # Empty part means double slash
                continue

        # On Windows, check for backslash in path
        if os.name == "nt" and "\\" in path_:
            return Err(GoError("path contains backslash"))

        return Ok(FromSlash(path_))

    lib = get_lib()
    _configure_fn(
        lib,
        "goated_filepath_Localize",
        [ctypes.c_char_p, ctypes.POINTER(ctypes.c_char_p)],
        ctypes.c_char_p,
    )
    err_out = ctypes.c_char_p()
    result = lib.goated_filepath_Localize(_encode(path_), ctypes.byref(err_out))

    if err_out.value:
        return Err(GoError(_decode(err_out.value)))
    return Ok(_decode(result))


def Match(pattern: str, name: str) -> Result[bool, GoError]:
    """Match reports whether name matches the shell file name pattern."""
    if not is_library_available():
        # Pure Python fallback using fnmatch
        try:
            # Validate pattern for Go compatibility - check for unclosed brackets
            i = 0
            while i < len(pattern):
                if pattern[i] == "[":
                    # Find closing bracket
                    j = i + 1
                    if j < len(pattern) and pattern[j] in "!^":
                        j += 1
                    if j < len(pattern) and pattern[j] == "]":
                        j += 1
                    while j < len(pattern) and pattern[j] != "]":
                        j += 1
                    if j >= len(pattern):
                        return Err(GoError("syntax error in pattern"))
                    i = j + 1
                else:
                    i += 1

            matched = fnmatch.fnmatch(name, pattern)
            return Ok(matched)
        except Exception:
            return Err(GoError("syntax error in pattern"))

    lib = get_lib()
    _configure_fn(
        lib,
        "goated_filepath_Match",
        [ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_char_p)],
        ctypes.c_bool,
    )
    err_out = ctypes.c_char_p()
    result = lib.goated_filepath_Match(_encode(pattern), _encode(name), ctypes.byref(err_out))

    if err_out.value:
        return Err(GoError(_decode(err_out.value)))
    return Ok(result)


def Rel(basepath: str, targpath: str) -> Result[str, GoError]:
    """Rel returns a relative path that is lexically equivalent to targpath when
    joined to basepath with an intervening separator.
    """
    if not is_library_available():
        # Pure Python fallback
        try:
            result = _ospath.relpath(targpath, basepath)
            return Ok(result)
        except ValueError as e:
            # On Windows, relpath fails if paths are on different drives
            return Err(GoError(str(e)))

    lib = get_lib()
    _configure_fn(
        lib,
        "goated_filepath_Rel",
        [ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_char_p)],
        ctypes.c_char_p,
    )
    err_out = ctypes.c_char_p()
    result = lib.goated_filepath_Rel(_encode(basepath), _encode(targpath), ctypes.byref(err_out))

    if err_out.value:
        return Err(GoError(_decode(err_out.value)))
    return Ok(_decode(result))


def Split(path_: str) -> tuple[str, str]:
    """Split splits path immediately following the final Separator,
    separating it into a directory and file name component.
    If there is no Separator in path, Split returns an empty dir
    and file set to path.
    The returned values have the property that path = dir+file.
    """
    # Pure Python implementation
    dir_part, file_part = _ospath.split(path_)
    # Ensure dir ends with separator if non-empty
    if dir_part and not dir_part.endswith(os.sep):
        dir_part += os.sep
    return dir_part, file_part


def SplitList(path_: str) -> list[str]:
    """SplitList splits a list of paths joined by the OS-specific ListSeparator,
    usually found in PATH or GOPATH environment variables.
    """
    # Pure Python implementation
    if not path_:
        return []
    return path_.split(os.pathsep)


def ToSlash(path_: str) -> str:
    """ToSlash returns the result of replacing each separator character
    in path with a slash ('/') character. Multiple separators are
    replaced by multiple slashes.
    """
    if not is_library_available():
        # Pure Python fallback
        if os.sep == "/":
            return path_
        return path_.replace(os.sep, "/")

    lib = get_lib()
    _configure_fn(lib, "goated_filepath_ToSlash", [ctypes.c_char_p], ctypes.c_char_p)
    result = lib.goated_filepath_ToSlash(_encode(path_))
    return _decode(result)


def VolumeName(path_: str) -> str:
    r"""VolumeName returns leading volume name.
    Given "C:\\foo\\bar" it returns "C:" on Windows.
    Given "\\\\host\\share\\foo" it returns "\\\\host\\share".
    On other platforms it returns "".
    """
    if not is_library_available():
        # Pure Python fallback
        if os.name != "nt":
            return ""

        # Windows volume name extraction
        if len(path_) >= 2 and path_[1] == ":":
            return path_[:2]

        # UNC path
        if path_.startswith("\\\\") or path_.startswith("//"):
            # Find the share part
            sep = "\\" if "\\" in path_[2:] else "/"
            parts = path_[2:].split(sep, 2)
            if len(parts) >= 2:
                return path_[:2] + parts[0] + sep + parts[1]

        return ""

    lib = get_lib()
    _configure_fn(lib, "goated_filepath_VolumeName", [ctypes.c_char_p], ctypes.c_char_p)
    result = lib.goated_filepath_VolumeName(_encode(path_))
    return _decode(result)


WalkFunc = Callable[[str, os.stat_result | None, Exception | None], Exception | None]


def Walk(root: str, fn: WalkFunc) -> Result[None, GoError]:
    """Walk walks the file tree rooted at root."""
    try:
        for dirpath, dirnames, filenames in os.walk(root):
            # Call fn for the directory itself
            try:
                info = os.stat(dirpath)
                err = fn(dirpath, info, None)
                if err:
                    if str(err) == "skip directory":
                        dirnames.clear()  # Skip subdirectories
                        continue
                    elif str(err) == "skip all":
                        return Ok(None)
                    return Err(GoError(str(err)))
            except OSError as e:
                err = fn(dirpath, None, e)
                if err:
                    return Err(GoError(str(err)))

            # Call fn for each file
            for filename in filenames:
                filepath = Join(dirpath, filename)
                try:
                    info = os.stat(filepath)
                    err = fn(filepath, info, None)
                    if err:
                        if str(err) == "skip all":
                            return Ok(None)
                        return Err(GoError(str(err)))
                except OSError as e:
                    err = fn(filepath, None, e)
                    if err:
                        return Err(GoError(str(err)))

        return Ok(None)
    except Exception as e:
        return Err(GoError(str(e)))


# Sentinel errors for Walk
class SkipDir(Exception):
    """SkipDir is used as a return value from WalkFuncs to indicate that
    the directory named in the call is to be skipped.
    """

    def __str__(self) -> str:
        return "skip directory"


class SkipAll(Exception):
    """SkipAll is used as a return value from WalkFuncs to indicate that
    all remaining files and directories are to be skipped.
    """

    def __str__(self) -> str:
        return "skip all"


WalkDirFunc = Callable[[str, "_DirEntry | None", Exception | None], Exception | None]


def WalkDir(root: str, fn: WalkDirFunc) -> Result[None, GoError]:
    """WalkDir walks the file tree rooted at root."""
    try:
        for dirpath, dirnames, filenames in os.walk(root):
            # Process directory
            try:
                err = fn(dirpath, _DirEntry(dirpath, is_dir=True), None)
                if err:
                    if isinstance(err, SkipDir):
                        dirnames.clear()
                        continue
                    elif isinstance(err, SkipAll):
                        return Ok(None)
                    return Err(GoError(str(err)))
            except Exception as e:
                err = fn(dirpath, None, e)
                if err:
                    return Err(GoError(str(err)))

            # Process files
            for filename in filenames:
                filepath = Join(dirpath, filename)
                try:
                    err = fn(filepath, _DirEntry(filepath, is_dir=False), None)
                    if err:
                        if isinstance(err, SkipAll):
                            return Ok(None)
                        return Err(GoError(str(err)))
                except Exception as e:
                    err = fn(filepath, None, e)
                    if err:
                        return Err(GoError(str(err)))

        return Ok(None)
    except Exception as e:
        return Err(GoError(str(e)))


class _DirEntry:
    """A simple DirEntry-like object for WalkDir."""

    def __init__(self, path: str, is_dir: bool = False) -> None:
        self._path = path
        self._is_dir = is_dir
        self._stat_cache: os.stat_result | None = None

    def name(self) -> str:
        return Base(self._path)

    def is_dir(self) -> bool:
        return self._is_dir

    def is_file(self) -> bool:
        return not self._is_dir

    def is_symlink(self) -> bool:
        return _ospath.islink(self._path)

    def stat(self) -> os.stat_result:
        if self._stat_cache is None:
            self._stat_cache = os.stat(self._path)
        return self._stat_cache
