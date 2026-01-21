"""Performance testing for health check endpoints."""

import requests
import time
import statistics
from typing import List, Dict

BASE_URL = "http://localhost:8000"
WARMUP_REQUESTS = 20
TEST_REQUESTS = 500


def measure_endpoint_performance(endpoint: str, num_requests: int) -> List[float]:
    """Measure endpoint performance.

    Returns:
        List of response times in milliseconds
    """
    response_times = []

    for _ in range(num_requests):
        start_time = time.perf_counter()
        response = requests.get(f"{BASE_URL}{endpoint}")
        end_time = time.perf_counter()

        if response.status_code == 200:
            response_times.append((end_time - start_time) * 1000)

    return response_times


def calculate_statistics(response_times: List[float]) -> Dict[str, float]:
    """Calculate performance statistics."""
    return {
        "min": min(response_times),
        "max": max(response_times),
        "mean": statistics.mean(response_times),
        "median": statistics.median(response_times),
        "p95": statistics.quantiles(response_times, n=20)[18],
        "p99": statistics.quantiles(response_times, n=100)[98],
    }


def main():
    """Run health endpoint performance tests."""
    print("="*60)
    print("Health Endpoint Performance Testing")
    print("="*60)

    endpoints = ["/health", "/health/live", "/health/ready"]

    for endpoint in endpoints:
        # Warmup
        print(f"\nWarming up {endpoint}...")
        measure_endpoint_performance(endpoint, WARMUP_REQUESTS)

        # Test
        print(f"Testing {endpoint} ({TEST_REQUESTS} requests)...")
        times = measure_endpoint_performance(endpoint, TEST_REQUESTS)
        stats = calculate_statistics(times)

        print(f"\nResults for {endpoint}:")
        print(f"  Min:       {stats['min']:>6.2f} ms")
        print(f"  Max:       {stats['max']:>6.2f} ms")
        print(f"  Mean:      {stats['mean']:>6.2f} ms")
        print(f"  Median:    {stats['median']:>6.2f} ms")
        print(f"  95th:      {stats['p95']:>6.2f} ms")
        print(f"  99th:      {stats['p99']:>6.2f} ms")
        print(f"  Throughput: {1000/stats['mean']:>6.0f} req/sec")

    print("\n" + "="*60)


if __name__ == "__main__":
    main()