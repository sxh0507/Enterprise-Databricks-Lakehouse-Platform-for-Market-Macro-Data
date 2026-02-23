from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Sequence, Any


_INTERVAL_MAP = {
    "1m": timedelta(minutes=1),
    "1h": timedelta(hours=1),
    "1d": timedelta(days=1),
}


def interval_to_timedelta(interval: str) -> timedelta:
    if interval not in _INTERVAL_MAP:
        raise ValueError(f"Unsupported interval: {interval}")
    return _INTERVAL_MAP[interval]


def parse_coinbase_kline(kline: Sequence[Any], interval: str = "1m") -> Dict[str, Any]:
    """
    Coinbase candle format: [time, low, high, open, close, volume]
    time is epoch seconds.
    """
    if len(kline) < 6:
        raise ValueError("kline length must be >= 6")

    bar_start_ts = datetime.fromtimestamp(int(kline[0]), tz=timezone.utc)
    delta = interval_to_timedelta(interval)

    return {
        "bar_start_ts": bar_start_ts,
        "bar_end_ts": bar_start_ts + delta,
        "low": float(kline[1]),
        "high": float(kline[2]),
        "open": float(kline[3]),
        "close": float(kline[4]),
        "volume": float(kline[5]),
    }


def parse_coinbase_payload(payload: Dict[str, Any], interval: str = "1m") -> List[Dict[str, Any]]:
    klines = payload.get("klines", []) or []
    out: List[Dict[str, Any]] = []
    for k in klines:
        try:
            out.append(parse_coinbase_kline(k, interval=interval))
        except Exception:
            # keep parser fault-tolerant for dirty bronze payloads
            continue
    return out
