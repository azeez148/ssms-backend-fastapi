#!/usr/bin/env python3
import argparse
import asyncio
import json
import math
import random
import statistics
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import httpx


@dataclass
class RequestResult:
    name: str
    ok: bool
    status_code: int
    latency_ms: float
    error: Optional[str] = None


def percentile(sorted_values: List[float], p: float) -> float:
    if not sorted_values:
        return 0.0
    if len(sorted_values) == 1:
        return sorted_values[0]
    rank = (p / 100.0) * (len(sorted_values) - 1)
    low = math.floor(rank)
    high = math.ceil(rank)
    if low == high:
        return sorted_values[low]
    frac = rank - low
    return sorted_values[low] + (sorted_values[high] - sorted_values[low]) * frac


def build_default_endpoints() -> List[Tuple[str, str]]:
    # Weighted by repetition to simulate realistic mixed load.
    return [
        ("sales_total", "GET /sales/total"),
        ("sales_recent", "GET /sales/recent"),
        ("sales_all", "GET /sales/all?skip=0&limit=100"),
        ("products_all", "GET /products/all"),
        ("reports_today", "GET /reports/sales/today"),
        ("reports_month", "GET /reports/sales/this-month"),
        ("dashboard", "GET /dashboard/all"),
        ("sales_total", "GET /sales/total"),
        ("sales_recent", "GET /sales/recent"),
        ("reports_today", "GET /reports/sales/today"),
    ]


def parse_endpoint_spec(spec: str) -> Tuple[str, str, str]:
    # Format: "name|METHOD|/path"
    parts = spec.split("|", 2)
    if len(parts) != 3:
        raise ValueError(f"Invalid --endpoint format: {spec}")
    name, method, path = parts[0].strip(), parts[1].strip().upper(), parts[2].strip()
    if not path.startswith("/"):
        raise ValueError(f"Endpoint path must start with '/': {spec}")
    return name, method, path


async def run_one(
    client: httpx.AsyncClient,
    name: str,
    method: str,
    path: str,
) -> RequestResult:
    start = time.perf_counter()
    try:
        response = await client.request(method, path)
        elapsed_ms = (time.perf_counter() - start) * 1000
        ok = 200 <= response.status_code < 400
        return RequestResult(name=name, ok=ok, status_code=response.status_code, latency_ms=elapsed_ms)
    except Exception as exc:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return RequestResult(name=name, ok=False, status_code=0, latency_ms=elapsed_ms, error=str(exc))


async def worker(
    worker_id: int,
    queue: asyncio.Queue,
    client: httpx.AsyncClient,
    results: List[RequestResult],
):
    del worker_id
    while True:
        item = await queue.get()
        if item is None:
            queue.task_done()
            return
        name, method, path = item
        result = await run_one(client, name, method, path)
        results.append(result)
        queue.task_done()


def summarize(results: List[RequestResult]) -> Dict[str, object]:
    latencies = sorted(r.latency_ms for r in results)
    ok_count = sum(1 for r in results if r.ok)
    err_count = len(results) - ok_count
    by_status: Dict[str, int] = {}
    for r in results:
        key = str(r.status_code)
        by_status[key] = by_status.get(key, 0) + 1

    per_endpoint: Dict[str, Dict[str, object]] = {}
    for r in results:
        group = per_endpoint.setdefault(r.name, {"latencies": [], "ok": 0, "err": 0})
        group["latencies"].append(r.latency_ms)
        if r.ok:
            group["ok"] += 1
        else:
            group["err"] += 1

    endpoint_summary: Dict[str, Dict[str, object]] = {}
    for name, group in per_endpoint.items():
        vals = sorted(group["latencies"])
        endpoint_summary[name] = {
            "count": len(vals),
            "ok": group["ok"],
            "err": group["err"],
            "avg_ms": round(statistics.mean(vals), 2) if vals else 0.0,
            "p50_ms": round(percentile(vals, 50), 2),
            "p95_ms": round(percentile(vals, 95), 2),
            "p99_ms": round(percentile(vals, 99), 2),
        }

    return {
        "count": len(results),
        "ok": ok_count,
        "err": err_count,
        "error_rate": round((err_count / len(results)) * 100, 2) if results else 0.0,
        "avg_ms": round(statistics.mean(latencies), 2) if latencies else 0.0,
        "p50_ms": round(percentile(latencies, 50), 2),
        "p95_ms": round(percentile(latencies, 95), 2),
        "p99_ms": round(percentile(latencies, 99), 2),
        "status_counts": by_status,
        "by_endpoint": endpoint_summary,
    }


async def main_async(args: argparse.Namespace) -> Dict[str, object]:
    headers = {}
    if args.token:
        headers["Authorization"] = f"Bearer {args.token}"

    timeout = httpx.Timeout(args.timeout_seconds)
    limits = httpx.Limits(max_keepalive_connections=args.concurrency, max_connections=args.concurrency * 2)

    if args.endpoint:
        endpoint_pool = [parse_endpoint_spec(spec) for spec in args.endpoint]
    else:
        endpoint_pool = []
        for name, spec in build_default_endpoints():
            method, path = spec.split(" ", 1)
            endpoint_pool.append((name, method, path))

    queue: asyncio.Queue = asyncio.Queue()
    results: List[RequestResult] = []

    for _ in range(args.requests):
        queue.put_nowait(random.choice(endpoint_pool))

    async with httpx.AsyncClient(base_url=args.base_url.rstrip("/"), headers=headers, timeout=timeout, limits=limits) as client:
        workers = [asyncio.create_task(worker(i, queue, client, results)) for i in range(args.concurrency)]
        await queue.join()
        for _ in workers:
            queue.put_nowait(None)
        await queue.join()
        await asyncio.gather(*workers)

    summary = summarize(results)
    summary["meta"] = {
        "base_url": args.base_url,
        "requests": args.requests,
        "concurrency": args.concurrency,
        "timeout_seconds": args.timeout_seconds,
    }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Lightweight API latency benchmark for before/after comparison.")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--token", default=None, help="Bearer token for authenticated routes")
    parser.add_argument("--requests", type=int, default=300, help="Total request count")
    parser.add_argument("--concurrency", type=int, default=20, help="Concurrent workers")
    parser.add_argument("--timeout-seconds", type=float, default=20.0, help="Per-request timeout")
    parser.add_argument(
        "--endpoint",
        action="append",
        help="Custom endpoint in the format name|METHOD|/path. Repeat for multiple endpoints.",
    )
    parser.add_argument("--out", default=None, help="Optional JSON output path")

    args = parser.parse_args()

    started = time.perf_counter()
    summary = asyncio.run(main_async(args))
    summary["duration_seconds"] = round(time.perf_counter() - started, 2)

    print(json.dumps(summary, indent=2))

    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(summary, fh, indent=2)


if __name__ == "__main__":
    main()
