-- 30_gold_ohlc_features.sql
-- Build Gold mart: OHLC 1m + basic features from Silver
-- Source: enterprise.silver_market.crypto_ohlc_1m
-- Target: enterprise.gold_market.ohlc_1m

CREATE OR REPLACE TABLE enterprise.gold_market.ohlc_1m
USING DELTA
PARTITIONED BY (p_date)
AS
WITH base AS (
  SELECT
    source,
    symbol,
    bar_start_ts,
    bar_end_ts,
    open,
    high,
    low,
    close,
    volume,
    p_date,
    ingestion_ts
  FROM enterprise.silver_market.crypto_ohlc_1m
),
feat AS (
  SELECT
    *,
    -- previous close within (source, symbol)
    LAG(close) OVER (PARTITION BY source, symbol ORDER BY bar_start_ts) AS prev_close,

    -- price change features
    (close - open) AS candle_body,
    (high - low)   AS candle_range,

    -- simple returns
    CASE
      WHEN LAG(close) OVER (PARTITION BY source, symbol ORDER BY bar_start_ts) IS NULL THEN NULL
      WHEN LAG(close) OVER (PARTITION BY source, symbol ORDER BY bar_start_ts) = 0 THEN NULL
      ELSE (close / LAG(close) OVER (PARTITION BY source, symbol ORDER BY bar_start_ts) - 1)
    END AS ret_1m,

    -- log return
    CASE
      WHEN LAG(close) OVER (PARTITION BY source, symbol ORDER BY bar_start_ts) IS NULL THEN NULL
      WHEN LAG(close) OVER (PARTITION BY source, symbol ORDER BY bar_start_ts) <= 0 THEN NULL
      ELSE LN(close / LAG(close) OVER (PARTITION BY source, symbol ORDER BY bar_start_ts))
    END AS log_ret_1m

  FROM base
),
rolling AS (
  SELECT
    *,
    -- rolling windows: 15m, 60m (within symbol)
    AVG(close) OVER (
      PARTITION BY source, symbol
      ORDER BY bar_start_ts
      ROWS BETWEEN 14 PRECEDING AND CURRENT ROW
    ) AS ma_close_15m,

    AVG(close) OVER (
      PARTITION BY source, symbol
      ORDER BY bar_start_ts
      ROWS BETWEEN 59 PRECEDING AND CURRENT ROW
    ) AS ma_close_60m,

    -- rolling volatility (stddev of log returns)
    STDDEV_POP(log_ret_1m) OVER (
      PARTITION BY source, symbol
      ORDER BY bar_start_ts
      ROWS BETWEEN 59 PRECEDING AND CURRENT ROW
    ) AS vol_logret_60m
  FROM feat
)
SELECT
  source,
  symbol,
  bar_start_ts,
  bar_end_ts,
  open,
  high,
  low,
  close,
  volume,

  -- features
  prev_close,
  candle_body,
  candle_range,
  ret_1m,
  log_ret_1m,
  ma_close_15m,
  ma_close_60m,
  vol_logret_60m,

  -- lineage / audit
  ingestion_ts,
  p_date,
  current_timestamp() AS mart_ts
FROM rolling;
