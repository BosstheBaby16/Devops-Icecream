#!/usr/bin/env python3
"""
==============================================================
Load Testing Script for IceCream Application
==============================================================
Simulates 500 concurrent requests over 60 seconds and reports:
- Total requests sent
- Success / error rates
- Min / Max / Average / P95 / P99 latency
- Requests per second

Usage:
    pip install aiohttp
    python load_test.py --url http://<MINIKUBE_IP>:30080 --users 500 --duration 60
"""


import asyncio
import aiohttp
import argparse
import time
import statistics
from datetime import datetime


# -------------------------------------------------------
# Result Tracker (thread-safe via asyncio)
# -------------------------------------------------------
class ResultTracker:
    def __init__(self):
        self.latencies = []
        self.errors = []
        self.status_codes = {}
        self.start_time = None
        self.end_time = None

    def record_success(self, latency_ms: float, status: int):
        self.latencies.append(latency_ms)
        self.status_codes[status] = self.status_codes.get(status, 0) + 1

    def record_error(self, error: str):
        self.errors.append(error)

    def total_requests(self):
        return len(self.latencies) + len(self.errors)

    def success_rate(self):
        total = self.total_requests()
        return (len(self.latencies) / total * 100) if total > 0 else 0

    def percentile(self, p):
        if not self.latencies:
            return 0
        sorted_lat = sorted(self.latencies)
        idx = int(len(sorted_lat) * p / 100)
        return sorted_lat[min(idx, len(sorted_lat) - 1)]

    def print_report(self):
        duration = self.end_time - self.start_time
        total = self.total_requests()
        rps = total / duration if duration > 0 else 0

        print("\n" + "=" * 55)
        print("       LOAD TEST RESULTS - IceCream App")
        print("=" * 55)
        print(f"  Duration          : {duration:.2f} seconds")
        print(f"  Total Requests    : {total}")
        print(f"  Successful        : {len(self.latencies)}")
        print(f"  Failed            : {len(self.errors)}")
        print(f"  Success Rate      : {self.success_rate():.2f}%")
        print(f"  Requests/sec      : {rps:.2f}")
        print("-" * 55)
        if self.latencies:
            print(f"  Min Latency       : {min(self.latencies):.2f} ms")
            print(f"  Max Latency       : {max(self.latencies):.2f} ms")
            print(f"  Avg Latency       : {statistics.mean(self.latencies):.2f} ms")
            print(f"  Median Latency    : {statistics.median(self.latencies):.2f} ms")
            print(f"  P95 Latency       : {self.percentile(95):.2f} ms")
            print(f"  P99 Latency       : {self.percentile(99):.2f} ms")
        print("-" * 55)
        print("  HTTP Status Codes :")
        for code, count in sorted(self.status_codes.items()):
            print(f"    {code}               : {count}")
        if self.errors:
            print("-" * 55)
            print(f"  Sample Errors (first 5):")
            for e in self.errors[:5]:
                print(f"    {e}")
        print("=" * 55)


# -------------------------------------------------------
# Single Request Worker
# -------------------------------------------------------
async def make_request(session: aiohttp.ClientSession, url: str, tracker: ResultTracker):
    """Send a single GET request and record results."""
    start = time.perf_counter()
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
            await response.read()  # Fully consume response
            latency_ms = (time.perf_counter() - start) * 1000
            tracker.record_success(latency_ms, response.status)
    except asyncio.TimeoutError:
        tracker.record_error("Timeout")
    except aiohttp.ClientConnectorError as e:
        tracker.record_error(f"ConnectionError: {str(e)[:60]}")
    except Exception as e:
        tracker.record_error(f"Error: {type(e).__name__}: {str(e)[:60]}")


# -------------------------------------------------------
# Load Generator
# -------------------------------------------------------
async def run_load_test(url: str, concurrent_users: int, duration: int):
    """
    Spawn `concurrent_users` workers that continuously send requests
    for `duration` seconds.
    """
    tracker = ResultTracker()
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Starting load test...")
    print(f"  Target URL        : {url}")
    print(f"  Concurrent Users  : {concurrent_users}")
    print(f"  Duration          : {duration}s")
    print(f"  Minimum Requests  : 500\n")

    connector = aiohttp.TCPConnector(limit=concurrent_users, limit_per_host=concurrent_users)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        tracker.start_time = time.time()
        deadline = tracker.start_time + duration

        async def worker():
            """A single virtual user that keeps making requests until deadline."""
            while time.time() < deadline:
                await make_request(session, url, tracker)

        # Launch all workers concurrently
        tasks = [asyncio.create_task(worker()) for _ in range(concurrent_users)]

        # Progress reporter
        async def progress():
            while time.time() < deadline:
                elapsed = time.time() - tracker.start_time
                print(
                    f"\r  [{elapsed:5.1f}s] Requests: {tracker.total_requests():5d}  "
                    f"Success: {len(tracker.latencies):5d}  "
                    f"Errors: {len(tracker.errors):4d}",
                    end="",
                    flush=True,
                )
                await asyncio.sleep(1)

        await asyncio.gather(*tasks, progress())
        tracker.end_time = time.time()

    tracker.print_report()


# -------------------------------------------------------
# Entry Point
# -------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load test the IceCream application")
    parser.add_argument(
        "--url",
        default="http://localhost:30080",
        help="Target URL (default: http://localhost:30080)",
    )
    parser.add_argument(
        "--users",
        type=int,
        default=500,
        help="Number of concurrent users (default: 500)",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=60,
        help="Test duration in seconds (default: 60)",
    )
    args = parser.parse_args()

    asyncio.run(run_load_test(args.url, args.users, args.duration))
