"""Go os package bindings - Operating system functionality.

This module provides Python bindings for Go's os package.

Example:
    >>> from goated.std import goos as os
    >>>
    >>> os.Getenv("HOME")
    '/home/user'
    >>> os.Getwd()
    Ok('/current/dir')

"""

from __future__ import annotations

import os as _os
import shutil
import stat
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import IO, Any

from goated.result import Err, GoError, Ok, Result

__all__ = [
    # Environment
    "Getenv",
    "LookupEnv",
    "Setenv",
    "Unsetenv",
    "Clearenv",
    "Environ",
    "ExpandEnv",
    "Getwd",
    "Chdir",
    "TempDir",
    "UserHomeDir",
    "UserCacheDir",
    "UserConfigDir",
    "Hostname",
    "Getpid",
    "Getppid",
    "Getuid",
    "Getgid",
    "Geteuid",
    "Getegid",
    # File operations
    "Create",
    "Open",
    "OpenFile",
    "ReadFile",
    "WriteFile",
    "Remove",
    "RemoveAll",
    "Rename",
    "Mkdir",
    "MkdirAll",
    "MkdirTemp",
    "CreateTemp",
    "Stat",
    "Lstat",
    "Chmod",
    "Chown",
    "Link",
    "Symlink",
    "Readlink",
    "ReadDir",
    "IsExist",
    "IsNotExist",
    "IsPermission",
    "Truncate",
    "SameFile",
    # Constants
    "O_RDONLY",
    "O_WRONLY",
    "O_RDWR",
    "O_APPEND",
    "O_CREATE",
    "O_EXCL",
    "O_SYNC",
    "O_TRUNC",
    "PathSeparator",
    "PathListSeparator",
    "DevNull",
    # Types
    "FileInfo",
    "FileMode",
    "DirEntry",
    "File",
    # Args
    "Args",
    "Exit",
    "Executable",
]

# Constants
O_RDONLY = _os.O_RDONLY
O_WRONLY = _os.O_WRONLY
O_RDWR = _os.O_RDWR
O_APPEND = _os.O_APPEND
O_CREATE = _os.O_CREAT
O_EXCL = _os.O_EXCL
O_SYNC = getattr(_os, "O_SYNC", 0)
O_TRUNC = _os.O_TRUNC

PathSeparator = _os.sep
PathListSeparator = _os.pathsep
DevNull = _os.devnull

# Args
Args = sys.argv.copy()


def Exit(code: int) -> None:
    """Causes the current program to exit with the given status code."""
    sys.exit(code)


def Executable() -> Result[str, GoError]:
    """Returns the path name for the executable that started the current process."""
    try:
        return Ok(sys.executable)
    except Exception as e:
        return Err(GoError(str(e), "os.PathError"))


# Environment functions
def Getenv(key: str) -> str:
    """Retrieves the value of the environment variable named by the key."""
    return _os.environ.get(key, "")


def LookupEnv(key: str) -> tuple[str, bool]:
    """Retrieves the value of the environment variable and reports whether it was present."""
    if key in _os.environ:
        return _os.environ[key], True
    return "", False


def Setenv(key: str, value: str) -> Result[None, GoError]:
    """Sets the value of the environment variable named by the key."""
    try:
        _os.environ[key] = value
        return Ok(None)
    except Exception as e:
        return Err(GoError(str(e), "os.Error"))


def Unsetenv(key: str) -> Result[None, GoError]:
    """Unsets a single environment variable."""
    try:
        _os.environ.pop(key, None)
        return Ok(None)
    except Exception as e:
        return Err(GoError(str(e), "os.Error"))


def Clearenv() -> None:
    """Deletes all environment variables."""
    _os.environ.clear()


def Environ() -> list[str]:
    """Returns a copy of strings representing the environment."""
    return [f"{k}={v}" for k, v in _os.environ.items()]


def ExpandEnv(s: str) -> str:
    """Replaces ${var} or $var in the string."""
    return _os.path.expandvars(s)


def Getwd() -> Result[str, GoError]:
    """Returns a rooted path name corresponding to the current directory."""
    try:
        return Ok(_os.getcwd())
    except Exception as e:
        return Err(GoError(str(e), "os.PathError"))


def Chdir(dir: str) -> Result[None, GoError]:
    """Changes the current working directory to the named directory."""
    try:
        _os.chdir(dir)
        return Ok(None)
    except FileNotFoundError:
        return Err(GoError(f"chdir {dir}: no such file or directory", "os.PathError"))
    except PermissionError:
        return Err(GoError(f"chdir {dir}: permission denied", "os.PathError"))
    except Exception as e:
        return Err(GoError(str(e), "os.PathError"))


def TempDir() -> str:
    """Returns the default directory to use for temporary files."""
    return tempfile.gettempdir()


def UserHomeDir() -> Result[str, GoError]:
    """Returns the current user's home directory."""
    try:
        home = Path.home()
        return Ok(str(home))
    except Exception as e:
        return Err(GoError(str(e), "os.Error"))


def UserCacheDir() -> Result[str, GoError]:
    """Returns the default root directory to use for user-specific cached data."""
    try:
        if sys.platform == "darwin":
            return Ok(str(Path.home() / "Library" / "Caches"))
        elif sys.platform == "win32":
            local_app_data = _os.environ.get("LOCALAPPDATA", "")
            if local_app_data:
                return Ok(local_app_data)
            return Err(GoError("LOCALAPPDATA not set", "os.Error"))
        else:
            xdg_cache = _os.environ.get("XDG_CACHE_HOME", "")
            if xdg_cache:
                return Ok(xdg_cache)
            return Ok(str(Path.home() / ".cache"))
    except Exception as e:
        return Err(GoError(str(e), "os.Error"))


def UserConfigDir() -> Result[str, GoError]:
    """Returns the default root directory to use for user-specific configuration data."""
    try:
        if sys.platform == "darwin":
            return Ok(str(Path.home() / "Library" / "Application Support"))
        elif sys.platform == "win32":
            app_data = _os.environ.get("APPDATA", "")
            if app_data:
                return Ok(app_data)
            return Err(GoError("APPDATA not set", "os.Error"))
        else:
            xdg_config = _os.environ.get("XDG_CONFIG_HOME", "")
            if xdg_config:
                return Ok(xdg_config)
            return Ok(str(Path.home() / ".config"))
    except Exception as e:
        return Err(GoError(str(e), "os.Error"))


def Hostname() -> Result[str, GoError]:
    """Returns the host name reported by the kernel."""
    try:
        import socket

        return Ok(socket.gethostname())
    except Exception as e:
        return Err(GoError(str(e), "os.Error"))


def Getpid() -> int:
    """Returns the process id of the caller."""
    return _os.getpid()


def Getppid() -> int:
    """Returns the process id of the caller's parent."""
    return _os.getppid()


def Getuid() -> int:
    """Returns the numeric user id of the caller."""
    return getattr(_os, "getuid", lambda: -1)()


def Getgid() -> int:
    """Returns the numeric group id of the caller."""
    return getattr(_os, "getgid", lambda: -1)()


def Geteuid() -> int:
    """Returns the numeric effective user id of the caller."""
    return getattr(_os, "geteuid", lambda: -1)()


def Getegid() -> int:
    """Returns the numeric effective group id of the caller."""
    return getattr(_os, "getegid", lambda: -1)()


# FileMode represents a file's mode and permission bits
class FileMode(int):
    """FileMode represents a file's mode and permission bits."""

    # File mode bits
    ModeDir = 1 << 31
    ModeAppend = 1 << 30
    ModeExclusive = 1 << 29
    ModeTemporary = 1 << 28
    ModeSymlink = 1 << 27
    ModeDevice = 1 << 26
    ModeNamedPipe = 1 << 25
    ModeSocket = 1 << 24
    ModeSetuid = 1 << 23
    ModeSetgid = 1 << 22
    ModeCharDevice = 1 << 21
    ModeSticky = 1 << 20
    ModeIrregular = 1 << 19
    ModeType = (
        ModeDir
        | ModeSymlink
        | ModeNamedPipe
        | ModeSocket
        | ModeDevice
        | ModeCharDevice
        | ModeIrregular
    )
    ModePerm = 0o777

    def IsDir(self) -> bool:
        """Reports whether m describes a directory."""
        return bool(self & FileMode.ModeDir)

    def IsRegular(self) -> bool:
        """Reports whether m describes a regular file."""
        return (self & FileMode.ModeType) == 0

    def Perm(self) -> FileMode:
        """Returns the Unix permission bits."""
        return FileMode(self & FileMode.ModePerm)

    def String(self) -> str:
        """Returns a string representation of the file mode."""
        return format(self & FileMode.ModePerm, "o")


@dataclass
class FileInfo:
    """FileInfo describes a file and is returned by Stat and Lstat."""

    _name: str
    _size: int
    _mode: FileMode
    _mod_time: float
    _is_dir: bool
    _sys: object = None

    def Name(self) -> str:
        """Returns the base name of the file."""
        return self._name

    def Size(self) -> int:
        """Returns the length in bytes for regular files."""
        return self._size

    def Mode(self) -> FileMode:
        """Returns the file mode bits."""
        return self._mode

    def ModTime(self) -> float:
        """Returns the modification time."""
        return self._mod_time

    def IsDir(self) -> bool:
        """Abbreviation for Mode().IsDir()."""
        return self._is_dir

    def Sys(self) -> object:
        """Returns underlying data source."""
        return self._sys


@dataclass
class DirEntry:
    """DirEntry is an entry read from a directory."""

    _name: str
    _is_dir: bool
    _type: FileMode
    _info: FileInfo | None = None

    def Name(self) -> str:
        """Returns the name of the file."""
        return self._name

    def IsDir(self) -> bool:
        """Reports whether the entry describes a directory."""
        return self._is_dir

    def Type(self) -> FileMode:
        """Returns the type bits for the entry."""
        return self._type

    def Info(self) -> Result[FileInfo, GoError]:
        """Returns the FileInfo for the file or subdirectory."""
        if self._info:
            return Ok(self._info)
        return Err(GoError("info not available", "os.PathError"))


class File:
    """File represents an open file descriptor."""

    def __init__(self, f: IO[bytes], name: str) -> None:
        self._file = f
        self._name = name

    def Name(self) -> str:
        """Returns the name of the file."""
        return self._name

    def Read(self, n: int = -1) -> Result[bytes, GoError]:
        """Reads up to n bytes from the file."""
        try:
            data = self._file.read(n)
            return Ok(data if isinstance(data, bytes) else data.encode())
        except Exception as e:
            return Err(GoError(str(e), "os.PathError"))

    def ReadAt(self, n: int, off: int) -> Result[bytes, GoError]:
        """Reads n bytes from the file starting at byte offset off."""
        try:
            current = self._file.tell()
            self._file.seek(off)
            data = self._file.read(n)
            self._file.seek(current)
            return Ok(data if isinstance(data, bytes) else data.encode())
        except Exception as e:
            return Err(GoError(str(e), "os.PathError"))

    def Write(self, data: bytes | str) -> Result[int, GoError]:
        """Writes data to the file."""
        try:
            if isinstance(data, str):
                data = data.encode()
            return Ok(self._file.write(data))
        except Exception as e:
            return Err(GoError(str(e), "os.PathError"))

    def WriteString(self, s: str) -> Result[int, GoError]:
        """Writes a string to the file."""
        return self.Write(s.encode())

    def WriteAt(self, data: bytes, off: int) -> Result[int, GoError]:
        """Writes data to the file at offset off."""
        try:
            current = self._file.tell()
            self._file.seek(off)
            n = self._file.write(data)
            self._file.seek(current)
            return Ok(n)
        except Exception as e:
            return Err(GoError(str(e), "os.PathError"))

    def Seek(self, offset: int, whence: int = 0) -> Result[int, GoError]:
        """Seeks to the offset."""
        try:
            return Ok(self._file.seek(offset, whence))
        except Exception as e:
            return Err(GoError(str(e), "os.PathError"))

    def Close(self) -> Result[None, GoError]:
        """Closes the file."""
        try:
            self._file.close()
            return Ok(None)
        except Exception as e:
            return Err(GoError(str(e), "os.PathError"))

    def Sync(self) -> Result[None, GoError]:
        """Commits the current contents of the file to stable storage."""
        try:
            self._file.flush()
            if hasattr(self._file, "fileno"):
                _os.fsync(self._file.fileno())
            return Ok(None)
        except Exception as e:
            return Err(GoError(str(e), "os.PathError"))

    def Stat(self) -> Result[FileInfo, GoError]:
        """Returns the FileInfo for the file."""
        try:
            st = _os.fstat(self._file.fileno())
            return Ok(_stat_to_fileinfo(self._name, st))
        except Exception as e:
            return Err(GoError(str(e), "os.PathError"))

    def Truncate(self, size: int) -> Result[None, GoError]:
        """Changes the size of the file."""
        try:
            self._file.truncate(size)
            return Ok(None)
        except Exception as e:
            return Err(GoError(str(e), "os.PathError"))

    def Fd(self) -> int:
        """Returns the integer Unix file descriptor."""
        return self._file.fileno()

    def __enter__(self) -> File:
        return self

    def __exit__(self, *args: Any) -> None:
        self.Close()


def _stat_to_fileinfo(name: str, st: _os.stat_result) -> FileInfo:
    """Convert os.stat_result to FileInfo."""
    mode = FileMode(st.st_mode & 0o777)
    if stat.S_ISDIR(st.st_mode):
        mode = FileMode(mode | FileMode.ModeDir)
    if stat.S_ISLNK(st.st_mode):
        mode = FileMode(mode | FileMode.ModeSymlink)

    return FileInfo(
        _name=_os.path.basename(name),
        _size=st.st_size,
        _mode=mode,
        _mod_time=st.st_mtime,
        _is_dir=stat.S_ISDIR(st.st_mode),
        _sys=st,
    )


def Create(name: str) -> Result[File, GoError]:
    """Creates or truncates the named file."""
    try:
        f = open(name, "wb+")
        return Ok(File(f, name))
    except Exception as e:
        return Err(GoError(str(e), "os.PathError"))


def Open(name: str) -> Result[File, GoError]:
    """Opens the named file for reading."""
    try:
        f = open(name, "rb")
        return Ok(File(f, name))
    except FileNotFoundError:
        return Err(GoError(f"open {name}: no such file or directory", "os.PathError"))
    except PermissionError:
        return Err(GoError(f"open {name}: permission denied", "os.PathError"))
    except Exception as e:
        return Err(GoError(str(e), "os.PathError"))


def OpenFile(name: str, flag: int, perm: int) -> Result[File, GoError]:
    """Opens the named file with specified flag and permissions."""
    try:
        mode = ""
        if flag & O_RDWR:
            mode = "r+b"
        elif flag & O_WRONLY:
            mode = "wb"
        else:
            mode = "rb"

        if flag & O_CREATE:
            if flag & O_EXCL:
                mode = "xb" if flag & O_WRONLY else "x+b"
            elif flag & O_TRUNC:
                mode = "wb" if flag & O_WRONLY else "w+b"
            elif flag & O_APPEND:
                mode = "ab" if flag & O_WRONLY else "a+b"
        elif flag & O_APPEND:
            mode = "ab" if flag & O_WRONLY else "a+b"

        f = open(name, mode)
        return Ok(File(f, name))
    except FileExistsError:
        return Err(GoError(f"open {name}: file exists", "os.PathError"))
    except FileNotFoundError:
        return Err(GoError(f"open {name}: no such file or directory", "os.PathError"))
    except PermissionError:
        return Err(GoError(f"open {name}: permission denied", "os.PathError"))
    except Exception as e:
        return Err(GoError(str(e), "os.PathError"))


def ReadFile(name: str) -> Result[bytes, GoError]:
    """Reads the named file and returns the contents."""
    try:
        with open(name, "rb") as f:
            return Ok(f.read())
    except FileNotFoundError:
        return Err(GoError(f"open {name}: no such file or directory", "os.PathError"))
    except PermissionError:
        return Err(GoError(f"open {name}: permission denied", "os.PathError"))
    except Exception as e:
        return Err(GoError(str(e), "os.PathError"))


def WriteFile(name: str, data: bytes | str, perm: int = 0o644) -> Result[None, GoError]:
    """Writes data to the named file, creating it if necessary."""
    try:
        if isinstance(data, str):
            data = data.encode()
        with open(name, "wb") as f:
            f.write(data)
        _os.chmod(name, perm)
        return Ok(None)
    except Exception as e:
        return Err(GoError(str(e), "os.PathError"))


def Remove(name: str) -> Result[None, GoError]:
    """Removes the named file or empty directory."""
    try:
        _os.remove(name)
        return Ok(None)
    except IsADirectoryError:
        try:
            _os.rmdir(name)
            return Ok(None)
        except Exception as e:
            return Err(GoError(str(e), "os.PathError"))
    except FileNotFoundError:
        return Err(GoError(f"remove {name}: no such file or directory", "os.PathError"))
    except Exception as e:
        return Err(GoError(str(e), "os.PathError"))


def RemoveAll(path: str) -> Result[None, GoError]:
    """Removes path and any children it contains."""
    try:
        if _os.path.isdir(path):
            shutil.rmtree(path)
        elif _os.path.exists(path):
            _os.remove(path)
        return Ok(None)
    except Exception as e:
        return Err(GoError(str(e), "os.PathError"))


def Rename(oldpath: str, newpath: str) -> Result[None, GoError]:
    """Renames (moves) oldpath to newpath."""
    try:
        _os.rename(oldpath, newpath)
        return Ok(None)
    except Exception as e:
        return Err(GoError(str(e), "os.LinkError"))


def Mkdir(name: str, perm: int = 0o755) -> Result[None, GoError]:
    """Creates a new directory with the specified permission bits."""
    try:
        _os.mkdir(name, perm)
        return Ok(None)
    except FileExistsError:
        return Err(GoError(f"mkdir {name}: file exists", "os.PathError"))
    except Exception as e:
        return Err(GoError(str(e), "os.PathError"))


def MkdirAll(path: str, perm: int = 0o755) -> Result[None, GoError]:
    """Creates a directory named path, along with any necessary parents."""
    try:
        _os.makedirs(path, perm, exist_ok=True)
        return Ok(None)
    except Exception as e:
        return Err(GoError(str(e), "os.PathError"))


def MkdirTemp(dir: str, pattern: str) -> Result[str, GoError]:
    """Creates a new temporary directory and returns its path."""
    try:
        return Ok(tempfile.mkdtemp(prefix=pattern, dir=dir or None))
    except Exception as e:
        return Err(GoError(str(e), "os.PathError"))


def CreateTemp(dir: str, pattern: str) -> Result[File, GoError]:
    """Creates a new temporary file and returns an open file."""
    try:
        fd, name = tempfile.mkstemp(prefix=pattern, dir=dir or None)
        f = _os.fdopen(fd, "w+b")
        return Ok(File(f, name))
    except Exception as e:
        return Err(GoError(str(e), "os.PathError"))


def Stat(name: str) -> Result[FileInfo, GoError]:
    """Returns a FileInfo describing the named file."""
    try:
        st = _os.stat(name)
        return Ok(_stat_to_fileinfo(name, st))
    except FileNotFoundError:
        return Err(GoError(f"stat {name}: no such file or directory", "os.PathError"))
    except Exception as e:
        return Err(GoError(str(e), "os.PathError"))


def Lstat(name: str) -> Result[FileInfo, GoError]:
    """Like Stat but does not follow symbolic links."""
    try:
        st = _os.lstat(name)
        return Ok(_stat_to_fileinfo(name, st))
    except FileNotFoundError:
        return Err(GoError(f"lstat {name}: no such file or directory", "os.PathError"))
    except Exception as e:
        return Err(GoError(str(e), "os.PathError"))


def Chmod(name: str, mode: int) -> Result[None, GoError]:
    """Changes the mode of the named file."""
    try:
        _os.chmod(name, mode)
        return Ok(None)
    except Exception as e:
        return Err(GoError(str(e), "os.PathError"))


def Chown(name: str, uid: int, gid: int) -> Result[None, GoError]:
    """Changes the numeric uid and gid of the named file."""
    try:
        _os.chown(name, uid, gid)
        return Ok(None)
    except AttributeError:
        return Err(GoError("chown not supported on this platform", "os.PathError"))
    except Exception as e:
        return Err(GoError(str(e), "os.PathError"))


def Link(oldname: str, newname: str) -> Result[None, GoError]:
    """Creates newname as a hard link to oldname."""
    try:
        _os.link(oldname, newname)
        return Ok(None)
    except Exception as e:
        return Err(GoError(str(e), "os.LinkError"))


def Symlink(oldname: str, newname: str) -> Result[None, GoError]:
    """Creates newname as a symbolic link to oldname."""
    try:
        _os.symlink(oldname, newname)
        return Ok(None)
    except Exception as e:
        return Err(GoError(str(e), "os.LinkError"))


def Readlink(name: str) -> Result[str, GoError]:
    """Returns the destination of the named symbolic link."""
    try:
        return Ok(_os.readlink(name))
    except Exception as e:
        return Err(GoError(str(e), "os.PathError"))


def ReadDir(name: str) -> Result[list[DirEntry], GoError]:
    """Reads the named directory, returning all its directory entries."""
    try:
        entries = []
        for entry in _os.scandir(name):
            is_dir = entry.is_dir(follow_symlinks=False)
            mode = FileMode.ModeDir if is_dir else FileMode(0)
            if entry.is_symlink():
                mode = FileMode(mode | FileMode.ModeSymlink)

            entries.append(
                DirEntry(
                    _name=entry.name,
                    _is_dir=is_dir,
                    _type=FileMode(mode),
                )
            )
        entries.sort(key=lambda e: e._name)
        return Ok(entries)
    except FileNotFoundError:
        return Err(GoError(f"open {name}: no such file or directory", "os.PathError"))
    except Exception as e:
        return Err(GoError(str(e), "os.PathError"))


def IsExist(err: GoError) -> bool:
    """Returns whether the error is known to report that a file or directory already exists."""
    return "exists" in str(err).lower()


def IsNotExist(err: GoError) -> bool:
    """Returns whether the error is known to report that a file or directory does not exist."""
    return "no such file" in str(err).lower() or "not exist" in str(err).lower()


def IsPermission(err: GoError) -> bool:
    """Returns whether the error is known to report that permission is denied."""
    return "permission denied" in str(err).lower()


def Truncate(name: str, size: int) -> Result[None, GoError]:
    """Changes the size of the named file."""
    try:
        _os.truncate(name, size)
        return Ok(None)
    except Exception as e:
        return Err(GoError(str(e), "os.PathError"))


def SameFile(fi1: FileInfo, fi2: FileInfo) -> bool:
    """Reports whether fi1 and fi2 describe the same file."""
    if fi1._sys and fi2._sys:
        s1: Any = fi1._sys
        s2: Any = fi2._sys
        return bool(s1.st_dev == s2.st_dev and s1.st_ino == s2.st_ino)
    return False
