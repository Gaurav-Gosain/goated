#!/usr/bin/env python3
"""Example demonstrating Go-style channels with Python asyncio.

Shows:
1. Buffered and unbuffered channels
2. Producer/consumer patterns
3. Async iteration
4. Multiple workers
"""

import asyncio

from goated import Channel, ChannelClosed, go


async def demo_basic_channel():
    print("=" * 50)
    print("Basic Channel Operations")
    print("=" * 50)

    ch = Channel[int](buffer_size=3)

    await ch.send(1)
    await ch.send(2)
    await ch.send(3)

    print("\nSent 3 values to buffered channel")
    print(f"Channel length: {len(ch)}")

    val1 = await ch.recv()
    val2 = await ch.recv()
    val3 = await ch.recv()

    print(f"Received: {val1}, {val2}, {val3}")
    print(f"Channel length after recv: {len(ch)}")


async def demo_producer_consumer():
    print("\n" + "=" * 50)
    print("Producer/Consumer Pattern")
    print("=" * 50)

    ch = Channel[str](buffer_size=5)

    async def producer():
        items = ["apple", "banana", "cherry", "date", "elderberry"]
        for item in items:
            await ch.send(item)
            print(f"  Produced: {item}")
        ch.close()
        print("  Producer: closed channel")

    async def consumer():
        print("  Consumer: starting")
        async for item in ch:
            print(f"  Consumed: {item}")
        print("  Consumer: channel closed, done")

    await asyncio.gather(producer(), consumer())


async def demo_multiple_workers():
    print("\n" + "=" * 50)
    print("Multiple Workers")
    print("=" * 50)

    jobs = Channel[int](buffer_size=10)
    results = Channel[str](buffer_size=10)

    async def worker(id: int):
        while True:
            try:
                job = await asyncio.wait_for(jobs.recv(), timeout=0.5)
                result = f"Worker {id} processed job {job} -> {job * 2}"
                await results.send(result)
            except (ChannelClosed, asyncio.TimeoutError):
                break

    async def dispatcher():
        for i in range(10):
            await jobs.send(i)
        jobs.close()

    async def collector():
        collected = []
        while len(collected) < 10:
            try:
                result = await asyncio.wait_for(results.recv(), timeout=1.0)
                collected.append(result)
                print(f"  {result}")
            except asyncio.TimeoutError:
                break
        results.close()
        return collected

    await asyncio.gather(dispatcher(), worker(1), worker(2), worker(3), collector())


async def demo_fan_out():
    print("\n" + "=" * 50)
    print("Fan-Out Pattern")
    print("=" * 50)

    source = Channel[int](buffer_size=5)

    async def generator():
        for i in range(1, 6):
            await source.send(i)
            print(f"  Generated: {i}")
        source.close()

    async def square_worker(id: str):
        async for n in source:
            print(f"  Worker {id}: {n}^2 = {n * n}")
            await asyncio.sleep(0.05)

    async def runner():
        gen_task = asyncio.create_task(generator())
        await asyncio.sleep(0.1)

        workers = [
            asyncio.create_task(square_worker("A")),
            asyncio.create_task(square_worker("B")),
        ]

        await gen_task
        await asyncio.gather(*workers)

    await runner()


def demo_go_function():
    print("\n" + "=" * 50)
    print("go() Function - Spawn Goroutines")
    print("=" * 50)

    def compute_factorial(n: int) -> int:
        result = 1
        for i in range(1, n + 1):
            result *= i
        return result

    futures = []
    for n in [5, 7, 10]:
        future = go(compute_factorial, n)
        futures.append((n, future))

    for n, future in futures:
        result = future.result(timeout=1.0)
        print(f"  {n}! = {result}")


async def main():
    print("\n🐐 GOATED - Async Channels Demo 🐐\n")

    await demo_basic_channel()
    await demo_producer_consumer()
    await demo_multiple_workers()
    await demo_fan_out()
    demo_go_function()

    print("\n" + "=" * 50)
    print("Done!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
