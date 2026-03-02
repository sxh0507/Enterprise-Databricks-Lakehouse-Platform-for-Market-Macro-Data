import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import List, Dict, Any, Callable

def fetch_pages_concurrently(
    symbols: List[str],
    days: List[datetime],
    interval: str,
    fetch_func: Callable[[str, str, datetime], List[Dict[str, Any]]],
    max_workers: int = 4
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
            executor.submit(fetch_func, sym, interval, day): (sym, day) 
            for sym, day in tasks
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
                errors.append({
                    "symbol": sym,
                    "day": str(day.date()),
                    "interval": interval,
                    "error": err_msg[:500]
                })
                print(f"[ERROR] {sym} {day.date()} failed: {err_msg[:200]}")
                
    return all_pages, errors
