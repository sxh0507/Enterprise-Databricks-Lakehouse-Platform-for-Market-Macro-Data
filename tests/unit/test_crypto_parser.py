from datetime import timedelta

from lakehouse.crypto_parser import interval_to_timedelta, parse_coinbase_kline


def test_interval_map():
    assert interval_to_timedelta("1m") == timedelta(minutes=1)
    assert interval_to_timedelta("1h") == timedelta(hours=1)
    assert interval_to_timedelta("1d") == timedelta(days=1)


def test_parse_coinbase_kline_mapping():
    # [time, low, high, open, close, volume]
    k = [1704067200, 99.0, 110.0, 100.0, 105.0, 123.45]
    row = parse_coinbase_kline(k, interval="1m")
    assert row["open"] == 100.0
    assert row["high"] == 110.0
    assert row["low"] == 99.0
    assert row["close"] == 105.0
    assert row["volume"] == 123.45
    assert int((row["bar_end_ts"] - row["bar_start_ts"]).total_seconds()) == 60
