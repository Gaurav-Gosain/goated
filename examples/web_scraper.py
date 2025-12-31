#!/usr/bin/env python3
"""Concurrent web scraper using goated goroutines and channels.

Demonstrates:
- GoGroup for concurrent task management
- Channels for collecting results
- Rate limiting with semaphores
- Error handling in concurrent code
"""

import random
import time
from dataclasses import dataclass

from goated.std import fmt
from goated.std.goroutine import Chan, GoGroup, Mutex


@dataclass
class PageResult:
    url: str
    title: str
    links: list[str]
    fetch_time_ms: int
    error: str | None = None


@dataclass
class ScraperStats:
    total: int = 0
    success: int = 0
    failed: int = 0
    total_time_ms: int = 0

    @property
    def avg_time_ms(self) -> float:
        return self.total_time_ms / self.success if self.success > 0 else 0


def simulate_fetch(url: str) -> PageResult:
    """Simulate fetching a URL (replace with real HTTP in production)."""
    start = time.perf_counter_ns()

    fetch_time = random.uniform(0.05, 0.2)
    time.sleep(fetch_time)

    if random.random() < 0.1:
        elapsed_ms = int((time.perf_counter_ns() - start) / 1_000_000)
        return PageResult(
            url=url,
            title="",
            links=[],
            fetch_time_ms=elapsed_ms,
            error="connection timeout",
        )

    domain = url.split("/")[2] if len(url.split("/")) > 2 else "example.com"
    path = "/" + "/".join(url.split("/")[3:]) if len(url.split("/")) > 3 else "/"

    title = fmt.Sprintf("Page: %s", path)
    links = [fmt.Sprintf("https://%s/page%d", domain, i) for i in range(random.randint(2, 5))]

    elapsed_ms = int((time.perf_counter_ns() - start) / 1_000_000)
    return PageResult(
        url=url,
        title=title,
        links=links,
        fetch_time_ms=elapsed_ms,
    )


class WebScraper:
    """Concurrent web scraper with configurable parallelism."""

    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self.stats = ScraperStats()
        self._stats_lock = Mutex()

    def _update_stats(self, result: PageResult) -> None:
        with self._stats_lock:
            self.stats.total += 1
            if result.error:
                self.stats.failed += 1
            else:
                self.stats.success += 1
                self.stats.total_time_ms += result.fetch_time_ms

    def scrape(self, urls: list[str]) -> list[PageResult]:
        """Scrape multiple URLs concurrently."""
        results: Chan[PageResult] = Chan[PageResult](buffer=len(urls))

        def fetch_url(url: str) -> None:
            result = simulate_fetch(url)
            self._update_stats(result)
            results.Send(result)

        with GoGroup(limit=self.max_concurrent) as g:
            for url in urls:
                g.go(fetch_url, url)

        results.Close()

        collected = []
        for result in results:
            collected.append(result)

        return collected

    def scrape_with_depth(
        self,
        start_urls: list[str],
        max_depth: int = 2,
        max_pages: int = 50,
    ) -> list[PageResult]:
        """Crawl starting from URLs, following links up to max_depth."""
        visited: set[str] = set()
        all_results: list[PageResult] = []
        current_urls = start_urls[:]

        for depth in range(max_depth):
            urls_to_fetch = [
                url for url in current_urls if url not in visited and len(visited) < max_pages
            ]

            if not urls_to_fetch:
                break

            for url in urls_to_fetch:
                visited.add(url)

            print(fmt.Sprintf("  Depth %d: fetching %d URLs...", depth, len(urls_to_fetch)))
            results = self.scrape(urls_to_fetch)
            all_results.extend(results)

            next_urls = []
            for result in results:
                if not result.error:
                    for link in result.links:
                        if link not in visited:
                            next_urls.append(link)

            current_urls = next_urls

        return all_results


def print_results(results: list[PageResult]) -> None:
    """Print scraping results in a formatted table."""
    print("\n  URL" + " " * 40 + "Title" + " " * 20 + "Time  Status")
    print("  " + "-" * 90)

    for r in results:
        url_short = r.url[:42] + "..." if len(r.url) > 45 else r.url.ljust(45)
        title_short = r.title[:22] + "..." if len(r.title) > 25 else r.title.ljust(25)
        status = "ERROR" if r.error else "OK"
        print(fmt.Sprintf("  %s %s %4dms %s", url_short, title_short, r.fetch_time_ms, status))


def main():
    print("=" * 60)
    print("  CONCURRENT WEB SCRAPER")
    print("  Using goated goroutines and channels")
    print("=" * 60)

    urls = [
        "https://example.com/page1",
        "https://example.com/page2",
        "https://example.com/page3",
        "https://example.com/products/item1",
        "https://example.com/products/item2",
        "https://example.com/blog/post1",
        "https://example.com/blog/post2",
        "https://example.com/blog/post3",
        "https://example.com/about",
        "https://example.com/contact",
    ]

    print(fmt.Sprintf("\n=== Scraping %d URLs with concurrency=5 ===", len(urls)))

    scraper = WebScraper(max_concurrent=5)
    start = time.perf_counter()
    results = scraper.scrape(urls)
    elapsed = time.perf_counter() - start

    print_results(results)

    print("\n=== Statistics ===")
    print(fmt.Sprintf("  Total URLs:    %d", scraper.stats.total))
    print(fmt.Sprintf("  Successful:    %d", scraper.stats.success))
    print(fmt.Sprintf("  Failed:        %d", scraper.stats.failed))
    print(fmt.Sprintf("  Avg fetch:     %.1fms", scraper.stats.avg_time_ms))
    print(fmt.Sprintf("  Total time:    %.2fs", elapsed))
    print(fmt.Sprintf("  Throughput:    %.1f pages/sec", len(urls) / elapsed))

    print("\n=== Crawling with Depth ===")
    scraper2 = WebScraper(max_concurrent=8)
    start = time.perf_counter()
    crawl_results = scraper2.scrape_with_depth(
        ["https://example.com/"],
        max_depth=3,
        max_pages=20,
    )
    elapsed = time.perf_counter() - start

    print(fmt.Sprintf("\n  Crawled %d pages in %.2fs", len(crawl_results), elapsed))
    print(
        fmt.Sprintf(
            "  Success rate: %.1f%%",
            100 * scraper2.stats.success / scraper2.stats.total if scraper2.stats.total > 0 else 0,
        )
    )

    print("\n=== Sample of crawled pages ===")
    for r in crawl_results[:5]:
        if not r.error:
            print(fmt.Sprintf("  %s -> %d links", r.url, len(r.links)))


if __name__ == "__main__":
    main()
