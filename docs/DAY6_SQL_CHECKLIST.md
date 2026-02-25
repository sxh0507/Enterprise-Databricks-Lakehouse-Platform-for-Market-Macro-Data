# Day6 SQL 校验清单 + 回填模板（Direct 1d 口径）

适用前提：
- Direct pipeline 使用 `1d` 粒度。
- 宏观融合目标表使用：`enterprise.gold_ref.market_macro_daily`。
- Observability 表：`enterprise.gold_observability.pipeline_metrics_daily`。

## A. 结构与存在性检查

```sql
WITH expected AS (
  SELECT 'enterprise' AS catalog, 'bronze_market' AS schema, 'crypto_ohlc_raw' AS table_name UNION ALL
  SELECT 'enterprise', 'bronze_ref', 'ecb_fx_raw' UNION ALL
  SELECT 'enterprise', 'bronze_ref', 'fred_series_raw' UNION ALL
  SELECT 'enterprise', 'silver_market', 'crypto_ohlc_1d' UNION ALL
  SELECT 'enterprise', 'silver_ref', 'ecb_fx_daily' UNION ALL
  SELECT 'enterprise', 'silver_ref', 'fred_series_daily' UNION ALL
  SELECT 'enterprise', 'gold_market', 'ohlc_1d' UNION ALL
  SELECT 'enterprise', 'gold_ref', 'market_macro_daily' UNION ALL
  SELECT 'enterprise', 'gold_observability', 'pipeline_metrics_daily'
)
SELECT
  e.catalog,
  e.schema,
  e.table_name,
  CASE WHEN t.table_name IS NULL THEN 'MISSING' ELSE 'OK' END AS status
FROM expected e
LEFT JOIN system.information_schema.tables t
  ON t.table_catalog = e.catalog
 AND t.table_schema = e.schema
 AND t.table_name = e.table_name
ORDER BY e.catalog, e.schema, e.table_name;
```

## B. 行数与新鲜度检查

```sql
-- row count
SELECT 'enterprise.bronze_market.crypto_ohlc_raw' AS table_name, COUNT(*) AS row_cnt FROM enterprise.bronze_market.crypto_ohlc_raw
UNION ALL
SELECT 'enterprise.silver_market.crypto_ohlc_1d', COUNT(*) FROM enterprise.silver_market.crypto_ohlc_1d
UNION ALL
SELECT 'enterprise.silver_ref.ecb_fx_daily', COUNT(*) FROM enterprise.silver_ref.ecb_fx_daily
UNION ALL
SELECT 'enterprise.silver_ref.fred_series_daily', COUNT(*) FROM enterprise.silver_ref.fred_series_daily
UNION ALL
SELECT 'enterprise.gold_market.ohlc_1d', COUNT(*) FROM enterprise.gold_market.ohlc_1d
UNION ALL
SELECT 'enterprise.gold_ref.market_macro_daily', COUNT(*) FROM enterprise.gold_ref.market_macro_daily
UNION ALL
SELECT 'enterprise.gold_observability.pipeline_metrics_daily', COUNT(*) FROM enterprise.gold_observability.pipeline_metrics_daily;
```

```sql
-- freshness (minutes)
SELECT 'bronze_crypto' AS table_name, MAX(ingestion_ts) AS max_ts, TIMESTAMPDIFF(MINUTE, MAX(ingestion_ts), CURRENT_TIMESTAMP()) AS freshness_min
FROM enterprise.bronze_market.crypto_ohlc_raw
UNION ALL
SELECT 'silver_crypto_1d', MAX(bar_end_ts), TIMESTAMPDIFF(MINUTE, MAX(bar_end_ts), CURRENT_TIMESTAMP())
FROM enterprise.silver_market.crypto_ohlc_1d
UNION ALL
SELECT 'silver_ecb_daily', CAST(MAX(rate_date) AS TIMESTAMP), TIMESTAMPDIFF(MINUTE, CAST(MAX(rate_date) AS TIMESTAMP), CURRENT_TIMESTAMP())
FROM enterprise.silver_ref.ecb_fx_daily
UNION ALL
SELECT 'silver_fred_daily', CAST(MAX(obs_date) AS TIMESTAMP), TIMESTAMPDIFF(MINUTE, CAST(MAX(obs_date) AS TIMESTAMP), CURRENT_TIMESTAMP())
FROM enterprise.silver_ref.fred_series_daily
UNION ALL
SELECT 'gold_ref_market_macro_daily', MAX(mart_ts), TIMESTAMPDIFF(MINUTE, MAX(mart_ts), CURRENT_TIMESTAMP())
FROM enterprise.gold_ref.market_macro_daily
UNION ALL
SELECT 'obs_pipeline_metrics_daily', MAX(computed_ts), TIMESTAMPDIFF(MINUTE, MAX(computed_ts), CURRENT_TIMESTAMP())
FROM enterprise.gold_observability.pipeline_metrics_daily;
```

## C. 质量与完整性检查（含 macro 缺失）

```sql
-- C1: silver crypto 主键重复检查
SELECT source, symbol, bar_start_ts, COUNT(*) AS dup_cnt
FROM enterprise.silver_market.crypto_ohlc_1d
GROUP BY source, symbol, bar_start_ts
HAVING COUNT(*) > 1
ORDER BY dup_cnt DESC
LIMIT 50;
```

```sql
-- C2: silver crypto OHLC 合法性检查
SELECT COUNT(*) AS bad_ohlc_rows
FROM enterprise.silver_market.crypto_ohlc_1d
WHERE open <= 0
   OR high <= 0
   OR low <= 0
   OR close <= 0
   OR high < GREATEST(open, close)
   OR low > LEAST(open, close);
```

```sql
-- C3: macro 核心字段缺失率（你提出的重点）
SELECT
  COUNT(*) AS total_rows,
  SUM(CASE WHEN eurusd_rate IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS null_rate_eurusd_rate,
  SUM(CASE WHEN fedfunds  IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS null_rate_fedfunds,
  SUM(CASE WHEN close_px  IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS null_rate_close_px
FROM enterprise.gold_ref.market_macro_daily;
```

```sql
-- C4: 宏观数据覆盖天数（是否存在“市场有数据但宏观缺失”的日期）
WITH m AS (
  SELECT DISTINCT trade_date
  FROM enterprise.gold_ref.market_macro_daily
),
missing AS (
  SELECT trade_date
  FROM enterprise.gold_ref.market_macro_daily
  WHERE eurusd_rate IS NULL OR fedfunds IS NULL
)
SELECT
  (SELECT COUNT(*) FROM m) AS total_trade_days,
  (SELECT COUNT(*) FROM missing) AS days_with_macro_missing;
```

## D. Observability 结果核对

```sql
WITH d AS (
  SELECT MAX(metric_date) AS latest_metric_date
  FROM enterprise.gold_observability.pipeline_metrics_daily
)
SELECT
  metric_date,
  pipeline,
  table_name,
  row_count,
  freshness_minutes,
  null_rate,
  duplicate_rate,
  status
FROM enterprise.gold_observability.pipeline_metrics_daily
WHERE metric_date = (SELECT latest_metric_date FROM d)
ORDER BY status DESC, table_name;
```

## E. 文档回填模板（复制到 `docs/WEEK1_REGRESSION_EVIDENCE.md`）

```md
### Day6 回归补录（YYYY-MM-DD）

#### 1) Run 信息
- Run URL:
- Job Key: `direct_market_macro_pipeline`
- Trigger Time:
- End Time:
- Final Status: SUCCESS / FAILED

#### 2) Task 级结果
| task_key | status | duration | retry | note |
|---|---|---|---|---|
| platform_setup_catalog_schema |  |  |  |  |
| direct_bronze_market_crypto_ingest |  |  |  |  |
| direct_bronze_ref_ecb_fx_ingest |  |  |  |  |
| direct_bronze_ref_fred_ingest |  |  |  |  |
| direct_silver_market_crypto_ohlc_transform |  |  |  |  |
| direct_silver_ref_macro_transform |  |  |  |  |
| direct_gold_market_ohlc_features_build |  |  |  |  |
| direct_gold_market_macro_daily_build |  |  |  |  |
| platform_observability_metrics_build |  |  |  |  |

#### 3) SQL 校验结果
| check | table | metric | result | pass/fail |
|---|---|---|---|---|
| row_count | enterprise.bronze_market.crypto_ohlc_raw | count(*) |  |  |
| row_count | enterprise.silver_market.crypto_ohlc_1d | count(*) |  |  |
| row_count | enterprise.gold_ref.market_macro_daily | count(*) |  |  |
| freshness | enterprise.gold_observability.pipeline_metrics_daily | freshness_min |  |  |
| duplicate | enterprise.silver_market.crypto_ohlc_1d | dup_rows |  |  |
| ohlc_validity | enterprise.silver_market.crypto_ohlc_1d | bad_ohlc_rows |  |  |
| macro_null_rate | enterprise.gold_ref.market_macro_daily | null_rate_eurusd_rate / null_rate_fedfunds |  |  |

#### 4) 结论
- Day6 Regression Gate: PASS / FAIL
- 是否进入 Day7: YES / NO
```

