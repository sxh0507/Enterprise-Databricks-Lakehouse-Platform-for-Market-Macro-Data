# KNOWN ISSUES (Day2)

## Fixed in Day2
- Removed hard-coded bronze table path in `20_silver_crypto_ohlc_parse.py.ipynb` (use `BRONZE_TBL`)
- Fixed `T.col` runtime risk in `11_bronze_ingest_ecb_fx.ipynb` (use `F.col` and import `F`)

## Remaining (to handle later)
- `40_observability_metrics.py.ipynb` has repeated `count()` calls; optimize in Day3/Day6
- Add test coverage for parser/quality rules in Day4
