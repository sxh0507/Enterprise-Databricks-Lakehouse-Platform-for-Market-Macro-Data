from __future__ import annotations

import json
import re
from typing import Any, Dict, List

_ECB_TIME_BLOCK_RE = re.compile(r'time="(\d{4}-\d{2}-\d{2})"(.*?)(?=time="|$)', re.DOTALL)
_ECB_PAIR_RE = re.compile(r'currency="([A-Z]{3})"\s+rate="([0-9.]+)"')
_FRED_MISSING_VALUES = {".", "nan", "NaN", "", None}


def parse_ecb_fx_xml(raw_xml: str | None, base_ccy: str = "EUR") -> List[Dict[str, Any]]:
    """
    Parse ECB FX XML payload into normalized records.
    Returns items with keys: rate_date, base_ccy, quote_ccy, fx_rate.
    """
    if not raw_xml:
        return []

    xml = raw_xml.replace("'", '"')
    out: List[Dict[str, Any]] = []
    base = (base_ccy or "EUR").upper()

    for m in _ECB_TIME_BLOCK_RE.finditer(xml):
        rate_date = m.group(1)
        body = m.group(2)
        for ccy, rate_str in _ECB_PAIR_RE.findall(body):
            try:
                fx = float(rate_str)
            except Exception:
                continue
            out.append(
                {
                    "rate_date": rate_date,
                    "base_ccy": base,
                    "quote_ccy": ccy,
                    "fx_rate": fx,
                }
            )
    return out


def parse_fred_observations(raw_json: str | None) -> List[Dict[str, Any]]:
    """
    Parse FRED observations payload into normalized records.
    Returns items with keys: obs_date, value.
    """
    if not raw_json:
        return []

    try:
        payload = json.loads(raw_json)
    except Exception:
        return []

    obs = payload.get("observations") or []
    out: List[Dict[str, Any]] = []
    for item in obs:
        obs_date = item.get("date")
        value_raw = item.get("value")
        if not obs_date or value_raw in _FRED_MISSING_VALUES:
            continue
        try:
            val = float(value_raw)
        except Exception:
            continue
        out.append({"obs_date": obs_date, "value": val})
    return out
