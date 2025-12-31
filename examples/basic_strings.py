#!/usr/bin/env python3
"""Basic example demonstrating goated strings package.

Shows all three API styles:
1. Direct Go-style (goated.std.strings)
2. Pythonic wrapper (goated.pythonic.strings)
3. Builder pattern
"""

from goated.pythonic import strings as py_strings
from goated.std import strings


def demo_go_style():
    print("=" * 50)
    print("Go-Style API (goated.std.strings)")
    print("=" * 50)

    text = "Hello, Gophers! Welcome to GOATED!"

    print(f"\nOriginal: {text!r}")
    print(f"Contains 'Gophers': {strings.Contains(text, 'Gophers')}")
    print(f"HasPrefix 'Hello': {strings.HasPrefix(text, 'Hello')}")
    print(f"HasSuffix '!': {strings.HasSuffix(text, '!')}")
    print(f"Index of 'Gophers': {strings.Index(text, 'Gophers')}")
    print(f"Count of '!': {strings.Count(text, '!')}")

    result = strings.Split("a,b,c,d,e", ",")
    parts = result.to_list() if hasattr(result, "to_list") else result
    print(f"\nSplit 'a,b,c,d,e' by ',': {parts}")

    print(f"ToUpper: {strings.ToUpper(text)}")
    print(f"ToLower: {strings.ToLower(text)}")
    print(f"TrimSpace '  hello  ': {strings.TrimSpace('  hello  ')!r}")
    print(f"Repeat 'Go' 3x: {strings.Repeat('Go', 3)}")
    print(
        f"Replace 'Gophers' with 'Pythonistas': {strings.Replace(text, 'Gophers', 'Pythonistas', 1)}"
    )


def demo_pythonic_style():
    print("\n" + "=" * 50)
    print("Pythonic API (goated.pythonic.strings)")
    print("=" * 50)

    text = "hello world from goated"

    print(f"\nOriginal: {text!r}")
    print(f"contains 'world': {py_strings.contains(text, 'world')}")
    print(f"has_prefix 'hello': {py_strings.has_prefix(text, 'hello')}")
    print(f"has_suffix 'goated': {py_strings.has_suffix(text, 'goated')}")

    parts = py_strings.split("one,two,three", ",")
    print(f"split 'one,two,three' by ',': {parts}")

    print(f"to_upper: {py_strings.to_upper(text)}")
    print(f"to_lower: {py_strings.to_lower('HELLO')}")
    print(f"trim_space: {py_strings.trim_space('  padded  ')!r}")
    print(f"replace: {py_strings.replace(text, 'world', 'universe')}")

    words = py_strings.fields("  multiple   spaces   between  ")
    print(f"fields: {words}")


def demo_builder():
    print("\n" + "=" * 50)
    print("Builder Pattern")
    print("=" * 50)

    b = strings.Builder()
    b.WriteString("Hello")
    b.WriteString(", ")
    b.WriteString("World")
    b.WriteString("!")

    result = str(b)
    print(f"Built string: {result!r}")
    print(f"Length: {b.Len()} bytes")

    b.Reset()
    print(f"After reset: {str(b)!r}")


def main():
    print("\n🐐 GOATED - Go stdlib for Python 🐐\n")

    demo_go_style()
    demo_pythonic_style()
    demo_builder()

    print("\n" + "=" * 50)
    print("Done!")
    print("=" * 50)


if __name__ == "__main__":
    main()
