"""Comprehensive tests for Result[T, E] types.

Tests cover:
- Ok and Err creation and basic operations
- Pattern matching with match/case
- Fluent API (map, and_then, etc.)
- Type guards (is_ok, is_err)
- GoError exception handling
"""

import pytest

from goated import Err, GoError, Ok, Result, is_err, is_ok


class TestOk:
    def test_creation(self):
        ok = Ok(42)
        assert ok.value == 42

    def test_is_ok_returns_true(self):
        ok = Ok("hello")
        assert ok.is_ok() is True

    def test_is_err_returns_false(self):
        ok = Ok(100)
        assert ok.is_err() is False

    def test_unwrap_returns_value(self):
        ok = Ok([1, 2, 3])
        assert ok.unwrap() == [1, 2, 3]

    def test_unwrap_or_returns_value(self):
        ok = Ok(42)
        assert ok.unwrap_or(0) == 42

    def test_unwrap_or_else_returns_value(self):
        ok = Ok(42)
        assert ok.unwrap_or_else(lambda e: 0) == 42

    def test_expect_returns_value(self):
        ok = Ok("success")
        assert ok.expect("should not fail") == "success"

    def test_map_transforms_value(self):
        ok = Ok(21)
        result = ok.map(lambda x: x * 2)
        assert isinstance(result, Ok)
        assert result.value == 42

    def test_map_err_returns_unchanged(self):
        ok: Result[int, Exception] = Ok(42)
        result = ok.map_err(lambda e: RuntimeError(str(e)))
        assert isinstance(result, Ok)
        assert result.value == 42

    def test_and_then_chains_operations(self):
        ok = Ok(10)
        result = ok.and_then(lambda x: Ok(x + 5))
        assert isinstance(result, Ok)
        assert result.value == 15

    def test_and_then_can_return_err(self):
        ok = Ok(-5)
        result = ok.and_then(lambda x: Err(ValueError("negative")) if x < 0 else Ok(x))
        assert isinstance(result, Err)

    def test_or_else_returns_unchanged(self):
        ok: Result[int, ValueError] = Ok(42)
        result = ok.or_else(lambda e: Ok(0))
        assert isinstance(result, Ok)
        assert result.value == 42

    def test_ok_method_returns_value(self):
        ok = Ok("test")
        assert ok.ok() == "test"

    def test_err_method_returns_none(self):
        ok = Ok("test")
        assert ok.err() is None

    def test_bool_is_true(self):
        ok = Ok(0)
        assert bool(ok) is True

    def test_repr(self):
        ok = Ok(42)
        assert repr(ok) == "Ok(42)"

    def test_equality(self):
        assert Ok(42) == Ok(42)
        assert Ok(42) != Ok(43)
        assert Ok("hello") == Ok("hello")

    def test_hash(self):
        ok1 = Ok(42)
        ok2 = Ok(42)
        assert hash(ok1) == hash(ok2)

    def test_pattern_matching(self):
        result: Result[int, Exception] = Ok(42)
        match result:
            case Ok(value):
                assert value == 42
            case Err(_):
                pytest.fail("Should not match Err")


class TestErr:
    def test_creation(self):
        err = Err(GoError("something went wrong"))
        assert isinstance(err.error, GoError)

    def test_is_ok_returns_false(self):
        err = Err(GoError("error"))
        assert err.is_ok() is False

    def test_is_err_returns_true(self):
        err = Err(GoError("error"))
        assert err.is_err() is True

    def test_unwrap_raises_error(self):
        err = Err(GoError("test error"))
        with pytest.raises(GoError, match="test error"):
            err.unwrap()

    def test_unwrap_or_returns_default(self):
        err: Err[GoError] = Err(GoError("error"))
        assert err.unwrap_or(42) == 42

    def test_unwrap_or_else_computes_from_error(self):
        err = Err(GoError("error"))
        assert err.unwrap_or_else(lambda e: len(str(e))) == 5

    def test_expect_raises_with_message(self):
        err = Err(GoError("original"))
        with pytest.raises(RuntimeError, match="custom message"):
            err.expect("custom message")

    def test_map_returns_unchanged(self):
        err: Result[int, GoError] = Err(GoError("error"))
        result = err.map(lambda x: x * 2)
        assert isinstance(result, Err)

    def test_map_err_transforms_error(self):
        err = Err(GoError("original"))
        result = err.map_err(lambda e: RuntimeError(f"wrapped: {e}"))
        assert isinstance(result, Err)
        assert isinstance(result.error, RuntimeError)

    def test_and_then_returns_unchanged(self):
        err: Result[int, GoError] = Err(GoError("error"))
        result = err.and_then(lambda x: Ok(x + 1))
        assert isinstance(result, Err)

    def test_or_else_handles_error(self):
        err: Err[GoError] = Err(GoError("error"))
        result = err.or_else(lambda e: Ok(42))
        assert isinstance(result, Ok)
        assert result.value == 42

    def test_ok_method_returns_none(self):
        err = Err(GoError("error"))
        assert err.ok() is None

    def test_err_method_returns_error(self):
        error = GoError("test")
        err = Err(error)
        assert err.err() is error

    def test_bool_is_false(self):
        err = Err(GoError("error"))
        assert bool(err) is False

    def test_repr(self):
        err = Err(GoError("test"))
        assert "Err" in repr(err)
        assert "test" in repr(err)

    def test_pattern_matching(self):
        result: Result[int, GoError] = Err(GoError("failed"))
        match result:
            case Ok(_):
                pytest.fail("Should not match Ok")
            case Err(error):
                assert str(error) == "failed"


class TestGoError:
    def test_creation(self):
        err = GoError("something went wrong")
        assert err.message == "something went wrong"
        assert err.go_type == "error"

    def test_creation_with_type(self):
        err = GoError("not found", go_type="os.PathError")
        assert err.go_type == "os.PathError"

    def test_str(self):
        err = GoError("test message")
        assert str(err) == "test message"

    def test_repr(self):
        err = GoError("test")
        assert repr(err) == "GoError('test')"

    def test_can_be_raised(self):
        with pytest.raises(GoError, match="test error"):
            raise GoError("test error")

    def test_equality(self):
        assert GoError("test") == GoError("test")
        assert GoError("a") != GoError("b")

    def test_hash(self):
        err1 = GoError("test")
        err2 = GoError("test")
        assert hash(err1) == hash(err2)


class TestTypeGuards:
    def test_is_ok_with_ok(self):
        result: Result[int, GoError] = Ok(42)
        assert is_ok(result) is True

    def test_is_ok_with_err(self):
        result: Result[int, GoError] = Err(GoError("error"))
        assert is_ok(result) is False

    def test_is_err_with_ok(self):
        result: Result[int, GoError] = Ok(42)
        assert is_err(result) is False

    def test_is_err_with_err(self):
        result: Result[int, GoError] = Err(GoError("error"))
        assert is_err(result) is True

    def test_type_narrowing_with_is_ok(self):
        result: Result[int, GoError] = Ok(42)
        if is_ok(result):
            assert result.value == 42

    def test_type_narrowing_with_is_err(self):
        result: Result[int, GoError] = Err(GoError("test"))
        if is_err(result):
            assert result.error.message == "test"


class TestResultChaining:
    def test_chain_multiple_maps(self):
        result = Ok(5).map(lambda x: x * 2).map(lambda x: x + 1).map(str)
        assert result.unwrap() == "11"

    def test_chain_and_then(self):
        def double_if_positive(x: int) -> Result[int, str]:
            if x > 0:
                return Ok(x * 2)
            return Err(ValueError("not positive"))

        result = Ok(5).and_then(double_if_positive).and_then(double_if_positive)
        assert result.unwrap() == 20

    def test_chain_stops_at_error(self):
        def fail_at_10(x: int) -> Result[int, GoError]:
            if x >= 10:
                return Err(GoError("too big"))
            return Ok(x + 3)

        result = Ok(5).and_then(fail_at_10).and_then(fail_at_10).and_then(fail_at_10)
        assert isinstance(result, Err)

    def test_complex_pipeline(self):
        def parse_int(s: str) -> Result[int, GoError]:
            try:
                return Ok(int(s))
            except ValueError:
                return Err(GoError(f"cannot parse '{s}' as int"))

        def validate_positive(n: int) -> Result[int, GoError]:
            if n > 0:
                return Ok(n)
            return Err(GoError("must be positive"))

        result = parse_int("42").and_then(validate_positive).map(lambda x: x * 2)
        assert result.unwrap() == 84

        result = parse_int("abc").and_then(validate_positive).map(lambda x: x * 2)
        assert isinstance(result, Err)

        result = parse_int("-5").and_then(validate_positive).map(lambda x: x * 2)
        assert isinstance(result, Err)
