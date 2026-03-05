import pytest
from datetime import datetime, timezone
from lakehouse.pipelines.crypto_bronze_ingestor import CryptoBronzeIngestor

def test_resolve_days_to_fetch_backfill():
    ingestor = CryptoBronzeIngestor(spark=None, catalog="cat", schema="sch", table_name="tbl", api_client=None)
    
    start_dt = datetime(2026, 3, 1, tzinfo=timezone.utc)
    end_dt = datetime(2026, 3, 3, tzinfo=timezone.utc)
    
    # 3 days total
    days = ingestor._resolve_days_to_fetch(
        mode="backfill",
        symbols=["BTCUSDT", "ETHUSDT"],
        interval="1d",
        start_date=start_dt,
        end_date=end_dt,
        max_days=5,
        default_lookback_days=1
    )
    
    assert len(days["BTCUSDT"]) == 3
    assert len(days["ETHUSDT"]) == 3
    assert days["BTCUSDT"][0] == start_dt
    assert days["BTCUSDT"][-1] == end_dt

def test_resolve_days_to_fetch_realtime_symbol_casing(monkeypatch):
    # Mock _get_watermarks to return uppercase keys exactly as Spark's DataFrame row projection would
    monkeypatch.setattr(CryptoBronzeIngestor, "_get_watermarks", lambda self, symbols, interval: {"BTCUSDT": datetime(2026, 3, 2, 0, 0, tzinfo=timezone.utc)})
    
    ingestor = CryptoBronzeIngestor(spark=None, catalog="cat", schema="sch", table_name="tbl", api_client=None)
    
    end_dt = datetime(2026, 3, 3, tzinfo=timezone.utc)
    
    # Passing lower case symbol
    days = ingestor._resolve_days_to_fetch(
        mode="realtime",
        symbols=["btcusdt"],
        interval="1d",
        start_date=None,
        end_date=end_dt,
        max_days=5,
        default_lookback_days=5
    )
    
    # It should have found the watermark (using upper) which means starting at 3/2 + 1d = 3/3
    assert len(days["btcusdt"]) == 1
    assert days["btcusdt"][0] == end_dt
