# KNOWN ISSUES (Day2)

## Fixed in Day2
- Removed hard-coded bronze table path in `20_direct_silver_market_crypto_ohlc_transform.ipynb` (use `BRONZE_TBL`)
- Fixed `T.col` runtime risk in `11_direct_bronze_ref_ecb_fx_ingest.ipynb` (use `F.col` and import `F`)

## Remaining (to handle later)
- `70_platform_observability_metrics_build.ipynb` has repeated `count()` calls; optimize in Day3/Day6
- Add test coverage for parser/quality rules in Day4
