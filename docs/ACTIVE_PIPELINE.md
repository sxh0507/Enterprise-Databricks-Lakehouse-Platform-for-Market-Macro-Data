# ACTIVE PIPELINE (Week 1)

## Active files (main pipeline)
- 00_platform_setup_catalog_schema.ipynb
- 10_direct_bronze_market_crypto_ingest.ipynb
- 11_direct_bronze_ref_ecb_fx_ingest.ipynb
- 12_direct_bronze_ref_fred_ingest.ipynb
- 20_direct_silver_market_crypto_ohlc_transform.ipynb
- 22_direct_silver_ref_macro_transform.ipynb
- 30_direct_gold_market_ohlc_features_build.ipynb
- 32_direct_gold_market_macro_daily_build.ipynb
- 70_platform_observability_metrics_build.ipynb

## Landing pipeline files
- 40_landing_producer_market_crypto_to_s3_1m.ipynb
- 41_landing_bronze_market_crypto_load_from_s3.ipynb
- 43_landing_gold_market_crypto_features_build.dbquery.ipynb
- 50_landing_producer_ref_ecb_to_s3.ipynb
- 51_landing_bronze_ref_ecb_load_from_s3.ipynb
- 53_landing_producer_ref_fred_to_s3.ipynb
- 54_landing_bronze_ref_fred_load_from_s3.ipynb
- 56_landing_gold_market_macro_daily_build.dbquery.ipynb

## Archived in Week 1 (not deleted)
- _archive/week1/3_gold_ohlc_features.sql
- _archive/week1/33_direct_gold_market_macro_daily_build.sql
- _archive/week1/42_landing_silver_market_crypto_clean_transform.ipynb
- _archive/week1/55_landing_silver_ref_macro_transform.ipynb
