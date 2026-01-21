"""Performance testing for /new and /validate endpoints.

This script measures endpoint performance after a warm-up period to account for:
- FastAPI startup overhead
- Template loading and caching
- Validation factory initialization
- First-time JIT compilation
"""

import requests
import time
import json
import statistics
from pathlib import Path
from typing import List, Dict, Any


BASE_URL = "http://localhost:5000/api/v1/trades"
WARMUP_REQUESTS = 50  # Number of requests to warm up the system
TEST_REQUESTS = 1000  # Number of requests for actual measurement


def load_test_trade_data() -> Dict[str, Any]:
    """Load IR swap test data for /validate endpoint."""
    test_file = Path(__file__).parent.parent.parent / "json-examples" / "polar" / "ir-swap-presave-flattened.json"
    with open(test_file, 'r') as f:
        return json.load(f)


def test_new_endpoint_warmup(num_requests: int) -> None:
    """Warm up the /new endpoint."""
    print(f"Warming up /new endpoint with {num_requests} requests...")
    for _ in range(num_requests):
        requests.get(f"{BASE_URL}/new", params={"trade_type": "ir-swap"})
    print("✓ /new endpoint warmed up")


def test_validate_endpoint_warmup(num_requests: int, trade_data: Dict[str, Any]) -> None:
    """Warm up the /validate endpoint."""
    print(f"Warming up /validate endpoint with {num_requests} requests...")
    for _ in range(num_requests):
        requests.post(f"{BASE_URL}/validate", json={"trade_data": trade_data})
    print("✓ /validate endpoint warmed up")


def measure_new_endpoint_performance(num_requests: int) -> List[float]:
    """Measure /new endpoint performance after warm-up.

    Returns:
        List of response times in milliseconds
    """
    print(f"\nMeasuring /new endpoint performance ({num_requests} requests)...")
    response_times = []

    for i in range(num_requests):
        start_time = time.perf_counter()
        response = requests.get(f"{BASE_URL}/new", params={"trade_type": "ir-swap"})
        end_time = time.perf_counter()

        if response.status_code == 200:
            response_times.append((end_time - start_time) * 1000)  # Convert to ms

        if (i + 1) % 100 == 0:
            print(f"  Progress: {i + 1}/{num_requests}")

    return response_times


def measure_validate_endpoint_performance(num_requests: int, trade_data: Dict[str, Any]) -> List[float]:
    """Measure /validate endpoint performance after warm-up.

    Returns:
        List of response times in milliseconds
    """
    print(f"\nMeasuring /validate endpoint performance ({num_requests} requests)...")
    response_times = []

    for i in range(num_requests):
        start_time = time.perf_counter()
        response = requests.post(f"{BASE_URL}/validate", json={"trade_data": trade_data})
        end_time = time.perf_counter()

        if response.status_code == 200:
            response_times.append((end_time - start_time) * 1000)  # Convert to ms

        if (i + 1) % 100 == 0:
            print(f"  Progress: {i + 1}/{num_requests}")

    return response_times


def calculate_statistics(response_times: List[float]) -> Dict[str, float]:
    """Calculate performance statistics from response times."""
    return {
        "min": min(response_times),
        "max": max(response_times),
        "mean": statistics.mean(response_times),
        "median": statistics.median(response_times),
        "p95": statistics.quantiles(response_times, n=20)[18],  # 95th percentile
        "p99": statistics.quantiles(response_times, n=100)[98],  # 99th percentile
        "stdev": statistics.stdev(response_times) if len(response_times) > 1 else 0,
    }


def print_performance_report(endpoint: str, stats: Dict[str, float], num_requests: int) -> None:
    """Print formatted performance report."""
    print(f"\n{'='*60}")
    print(f"Performance Report: {endpoint}")
    print(f"{'='*60}")
    print(f"Total Requests: {num_requests}")
    print(f"Min:            {stats['min']:>8.2f} ms")
    print(f"Max:            {stats['max']:>8.2f} ms")
    print(f"Mean:           {stats['mean']:>8.2f} ms")
    print(f"Median:         {stats['median']:>8.2f} ms")
    print(f"95th %ile:      {stats['p95']:>8.2f} ms")
    print(f"99th %ile:      {stats['p99']:>8.2f} ms")
    print(f"Std Dev:        {stats['stdev']:>8.2f} ms")
    print(f"\nThroughput:     {1000 / stats['mean']:>8.2f} req/sec (based on mean)")
    print(f"{'='*60}\n")


def main():
    """Run performance tests."""
    print("="*60)
    print("API Endpoint Performance Testing")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print(f"Warm-up requests: {WARMUP_REQUESTS}")
    print(f"Test requests: {TEST_REQUESTS}")
    print("="*60)

    # Load test data
    trade_data = load_test_trade_data()

    # Phase 1: Warm-up
    print("\n[Phase 1: Warm-up]")
    test_new_endpoint_warmup(WARMUP_REQUESTS)
    test_validate_endpoint_warmup(WARMUP_REQUESTS, trade_data)

    # Phase 2: Performance measurement
    print("\n[Phase 2: Performance Measurement]")

    # Test /new endpoint
    new_response_times = measure_new_endpoint_performance(TEST_REQUESTS)
    new_stats = calculate_statistics(new_response_times)
    print_performance_report("GET /api/v1/trades/new", new_stats, TEST_REQUESTS)

    # Test /validate endpoint
    validate_response_times = measure_validate_endpoint_performance(TEST_REQUESTS, trade_data)
    validate_stats = calculate_statistics(validate_response_times)
    print_performance_report("POST /api/v1/trades/validate", validate_stats, TEST_REQUESTS)

    # Comparison
    print("="*60)
    print("Performance Comparison")
    print("="*60)
    print(f"/new is {validate_stats['mean'] / new_stats['mean']:.2f}x {'faster' if new_stats['mean'] < validate_stats['mean'] else 'slower'} than /validate")
    print(f"  /new mean:      {new_stats['mean']:.2f} ms")
    print(f"  /validate mean: {validate_stats['mean']:.2f} ms")
    print("="*60)


if __name__ == "__main__":
    main()