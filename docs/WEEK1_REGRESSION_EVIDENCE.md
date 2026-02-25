# Week1 回归证据（当前真实进度版）

## A. 执行信息
- 日期：2026-02-23
- 执行人：xh.shi0507@gmail.com
- 分支：`s3-integration`（当次运行），后续已合并到 `main`
- Databricks Workspace：`https://dbc-ccc612b1-3dfb.cloud.databricks.com`
- Job Key：`direct_market_macro_pipeline`
- Run URL：`https://dbc-ccc612b1-3dfb.cloud.databricks.com/?o=7474650217904913#job/258899764875401/run/1094257915597442`
- 当时终端状态：`QUEUED -> RUNNING`
- 最终状态：待在 Databricks Jobs UI 补录（建议补为 SUCCESS/FAILED 截图）

## B. 任务级状态（按当前证据）
| task_key | status | duration | 备注 |
|---|---|---|---|
| platform_setup_catalog_schema | 已触发（待补最终） | 待补 | 属于本次 run 任务链 |
| direct_bronze_market_crypto_ingest | 已触发（待补最终） | 待补 |  |
| direct_bronze_ref_ecb_fx_ingest | 已触发（待补最终） | 待补 |  |
| direct_bronze_ref_fred_ingest | 已触发（待补最终） | 待补 |  |
| direct_silver_market_crypto_ohlc_transform | 已触发（待补最终） | 待补 | 已接入 `lakehouse` 模块导入 |
| direct_silver_ref_macro_transform | 已触发（待补最终） | 待补 |  |
| direct_gold_market_ohlc_features_build | 已触发（待补最终） | 待补 |  |
| direct_gold_market_macro_daily_build | 已触发（待补最终） | 待补 |  |
| platform_observability_metrics_build | 已触发（待补最终） | 待补 | 已接入 `lakehouse.observability_rules` |

## C. 代码与配置一致性验收（已完成）
- `databricks.yml` 的 `direct_market_macro_pipeline` 与当前 notebook 命名一致。
- notebook 重命名已完成（`direct_* / landing_* / platform_*` 规则）。
- 已执行 notebook 路径存在性校验（历史输出：`missing notebook paths: []`）。

## D. 本地工程质量证据（已完成）
- 单元测试执行命令：`PYTHONPATH=src python3 -m pytest -q tests/unit`
- 最近结果：`7 passed`
- 模块覆盖：
  - `src/lakehouse/crypto_parser.py`
  - `src/lakehouse/quality_rules.py`
  - `src/lakehouse/observability_rules.py`
- 测试覆盖文件：
  - `tests/unit/test_crypto_parser.py`
  - `tests/unit/test_quality_rules.py`
  - `tests/unit/test_observability_rules.py`

## E. CI 证据（已完成到仓库层）
- 已新增：`.github/workflows/ci.yml`
- 触发条件：push / pull_request（`main`）
- 当前状态：workflow 已升级为 `ruff + pytest` 并推送到 `main`
- 本地验证：`python3 -m ruff check src tests` + `python3 -m pytest -q tests/unit` 均通过
- Actions 页面运行结果：待在 GitHub Actions 页面补录 run 链接与 PASS/FAIL

## F. 数据验收（Day6 实测，2026-02-25）
> 以下为通过 Databricks SQL Statements API 在 warehouse `b4a6b904b8ac6197` 的真实输出。

### F1. 表存在性检查
| 表名 | 状态 |
|---|---|
| `enterprise.bronze_market.crypto_ohlc_raw` | OK |
| `enterprise.bronze_ref.ecb_fx_raw` | OK |
| `enterprise.bronze_ref.fred_series_raw` | OK |
| `enterprise.silver_market.crypto_ohlc_1d` | OK |
| `enterprise.silver_ref.ecb_fx_daily` | OK |
| `enterprise.silver_ref.fred_series_daily` | OK |
| `enterprise.gold_market.ohlc_1d` | OK |
| `enterprise.gold_observability.pipeline_metrics_daily` | OK |
| `enterprise.gold_ref.market_macro_daily` | MISSING |

### F2. 行数检查（count）
| 表名 | row_count |
|---|---:|
| `enterprise.bronze_market.crypto_ohlc_raw` | 8162 |
| `enterprise.silver_market.crypto_ohlc_1d` | 7439 |
| `enterprise.silver_ref.ecb_fx_daily` | 225 |
| `enterprise.silver_ref.fred_series_daily` | 26167 |
| `enterprise.gold_market.ohlc_1d` | 7439 |
| `enterprise.gold_market.market_macro_daily`（legacy） | 7439 |
| `enterprise.gold_ref.market_macro_daily`（target） | N/A（MISSING） |
| `enterprise.gold_observability.pipeline_metrics_daily` | 72 |

### F3. Freshness 检查（分钟）
| 表名 | max_ts | freshness_min |
|---|---|---:|
| bronze_crypto | 2026-02-23T21:32:42.735Z | 2754 |
| silver_crypto_1d | 2026-02-24T00:00:00.000Z | 2607 |
| silver_ecb_daily | 2026-02-23T00:00:00.000Z | 4047 |
| silver_fred_daily | 2026-02-19T00:00:00.000Z | 9807 |
| gold_market_macro_daily（legacy） | 2026-02-23T21:46:37.032Z | 2740 |
| obs_pipeline_metrics_daily | 2026-02-23T21:48:22.009Z | 2739 |

### F4. 质量检查（Day6）
| 检查项 | 结果 | 结论 |
|---|---:|---|
| `dup_group_cnt` on `silver_market.crypto_ohlc_1d` | 0 | PASS |
| `bad_ohlc_rows` on `silver_market.crypto_ohlc_1d` | 0 | PASS |
| `null_rate_eurusd_rate` on legacy `gold_market.market_macro_daily` | 0.970426 | FAIL |
| `null_rate_fedfunds` on legacy `gold_market.market_macro_daily` | 0.000000 | PASS |
| `null_rate_close_px` on legacy `gold_market.market_macro_daily` | 0.000000 | PASS |
| `days_with_macro_missing / total_trade_days`（去重日期） | 3762 / 3872（97.16%） | FAIL |
| latest obs status summary | FAIL=1, OK=2 | FAIL |

### F5. Day6 回归结论
- Regression Gate：**FAIL**
- 主要原因：
  1. 目标表 `enterprise.gold_ref.market_macro_daily` 尚未物化（当前仍是 legacy `gold_market.market_macro_daily`）。
  2. 宏观融合覆盖率明显不足（EURUSD 在 legacy gold 表中缺失率约 97%）。
  3. Observability 最新分区存在 `FAIL` 状态记录。
- 进入 Day7 前必须完成：
  1. 重新部署并运行包含 `gold_ref` 修复后的 direct pipeline。
  2. 复跑 Day6 SQL 清单并替换 legacy 指标为 `gold_ref` 指标。
  3. 让 observability latest 分区全部达成预期（至少无结构性 FAIL）。

## G. 已识别问题与处理
| 问题 | 影响 | 修复动作 | 关联提交 |
|---|---|---|---|
| 分支 diverged 导致 push 拒绝 | 无法推送 | 同步分支后重新 push/PR | 历史 PR 合并 |
| zsh 粘贴多行注释导致 parse error | CLI 执行中断 | 改为逐行纯命令执行 | 运维过程修复 |
| 命名不一致 | 维护成本高 | 统一命名 + 更新 `databricks.yml` + 文档同步 | `82e22f6`, `754968b` |
| 缓存文件误纳入版本控制 | 污染仓库 | 更新 `.gitignore`，清理 `__pycache__` | `5d5b90b` |
| CI 缺少 lint gate | 质量门禁不完整 | 升级 `ci.yml` 为 `ruff + pytest` | `19d7b62` |
| Gold 目标 schema 错位（`gold_market` vs `gold_ref`） | 域治理与回归口径混乱 | 修正 notebook + setup + day6 checklist，并待重新运行 pipeline 物化 | `afcc84a` |
