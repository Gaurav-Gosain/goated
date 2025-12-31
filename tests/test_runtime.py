"""Tests for the M:N work-stealing runtime.

Tests the goroutine-style concurrency primitives backed by the
work-stealing scheduler.
"""

import threading
import time

import pytest


class TestRuntime:
    """Test the M:N runtime scheduler."""

    def test_runtime_starts_and_shuts_down(self):
        """Runtime can start and shutdown cleanly."""
        from goated.runtime.scheduler import Runtime

        runtime = Runtime(num_workers=2)
        runtime.start()
        assert runtime._started
        assert runtime.num_workers == 2

        runtime.shutdown()
        assert not runtime._started

    def test_submit_task(self):
        """Can submit and execute a task."""
        from goated.runtime.scheduler import Runtime

        runtime = Runtime(num_workers=2)
        runtime.start()

        try:
            result = [None]

            def task():
                result[0] = 42

            future = runtime.submit(task)
            future.result(timeout=5.0)
            assert result[0] == 42
        finally:
            runtime.shutdown()

    def test_submit_with_return_value(self):
        """Task return value is available via future."""
        from goated.runtime.scheduler import Runtime

        runtime = Runtime(num_workers=2)
        runtime.start()

        try:

            def compute(x, y):
                return x + y

            future = runtime.submit(compute, 10, 20)
            result = future.result(timeout=5.0)
            assert result == 30
        finally:
            runtime.shutdown()

    def test_parallel_execution(self):
        """Multiple tasks execute in parallel."""
        from goated.runtime.scheduler import Runtime

        runtime = Runtime(num_workers=4)
        runtime.start()

        try:
            results = []
            lock = threading.Lock()

            def work(n):
                time.sleep(0.01)  # Small delay
                with lock:
                    results.append(n)
                return n

            futures = [runtime.submit(work, i) for i in range(10)]

            # Wait for all
            for f in futures:
                f.result(timeout=5.0)

            assert len(results) == 10
            assert set(results) == set(range(10))
        finally:
            runtime.shutdown()

    def test_runtime_stats(self):
        """Runtime provides useful statistics."""
        from goated.runtime.scheduler import Runtime

        runtime = Runtime(num_workers=2)
        runtime.start()

        try:
            # Submit some tasks
            futures = [runtime.submit(lambda: 1) for _ in range(10)]
            for f in futures:
                f.result(timeout=5.0)

            time.sleep(0.1)  # Let stats settle

            stats = runtime.stats()
            assert stats["num_workers"] == 2
            assert stats["started"] is True
            assert stats["total_submitted"] >= 10
        finally:
            runtime.shutdown()


class TestGo:
    """Test the go() function."""

    def test_go_fire_and_forget(self):
        """go() can fire and forget."""
        from goated.runtime import go

        result = [None]
        done = threading.Event()

        def task():
            result[0] = "done"
            done.set()

        go(task)
        done.wait(timeout=5.0)
        assert result[0] == "done"

    def test_go_with_args(self):
        """go() passes args correctly."""
        from goated.runtime import go

        def add(a, b, c=0):
            return a + b + c

        future = go(add, 1, 2, c=3)
        result = future.result(timeout=5.0)
        assert result == 6

    def test_go_with_waitgroup(self):
        """go() integrates with WaitGroup."""
        from goated.runtime import WaitGroup, go

        results = []
        lock = threading.Lock()
        wg = WaitGroup()

        def worker(n):
            with lock:
                results.append(n)

        for i in range(5):
            wg.Add(1)
            go(worker, i, done=wg)

        wg.Wait(timeout=5.0)
        assert len(results) == 5
        assert set(results) == {0, 1, 2, 3, 4}


class TestWaitGroup:
    """Test WaitGroup."""

    def test_waitgroup_basic(self):
        """Basic WaitGroup usage."""
        from goated.runtime import WaitGroup

        wg = WaitGroup()
        wg.Add(2)

        assert not wg._event.is_set()

        wg.Done()
        assert not wg._event.is_set()

        wg.Done()
        assert wg._event.is_set()

    def test_waitgroup_wait_returns_immediately_when_zero(self):
        """Wait returns immediately when counter is zero."""
        from goated.runtime import WaitGroup

        wg = WaitGroup()
        assert wg.Wait(timeout=0.1) is True

    def test_waitgroup_wait_timeout(self):
        """Wait respects timeout."""
        from goated.runtime import WaitGroup

        wg = WaitGroup()
        wg.Add(1)

        start = time.time()
        result = wg.Wait(timeout=0.1)
        elapsed = time.time() - start

        assert result is False
        assert elapsed < 0.5  # Should timeout quickly

    def test_waitgroup_negative_counter_raises(self):
        """Negative counter raises ValueError."""
        from goated.runtime import WaitGroup

        wg = WaitGroup()
        with pytest.raises(ValueError, match="negative"):
            wg.Done()


class TestChan:
    """Test channel implementation."""

    def test_chan_send_recv(self):
        """Basic send and receive."""
        from goated.runtime import Chan

        ch = Chan[int](buffer=1)
        ch.Send(42)

        val, ok = ch.Recv(timeout=1.0)
        assert val == 42
        assert ok is True

    def test_chan_buffered(self):
        """Buffered channel stores values."""
        from goated.runtime import Chan

        ch = Chan[int](buffer=3)
        ch.Send(1)
        ch.Send(2)
        ch.Send(3)

        vals = []
        for _ in range(3):
            val, ok = ch.Recv(timeout=1.0)
            assert ok
            vals.append(val)

        assert vals == [1, 2, 3]

    def test_chan_close(self):
        """Closed channel behavior."""
        from goated.runtime import Chan

        ch = Chan[int](buffer=1)
        ch.Send(1)
        ch.Close()

        # Can still receive buffered value
        val, ok = ch.Recv(timeout=1.0)
        assert val == 1
        assert ok is True

        # Now returns (None, False)
        val, ok = ch.Recv(timeout=0.1)
        assert ok is False

    def test_chan_send_on_closed_raises(self):
        """Send on closed channel raises."""
        from goated.runtime import Chan

        ch = Chan[int](buffer=1)
        ch.Close()

        with pytest.raises(ValueError, match="closed"):
            ch.Send(1)

    def test_chan_iteration(self):
        """Can iterate over channel."""
        from goated.runtime import Chan, go

        ch = Chan[int](buffer=5)

        def producer():
            for i in range(5):
                ch.Send(i)
            ch.Close()

        go(producer)

        values = list(ch)
        assert values == [0, 1, 2, 3, 4]


class TestGoGroup:
    """Test GoGroup context manager."""

    def test_gogroup_basic(self):
        """Basic GoGroup usage."""
        from goated.runtime import GoGroup

        results = []
        lock = threading.Lock()

        with GoGroup() as g:
            for i in range(5):

                def work(n):
                    with lock:
                        results.append(n)

                g.go(work, i)

        assert len(results) == 5
        assert set(results) == {0, 1, 2, 3, 4}

    def test_gogroup_with_limit(self):
        """GoGroup respects concurrency limit."""
        from goated.runtime import GoGroup

        concurrent_count = [0]
        max_concurrent = [0]
        lock = threading.Lock()

        def work():
            with lock:
                concurrent_count[0] += 1
                max_concurrent[0] = max(max_concurrent[0], concurrent_count[0])
            time.sleep(0.05)
            with lock:
                concurrent_count[0] -= 1

        with GoGroup(limit=2) as g:
            for _ in range(10):
                g.go(work)

        assert max_concurrent[0] <= 2

    def test_gogroup_returns_futures(self):
        """GoGroup returns futures."""
        from goated.runtime import GoGroup

        with GoGroup() as g:
            f1 = g.go(lambda: 1)
            f2 = g.go(lambda: 2)

        assert f1.result() == 1
        assert f2.result() == 2


class TestErrGroup:
    """Test ErrGroup for error handling."""

    def test_errgroup_captures_error(self):
        """ErrGroup captures first error."""
        from goated.runtime import ErrGroup

        def failing_task():
            raise ValueError("task failed")

        def ok_task():
            return "ok"

        g = ErrGroup()
        g.go(ok_task)
        g.go(failing_task)

        err = g.Wait()
        assert err is not None
        assert isinstance(err, ValueError)

    def test_errgroup_context_raises(self):
        """ErrGroup context manager raises on error."""
        from goated.runtime import ErrGroup

        with pytest.raises(ValueError, match="task failed"), ErrGroup() as g:
            g.go(lambda: "ok")
            g.go(lambda: (_ for _ in ()).throw(ValueError("task failed")))

    def test_errgroup_no_error(self):
        """ErrGroup returns None when no errors."""
        from goated.runtime import ErrGroup

        g = ErrGroup()
        g.go(lambda: 1)
        g.go(lambda: 2)

        err = g.Wait()
        assert err is None


class TestSelect:
    """Test Select statement."""

    def test_select_recv(self):
        """Select on receive."""
        from goated.runtime import Chan, Select, SelectCase

        ch1 = Chan[int](buffer=1)
        ch2 = Chan[str](buffer=1)

        ch1.Send(42)

        idx, val, ok = Select(
            SelectCase(ch1),
            SelectCase(ch2),
        )

        assert idx == 0
        assert val == 42
        assert ok is True

    def test_select_default(self):
        """Select with default case."""
        from goated.runtime import Chan, Select, SelectCase

        ch = Chan[int](buffer=1)

        idx, val, ok = Select(
            SelectCase(ch),
            default=True,
        )

        assert idx == -1
        assert ok is False


class TestParallelOperations:
    """Test parallel_for and parallel_map."""

    def test_parallel_for(self):
        """parallel_for executes function for each index."""
        from goated.runtime import parallel_for

        results = [None] * 10

        def fill(i):
            results[i] = i * 2

        parallel_for(0, 10, fill)
        assert results == [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

    def test_parallel_map(self):
        """parallel_map applies function to each item."""
        from goated.runtime import parallel_map

        items = [1, 2, 3, 4, 5]
        results = parallel_map(lambda x: x**2, items)
        assert results == [1, 4, 9, 16, 25]

    def test_parallel_map_preserves_order(self):
        """parallel_map preserves input order."""
        from goated.runtime import parallel_map

        def slow_double(x):
            time.sleep(0.01 * (5 - x))  # Slower for smaller numbers
            return x * 2

        items = [1, 2, 3, 4, 5]
        results = parallel_map(slow_double, items)
        assert results == [2, 4, 6, 8, 10]


class TestFastChan:
    """Test optimized FastChan."""

    def test_fastchan_send_recv(self):
        """Basic FastChan operations."""
        from goated.runtime.channel import FastChan

        ch = FastChan[int](buffer=5)
        ch.Send(1)
        ch.Send(2)

        val, ok = ch.Recv()
        assert val == 1
        assert ok is True

        val, ok = ch.Recv()
        assert val == 2
        assert ok is True

    def test_fastchan_close(self):
        """FastChan close behavior."""
        from goated.runtime.channel import FastChan

        ch = FastChan[int](buffer=1)
        ch.Send(42)
        ch.Close()

        val, ok = ch.Recv()
        assert val == 42
        assert ok is True

        val, ok = ch.Recv()
        assert ok is False


class TestMPMCQueue:
    """Test MPMC queue."""

    def test_mpmc_basic(self):
        """Basic MPMC queue operations."""
        from goated.runtime.channel import MPMCQueue

        q = MPMCQueue[int](capacity=10)
        assert q.put(1)
        assert q.put(2)

        val, ok = q.get()
        assert val == 1
        assert ok is True

        val, ok = q.get()
        assert val == 2
        assert ok is True

    def test_mpmc_concurrent(self):
        """MPMC queue handles concurrent access."""
        from goated.runtime import GoGroup
        from goated.runtime.channel import MPMCQueue

        q = MPMCQueue[int](capacity=100)
        results = []
        lock = threading.Lock()

        def producer(start):
            for i in range(10):
                q.put(start + i)

        def consumer():
            while True:
                val, ok = q.try_get()
                if not ok:
                    break
                with lock:
                    results.append(val)

        # Produce
        with GoGroup() as g:
            for i in range(5):
                g.go(producer, i * 10)

        # Consume
        with GoGroup() as g:
            for _ in range(3):
                g.go(consumer)

        assert len(results) == 50
