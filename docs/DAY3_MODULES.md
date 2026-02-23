# Day3 Modules (Direct Job)

## New reusable modules
- src/lakehouse/crypto_parser.py
- src/lakehouse/quality_rules.py
- src/lakehouse/observability_rules.py

## Unit tests
- tests/unit/test_crypto_parser.py
- tests/unit/test_quality_rules.py
- tests/unit/test_observability_rules.py

## Next integration step (Notebook)
Use these imports in Direct notebooks:
- from lakehouse.crypto_parser import parse_coinbase_kline, parse_coinbase_payload
- from lakehouse.quality_rules import is_valid_ohlc, dedupe_latest
- from lakehouse.observability_rules import freshness_minutes, status_from_freshness
