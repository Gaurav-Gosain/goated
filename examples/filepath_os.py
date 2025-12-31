#!/usr/bin/env python3
"""File path and OS operations examples using goated stdlib packages.

Demonstrates:
- filepath package (path manipulation)
- path package (URL paths)
- os package (file and environment operations)
"""

import os as pyos
import tempfile

from goated.std import filepath, os, path


def demo_filepath_basics():
    """Demonstrate basic filepath operations."""
    print("=== filepath Basics ===\n")

    # Path joining
    joined = filepath.Join("home", "user", "documents", "file.txt")
    print(f"Join: {joined}")

    # Base and Dir
    p = "/home/user/documents/report.pdf"
    print(f"\nPath: {p}")
    print(f"  Base: {filepath.Base(p)}")
    print(f"  Dir: {filepath.Dir(p)}")
    print(f"  Ext: {filepath.Ext(p)}")

    # Split
    dir_part, file_part = filepath.Split(p)
    print(f"  Split: dir={dir_part!r}, file={file_part!r}")
    print()


def demo_filepath_clean():
    """Demonstrate path cleaning."""
    print("=== filepath Clean ===\n")

    paths = [
        "/home/user/../user/./documents",
        "foo//bar///baz",
        "./relative/./path/../path",
        "/a/b/c/../../d",
    ]

    for p in paths:
        cleaned = filepath.Clean(p)
        print(f"  {p!r:40} -> {cleaned!r}")
    print()


def demo_filepath_abs_rel():
    """Demonstrate absolute and relative paths."""
    print("=== filepath Abs/Rel ===\n")

    # Absolute path
    rel_path = "relative/path/file.txt"
    abs_result = filepath.Abs(rel_path)
    if abs_result.is_ok():
        abs_path = abs_result.unwrap()
        print(f"Relative: {rel_path}")
        print(f"Absolute: {abs_path}")

    # Relative path
    base = "/home/user"
    target = "/home/user/documents/file.txt"
    rel_result = filepath.Rel(base, target)
    if rel_result.is_ok():
        rel = rel_result.unwrap()
        print(f"\nBase: {base}")
        print(f"Target: {target}")
        print(f"Relative: {rel}")

    # IsAbs
    print(f"\nIsAbs('/absolute/path'): {filepath.IsAbs('/absolute/path')}")
    print(f"IsAbs('relative/path'): {filepath.IsAbs('relative/path')}")
    print()


def demo_filepath_match():
    """Demonstrate path matching."""
    print("=== filepath Match ===\n")

    patterns = [
        ("*.txt", "report.txt"),
        ("*.txt", "report.pdf"),
        ("data/*.csv", "data/users.csv"),
        ("data/*.csv", "other/users.csv"),
        ("*.go", "main.go"),
        ("test_*.py", "test_main.py"),
    ]

    for pattern, name in patterns:
        result = filepath.Match(pattern, name)
        matched = result.unwrap_or(False)
        status = "MATCH" if matched else "no match"
        print(f"  Match({pattern!r}, {name!r}): {status}")
    print()


def demo_filepath_walk():
    """Demonstrate directory walking."""
    print("=== filepath Walk ===\n")

    # Create temp directory structure
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create some files and directories
        pyos.makedirs(pyos.path.join(tmpdir, "subdir1"))
        pyos.makedirs(pyos.path.join(tmpdir, "subdir2"))

        for name in ["file1.txt", "file2.txt", "subdir1/nested.txt"]:
            with open(pyos.path.join(tmpdir, name), "w") as f:
                f.write("content")

        # Walk the directory
        print(f"Walking: {tmpdir}")

        def walk_func(path, info, err):
            if err:
                print(f"  Error: {err}")
                return None

            rel = path.replace(tmpdir, ".")
            if info.IsDir():
                print(f"  DIR:  {rel}")
            else:
                print(f"  FILE: {rel} ({info.Size()} bytes)")
            return None

        filepath.Walk(tmpdir, walk_func)
    print()


def demo_path_package():
    """Demonstrate path package (URL paths)."""
    print("=== path Package (URL paths) ===\n")

    # Join
    joined = path.Join("api", "v1", "users")
    print(f"Join('api', 'v1', 'users'): {joined}")

    # Base and Dir
    p = "/api/v1/users/123"
    print(f"\nPath: {p}")
    print(f"  Base: {path.Base(p)}")
    print(f"  Dir: {path.Dir(p)}")
    print(f"  Ext: {path.Ext(p)}")

    # Split
    dir_part, file_part = path.Split(p)
    print(f"  Split: dir={dir_part!r}, file={file_part!r}")

    # Clean
    dirty = "/api//v1/../v2/./users"
    print(f"\nClean({dirty!r}): {path.Clean(dirty)}")

    # IsAbs
    print(f"\nIsAbs('/absolute'): {path.IsAbs('/absolute')}")
    print(f"IsAbs('relative'): {path.IsAbs('relative')}")

    # Match
    result = path.Match("*.json", "config.json")
    matched = result.unwrap_or(False)
    print(f"\nMatch('*.json', 'config.json'): {matched}")
    print()


def demo_os_environment():
    """Demonstrate OS environment operations."""
    print("=== os Environment ===\n")

    # Get environment variable
    home = os.Getenv("HOME")
    print(f"HOME: {home}")

    path_var = os.Getenv("PATH")
    print(f"PATH (truncated): {path_var[:50]}...")

    # Get with default
    value = os.Getenv("NONEXISTENT_VAR")
    print(f"NONEXISTENT_VAR: {value!r}")

    # Lookup (returns value and ok)
    value, ok = os.LookupEnv("HOME")
    print(f"\nLookupEnv('HOME'): {value!r}, exists: {ok}")

    value, ok = os.LookupEnv("NONEXISTENT_VAR")
    print(f"LookupEnv('NONEXISTENT_VAR'): {value!r}, exists: {ok}")

    # Set and unset (in test environment)
    os.Setenv("GOATED_TEST", "hello")
    print(f"\nAfter Setenv: GOATED_TEST={os.Getenv('GOATED_TEST')}")

    os.Unsetenv("GOATED_TEST")
    print(f"After Unsetenv: GOATED_TEST={os.Getenv('GOATED_TEST')!r}")

    # Environ
    env = os.Environ()
    print(f"\nTotal environment variables: {len(env)}")
    print()


def demo_os_files():
    """Demonstrate OS file operations."""
    print("=== os File Operations ===\n")

    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = pyos.path.join(tmpdir, "test.txt")

        # Create/Write file
        result = os.WriteFile(test_file, b"Hello, World!")
        if result.is_ok():
            print(f"Created: {test_file}")

        # Read file
        result = os.ReadFile(test_file)
        if result.is_ok():
            content = result.unwrap()
            print(f"Content: {content.decode()}")

        # File info (Stat)
        result = os.Stat(test_file)
        if result.is_ok():
            info = result.unwrap()
            print(f"Size: {info.Size()} bytes")
            print(f"Is directory: {info.IsDir()}")

        # Check if file exists (Go pattern: use Stat and check error)
        def file_exists(path: str) -> bool:
            return os.Stat(path).is_ok()

        print(f"File exists: {file_exists(test_file)}")
        print(f"Non-existent: {file_exists('/nonexistent/path')}")

        # Create directory
        new_dir = pyos.path.join(tmpdir, "new_directory")
        result = os.Mkdir(new_dir, 0o755)
        if result.is_ok():
            print(f"\nCreated directory: {new_dir}")

        # Create nested directories
        nested = pyos.path.join(tmpdir, "a", "b", "c")
        result = os.MkdirAll(nested, 0o755)
        if result.is_ok():
            print(f"Created nested: {nested}")

        # Read directory
        result = os.ReadDir(tmpdir)
        if result.is_ok():
            entries = result.unwrap()
            print(f"\nDirectory contents of {tmpdir}:")
            for entry in entries:
                entry_type = "DIR" if entry.IsDir() else "FILE"
                print(f"  {entry_type}: {entry.Name()}")

        # Rename file
        new_path = pyos.path.join(tmpdir, "renamed.txt")
        result = os.Rename(test_file, new_path)
        if result.is_ok():
            print(f"\nRenamed to: {new_path}")

        # Remove file
        result = os.Remove(new_path)
        if result.is_ok():
            print(f"Removed: {new_path}")
    print()


def demo_os_info():
    """Demonstrate OS information functions."""
    print("=== os Information ===\n")

    # Hostname
    result = os.Hostname()
    if result.is_ok():
        print(f"Hostname: {result.unwrap()}")

    # Working directory
    result = os.Getwd()
    if result.is_ok():
        print(f"Working directory: {result.unwrap()}")

    # User home directory
    result = os.UserHomeDir()
    if result.is_ok():
        print(f"Home directory: {result.unwrap()}")

    # User cache directory
    result = os.UserCacheDir()
    if result.is_ok():
        print(f"Cache directory: {result.unwrap()}")

    # User config directory
    result = os.UserConfigDir()
    if result.is_ok():
        print(f"Config directory: {result.unwrap()}")

    # Temp directory
    print(f"Temp directory: {os.TempDir()}")

    # Process ID
    print(f"Process ID: {os.Getpid()}")
    print()


def demo_os_temp():
    """Demonstrate temp file/dir operations."""
    print("=== os Temp Files ===\n")

    # Create temp file
    result = os.CreateTemp("", "goated-*.txt")
    if result.is_ok():
        f = result.unwrap()
        print(f"Temp file: {f.Name()}")
        f.Write(b"Temporary content")
        f.Close()

        # Clean up
        os.Remove(f.Name())

    # Create temp directory
    result = os.MkdirTemp("", "goated-*")
    if result.is_ok():
        tmpdir = result.unwrap()
        print(f"Temp directory: {tmpdir}")

        # Clean up
        os.Remove(tmpdir)
    print()


def demo_os_executable():
    """Demonstrate executable path."""
    print("=== os Executable ===\n")

    result = os.Executable()
    if result.is_ok():
        print(f"Executable: {result.unwrap()}")

    # Args
    print(f"Args: {os.Args[:3]}...")  # First few args
    print()


def main():
    print("=" * 60)
    print("  goated - filepath and os Examples")
    print("=" * 60)
    print()

    demo_filepath_basics()
    demo_filepath_clean()
    demo_filepath_abs_rel()
    demo_filepath_match()
    demo_filepath_walk()
    demo_path_package()
    demo_os_environment()
    demo_os_files()
    demo_os_info()
    demo_os_temp()
    demo_os_executable()

    print("=" * 60)
    print("  Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
