from datetime import datetime, timezone, timedelta

from lakehouse.observability_rules import (
    freshness_minutes,
    status_from_freshness,
    null_rate,
    duplicate_rate,
)


def test_freshness_and_status():
    now = datetime(2025, 1, 1, 1, 0, 0, tzinfo=timezone.utc)
    ts = now - timedelta(minutes=20)
    f = freshness_minutes(ts, now_utc=now)
    assert round(f, 2) == 20.0
    assert status_from_freshness(f, warn_min=30, fail_min=180) == "OK"
    assert status_from_freshness(40, warn_min=30, fail_min=180) == "WARN"
    assert status_from_freshness(200, warn_min=30, fail_min=180) == "FAIL"


def test_null_and_duplicate_rate():
    rows = [
        {"a": 1, "b": None, "k": 1},
        {"a": None, "b": 2, "k": 1},
        {"a": 3, "b": 4, "k": 2},
    ]
    nr = null_rate(rows, ["a", "b"])
    dr = duplicate_rate(rows, ["k"])
    assert nr > 0
    assert dr > 0
