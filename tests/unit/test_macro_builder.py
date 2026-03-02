from datetime import datetime, timedelta

import pytest
from pyspark.sql import Row

from lakehouse.transforms.macro_builder import build_gold_market_macro_daily

# All tests in this file require a live SparkSession.
# CI skips them via `pytest -m "not spark"`.
# Run locally with: pip install -e ".[spark]" && pytest -m spark
pytestmark = pytest.mark.spark


def test_macro_builder_forward_fill_ttl(spark):
    """
    Test that forward-fill correctly propagates within TTL bounds
    and correctly reverts to NULL when TTL is exceeded.
    """
    # Create dates spanning 7 days
    base = datetime(2025, 1, 1)
    dates = [base + timedelta(days=i) for i in range(7)]

    # 1. Market data exists every day
    mkt_data = [
        Row(source="test", symbol="BTC", bar_start_ts=d, bar_end_ts=d, close=100.0 + i, volume=10.0)
        for i, d in enumerate(dates)
    ]

    # 2. FX and FED data stop after day 0
    fx_data = [Row(rate_date=dates[0], base_ccy="EUR", quote_ccy="USD", fx_rate=1.10)]
    fed_data = [Row(obs_date=dates[0], series_id="DFF", value=5.25)]

    mkt_df = spark.createDataFrame(mkt_data)
    fx_df = spark.createDataFrame(fx_data)
    fed_df = spark.createDataFrame(fed_data)

    # Run the builder with a TTL of 3 days
    # So day 0, 1, 2, 3 should have macro values, but day 4, 5, 6 should be NULL
    res_df = build_gold_market_macro_daily(mkt_df, fx_df, fed_df, max_fill_days=3)

    # Extract results and sort by trade_date
    results = sorted([row.asDict() for row in res_df.collect()], key=lambda r: r["trade_date"])

    # Day 0: Direct Match -> Not Null
    assert results[0]["eurusd_rate"] == 1.10

    # Day 1-3: Forward Filled within TTL -> Not Null
    assert results[1]["eurusd_rate"] == 1.10
    assert results[2]["eurusd_rate"] == 1.10
    assert results[3]["eurusd_rate"] == 1.10

    # Day 4-6: Exceeds TTL gap (4 days from day 0) -> Should be NULL
    assert results[4]["eurusd_rate"] is None
    assert results[5]["fedfunds"] is None
    assert results[6]["eurusd_rate"] is None
