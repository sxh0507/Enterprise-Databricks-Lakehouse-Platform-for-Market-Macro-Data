from __future__ import annotations

from typing import Any, Dict


def is_valid_ecb_fx_record(row: Dict[str, Any]) -> bool:
    rate_date = row.get("rate_date")
    base_ccy = row.get("base_ccy")
    quote_ccy = row.get("quote_ccy")
    fx_rate = row.get("fx_rate")

    if not rate_date or not base_ccy or not quote_ccy:
        return False
    if len(str(base_ccy)) != 3 or len(str(quote_ccy)) != 3:
        return False
    try:
        fx = float(fx_rate)
    except Exception:
        return False
    return fx > 0


def is_valid_fred_record(row: Dict[str, Any]) -> bool:
    obs_date = row.get("obs_date")
    value = row.get("value")
    if not obs_date:
        return False
    try:
        float(value)
    except Exception:
        return False
    return True
