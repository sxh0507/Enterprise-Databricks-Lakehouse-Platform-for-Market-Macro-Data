# Week1 STAR（CN + EN）

## STAR 1: 项目工程化重构（命名 + 编排 + 可维护）

### CN
- Situation：项目由多条 notebook 链路演化而来，命名混乱、重复脚本多、`databricks.yml` 与实际文件不一致，难以稳定维护。
- Task：在不破坏现有业务输出的前提下，完成 Week1 的工程化重构，建立“可部署、可验证、可交接”的基线。
- Action：统一 notebook 命名（direct/landing/platform），归档重复脚本，修正 bundle job 路径，补齐 `ACTIVE_PIPELINE`/`KNOWN_ISSUES` 文档，并做路径存在性校验。
- Result：主链路可通过 bundle 正常部署与运行；仓库结构和任务口径统一，后续开发效率与可读性明显提升。

### EN
- Situation: The project had evolved into multiple notebook paths with inconsistent naming, duplicate scripts, and mismatch between `databricks.yml` and actual files.
- Task: Refactor the project in Week1 without breaking outputs, and establish a deployable and verifiable baseline.
- Action: Standardized notebook naming (direct/landing/platform), archived duplicates, fixed bundle job paths, added `ACTIVE_PIPELINE` and `KNOWN_ISSUES`, and validated notebook path integrity.
- Result: The core pipeline became deployable/runnable via bundle, and repository structure plus task semantics were aligned for maintainability.

## STAR 2: 从 Notebook 逻辑到可测试模块（Python + Unit Test + CI）

### CN
- Situation：关键逻辑主要散落在 notebook 中，难复用、难单测、难做质量门禁。
- Task：抽取最关键的纯逻辑为 Python 模块，并建立自动化测试与 CI。
- Action：把解析/质量/可观测规则抽到 `src/lakehouse`，补充 `tests/unit`，建立 `ruff + pytest` 的 GitHub Actions，并加入 pre-commit。
- Result：形成最小工程化质量闭环，本地与 CI 都可自动验证，Week1 测试基线稳定通过（7 passed）。

### EN
- Situation: Core logic lived mostly inside notebooks, making reuse, unit testing, and quality gating difficult.
- Task: Extract critical pure logic into Python modules and introduce automated testing with CI.
- Action: Moved parser/quality/observability logic to `src/lakehouse`, added `tests/unit`, enabled GitHub Actions with `ruff + pytest`, and added pre-commit hooks.
- Result: Established a minimal engineering quality loop; validations are automated locally and in CI, with a stable Week1 baseline (`7 passed`).

## STAR 3: Day6 回归验收与口径修正（Gold Target + Observability）

### CN
- Situation：历史 legacy gold 表宏观字段缺失严重，且 observability 有结构性误报，影响回归判断。
- Task：把验收口径切到 `enterprise.gold_ref.market_macro_daily`，并定位 observability 误报来源。
- Action：新增 `96_validation_day6_regression_checks.ipynb`，分 target/legacy 双口径校验；确认 target 数据质量通过；修复 70 中 freshness 时间列映射（`ingestion_ts`、`mart_ts`）。
- Result：主链路 target 质量达标（空值率与缺失交易日为 0），遗留问题收敛为单点配置修正，进入可控重跑验证阶段。

### EN
- Situation: The legacy gold table had severe macro missingness, and observability produced structural false fails.
- Task: Switch validation to `enterprise.gold_ref.market_macro_daily` and identify the observability root cause.
- Action: Added `96_validation_day6_regression_checks.ipynb` with target vs legacy checks, confirmed target quality pass, and fixed freshness timestamp mapping in notebook 70 (`ingestion_ts`, `mart_ts`).
- Result: Target pipeline quality passed (zero null-rate/missing-day on key checks), and remaining risk was reduced to a controlled configuration rerun.
