"""Tests for goated.std.testing module (testing)."""

import os

import pytest

from goated.std import testing


class TestVerbose:
    """Test Verbose function."""

    def test_verbose_default(self):
        result = testing.Verbose()
        assert isinstance(result, bool)


class TestShort:
    """Test Short function."""

    def test_short_default(self):
        result = testing.Short()
        assert isinstance(result, bool)


class TestT:
    """Test T class (testing.T)."""

    def test_t_name(self):
        t = testing.T(_name="TestExample")
        assert t.Name() == "TestExample"

    def test_t_failed_initially_false(self):
        t = testing.T()
        assert not t.Failed()

    def test_t_skipped_initially_false(self):
        t = testing.T()
        assert not t.Skipped()

    def test_t_fail(self):
        t = testing.T()
        t.Fail()
        assert t.Failed()

    def test_t_log(self):
        t = testing.T(_name="Test")
        t.Log("test message")
        assert "test message" in t._output

    def test_t_logf(self):
        t = testing.T(_name="Test")
        t.Logf("value: %d", 42)
        assert "value: 42" in t._output

    def test_t_error(self):
        t = testing.T(_name="Test")
        t.Error("error message")
        assert t.Failed()
        assert "error message" in t._output

    def test_t_errorf(self):
        t = testing.T(_name="Test")
        t.Errorf("error: %s", "test")
        assert t.Failed()
        assert "error: test" in t._output

    def test_t_fail_now(self):
        t = testing.T(_name="Test")
        with pytest.raises(testing._FailNowException):
            t.FailNow()
        assert t.Failed()

    def test_t_fatal(self):
        t = testing.T(_name="Test")
        with pytest.raises(testing._FailNowException):
            t.Fatal("fatal error")
        assert t.Failed()
        assert "fatal error" in t._output

    def test_t_fatalf(self):
        t = testing.T(_name="Test")
        with pytest.raises(testing._FailNowException):
            t.Fatalf("fatal: %s", "test")
        assert t.Failed()

    def test_t_skip_now(self):
        t = testing.T(_name="Test")
        with pytest.raises(testing._SkipNowException):
            t.SkipNow()
        assert t.Skipped()

    def test_t_skip(self):
        t = testing.T(_name="Test")
        with pytest.raises(testing._SkipNowException):
            t.Skip("skipping")
        assert t.Skipped()
        assert "skipping" in t._output

    def test_t_skipf(self):
        t = testing.T(_name="Test")
        with pytest.raises(testing._SkipNowException):
            t.Skipf("skip: %s", "reason")
        assert t.Skipped()

    def test_t_helper(self):
        t = testing.T(_name="Test")
        t.Helper()

    def test_t_temp_dir(self):
        t = testing.T(_name="Test")
        dir_path = t.TempDir()
        assert os.path.isdir(dir_path)
        os.rmdir(dir_path)

    def test_t_cleanup(self):
        t = testing.T(_name="Test")
        cleaned = [False]

        def cleanup():
            cleaned[0] = True

        t.Cleanup(cleanup)
        assert len(t._cleanup) == 1

    def test_t_setenv(self):
        t = testing.T(_name="Test")
        original = os.environ.get("TEST_VAR_GOATED")

        t.Setenv("TEST_VAR_GOATED", "test_value")
        assert os.environ.get("TEST_VAR_GOATED") == "test_value"

        for cleanup in reversed(t._cleanup):
            cleanup()

        assert os.environ.get("TEST_VAR_GOATED") == original

    def test_t_parallel(self):
        t = testing.T(_name="Test")
        assert not t._parallel
        t.Parallel()
        assert t._parallel

    def test_t_deadline(self):
        t = testing.T(_name="Test")
        deadline, ok = t.Deadline()
        assert isinstance(deadline, float)
        assert isinstance(ok, bool)


class TestTRun:
    """Test T.Run method."""

    def test_run_passing(self):
        t = testing.T(_name="TestParent")

        def subtest(t):
            t.Log("subtest running")

        result = t.Run("SubTest", subtest)
        assert result

    def test_run_failing(self):
        t = testing.T(_name="TestParent")

        def subtest(t):
            t.Fail()

        result = t.Run("SubTest", subtest)
        assert not result

    def test_run_name(self):
        t = testing.T(_name="TestParent")

        def subtest(sub_t):
            assert sub_t.Name() == "TestParent/SubTest"

        t.Run("SubTest", subtest)

    def test_run_with_fail_now(self):
        t = testing.T(_name="TestParent")

        def subtest(t):
            t.FailNow()

        result = t.Run("SubTest", subtest)
        assert not result

    def test_run_with_skip(self):
        t = testing.T(_name="TestParent")

        def subtest(t):
            t.Skip("skipped")

        result = t.Run("SubTest", subtest)
        assert result

    def test_run_with_panic(self):
        t = testing.T(_name="TestParent")

        def subtest(t):
            raise ValueError("test error")

        result = t.Run("SubTest", subtest)
        assert not result


class TestB:
    """Test B class (testing.B)."""

    def test_b_name(self):
        b = testing.B(_name="BenchmarkExample")
        assert b.Name() == "BenchmarkExample"

    def test_b_n(self):
        b = testing.B()
        b.N = 1000
        assert b.N == 1000

    def test_b_reset_timer(self):
        b = testing.B()
        b._start = 0.0
        b.ResetTimer()
        assert b._start > 0.0

    def test_b_start_timer(self):
        b = testing.B()
        b._timer_on = False
        b.StartTimer()
        assert b._timer_on

    def test_b_stop_timer(self):
        b = testing.B()
        b._timer_on = True
        b._start = 0.0
        b.StopTimer()
        assert not b._timer_on

    def test_b_set_bytes(self):
        b = testing.B()
        b.SetBytes(1024)
        assert b._bytes == 1024

    def test_b_report_allocs(self):
        b = testing.B()
        b.ReportAllocs()

    def test_b_report_metric(self):
        b = testing.B()
        b.ReportMetric(100.0, "custom/op")

    def test_b_log(self):
        b = testing.B(_name="Benchmark")
        b.Log("benchmark message")
        assert "benchmark message" in b._output


class TestBenchmarkResult:
    """Test BenchmarkResult class."""

    def test_ns_per_op(self):
        result = testing.BenchmarkResult(N=1000, T=1.0)
        assert result.NsPerOp() == 1_000_000

    def test_ns_per_op_zero_n(self):
        result = testing.BenchmarkResult(N=0, T=1.0)
        assert result.NsPerOp() == 0

    def test_allocs_per_op(self):
        result = testing.BenchmarkResult(N=100, MemAllocs=1000)
        assert result.AllocsPerOp() == 10

    def test_allocs_per_op_zero_n(self):
        result = testing.BenchmarkResult(N=0, MemAllocs=100)
        assert result.AllocsPerOp() == 0

    def test_alloced_bytes_per_op(self):
        result = testing.BenchmarkResult(N=100, MemBytes=10000)
        assert result.AllocedBytesPerOp() == 100

    def test_string(self):
        result = testing.BenchmarkResult(N=1000, T=0.001)
        s = result.String()
        assert "1000" in s
        assert "ns/op" in s


class TestBenchmark:
    """Test Benchmark function."""

    def test_benchmark_simple(self):
        def bench(b):
            for _i in range(b.N):
                _ = 1 + 1

        result = testing.Benchmark(bench)
        assert result.N > 0
        assert result.T > 0

    def test_benchmark_with_setup(self):
        def bench(b):
            data = list(range(100))
            b.ResetTimer()
            for _i in range(b.N):
                _ = sum(data)

        result = testing.Benchmark(bench)
        assert result.N > 0


class TestAllocsPerRun:
    """Test AllocsPerRun function."""

    def test_allocs_per_run(self):
        def fn():
            _ = [1, 2, 3]

        result = testing.AllocsPerRun(10, fn)
        assert isinstance(result, float)


class TestMain:
    """Test Main function."""

    def test_main_no_error(self):
        testing.Main()


class TestTB:
    """Test TB type alias."""

    def test_tb_is_t(self):
        assert testing.TB is testing.T


class TestModuleExports:
    """Test module exports."""

    def test_exports(self):
        assert hasattr(testing, "T")
        assert hasattr(testing, "B")
        assert hasattr(testing, "TB")
        assert hasattr(testing, "Main")
        assert hasattr(testing, "Benchmark")
        assert hasattr(testing, "Short")
        assert hasattr(testing, "Verbose")
        assert hasattr(testing, "AllocsPerRun")


class TestCommonMethods:
    """Test common methods shared between T and B."""

    def test_error_methods_on_b(self):
        b = testing.B(_name="Benchmark")
        b.Error("error")
        assert b.Failed()

    def test_skip_methods_on_b(self):
        b = testing.B(_name="Benchmark")
        with pytest.raises(testing._SkipNowException):
            b.Skip("skip")
        assert b.Skipped()

    def test_cleanup_on_b(self):
        b = testing.B(_name="Benchmark")
        called = [False]

        def cleanup():
            called[0] = True

        b.Cleanup(cleanup)
        assert len(b._cleanup) == 1
