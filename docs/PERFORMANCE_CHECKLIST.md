# Performance Checklist

Use this checklist to validate performance before and after optimization changes.

## 1) API Baseline

- Run the latency benchmark against a stable test dataset.
- Capture p50, p95, p99, error rate, and throughput.
- Test with at least two profiles:
  - Read-heavy (report/dashboard/list endpoints)
  - Mixed read/write (sales + reports)

Example:

```bash
python scripts/benchmark_latency.py --base-url http://localhost:8000 --token "<jwt>" --requests 300 --concurrency 20
```

## 2) Database Health

- Confirm key indexes exist on hot predicates and joins.
- Run query plans for slow endpoints using EXPLAIN ANALYZE.
- Verify no sequential scans on large tables for hot queries.
- Check lock and wait behavior during write-heavy flows.

Recommended SQL checks:

```sql
EXPLAIN ANALYZE SELECT * FROM sales WHERE status = 'COMPLETED' AND shop_id = 1 AND date >= '2026-01-01';
EXPLAIN ANALYZE SELECT * FROM sale_items WHERE sale_id = 12345;
EXPLAIN ANALYZE SELECT * FROM sale_items WHERE product_id = 100;
```

## 3) Transaction Behavior

- Ensure sales write flow uses one transaction per request.
- Confirm stock updates do not commit per line item.
- Validate rollback behavior on partial failures.

## 4) Endpoint Payload and Pagination

- Verify list endpoints use pagination defaults.
- Keep default page size bounded (for example 100).
- Ensure clients can request next pages correctly.

## 5) Reports and Aggregates

- Confirm report generation avoids N+1 lookups.
- Confirm totals/counts are computed in SQL, not Python loops over full tables.
- Re-run benchmark for report endpoints with large date ranges.

## 6) Background and Long-running Jobs

- Do not execute backup/migration heavy subprocesses in user-facing request paths.
- Move backup/email-heavy tasks to background workers if possible.
- Measure API latency while long-running jobs execute.

## 7) Operational Readiness

- Enable DB connection liveness settings (pool_pre_ping) in production.
- Set worker process count according to CPU and workload.
- Add endpoint-level latency dashboards and alerts for p95/p99 regression.

## 8) Before/After Sign-off

- Save benchmark results for both versions.
- Compare p95, p99, and error rate.
- Approve only if there is no correctness regression and latency improves.
