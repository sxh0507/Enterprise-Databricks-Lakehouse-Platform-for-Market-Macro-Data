from datetime import datetime, timezone

from lakehouse.quality_rules import is_valid_ohlc, dedupe_latest


def test_is_valid_ohlc_true():
    row = {
        "bar_start_ts": datetime(2025, 1, 1, tzinfo=timezone.utc),
        "open": 100.0,
        "high": 110.0,
        "low": 90.0,
        "close": 105.0,
        "volume": 1.0,
    }
    assert is_valid_ohlc(row) is True


def test_is_valid_ohlc_false_by_bounds():
    row = {
        "bar_start_ts": datetime(2025, 1, 1, tzinfo=timezone.utc),
        "open": 100.0,
        "high": 99.0,
        "low": 90.0,
        "close": 105.0,
        "volume": 1.0,
    }
    assert is_valid_ohlc(row) is False


def test_dedupe_latest_keeps_latest_ts():
    rows = [
        {"source": "cb", "symbol": "BTC", "bar_start_ts": 1, "ingestion_ts": 10, "close": 100},
        {"source": "cb", "symbol": "BTC", "bar_start_ts": 1, "ingestion_ts": 20, "close": 101},
    ]
    out = dedupe_latest(rows, key_fields=["source", "symbol", "bar_start_ts"], ts_field="ingestion_ts")
    assert len(out) == 1
    assert out[0]["close"] == 101
