# WEEK1 Changelog

## 时间范围
- 2026-02-22 到 2026-02-25

## 目标
- 把 notebook 为主的 Databricks 项目改造成可维护、可测试、可部署、可验收的工程化版本。

## Day1-Day2（结构与命名治理）
- 统一 direct/landing/platform notebook 命名。
- 清理重复脚本并归档到 `_archive/week1`。
- 修复 `databricks.yml` 任务路径与当前文件名一致性问题。
- 输出 `docs/ACTIVE_PIPELINE.md` 和 `docs/KNOWN_ISSUES.md`。

## Day3-Day4（模块化与测试）
- 抽取可复用 Python 模块到 `src/lakehouse/`：
  - `crypto_parser.py`
  - `quality_rules.py`
  - `observability_rules.py`
- 新增单元测试到 `tests/unit/`，本地基线通过（`7 passed`）。
- 清理 `__pycache__` 并完善 `.gitignore`。

## Day5（CI 落地）
- 新增并升级 GitHub Actions：
  - `.github/workflows/ci.yml`
  - 质量门禁为 `ruff + pytest`
- 增加 `.pre-commit-config.yaml` 和 `ruff` 配置。

## Day6（回归与数据验收）
- 新增校验 notebook：`96_validation_day6_regression_checks.ipynb`。
- 完成 Bronze/Silver/Gold/Observability 的 SQL 校验清单执行。
- 主链路目标表切换到 `enterprise.gold_ref.market_macro_daily` 后：
  - target 表存在性 OK
  - target 空值率和缺失交易日比例为 0
  - legacy 表保留用于对照（仍显示高缺失）

## Day7（交付文档冻结）
- 回填 `docs/WEEK1_REGRESSION_EVIDENCE.md` 为最新实测版本。
- 冻结 `docs/WEEK1_JD_MAPPING.md` 为投递口径。
- 新增 `docs/WEEK1_STAR_CN_EN.md` 作为面试材料。

## Week1 收尾修复（本次）
- 修复 `70_platform_observability_metrics_build.ipynb` freshness 口径：
  - `enterprise.bronze_market.crypto_ohlc_raw`: `event_time` -> `ingestion_ts`
  - `enterprise.gold_ref.market_macro_daily`: `trade_date` -> `mart_ts`
- 目的：消除 observability 的结构性误报。

## Week1 完成定义（DoD）
- 命名、任务编排、测试、CI、回归证据、JD 映射、STAR 材料全部具备。
- 剩余动作仅为一次重跑验证 observability 新口径。
