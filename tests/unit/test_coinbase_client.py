from datetime import datetime, timezone

import pytest
import responses

from lakehouse.clients.coinbase import CoinbaseClient


@pytest.fixture
def client():
    # Use small or zero sleep times to speed up tests
    return CoinbaseClient(max_retries=3, base_sleep=0.01, sleep_ms=0)


@responses.activate
def test_fetch_klines_success(client):
    start_dt = datetime(2026, 3, 1, tzinfo=timezone.utc)
    end_dt = datetime(2026, 3, 2, tzinfo=timezone.utc)

    responses.add(
        responses.GET,
        "https://api.exchange.coinbase.com/products/BTC-USD/candles",
        json=[[1646092800, 43000, 44000, 42000, 43500, 100]],  # Mocked K-line data
        status=200,
    )

    result = client.fetch_klines("BTCUSDT", "1d", start_dt, end_dt)

    assert result["symbol"] == "BTCUSDT"
    assert result["interval"] == "1d"
    assert result["kline_count"] == 1
    assert len(result["klines"]) == 1


@responses.activate
def test_fetch_klines_retry_on_429(client):
    start_dt = datetime(2026, 3, 1, tzinfo=timezone.utc)
    end_dt = datetime(2026, 3, 2, tzinfo=timezone.utc)

    # First two requests fail with 429
    responses.add(
        responses.GET,
        "https://api.exchange.coinbase.com/products/BTC-USD/candles",
        status=429,
        body="Rate limit exceeded",
    )
    responses.add(
        responses.GET,
        "https://api.exchange.coinbase.com/products/BTC-USD/candles",
        status=429,
        body="Rate limit exceeded",
    )
    # Third request succeeds
    responses.add(
        responses.GET,
        "https://api.exchange.coinbase.com/products/BTC-USD/candles",
        json=[[1646092800, 43000, 44000, 42000, 43500, 100]],
        status=200,
    )

    result = client.fetch_klines("BTCUSDT", "1d", start_dt, end_dt)

    # Needs to have succeeded eventually
    assert result["kline_count"] == 1
    # Verify that it retried exactly 3 times
    assert len(responses.calls) == 3


@responses.activate
def test_fetch_klines_fails_on_400(client):
    start_dt = datetime(2026, 3, 1, tzinfo=timezone.utc)
    end_dt = datetime(2026, 3, 2, tzinfo=timezone.utc)

    # 400 errors should NOT be retried, they should fail immediately
    responses.add(
        responses.GET,
        "https://api.exchange.coinbase.com/products/BTC-USD/candles",
        status=400,
        body="Invalid granularity",
    )

    with pytest.raises(RuntimeError) as exc_info:
        client.fetch_klines("BTCUSDT", "1d", start_dt, end_dt)

    assert "Coinbase API Error 400" in str(exc_info.value)
    # Verify it only tried once and gave up
    assert len(responses.calls) == 1


def test_backfill_klines_one_day_pagination_1m(monkeypatch, client):
    # Mock fetch_klines to return a dummy page
    def dict_return(*args, **kwargs):
        return {"kline_count": 300, "klines": []}

    monkeypatch.setattr(client, "fetch_klines", dict_return)

    day_start = datetime(2026, 3, 1, tzinfo=timezone.utc)

    # For 1m interval, 1 day = 1440 minutes.
    # Step size is 300 minutes.
    # Expected pages: 1440 / 300 = 4.8 -> 5 pages.
    pages = client.backfill_klines_one_day("BTCUSDT", "1m", day_start)

    assert len(pages) == 5
