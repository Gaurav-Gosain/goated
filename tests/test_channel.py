"""Comprehensive tests for Go channel integration with asyncio.

Tests cover:
- Channel creation (buffered and unbuffered)
- Send and receive operations
- Async iteration
- Channel closing
- Select statement
- go() function for spawning goroutines
"""

import asyncio

import pytest

from goated import Channel, ChannelClosed, SelectCase, SelectOp, go


class TestChannelCreation:
    def test_unbuffered_channel(self):
        ch = Channel[int]()
        assert ch._buffer_size == 0
        assert not ch.closed

    def test_buffered_channel(self):
        ch = Channel[int](buffer_size=5)
        assert ch._buffer_size == 5

    def test_unlimited_buffer(self):
        ch = Channel[str](buffer_size=-1)
        assert ch._buffer_size == -1


class TestBufferedChannel:
    @pytest.mark.asyncio
    async def test_send_recv_basic(self):
        ch = Channel[int](buffer_size=3)
        await ch.send(1)
        await ch.send(2)
        await ch.send(3)

        assert await ch.recv() == 1
        assert await ch.recv() == 2
        assert await ch.recv() == 3

    @pytest.mark.asyncio
    async def test_send_nowait(self):
        ch = Channel[int](buffer_size=2)
        assert ch.send_nowait(1) is True
        assert ch.send_nowait(2) is True
        assert len(ch) == 2

    @pytest.mark.asyncio
    async def test_recv_nowait(self):
        ch = Channel[int](buffer_size=2)
        await ch.send(42)
        assert ch.recv_nowait() == 42
        assert ch.recv_nowait() is None

    @pytest.mark.asyncio
    async def test_fifo_order(self):
        ch = Channel[int](buffer_size=5)
        for i in range(5):
            await ch.send(i)

        for i in range(5):
            assert await ch.recv() == i


class TestChannelClose:
    @pytest.mark.asyncio
    async def test_close_prevents_send(self):
        ch = Channel[int](buffer_size=1)
        ch.close()

        with pytest.raises(ChannelClosed):
            await ch.send(1)

    @pytest.mark.asyncio
    async def test_close_prevents_send_nowait(self):
        ch = Channel[int](buffer_size=1)
        ch.close()

        with pytest.raises(ChannelClosed):
            ch.send_nowait(1)

    @pytest.mark.asyncio
    async def test_recv_after_close_with_data(self):
        ch = Channel[int](buffer_size=2)
        await ch.send(1)
        await ch.send(2)
        ch.close()

        assert await ch.recv() == 1
        assert await ch.recv() == 2

    @pytest.mark.asyncio
    async def test_recv_after_close_empty(self):
        ch = Channel[int](buffer_size=1)
        ch.close()

        with pytest.raises(ChannelClosed):
            await ch.recv()

    def test_closed_property(self):
        ch = Channel[int]()
        assert ch.closed is False
        ch.close()
        assert ch.closed is True


class TestAsyncIteration:
    @pytest.mark.asyncio
    async def test_async_for(self):
        ch = Channel[int](buffer_size=5)

        for i in range(5):
            await ch.send(i)
        ch.close()

        received = []
        async for value in ch:
            received.append(value)

        assert received == [0, 1, 2, 3, 4]

    @pytest.mark.asyncio
    async def test_async_for_empty_closed(self):
        ch = Channel[int](buffer_size=1)
        ch.close()

        received = []
        async for value in ch:
            received.append(value)

        assert received == []


class TestConcurrentOperations:
    @pytest.mark.asyncio
    async def test_producer_consumer(self):
        ch = Channel[int](buffer_size=3)
        received = []

        async def producer():
            for i in range(10):
                await ch.send(i)
            ch.close()

        async def consumer():
            async for value in ch:
                received.append(value)

        await asyncio.gather(producer(), consumer())
        assert received == list(range(10))

    @pytest.mark.asyncio
    async def test_multiple_consumers(self):
        ch = Channel[int](buffer_size=5)
        received = []
        lock = asyncio.Lock()

        async def producer():
            for i in range(20):
                await ch.send(i)
            ch.close()

        async def consumer(id: int):
            async for value in ch:
                async with lock:
                    received.append((id, value))

        await asyncio.gather(producer(), consumer(1), consumer(2))

        values = sorted([v for _, v in received])
        assert values == list(range(20))


class TestChannelLen:
    @pytest.mark.asyncio
    async def test_len_empty(self):
        ch = Channel[int](buffer_size=5)
        assert len(ch) == 0

    @pytest.mark.asyncio
    async def test_len_after_send(self):
        ch = Channel[int](buffer_size=5)
        await ch.send(1)
        await ch.send(2)
        assert len(ch) == 2

    @pytest.mark.asyncio
    async def test_len_after_recv(self):
        ch = Channel[int](buffer_size=5)
        await ch.send(1)
        await ch.send(2)
        await ch.recv()
        assert len(ch) == 1


class TestChannelRepr:
    def test_repr_open(self):
        ch = Channel[int](buffer_size=5)
        r = repr(ch)
        assert "open" in r
        assert "buf=5" in r

    def test_repr_closed(self):
        ch = Channel[int](buffer_size=5)
        ch.close()
        r = repr(ch)
        assert "closed" in r


class TestGo:
    def test_go_sync_function(self):
        def compute(x: int) -> int:
            return x * 2

        future = go(compute, 21)
        assert future.result(timeout=1) == 42

    def test_go_multiple(self):
        def add(a: int, b: int) -> int:
            return a + b

        futures = [go(add, i, i) for i in range(5)]
        results = [f.result(timeout=1) for f in futures]
        assert results == [0, 2, 4, 6, 8]

    @pytest.mark.asyncio
    async def test_go_async_function(self):
        async def async_compute(x: int) -> int:
            await asyncio.sleep(0.01)
            return x * 2

        future = go(async_compute, 21)
        result = await asyncio.wrap_future(future)
        assert result == 42


class TestSelectCase:
    def test_select_case_recv(self):
        ch = Channel[int](buffer_size=1)
        case = SelectCase(ch, SelectOp.RECV)
        assert case.channel is ch
        assert case.op == SelectOp.RECV

    def test_select_case_send(self):
        ch = Channel[int](buffer_size=1)
        case = SelectCase(ch, SelectOp.SEND, value=42)
        assert case.channel is ch
        assert case.op == SelectOp.SEND
        assert case.value == 42
