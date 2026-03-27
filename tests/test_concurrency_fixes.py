"""Tests for concurrency fixes and new features.

Covers:
- Unbuffered channel rendezvous semantics
- Channel iterator proper blocking (no polling)
- Select condition-variable notification (no spin-wait)
- RWMutex concurrent reads with writer preference
- Semaphore weighted concurrency limiting
- pipe/merge/fan_out channel helpers
- Pool thread-local fast path
- goroutine decorator metadata preservation
"""

import threading
import time


class TestUnbufferedChannel:
    """Test true unbuffered (rendezvous) channel semantics."""

    def test_unbuffered_send_blocks_until_recv(self):
        """Send on unbuffered channel blocks until a receiver is ready."""
        from goated.runtime import Chan, go

        ch = Chan[int](buffer=0)
        send_done = threading.Event()
        recv_done = threading.Event()

        def sender():
            ch.Send(42)
            send_done.set()

        def receiver():
            time.sleep(0.05)  # Ensure sender is blocked first
            val, ok = ch.Recv()
            assert val == 42
            assert ok is True
            recv_done.set()

        go(sender)
        go(receiver)

        # Sender should not complete before receiver starts
        assert not send_done.wait(timeout=0.03)
        assert recv_done.wait(timeout=2.0)
        # Sender should complete shortly after receiver
        assert send_done.wait(timeout=2.0)

    def test_unbuffered_recv_blocks_until_send(self):
        """Recv on unbuffered channel blocks until a sender is ready."""
        from goated.runtime import Chan, go

        ch = Chan[int](buffer=0)
        result = [None]
        recv_done = threading.Event()

        def receiver():
            val, ok = ch.Recv()
            result[0] = val
            recv_done.set()

        go(receiver)
        time.sleep(0.05)  # Ensure receiver is waiting
        ch.Send(99)
        assert recv_done.wait(timeout=2.0)
        assert result[0] == 99

    def test_unbuffered_close_unblocks_recv(self):
        """Close on unbuffered channel unblocks waiting receivers."""
        from goated.runtime import Chan, go

        ch = Chan[int](buffer=0)
        result = [None]
        done = threading.Event()

        def receiver():
            val, ok = ch.Recv()
            result[0] = ok
            done.set()

        go(receiver)
        time.sleep(0.05)
        ch.Close()
        assert done.wait(timeout=2.0)
        assert result[0] is False

    def test_unbuffered_multiple_rendezvous(self):
        """Multiple send/recv pairs work correctly on unbuffered channel."""
        from goated.runtime import Chan, go

        ch = Chan[int](buffer=0)
        results = []
        lock = threading.Lock()
        done = threading.Event()

        def producer():
            for i in range(5):
                ch.Send(i)
            ch.Close()

        def consumer():
            for val in ch:
                with lock:
                    results.append(val)
            done.set()

        go(producer)
        go(consumer)
        assert done.wait(timeout=5.0)
        assert results == [0, 1, 2, 3, 4]

    def test_unbuffered_trysend_returns_false(self):
        """TrySend on unbuffered channel returns False (no receiver waiting)."""
        from goated.runtime import Chan

        ch = Chan[int](buffer=0)
        assert ch.TrySend(42) is False

    def test_unbuffered_send_timeout(self):
        """Send with timeout returns False on timeout."""
        from goated.runtime import Chan

        ch = Chan[int](buffer=0)
        result = ch.Send(42, timeout=0.05)
        assert result is False


class TestChannelIteratorBlocking:
    """Test that channel iterators block properly without polling."""

    def test_iterator_blocks_on_empty_channel(self):
        """Iterator blocks properly waiting for values, not polling."""
        from goated.runtime import Chan, go

        ch = Chan[int](buffer=5)
        values = []
        done = threading.Event()

        def consumer():
            for v in ch:
                values.append(v)
            done.set()

        go(consumer)
        time.sleep(0.05)
        assert values == []  # Consumer is blocking

        ch.Send(1)
        ch.Send(2)
        time.sleep(0.05)
        ch.Close()

        assert done.wait(timeout=2.0)
        assert values == [1, 2]

    def test_iterator_exits_on_close(self):
        """Iterator exits immediately when channel is closed."""
        from goated.runtime import Chan

        ch = Chan[int](buffer=5)
        ch.Send(1)
        ch.Send(2)
        ch.Close()

        values = list(ch)
        assert values == [1, 2]


class TestSelectNotification:
    """Test Select with proper condition-variable notification."""

    def test_select_wakes_on_channel_activity(self):
        """Select wakes up when a channel gets data (not by polling)."""
        from goated.runtime import Chan, Select, SelectCase, go

        ch1 = Chan[int](buffer=1)
        ch2 = Chan[str](buffer=1)
        result = [None, None, None]
        done = threading.Event()

        def selector():
            idx, val, ok = Select(SelectCase(ch1), SelectCase(ch2))
            result[0] = idx
            result[1] = val
            result[2] = ok
            done.set()

        go(selector)
        time.sleep(0.05)  # Let selector start waiting
        ch2.Send("hello")  # This should wake up Select

        assert done.wait(timeout=2.0)
        assert result[0] == 1
        assert result[1] == "hello"
        assert result[2] is True

    def test_select_on_closed_channel(self):
        """Select returns (None, False) for closed channel."""
        from goated.runtime import Chan, Select, SelectCase

        ch = Chan[int](buffer=1)
        ch.Close()

        idx, val, ok = Select(SelectCase(ch))
        assert idx == 0
        assert ok is False

    def test_select_send_case(self):
        """Select with send case."""
        from goated.runtime import Chan, Select, SelectCase

        ch = Chan[int](buffer=1)
        idx, val, ok = Select(SelectCase(ch, send_value=42, is_send=True))
        assert idx == 0
        assert ok is True

        recv_val, recv_ok = ch.Recv(timeout=1.0)
        assert recv_val == 42
        assert recv_ok is True


class TestRWMutexFixed:
    """Test corrected RWMutex with proper reader-writer semantics."""

    def test_concurrent_reads_allowed(self):
        """Multiple readers can hold the lock simultaneously."""
        from goated.runtime import RWMutex, go

        rw = RWMutex()
        concurrent_readers = [0]
        max_readers = [0]
        lock = threading.Lock()
        barrier = threading.Barrier(3)

        def reader():
            rw.RLock()
            try:
                with lock:
                    concurrent_readers[0] += 1
                    max_readers[0] = max(max_readers[0], concurrent_readers[0])
                barrier.wait(timeout=2.0)  # All readers should be here
                time.sleep(0.02)
                with lock:
                    concurrent_readers[0] -= 1
            finally:
                rw.RUnlock()

        futures = [go(reader) for _ in range(3)]
        for f in futures:
            f.result(timeout=5.0)

        assert max_readers[0] == 3, "All 3 readers should hold lock concurrently"

    def test_writer_excludes_readers(self):
        """Writer gets exclusive access, no readers during write."""
        from goated.runtime import RWMutex, go

        rw = RWMutex()
        in_write = [False]
        reader_saw_write = [False]
        lock = threading.Lock()

        def writer():
            rw.Lock()
            try:
                with lock:
                    in_write[0] = True
                time.sleep(0.1)
                with lock:
                    in_write[0] = False
            finally:
                rw.Unlock()

        def reader():
            time.sleep(0.02)  # Let writer start
            rw.RLock()
            try:
                with lock:
                    if in_write[0]:
                        reader_saw_write[0] = True
            finally:
                rw.RUnlock()

        fw = go(writer)
        fr = go(reader)
        fw.result(timeout=5.0)
        fr.result(timeout=5.0)

        assert not reader_saw_write[0], "Reader must not enter during write"

    def test_std_rwmutex_concurrent_reads(self):
        """std.sync.RWMutex also allows concurrent reads."""
        from goated.std.sync import RWMutex

        rw = RWMutex()
        concurrent = [0]
        max_concurrent = [0]
        lock = threading.Lock()
        barrier = threading.Barrier(3)

        def reader():
            rw.RLock()
            try:
                with lock:
                    concurrent[0] += 1
                    max_concurrent[0] = max(max_concurrent[0], concurrent[0])
                barrier.wait(timeout=2.0)
                time.sleep(0.02)
                with lock:
                    concurrent[0] -= 1
            finally:
                rw.RUnlock()

        threads = [threading.Thread(target=reader) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5.0)

        assert max_concurrent[0] == 3

    def test_trylock_rlock(self):
        """TryLock and TryRLock work correctly."""
        from goated.runtime import RWMutex

        rw = RWMutex()

        assert rw.TryRLock() is True
        rw.RUnlock()

        assert rw.TryLock() is True
        # While write-locked, TryRLock should fail
        assert rw.TryRLock() is False
        rw.Unlock()


class TestSemaphore:
    """Test Semaphore primitive."""

    def test_semaphore_limits_concurrency(self):
        """Semaphore limits concurrent access."""
        from goated.runtime import GoGroup, Semaphore

        sem = Semaphore(2)
        concurrent = [0]
        max_concurrent = [0]
        lock = threading.Lock()

        def work():
            with sem:
                with lock:
                    concurrent[0] += 1
                    max_concurrent[0] = max(max_concurrent[0], concurrent[0])
                time.sleep(0.02)
                with lock:
                    concurrent[0] -= 1

        with GoGroup() as g:
            for _ in range(10):
                g.go(work)

        assert max_concurrent[0] <= 2

    def test_semaphore_try_acquire(self):
        """TryAcquire is non-blocking."""
        from goated.runtime import Semaphore

        sem = Semaphore(1)
        assert sem.TryAcquire() is True
        assert sem.TryAcquire() is False
        sem.Release()
        assert sem.TryAcquire() is True
        sem.Release()

    def test_semaphore_weighted(self):
        """Semaphore supports weighted acquire/release."""
        from goated.runtime import Semaphore

        sem = Semaphore(5)
        assert sem.TryAcquire(3) is True
        assert sem.TryAcquire(3) is False  # Only 2 left
        assert sem.TryAcquire(2) is True
        sem.Release(5)

    def test_semaphore_timeout(self):
        """Acquire with timeout."""
        from goated.runtime import Semaphore

        sem = Semaphore(0)
        result = sem.Acquire(timeout=0.05)
        assert result is False


class TestPipe:
    """Test pipe() channel helper."""

    def test_basic_pipe(self):
        """Pipe transforms values between channels."""
        from goated.runtime import Chan, go, pipe

        src = Chan[int](buffer=5)
        dst = pipe(src, lambda x: x * 2, buffer=5)

        def produce():
            for i in range(5):
                src.Send(i)
            src.Close()

        go(produce)
        results = list(dst)
        assert results == [0, 2, 4, 6, 8]

    def test_pipe_chain(self):
        """Multiple pipes can be chained."""
        from goated.runtime import Chan, go, pipe

        ch1 = Chan[int](buffer=5)
        ch2 = pipe(ch1, lambda x: x + 1, buffer=5)
        ch3 = pipe(ch2, lambda x: x * 10, buffer=5)

        def produce():
            for i in range(3):
                ch1.Send(i)
            ch1.Close()

        go(produce)
        results = list(ch3)
        assert results == [10, 20, 30]


class TestMerge:
    """Test merge() fan-in helper."""

    def test_merge_two_channels(self):
        """Merge combines values from multiple channels."""
        from goated.runtime import Chan, go, merge

        ch1 = Chan[int](buffer=5)
        ch2 = Chan[int](buffer=5)
        merged = merge(ch1, ch2, buffer=10)

        def produce1():
            for i in [1, 3, 5]:
                ch1.Send(i)
            ch1.Close()

        def produce2():
            for i in [2, 4, 6]:
                ch2.Send(i)
            ch2.Close()

        go(produce1)
        go(produce2)
        results = sorted(merged)
        assert results == [1, 2, 3, 4, 5, 6]


class TestFanOut:
    """Test fan_out() distribution helper."""

    def test_fan_out_distributes(self):
        """fan_out distributes values round-robin."""
        from goated.runtime import Chan, fan_out, go

        src = Chan[int](buffer=10)
        outputs = fan_out(src, 3, buffer=5)

        def produce():
            for i in range(9):
                src.Send(i)
            src.Close()

        go(produce)

        all_values = []
        for ch in outputs:
            all_values.extend(list(ch))

        assert sorted(all_values) == list(range(9))


class TestPoolTLS:
    """Test Pool with thread-local fast path."""

    def test_pool_basic(self):
        """Pool Get/Put works."""
        from goated.runtime import Pool

        pool = Pool[list](new=lambda: [0] * 10)

        obj = pool.Get()
        assert obj is not None
        assert len(obj) == 10

        pool.Put(obj)
        obj2 = pool.Get()
        assert obj2 is obj  # Should get same object back from TLS

    def test_pool_thread_local_fast_path(self):
        """Pool uses thread-local caching - same thread gets TLS, overflow goes to shared."""
        from goated.runtime import Pool

        pool = Pool[int]()

        # First Put goes to TLS
        pool.Put(42)
        # Second Put overflows to shared pool (TLS slot is taken)
        pool.Put(99)

        # First Get returns TLS cached value (42)
        assert pool.Get() == 42
        # Second Get goes to shared pool (99)
        assert pool.Get() == 99
        # Third Get returns None (empty)
        assert pool.Get() is None


class TestGoroutineDecorator:
    """Test that goroutine decorator preserves metadata."""

    def test_preserves_name_and_doc(self):
        """@goroutine preserves function name and docstring."""
        from goated.runtime import goroutine

        @goroutine
        def my_func():
            """My docstring."""
            return 42

        assert my_func.__name__ == "my_func"
        assert my_func.__doc__ == "My docstring."

    def test_preserves_module(self):
        """@goroutine preserves __module__."""
        from goated.runtime import goroutine

        @goroutine
        def my_func():
            return 1

        assert my_func.__module__ == __name__


class TestMutexContextManager:
    """Test Mutex and RWMutex as context managers."""

    def test_mutex_context(self):
        """Mutex works as context manager."""
        from goated.runtime import Mutex

        mu = Mutex()
        with mu:
            assert not mu.TryLock()  # Already locked
        assert mu.TryLock()  # Now free
        mu.Unlock()

    def test_rwmutex_rlocker(self):
        """RWMutex RLocker context manager."""
        from goated.runtime import RWMutex

        rw = RWMutex()
        with rw.RLocker(), rw.RLocker():
            pass  # Nested reads should be OK
