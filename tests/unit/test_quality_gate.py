import pytest
from pyspark.sql import Row

from lakehouse.quality_gate import check_duplicate_bars, check_invalid_ohlc, check_macro_null_rates

# All tests in this file require a live SparkSession.
# CI skips them via `pytest -m "not spark"`.
# Run locally with: pip install -e ".[spark]" && pytest -m spark
pytestmark = pytest.mark.spark


def test_check_invalid_ohlc(spark):
    data = [
        Row(open=100.0, high=105.0, low=95.0, close=102.0, volume=1.0),  # valid
        Row(open=-1.0, high=105.0, low=95.0, close=102.0, volume=1.0),  # invalid open
        Row(open=100.0, high=90.0, low=95.0, close=102.0, volume=1.0),  # invalid high
        Row(open=100.0, high=105.0, low=95.0, close=102.0, volume=-5.0),  # invalid volume
    ]
    df = spark.createDataFrame(data)

    assert check_invalid_ohlc(df) == 3  # 3 rows are invalid


def test_check_duplicate_bars(spark):
    data = [
        Row(source="coinbase", symbol="BTC", bar_start_ts="2023-01-01T00:00:00"),
        Row(source="coinbase", symbol="BTC", bar_start_ts="2023-01-01T00:00:00"),  # duplicate
        Row(source="coinbase", symbol="ETH", bar_start_ts="2023-01-01T00:00:00"),
    ]
    df = spark.createDataFrame(data)

    # Expect 1 duplicate group
    assert check_duplicate_bars(df) == 1


def test_check_macro_null_rates(spark):
    data = [
        Row(eurusd_rate=1.1, fedfunds=5.25),
        Row(eurusd_rate=None, fedfunds=5.25),
        Row(eurusd_rate=1.1, fedfunds=None),
        Row(eurusd_rate=None, fedfunds=None),
    ]
    df = spark.createDataFrame(data)

    res = check_macro_null_rates(df)

    assert res["total"] == 4
    assert res["eurusd_null_rate"] == 0.5
    assert res["fedfunds_null_rate"] == 0.5
