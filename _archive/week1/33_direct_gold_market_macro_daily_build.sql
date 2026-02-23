-- =========================================================
-- 33_gold_market_macro_daily.sql
-- Version: Updated for DFF (Daily) + Forward Fill
-- =========================================================

CREATE OR REPLACE TABLE enterprise.gold_market.market_macro_daily
USING DELTA
PARTITIONED BY (trade_date)
AS
WITH mkt AS (
  -- 1. 市场数据 (7x24小时)
  SELECT
    source,
    symbol,
    date(bar_start_ts) AS trade_date,
    max_by(close, bar_end_ts) AS close_px,
    sum(volume) AS daily_volume
  FROM enterprise.silver_market.crypto_ohlc_1m
  GROUP BY source, symbol, date(bar_start_ts)
),
fx AS (
  -- 2. 外汇数据 (仅工作日有数据)
  SELECT
    rate_date,
    fx_rate AS eurusd_rate
  FROM enterprise.silver_ref.ecb_fx_daily
  WHERE base_ccy = 'EUR' AND quote_ccy = 'USD'
),
fed AS (
  -- 3. 美联储利率 (改为使用 DFF 日度数据)
  SELECT
    obs_date,
    value AS fedfunds
  FROM enterprise.silver_ref.fred_series_daily
  WHERE series_id = 'DFF'  -- <--- 【关键修改】改为 DFF
),
joined_raw AS (
  -- 4. 原始关联 (此时周末的 FX 仍为 NULL)
  SELECT
    mkt.source,
    mkt.symbol,
    mkt.trade_date,
    mkt.close_px,
    mkt.daily_volume,
    fx.eurusd_rate as raw_fx,
    fed.fedfunds as raw_fed
  FROM mkt
  LEFT JOIN fx  ON fx.rate_date = mkt.trade_date
  LEFT JOIN fed ON fed.obs_date = mkt.trade_date
)
-- 5. 最终层：使用“向前填充”填补周末/假期的空白
SELECT
  source,
  symbol,
  trade_date,
  close_px,
  daily_volume,
  -- 汇率：周末没有数据，沿用周五的
  LAST_VALUE(raw_fx, TRUE) OVER (
    PARTITION BY source, symbol 
    ORDER BY trade_date 
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ) AS eurusd_rate,
  
  -- 利率：DFF 虽然有周末数据，但加个填充逻辑作为双重保险 (Safety Net)
  LAST_VALUE(raw_fed, TRUE) OVER (
    PARTITION BY source, symbol 
    ORDER BY trade_date 
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ) AS fedfunds,
  
  current_timestamp() AS mart_ts
FROM joined_raw;