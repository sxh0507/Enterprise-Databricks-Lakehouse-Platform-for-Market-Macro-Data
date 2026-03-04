from datetime import datetime, timezone

from lakehouse.ingestion import (
    day_floor_utc,
    resolve_realtime_end_dt,
    resolve_symbol_start_for_realtime,
)


def test_day_floor_utc_normalizes_timezone_and_time():
    ts = datetime(2026, 3, 4, 10, 30, tzinfo=timezone.utc)
    assert day_floor_utc(ts) == datetime(2026, 3, 4, 0, 0, tzinfo=timezone.utc)


def test_resolve_realtime_end_dt_applies_safety_lag_across_midnight():
    now_utc = datetime(2026, 3, 4, 0, 1, tzinfo=timezone.utc)
    end_dt = resolve_realtime_end_dt(now_utc, safety_lag_minutes=2)
    assert end_dt == datetime(2026, 3, 3, 0, 0, tzinfo=timezone.utc)


def test_resolve_symbol_start_for_realtime_intraday_replays_watermark_day():
    watermark = datetime(2026, 3, 4, 15, 20, tzinfo=timezone.utc)
    end_dt = datetime(2026, 3, 5, 0, 0, tzinfo=timezone.utc)
    start = resolve_symbol_start_for_realtime(
        watermark,
        end_dt=end_dt,
        lookback_days=1,
        interval="1m",
    )
    assert start == datetime(2026, 3, 4, 0, 0, tzinfo=timezone.utc)


def test_resolve_symbol_start_for_realtime_daily_uses_next_day():
    watermark = datetime(2026, 3, 4, 15, 20, tzinfo=timezone.utc)
    end_dt = datetime(2026, 3, 6, 0, 0, tzinfo=timezone.utc)
    start = resolve_symbol_start_for_realtime(
        watermark,
        end_dt=end_dt,
        lookback_days=1,
        interval="1d",
    )
    assert start == datetime(2026, 3, 5, 0, 0, tzinfo=timezone.utc)


def test_resolve_symbol_start_for_realtime_without_watermark_uses_lookback():
    end_dt = datetime(2026, 3, 6, 0, 0, tzinfo=timezone.utc)
    start = resolve_symbol_start_for_realtime(
        None,
        end_dt=end_dt,
        lookback_days=2,
        interval="1m",
    )
    assert start == datetime(2026, 3, 4, 0, 0, tzinfo=timezone.utc)
