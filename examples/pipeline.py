#!/usr/bin/env python3
"""Data processing pipeline using goated channels.

Demonstrates:
- Multi-stage pipeline with channels
- Fan-out/fan-in patterns
- Backpressure handling
- Pipeline composition
- Metrics collection
"""

import random
import time
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from typing import Generic, TypeVar

from goated.std import crypto, fmt, strings
from goated.std.goroutine import Chan, GoGroup, Mutex, go

T = TypeVar("T")
U = TypeVar("U")


@dataclass
class PipelineMetrics:
    stage_name: str
    items_processed: int = 0
    total_time_ms: int = 0
    errors: int = 0

    @property
    def avg_time_ms(self) -> float:
        return self.total_time_ms / self.items_processed if self.items_processed > 0 else 0


class Stage(Generic[T, U]):
    """A single stage in a processing pipeline."""

    def __init__(
        self,
        name: str,
        process_fn: Callable[[T], U],
        workers: int = 1,
        buffer_size: int = 10,
    ):
        self.name = name
        self.process_fn = process_fn
        self.workers = workers
        self.buffer_size = buffer_size
        self.metrics = PipelineMetrics(stage_name=name)
        self._metrics_lock = Mutex()

    def _worker(self, input_ch: Chan[T], output_ch: Chan[U]) -> None:
        """Worker that processes items from input channel."""
        for item in input_ch:
            start = time.perf_counter_ns()
            try:
                result = self.process_fn(item)
                duration_ms = int((time.perf_counter_ns() - start) / 1_000_000)

                output_ch.Send(result)

                with self._metrics_lock:
                    self.metrics.items_processed += 1
                    self.metrics.total_time_ms += duration_ms

            except Exception:
                with self._metrics_lock:
                    self.metrics.errors += 1

    def run(self, input_ch: Chan[T]) -> Chan[U]:
        """Start the stage and return output channel."""
        output_ch: Chan[U] = Chan[U](buffer=self.buffer_size)

        def run_workers():
            with GoGroup() as g:
                for _ in range(self.workers):
                    g.go(self._worker, input_ch, output_ch)
            output_ch.Close()

        go(run_workers)
        return output_ch


class Pipeline:
    """A multi-stage data processing pipeline."""

    def __init__(self, name: str):
        self.name = name
        self.stages: list[Stage] = []

    def add_stage(self, stage: Stage) -> "Pipeline":
        """Add a stage to the pipeline."""
        self.stages.append(stage)
        return self

    def run(self, input_data: Iterator[T]) -> Chan:
        """Run the pipeline with input data."""
        input_ch: Chan = Chan(buffer=100)

        def feed_input():
            for item in input_data:
                input_ch.Send(item)
            input_ch.Close()

        go(feed_input)

        current_ch = input_ch
        for stage in self.stages:
            current_ch = stage.run(current_ch)

        return current_ch

    def print_metrics(self) -> None:
        """Print metrics for all stages."""
        print(fmt.Sprintf("\n  Pipeline: %s", self.name))
        print("  " + "-" * 50)
        print("  Stage              Items    Errors   Avg Time")
        print("  " + "-" * 50)

        for stage in self.stages:
            m = stage.metrics
            print(
                fmt.Sprintf(
                    "  %-18s %6d   %6d   %6.1fms",
                    m.stage_name,
                    m.items_processed,
                    m.errors,
                    m.avg_time_ms,
                )
            )


@dataclass
class DataRecord:
    id: int
    raw_text: str
    processed_text: str = ""
    word_count: int = 0
    hash_value: str = ""
    metadata: dict | None = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


def example_simple_pipeline():
    """Simple three-stage pipeline."""
    print("=" * 60)
    print("  SIMPLE THREE-STAGE PIPELINE")
    print("=" * 60)

    def stage1_clean(record: DataRecord) -> DataRecord:
        """Clean and normalize text."""
        time.sleep(0.005)
        record.processed_text = strings.TrimSpace(record.raw_text)
        record.processed_text = strings.ToLower(record.processed_text)
        return record

    def stage2_analyze(record: DataRecord) -> DataRecord:
        """Analyze text content."""
        time.sleep(0.008)
        words = strings.Fields(record.processed_text)
        record.word_count = len(words)
        if record.metadata is None:
            record.metadata = {}
        record.metadata["unique_words"] = len(set(words))
        return record

    def stage3_hash(record: DataRecord) -> DataRecord:
        """Generate content hash."""
        time.sleep(0.003)
        hash_bytes = crypto.sha256.SumBytes(record.processed_text)
        record.hash_value = hash_bytes[:16].hex()
        return record

    pipeline = Pipeline("text-processing")
    pipeline.add_stage(Stage("clean", stage1_clean, workers=2))
    pipeline.add_stage(Stage("analyze", stage2_analyze, workers=4))
    pipeline.add_stage(Stage("hash", stage3_hash, workers=2))

    sample_texts = [
        "  Hello World  ",
        "The quick brown fox jumps over the lazy dog",
        "Python is a great programming language",
        "Go channels are awesome for concurrency",
        "Data pipelines process information efficiently",
        "Machine learning models need clean data",
        "The weather is nice today",
        "Coffee helps programmers code better",
        "Open source software powers the internet",
        "Cloud computing enables scalability",
    ]

    records = [DataRecord(id=i, raw_text=text) for i, text in enumerate(sample_texts)]

    print(fmt.Sprintf("\n  Processing %d records through 3 stages...", len(records)))
    start = time.perf_counter()

    output_ch = pipeline.run(iter(records))

    results = []
    for record in output_ch:
        results.append(record)

    elapsed = time.perf_counter() - start

    print("\n  Sample results:")
    for r in results[:3]:
        print(fmt.Sprintf("    [%d] words=%d, hash=%s", r.id, r.word_count, r.hash_value))

    pipeline.print_metrics()
    print(fmt.Sprintf("\n  Total time: %.3fs", elapsed))


def example_fan_out_fan_in():
    """Fan-out/fan-in pattern for CPU-intensive work."""
    print("\n" + "=" * 60)
    print("  FAN-OUT/FAN-IN PATTERN")
    print("=" * 60)

    def generate_numbers(n: int) -> Iterator[int]:
        yield from range(n)

    def expensive_computation(x: int) -> dict:
        """Simulate CPU-intensive work."""
        time.sleep(0.01)
        result = x * x
        for _ in range(100):
            result = (result * 31337) % 1000000007
        return {"input": x, "result": result}

    input_ch: Chan[int] = Chan[int](buffer=100)
    output_ch: Chan[dict] = Chan[dict](buffer=100)
    num_workers = 8
    num_items = 50

    def producer():
        for i in range(num_items):
            input_ch.Send(i)
        input_ch.Close()

    def worker():
        for x in input_ch:
            result = expensive_computation(x)
            output_ch.Send(result)

    def collector() -> list[dict]:
        results = []
        for r in output_ch:
            results.append(r)
        return results

    print(fmt.Sprintf("\n  Processing %d items with %d workers...", num_items, num_workers))
    start = time.perf_counter()

    go(producer)

    with GoGroup() as g:
        for _ in range(num_workers):
            g.go(worker)

    output_ch.Close()

    results = []
    for r in output_ch:
        results.append(r)

    elapsed = time.perf_counter() - start

    print(fmt.Sprintf("  Processed %d items in %.3fs", len(results), elapsed))
    print(fmt.Sprintf("  Throughput: %.1f items/sec", num_items / elapsed))


def example_streaming_etl():
    """Streaming ETL pipeline with backpressure."""
    print("\n" + "=" * 60)
    print("  STREAMING ETL PIPELINE")
    print("=" * 60)

    @dataclass
    class Event:
        id: int
        event_type: str
        user_id: int
        value: float
        timestamp: float

    def generate_events(n: int) -> Iterator[Event]:
        event_types = ["click", "purchase", "view", "signup"]
        for i in range(n):
            yield Event(
                id=i,
                event_type=random.choice(event_types),
                user_id=random.randint(1, 100),
                value=random.uniform(0, 100),
                timestamp=time.time(),
            )

    def extract(event: Event) -> dict:
        """Extract stage - parse and validate."""
        time.sleep(0.002)
        return {
            "id": event.id,
            "type": event.event_type,
            "user": event.user_id,
            "value": event.value,
            "ts": event.timestamp,
        }

    def transform(record: dict) -> dict:
        """Transform stage - enrich and normalize."""
        time.sleep(0.003)
        record["value_category"] = "high" if record["value"] > 50 else "low"
        record["type_code"] = strings.ToUpper(record["type"][:3])
        return record

    def load(record: dict) -> dict:
        """Load stage - simulate database write."""
        time.sleep(0.001)
        record["stored"] = True
        return record

    pipeline = Pipeline("streaming-etl")
    pipeline.add_stage(Stage("extract", extract, workers=2, buffer_size=20))
    pipeline.add_stage(Stage("transform", transform, workers=4, buffer_size=30))
    pipeline.add_stage(Stage("load", load, workers=2, buffer_size=20))

    num_events = 100
    print(fmt.Sprintf("\n  Streaming %d events through ETL pipeline...", num_events))

    start = time.perf_counter()
    output_ch = pipeline.run(generate_events(num_events))

    results = []
    for record in output_ch:
        results.append(record)

    elapsed = time.perf_counter() - start

    by_type: dict[str, int] = {}
    for r in results:
        t = r["type_code"]
        by_type[t] = by_type.get(t, 0) + 1

    print("\n  Events by type:")
    for event_type, count in sorted(by_type.items()):
        print(fmt.Sprintf("    %s: %d", event_type, count))

    pipeline.print_metrics()
    print(fmt.Sprintf("\n  Total time: %.3fs", elapsed))
    print(fmt.Sprintf("  Throughput: %.1f events/sec", num_events / elapsed))


def main():
    print("\n" + "=" * 60)
    print("  DATA PIPELINE EXAMPLES")
    print("  Channel-based pipelines with goated")
    print("=" * 60 + "\n")

    example_simple_pipeline()
    example_fan_out_fan_in()
    example_streaming_etl()

    print("\n" + "=" * 60)
    print("  ALL PIPELINE EXAMPLES COMPLETED")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
