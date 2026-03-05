import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

import requests


class CoinbaseClient:
    """Client for interacting with the Coinbase Exchange API."""
    
    BASE_URL = "https://api.exchange.coinbase.com"

    def __init__(self, max_retries: int = 6, base_sleep: float = 1.0, sleep_ms: int = 250):
        self.max_retries = max_retries
        self.base_sleep = base_sleep
        self.sleep_ms = sleep_ms

    def _iso_utc_z(self, dt: datetime) -> str:
        """Coinbase requires RFC3339/Z format."""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    def fetch_klines(self, symbol: str, interval: str, start_dt: datetime, end_dt: datetime) -> Dict[str, Any]:
        """Fetch a single page of klines from Coinbase for a given time window."""
        product_id = symbol.replace("USDT", "-USD")
        
        if interval == "1d":
            granularity = 86400
        elif interval == "1h":
            granularity = 3600
        elif interval == "1m":
            granularity = 60
        else:
            raise ValueError("Coinbase: only 1m / 1h / 1d supported")

        url = f"{self.BASE_URL}/products/{product_id}/candles"
        params = {
            "start": self._iso_utc_z(start_dt),
            "end": self._iso_utc_z(end_dt),
            "granularity": granularity
        }
        headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}

        last_err = None

        for attempt in range(1, self.max_retries + 1):
            try:
                r = requests.get(url, params=params, headers=headers, timeout=30)

                if r.status_code == 200:
                    kl = r.json()
                    return {
                        "symbol": symbol,
                        "interval": interval,
                        "start_utc": params["start"],
                        "end_utc": params["end"],
                        "kline_count": len(kl),
                        "klines": kl
                    }

                # Retry on 429 or 5xx Server Errors
                if r.status_code == 429 or (500 <= r.status_code < 600):
                    last_err = f"{r.status_code}: {r.text[:200]}"
                else:
                    # Do not retry on 400/401/403/404 etc
                    raise RuntimeError(f"Coinbase API Error {r.status_code}: {r.text[:200]}")

            except requests.RequestException as e:
                last_err = str(e)

            if attempt < self.max_retries:
                # Exponential backoff with jitter
                sleep_s = self.base_sleep * (2 ** (attempt - 1)) + (0.1 * attempt)
                print(f"[WARN] Coinbase retry {attempt}/{self.max_retries} after {sleep_s:.1f}s, last_err={last_err}")
                time.sleep(sleep_s)
            else:
                break

        raise RuntimeError(f"Coinbase API failed after retries. symbol={symbol}, start={params['start']}, end={params['end']}, last_err={last_err}")

    def backfill_klines_one_day(self, symbol: str, interval: str, day_start: datetime) -> List[Dict[str, Any]]:
        """
        Fetch all pages of klines for a single day based on API limits.
        - 1m: 300 minutes per chunk (<=300 candles)
        - 1h: 1 day per chunk (24 candles)
        - 1d: 1 day per chunk (1 candle)
        """
        if day_start.tzinfo is None:
            day_start = day_start.replace(tzinfo=timezone.utc)

        day_end = day_start + timedelta(days=1)

        if interval == "1m":
            step = timedelta(minutes=300)
        elif interval == "1h":
            step = timedelta(hours=24)
        elif interval == "1d":
            step = timedelta(days=1)
        else:
            raise ValueError("Coinbase backfill: only 1m / 1h / 1d supported")

        pages: List[Dict[str, Any]] = []
        cur = day_start
        while cur < day_end:
            nxt = min(cur + step, day_end)
            page = self.fetch_klines(symbol, interval, cur, nxt)
            pages.append(page)
            cur = nxt

            # Rate limit backoff between pages
            if self.sleep_ms > 0:
                time.sleep(self.sleep_ms / 1000.0)

        return pages
