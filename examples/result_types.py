#!/usr/bin/env python3
"""Example demonstrating Result[T, E] types for error handling.

Shows:
1. Basic Ok/Err usage
2. Pattern matching with match/case
3. Fluent API (map, and_then, unwrap_or, etc.)
4. Building pipelines that handle errors gracefully
"""

from goated import Err, GoError, Ok, Result, is_err, is_ok


def parse_int(s: str) -> Result[int, GoError]:
    """Parse a string to int, returning Result."""
    try:
        return Ok(int(s))
    except ValueError:
        return Err(GoError(f"cannot parse '{s}' as integer"))


def validate_positive(n: int) -> Result[int, GoError]:
    """Validate that n is positive."""
    if n > 0:
        return Ok(n)
    return Err(GoError(f"{n} is not positive"))


def validate_even(n: int) -> Result[int, GoError]:
    """Validate that n is even."""
    if n % 2 == 0:
        return Ok(n)
    return Err(GoError(f"{n} is not even"))


def demo_basic_usage():
    print("=" * 50)
    print("Basic Ok/Err Usage")
    print("=" * 50)

    ok_result: Result[int, GoError] = Ok(42)
    err_result: Result[int, GoError] = Err(GoError("something went wrong"))

    print("\nOk(42):")
    print(f"  is_ok: {ok_result.is_ok()}")
    print(f"  is_err: {ok_result.is_err()}")
    print(f"  unwrap: {ok_result.unwrap()}")

    print("\nErr('something went wrong'):")
    print(f"  is_ok: {err_result.is_ok()}")
    print(f"  is_err: {err_result.is_err()}")
    print(f"  unwrap_or(0): {err_result.unwrap_or(0)}")


def demo_pattern_matching():
    print("\n" + "=" * 50)
    print("Pattern Matching (Python 3.10+)")
    print("=" * 50)

    test_cases = ["42", "-5", "hello", "100"]

    for value in test_cases:
        result = parse_int(value)

        match result:
            case Ok(n):
                print(f"\nParsed '{value}' -> {n}")
            case Err(error):
                print(f"\nFailed to parse '{value}': {error}")


def demo_fluent_api():
    print("\n" + "=" * 50)
    print("Fluent API")
    print("=" * 50)

    print("\nChaining with map():")
    result = Ok(10).map(lambda x: x * 2).map(lambda x: x + 1)
    print(f"  Ok(10).map(x * 2).map(x + 1) = {result.unwrap()}")

    print("\nUsing unwrap_or():")
    ok_val = Ok(42).unwrap_or(0)
    err_val = Err(GoError("oops")).unwrap_or(0)
    print(f"  Ok(42).unwrap_or(0) = {ok_val}")
    print(f"  Err('oops').unwrap_or(0) = {err_val}")

    print("\nUsing and_then() for chaining operations:")
    result = parse_int("42").and_then(validate_positive).and_then(validate_even)
    print(f"  parse_int('42') -> validate_positive -> validate_even = {result}")

    result = parse_int("7").and_then(validate_positive).and_then(validate_even)
    print(f"  parse_int('7') -> validate_positive -> validate_even = {result}")


def demo_pipeline():
    print("\n" + "=" * 50)
    print("Building a Pipeline")
    print("=" * 50)

    def process_input(raw: str) -> Result[str, GoError]:
        return (
            parse_int(raw)
            .and_then(validate_positive)
            .and_then(validate_even)
            .map(lambda n: n * 2)
            .map(lambda n: f"Result: {n}")
        )

    inputs = ["20", "7", "-4", "abc", "100"]

    for inp in inputs:
        result = process_input(inp)
        if is_ok(result):
            print(f"\n'{inp}' -> Success: {result.value}")
        else:
            print(f"\n'{inp}' -> Error: {result.error}")


def demo_type_guards():
    print("\n" + "=" * 50)
    print("Type Guards (is_ok, is_err)")
    print("=" * 50)

    result: Result[int, GoError] = parse_int("42")

    if is_ok(result):
        print(f"\nUsing is_ok type guard: {result.value}")

    result2: Result[int, GoError] = parse_int("abc")

    if is_err(result2):
        print(f"Using is_err type guard: {result2.error}")


def main():
    print("\n🐐 GOATED - Result Types Demo 🐐\n")

    demo_basic_usage()
    demo_pattern_matching()
    demo_fluent_api()
    demo_pipeline()
    demo_type_guards()

    print("\n" + "=" * 50)
    print("Done!")
    print("=" * 50)


if __name__ == "__main__":
    main()
