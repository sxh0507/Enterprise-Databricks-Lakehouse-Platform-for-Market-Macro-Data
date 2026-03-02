import pytest
from pyspark.sql import Row, SparkSession

from lakehouse.quality_gate import check_duplicate_bars, check_invalid_ohlc, check_macro_null_rates


@pytest.fixture(scope="session")
def spark():
    return SparkSession.builder.appName("test-quality-gates").master("local[1]").getOrCreate()


def test_check_invalid_ohlc(spark):
    data = [
        Row(open=100.0, high=105.0, low=95.0, close=102.0),  # valid
        Row(open=-1.0, high=105.0, low=95.0, close=102.0),  # invalid open
        Row(open=100.0, high=90.0, low=95.0, close=102.0),  # invalid high
    ]
    df = spark.createDataFrame(data)

    assert check_invalid_ohlc(df) == 2


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
