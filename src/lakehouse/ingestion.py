from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, List


def day_floor_utc(ts: datetime) -> datetime:
    """Normalize a datetime to 00:00:00 UTC."""
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return ts.astimezone(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)


def resolve_realtime_end_dt(now_utc: datetime, safety_lag_minutes: int) -> datetime:
    """
    Resolve realtime extraction end date as a UTC day anchor.

    A safety lag prevents selecting an in-flight day near UTC midnight.
    """
    if safety_lag_minutes < 0:
        raise ValueError("safety_lag_minutes must be >= 0")
    return day_floor_utc(now_utc - timedelta(minutes=safety_lag_minutes))


def resolve_symbol_start_for_realtime(
    watermark: datetime | None,
    *,
    end_dt: datetime,
    lookback_days: int,
    interval: str,
) -> datetime:
    """
    Resolve per-symbol realtime start date (UTC day anchor).

    For intraday intervals, replay watermark day to backfill late/partial bars.
    For daily interval, continue from next day to avoid unnecessary replay.
    """
    if lookback_days < 1:
        raise ValueError("lookback_days must be >= 1")

    if watermark is None:
        return day_floor_utc(end_dt - timedelta(days=lookback_days))

    wm_day = day_floor_utc(watermark)
    if interval in {"1m", "1h"}:
        return wm_day
    if interval == "1d":
        return wm_day + timedelta(days=1)
    raise ValueError(f"Unsupported interval: {interval}")


def fetch_pages_concurrently(
    symbols: List[str],
    days: List[datetime],
    interval: str,
    fetch_func: Callable[[str, str, datetime], List[Dict[str, Any]]],
    max_workers: int = 4,
) -> tuple[List[Any], List[Dict[str, Any]]]:
    """
    Fetch data pages concurrently for multiple symbols and days.

    Args:
        symbols: List of symbols (e.g., ['BTCUSDT', 'ETHUSDT'])
        days: List of day start datetimes to fetch
        interval: Interval string (e.g., '1d', '1m')
        fetch_func: Function that takes (symbol, interval, day_start) and returns a list of pages
        max_workers: Maximum number of concurrent threads

    Returns:
        tuple containing (list of accumulated page results, list of error dictionaries)
    """
    all_pages = []
    errors = []

    tasks = []
    # Create tasks for each symbol-day combination
    for symbol in symbols:
        for day_start in days:
            tasks.append((symbol, day_start))

    print(f"[INFO] Submitting {len(tasks)} tasks to ThreadPool with {max_workers} workers...")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_task = {
            executor.submit(fetch_func, sym, interval, day): (sym, day) for sym, day in tasks
        }

        # Process as they complete
        for future in as_completed(future_to_task):
            sym, day = future_to_task[future]
            try:
                pages = future.result()
                all_pages.extend([(sym, day, p) for p in pages])
                print(f"[OK] {sym} {day.date()} fetched {len(pages)} pages")
            except Exception as e:
                err_msg = str(e)
                errors.append(
                    {
                        "symbol": sym,
                        "day": str(day.date()),
                        "interval": interval,
                        "error": err_msg[:500],
                    }
                )
                print(f"[ERROR] {sym} {day.date()} failed: {err_msg[:200]}")

    return all_pages, errors
