from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Sequence


def freshness_minutes(max_ts: datetime | None, now_utc: datetime | None = None) -> float:
    if max_ts is None:
        return float("inf")
    now = now_utc or datetime.now(timezone.utc)
    if max_ts.tzinfo is None:
        max_ts = max_ts.replace(tzinfo=timezone.utc)
    return (now - max_ts).total_seconds() / 60.0


def status_from_freshness(freshness_m: float, warn_min: float, fail_min: float) -> str:
    if freshness_m == float("inf") or freshness_m >= fail_min:
        return "FAIL"
    if freshness_m >= warn_min:
        return "WARN"
    return "OK"


def null_rate(rows: Iterable[Dict[str, Any]], cols: Sequence[str]) -> float:
    rows = list(rows)
    if not rows:
        return 0.0
    total = len(rows)
    total_null_frac = 0.0
    for c in cols:
        null_count = sum(1 for r in rows if r.get(c) is None)
        total_null_frac += (null_count / total)
    return total_null_frac / len(cols) if cols else 0.0


def duplicate_rate(rows: Iterable[Dict[str, Any]], key_cols: Sequence[str]) -> float:
    rows = list(rows)
    if not rows or not key_cols:
        return 0.0
    total = len(rows)
    keys = [tuple(r.get(c) for c in key_cols) for r in rows]
    distinct = len(set(keys))
    return (total - distinct) / total
