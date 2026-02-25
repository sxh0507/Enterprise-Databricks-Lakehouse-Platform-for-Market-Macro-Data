# Week1 回归证据（2026-02-25 实测版）

## A. 执行信息
- 日期：2026-02-25
- 执行人：`xh.shi0507@gmail.com`
- 分支：`main`
- Databricks Workspace：`https://dbc-ccc612b1-3dfb.cloud.databricks.com`
- Job Key：`direct_market_macro_pipeline`
- 校验 Notebook：`96_validation_day6_regression_checks.ipynb`

## B. Day6 SQL 验收结果（真实输出）

### B1. 表存在性
| catalog | schema | table_name | status |
|---|---|---|---|
| enterprise | bronze_market | crypto_ohlc_raw | OK |
| enterprise | bronze_ref | ecb_fx_raw | OK |
| enterprise | bronze_ref | fred_series_raw | OK |
| enterprise | silver_market | crypto_ohlc_1d | OK |
| enterprise | silver_ref | ecb_fx_daily | OK |
| enterprise | silver_ref | fred_series_daily | OK |
| enterprise | gold_market | ohlc_1d | OK |
| enterprise | gold_observability | pipeline_metrics_daily | OK |
| enterprise | gold_ref | market_macro_daily | OK |

### B2. 行数检查（target + legacy 对照）
| table_name | row_cnt |
|---|---:|
| enterprise.bronze_market.crypto_ohlc_raw | 8166 |
| enterprise.silver_market.crypto_ohlc_1d | 7441 |
| enterprise.silver_ref.ecb_fx_daily | 231 |
| enterprise.silver_ref.fred_series_daily | 26167 |
| enterprise.gold_market.ohlc_1d | 7441 |
| enterprise.gold_ref.market_macro_daily | 212 |
| enterprise.gold_observability.pipeline_metrics_daily | 78 |
| enterprise.gold_market.market_macro_daily (legacy) | 7439 |

### B3. Freshness 检查（分钟）
| table_name | max_ts | freshness_min |
|---|---|---:|
| bronze_crypto | 2026-02-25T21:47:14.737+00:00 | 47 |
| silver_crypto_1d | 2026-02-26T00:00:00.000+00:00 | -85 |
| gold_ref_market_macro_daily | 2026-02-25T22:01:51.504+00:00 | 32 |
| obs_pipeline_metrics_daily | 2026-02-25T22:02:27.492+00:00 | 32 |
| silver_ecb_daily | 2026-02-25T00:00:00.000+00:00 | 1354 |
| silver_fred_daily | 2026-02-19T00:00:00.000+00:00 | 9994 |

### B4. 质量检查
| check | result | status |
|---|---:|---|
| `bad_ohlc_rows` on `enterprise.silver_market.crypto_ohlc_1d` | 0 | PASS |
| `dup_group_cnt` on `enterprise.silver_market.crypto_ohlc_1d` | 0 | PASS |
| `null_rate_eurusd_rate` on `enterprise.gold_ref.market_macro_daily` | 0 | PASS |
| `null_rate_fedfunds` on `enterprise.gold_ref.market_macro_daily` | 0 | PASS |
| `null_rate_close_px` on `enterprise.gold_ref.market_macro_daily` | 0 | PASS |
| `missing_day_ratio` on `enterprise.gold_ref.market_macro_daily` | 0（0/106） | PASS |
| `null_rate_eurusd_rate` on `enterprise.gold_market.market_macro_daily` (legacy) | 0.9704261325 | FAIL（历史旧链路） |
| `missing_day_ratio` on `enterprise.gold_market.market_macro_daily` (legacy) | 0.9715909091（3762/3872） | FAIL（历史旧链路） |

### B5. Observability 最新分区摘要
| status | cnt |
|---|---:|
| FAIL | 2 |
| OK | 4 |

## C. 结果解读（当前版本）
- 主链路数据质量已达标：`gold_ref.market_macro_daily` 已可用，目标表空值与缺失交易日均为 0。
- legacy 表仍高缺失（约 97%）是预期现象，不作为主链路失败依据。
- 当前剩余问题只在 observability freshness 判定口径：
  - `enterprise.bronze_market.crypto_ohlc_raw` 应使用 `ingestion_ts`。
  - `enterprise.gold_ref.market_macro_daily` 应使用 `mart_ts`。

## D. 已完成修复与下一步
- 已修复：`70_platform_observability_metrics_build.ipynb`
  - `event_ts_col`: `event_time` -> `ingestion_ts`
  - `event_ts_col`: `trade_date` -> `mart_ts`
- 下一步：
  1. 重跑 `direct_market_macro_pipeline`（刷新 70 的最新指标分区）。
  2. 复跑 `96_validation_day6_regression_checks.ipynb`。
  3. 若 B5 变为全 `OK`，将 Week1 回归门禁标记为 PASS。
