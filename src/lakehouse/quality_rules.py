from __future__ import annotations

from typing import Dict, Iterable, List, Sequence, Tuple, Any


def is_valid_ohlc(row: Dict[str, Any]) -> bool:
    required = ["open", "high", "low", "close", "bar_start_ts"]
    if any(row.get(c) is None for c in required):
        return False

    o = float(row["open"])
    h = float(row["high"])
    l = float(row["low"])
    c = float(row["close"])
    v = float(row.get("volume", 0.0))

    if o <= 0 or h <= 0 or l <= 0 or c <= 0:
        return False
    if v < 0:
        return False
    if h < max(o, c):
        return False
    if l > min(o, c):
        return False
    return True


def dedupe_latest(
    rows: Iterable[Dict[str, Any]],
    key_fields: Sequence[str],
    ts_field: str = "ingestion_ts",
) -> List[Dict[str, Any]]:
    bucket: Dict[Tuple[Any, ...], Dict[str, Any]] = {}
    for r in rows:
        key = tuple(r.get(k) for k in key_fields)
        if key not in bucket:
            bucket[key] = r
            continue

        old_ts = bucket[key].get(ts_field)
        new_ts = r.get(ts_field)
        if new_ts is not None and (old_ts is None or new_ts >= old_ts):
            bucket[key] = r
    return list(bucket.values())
